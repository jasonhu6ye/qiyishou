"""幻兽的像素立绘：每个物种生成正面图（72x72）和背面图（96x96）。

形状用椭圆、多边形和线段描述（单位坐标，原点在脚底中心，y 向上为负）。
渲染按像素中心逐点采样，不做抗锯齿，步骤是：
1. 每个图元算出表面法线：椭圆当成椭球，线段当成圆柱，多边形边缘做倒角，
   完全落在先前图元里的图元（肚皮、花纹）当作贴花，沿用下面那层的法线；
2. 左上前方打光，按亮度落到 5 级色阶（暗部偏冷、亮部偏暖），色阶交界用 4x4 Bayer 抖动；
3. 前面的部件在后面的部件上投 1~2 像素阴影，并勾出 1 像素的内轮廓；
4. 外轮廓用相邻颜色的最暗色（sel-out），受光一侧稍亮；
5. 正面再画眼睛（瞳孔、虹膜渐变、两个高光）、嘴和腮红。
由 gen_pixel_art.py 调用，输出到 assets/sprites/monsters/。
"""
import colorsys
import math

from PIL import Image

FRONT = (72, 1.5)  # 画布边长, 缩放；脚底在画布底边往上 5 像素处
BACK = (96, 1.95)

LIGHT = (-0.5, -0.62, 0.6)
_ll = math.sqrt(sum(c * c for c in LIGHT))
LIGHT = tuple(c / _ll for c in LIGHT)
_hv = (LIGHT[0], LIGHT[1], LIGHT[2] + 1.0)
_hl = math.sqrt(sum(c * c for c in _hv))
HALF = tuple(c / _hl for c in _hv)  # 观察方向 (0,0,1) 与光线的半程向量，用于高光

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
EYE_DARK = (27, 27, 43, 255)


def hexc(s, a=255):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (c[3],)


def _toward(h, target, amt):
    d = (target - h + 0.5) % 1.0 - 0.5
    return (h + d * amt) % 1.0


_RAMPS = {}


def ramp(c):
    """5 级色阶：0 最暗 … 2 原色 … 4 高光。暗部色相往蓝紫偏、亮部往黄偏"""
    if c in _RAMPS:
        return _RAMPS[c]
    h, s, v = colorsys.rgb_to_hsv(*(x / 255 for x in c[:3]))
    out = []
    for dv, ds, amt, target in ((0.52, 0.18, 0.12, 0.70), (0.74, 0.10, 0.06, 0.70), (1.0, 0.0, 0.0, 0.0),
                                (1.12, -0.12, 0.05, 0.14), (1.3, -0.35, 0.10, 0.14)):
        hh = _toward(h, target, amt) if s > 0.05 else h
        ss = max(0.0, min(1.0, s + ds * (1 if s > 0.05 else 0)))
        vv = max(0.0, min(1.0, v * dv if dv <= 1 else v + (1 - v) * (dv - 1) * 2.2))
        r, g, b = colorsys.hsv_to_rgb(hh, ss, vv)
        out.append((round(r * 255), round(g * 255), round(b * 255), 255))
    _RAMPS[c] = out
    return out


# ------------------------------------------------------------------ 图元
# ("e", x, y, rx, ry, 颜色, 旋转)      椭圆
# ("p", [(x, y), ...], 颜色)            多边形
# ("l", x1, y1, x2, y2, 线宽, 颜色)     线段
# 颜色可以是 "a"（主色）"b"（副色）"d"（暗色）或 "#rrggbb"
# 第一个元素写成 "e!" / "p!" / "l!" 表示只在正面画（脸、肚皮等），"e?" 等表示只在背面画


def _rot(x, y, a):
    c, s = math.cos(a), math.sin(a)
    return x * c - y * s, x * s + y * c


def _sample(prim, u, v):
    """像素落在图元内时返回表面法线 (nx, ny, nz)，否则返回 None"""
    kind = prim[0].rstrip("!?")
    if kind == "e":
        _, x, y, rx, ry, _c, rot = prim
        du, dv = _rot(u - x, v - y, -rot)
        a, b = du / rx, dv / ry
        r2 = a * a + b * b
        if r2 > 1.0:
            return None
        a, b = _rot(a, b, rot)
        return (a, b, math.sqrt(1.0 - r2))
    if kind == "l":
        _, x1, y1, x2, y2, w, _c = prim
        dx, dy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, ((u - x1) * dx + (v - y1) * dy) / (dx * dx + dy * dy)))
        a, b = (u - (x1 + t * dx)) / (w / 2), (v - (y1 + t * dy)) / (w / 2)
        r2 = a * a + b * b
        if r2 > 1.0:
            return None
        return (a, b, math.sqrt(1.0 - r2))
    if kind == "p":
        pts = prim[1]
        hit = False
        best, bq = 1e9, (u, v)
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > v) != (yj > v) and u < (xj - xi) * (v - yi) / (yj - yi) + xi:
                hit = not hit
            ex, ey = xi - xj, yi - yj
            t = max(0.0, min(1.0, ((u - xj) * ex + (v - yj) * ey) / (ex * ex + ey * ey or 1)))
            qx, qy = xj + t * ex, yj + t * ey
            d = math.hypot(u - qx, v - qy)
            if d < best:
                best, bq = d, (qx, qy)
            j = i
        if not hit:
            return None
        t = min(1.0, best / 2.2)
        ox, oy = bq[0] - u, bq[1] - v
        ol = math.hypot(ox, oy) or 1.0
        k = math.sqrt(max(0.0, 1.0 - t * t))
        return (ox / ol * k, oy / ol * k, t)
    raise ValueError(kind)


def _color(prim, pal):
    kind = prim[0].rstrip("!?")
    c = prim[6] if kind == "l" else prim[5] if kind == "e" else prim[2]
    return hexc(pal[c]) if c in pal else hexc(c)


def render(sp, size, scale, back):
    pal = {"a": sp["a"], "b": sp["b"], "d": sp["d"]}
    s = scale * sp.get("scale", 1.0)
    ox, oy = size / 2, size - 5
    prims = [p for p in sp["shape"] if not (back and p[0].endswith("!")) and not (not back and p[0].endswith("?"))]
    gloss = sp.get("gloss", 0.0)

    # 1. 栅格化：每个像素记录最上层的「表面」图元（法线来源）和颜色
    surf = [[-1] * size for _ in range(size)]
    norm = [[None] * size for _ in range(size)]
    col = [[None] * size for _ in range(size)]
    hits = []
    for i, prim in enumerate(prims):
        cells = []
        for py in range(size):
            for pxl in range(size):
                n = _sample(prim, (pxl + 0.5 - ox) / s, (py + 0.5 - oy) / s)
                if n is not None:
                    cells.append((pxl, py, n))
        hits.append(cells)
    for i, cells in enumerate(hits):
        covered = sum(1 for x, y, _n in cells if surf[y][x] >= 0)
        decal = cells and covered >= 0.97 * len(cells) and prims[i][0].rstrip("!?") != "l"
        c = _color(prims[i], pal)
        for x, y, n in cells:
            if not decal:
                surf[y][x] = i
                norm[y][x] = n
            col[y][x] = c

    # 2. 光照 → 色阶
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = im.load()
    level = [[0] * size for _ in range(size)]
    for y in range(size):
        for x in range(size):
            if surf[y][x] < 0:
                continue
            nx, ny, nz = norm[y][x]
            ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            nx, ny, nz = nx / ln, ny / ln, nz / ln
            d = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
            f = 0.6 + max(-1.0, d) * 2.6  # 约 -2 … 3.2
            if nz < 0.35 and d < 0.0:
                f += 0.6  # 背光边缘的反射光
            f += (BAYER[y % 4][x % 4] / 16.0 - 0.5) * 0.38
            lv = max(0, min(3, int(math.floor(f))))
            spec = nx * HALF[0] + ny * HALF[1] + nz * HALF[2]
            if spec > 0.993 - gloss * 0.03:
                lv = 4
            me = surf[y][x]
            # 3. 前面的部件投下阴影
            for k in (1, 2):
                if x - k >= 0 and y - k >= 0 and surf[y - k][x - k] > me:
                    lv = max(0, lv - 1)
                    break
            level[y][x] = lv
    for y in range(size):
        for x in range(size):
            me = surf[y][x]
            if me < 0:
                continue
            lv = level[y][x]
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < size and 0 <= ny < size and surf[ny][nx] > me:
                    lv = 0  # 内轮廓
                    break
            px[x, y] = ramp(col[y][x])[lv]

    # 4. 外轮廓：取相邻像素颜色色阶的最暗色再压暗；受光（左上）一侧稍亮
    src = im.copy().load()
    for y in range(size):
        for x in range(size):
            if src[x, y][3]:
                continue
            for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < size and 0 <= ny < size and src[nx, ny][3]:
                    base = ramp(col[ny][nx])[0]
                    lit = dx > 0 or dy > 0
                    px[x, y] = shade(base, 0.62 if lit else 0.42)
                    break

    if not back:
        _face(px, sp, s, ox, oy, size)
    return im


def _face(px, sp, s, ox, oy, size):
    """眼睛、嘴、腮红，直接按像素画，保证小尺寸下也清楚"""
    iris = hexc(sp.get("iris", "#3b3f8f"))
    er = sp.get("eye_size", 1.15)
    for ex, ey in sp.get("eyes", [(-5, -14), (5, -14)]):
        cx, cy = ox + ex * s, oy + ey * s
        rx, ry = 1.9 * s * er, 2.5 * s * er
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                a, b = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                if a * a + b * b <= 1.0 and 0 <= x < size and 0 <= y < size:
                    px[x, y] = shade(iris, 1.0 + 0.5 * max(0.0, b)) if b > 0.15 and a * a + b * b < 0.7 else EYE_DARK
        hx, hy = int(cx - rx * 0.15), int(cy - ry * 0.55)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            if 0 <= hx + dx < size and 0 <= hy + dy < size:
                px[hx + dx, hy + dy] = (255, 255, 255, 255)
        lx, ly = int(cx + rx * 0.35), int(cy + ry * 0.45)
        if 0 <= lx < size and 0 <= ly < size:
            px[lx, ly] = (236, 240, 255, 255)
    mouth = sp.get("mouth")
    if mouth:
        kind, mx, my = mouth
        cx, cy = int(ox + mx * s), int(oy + my * s)
        dark = shade(hexc(sp["d"]), 0.45)
        if kind == "smile":
            pts = [(-2, 0), (-1, 1), (0, 1), (1, 1), (2, 0)]
        elif kind == "cat":
            pts = [(-3, 0), (-2, 1), (-1, 1), (0, 0), (1, 1), (2, 1), (3, 0)]
        elif kind == "wide":
            pts = [(-6, -1), (-5, 0)] + [(i, 1) for i in range(-4, 5)] + [(5, 0), (6, -1)]
        else:  # "o"
            pts = [(-1, 0), (0, 0), (-1, 1), (0, 1)]
        for dx, dy in pts:
            px[cx + dx, cy + dy] = dark
        if kind == "cat":
            px[cx - 1, cy + 2] = (255, 255, 255, 255)
            px[cx + 1, cy + 2] = (255, 255, 255, 255)
    for bx, by in sp.get("blush", []):
        cx, cy = int(ox + bx * s), int(oy + by * s)
        for dx in range(-2, 2):
            p = px[cx + dx, cy]
            if p[3]:
                px[cx + dx, cy] = (min(255, (p[0] + 255 * 2) // 3), (p[1] + 120) // 2, (p[2] + 150) // 2, 255)


# ------------------------------------------------------------------ 物种
# 可选字段：scale 缩放、eyes 眼睛位置、eye_size、iris 虹膜色、mouth (类型, x, y)、
# blush 腮红位置、gloss 光泽度（0 哑光，1 很亮，用于水系和果冻质感）
FOX = [
    ("e", 13, -13, 9, 5, "a", -0.7), ("e", 18, -18, 4.5, 3.2, "b", -0.7),
    ("p", [(-11, -18), (-8, -30), (-3, -21)], "a"), ("p", [(11, -18), (8, -30), (3, -21)], "a"),
    ("p", [(-9, -21), (-8, -27), (-5, -22)], "d"), ("p", [(9, -21), (8, -27), (5, -22)], "d"),
    ("e", 0, -12, 12, 11, "a", 0),
    ("p!", [(-6, -5), (-4, -1), (-2, -4), (0, -0.5), (2, -4), (4, -1), (6, -5), (0, -7.5)], "b"),
    ("e!", 0, -11.2, 1.3, 0.9, "#3a1d14", 0),
    ("p?", [(-3, -23), (0, -17), (3, -23)], "d"), ("p?", [(-2.5, -15), (0, -10), (2.5, -15)], "d"),
    ("e", -6, -1, 3, 2, "d", 0), ("e", 6, -1, 3, 2, "d", 0),
]
FROG = [
    ("e", -7, -19, 5, 5, "a", 0), ("e", 7, -19, 5, 5, "a", 0),
    ("e", 0, -10, 15, 10, "a", 0), ("e!", 0, -5.5, 9.5, 4.5, "b", 0),
    ("e?", -6, -12, 2.5, 2, "d", 0.3), ("e?", 5, -8, 2, 1.6, "d", -0.2), ("e?", 7, -14, 1.6, 1.3, "d", 0),
    ("e", -11, -1, 4, 2, "d", 0), ("e", 11, -1, 4, 2, "d", 0),
]
MOUSE = [
    ("e", -9, -21, 5, 5, "a", 0), ("e", 9, -21, 5, 5, "a", 0),
    ("e", -9, -21, 2.5, 2.5, "b", 0), ("e", 9, -21, 2.5, 2.5, "b", 0),
    ("l", 9, -5, 17, -12, 2, "d"),
    ("e", 0, -11, 11, 11, "a", 0),
    ("e!", 0, -5, 6.5, 4.5, "#efe2c4", 0),
    ("e", -1, -25, 2.6, 5.5, "#4fb34f", 0.5), ("e", 3, -26, 2, 4, "#7bd36b", -0.6),
    ("e!", 0, -9.6, 1.4, 1.1, "#d77a86", 0),
    ("e", -5, -0.5, 2.6, 1.6, "d", 0), ("e", 5, -0.5, 2.6, 1.6, "d", 0),
]
BIRD = [
    ("e", 0, -12, 12, 12, "a", 0),
    ("e?", 0, -13, 6, 8, "d", 0),
    ("e", -10, -11, 4.5, 7, "d", 0.3), ("e", 10, -11, 4.5, 7, "d", -0.3),
    ("p", [(-2, -23), (0, -30), (3, -23)], "d"),
    ("e!", 0, -6, 7, 5, "b", 0), ("p!", [(-3, -11), (3, -11), (0, -7)], "#f2a33a"),
    ("l", -4, 0, -4, -3, 2, "#f2a33a"), ("l", 4, 0, 4, -3, 2, "#f2a33a"),
]
WORM = [
    ("e", -12, -5, 6, 5, "d", 0), ("e", -3, -7, 7, 6.5, "a", 0), ("e", 8, -11, 9, 9, "a", 0),
    ("e", -3, -10, 2, 1.6, "#f2d24a", 0), ("e", -12, -7, 1.6, 1.3, "#f2d24a", 0),
    ("e!", 8, -6, 5.5, 3.5, "b", 0),
    ("l", 5, -19, 2, -25, 1.3, "d"), ("l", 11, -19, 14, -25, 1.3, "d"),
    ("e", 2, -25, 1.8, 1.8, "#ff7a5a", 0), ("e", 14, -25, 1.8, 1.8, "#ff7a5a", 0),
]
JELLY = [
    ("l", -8, -9, -9, 0, 2, "d"), ("l", -4, -9, -3, 1, 2, "d"), ("l", 0, -9, 0, 0, 2, "d"),
    ("l", 4, -9, 3, 1, 2, "d"), ("l", 8, -9, 9, 0, 2, "d"),
    ("e", 0, -14, 12, 9, "a", 0), ("e", 0, -8, 11, 2.5, "d", 0), ("e", -4, -18, 4, 2, "b", 0),
    ("e?", 4, -15, 2, 1.5, "b", 0),
]
BLOB = [
    ("e", 0, -11, 12, 11, "a", 0),
    ("e", -8, -16, 2, 1.5, "#6a5a70", 0.4), ("e", 7, -5, 2.5, 1.5, "#6a5a70", -0.3),
    ("p", [(-6, -19), (0, -32), (6, -19)], "#ff9b3a"), ("p", [(-3, -20), (0, -27), (3, -20)], "b"),
]

SPECIES = {
    "huohu": {"a": "#e8743b", "b": "#ffe1a8", "d": "#a8441c", "shape": FOX,
              "iris": "#7a3b12", "mouth": ("cat", 0, -9.2)},
    "huohu2": {
        "a": "#d9502a", "b": "#ffe1a8", "d": "#8a2f12", "scale": 1.15, "iris": "#8a2a10", "mouth": ("cat", 0, -9.2),
        "shape": [("p", [(-9, -20), (-4, -36), (0, -24), (4, -36), (9, -20)], "#ffb03a"),
                  ("p", [(-5, -22), (-3, -31), (0, -24), (3, -31), (5, -22)], "#ffe066")] + FOX
        + [("e", 20, -21, 4.5, 4.5, "#ffd35a", 0), ("e", 21, -23, 2, 2.5, "#fff2a8", 0)],
    },
    "paowa": {"a": "#4c9be8", "b": "#d6efff", "d": "#2a6bb0", "shape": FROG, "eyes": [(-7, -20), (7, -20)],
              "gloss": 1.0, "mouth": ("wide", 0, -11), "blush": [(-11, -11), (11, -11)]},
    "paowa2": {
        "a": "#3a7fd6", "b": "#d6efff", "d": "#1f548f", "scale": 1.15, "eyes": [(-7, -20), (7, -20)],
        "gloss": 1.0, "mouth": ("wide", 0, -11), "iris": "#1b3f7a",
        "shape": [("p", [(-3, -22), (2, -36), (8, -22)], "b")] + FROG
        + [("e!", -12, -9, 2.5, 1.5, "#ff9fb5", 0), ("e!", 12, -9, 2.5, 1.5, "#ff9fb5", 0),
           ("e", -13, -15, 2, 1.2, "b", 0.4), ("e", 13, -15, 2, 1.2, "b", -0.4)],
    },
    "yeshu": {"a": "#c9b78a", "b": "#f5c2c7", "d": "#8d7a52", "shape": MOUSE, "iris": "#4a3524",
              "mouth": ("o", 0, -7.5), "blush": [(-7, -9), (7, -9)]},
    "yeshu2": {
        "a": "#a89466", "b": "#f5c2c7", "d": "#6c5a36", "scale": 1.15, "iris": "#2f5a24",
        "mouth": ("smile", 0, -7.5), "blush": [(-7, -9), (7, -9)],
        "shape": MOUSE + [("e", 0, -31, 4.5, 9, "#3f9a3c", 0.25), ("l", -1, -24, 1, -38, 0.8, "#2a7429"),
                          ("e", 19, -14, 3.5, 6, "#3f9a3c", -0.6), ("e", 23, -9, 2.5, 4, "#6cc25a", -1.1)],
    },
    "yuanniao": {"a": "#b9a3e3", "b": "#f4ecff", "d": "#7a62a8", "shape": BIRD, "iris": "#3b2f6a",
                 "blush": [(-7, -10), (7, -10)]},
    "yuanniao2": {
        "a": "#8f74d1", "b": "#f4ecff", "d": "#55408a", "scale": 1.15, "iris": "#2b1f5a", "eye_size": 1.0,
        "shape": [("e", -15, -16, 5, 10, "d", 0.6), ("e", 15, -16, 5, 10, "d", -0.6),
                  ("e", -18, -20, 2.5, 6, "a", 0.6), ("e", 18, -20, 2.5, 6, "a", -0.6),
                  ("p", [(-5, -22), (-7, -33), (-1, -23)], "#ff7a5a"), ("p", [(1, -23), (4, -34), (5, -22)], "#ffb03a")]
        + BIRD + [("p!", [(-7, -18), (-2, -15), (-7, -15)], "#2b1f5a"), ("p!", [(7, -18), (2, -15), (7, -15)], "#2b1f5a")],
    },
    "chongchong": {"a": "#9ad66b", "b": "#e4ffc9", "d": "#5c9a3a", "shape": WORM, "eyes": [(4, -13), (12, -13)],
                   "eye_size": 1.0, "mouth": ("smile", 8, -8.5), "gloss": 0.5},
    "jianjian": {
        "a": "#cfc27a", "b": "#f0e8b0", "d": "#8a7f40",
        "shape": [("l", 0, -29, 0, -35, 1.5, "d"), ("e", 0, -15, 10, 15, "a", 0),
                  ("l", -9, -20, 9, -16, 1.5, "d"), ("l", -9, -11, 9, -7, 1.5, "d"),
                  ("e", -4, -24, 3, 2, "b", 0.4)],
        "eyes": [(-3, -19), (3, -19)], "eye_size": 0.85, "iris": "#5a4a1a",
    },
    "caidie": {
        "a": "#7d5ac9", "b": "#ffd35a", "d": "#3f2a70",
        "shape": [("e", -12, -22, 11, 8, "b", -0.5), ("e", 12, -22, 11, 8, "b", 0.5),
                  ("e", -13, -22, 5, 3.5, "#ff7a5a", -0.5), ("e", 13, -22, 5, 3.5, "#ff7a5a", 0.5),
                  ("e", -17, -25, 1.8, 1.8, "#ffffff", 0), ("e", 17, -25, 1.8, 1.8, "#ffffff", 0),
                  ("e", -9, -9, 7, 6, "a", -0.3), ("e", 9, -9, 7, 6, "a", 0.3),
                  ("e", -9, -9, 2.5, 2, "#c9a8ff", -0.3), ("e", 9, -9, 2.5, 2, "#c9a8ff", 0.3),
                  ("e", 0, -14, 4, 11, "d", 0), ("e", 0, -24, 4.5, 4.5, "a", 0),
                  ("l", -2, -27, -6, -34, 1.3, "d"), ("l", 2, -27, 6, -34, 1.3, "d"),
                  ("e", -6, -34, 1.5, 1.5, "b", 0), ("e", 6, -34, 1.5, 1.5, "b", 0)],
        "eyes": [(-2, -24), (2, -24)], "eye_size": 0.75, "iris": "#ff5aa0",
    },
    "tantan": {"a": "#4a3f4f", "b": "#ffe17a", "d": "#2b232e", "shape": BLOB, "eyes": [(-4, -12), (4, -12)],
               "iris": "#ff9b3a", "mouth": ("cat", 0, -7.5), "blush": [(-8, -8), (8, -8)]},
    "fufu": {"a": "#8fd8e8", "b": "#ffffff", "d": "#4aa2b8", "shape": JELLY, "eyes": [(-4, -13), (4, -13)],
             "gloss": 1.0, "iris": "#2a6b8a", "mouth": ("smile", 0, -10), "blush": [(-8, -11), (8, -11)]},
    "dianli": {
        "a": "#f2d24a", "b": "#fff4b8", "d": "#b08a1a", "iris": "#5a3a10", "mouth": ("cat", 0, -8.5),
        "shape": [("p", [(-12, -12), (-16, -22), (-6, -19)], "d"), ("p", [(-6, -19), (-4, -28), (1, -21)], "d"),
                  ("p", [(1, -21), (6, -29), (7, -19)], "d"), ("p", [(7, -19), (16, -23), (12, -12)], "d"),
                  ("p", [(10, -6), (18, -10), (15, -4), (21, -6)], "d"),
                  ("e", 0, -11, 12, 10, "a", 0), ("e!", 0, -6, 7, 4, "b", 0),
                  ("p?", [(-4, -16), (1, -16), (-1, -12), (3, -12), (-3, -6), (-1, -10), (-4, -10)], "d"),
                  ("e!", -8, -9, 2.2, 1.6, "#ff6b5a", 0), ("e!", 8, -9, 2.2, 1.6, "#ff6b5a", 0)],
        "eyes": [(-4, -13), (4, -13)],
    },
}


def render_fit(sp, size, scale, back):
    """渲染；如果碰到画布边缘（描边会被切掉）就把缩放调小 5% 再试"""
    while True:
        im = render(sp, size, scale, back)
        x0, y0, x1, y1 = im.getbbox()
        if x0 > 0 and y0 > 0 and x1 < size and y1 < size:
            return im
        scale *= 0.95


def make_monsters(out_dir):
    out = out_dir / "monsters"
    out.mkdir(parents=True, exist_ok=True)
    for key, sp in SPECIES.items():
        render_fit(sp, FRONT[0], FRONT[1], back=False).save(out / f"{key}_front.png")
        render_fit(sp, BACK[0], BACK[1], back=True).save(out / f"{key}_back.png")
    return list(SPECIES)
