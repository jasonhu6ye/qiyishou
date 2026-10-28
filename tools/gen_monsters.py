"""奇异兽的像素立绘：每个物种生成正面图（64x64）和背面图（80x80）。

形状用椭圆、多边形和线段描述（单位坐标，原点在脚底中心，y 向上为负），
按像素中心逐点判断是否落在形状内，不做抗锯齿；最后自动加明暗和深色描边。
由 gen_pixel_art.py 调用，输出到 assets/sprites/monsters/。
"""
import math

from PIL import Image

FRONT = (64, 1.25)  # 画布边长, 缩放；脚底在画布底边往上 5 像素处
BACK = (80, 1.6)


def hexc(s, a=255):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (c[3],)


# ------------------------------------------------------------------ 图元
# ("e", x, y, rx, ry, 颜色, 旋转)      椭圆
# ("p", [(x, y), ...], 颜色)            多边形
# ("l", x1, y1, x2, y2, 线宽, 颜色)     线段
# 颜色可以是 "a"（主色）"b"（副色）"d"（暗色）或 "#rrggbb"
# 第一个元素写成 "e!" / "p!" / "l!" 表示只在正面画（脸、肚皮等）


def _inside(prim, u, v):
    kind = prim[0].rstrip("!")
    if kind == "e":
        _, x, y, rx, ry, _c, rot = prim
        du, dv = u - x, v - y
        cr, sr = math.cos(-rot), math.sin(-rot)
        du, dv = du * cr - dv * sr, du * sr + dv * cr
        return (du / rx) ** 2 + (dv / ry) ** 2 <= 1.0
    if kind == "p":
        pts = prim[1]
        hit = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > v) != (yj > v) and u < (xj - xi) * (v - yi) / (yj - yi) + xi:
                hit = not hit
            j = i
        return hit
    if kind == "l":
        _, x1, y1, x2, y2, w, _c = prim
        dx, dy = x2 - x1, y2 - y1
        t = max(0.0, min(1.0, ((u - x1) * dx + (v - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(u - (x1 + t * dx), v - (y1 + t * dy)) <= w / 2
    raise ValueError(kind)


def _color(prim, pal):
    c = prim[5] if prim[0].rstrip("!") in ("e", "l") else prim[2]
    if prim[0].rstrip("!") == "l":
        c = prim[6]
    return hexc(pal[c]) if c in pal else hexc(c)


def render(sp, size, scale, back):
    pal = {"a": sp["a"], "b": sp["b"], "d": sp["d"]}
    s = scale * sp.get("scale", 1.0)
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = im.load()
    ox, oy = size / 2, size - 5
    prims = [p for p in sp["shape"] if not (back and p[0].endswith("!"))]
    if not back:
        for ex, ey in sp.get("eyes", [(-5, -14), (5, -14)]):
            prims.append(("e!", ex, ey, 1.8, 2.4, "#1b1b2b", 0))
    for prim in prims:
        col = _color(prim, pal)
        for py in range(size):
            for pxl in range(size):
                u = (pxl + 0.5 - ox) / s
                v = (py + 0.5 - oy) / s
                if _inside(prim, u, v):
                    px[pxl, py] = col
    if not back:
        # 眼睛高光：每只眼睛右上角一个白点
        for ex, ey in sp.get("eyes", [(-5, -14), (5, -14)]):
            hx, hy = int(ox + (ex + 0.6) * s), int(oy + (ey - 1.0) * s)
            if 0 <= hx < size and 0 <= hy < size:
                px[hx, hy] = (255, 255, 255, 255)
    _auto_shade(im)
    _outline(im, shade(hexc(sp["d"]), 0.45))
    return im


def _auto_shade(im):
    """左上受光：左上邻居透明的像素提亮，右下邻居透明的像素压暗"""
    w, h = im.size
    src = im.copy().load()
    px = im.load()
    for y in range(h):
        for x in range(w):
            c = src[x, y]
            if not c[3] or c[:3] == (27, 27, 43) or c[:3] == (255, 255, 255):
                continue
            up = src[x, y - 1][3] if y > 0 else 0
            left = src[x - 1, y][3] if x > 0 else 0
            down = src[x, y + 1][3] if y < h - 1 else 0
            right = src[x + 1, y][3] if x < w - 1 else 0
            if not up or not left:
                px[x, y] = shade(c, 1.18)
            elif not down or not right:
                px[x, y] = shade(c, 0.78)


def _outline(im, col):
    w, h = im.size
    src = im.copy().load()
    px = im.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3]:
                continue
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3]:
                    px[x, y] = col
                    break


# ------------------------------------------------------------------ 物种
FOX = [
    ("e", 13, -13, 9, 5, "a", -0.7), ("e", 18, -18, 4, 3, "b", -0.7),
    ("p", [(-11, -18), (-8, -30), (-3, -21)], "a"), ("p", [(11, -18), (8, -30), (3, -21)], "a"),
    ("p", [(-9, -21), (-8, -27), (-5, -22)], "d"), ("p", [(9, -21), (8, -27), (5, -22)], "d"),
    ("e", 0, -12, 12, 11, "a", 0), ("e!", 0, -7, 7, 4.5, "b", 0),
    ("e", -6, -1, 3, 2, "d", 0), ("e", 6, -1, 3, 2, "d", 0),
]
FROG = [
    ("e", -7, -19, 5, 5, "a", 0), ("e", 7, -19, 5, 5, "a", 0),
    ("e", 0, -10, 15, 10, "a", 0), ("e!", 0, -6, 9, 4.5, "b", 0),
    ("e", -11, -1, 4, 2, "d", 0), ("e", 11, -1, 4, 2, "d", 0),
]
MOUSE = [
    ("e", -9, -21, 5, 5, "a", 0), ("e", 9, -21, 5, 5, "a", 0),
    ("e", -9, -21, 2.5, 2.5, "b", 0), ("e", 9, -21, 2.5, 2.5, "b", 0),
    ("l", 9, -5, 17, -12, 2, "d"),
    ("e", 0, -11, 11, 11, "a", 0),
    ("e", -1, -25, 2.6, 5.5, "#4fb34f", 0.5), ("e", 3, -26, 2, 4, "#7bd36b", -0.6),
    ("e!", 0, -8, 2, 1.5, "#d77a86", 0),
]
BIRD = [
    ("e", 0, -12, 12, 12, "a", 0),
    ("e", -10, -11, 4.5, 7, "d", 0.3), ("e", 10, -11, 4.5, 7, "d", -0.3),
    ("p", [(-2, -23), (0, -30), (3, -23)], "d"),
    ("e!", 0, -6, 7, 5, "b", 0), ("p!", [(-3, -11), (3, -11), (0, -7)], "#f2a33a"),
    ("l", -4, 0, -4, -3, 2, "#f2a33a"), ("l", 4, 0, 4, -3, 2, "#f2a33a"),
]
WORM = [
    ("e", -12, -5, 6, 5, "d", 0), ("e", -3, -7, 7, 6.5, "a", 0), ("e", 8, -11, 9, 9, "a", 0),
    ("l", 5, -19, 2, -25, 1.3, "d"), ("l", 11, -19, 14, -25, 1.3, "d"),
    ("e", 2, -25, 1.6, 1.6, "d", 0), ("e", 14, -25, 1.6, 1.6, "d", 0),
]
JELLY = [
    ("l", -8, -9, -9, 0, 2, "d"), ("l", -4, -9, -3, 1, 2, "d"), ("l", 0, -9, 0, 0, 2, "d"),
    ("l", 4, -9, 3, 1, 2, "d"), ("l", 8, -9, 9, 0, 2, "d"),
    ("e", 0, -14, 12, 9, "a", 0), ("e", -4, -18, 4, 2, "b", 0),
]
BLOB = [
    ("e", 0, -11, 12, 11, "a", 0),
    ("p", [(-6, -19), (0, -32), (6, -19)], "#ff9b3a"), ("p", [(-3, -20), (0, -27), (3, -20)], "b"),
    ("e!", -7, -7, 2, 1.2, "#ff7a5a", 0), ("e!", 7, -7, 2, 1.2, "#ff7a5a", 0),
]

SPECIES = {
    "huohu": {"a": "#e8743b", "b": "#ffe1a8", "d": "#a8441c", "shape": FOX},
    "huohu2": {
        "a": "#d9502a", "b": "#ffe1a8", "d": "#8a2f12", "scale": 1.15,
        "shape": [("p", [(-9, -20), (-4, -36), (0, -24), (4, -36), (9, -20)], "#ffb03a")] + FOX
        + [("e", 20, -21, 4, 4, "#ffd35a", 0)],
    },
    "paowa": {"a": "#4c9be8", "b": "#d6efff", "d": "#2a6bb0", "shape": FROG, "eyes": [(-7, -20), (7, -20)]},
    "paowa2": {
        "a": "#3a7fd6", "b": "#d6efff", "d": "#1f548f", "scale": 1.15, "eyes": [(-7, -20), (7, -20)],
        "shape": [("p", [(-3, -22), (2, -36), (8, -22)], "b")] + FROG
        + [("e!", -12, -9, 2.5, 1.5, "#ff9fb5", 0), ("e!", 12, -9, 2.5, 1.5, "#ff9fb5", 0)],
    },
    "yeshu": {"a": "#c9b78a", "b": "#f5c2c7", "d": "#8d7a52", "shape": MOUSE},
    "yeshu2": {
        "a": "#a89466", "b": "#f5c2c7", "d": "#6c5a36", "scale": 1.15,
        "shape": MOUSE + [("e", 0, -31, 4.5, 9, "#3f9a3c", 0.25), ("e", -1, -31, 1.5, 7, "#6cc25a", 0.25),
                          ("e", 19, -14, 3.5, 6, "#3f9a3c", -0.6)],
    },
    "yuanniao": {"a": "#b9a3e3", "b": "#f4ecff", "d": "#7a62a8", "shape": BIRD},
    "yuanniao2": {
        "a": "#8f74d1", "b": "#f4ecff", "d": "#55408a", "scale": 1.15,
        "shape": [("e", -15, -16, 5, 10, "d", 0.6), ("e", 15, -16, 5, 10, "d", -0.6),
                  ("p", [(-5, -22), (-7, -33), (-1, -23)], "#ff7a5a"), ("p", [(1, -23), (4, -34), (5, -22)], "#ffb03a")] + BIRD,
    },
    "chongchong": {"a": "#9ad66b", "b": "#e4ffc9", "d": "#5c9a3a", "shape": WORM, "eyes": [(4, -12), (12, -12)]},
    "jianjian": {
        "a": "#cfc27a", "b": "#f0e8b0", "d": "#8a7f40",
        "shape": [("e", 0, -15, 10, 15, "a", 0), ("l", -9, -20, 9, -16, 1.5, "d"), ("l", -9, -11, 9, -7, 1.5, "d"),
                  ("l", 0, -30, 0, -34, 1.5, "d")],
        "eyes": [(-3, -19), (3, -19)],
    },
    "caidie": {
        "a": "#7d5ac9", "b": "#ffd35a", "d": "#3f2a70",
        "shape": [("e", -12, -22, 11, 8, "b", -0.5), ("e", 12, -22, 11, 8, "b", 0.5),
                  ("e", -13, -22, 5, 3.5, "#ff7a5a", -0.5), ("e", 13, -22, 5, 3.5, "#ff7a5a", 0.5),
                  ("e", -9, -9, 7, 6, "a", -0.3), ("e", 9, -9, 7, 6, "a", 0.3),
                  ("e", 0, -14, 4, 11, "d", 0), ("e", 0, -24, 4.5, 4.5, "a", 0),
                  ("l", -2, -27, -6, -34, 1.3, "d"), ("l", 2, -27, 6, -34, 1.3, "d")],
        "eyes": [(-2, -24), (2, -24)],
    },
    "tantan": {"a": "#4a3f4f", "b": "#ffe17a", "d": "#2b232e", "shape": BLOB, "eyes": [(-4, -11), (4, -11)]},
    "fufu": {"a": "#8fd8e8", "b": "#ffffff", "d": "#4aa2b8", "shape": JELLY, "eyes": [(-4, -13), (4, -13)]},
    "dianli": {
        "a": "#f2d24a", "b": "#fff4b8", "d": "#b08a1a",
        "shape": [("p", [(-12, -12), (-16, -22), (-6, -19)], "d"), ("p", [(-6, -19), (-4, -28), (1, -21)], "d"),
                  ("p", [(1, -21), (6, -29), (7, -19)], "d"), ("p", [(7, -19), (16, -23), (12, -12)], "d"),
                  ("p", [(10, -6), (18, -10), (15, -4), (21, -6)], "d"),
                  ("e", 0, -11, 12, 10, "a", 0), ("e!", 0, -7, 7, 4, "b", 0),
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
