"""#076-#100：月精、灵荆貂、影影蜂、汐汐螺、火火蜗、芝芝蝶、斗斗牛、云鹤、冻蛾、小翔鸟、砾螺、小汐菇、涟涟鲸、震鳄"""
import math

from kit import Sprite, anim, ell, poly, rot, scale_about
from fox import HIND, LEG
from legends1 import flame
from legends2 import star
from mouse import leaf
from frog import bubble
from early1 import hop, smoke
from mid1 import float_y, spiral, bat_wing


# ================================================================== 076 月精（妖精）
def d076(f):
    a = anim(f)
    LINE = "#2a1e3a"
    s = Sprite(LINE)
    s.lid_color = "#c8a040"
    M = ("#fff0a0", "#e0b850", "#ffffff")
    y0 = float_y(a, 3)
    s.flat(ell(48, 89, 12 + y0, 2), "#d0c8d8")
    with s.group(f"translate(0 {y0:.2f})"):
        # 背后的弯月
        s.part("M60,22 C80,30 84,58 66,72 C76,58 74,36 60,22 Z", *M)
        # 薄纱翅膀
        for side in (-1, 1):
            with s.group(rot(side * a["flap"] * 10, 48 + side * 6, 52)):
                s.part(ell(48 + side * 16, 46, 10, 6), "#f0e8ff", "#c0b0e8")
                s.part(ell(48 + side * 14, 58, 7, 4), "#f0e8ff", "#c0b0e8")
        # 小裙子身体
        s.part("M40,56 C38,64 36,70 34,76 C42,80 54,80 62,76 C60,70 58,64 56,56 Z", "#c8b0ff", "#8a70d0")
        s.part(ell(48, 44, 13, 12), *M)
        # 月牙发饰
        s.part("M38,34 C36,26 42,20 50,20 C44,24 42,30 44,36 Z", "#c8b0ff", "#8a70d0")
        s.eye(43, 44, 3, 3.8, "#8a70d0", a["blink"])
        s.eye(53, 44, 3, 3.8, "#8a70d0", a["blink"])
        s.flat(ell(39, 49, 2, 1.1), "#ffa8c8")
        s.flat(ell(57, 49, 2, 1.1), "#ffa8c8")
        s.line("M46.5,50 Q48,51 49.5,50")
        # 星星魔杖
        with s.group(rot(a["sway"] * 10, 30, 66)):
            s.line("M30,66 L24,52", "#e0b850", 1.6)
            s.flat(star(24, 50, 4.5, 2), M[0], LINE, .8)
    for i in range(3):
        t = (a["f"] / 24 + i / 3) % 1
        s.flat(star(20 + i * 26, 20 + t * 50, 1.8, .8), "#ffffff", LINE, .5)
    return s


# ================================================================== 077 灵荆貂（普通/草）
def d077(f):
    a = anim(f)
    LINE = "#2a1a10"
    s = Sprite(LINE)
    s.fit = .95
    s.lid_color = "#7a5030"
    B = ("#c89a6a", "#8a6038", "#ecc89a")
    C = ("#fff4e0", "#e0c8a0")
    b = a["breath"]
    # 毛茸茸的长尾巴，尾巴上缠着荆藤
    with s.group(rot(a["sway"] * 8, 70, 68)):
        s.part("M66,70 C80,72 92,62 90,48 C88,40 82,38 78,40 C84,48 82,58 70,62 Z", *B)
        s.line("M70,66 C78,64 86,58 86,48", "#4a8a3a", 1.6)
        for x, y in ((76, 64), (84, 56), (86, 48)):
            s.flat(poly((x, y), (x + 2, y - 2), (x + 1, y + 1)), "#2a6a2a")
        s.flat(ell(86, 44, 2.4, 2.4), "#ff7aa8", LINE, .7)
    # 细长的身体，矮腿
    s.part(LEG(34, 72, 89, 5), B[1], "#5a3a1a")
    s.part(LEG(68, 70, 89, 5), B[1], "#5a3a1a")
    with s.group(f"translate(0 {-b * .7:.2f})"):
        s.part("M22,66 C22,58 34,54 50,56 C66,57 74,60 74,68 C74,76 64,78 48,78 C32,78 22,74 22,66 Z", *B)
        s.part("M26,70 C34,76 48,77 60,76 C50,72 38,71 26,70 Z", *C, line="none")
    s.part(LEG(30, 70, 88, 6), *B)
    s.part(LEG(64, 68, 88, 6), *B)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        # 荆藤围巾
        s.part("M16,54 C22,62 36,62 42,54 L42,58 C36,66 22,66 16,58 Z", "#5aa84a", "#2a6a2a")
        for x in (18, 24, 30, 36, 40):
            s.flat(poly((x, 60), (x + 1, 63), (x + 2, 60)), "#2a6a2a")
        leaf(s, 40, 58, 9, 4, 120, "#5aa84a", "#2a6a2a")
        for side in (-1, 1):
            tw = 8 if (a["f"] in (18, 19) and side > 0) else 0
            with s.group(rot(tw, 29 + side * 10, 38)):
                s.part(ell(29 + side * 10, 38, 5, 5), *B)
                s.part(ell(29 + side * 10, 38, 2.6, 2.6), "#ffb0b0", "#d08080", line="none")
        s.part("M16,48 C16,40 22,36 29,36 C36,36 42,40 42,48 C42,56 36,60 29,60 C22,60 16,56 16,48 Z", *B)
        s.part("M20,52 C22,46 36,46 38,52 C36,58 22,58 20,52 Z", *C, line="none")
        s.flat(ell(29, 51, 1.8, 1.3), LINE)
        s.eye(23.5, 46, 3, 3.6, "#3a2a1a", a["blink"])
        s.eye(34.5, 46, 3, 3.6, "#3a2a1a", a["blink"])
        s.line("M27,54 Q29,55.5 31,54")
    return s


# ================================================================== 影影蜂线（幽灵/虫）
SHD = ("#5a4a7a", "#34284e", "#8a7ab0")
GLW = "#c0ff7a"


def stinger_wisp(s, a, x, y, ln):
    with s.group(rot(a["sway"] * 10, x, y)):
        s.part(f"M{x - 4},{y} C{x - 2},{y + ln * .5} {x + 2},{y + ln * .7} {x + a['sway'] * 3},{y + ln} C{x + 4},{y + ln * .5} {x + 4},{y + ln * .2} {x + 4},{y} Z", "#d8f0ff", "#9ab0d8")


def d078(f):
    a = anim(f)
    LINE = "#140e20"
    s = Sprite(LINE)
    s.lid_color = SHD[1]
    y0 = float_y(a, 3)
    s.flat(ell(48, 89, 10 + y0, 2), "#c0b8d0")
    with s.group(f"translate(0 {y0 - 4:.2f})"):
        for side in (-1, 1):
            with s.group(rot(side * a["flap"] * 25, 48 + side * 6, 52)):
                s.part(ell(48 + side * 16, 46, 10, 6), "#e8f0ff", "#a8b8e0")
        stinger_wisp(s, a, 48, 72, 14)
        s.part(ell(48, 66, 11, 10), *SHD)
        for y in (62, 68):
            s.line(f"M38,{y} Q48,{y + 3} 58,{y}", GLW, 2)
        for side in (-1, 1):
            s.line(f"M{48 + side * 4},40 C{48 + side * 6},34 {48 + side * 10},32 {48 + side * 12},32", LINE, 1.2)
            s.flat(ell(48 + side * 12, 32, 2, 2), GLW, LINE, .7)
        s.part(ell(48, 50, 12, 11), *SHD)
        s.eye(43.5, 50, 3.2, 3.8, "#9aff5a", a["blink"])
        s.eye(52.5, 50, 3.2, 3.8, "#9aff5a", a["blink"])
        s.line("M46,56 Q48,57.5 50,56", "#c8c0e0")
    return s


def d079(f):
    a = anim(f)
    LINE = "#140e20"
    s = Sprite(LINE)
    s.fit = .9
    s.lid_color = SHD[1]
    y0 = float_y(a, 3)
    with s.group(f"translate(0 {y0 - 4:.2f})"):
        # 两对破洞的翅膀
        for side in (-1, 1):
            with s.group(rot(side * a["flap"] * 18, 48 + side * 8, 40)):
                s.part(poly((48 + side * 8, 40), (48 + side * 30, 18), (48 + side * 40, 24), (48 + side * 34, 32), (48 + side * 38, 38), (48 + side * 20, 44)), "#e8f0ff", "#a8b8e0")
                s.flat(ell(48 + side * 30, 28, 2.5, 2), "#c0b8d0")
                s.part(poly((48 + side * 8, 46), (48 + side * 26, 50), (48 + side * 30, 58), (48 + side * 14, 54)), "#e8f0ff", "#a8b8e0")
        stinger_wisp(s, a, 48, 78, 16)
        s.part("M36,62 C36,52 60,52 60,62 C60,74 54,82 48,82 C42,82 36,74 36,62 Z", *SHD)
        for y in (60, 67, 74):
            s.line(f"M38,{y} Q48,{y + 3} 58,{y}", GLW, 2)
        s.part(ell(48, 50, 9, 7), *SHD)
        # 细长的手臂（有爪）
        for side in (-1, 1):
            s.line(f"M{48 + side * 7},50 L{48 + side * 16},58 L{48 + side * 14},66", SHD[1], 2)
        # 头：骷髅面具一样的白脸
        for side in (-1, 1):
            s.line(f"M{48 + side * 5},26 C{48 + side * 8},16 {48 + side * 14},12 {48 + side * 18},14", LINE, 1.4)
        s.part("M38,34 C38,26 44,22 48,22 C52,22 58,26 58,34 C58,42 54,46 48,46 C42,46 38,42 38,34 Z", "#f0ecf8", "#b0a8c8")
        s.eye(43.5, 33, 3.2, 3.8, "#9aff5a", a["blink"], lid=.45)
        s.eye(52.5, 33, 3.2, 3.8, "#9aff5a", a["blink"], lid=.45)
        s.line("M44,41 L52,41")
        for x in (45, 48, 51):
            s.line(f"M{x},40 L{x},42", LINE, .8)
    return s


# ================================================================== 汐汐螺线（水）：扇贝
SC = ("#ffb0c8", "#d0708a", "#ffe0ea")
SCb = ("#8ad8f0", "#3a98c0")


def scallop(s, cx, cy, w, h, top, open_):
    """扇贝壳：下壳、上壳张开 open_ 度"""
    def shell(y, sgn):
        pts = []
        for i in range(9):
            t = i / 8
            ang = math.pi * (1 - t)
            pts.append((cx + math.cos(ang) * w, y - sgn * math.sin(ang) * h))
        return pts
    lo = shell(cy, -1)
    s.part(poly((cx - w, cy), *lo, (cx + w, cy)), *SC)
    with s.group(rot(0, cx, cy)):
        hi = shell(cy - open_, 1)
        s.part(poly((cx - w, cy - open_), *hi, (cx + w, cy - open_)), *top)
        for k in (-.6, -.3, 0, .3, .6):
            s.line(f"M{cx + k * w * .3},{cy - open_} L{cx + k * w},{cy - open_ - h * .85 * math.cos(k * 1.2)}", top[1], 1)


def d080(f):
    a = anim(f)
    LINE = "#2a1424"
    s = Sprite(LINE)
    s.lid_color = SC[1]
    op = 14 + math.sin(a["ph"]) * 2
    # 下壳
    s.part("M26,80 C26,90 70,90 70,80 Z", *SC)
    # 壳里探出来的身子
    s.part(ell(48, 78 - op * .2, 12, 10), *SCb, "#c8f0ff")
    s.eye(43.5, 76 - op * .2, 3, 3.6, "#1e4a8a", a["blink"])
    s.eye(52.5, 76 - op * .2, 3, 3.6, "#1e4a8a", a["blink"])
    s.line(f"M46,{82 - op * .2} Q48,{83.5 - op * .2} 50,{82 - op * .2}")
    s.flat(ell(39, 81 - op * .2, 2, 1.1), "#ff9ac0")
    s.flat(ell(57, 81 - op * .2, 2, 1.1), "#ff9ac0")
    # 上壳像帽子一样掀起来
    y = 80 - op - 6
    s.part(f"M24,{y + 8} C24,{y - 14} 72,{y - 14} 72,{y + 8} C64,{y + 4} 32,{y + 4} 24,{y + 8} Z", *SC)
    for x in (34, 42, 48, 54, 62):
        s.line(f"M48,{y + 4} L{x},{y - 8 + abs(x - 48) * .4}", SC[1], 1)
    bubble(s, 72, 60 - (a["f"] % 12), 3)
    return s


def d081(f):
    a = anim(f)
    LINE = "#2a1424"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = SC[1]
    op = 24 + math.sin(a["ph"]) * 2
    # 大扇贝，里面坐着一位抱着珍珠的小人
    s.part("M14,80 C14,94 82,94 82,80 Z", *SC)
    y = 80 - op
    s.part(f"M10,{y + 6} C8,{y - 30} 88,{y - 30} 86,{y + 6} C70,{y} 26,{y} 10,{y + 6} Z", *SC)
    for x in (16, 28, 40, 48, 56, 68, 80):
        s.line(f"M48,{y + 2} L{x},{y - 16 + abs(x - 48) * .35}", SC[1], 1.2)
    s.flat(f"M14,{y + 6} C30,{y + 1} 66,{y + 1} 82,{y + 6} L82,80 L14,80 Z", "#5a2a4a")
    s.part(ell(48, 66, 14, 13), *SCb, "#c8f0ff")
    for side in (-1, 1):
        s.part(f"M{48 + side * 12},62 L{48 + side * 22},56 L{48 + side * 18},68 Z", "#ffb0c8", "#d0708a")
    s.eye(43, 63, 3.2, 3.8, "#1e4a8a", a["blink"], lid=.2)
    s.eye(53, 63, 3.2, 3.8, "#1e4a8a", a["blink"], lid=.2)
    s.line("M46,69 Q48,70.5 50,69")
    s.part(ell(48, 80, 7, 6.5), "#fff8fc", "#d8c8e0", "#ffffff")
    for side in (-1, 1):
        s.part(ell(48 + side * 8, 78, 3.5, 3), *SCb)
    return s


# ================================================================== 火火蜗线（火）：火山壳蜗牛
FB = ("#ffb07a", "#d0743a", "#ffe0c0")
VO = ("#6a4a42", "#3e2a24", "#9a7a6a")


def volcano(s, a, cx, by, w, h, erupt):
    s.part(poly((cx - w, by), (cx - w * .3, by - h), (cx + w * .3, by - h), (cx + w, by)), *VO)
    s.flat(poly((cx - w * .3, by - h), (cx - w * .4, by - h + h * .4), (cx - w * .2, by - h + h * .25), (cx, by - h + h * .5), (cx + w * .15, by - h + h * .2), (cx + w * .35, by - h + h * .45), (cx + w * .3, by - h)), "#ff7a2a")
    flame(s, cx, by - h + 1, h * erupt, a["flick"])


def d082(f):
    a = anim(f)
    LINE = "#2a140a"
    s = Sprite(LINE)
    s.lid_color = FB[1]
    st = math.sin(a["ph"]) * 1.5
    s.part("M20,89 C18,82 24,76 32,76 L66,78 C74,80 76,88 72,89 Z", *FB)
    volcano(s, a, 58, 80, 16, 24, .55)
    smoke(s, a, 58, 50)
    with s.group(f"translate({-st:.2f} 0)"):
        for side in (-1, 1):
            s.line(f"M{30 + side * 4},64 L{30 + side * 6},56", FB[1], 1.6)
            s.part(ell(30 + side * 6, 55, 2.2, 2.2), "#ff7a2a", "#c8401a")
        s.part(ell(30, 72, 10, 9), *FB)
        s.eye(26, 71, 2.8, 3.4, "#8a2a1a", a["blink"])
        s.eye(34, 71, 2.8, 3.4, "#8a2a1a", a["blink"])
        s.line("M28.5,77 Q30,78.5 31.5,77")
    return s


def d083(f):
    a = anim(f)
    LINE = "#2a140a"
    s = Sprite(LINE)
    s.fit = .88
    s.lid_color = FB[1]
    st = math.sin(a["ph"]) * 1.5
    s.part("M12,89 C10,80 18,72 28,72 L74,76 C84,78 86,88 82,89 Z", *FB)
    volcano(s, a, 58, 80, 26, 40, .7)
    # 熔岩从山口流下来
    s.line("M50,44 C48,54 46,62 44,72", "#ff7a2a", 2.4)
    s.line("M66,44 C68,56 70,64 72,74", "#ff7a2a", 2.4)
    for i in range(3):
        t = (a["f"] / 24 + i / 3) % 1
        s.flat(ell(58 + (i - 1) * 10 * t, 30 - t * 24, 2 - t, 2 - t), "#ffd04a", LINE, .6)
    with s.group(f"translate({-st:.2f} 0)"):
        for side in (-1, 1):
            s.line(f"M{24 + side * 5},58 L{24 + side * 8},46", FB[1], 2)
            flame(s, 24 + side * 8, 47, 7, a["flick"], 0)
        s.part(ell(24, 68, 13, 12), *FB)
        s.eye(19, 66, 3, 3.6, "#8a2a1a", a["blink"], lid=.4)
        s.eye(29, 66, 3, 3.6, "#8a2a1a", a["blink"], lid=.4)
        s.line("M21,74 Q24,76 27,74")
    return s


# ================================================================== 芝芝蝶线（虫/妖精）：灵芝伞盖
LZ = ("#c86a3a", "#8a3a1a", "#f0a070")
FY = ("#ffd8f0", "#e0a0c8", "#ffffff")


def d084(f):
    a = anim(f)
    LINE = "#2a1410"
    s = Sprite(LINE)
    s.lid_color = "#c8a090"
    W = ("#fff4e8", "#e0c8b0", "#ffffff")
    for i in range(3, 0, -1):
        x = 44 + i * 8
        y = 82 - abs(math.sin(a["ph"] + i)) * 2
        s.part(ell(x, y, 7, 6.5), *W)
        s.flat(ell(x, y - 4, 2, 1.4), "#ff9ac8")
    s.part(ell(42, 72, 12, 11), *W)
    # 头上顶一朵灵芝
    with s.group(rot(a["sway"] * 5, 42, 62)):
        s.part("M26,60 C26,50 36,44 44,44 C52,44 60,50 60,58 C52,62 34,62 26,60 Z", *LZ)
        s.line("M30,56 Q44,50 56,55", "#ffd04a", 1.2)
        s.flat(ell(36, 52, 2, 1.4), "#ffd04a")
    s.eye(37.5, 71, 3, 3.6, "#c84a8a", a["blink"])
    s.eye(46.5, 71, 3, 3.6, "#c84a8a", a["blink"])
    s.flat(ell(33, 76, 2, 1.1), "#ff9ac8")
    s.flat(ell(51, 76, 2, 1.1), "#ff9ac8")
    s.line("M40.5,77 Q42,78 43.5,77")
    return s


def d085(f):
    a = anim(f)
    LINE = "#2a1410"
    s = Sprite(LINE)
    s.lid_color = LZ[1]
    sw = a["sway"]
    # 挂在树枝上的蛹，穿着灵芝甲
    s.part("M20,10 L76,10 L76,14 L20,14 Z", "#8a5a32", "#5a3618")
    s.line("M48,14 L48,22", "#e8e0c8", 1.4)
    with s.group(rot(sw * 4, 48, 14)):
        s.part("M48,20 C62,24 66,44 64,60 C62,76 54,86 48,88 C42,86 34,76 32,60 C30,44 34,24 48,20 Z", *FY)
        for y, w in ((36, 14), (50, 16), (64, 15)):
            s.part(f"M{48 - w},{y} C{48 - w},{y - 8} {48 + w},{y - 8} {48 + w},{y} C{48 + w * .6},{y - 3} {48 - w * .6},{y - 3} {48 - w},{y} Z", *LZ)
            s.line(f"M{48 - w * .7},{y - 3} Q48,{y - 6} {48 + w * .7},{y - 3}", "#ffd04a", 1)
        for side in (-1, 1):
            s.part(f"M{48 + side * 14},62 C{48 + side * 22},60 {48 + side * 24},70 {48 + side * 20},76 C{48 + side * 16},72 {48 + side * 14},68 {48 + side * 14},62 Z", "#ffe8f8", "#e0a0c8")
        s.eye(43.5, 44, 2.8, 3.2, "#c84a8a", a["blink"], lid=.35)
        s.eye(52.5, 44, 2.8, 3.2, "#c84a8a", a["blink"], lid=.35)
    return s


def d086(f):
    a = anim(f)
    LINE = "#2a1410"
    s = Sprite(LINE)
    s.fit = .9
    s.lid_color = LZ[1]
    y0 = float_y(a, 3)
    k = .6 + .4 * abs(math.cos(a["ph"]))
    with s.group(f"translate(0 {y0:.2f})"):
        for side in (-1, 1):
            with s.group(scale_about(k, 1, 48, 46)):
                # 大翅：灵芝一样一圈圈的年轮花纹
                s.part(f"M48,42 C{48 + side * 12},10 {48 + side * 44},2 {48 + side * 46},22 C{48 + side * 48},38 {48 + side * 34},48 48,50 Z", *LZ)
                for r in (14, 9):
                    s.line(f"M{48 + side * (34 - r)},{30 + r * .2} Q{48 + side * 34},{30 - r} {48 + side * (34 + r * .6)},{26}", "#ffd04a", 1.2)
                s.flat(ell(48 + side * 34, 24, 3.5, 3.5), "#ffd8f0", LINE, .8)
                s.part(f"M48,52 C{48 + side * 24},50 {48 + side * 34},64 {48 + side * 26},78 C{48 + side * 18},82 {48 + side * 10},72 48,58 Z", *FY)
                s.flat(ell(48 + side * 22, 68, 3, 3), "#ff9ac8", LINE, .7)
        # 金甲身躯
        s.part("M42,44 C42,36 54,36 54,44 L53,74 C52,80 44,80 43,74 Z", "#e0b850", "#a87a1a", "#fff0a0")
        for y in (52, 60, 68):
            s.line(f"M43,{y} L53,{y}", "#a87a1a", 1)
        for side in (-1, 1):
            s.line(f"M{48 + side * 3},28 C{48 + side * 8},16 {48 + side * 14},12 {48 + side * 18},12", LINE, 1.4)
            s.flat(ell(48 + side * 18, 12, 2.4, 2.4), "#ff9ac8", LINE, .7)
        s.part(ell(48, 34, 10, 9), "#e0b850", "#a87a1a", "#fff0a0")
        s.part(poly((40, 28), (48, 22), (56, 28), (56, 32), (40, 32)), *LZ)
        s.eye(44, 35, 2.8, 3.4, "#c84a8a", a["blink"], lid=.4)
        s.eye(52, 35, 2.8, 3.4, "#c84a8a", a["blink"], lid=.4)
    return s


# ================================================================== 斗斗牛线（格斗）
BL = ("#a8603a", "#6e381a", "#d89068")
TAPE = ("#f4f0e8", "#c0b8a8")


def d087(f):
    a = anim(f)
    LINE = "#2a140a"
    s = Sprite(LINE)
    s.lid_color = BL[1]
    b = a["breath"]
    with s.group(rot(a["sway"] * 10, 62, 72)):
        s.line("M60,72 C70,72 74,66 74,60", BL[1], 2)
        s.part(ell(74, 58, 3, 4), "#3a2a1a", "#1a1008")
    s.part(LEG(36, 70, 89, 6), BL[1], "#4a2410")
    s.part(LEG(60, 70, 89, 6), BL[1], "#4a2410")
    with s.group(f"translate(0 {-b * .6:.2f})"):
        s.part(ell(48, 70, 18, 12), *BL)
        s.part(ell(48, 74, 10, 7), "#f0d8b8", "#c8a888", line="none")
    for x in (40, 56):
        s.part(LEG(x, 72, 88, 7), *BL)
        s.part(ell(x, 89, 4.4, 2), "#3a2a1a", "#1a1008")
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        # 小短角 + 头巾
        for side in (-1, 1):
            s.part(f"M{48 + side * 10},40 C{48 + side * 16},38 {48 + side * 18},32 {48 + side * 16},28 C{48 + side * 20},32 {48 + side * 20},40 {48 + side * 14},44 Z", *TAPE)
            s.part(ell(48 + side * 16, 46, 5, 3), *BL)
        s.part(ell(48, 50, 14, 13), *BL)
        s.part("M34,42 C40,38 56,38 62,42 L62,46 C56,42 40,42 34,46 Z", "#e83a3a", "#a81a1a")
        with s.group(rot(a["sway"] * 10, 62, 44)):
            s.part("M62,42 L70,40 L68,46 L62,46 Z", "#e83a3a", "#a81a1a")
        s.part(ell(48, 57, 8, 6), "#f0d8b8", "#c8a888", line="none")
        s.flat(ell(45, 56.5, 1, .8), LINE)
        s.flat(ell(51, 56.5, 1, .8), LINE)
        s.eye(42.5, 49, 3, 3.6, "#3a2a1a", a["blink"], lid=.3)
        s.eye(53.5, 49, 3, 3.6, "#3a2a1a", a["blink"], lid=.3)
        s.line("M46,60.5 Q48,61.5 50,60.5")
    smoke(s, a, 45, 58)
    return s


def d088(f):
    a = anim(f)
    LINE = "#2a140a"
    s = Sprite(LINE)
    s.fit = .88
    s.lid_color = BL[1]
    b = a["breath"]
    sw = a["sway"]
    # 站起来的牛拳手：缠手带、腰带
    s.part("M36,66 C30,72 30,82 32,89 L44,89 C44,82 44,76 46,70 Z", *BL)
    s.part("M60,66 C66,72 66,82 64,89 L52,89 C52,82 52,76 50,70 Z", *BL)
    s.part(ell(37, 89, 7, 2.4), "#3a2a1a", "#1a1008")
    s.part(ell(59, 89, 7, 2.4), "#3a2a1a", "#1a1008")
    with s.group(f"translate(0 {-b * .8:.2f})"):
        s.part("M28,42 C26,32 38,28 48,28 C58,28 70,32 68,42 L64,66 C58,72 38,72 32,66 Z", *BL)
        s.part("M38,44 C38,38 58,38 58,44 L56,60 C52,64 44,64 40,60 Z", "#f0d8b8", "#c8a888", line="none")
        s.line("M48,44 L48,60", "#c8a888", 1)
        s.part(poly((32, 62), (64, 62), (64, 68), (32, 68)), "#ffd24a", "#c08a1a")
        s.part(ell(48, 65, 5, 4), "#e83a3a", "#a81a1a")
        # 双拳护在胸前
        for side in (-1, 1):
            with s.group(rot(side * sw * 6, 48 + side * 18, 34)):
                s.part(f"M{48 + side * 18},34 C{48 + side * 26},38 {48 + side * 26},46 {48 + side * 20},50 L{48 + side * 14},48 C{48 + side * 18},44 {48 + side * 16},40 {48 + side * 12},38 Z", *BL)
                s.part(ell(48 + side * 12, 48, 6, 5.5), *TAPE)
                s.line(f"M{48 + side * 8},46 L{48 + side * 16},50", TAPE[1], 1)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        for side in (-1, 1):
            s.part(f"M{48 + side * 10},16 C{48 + side * 18},14 {48 + side * 24},8 {48 + side * 24},0 C{48 + side * 30},8 {48 + side * 26},18 {48 + side * 14},22 Z", *TAPE)
            s.part(ell(48 + side * 15, 22, 5, 3), *BL)
        s.part(ell(48, 24, 13, 12), *BL)
        s.part("M35,16 C40,12 56,12 61,16 L61,20 C56,16 40,16 35,20 Z", "#e83a3a", "#a81a1a")
        s.part(ell(48, 31, 8, 5.5), "#f0d8b8", "#c8a888", line="none")
        s.flat(ell(45, 30.5, 1, .8), LINE)
        s.flat(ell(51, 30.5, 1, .8), LINE)
        s.line("M47,33 Q48,36 49,33", "#ffd24a", 1.4)
        s.eye(42.5, 23, 3, 3.4, "#3a2a1a", a["blink"], lid=.45)
        s.eye(53.5, 23, 3, 3.4, "#3a2a1a", a["blink"], lid=.45)
    smoke(s, a, 45, 32)
    return s


# ================================================================== 089 云鹤（飞行）
def d089(f):
    a = anim(f)
    LINE = "#1e2030"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = "#a8b0c0"
    W = ("#f8faff", "#c0c8d8", "#ffffff")
    b = a["breath"]
    # 单腿站立
    s.line("M50,66 L50,89", "#3a3a4a", 2)
    s.flat(poly((44, 90), (50, 87), (56, 90)), "#3a3a4a", LINE, .8)
    s.line("M54,66 L58,72 L52,76", "#3a3a4a", 2)
    # 云朵一样的尾羽
    with s.group(rot(a["sway"] * 4, 62, 60)):
        for x, y, r in ((66, 64, 7), (74, 60, 6), (72, 68, 6), (80, 66, 5)):
            s.part(ell(x, y, r, r * .85), *W)
    with s.group(f"translate(0 {-b * .8:.2f})"):
        s.part("M34,56 C34,46 44,42 54,44 C66,46 72,54 68,64 C64,70 52,72 44,70 C38,68 34,62 34,56 Z", *W)
        with s.group(rot(a["flap"] * 3, 44, 52)):
            s.part("M42,50 C52,46 66,48 70,58 C62,58 52,60 44,62 Z", "#e8ecf8", "#b0b8cc")
            s.part("M62,56 L72,58 L68,62 Z", "#2a2a3a", "#101018")
        # 长脖子
        s.part("M36,52 C30,44 30,34 34,26 L40,26 C38,34 38,44 44,50 Z", *W)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        s.part(ell(37, 22, 8, 7.5), *W)
        s.flat(ell(37, 15.5, 3.5, 2), "#e83a3a", LINE, .7)
        s.part(poly((35, 25), (39, 25), (37, 36)), "#e0b060", "#a87a2a")
        s.eye(34, 21.5, 2.2, 2.8, "#3a3a4a", a["blink"])
        s.eye(40, 21.5, 2.2, 2.8, "#3a3a4a", a["blink"])
    return s


# ================================================================== 090 冻蛾（冰）
def d090(f):
    a = anim(f)
    LINE = "#142a3a"
    s = Sprite(LINE)
    s.lid_color = "#6ab0c0"
    y0 = float_y(a, 3)
    I = ("#d8f6ff", "#7ac0d8", "#ffffff")
    with s.group(f"translate(0 {y0:.2f})"):
        k = .7 + .3 * abs(math.cos(a["ph"]))
        for side in (-1, 1):
            with s.group(scale_about(k, 1, 48, 50)):
                s.part(f"M48,46 C{48 + side * 18},28 {48 + side * 38},26 {48 + side * 40},40 C{48 + side * 40},52 {48 + side * 26},56 48,54 Z", *I)
                s.flat(star(48 + side * 26, 42, 5, 1.4, 8), "#ffffff", I[1], .8)
                s.part(f"M48,56 C{48 + side * 16},56 {48 + side * 26},64 {48 + side * 22},74 C{48 + side * 14},76 {48 + side * 8},68 48,60 Z", *I)
        s.part("M42,48 C42,40 54,40 54,48 C54,60 52,68 48,70 C44,68 42,60 42,48 Z", "#f0fcff", "#a8d0e0", "#ffffff")
        # 毛茸茸的冰领
        for x in (40, 44, 48, 52, 56):
            s.flat(ell(x, 44, 3, 2.5), "#ffffff", I[1], .6)
        for side in (-1, 1):
            s.part(f"M{48 + side * 3},32 C{48 + side * 8},24 {48 + side * 14},22 {48 + side * 16},26 C{48 + side * 12},26 {48 + side * 8},30 {48 + side * 6},34 Z", *I)
        s.part(ell(48, 38, 8, 7), "#f0fcff", "#a8d0e0", "#ffffff")
        s.eye(44.5, 38, 2.6, 3.2, "#2a6a9a", a["blink"])
        s.eye(51.5, 38, 2.6, 3.2, "#2a6a9a", a["blink"])
    for i in range(3):
        t = (a["f"] / 24 + i / 3) % 1
        s.flat(ell(24 + i * 24, 60 + t * 26, 1, 1), "#ffffff", LINE, .4)
    return s


# ================================================================== 小翔鸟线（飞行）：燕子
SW = ("#3a4a8a", "#1e2a5a", "#6a7ac0")
SWr = ("#e85a3a", "#a83a1a")


def d091(f):
    a = anim(f)
    LINE = "#141a2e"
    s = Sprite(LINE)
    s.lid_color = SW[1]
    dy, sq = hop(a, 3)
    with s.group(f"translate(0 {dy:.2f})"):
        with s.group(rot(a["sway"] * 6, 60, 76)):
            s.part("M58,76 L76,82 L68,78 L78,74 Z", *SW[:2])
        for x in (44, 52):
            s.line(f"M{x},82 L{x},89", "#3a3a4a", 1.6)
        s.part(ell(48, 72, 14, 12), *SW)
        s.part(ell(48, 76, 8, 7), "#fff8f0", "#e0d0c0", line="none")
        for side in (-1, 1):
            with s.group(rot(side * (10 + a["flap"] * 14), 48 + side * 12, 68)):
                s.part(f"M{48 + side * 12},64 C{48 + side * 24},62 {48 + side * 28},70 {48 + side * 26},76 C{48 + side * 20},74 {48 + side * 14},72 {48 + side * 12},70 Z", *SW[:2])
        s.part(ell(48, 54, 12, 11), *SW)
        s.part(ell(48, 60, 6, 3.6), *SWr, line="none")
        s.eye(43.5, 53, 3, 3.6, "#1e2a5a", a["blink"])
        s.eye(52.5, 53, 3, 3.6, "#1e2a5a", a["blink"])
        s.part(poly((46, 56), (50, 56), (48, 59)), "#3a3a4a", "#1a1a2a")
    return s


def d092(f):
    a = anim(f)
    LINE = "#141a2e"
    s = Sprite(LINE)
    s.fit = .88
    s.lid_color = SW[1]
    y0 = float_y(a, 3)
    fl = a["flap"]
    with s.group(f"translate(0 {y0:.2f})"):
        # 剪刀一样的长尾
        for side in (-1, 1):
            with s.group(rot(side * (8 + a["sway"] * 4), 48, 70)):
                s.part(f"M{48 - side * 2},70 L{48 + side * 4},70 L{48 + side * 10},94 Z", *SW[:2])
        # 后掠的镰刀翼
        for side in (-1, 1):
            with s.group(rot(side * fl * 8, 48 + side * 8, 48)):
                s.part(f"M{48 + side * 8},44 C{48 + side * 24},34 {48 + side * 40},32 {48 + side * 48},40 C{48 + side * 36},42 {48 + side * 26},48 {48 + side * 12},56 Z", *SW)
                s.line(f"M{48 + side * 14},46 L{48 + side * 40},38", SW[2], 1)
        s.part("M38,48 C38,38 58,38 58,48 C58,62 54,72 48,72 C42,72 38,62 38,48 Z", *SW)
        s.part("M42,52 C42,46 54,46 54,52 C54,62 52,68 48,68 C44,68 42,62 42,52 Z", "#fff8f0", "#e0d0c0", line="none")
        with s.group(rot(a["sway"] * 5, 48, 24)):
            s.part(poly((44, 26), (40, 14), (48, 20), (56, 14), (52, 26)), *SWr)
        s.part(ell(48, 32, 10, 9), *SW)
        s.part(ell(48, 37, 5, 3), *SWr, line="none")
        s.eye(44, 31, 2.6, 3.2, "#e85a3a", a["blink"], lid=.4)
        s.eye(52, 31, 2.6, 3.2, "#e85a3a", a["blink"], lid=.4)
        s.part(poly((46, 34), (50, 34), (48, 38)), "#3a3a4a", "#1a1a2a")
    return s


# ================================================================== 砾螺线（岩石）：菊石
AM = ("#c8b090", "#8a7458", "#ecdcc0")
AMb = ("#7ab8a0", "#3a7a62")


def ammonite(s, cx, cy, r, spikes=0):
    s.part(ell(cx, cy, r, r), *AM)
    spiral(s, cx + r * .1, cy + r * .05, r * .85, 2.3, AM[1], 1.4)
    for i in range(spikes):
        ang = -math.pi * .9 + i * math.pi * 1.1 / max(1, spikes - 1)
        x, y = cx + math.cos(ang) * r, cy + math.sin(ang) * r
        s.part(poly((x - math.sin(ang) * 3, y + math.cos(ang) * 3), (x + math.cos(ang) * 7, y + math.sin(ang) * 7), (x + math.sin(ang) * 3, y - math.cos(ang) * 3)), *AM)


def tentacle_face(s, a, cx, cy, n, ln):
    for i in range(n):
        x = cx - (n - 1) * 2.5 + i * 5
        ph = a["ph"] + i
        s.line(f"M{x},{cy} C{x + math.sin(ph) * 2},{cy + ln * .5} {x - math.sin(ph) * 2},{cy + ln * .8} {x + math.sin(ph + 1) * 2},{cy + ln}", AMb[1], 3)
        s.line(f"M{x},{cy} C{x + math.sin(ph) * 2},{cy + ln * .5} {x - math.sin(ph) * 2},{cy + ln * .8} {x + math.sin(ph + 1) * 2},{cy + ln}", AMb[0], 1.6)


def d093(f):
    a = anim(f)
    LINE = "#1e1a12"
    s = Sprite(LINE)
    s.lid_color = AMb[1]
    b = a["breath"]
    with s.group(f"translate(0 {-b:.2f})"):
        ammonite(s, 54, 66, 18)
        tentacle_face(s, a, 36, 78, 4, 10)
        s.part(ell(36, 72, 10, 8), *AMb)
        s.eye(32, 71, 2.8, 3.4, "#1e3a2a", a["blink"])
        s.eye(40, 71, 2.8, 3.4, "#1e3a2a", a["blink"])
    return s


def d094(f):
    a = anim(f)
    LINE = "#1e1a12"
    s = Sprite(LINE)
    s.fit = .94
    s.lid_color = AMb[1]
    b = a["breath"]
    with s.group(f"translate(0 {-b:.2f})"):
        ammonite(s, 56, 58, 24, 5)
        tentacle_face(s, a, 32, 72, 5, 16)
        s.part(ell(32, 66, 12, 9), *AMb)
        s.eye(27, 65, 2.8, 3.4, "#1e3a2a", a["blink"], lid=.35)
        s.eye(37, 65, 2.8, 3.4, "#1e3a2a", a["blink"], lid=.35)
    return s


def d095(f):
    a = anim(f)
    LINE = "#1e1a12"
    s = Sprite(LINE)
    s.fit = .86
    s.lid_color = AMb[1]
    b = a["breath"]
    with s.group(f"translate(0 {-b:.2f})"):
        ammonite(s, 56, 52, 32, 7)
        # 壳上长着青苔和小石块
        for x, y in ((40, 26), (66, 24), (82, 44)):
            s.flat(ell(x, y, 4, 2), "#7aaa4a", LINE, .6)
        tentacle_face(s, a, 28, 70, 6, 18)
        # 长出一对粗壮的触手当手臂
        for side in (-1, 1):
            x0 = 28 + side * 10
            s.line(f"M{x0},66 C{x0 + side * 8},70 {x0 + side * 10},80 {x0 + side * 6 + a['sway'] * 2},88", AMb[1], 5)
            s.line(f"M{x0},66 C{x0 + side * 8},70 {x0 + side * 10},80 {x0 + side * 6 + a['sway'] * 2},88", AMb[0], 3)
        s.part(ell(28, 62, 14, 10), *AMb)
        s.eye(22, 61, 3, 3.6, "#1e3a2a", a["blink"], lid=.45)
        s.eye(34, 61, 3, 3.6, "#1e3a2a", a["blink"], lid=.45)
    return s


# ================================================================== 小汐菇线（水/毒）
MU = ("#7a8ae8", "#4a54b0", "#b0b8ff")
MS = ("#f4ecf8", "#c8b8d8")
DRIP = "#c0ff7a"


def drip(s, a, x, y, k):
    t = (a["f"] / 24 + k) % 1
    s.flat(f"M{x},{y + t * 10} C{x - 1.6},{y + t * 10 + 2} {x - 1.6},{y + t * 10 + 3.5} {x},{y + t * 10 + 3.5} C{x + 1.6},{y + t * 10 + 3.5} {x + 1.6},{y + t * 10 + 2} {x},{y + t * 10} Z", DRIP, s.outline, .6)


def d096(f):
    a = anim(f)
    LINE = "#1a1430"
    s = Sprite(LINE)
    s.lid_color = MS[1]
    b = a["breath"]
    with s.group(scale_about(1 + .03 * b, 1 - .02 * b, 48, 89)):
        s.part("M38,89 C36,80 38,70 40,64 L56,64 C58,70 60,80 58,89 Z", *MS)
        s.part(ell(40, 89, 5, 2.2), *MS)
        s.part(ell(56, 89, 5, 2.2), *MS)
        s.eye(43.5, 74, 3, 3.6, "#4a54b0", a["blink"])
        s.eye(52.5, 74, 3, 3.6, "#4a54b0", a["blink"])
        s.flat(ell(40, 79, 2, 1.1), "#ffa8c8")
        s.flat(ell(56, 79, 2, 1.1), "#ffa8c8")
        s.line("M46.5,80 Q48,81 49.5,80")
    with s.group(f"translate(0 {-b * 1.2:.2f}) {rot(a['sway'] * 4, 48, 64)}"):
        s.part("M26,64 C24,48 36,40 48,40 C60,40 72,48 70,64 C62,68 34,68 26,64 Z", *MU)
        for x, y, r in ((38, 50, 3), (54, 47, 3.6), (62, 56, 2.4), (44, 58, 2)):
            s.flat(f"M{x},{y - r * 1.4} C{x - r},{y - r * .2} {x - r},{y + r} {x},{y + r} C{x + r},{y + r} {x + r},{y - r * .2} {x},{y - r * 1.4} Z", "#d8f4ff", LINE, .6)
    drip(s, a, 30, 66, 0)
    drip(s, a, 66, 66, .5)
    return s


def d097(f):
    a = anim(f)
    LINE = "#1a1430"
    s = Sprite(LINE)
    s.fit = .9
    s.lid_color = MS[1]
    b = a["breath"]
    # 菌褶裙
    s.part("M30,89 C28,78 34,66 40,60 L56,60 C62,66 68,78 66,89 Z", *MS)
    for x in (36, 42, 48, 54, 60):
        s.line(f"M48,62 L{x},88", MS[1], 1)
    s.part("M38,88 L58,88 L56,62 L40,62 Z", MS[0], MS[1])
    # 两只菌丝手臂
    for side in (-1, 1):
        s.line(f"M{48 + side * 8},66 C{48 + side * 18},68 {48 + side * 22},74 {48 + side * 22 + a['sway'] * 2},80", MS[1], 3.4)
        s.line(f"M{48 + side * 8},66 C{48 + side * 18},68 {48 + side * 22},74 {48 + side * 22 + a['sway'] * 2},80", MS[0], 2)
    s.eye(43.5, 70, 3, 3.6, "#9a2aa8", a["blink"], lid=.4)
    s.eye(52.5, 70, 3, 3.6, "#9a2aa8", a["blink"], lid=.4)
    s.line("M45,77 Q48,78.5 51,77")
    with s.group(f"translate(0 {-b * 1.2:.2f}) {rot(a['sway'] * 3, 48, 60)}"):
        # 宽大的伞盖，边缘滴着毒水
        s.part("M8,58 C6,34 28,18 48,18 C68,18 90,34 88,58 C82,62 78,58 74,62 C70,58 64,62 60,60 C56,64 52,62 48,62 C44,62 40,64 36,60 C32,62 26,58 22,62 C18,58 14,62 8,58 Z", "#5a5ac8", "#30308a", "#9a9aff")
        for x, y, r in ((28, 36, 4), (48, 28, 5), (68, 36, 4), (38, 48, 3), (60, 48, 3), (18, 50, 2.5), (78, 50, 2.5)):
            s.flat(ell(x, y, r, r * .9), "#c0ff7a" if (x + a["f"]) % 3 else "#e0ffb0", LINE, .6)
    for i, x in enumerate((14, 30, 48, 66, 82)):
        drip(s, a, x, 62, i / 5)
    return s


# ================================================================== 涟涟鲸线（水）
WH = ("#4a8ae0", "#2a58a8", "#8ac0ff")
WHb = ("#e8f6ff", "#a8d0ec")


def spout(s, a, x, y, h):
    t = (math.sin(a["ph"] * 2) + 1) / 2
    hh = h * (.6 + .4 * t)
    s.line(f"M{x},{y} L{x},{y - hh}", "#c8ecff", 2)
    for side in (-1, 1):
        s.line(f"M{x},{y - hh} C{x + side * 4},{y - hh - 3} {x + side * 7},{y - hh} {x + side * 8},{y - hh + 4}", "#c8ecff", 1.6)
        s.flat(ell(x + side * 8, y - hh + 5, 1.5, 1.5), "#ffffff", s.outline, .5)


def d098(f):
    a = anim(f)
    LINE = "#0e1e3a"
    s = Sprite(LINE)
    s.lid_color = WH[1]
    y0 = float_y(a, 2)
    with s.group(f"translate(0 {y0:.2f})"):
        with s.group(rot(a["sway"] * 10, 70, 70)):
            s.part("M66,72 C74,70 78,64 86,60 C84,66 86,72 84,76 C80,74 74,76 68,78 Z", *WH)
        s.part("M20,70 C20,56 34,50 50,50 C66,50 76,58 76,70 C76,80 64,84 48,84 C32,84 20,80 20,70 Z", *WH)
        s.part("M26,74 C30,82 64,84 70,74 C60,78 36,78 26,74 Z", *WHb, line="none")
        for x in (36, 44, 52, 60):
            s.line(f"M{x},76 L{x},81", WHb[1], 1)
        for side in (-1, 1):
            with s.group(rot(side * a["flap"] * 10, 48 + side * 22, 72)):
                s.part(ell(48 + side * 26, 76, 6, 3), *WH)
        s.eye(40, 66, 3.2, 3.8, "#0e2a5a", a["blink"])
        s.eye(56, 66, 3.2, 3.8, "#0e2a5a", a["blink"])
        s.flat(ell(34, 72, 2.4, 1.3), "#ff9ac0")
        s.flat(ell(62, 72, 2.4, 1.3), "#ff9ac0")
        s.line("M44,73 Q48,76 52,73")
        spout(s, a, 48, 50, 12)
    s.part("M8,86 C18,82 28,88 38,85 C48,82 58,88 68,85 C78,82 86,86 90,88 L90,90 L8,90 Z", "#8ad8f8", "#4aa0d0")
    return s


def d099(f):
    a = anim(f)
    LINE = "#0a1630"
    s = Sprite(LINE)
    s.fit = .86
    s.lid_color = WH[1]
    D = ("#2e5ab8", "#1a3478", "#6a98f0")
    y0 = float_y(a, 2)
    with s.group(f"translate(0 {y0:.2f})"):
        with s.group(rot(a["sway"] * 6, 78, 56)):
            s.part("M74,58 C82,52 86,40 96,32 C94,42 98,50 96,58 C90,56 84,60 78,64 Z", *D)
        s.part("M10,62 C8,42 28,30 52,30 C74,30 86,44 84,62 C82,76 66,82 46,82 C24,82 12,76 10,62 Z", *D)
        s.part("M16,66 C22,78 70,80 78,66 C66,72 30,72 16,66 Z", *WHb, line="none")
        for x in (28, 38, 48, 58, 68):
            s.line(f"M{x},70 L{x},77", WHb[1], 1)
        # 额头一道道浪纹
        for i, y in enumerate((38, 44)):
            s.line(f"M{30 + i * 4},{y} q4,-3 8,0 q4,3 8,0 q4,-3 8,0 q4,3 8,0", D[2], 1.4)
        for side in (-1, 1):
            with s.group(rot(side * a["flap"] * 8, 48 + side * 30, 66)):
                s.part(f"M{48 + side * 30},64 C{48 + side * 40},62 {48 + side * 46},68 {48 + side * 44},76 C{48 + side * 38},74 {48 + side * 34},72 {48 + side * 30},70 Z", *D)
        s.eye(36, 56, 3.4, 4, "#0e2a5a", a["blink"], lid=.45)
        s.eye(60, 56, 3.4, 4, "#0e2a5a", a["blink"], lid=.45)
        s.line("M40,66 Q48,70 56,66")
        spout(s, a, 48, 30, 18)
    # 脚下的大浪
    sw = a["sway"]
    s.part(f"M2,84 C10,{76 + sw} 18,{78 - sw} 26,84 C34,{78 + sw} 44,{76 - sw} 52,84 C60,{78 + sw} 70,{76 - sw} 78,84 C84,{78 + sw} 92,80 94,84 L94,92 L2,92 Z", "#8ad8f8", "#4aa0d0", "#d8f6ff")
    for x in (14, 40, 66):
        s.line(f"M{x},86 q3,-2 6,0", "#ffffff", 1)
    return s


# ================================================================== 100 震鳄（大地）
def d100(f):
    a = anim(f)
    LINE = "#2a1a0e"
    s = Sprite(LINE)
    s.lid_color = "#8a6230"
    E = ("#c8a060", "#8a6230", "#ecd098")
    D = ("#7a5a3a", "#4a3420")
    b = a["breath"]
    # 尾巴拍地，拍一下地面震一下
    slam = max(0, math.sin(a["ph"] * 2))
    with s.group(rot(-slam * 12, 62, 80)):
        s.part("M58,76 C70,74 82,80 90,88 C80,90 68,88 58,86 Z", *E)
        for x in (68, 76, 84):
            s.part(poly((x - 2, 79), (x, 74), (x + 3, 80)), *D)
    if slam < .2:
        for x in (86, 92):
            s.line(f"M{x},90 L{x + 2},84", "#c8a060", 1)
    with s.group(scale_about(1 + .02 * b, 1 + .02 * b, 48, 89)):
        s.part(ell(46, 78, 20, 11), *E)
        s.part(ell(44, 82, 12, 6), "#f4e8c8", "#c8b890", line="none")
        for x in (30, 58):
            s.part(ell(x, 88, 6, 2.8), *E)
            for k in (-3, 0, 3):
                s.line(f"M{x + k},89 L{x + k},91", LINE, 1)
    with s.group(f"translate(0 {-b * 1.5:.2f})"):
        # 宽扁的头，鼻子上一个钻头角
        s.part("M24,60 C24,48 34,44 44,44 C54,44 64,48 64,60 C64,70 56,74 44,74 C32,74 24,70 24,60 Z", *E)
        s.part("M28,64 C30,72 58,72 60,64 C52,67 36,67 28,64 Z", "#f4e8c8", "#c8b890", line="none")
        s.line("M28,64 Q44,68 60,64")
        for x in (33, 39, 49, 55):
            s.flat(poly((x - 1.2, 65), (x, 68), (x + 1.2, 65.3)), "#ffffff")
        s.part(poly((40, 52), (44, 36), (48, 52)), *D)
        for y in (40, 44, 48):
            s.line(f"M{44 - (y - 36) * .25},{y} L{44 + (y - 36) * .25},{y + 1.5}", D[1], 1)
        for side in (-1, 1):
            s.part(ell(44 + side * 11, 48, 6, 5.5), *E)
        s.eye(33, 48, 3, 3.6, "#c84a1a", a["blink"], lid=.3)
        s.eye(55, 48, 3, 3.6, "#c84a1a", a["blink"], lid=.3)
    return s


SPECIES = {k: v for k, v in globals().items() if k.startswith("d0") or k == "d100"}
SPECIES = {k: v for k, v in SPECIES.items() if callable(v) and len(k) == 4}
