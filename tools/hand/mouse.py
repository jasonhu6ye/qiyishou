"""叶芽鼠 → 森叶鼠 → 古木鼠王（#007-#009，草，初始）"""
from kit import Sprite, anim, ell, poly, rot, scale_about

G, Gs, Gh = "#8cd068", "#4f9a3c", "#c4f09a"
L1, L1s = "#3fae4a", "#1f7a34"  # 叶子
C, Cs = "#fff4d8", "#e4cc9a"
BARK, BARKs = "#9a6a3a", "#5e3c1e"
IRIS = "#2f7a24"
LINE = "#1e3018"
PINK = "#ff9aa8"


def leaf(s, x, y, ln, w, ang, c=L1, cs=L1s, vein=True):
    """一片叶子：叶柄在 (x, y)，朝 ang 度方向（0 向上）"""
    with s.group(rot(ang, x, y)):
        s.part(f"M{x},{y} C{x - w},{y - ln * .3} {x - w * .8},{y - ln * .8} {x},{y - ln} C{x + w * .8},{y - ln * .8} {x + w},{y - ln * .3} {x},{y} Z", c, cs)
        if vein:
            s.line(f"M{x},{y - 1} L{x},{y - ln * .8}", cs, 1.0)


def yeshu(f):
    a = anim(f)
    s = Sprite(LINE)
    s.lid_color = Gs
    b = a["breath"]
    # 细长尾巴，尾尖一片叶子
    with s.group(rot(a["sway"] * 8, 62, 84)):
        s.line("M60,85 C74,88 84,80 82,66 C81,58 76,54 72,54", Gs, 3.2)
        s.line("M60,85 C74,88 84,80 82,66 C81,58 76,54 72,54", G, 1.6)
        leaf(s, 72, 55, 14, 6, -40)
    s.part(ell(55, 86, 7, 3), Gs, "#3a7a2c")
    with s.group(scale_about(1 + .02 * b, 1 + .03 * b, 46, 89)):
        s.part("M32,89 C26,80 28,64 40,60 C50,57 60,62 62,72 C64,82 60,88 56,89 Z", G, Gs, Gh)
        s.part("M34,72 C36,64 46,64 50,70 C52,80 48,87 42,88 C36,88 33,80 34,72 Z", C, Cs, line="none")
        s.part(ell(36, 87, 5.5, 2.6), G, Gs)
        s.part(ell(50, 88, 5.5, 2.6), G, Gs)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        # 叶子耳朵（远的那只先画）
        leaf(s, 30, 40, 18, 8, -38, Gs, "#3a7a2c", False)
        s.part("M20,50 C20,38 30,30 42,30 C55,30 62,38 62,48 C62,58 54,64 42,64 C30,64 20,60 20,50 Z", G, Gs, Gh)
        s.part("M18,52 C18,58 26,62 34,61 C36,56 32,50 26,49 C22,49 19,50 18,52 Z", C, Cs, line="none")
        s.flat(ell(19, 51.5, 2.6, 2), PINK, LINE, .8)
        with s.group(rot(-10 if a["f"] in (18, 19) else 0, 52, 34)):
            leaf(s, 52, 36, 22, 10, 30)
        # 头顶小芽
        with s.group(rot(a["sway"] * 6, 42, 31)):
            s.line("M42,31 L42,24", L1s, 1.6)
            leaf(s, 42, 25, 9, 4, -45)
            leaf(s, 42, 25, 10, 4.5, 40)
        s.eye(29, 46, 3.6, 4.6, IRIS, a["blink"])
        s.eye(43, 45.5, 4.6, 5.6, IRIS, a["blink"])
        s.line("M23,57 Q25.5,59 28,57")
        s.flat("M24.5,57.5 L25.5,60 L26.5,57.5 Z", "#ffffff")
        s.flat(ell(51, 55, 3, 1.6), PINK)
        # 胡须
        s.line("M16,54 L9,52", "#ffffff", .8)
        s.line("M16,56 L10,58", "#ffffff", .8)
    return s


def yeshu2(f):
    a = anim(f)
    s = Sprite(LINE)
    s.fit = 0.92
    s.lid_color = Gs
    b = a["breath"]
    # 大叶子尾巴竖在背后
    with s.group(rot(a["sway"] * 6, 70, 66)):
        s.line("M66,70 C78,70 84,60 82,46", Gs, 3.5)
        leaf(s, 82, 48, 30, 12, 15)
        leaf(s, 82, 48, 22, 9, -20, "#5fc04a", L1s)
    s.part("M60,60 C70,60 74,70 72,80 L74,89 L64,89 L62,78 C58,72 56,64 60,60 Z", Gs, "#3a7a2c")
    s.part("M30,64 L36,64 L35,89 L29,89 Z", Gs, "#3a7a2c")
    with s.group(f"translate(0 {-b * .7:.2f})"):
        s.part("M22,58 C24,46 38,42 52,44 C66,45 74,52 74,62 C74,70 66,74 52,74 C38,74 22,70 22,58 Z", G, Gs, Gh)
        s.part("M26,64 C32,72 46,75 58,73 C48,68 36,66 26,64 Z", C, Cs, line="none")
        # 叶子围脖
        for i, ang in enumerate((-70, -40, -10, 20)):
            leaf(s, 30 + i * 3, 50, 12, 5, 180 + ang, L1 if i % 2 else "#5fc04a", L1s)
    s.part("M24,60 C30,60 32,66 31,72 L31,88 L23,88 L23,70 C21,66 21,62 24,60 Z", G, Gs, Gh)
    s.part(ell(26, 89, 5, 2.3), C, Cs)
    s.part("M56,58 C66,58 70,66 68,74 L69,88 L61,88 L60,74 C56,70 54,62 56,58 Z", G, Gs, Gh)
    s.part(ell(64, 89, 5, 2.3), C, Cs)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        leaf(s, 22, 26, 22, 9, -35, Gs, "#3a7a2c", False)
        s.part("M8,38 C8,26 18,18 30,18 C43,18 50,26 50,36 C50,46 42,52 30,52 C18,52 8,48 8,38 Z", G, Gs, Gh)
        s.part("M4,40 C4,46 12,50 22,49 C24,44 20,38 13,37 C9,37 5,38 4,40 Z", C, Cs, line="none")
        s.flat(ell(5, 39.5, 2.6, 2), PINK, LINE, .8)
        with s.group(rot(-10 if a["f"] in (18, 19) else 0, 40, 22)):
            leaf(s, 40, 24, 26, 11, 25)
        with s.group(rot(a["sway"] * 5, 30, 19)):
            leaf(s, 30, 20, 14, 5, -30, "#5fc04a", L1s)
            leaf(s, 30, 20, 16, 6, 15)
        s.eye(17, 34, 3.4, 4.2, IRIS, a["blink"], lid=.2)
        s.eye(30, 33.5, 4.4, 5.2, IRIS, a["blink"], lid=.2)
        s.line("M9,45 Q11.5,47 14,45")
        s.line("M2,42 L-4,40", "#ffffff", .8)
    return s


def d009(f):
    a = anim(f)
    s = Sprite(LINE)
    s.fit = 0.86
    s.lid_color = Gs
    b = a["breath"]
    sw = a["sway"]
    # 背后巨大的叶子尾巴
    with s.group(rot(sw * 4, 64, 70)):
        s.line("M62,72 C76,72 86,62 86,46", BARKs, 4)
        leaf(s, 86, 50, 36, 15, 10)
        leaf(s, 86, 50, 26, 10, -30, "#5fc04a", L1s)
        leaf(s, 86, 50, 26, 10, 45, "#5fc04a", L1s)
    s.part("M54,66 C62,66 64,76 62,88 L70,89 L54,89 C52,82 50,72 54,66 Z", Gs, "#3a7a2c")
    s.part("M58,36 C68,40 72,50 70,58 L64,60 C64,52 60,46 54,44 Z", Gs, "#3a7a2c")
    with s.group(f"translate(0 {-b * .8:.2f})"):
        s.part("M28,46 C26,34 34,28 46,28 C58,28 66,36 64,50 C63,64 58,74 46,74 C34,74 28,64 28,46 Z", G, Gs, Gh)
        s.part("M34,52 C36,42 54,42 56,52 C56,66 52,72 46,72 C38,72 34,64 34,52 Z", C, Cs, line="none")
        # 树皮铠甲：肩甲和腰带
        s.part("M24,34 C28,26 40,26 44,32 C40,40 30,42 24,34 Z", BARK, BARKs, "#c89a62")
        s.part("M48,30 C54,24 66,28 66,36 C60,42 50,40 48,30 Z", BARK, BARKs, "#c89a62")
        s.part("M30,62 C40,66 54,66 62,62 L62,67 C54,71 40,71 30,67 Z", BARK, BARKs)
        s.line("M34,30 L38,36", BARKs, 1)
        s.line("M56,30 L58,36", BARKs, 1)
    s.part("M30,30 C20,36 16,46 18,56 L24,58 C24,48 28,42 34,38 Z", G, Gs, Gh)
    s.part(ell(20, 60, 5.5, 5), BARK, BARKs)
    s.part("M30,66 C24,68 22,78 24,88 L18,89 L36,89 C38,82 38,72 30,66 Z", G, Gs, Gh)
    s.part(ell(26, 89, 7, 2.4), BARK, BARKs)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        # 树枝鹿角，挂着叶子
        for x0, dirn in ((30, -1), (46, 1)):
            s.line(f"M{x0},14 C{x0 + dirn * 2},6 {x0 + dirn * 6},2 {x0 + dirn * 10},-2", BARKs, 3.2)
            s.line(f"M{x0},14 C{x0 + dirn * 2},6 {x0 + dirn * 6},2 {x0 + dirn * 10},-2", BARK, 1.6)
            s.line(f"M{x0 + dirn * 3},6 L{x0 + dirn * 1},0", BARKs, 2.2)
            leaf(s, x0 + dirn * 10, -1, 9, 4, dirn * 50, "#5fc04a", L1s)
        s.part("M16,24 C16,14 26,8 38,8 C50,8 56,16 56,24 C56,34 48,38 36,38 C24,38 16,34 16,24 Z", G, Gs, Gh)
        s.part("M12,26 C12,32 20,36 30,35 C32,30 28,24 21,23 C16,23 13,24 12,26 Z", C, Cs, line="none")
        s.flat(ell(13, 25.5, 2.6, 2), PINK, LINE, .8)
        leaf(s, 50, 14, 20, 9, 35)
        s.eye(24, 21, 3.2, 3.8, IRIS, a["blink"], lid=.35)
        s.eye(37, 20.5, 4.2, 4.8, IRIS, a["blink"], lid=.35)
        s.line("M17,31 Q19.5,33 22,31")
        s.line("M10,28 L4,26", "#ffffff", .8)
    return s


SPECIES = {"yeshu": yeshu, "yeshu2": yeshu2, "d009": d009}
