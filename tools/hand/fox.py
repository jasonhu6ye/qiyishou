"""焰尾狐 → 烈焰狐 → 炽阳九尾（#001-#003，火，初始）"""
from kit import Sprite, anim, ell, poly, rot, scale_about

O, Os, Oh = "#f07a2a", "#c4521c", "#ffab6a"
C, Cs = "#fff2d8", "#e8c49a"
EAR = "#7a2a1c"
F1, F2, F3 = "#ff5a1a", "#ffa02a", "#ffe066"
IRIS = "#c8381a"
LINE = "#3a1810"


def LEG(x, top, bottom, w):
    """前腿：上粗下细，脚腕处收一下"""
    return (f"M{x - w / 2},{top} C{x - w / 2 - .5},{top + (bottom - top) * .5} {x - w * .35},{bottom - 6} {x - w * .4},{bottom} "
            f"L{x + w * .45},{bottom} C{x + w * .4},{bottom - 6} {x + w / 2 + .5},{top + (bottom - top) * .5} {x + w / 2},{top} Z")


def HIND(x, top, bottom):
    """后腿：大腿鼓起来，小腿往后折"""
    return (f"M{x - 6},{top} C{x + 4},{top - 2} {x + 8},{top + 8} {x + 5},{top + 15} C{x + 4},{top + 19} {x + 3},{bottom - 6} {x + 3},{bottom} "
            f"L{x - 3},{bottom} C{x - 2},{bottom - 7} {x - 2},{top + 16} {x - 5},{top + 12} C{x - 8},{top + 8} {x - 8},{top + 2} {x - 6},{top} Z")


def flame(s, x, y, h, flick, lean=0.0):
    """一团火：底在 (x, y)，高 h"""
    k = 1 + .1 * flick
    with s.group(f"{rot(lean, x, y)} {scale_about(1, k, x, y)}"):
        w = h * .5
        s.part(f"M{x - w},{y} C{x - w * 1.3},{y - h * .5} {x - w * .4},{y - h * .6} {x - w * .2},{y - h} "
               f"C{x + w * .2},{y - h * .65} {x + w * .7},{y - h * .75} {x + w * .75},{y - h * .4} C{x + w * 1.1},{y - h * .1} {x + w * .6},{y + 1} {x},{y + 1} Z",
               F2, F1, line=LINE)
        s.flat(f"M{x - w * .45},{y - 1} C{x - w * .6},{y - h * .35} {x - w * .1},{y - h * .45} {x - w * .05},{y - h * .7} "
               f"C{x + w * .25},{y - h * .4} {x + w * .45},{y - h * .3} {x + w * .35},{y - 1} Z", F3)


def huohu(f):
    a = anim(f)
    s = Sprite(LINE)
    s.lid_color = Os
    b = a["breath"]
    # 尾巴：绕尾根摆动
    with s.group(rot(a["sway"] * 7, 58, 80)):
        s.part("M56,82 C70,88 88,78 87,60 C86,48 80,40 72,38 C76,50 75,60 67,67 C62,71 58,73 54,75 Z", O, Os, Oh)
        s.part("M72,38 C80,39 87,48 87,58 C83,52 79,49 73,47 Z", C, Cs)
        flame(s, 76, 40, 13, a["flick"], -10)
    # 远侧前腿
    s.part("M50,74 L56,74 L56,88 L50,88 Z", Os, "#a8441a")
    with s.group(scale_about(1 + .02 * b, 1 + .03 * b, 50, 89)):
        # 身体（坐姿，梨形）
        s.part("M36,89 C30,80 32,64 42,58 C50,54 61,58 65,66 C69,75 68,85 62,89 Z", O, Os, Oh)
        # 后腿大腿和脚
        s.part(ell(60, 80, 9, 8.5), O, Os)
        s.part(ell(59, 88, 7, 2.6), C, Cs)
        # 胸前白毛
        s.part("M37,62 C33,70 35,80 41,85 C46,79 48,69 46,60 Z", C, Cs, line="none")
        # 近侧前腿
        s.part("M40,71 L47,71 L47,87 L40,87 Z", O, Os)
        s.part(ell(43, 88, 5, 2.6), C, Cs)
    # 头（随呼吸轻点头）
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        for x0, flip in ((28, -1), (58, 1)):
            tw = -10 * flip if (a["f"] in (18, 19) and flip > 0) else 0
            with s.group(rot(tw, x0, 30)):
                s.part(poly((x0 - 7, 31), (x0 + flip * 4, 7), (x0 + 7, 29)), O, Os, Oh)
                s.flat(poly((x0 - 4, 29), (x0 + flip * 3.5, 13), (x0 + 4, 28)), EAR)
        s.part("M24,44 C24,32 33,26 43,26 C53,26 62,32 62,44 C62,52 58,57 52,60 L48,63 L46,59 L43,63 L40,59 L38,63 L34,60 C28,57 24,52 24,44 Z",
               O, Os, Oh)
        s.part(ell(43, 52.5, 8.5, 6), C, Cs, line="none")
        s.flat(ell(43, 49.5, 2.4, 1.8), LINE)
        flame(s, 43, 28, 9, a["flick"] * -1, 0)
        s.eye(35.5, 43, 4.2, 5.2, IRIS, a["blink"])
        s.eye(50.5, 43, 4.2, 5.2, IRIS, a["blink"])
        s.line("M40,54 Q43,56.5 46,54")
        s.flat(ell(29, 51, 2.8, 1.5), "#ff8a7a")
        s.flat(ell(57, 51, 2.8, 1.5), "#ff8a7a")
    return s


def huohu2(f):
    a = anim(f)
    s = Sprite(LINE)
    s.fit = 0.95
    s.lid_color = Os
    b = a["breath"]
    with s.group(rot(a["sway"] * 6, 70, 58)):
        s.part("M68,60 C80,58 92,48 91,34 C90,26 86,22 80,22 C84,32 82,42 74,48 C70,51 66,54 64,57 Z", O, Os, Oh)
        s.part("M80,22 C87,22 92,30 91,38 C88,33 84,30 80,29 Z", C, Cs)
        flame(s, 84, 25, 17, a["flick"], -5)
    # 远侧两条腿
    s.part(LEG(31, 64, 88, 6), Os, "#a8441a")
    s.part(HIND(66, 60, 88), Os, "#a8441a")
    with s.group(f"translate(0 {-b * .6:.2f})"):
        s.part("M24,56 C26,46 40,42 54,44 C66,45 74,50 74,58 C74,66 66,71 52,71 C38,71 24,68 24,56 Z", O, Os, Oh)
        s.part("M28,62 C34,70 48,72 58,70 C50,66 38,64 28,62 Z", C, Cs, line="none")
        # 脖子上的火焰鬃毛
        for i, (x, y, h, ln) in enumerate(((40, 48, 12, -25), (47, 46, 14, -10), (54, 47, 12, 5))):
            flame(s, x, y, h, a["flick"] * (1 if i % 2 else -1), ln)
    s.part(LEG(26, 60, 87, 7), O, Os, Oh)
    s.part(ell(25, 88, 4.8, 2.4), C, Cs)
    s.part(HIND(61, 56, 87), O, Os, Oh)
    s.part(ell(61, 88, 4.8, 2.4), C, Cs)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        for x0, flip in ((16, -1), (40, 1)):
            tw = -10 * flip if (a["f"] in (18, 19) and flip > 0) else 0
            with s.group(rot(tw, x0, 20)):
                s.part(poly((x0 - 6.5, 20), (x0 + flip * 4, -2 + 3), (x0 + 6.5, 18)), O, Os, Oh)
                s.flat(poly((x0 - 3.5, 18), (x0 + flip * 3.5, 6), (x0 + 3.5, 17)), EAR)
        s.part("M10,34 C10,24 18,18 28,18 C38,18 46,24 46,34 C46,42 42,46 37,48 L34,51 L32,47 L28,51 L24,47 L22,51 L19,48 C14,46 10,42 10,34 Z", O, Os, Oh)
        s.part(ell(28, 42, 7.5, 5.2), C, Cs, line="none")
        s.flat(ell(28, 39.5, 2.2, 1.6), LINE)
        s.eye(21.5, 33, 3.8, 4.6, IRIS, a["blink"], lid=.25)
        s.eye(34.5, 33, 3.8, 4.6, IRIS, a["blink"], lid=.25)
        s.line("M25,44 Q28,46 31,44")
    return s


def d003(f):
    a = anim(f)
    s = Sprite(LINE)
    s.fit = 0.94
    s.lid_color = Os
    b = a["breath"]
    G, Gs = "#ffd36a", "#e0a03a"  # 金色鬃毛
    # 五条（看得见的）火焰尾巴扇形展开
    for i, ang in enumerate((-48, -26, -4, 18, 40)):
        sw = a["sway"] * (6 + i)
        with s.group(f"{rot(ang + sw, 68, 62)}"):
            s.part("M66,64 C70,52 72,40 70,28 C76,34 80,46 76,58 C74,62 72,64 70,66 Z", O if i % 2 else Os, Os if i % 2 else "#a8441a", line=LINE)
            flame(s, 71, 31, 12 + (i % 2) * 3, a["flick"] * (1 if i % 2 else -1), 0)
    s.part(LEG(35, 66, 89, 5.5), Os, "#a8441a")
    s.part(HIND(69, 62, 89), Os, "#a8441a")
    with s.group(f"translate(0 {-b * .6:.2f})"):
        s.part("M28,58 C30,48 44,45 58,47 C70,48 76,54 76,61 C76,68 68,73 54,73 C40,73 28,70 28,58 Z", O, Os, Oh)
        s.part("M32,64 C38,71 50,74 60,72 C52,68 42,66 32,64 Z", C, Cs, line="none")
    s.part(LEG(30, 62, 88, 6), O, Os, Oh)
    s.part(ell(29, 89, 4.4, 2.2), F3, F2)
    s.part(HIND(64, 58, 88), O, Os, Oh)
    s.part(ell(64, 89, 4.4, 2.2), F3, F2)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        # 金色鬃毛领
        s.part("M14,42 C10,48 10,54 13,58 L16,56 L17,63 L22,59 L24,67 L28,61 L32,67 L34,59 L39,63 L40,56 L44,58 C46,50 42,44 38,42 Z", G, Gs, "#fff0b0")
        for x0, flip in ((16, -1), (40, 1)):
            tw = -10 * flip if (a["f"] in (18, 19) and flip > 0) else 0
            with s.group(rot(tw, x0, 20)):
                s.part(poly((x0 - 6.5, 20), (x0 + flip * 4, -2 + 3), (x0 + 6.5, 18)), O, Os, Oh)
                s.flat(poly((x0 - 3.5, 18), (x0 + flip * 3.5, 6), (x0 + 3.5, 17)), EAR)
        s.part("M10,34 C10,24 18,18 28,18 C38,18 46,24 46,34 C46,42 42,46 37,48 L34,51 L32,47 L28,51 L24,47 L22,51 L19,48 C14,46 10,42 10,34 Z", O, Os, Oh)
        s.part(ell(28, 42, 7.5, 5.2), C, Cs, line="none")
        s.flat(ell(28, 39.5, 2.2, 1.6), LINE)
        # 额头金色火焰冠
        flame(s, 28, 20, 11, a["flick"], 0)
        s.flat(poly((24, 25), (28, 21), (32, 25), (28, 28)), G, LINE)
        s.eye(21.5, 33, 3.6, 4.2, "#e8a020", a["blink"], lid=.35)
        s.eye(34.5, 33, 3.6, 4.2, "#e8a020", a["blink"], lid=.35)
        s.line("M25,44 Q28,45.5 31,44")
    return s


SPECIES = {"huohu": huohu, "huohu2": huohu2, "d003": d003}
