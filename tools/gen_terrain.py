"""大地图的地形图集：基础地面、地面之间的过渡、水面/道路/熔岩等覆盖层的自动拼接块、
各地形的遭遇草丛、地面装饰。输出：

- assets/sprites/terrain.png         图集
- scripts/world/terrain_atlas.gd     图集里每一块的位置（由本脚本生成，不要手改）

图集按 16 像素的格子排布：
- 基础地面每种一行：4 个变体 + 8 个过渡片（N S W E NW NE SW SE）。
  过渡片画在「北边邻居是这种地面」的格子上，表示这种地面从北边漫进来一点。
- 覆盖层（道路、浅水、深水、熔岩、沼泽水、冰面）和遭遇草丛用 RPG Maker 式的四分之一自动拼接：
  每帧一个 32x40 的块，4 列是格子的左上/右上/左下/右下四分之一，5 行是
  0 内部、1 上下边、2 左右边、3 外角、4 内角。
"""
import math
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "sprites"
T = 16
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def hexc(s, a=255):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def hash2(x, y, seed):
    h = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return (h ^ (h >> 16)) / 0xFFFFFFFF


def vnoise(x, y, period, seed):
    """周期为 period 的平滑值噪声（瓦片无缝）"""
    x0, y0 = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - x0, y - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)

    def g(ix, iy):
        return hash2(ix % period, iy % period, seed)
    a = g(x0, y0) + (g(x0 + 1, y0) - g(x0, y0)) * fx
    b = g(x0, y0 + 1) + (g(x0 + 1, y0 + 1) - g(x0, y0 + 1)) * fx
    return a + (b - a) * fy


def tex_noise(x, y, seed, cells=4):
    """16 像素瓦片上的无缝噪声，0..1"""
    return 0.65 * vnoise(x / T * cells, y / T * cells, cells, seed) + \
        0.35 * vnoise(x / T * cells * 2, y / T * cells * 2, cells * 2, seed + 7)


def ramp_pick(cols, f, x, y, spread=0.5):
    n = len(cols) - 1
    g = f * n + (BAYER[y % 4][x % 4] / 16 - 0.5) * spread
    return cols[max(0, min(n, int(g + 0.5)))]


# ------------------------------------------------------------------ 基础地面
BASES = {
    # 名字: (色阶 暗→亮, 纹理函数名)
    "grass": ["#4f9445", "#5ea84f", "#6fb85a", "#83c868", "#9ed67e"],
    "forest": ["#2f5f34", "#3a6f3b", "#467f43", "#55904c", "#6aa35a"],
    "sand": ["#cfae74", "#ddbf86", "#e8cf98", "#f1ddad", "#f8ebc6"],
    "snow": ["#b9c9de", "#cfdbea", "#e2eaf4", "#f0f5fa", "#ffffff"],
    "rock": ["#6c6660", "#7f7870", "#938b80", "#a69d90", "#bab2a4"],
    "ash": ["#2e2627", "#3b3131", "#4a3f3d", "#5a4d48", "#6b5d55"],
    "mud": ["#414a2c", "#4d5733", "#5a653b", "#687444", "#7a8650"],
}
BASE_ORDER = ["sand", "mud", "ash", "rock", "grass", "forest", "snow"]  # 后面的盖在前面的上面


def _base_pixel(name, x, y, variant):
    """底色：大块的两三种相近颜色，不做细碎抖动，细节交给 base_tile 里的小图案"""
    cols = [hexc(c) for c in BASES[name]]
    seed = BASE_ORDER.index(name) * 31 + variant * 7
    n = tex_noise(x, y, seed, 2)
    if name == "sand":
        w = math.sin((x * 0.5 + y * 1.4 + variant * 3) * 0.9 + n * 3)
        if w > 0.9:
            return cols[3]
        if w < -0.92:
            return cols[1]
    if name == "rock":
        crack = abs(math.sin(x * 0.7 + 3 * vnoise(x / 4, y / 4, 4, seed + 5) * math.pi))
        if crack < 0.06:
            return cols[1]
    lo, hi = (0.32, 0.7) if name in ("grass", "forest", "sand") else (0.2, 0.82)
    if n < lo:
        return cols[1] if name != "snow" else cols[3]
    if n > hi:
        return cols[3]
    return cols[2]


# 每种地面的小图案：(图案, 出现次数)。字符是色阶序号，E 火星、P 泥坑，"." 透明
GLYPHS = {
    "grass": [(["1.1", ".3."], 3), (["4"], 2)],
    "forest": [(["0.0", ".2."], 3), (["3.", ".1"], 1), (["4"], 1)],
    "sand": [(["0"], 2), (["4"], 1)],
    "snow": [(["1"], 1), (["4"], 2)],
    "rock": [([".4.", "411", ".1."], 1), (["0"], 2)],
    "ash": [(["E"], 2), (["0"], 3), (["3"], 1)],
    "mud": [(["0.0", ".1."], 2), (["P"], 1), (["4"], 1)],
}


def base_tile(name, variant):
    im = Image.new("RGBA", (T, T))
    px = im.load()
    for y in range(T):
        for x in range(T):
            px[x, y] = _base_pixel(name, x, y, variant)
    cols = [hexc(c) for c in BASES[name]]
    extra = {"E": hexc("#e8603a"), "P": hexc("#3d4a33")}
    rnd = random.Random(BASE_ORDER.index(name) * 100 + variant)
    for glyph, count in GLYPHS[name]:
        for _ in range(count + (variant % 2)):
            gx, gy = rnd.randrange(0, T), rnd.randrange(0, T)
            for dy, row in enumerate(glyph):
                for dx, ch in enumerate(row):
                    if ch != ".":
                        px[(gx + dx) % T, (gy + dy) % T] = extra[ch] if ch in extra else cols[int(ch)]
    return im


def _wob(t, seed, amp=1.2):
    """沿边缘的起伏，周期 16，保证相邻格子接得上"""
    return amp * (0.6 * math.sin(2 * math.pi * t / T * 2 + seed) + 0.4 * math.sin(2 * math.pi * t / T * 3 + seed * 2))


def transition_piece(name, side):
    """side: N S W E NW NE SW SE。返回 16x16，只有漫进来的那部分不透明"""
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    px = im.load()
    cols = [hexc(c) for c in BASES[name]]
    seed = BASE_ORDER.index(name)
    for y in range(T):
        for x in range(T):
            cx, cy = x + 0.5, y + 0.5
            if side in ("N", "S", "W", "E"):
                d = {"N": cy, "S": T - cy, "W": cx, "E": T - cx}[side]
                along = cx if side in ("N", "S") else cy
                depth = 3.2 + _wob(along, seed)
            else:
                ox = 0 if "W" in side else T
                oy = 0 if "N" in side else T
                d = math.hypot(cx - ox, cy - oy)
                depth = 3.6 + _wob(math.atan2(cy - oy, cx - ox) * 8, seed, 0.8)
            if d < depth:
                c = _base_pixel(name, x, y, 0)
                if d > depth - 1.0:
                    # 过渡边缘：雪和沙更亮，其他更暗，像一圈边
                    c = cols[4] if name in ("snow", "sand") else cols[0]
                px[x, y] = c
            elif d < depth + 1.0 and BAYER[y % 4][x % 4] < 6:
                px[x, y] = cols[1] if name not in ("snow", "sand") else cols[3]
    return im


# ------------------------------------------------------------------ 覆盖层
QUARTERS = [(0, 0), (1, 0), (0, 1), (1, 1)]  # TL TR BL BR
CASES = 5


def _inside(x, y, edges, notch, m_of, r=4.0):
    """格子坐标 (x, y)（0..16）是否在覆盖层形状内。edges: 有边的方向集合；notch: 内角缺口集合"""
    mu, md, ml, mr = m_of("u", x), m_of("d", x), m_of("l", y), m_of("r", y)
    if "u" in edges and y < mu:
        return False
    if "d" in edges and y > T - md:
        return False
    if "l" in edges and x < ml:
        return False
    if "r" in edges and x > T - mr:
        return False
    for vert, hor in (("u", "l"), ("u", "r"), ("d", "l"), ("d", "r")):
        if vert in edges and hor in edges:
            cx = (ml + r) if hor == "l" else (T - mr - r)
            cy = (mu + r) if vert == "u" else (T - md - r)
            inx = x < cx if hor == "l" else x > cx
            iny = y < cy if vert == "u" else y > cy
            if inx and iny and math.hypot(x - cx, y - cy) > r:
                return False
        if vert + hor in notch:
            inx = x < ml if hor == "l" else x > T - mr
            iny = y < mu if vert == "u" else y > T - md
            if inx and iny:
                return False
    return True


def _quarter_config(q, case):
    """第 q 个四分之一、第 case 种情况对应的 (edges, notch)"""
    qx, qy = QUARTERS[q]
    v = "u" if qy == 0 else "d"
    h = "l" if qx == 0 else "r"
    if case == 0:
        return set(), set()
    if case == 1:
        return {v}, set()
    if case == 2:
        return {h}, set()
    if case == 3:
        return {v, h}, set()
    return set(), {v + h}


def autotile_block(fill, rim, margin=3.0, seed=0):
    """fill(x, y, d_out) -> 颜色或 None；rim(x, y, side) 处理靠边像素。返回 32x40 的块"""
    def m_of(side, t):
        return margin + _wob(t, seed + "udlr".index(side) * 0.0, 0.9)

    block = Image.new("RGBA", (32, 40), (0, 0, 0, 0))
    bp = block.load()
    for case in range(CASES):
        for q in range(4):
            edges, notch = _quarter_config(q, case)
            qx, qy = QUARTERS[q]
            for py in range(8):
                for pxl in range(8):
                    x, y = qx * 8 + pxl, qy * 8 + py
                    cx, cy = x + 0.5, y + 0.5
                    ins = _inside(cx, cy, edges, notch, m_of)
                    # 到形状外的距离（只看 1~2 像素内），用来画边
                    side = None
                    if ins:
                        for dist in (1, 2):
                            for sx, sy, nm in ((0, -dist, "u"), (0, dist, "d"), (-dist, 0, "l"), (dist, 0, "r")):
                                if not _inside(cx + sx, cy + sy, edges, notch, m_of):
                                    side = (nm, dist)
                                    break
                            if side:
                                break
                        c = rim(x, y, side) if side else fill(x, y)
                    else:
                        near = None
                        for sx, sy, nm in ((0, 1, "u"), (0, -1, "d"), (1, 0, "l"), (-1, 0, "r")):
                            if _inside(cx + sx, cy + sy, edges, notch, m_of):
                                near = nm
                                break
                        c = rim(x, y, ("out", near)) if near else None
                    if c:
                        bp[q * 8 + pxl, case * 8 + py] = c
    return block


def path_block():
    cols = [hexc(c) for c in ["#a8875a", "#bf9e6c", "#d3b47f", "#e2c793", "#efdbb0"]]

    def fill(x, y):
        n = tex_noise(x, y, 41)
        r = hash2(x, y, 43)
        if r < 0.05:
            return cols[0]
        if r < 0.09:
            return cols[4]
        return ramp_pick(cols, 0.35 + n * 0.4, x, y)

    def rim(x, y, side):
        nm, d = side
        if nm == "out":
            return None
        if d == 1:
            return cols[0] if nm in ("u", "l") else cols[1]
        return cols[1] if nm == "u" else fill(x, y)
    return [autotile_block(fill, rim, 2.5, 1)]


def water_blocks(deep=False):
    if deep:
        cols = [hexc(c) for c in ["#1d4f8f", "#235c9f", "#2a68ad", "#3174b8"]]
        shore = hexc("#3f8fd0")
    else:
        cols = [hexc(c) for c in ["#2f7fc0", "#3a8fd0", "#47a0dc", "#5cb2e6"]]
        shore = hexc("#dff4ff")
    blocks = []
    for f in range(3):
        def fill(x, y, f=f):
            n = tex_noise(x, y, 61 if deep else 51, 2)
            c = ramp_pick(cols, 0.3 + n * 0.45, x, y, 0.4)
            # 波纹：随帧平移的亮短线
            w = math.sin((x + f * 5.333) * 2 * math.pi / 16 * 2 + math.sin(y * 2 * math.pi / 16 * 2) * 1.5)
            if (y % 4 == (1 + f) % 4) and w > 0.82:
                return hexc("#bfe6fa") if not deep else cols[3]
            return c

        def rim(x, y, side, f=f):
            nm, d = side
            if nm == "out":
                return None if deep else (hexc("#2a5f8a", 120) if d == "u" else None)
            if deep:
                return shore if d == 1 else mix(shore, cols[2], 0.5)
            if nm == "u":
                return hexc("#245f96") if d == 1 else hexc("#2f73b0")
            if d == 1:
                return shore if (x + y + f) % 3 else hexc("#a8dcf5")
            return fill(x, y)
        blocks.append(autotile_block(fill, rim, 3.0 if not deep else 3.5, 3 if deep else 2))
    return blocks


def lava_blocks():
    cols = [hexc(c) for c in ["#c2361a", "#e8501f", "#ff7a1a", "#ffa62a", "#ffd23a"]]
    blocks = []
    for f in range(3):
        def fill(x, y, f=f):
            n = 0.5 * tex_noise(x, y, 71, 2) + 0.5 * vnoise(x / 4 + f * 0.35, y / 4 + f * 0.2, 4, 73)
            return ramp_pick(cols, n * 1.1 - 0.05, x, y, 0.5)

        def rim(x, y, side):
            nm, d = side
            if nm == "out":
                return hexc("#1f1717")
            return hexc("#2b1d1b") if d == 1 else hexc("#8f2a14")
        blocks.append(autotile_block(fill, rim, 3.0, 5))
    return blocks


def bog_blocks():
    cols = [hexc(c) for c in ["#33452f", "#3b5036", "#455d3e", "#516b48"]]
    blocks = []
    for f in range(2):
        def fill(x, y, f=f):
            n = tex_noise(x, y, 81, 2)
            r = hash2(x, y, 83)
            if r < 0.03:
                return hexc("#7d9a4a")  # 浮萍
            if (x + y * 3 + f * 4) % 13 == 0:
                return hexc("#6b8a62")
            return ramp_pick(cols, 0.3 + n * 0.5, x, y)

        def rim(x, y, side):
            nm, d = side
            if nm == "out":
                return None
            return hexc("#2a3622") if d == 1 else cols[0]
        blocks.append(autotile_block(fill, rim, 3.0, 7))
    return blocks


def ice_block():
    cols = [hexc(c) for c in ["#8fc9e3", "#a6d7ec", "#bfe4f3", "#d8f1fa"]]

    def fill(x, y):
        n = tex_noise(x, y, 91, 2)
        if (x - y) % 11 == 0 and n > 0.4:
            return hexc("#ffffff")
        return ramp_pick(cols, 0.3 + n * 0.5, x, y)

    def rim(x, y, side):
        nm, d = side
        if nm == "out":
            return None
        return hexc("#ffffff") if d == 1 else cols[1]
    return [autotile_block(fill, rim, 2.5, 9)]


# 遭遇草丛（每个地形一种样子）：叶片颜色 暗/中/亮/尖
TALL = {
    "grass": ["#2a7429", "#3f9a3c", "#5cb84f", "#9ade7a"],
    "forest": ["#1d4a24", "#2b6332", "#3f7f40", "#7fbf63"],
    "swamp": ["#3d4a26", "#56662f", "#71833c", "#b4c26a"],
    "coast": ["#5f7f3a", "#7f9d48", "#a0b85c", "#e3e2a0"],
    "desert": ["#8a6a30", "#a8853f", "#c8a456", "#ead08a"],
    "volcano": ["#4a2a24", "#6b3a2c", "#8f4a30", "#ff9b3a"],
    "mountain": ["#4f6a4a", "#647f58", "#7c9668", "#b9c99a"],
    "lakes": ["#2f6f4a", "#3f8a58", "#57a56a", "#a6dca0"],
    "snow": ["#5f8a8a", "#7aa3a0", "#9fc2bc", "#ffffff"],
}


def tall_blocks(name):
    c = [hexc(v) for v in TALL[name]]
    blocks = []
    for f in range(2):
        def fill(x, y, f=f):
            # 一排排「W」形叶丛，行与行错开；每列根部暗、尖部亮
            row = y // 5
            lx = (x + row * 3 + (1 if f and row % 2 else 0)) % 6
            h = [2, 3, 4, 3, 2, 1][lx]
            yy = y % 5
            if yy >= 5 - h:
                return c[3] if yy == 5 - h else (c[2] if lx in (1, 2) else c[1])
            return c[0]

        def rim(x, y, side):
            nm, d = side
            if nm == "out":
                # 上边缘外侧冒出的叶尖
                if d == "u" and (x + f) % 3 == 0:
                    return c[3]
                return None
            if nm == "u" and d == 1:
                return c[2] if (x + f) % 2 else c[3]
            return fill(x, y)
        blocks.append(autotile_block(fill, rim, 1.5, 11))
    return blocks


def tall_front(name):
    """角色站在草丛里时盖住脚的叶片（只占下半格）"""
    c = [hexc(v) for v in TALL[name]]
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    px = im.load()
    for cx in (2, 7, 12):
        for dx, h in ((-2, 3), (-1, 5), (0, 6), (1, 5), (2, 3)):
            x = cx + dx
            if 0 <= x < T:
                for i in range(h):
                    px[x, T - 1 - i] = c[2] if dx in (-1, 0) else c[1]
                px[x, T - 1 - h] = c[3]
    return im


# ------------------------------------------------------------------ 地面装饰（可走过）
def decor(kind):
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    px = im.load()

    def put(x, y, c):
        if 0 <= x < T and 0 <= y < T:
            px[x, y] = hexc(c) if isinstance(c, str) else c

    if kind.startswith("flower"):
        petal = {"flower_r": "#ff8fa3", "flower_y": "#fff07a", "flower_w": "#ffffff", "flower_b": "#9fb8ff"}[kind]
        for cx, cy in ((4, 6), (11, 10), (6, 12)):
            put(cx, cy + 1, "#3f8a3a")
            put(cx, cy + 2, "#3f8a3a")
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                put(cx + dx, cy + dy, petal)
            put(cx, cy, "#f2a33a")
    elif kind == "pebbles":
        for cx, cy, r in ((4, 10, 1.6), (10, 6, 1.2), (12, 12, 1.0)):
            for y in range(T):
                for x in range(T):
                    d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                    if d <= r:
                        put(x, y, "#c9c2b6" if y + 0.5 < cy else "#8f877c")
    elif kind == "mushroom":
        for cx, cy in ((5, 11), (10, 9)):
            put(cx, cy + 1, "#f0e6d0")
            put(cx, cy + 2, "#d9ccb0")
            for dx in (-2, -1, 0, 1, 2):
                put(cx + dx, cy, "#d84a3a")
            for dx in (-1, 0, 1):
                put(cx + dx, cy - 1, "#e85a48")
            put(cx - 1, cy - 1, "#ffffff")
            put(cx + 1, cy, "#ffffff")
    elif kind == "shell":
        for cx, cy in ((5, 9), (11, 12)):
            for dx in (-1, 0, 1):
                put(cx + dx, cy, "#ffd8c8")
            put(cx, cy - 1, "#ffe9de")
            put(cx - 1, cy + 1, "#e8a890")
            put(cx + 1, cy + 1, "#e8a890")
    elif kind == "dry_bush":
        for i in range(12):
            a = math.pi * (0.15 + 0.7 * i / 11)
            for k in range(1, 6):
                put(int(8 + math.cos(a) * k), int(13 - math.sin(a) * k), "#a8853f" if k < 4 else "#d6b56a")
    elif kind == "ember":
        for x, y in ((4, 8), (5, 8), (6, 9), (10, 12), (11, 11), (12, 11)):
            put(x, y, "#ff7a1a")
        put(5, 7, "#ffd23a")
        put(11, 10, "#ffd23a")
    elif kind == "lily":
        for y in range(T):
            for x in range(T):
                d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
                if d < 4 and not (x > 8 and abs(y - 8) < 1.5):
                    put(x, y, "#5f9a3a" if d < 3 else "#3f7a2a")
        put(7, 6, "#ffffff")
        put(8, 6, "#ffb3c8")
    elif kind == "snow_tuft":
        for x, y in ((4, 11), (5, 10), (6, 11), (10, 8), (11, 7), (12, 8)):
            put(x, y, "#ffffff")
            put(x, y + 1, "#cfdbea")
    elif kind == "bones":
        for x in range(4, 11):
            put(x, 9, "#efe6d2")
        for x, y in ((3, 8), (3, 10), (11, 8), (11, 10)):
            put(x, y, "#efe6d2")
        put(7, 10, "#bfb39a")
    return im


DECOR = ["flower_r", "flower_y", "flower_w", "flower_b", "pebbles", "mushroom", "shell",
         "dry_bush", "ember", "lily", "snow_tuft", "bones"]


# ------------------------------------------------------------------ 桥
def bridge(vertical):
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    px = im.load()
    wood = [hexc("#6e4a2a"), hexc("#8f6338"), hexc("#a8784a"), hexc("#c49460")]
    for y in range(T):
        for x in range(T):
            a, b = (x, y) if vertical else (y, x)
            if 1 <= a <= 14:
                plank = b % 4
                c = wood[0] if plank == 3 else wood[2] if plank == 0 else wood[1]
                if a in (1, 14):
                    c = wood[0]
                if a == 2:
                    c = wood[3]
                px[x, y] = c
    return im


# ------------------------------------------------------------------ 组装
def build():
    entries = {}
    rows = []

    # 基础地面：每种一行
    base_rows = []
    for name in BASE_ORDER:
        row = Image.new("RGBA", (T * 12, T), (0, 0, 0, 0))
        for v in range(4):
            row.paste(base_tile(name, v), (v * T, 0))
        for i, side in enumerate(["N", "S", "W", "E", "NW", "NE", "SW", "SE"]):
            row.paste(transition_piece(name, side), ((4 + i) * T, 0))
        base_rows.append(row)
    y = 0
    base_y = {}
    for name, row in zip(BASE_ORDER, base_rows):
        base_y[name] = y
        rows.append((row, 0, y))
        y += T

    # 覆盖层块：每帧 32x40，横向排开
    overlay = {
        "path": path_block(), "water": water_blocks(), "deep": water_blocks(True),
        "lava": lava_blocks(), "bog": bog_blocks(), "ice": ice_block(),
    }
    for name in TALL:
        overlay["tall_" + name] = tall_blocks(name)
    ov_pos = {}
    x = 0
    oy = y
    for name, blocks in overlay.items():
        frames = []
        for b in blocks:
            if x + 32 > 32 * 12:
                x = 0
                oy += 40
            rows.append((b, x, oy))
            frames.append((x, oy))
            x += 32
        ov_pos[name] = frames
    oy += 40

    # 单格贴图：草丛前景、装饰、桥
    singles = {}
    for name in TALL:
        singles["front_" + name] = tall_front(name)
    for d in DECOR:
        singles["decor_" + d] = decor(d)
    singles["bridge_h"] = bridge(False)
    singles["bridge_v"] = bridge(True)
    single_pos = {}
    x = 0
    for name, im in singles.items():
        if x + T > T * 24:
            x = 0
            oy += T
        rows.append((im, x, oy))
        single_pos[name] = (x, oy)
        x += T
    oy += T

    width = max(T * 24, 32 * 12)
    sheet = Image.new("RGBA", (width, oy), (0, 0, 0, 0))
    for im, px_, py_ in rows:
        sheet.paste(im, (px_, py_))
    sheet.save(OUT / "terrain.png")

    gd = ["class_name TerrainAtlas", "extends RefCounted",
          "## 由 tools/gen_terrain.py 生成，不要手改。terrain.png 里每一块的位置（像素）。", "",
          "## 基础地面，按绘制先后（后面的盖住前面的）。每行：4 个变体 + N S W E NW NE SW SE 过渡片",
          "const BASES := [%s]" % ", ".join('"%s"' % n for n in BASE_ORDER),
          "const BASE_Y := {%s}" % ", ".join('"%s": %d' % (n, base_y[n]) for n in BASE_ORDER),
          "",
          "## 自动拼接块（每帧 32x40）的左上角",
          "const OVERLAY := {"]
    for name, frames in ov_pos.items():
        gd.append('\t"%s": [%s],' % (name, ", ".join("Vector2i(%d, %d)" % f for f in frames)))
    gd += ["}", "", "## 16x16 单格贴图的左上角", "const SINGLE := {"]
    for name, p in single_pos.items():
        gd.append('\t"%s": Vector2i(%d, %d),' % (name, *p))
    gd += ["}", ""]
    (ROOT / "scripts" / "world" / "terrain_atlas.gd").write_text("\n".join(gd), encoding="utf-8")
    return sheet


if __name__ == "__main__":
    s = build()
    print("terrain.png", s.size)
