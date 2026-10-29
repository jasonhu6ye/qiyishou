"""泡泡蛙 → 巨浪蛙 → 怒涛蛙皇（#004-#006，水，初始）"""
import math

from kit import Sprite, anim, ell, rot, scale_about

B, Bs, Bh = "#4c9be8", "#2c68b4", "#8fccff"
W, Ws = "#eaf6ff", "#b4d4ee"
FIN, FINs = "#7fe0e8", "#3fa8c0"
DK = "#1c4a8a"
IRIS = "#1b4f9a"
LINE = "#14284a"
PINK = "#ff9ab0"


def bubble(s, x, y, r):
    s.flat(ell(x, y, r, r), "#d8f2ff", LINE, 1.0)
    s.flat(ell(x - r * .35, y - r * .35, r * .3, r * .25), "#ffffff")
    s.flat(ell(x + r * .3, y + r * .4, r * .15, r * .12), "#ffffff")


def paowa(f):
    a = anim(f)
    s = Sprite(LINE)
    s.lid_color = Bs
    b = a["breath"]
    # 泡泡在头顶上浮动
    bubble(s, 66, 30 - a["sway"] * 2.5, 6.5)
    bubble(s, 74, 20 - a["sway"] * 2, 3.5)
    s.part(ell(70, 82, 9, 7), Bs, DK)  # 后腿
    with s.group(scale_about(1 + .04 * b, 1 - .03 * b, 48, 89)):
        s.part("M21,78 C17,63 28,52 46,52 C64,52 77,62 75,76 C74,86 64,89 48,89 C32,89 23,86 21,78 Z", B, Bs, Bh)
        s.part("M29,80 C33,71 58,70 67,78 C62,87 36,88 29,80 Z", W, Ws, line="none")
        # 眼睛鼓包
        s.part(ell(35, 52, 9, 8.5), B, Bs, Bh)
        s.part(ell(57, 50, 10.5, 9.5), B, Bs, Bh)
        s.eye(35, 51, 4.6, 5.4, IRIS, a["blink"])
        s.eye(57, 49.5, 5.6, 6.4, IRIS, a["blink"])
        s.line("M27,66 Q42,76 62,65", LINE, 1.2)
        s.flat(ell(25, 65, 3, 1.8), PINK)
        s.flat(ell(66, 64, 3, 1.8), PINK)
        # 背上三个浅色斑点
        for x, y, r in ((62, 60, 2.2), (68, 66, 1.8), (44, 58, 1.6)):
            s.flat(ell(x, y, r, r * .8), Bh)
    s.part(ell(30, 88, 6.5, 2.8), B, Bs)
    s.part(ell(53, 89, 6.5, 2.8), B, Bs)
    for x in (26, 30, 34, 49, 53, 57):
        s.flat(ell(x, 88.5, 1.2, 1), Bh)
    return s


def paowa2(f):
    a = anim(f)
    s = Sprite(LINE)
    s.lid_color = Bs
    b = a["breath"]
    # 远侧后腿
    s.part("M66,70 C80,66 88,76 84,86 L88,89 L70,89 C66,84 62,78 66,70 Z", Bs, DK)
    with s.group(scale_about(1 + .03 * b, 1 - .02 * b, 46, 89)):
        s.part("M18,70 C16,52 30,40 48,40 C66,40 78,52 76,70 C75,84 64,89 46,89 C30,89 19,84 18,70 Z", B, Bs, Bh)
        s.part("M24,74 C28,60 56,58 66,70 C64,84 34,88 24,74 Z", W, Ws, line="none")
        for i in range(3):
            s.line(f"M{30 + i * 2},{70 + i * 5} Q46,{66 + i * 5} {62 - i * 2},{70 + i * 5}", Ws, 1.0)
        # 头顶浪花鳍（三道弯）
        with s.group(rot(a["sway"] * 4, 48, 40)):
            s.part("M34,42 C30,30 38,22 44,26 C42,18 52,12 56,20 C58,12 70,14 68,26 C74,26 76,36 66,42 Z", FIN, FINs, "#c8fbff")
        s.part(ell(32, 42, 9, 8.5), B, Bs, Bh)
        s.part(ell(56, 40, 10.5, 9.5), B, Bs, Bh)
        s.eye(32, 41, 4.4, 5.2, IRIS, a["blink"], lid=.18)
        s.eye(56, 39.5, 5.4, 6.2, IRIS, a["blink"], lid=.18)
        s.line("M22,56 Q40,66 62,55", LINE, 1.3)
        s.flat(ell(21, 55, 3, 1.8), PINK)
        # 两侧蓝色条纹
        for x, y in ((70, 54), (73, 62), (72, 71)):
            s.flat(ell(x, y, 3.2, 1.5), DK)
    # 近侧后腿和前臂
    s.part("M60,72 C74,68 82,78 78,86 L82,89 L62,89 C58,84 56,78 60,72 Z", B, Bs, Bh)
    s.part("M24,62 C18,68 18,80 22,88 L32,89 C30,82 30,72 32,66 Z", B, Bs)
    for x in (21, 25, 29, 66, 71, 76):
        s.flat(ell(x, 88.6, 1.3, 1), Bh)
    return s


def d006(f):
    a = anim(f)
    s = Sprite(LINE)
    s.fit = 0.88
    s.lid_color = Bs
    b = a["breath"]
    sw = a["sway"]
    # 背后水流披风
    with s.group(rot(sw * 3, 60, 30)):
        s.part("M54,26 C74,26 90,40 88,62 C87,74 80,84 72,88 C76,76 74,64 66,58 C70,70 66,80 58,86 C60,72 56,58 50,50 Z", FIN, FINs, "#c8fbff")
    # 远侧腿和手臂
    s.part("M52,70 C60,70 64,78 62,88 L70,89 L52,89 C50,84 48,76 52,70 Z", Bs, DK)
    s.part("M60,40 C70,44 74,54 72,62 L66,64 C66,56 62,50 56,48 Z", Bs, DK)
    with s.group(f"translate(0 {-b * .8:.2f})"):
        # 身体（直立）
        s.part("M26,52 C24,36 34,28 46,28 C60,28 68,38 66,54 C66,68 62,76 46,76 C32,76 26,68 26,52 Z", B, Bs, Bh)
        s.part("M32,56 C34,46 56,44 60,56 C60,70 54,74 46,74 C38,74 32,68 32,56 Z", W, Ws, line="none")
        for i in range(3):
            s.line(f"M{36 + i},{56 + i * 6} Q46,{53 + i * 6} {56 - i},{56 + i * 6}", Ws, 1.0)
        # 王冠一样的浪花鳍
        with s.group(rot(sw * 3, 46, 20)):
            s.part("M30,22 L28,6 L36,14 L40,2 L46,12 L52,0 L56,12 L64,4 L62,22 Z", FIN, FINs, "#c8fbff")
            s.flat(ell(46, 17, 3, 3), "#ffe066", LINE)
        # 头
        s.part("M20,28 C18,16 30,12 44,12 C60,12 70,18 68,30 C66,40 56,42 44,42 C30,42 22,38 20,28 Z", B, Bs, Bh)
        s.part(ell(28, 16, 8, 7.5), B, Bs, Bh)
        s.part(ell(50, 14, 9.5, 8.5), B, Bs, Bh)
        s.eye(28, 15.5, 4, 4.6, IRIS, a["blink"], lid=.32)
        s.eye(50, 14, 5, 5.6, IRIS, a["blink"], lid=.32)
        s.line("M22,33 Q38,40 58,32", LINE, 1.4)
        s.flat("M30,34 L32,38 L34,35 Z", "#ffffff")
        for x, y in ((62, 26), (64, 33)):
            s.flat(ell(x, y, 3, 1.4), DK)
    # 近侧粗壮手臂，攥拳
    s.part("M28,40 C18,44 14,54 16,62 L22,64 C22,56 26,50 32,48 Z", B, Bs, Bh)
    s.part(ell(19, 66, 5.5, 5), B, Bs, Bh)
    # 近侧腿：青蛙腿蹲着
    s.part("M30,70 C20,70 16,80 20,86 L16,89 L36,89 C38,82 38,74 30,70 Z", B, Bs, Bh)
    for x in (17, 22, 27, 56, 61, 66):
        s.flat(ell(x, 88.7, 1.4, 1), Bh)
    return s


SPECIES = {"paowa": paowa, "paowa2": paowa2, "d006": d006}
