"""#056-#075：嫩猴、鬼鸦、小茧蚕、小泡虾、蠕蠕蚕、卵卵蟹、风蝠、小滴螺、幻幻鸮"""
import math

from kit import Sprite, anim, ell, poly, rot, scale_about
from fox import HIND, LEG
from legends1 import flame
from legends2 import star
from mouse import leaf
from frog import bubble


def float_y(a, amp=2.5):
    return -math.sin(a["ph"]) * amp


# ================================================================== 嫩猴线（草）
MK = ("#a8d070", "#6a9a3a", "#d8f0a8")
FC = ("#ffe4c0", "#d8b48a")
LF = ("#3fae4a", "#1f7a34")


def d056(f):
    a = anim(f)
    LINE = "#1e2a12"
    s = Sprite(LINE)
    s.lid_color = MK[1]
    b = a["breath"]
    # 卷成圈的藤蔓尾巴
    with s.group(rot(a["sway"] * 8, 62, 82)):
        s.line("M60,84 C76,86 82,72 76,64 C70,58 64,64 68,70", MK[1], 4)
        s.line("M60,84 C76,86 82,72 76,64 C70,58 64,64 68,70", MK[0], 2)
        leaf(s, 76, 64, 9, 4, 40, *LF)
    with s.group(scale_about(1 + .02 * b, 1 + .03 * b, 48, 89)):
        s.part(ell(48, 77, 15, 12), *MK)
        s.part(ell(48, 80, 8, 7), *FC, line="none")
        s.part(ell(37, 88, 6, 2.6), *FC)
        s.part(ell(59, 88, 6, 2.6), *FC)
        # 双手抱膝
        s.part(ell(38, 78, 4, 3.5), *FC)
        s.part(ell(58, 78, 4, 3.5), *FC)
    with s.group(f"translate(0 {-b * 1.3:.2f})"):
        # 大圆耳
        for side in (-1, 1):
            tw = 8 if (a["f"] in (18, 19) and side > 0) else 0
            with s.group(rot(tw, 48 + side * 16, 52)):
                s.part(ell(48 + side * 17, 52, 6, 6), *MK)
                s.part(ell(48 + side * 17, 52, 3.5, 3.5), *FC, line="none")
        # 头顶一撮嫩叶
        with s.group(rot(a["sway"] * 8, 48, 38)):
            leaf(s, 48, 39, 12, 5, -25, *LF)
            leaf(s, 48, 39, 10, 4, 30, "#6ac85a", LF[1])
        s.part(ell(48, 52, 15, 13), *MK)
        # 心形的脸
        s.part("M48,48 C44,42 36,44 36,51 C36,58 42,62 48,62 C54,62 60,58 60,51 C60,44 52,42 48,48 Z", *FC, line="none")
        s.eye(42.5, 51, 3.4, 4.2, "#3a5a1a", a["blink"])
        s.eye(53.5, 51, 3.4, 4.2, "#3a5a1a", a["blink"])
        s.flat(ell(46.5, 56.5, .8, .6), LINE)
        s.flat(ell(49.5, 56.5, .8, .6), LINE)
        s.line("M45,58.5 Q48,61 51,58.5")
    return s


def d057(f):
    a = anim(f)
    LINE = "#1e2a12"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = MK[1]
    b = a["breath"]
    sw = a["sway"]
    with s.group(rot(sw * 6, 60, 66)):
        s.line("M58,68 C76,70 86,56 80,44 C76,36 66,40 70,48", MK[1], 5)
        s.line("M58,68 C76,70 86,56 80,44 C76,36 66,40 70,48", MK[0], 3)
        for t, ang in ((0, 40), (1, -30)):
            leaf(s, 80 - t * 4, 46 + t * 12, 10, 4.5, ang, *LF)
    # 腿
    s.part("M38,70 C34,76 34,84 36,89 L44,89 C44,84 44,78 46,74 Z", *MK)
    s.part("M58,70 C62,76 62,84 60,89 L52,89 C52,84 52,78 50,74 Z", *MK)
    s.part(ell(39, 89, 5.5, 2.4), *FC)
    s.part(ell(57, 89, 5.5, 2.4), *FC)
    with s.group(f"translate(0 {-b * .8:.2f})"):
        s.part("M34,52 C32,42 40,36 48,36 C56,36 64,42 62,52 C62,64 58,74 48,74 C38,74 34,64 34,52 Z", *MK)
        s.part("M40,54 C40,46 56,46 56,54 C56,64 52,70 48,70 C44,70 40,64 40,54 Z", *FC, line="none")
        # 叶子围脖
        for i, ang in enumerate((-70, -35, 0, 35, 70)):
            leaf(s, 48 + ang * .2, 40, 9, 4.5, 180 + ang * .9, *(LF if i % 2 else ("#6ac85a", LF[1])))
        # 一只手举着果子，一只手垂着
        s.part("M34,44 C26,46 24,54 26,60 L31,60 C31,54 33,50 37,48 Z", *MK)
        s.part(ell(28, 62, 4, 3.5), *FC)
        with s.group(rot(sw * 6, 62, 44)):
            s.part("M62,44 C70,40 74,32 72,26 L67,26 C67,32 64,36 59,40 Z", *MK)
            s.part(ell(70, 24, 4, 3.5), *FC)
            s.part(ell(70, 18, 5, 5), "#ff7a5a", "#c8402a", "#ffc0a8")
            leaf(s, 70, 13, 5, 2.5, 20, *LF)
    with s.group(f"translate(0 {-b * 1.3:.2f})"):
        for side in (-1, 1):
            s.part(ell(48 + side * 15, 22, 5, 5), *MK)
            s.part(ell(48 + side * 15, 22, 2.8, 2.8), *FC, line="none")
        with s.group(rot(sw * 6, 48, 10)):
            leaf(s, 48, 10, 14, 6, -30, *LF)
            leaf(s, 48, 10, 14, 6, 30, *LF)
            leaf(s, 48, 10, 12, 5, 0, "#6ac85a", LF[1])
        s.part(ell(48, 22, 13, 12), *MK)
        s.part("M48,19 C44,13 37,15 37,21 C37,28 42,32 48,32 C54,32 59,28 59,21 C59,15 52,13 48,19 Z", *FC, line="none")
        s.eye(43, 21, 3, 3.6, "#3a5a1a", a["blink"], lid=.2)
        s.eye(53, 21, 3, 3.6, "#3a5a1a", a["blink"], lid=.2)
        s.line("M45.5,28 Q48,30 50.5,28")
    return s


# ================================================================== 鬼鸦线（幽灵/草）
CRW = ("#4a3a68", "#2a1e40", "#7a6aa0")
WISP = ("#b8f0c0", "#6ac87a")


def wisps(s, a, pts):
    for i, (x, y) in enumerate(pts):
        t = (a["f"] / 24 + i / len(pts)) % 1
        s.flat(ell(x, y - t * 8, 2.4 - t * 1.4, 3 - t * 1.6), WISP[0] if t < .5 else "#e0ffe4", s.outline, .6)


def d058(f):
    a = anim(f)
    LINE = "#140e20"
    s = Sprite(LINE)
    s.lid_color = CRW[1]
    dy = -abs(math.sin(a["ph"])) * 2
    with s.group(f"translate(0 {dy:.2f})"):
        # 叶子尾羽
        with s.group(rot(a["sway"] * 6, 60, 76)):
            leaf(s, 60, 76, 16, 6, 110, *LF)
            leaf(s, 60, 78, 14, 5, 140, "#6ac85a", LF[1])
        for x in (42, 52):
            s.line(f"M{x},82 L{x},89", "#8a8aa0", 2)
            s.flat(poly((x - 3, 90), (x, 87), (x + 3, 90)), "#8a8aa0", LINE, .8)
        s.part(ell(47, 70, 15, 14), *CRW)
        s.part(ell(47, 74, 8, 8), "#6a5a8a", "#4a3a68", line="none")
        for side in (-1, 1):
            with s.group(rot(side * (8 + a["flap"] * 10), 47 + side * 13, 66)):
                s.part(f"M{47 + side * 12},62 C{47 + side * 22},62 {47 + side * 24},72 {47 + side * 20},80 L{47 + side * 16},76 L{47 + side * 14},80 C{47 + side * 12},74 {47 + side * 12},68 {47 + side * 12},62 Z", *CRW[:2])
        # 头上顶着一片枯叶
        leaf(s, 47, 40, 12, 6, 10, "#c8a050", "#8a6a2a")
        s.part(ell(47, 50, 13, 12), *CRW)
        s.eye(42, 49, 3.4, 4, "#6ac87a", a["blink"], lid=.15)
        s.eye(52, 49, 3.4, 4, "#6ac87a", a["blink"], lid=.15)
        s.part(poly((44, 54), (50, 54), (47, 60)), "#c8c0a0", "#8a8268")
    wisps(s, a, ((24, 60), (72, 52)))
    return s


def d059(f):
    a = anim(f)
    LINE = "#140e20"
    s = Sprite(LINE)
    s.fit = .9
    s.lid_color = CRW[1]
    fl = a["flap"]
    # 破破烂烂的大翅膀
    for side in (-1, 1):
        with s.group(rot(side * (-4 + fl * 8), 48 + side * 10, 44)):
            x0 = 48 + side * 10
            s.part(poly((x0, 42), (x0 + side * 18, 22), (x0 + side * 38, 18), (x0 + side * 32, 28), (x0 + side * 40, 32), (x0 + side * 30, 38), (x0 + side * 36, 46),
                        (x0 + side * 24, 46), (x0 + side * 26, 56), (x0 + side * 14, 52), (x0 + side * 4, 58)), *CRW)
            s.line(f"M{x0},44 L{x0 + side * 30},26", CRW[1], 1)
    with s.group(rot(a["sway"] * 4, 56, 72)):
        for ang in (90, 120, 150):
            leaf(s, 56, 72, 18, 6, ang, *LF)
    for x in (42, 54):
        s.line(f"M{x},76 L{x},89", "#8a8aa0", 2.4)
        s.flat(poly((x - 4, 90), (x, 86), (x + 3, 90)), "#8a8aa0", LINE, .8)
    s.part("M32,52 C30,40 38,34 48,34 C58,34 66,40 64,52 C64,66 58,78 48,78 C38,78 32,66 32,52 Z", *CRW)
    s.part("M38,56 C38,48 58,48 58,56 C58,68 54,74 48,74 C42,74 38,68 38,56 Z", "#6a5a8a", "#4a3a68", line="none")
    # 荆棘藤缠在脖子上
    s.line("M32,46 Q40,52 48,46 Q56,52 64,46", "#5a8a3a", 2.4)
    for x in (36, 44, 52, 60):
        s.flat(poly((x, 47), (x + 1, 44), (x + 2, 47.5)), "#3a6a2a")
    with s.group(f"translate(0 {-a['breath'] * 1.2:.2f})"):
        with s.group(rot(a["sway"] * 5, 48, 16)):
            s.part(poly((42, 18), (38, 4), (46, 12), (48, 2), (50, 12), (58, 4), (54, 18)), *CRW[:2])
        s.part(ell(48, 24, 12, 11), *CRW)
        s.eye(43, 23, 3, 3.6, "#9aff7a", a["blink"], lid=.45)
        s.eye(53, 23, 3, 3.6, "#9aff7a", a["blink"], lid=.45)
        s.part(poly((44, 28), (52, 28), (48, 36)), "#c8c0a0", "#8a8268")
    wisps(s, a, ((14, 60), (82, 60), (48, 6)))
    return s


# ================================================================== 小茧蚕线（虫/幽灵）
GH = ("#ecf0ff", "#a8b0d8", "#ffffff")


def d060(f):
    a = anim(f)
    LINE = "#1e2040"
    s = Sprite(LINE)
    s.lid_color = GH[1]
    y0 = float_y(a, 3)
    s.flat(ell(48, 89, 14 + y0, 2), "#c8cce0")
    with s.group(f"translate(0 {y0:.2f})"):
        # 尾巴像幽灵一样拖成一缕
        with s.group(rot(a["sway"] * 10, 60, 72)):
            s.part("M54,70 C64,72 72,80 82,80 C76,84 66,84 56,78 Z", *GH[:2])
        for i in range(3, 0, -1):
            x = 42 + i * 7
            s.part(ell(x, 70 - i * .5, 8, 8), *GH)
        s.part(ell(40, 60, 13, 12), *GH)
        # 头顶小茧帽
        s.part("M30,54 C30,44 50,44 50,54 C46,52 34,52 30,54 Z", "#e8e0b0", "#b0a870")
        s.eye(35, 60, 3, 3.6, "#6a5aa8", a["blink"])
        s.eye(45, 60, 3, 3.6, "#6a5aa8", a["blink"])
        s.flat(ell(31, 65, 2.2, 1.2), "#c8b8f0")
        s.flat(ell(49, 65, 2.2, 1.2), "#c8b8f0")
        s.line("M38.5,66 Q40,67 41.5,66")
    return s


def d061(f):
    a = anim(f)
    LINE = "#1e2040"
    s = Sprite(LINE)
    s.fit = .94
    s.lid_color = GH[1]
    y0 = float_y(a, 3)
    RB = ["#ff8a9a", "#ffc87a", "#fff08a", "#9af0a0", "#8ac8ff", "#c8a0ff"]
    with s.group(f"translate(0 {y0:.2f})"):
        # 光环
        s.flat(ell(48, 14, 12, 3.5), "none", LINE, 2.6)
        s.flat(ell(48, 14, 12, 3.5), "none", "#fff08a", 1.4)
        # 身体弯成 S，一节一个彩虹色
        for i in range(6, 0, -1):
            t = i / 6
            x = 48 + math.sin(t * 3.2 + a["ph"] * .5) * 12
            y = 34 + t * 46
            r = 11 - t * 4
            s.part(ell(x, y, r, r * .9), RB[i - 1], GH[1], "#ffffff")
        with s.group(rot(a["sway"] * 10, 48, 82)):
            s.part("M44,82 C40,88 46,92 52,90 C48,88 48,86 50,82 Z", *GH[:2])
        # 两对半透明的小翅
        for side in (-1, 1):
            with s.group(rot(side * a["flap"] * 10, 48 + side * 8, 42)):
                s.part(ell(48 + side * 18, 40, 9, 5), "#f4f0ff", "#c8c0f0")
        s.part(ell(48, 30, 13, 12), *GH)
        for side in (-1, 1):
            s.line(f"M{48 + side * 5},20 C{48 + side * 8},14 {48 + side * 12},12 {48 + side * 14},10", LINE, 1)
            s.flat(ell(48 + side * 14, 10, 1.8, 1.8), RB[2 + side], LINE, .6)
        s.eye(43, 30, 3, 3.6, "#6a5aa8", a["blink"], lid=.25)
        s.eye(53, 30, 3, 3.6, "#6a5aa8", a["blink"], lid=.25)
        s.line("M46,36 Q48,37.5 50,36")
    return s


# ================================================================== 小泡虾线（水/火）
SH = ("#ff7a5a", "#c8402a", "#ffb8a0")
SB = ("#7ac8ff", "#3a88c8")


def d062(f):
    a = anim(f)
    LINE = "#2a1010"
    s = Sprite(LINE)
    s.lid_color = SH[1]
    b = a["breath"]
    # 尾扇：一团火
    with s.group(rot(a["sway"] * 8, 66, 78)):
        for i, x in enumerate((64, 70, 76)):
            s.part(ell(x, 80 - i * 3, 5 - i * .6, 4.5 - i * .5), *SH)
        flame(s, 82, 72, 11, a["flick"], 20)
    for x in (40, 46, 52, 58):
        s.line(f"M{x},82 L{x - 2},89", SH[1], 1.6)
    with s.group(scale_about(1 + .02 * b, 1 + .03 * b, 48, 89)):
        s.part(ell(46, 74, 16, 12), *SH)
        for x in (44, 52):
            s.line(f"M{x},64 Q{x + 3},74 {x},84", SH[1], 1)
        # 蓝色的水泡钳子
        for side in (-1, 1):
            s.part(ell(46 + side * 18, 70, 6, 5.5), *SB)
            s.line(f"M{46 + side * 15},68 L{46 + side * 21},72", LINE, 1)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        for side in (-1, 1):
            s.line(f"M{46 + side * 4},50 C{46 + side * 10},40 {46 + side * 16},36 {46 + side * 22},36", SH[1], 1.4)
        s.part(ell(46, 56, 13, 11), *SH)
        s.eye(41, 54, 3.4, 4, "#2a5a9a", a["blink"])
        s.eye(51, 54, 3.4, 4, "#2a5a9a", a["blink"])
        s.line("M44,61 Q46,62.5 48,61")
    bubble(s, 70, 48 - (a["f"] % 12), 3.2)
    return s


def d063(f):
    a = anim(f)
    LINE = "#2a1010"
    s = Sprite(LINE)
    s.fit = .88
    s.lid_color = SH[1]
    b = a["breath"]
    sw = a["sway"]
    with s.group(rot(sw * 5, 70, 74)):
        for i, x in enumerate((66, 74, 82)):
            s.part(ell(x, 76 - i * 4, 7 - i * .8, 6 - i * .6), *SH)
        flame(s, 90, 66, 16, a["flick"], 25)
    for x in (36, 44, 52, 60):
        s.line(f"M{x},78 L{x - 3},89", SH[1], 2)
    with s.group(f"translate(0 {-b * .8:.2f})"):
        s.part("M24,70 C24,58 36,52 50,52 C64,52 72,60 72,70 C72,80 62,84 48,84 C34,84 24,80 24,70 Z", *SH)
        for x in (38, 48, 58):
            s.line(f"M{x},54 Q{x + 3},68 {x},82", SH[1], 1)
        # 背上的蓝色甲壳
        s.part("M30,60 C34,52 62,52 66,60 C58,58 38,58 30,60 Z", *SB)
    # 两只大火钳
    for side in (-1, 1):
        op = 4 + a["sway"] * side * 3
        cx = 48 + side * 32
        with s.group(f"translate(0 {-b:.2f})"):
            s.line(f"M{48 + side * 18},62 C{48 + side * 24},56 {cx - side * 4},50 {cx},46", SH[1], 5)
            s.line(f"M{48 + side * 18},62 C{48 + side * 24},56 {cx - side * 4},50 {cx},46", SH[0], 3)
            s.part(f"M{cx - 7},{46} C{cx - 9},{34} {cx - 2},{28} {cx + 2},{30 - op} C{cx + 2},{36} {cx + 4},{40} {cx + 8},{40} C{cx + 8},{48} {cx},{50} {cx - 7},{46} Z", *SB, "#c8ecff")
            flame(s, cx, 30 - op, 10, a["flick"] * side, side * 10)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        for side in (-1, 1):
            s.line(f"M{48 + side * 4},34 C{48 + side * 12},22 {48 + side * 20},18 {48 + side * 28},20", SH[1], 1.6)
        s.part("M36,42 C36,32 42,28 48,28 C54,28 60,32 60,42 C60,50 54,54 48,54 C42,54 36,50 36,42 Z", *SH)
        s.part(poly((44, 30), (48, 20), (52, 30)), *SB)
        s.eye(43, 41, 3, 3.6, "#2a5a9a", a["blink"], lid=.4)
        s.eye(53, 41, 3, 3.6, "#2a5a9a", a["blink"], lid=.4)
        s.line("M45,49 Q48,50.5 51,49")
    return s


# ================================================================== 蠕蠕蚕线（虫）
WM = ("#d8d0a0", "#a09860", "#f4f0d0")
WG = ("#8ab04a", "#5a7a2a")


def d064(f):
    a = anim(f)
    LINE = "#2a2410"
    s = Sprite(LINE)
    s.lid_color = WM[1]
    # 一拱一拱往前爬
    hump = math.sin(a["ph"] * 2)
    for i in range(5, 0, -1):
        x = 36 + i * 9 - hump * .5 * i
        y = 82 - max(0, math.sin(a["ph"] * 2 + i * .8)) * 4
        s.part(ell(x, y, 7, 6.5), *WM)
        s.flat(ell(x, y - 4, 3, 1.4), WG[0])
        s.line(f"M{x},{y + 6} L{x},{y + 8}", WM[1], 1.6)
    s.part(ell(34, 74, 12, 11), *WM)
    for side in (-1, 1):
        s.part(ell(34 + side * 9, 64, 3, 3), *WG)
    s.eye(29.5, 73, 2.8, 3.4, "#3a3418", a["blink"])
    s.eye(38.5, 73, 2.8, 3.4, "#3a3418", a["blink"])
    s.line("M32,79 Q34,80.5 36,79")
    return s


def d065(f):
    a = anim(f)
    LINE = "#2a1a10"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = "#6a3a1a"
    M = ("#b8743a", "#7a4418", "#e0a870")
    # 千足：身体从后往前一节节翘起来
    segs = []
    for i in range(11):
        t = i / 10
        x = 86 - t * 50 + math.sin(t * 4 + a["ph"]) * 2
        y = 84 - max(0, t - .55) * 90
        segs.append((x, y, 6 + t * 3))
    for i, (x, y, r) in enumerate(segs):
        for k, side in enumerate((-1, 1)):
            ph = a["ph"] * 2 + i * 1.1 + k * 3
            s.line(f"M{x + side * 2},{y + r * .6} L{x + side * 3 + math.sin(ph) * 1.5},{min(89, y + r + 4)}", M[1], 1.4)
        s.part(ell(x, y, r, r * .9), *M)
        s.flat(ell(x, y - r * .55, r * .5, r * .2), "#e8c040")
    x, y, r = segs[-1]
    for side in (-1, 1):
        s.line(f"M{x + side * 4},{y - r} C{x + side * 8},{y - r - 8} {x + side * 14},{y - r - 10} {x + side * 16},{y - r - 6}", M[1], 1.4)
        s.line(f"M{x + side * 5},{y + r * .8} L{x + side * 7},{y + r + 3}", LINE, 1.6)
    s.part(ell(x, y, r + 3, r + 2), *M)
    s.eye(x - 4.5, y - 1, 2.8, 3.4, "#e8c040", a["blink"], lid=.35)
    s.eye(x + 4.5, y - 1, 2.8, 3.4, "#e8c040", a["blink"], lid=.35)
    s.line(f"M{x - 2},{y + 5} Q{x},{y + 6.5} {x + 2},{y + 5}")
    return s


# ================================================================== 卵卵蟹线（岩石）
RS = ("#b8a088", "#7a6450", "#e0d0b8")
CB = ("#e08a5a", "#a8502a", "#ffc0a0")


def crab(s, a, cx, cy, w, h, claw, legs=3):
    """正面的螃蟹：扁宽的身子、两只钳子举在两边、眼睛顶在小柄上"""
    for side in (-1, 1):
        for i in range(legs):
            x = cx + side * (w * .55 + i * w * .14)
            ph = a["ph"] * 2 + i
            s.line(f"M{x},{cy + h * .2} L{x + side * w * .25},{cy + h * .6} L{x + side * w * .28 + math.sin(ph)},{89}", CB[1], 2.4)
            s.line(f"M{x},{cy + h * .2} L{x + side * w * .25},{cy + h * .6} L{x + side * w * .28 + math.sin(ph)},{89}", CB[0], 1.2)
    s.part(ell(cx, cy, w, h), *CB)
    for side in (-1, 1):
        op = 3 + math.sin(a["ph"] + side) * 2
        x = cx + side * (w + claw * .4)
        y = cy - h * .4
        s.line(f"M{cx + side * w * .7},{cy} L{x},{y}", CB[1], 3)
        s.part(f"M{x - claw * .6},{y} C{x - claw * .7},{y - claw} {x},{y - claw * 1.2} {x + claw * .2},{y - claw * .9 - op} "
               f"C{x + claw * .1},{y - claw * .5} {x + claw * .5},{y - claw * .5} {x + claw * .7},{y - claw * .6} C{x + claw * .8},{y} {x + claw * .3},{y + claw * .3} {x - claw * .6},{y} Z", *CB)


def crab_face(s, a, cx, cy, gap, r, lid=0.0, stalk=0):
    """眼睛顶在小柄上，柄往下伸 stalk 像素"""
    for side in (-1, 1):
        if stalk:
            s.line(f"M{cx + side * gap},{cy + r} L{cx + side * gap},{cy + r + stalk}", CB[1], 2.4)
        s.part(ell(cx + side * gap, cy, r * 1.3, r * 1.3), *CB)
        s.eye(cx + side * gap, cy, r, r * 1.15, "#3a2a1a", a["blink"], lid=lid)


def d066(f):
    a = anim(f)
    LINE = "#2a1a10"
    s = Sprite(LINE)
    s.lid_color = CB[1]
    b = a["breath"]
    crab(s, a, 48, 80, 16, 7, 8)
    with s.group(f"translate(0 {-b * 1:.2f})"):
        # 蛋形的石头壳
        s.part("M32,72 C30,52 40,40 48,40 C56,40 66,52 64,72 C58,76 38,76 32,72 Z", *RS)
        s.line("M34,62 L40,58 L46,62 L52,56 L58,60 L62,58", RS[1], 1.2)
        crab_face(s, a, 48, 34, 7, 3.6, stalk=6)
    return s


def d067(f):
    a = anim(f)
    LINE = "#2a1a10"
    s = Sprite(LINE)
    s.fit = .94
    s.lid_color = CB[1]
    b = a["breath"]
    crab(s, a, 48, 76, 22, 9, 13)
    with s.group(f"translate(0 {-b * 1:.2f})"):
        # 背上一块块尖石
        s.part("M24,72 C22,58 32,48 48,48 C64,48 74,58 72,72 Z", *RS)
        for x, h in ((34, 8), (44, 14), (54, 12), (64, 7)):
            s.part(poly((x - 5, 54 + (14 - h) * .3), (x, 54 - h), (x + 5, 54 + (14 - h) * .3)), *RS)
        crab_face(s, a, 48, 38, 13, 3.6, lid=.3, stalk=8)
    return s


def d068(f):
    a = anim(f)
    LINE = "#2a1a10"
    s = Sprite(LINE)
    s.fit = .86
    s.lid_color = CB[1]
    b = a["breath"]
    crab(s, a, 48, 78, 26, 9, 16)
    with s.group(f"translate(0 {-b * 1:.2f})"):
        # 背着一整座山：山顶积雪，山腰长草
        s.part(poly((18, 74), (30, 40), (38, 48), (50, 20), (60, 36), (66, 30), (80, 74)), *RS)
        s.flat(poly((44, 30), (50, 20), (55, 28), (52, 30), (49, 27), (47, 31)), "#ffffff", LINE, .8)
        s.flat(poly((27, 48), (30, 40), (34, 44), (31, 47)), "#ffffff")
        for x, y in ((28, 62), (64, 58), (42, 54)):
            s.flat(ell(x, y, 4, 2), "#7aaa4a")
            s.flat(ell(x, y - 1, 2.5, 1.2), "#a8d070")
        s.flat(poly((50, 44), (52, 40), (54, 44)), "#5a8a3a")
        crab_face(s, a, 48, 74, 11, 3.8, lid=.4)
    return s


# ================================================================== 风蝠线（飞行/水）
BT = ("#6ab0e8", "#3a78b8", "#b0dcff")
BTw = ("#c8ecff", "#7ab8e0")


def bat_wing(s, x, y, side, span, ang, col, mem):
    with s.group(rot(side * ang, x, y)):
        s.part(f"M{x},{y - 4} C{x + side * span * .4},{y - span * .5} {x + side * span * .8},{y - span * .5} {x + side * span},{y - span * .2} "
               f"C{x + side * span * .85},{y} {x + side * span * .8},{y + span * .1} {x + side * span * .65},{y + span * .15} "
               f"C{x + side * span * .55},{y + span * .05} {x + side * span * .45},{y + span * .1} {x + side * span * .35},{y + span * .2} "
               f"C{x + side * span * .25},{y + span * .1} {x + side * span * .12},{y + span * .12} {x},{y + 6} Z", *mem)
        s.line(f"M{x},{y - 4} C{x + side * span * .4},{y - span * .5} {x + side * span * .8},{y - span * .5} {x + side * span},{y - span * .2}", col[1], 2)
        for k in (.35, .65):
            s.line(f"M{x + side * span * k},{y - span * .38} L{x + side * span * k},{y + span * .12}", col[1], 1)


def d069(f):
    a = anim(f)
    LINE = "#10203a"
    s = Sprite(LINE)
    s.lid_color = BT[1]
    y0 = float_y(a, 4)
    fl = a["flap"]
    s.flat(ell(48, 89, 12 + y0, 2), "#c0d0e0")
    with s.group(f"translate(0 {y0 - 6:.2f})"):
        for side in (-1, 1):
            bat_wing(s, 48 + side * 10, 56, side, 22, fl * 20, BT, BTw)
        s.part(ell(48, 58, 14, 13), *BT)
        # 水滴形的大耳朵
        for side in (-1, 1):
            s.part(f"M{48 + side * 6},48 C{48 + side * 4},40 {48 + side * 10},32 {48 + side * 14},28 C{48 + side * 16},36 {48 + side * 16},44 {48 + side * 12},50 Z", *BT)
            s.flat(f"M{48 + side * 8},46 C{48 + side * 8},40 {48 + side * 11},36 {48 + side * 13},33 C{48 + side * 14},38 {48 + side * 14},44 {48 + side * 11},47 Z", BTw[0])
        s.part(ell(48, 63, 7, 5), *BTw, line="none")
        s.eye(43, 57, 3.2, 3.8, "#1e4a8a", a["blink"])
        s.eye(53, 57, 3.2, 3.8, "#1e4a8a", a["blink"])
        s.line("M45.5,64 Q48,66 50.5,64")
        s.flat("M46.5,64.5 L47.3,66.5 L48,64.8 Z", "#ffffff")
        s.flat("M48,64.8 L48.7,66.5 L49.5,64.5 Z", "#ffffff")
        for x in (44, 52):
            s.line(f"M{x},70 L{x},73", BT[1], 1.6)
    return s


def d070(f):
    a = anim(f)
    LINE = "#10203a"
    s = Sprite(LINE)
    s.fit = .94
    s.lid_color = BT[1]
    y0 = float_y(a, 3)
    fl = a["flap"]
    with s.group(f"translate(0 {y0 - 4:.2f})"):
        for side in (-1, 1):
            bat_wing(s, 48 + side * 10, 50, side, 34, fl * 16, BT, BTw)
        s.part("M34,52 C32,40 40,34 48,34 C56,34 64,40 62,52 C62,64 56,72 48,72 C40,72 34,64 34,52 Z", *BT)
        # 胸前一团云毛
        for x, y, r in ((42, 58, 6), (54, 58, 6), (48, 64, 7), (48, 54, 5)):
            s.part(ell(x, y, r, r * .9), "#ffffff", "#c8dcec", line="none")
        for side in (-1, 1):
            s.part(f"M{48 + side * 6},38 C{48 + side * 6},28 {48 + side * 12},20 {48 + side * 18},16 C{48 + side * 18},26 {48 + side * 16},34 {48 + side * 12},40 Z", *BT)
        s.eye(42.5, 44, 3, 3.6, "#1e4a8a", a["blink"], lid=.25)
        s.eye(53.5, 44, 3, 3.6, "#1e4a8a", a["blink"], lid=.25)
        s.line("M45.5,50 Q48,51.5 50.5,50")
        for x in (42, 54):
            s.line(f"M{x},72 L{x},76", BT[1], 2)
    # 身边飘的小云
    for i in range(2):
        t = (a["f"] / 24 + i / 2) % 1
        x = 10 + t * 76
        s.flat(ell(x, 82 - i * 4, 6, 2.5), "#ffffff", "#c8dcec", .8)
    return s


def d071(f):
    a = anim(f)
    LINE = "#0e1a34"
    s = Sprite(LINE)
    s.fit = .86
    s.lid_color = "#1e4a8a"
    D = ("#3a6ac8", "#1e3a88", "#7aa8ff")
    y0 = float_y(a, 3)
    fl = a["flap"]
    with s.group(f"translate(0 {y0 - 4:.2f})"):
        # 翼膜下沿是一道道浪花
        for side in (-1, 1):
            with s.group(rot(side * fl * 12, 48 + side * 12, 46)):
                x0 = 48 + side * 12
                s.part(f"M{x0},40 C{x0 + side * 14},20 {x0 + side * 32},14 {x0 + side * 44},20 "
                       f"C{x0 + side * 40},26 {x0 + side * 44},32 {x0 + side * 38},36 C{x0 + side * 34},32 {x0 + side * 32},40 {x0 + side * 28},42 "
                       f"C{x0 + side * 24},38 {x0 + side * 20},46 {x0 + side * 16},48 C{x0 + side * 12},44 {x0 + side * 6},52 {x0},52 Z", *BTw)
                s.line(f"M{x0},40 C{x0 + side * 14},20 {x0 + side * 32},14 {x0 + side * 44},20", D[1], 2.4)
                for k in (16, 28):
                    s.line(f"M{x0 + side * k},{24 - k * .1} L{x0 + side * k},{46 - k * .3}", D[1], 1)
                for k in (36, 24, 12):
                    s.flat(ell(x0 + side * k, 42 - k * .1, 2.5, 1.2), "#ffffff")
        s.part("M32,48 C30,34 38,28 48,28 C58,28 66,34 64,48 C64,62 58,72 48,72 C38,72 32,62 32,48 Z", *D)
        s.part("M38,52 C38,44 58,44 58,52 C58,64 54,70 48,70 C42,70 38,64 38,52 Z", *BTw, line="none")
        for side in (-1, 1):
            s.part(f"M{48 + side * 6},32 C{48 + side * 6},22 {48 + side * 14},12 {48 + side * 20},8 C{48 + side * 20},20 {48 + side * 18},28 {48 + side * 12},34 Z", *D)
            s.flat(f"M{48 + side * 9},30 C{48 + side * 10},22 {48 + side * 15},16 {48 + side * 18},12 C{48 + side * 18},20 {48 + side * 16},26 {48 + side * 13},31 Z", BTw[0])
        s.eye(42, 40, 3.2, 3.6, "#7af0ff", a["blink"], lid=.45)
        s.eye(54, 40, 3.2, 3.6, "#7af0ff", a["blink"], lid=.45)
        s.line("M44,47 Q48,49 52,47")
        s.flat("M45,47.5 L46,50 L47,48 Z", "#ffffff")
        s.flat("M49,48 L50,50 L51,47.5 Z", "#ffffff")
        for x in (42, 54):
            s.line(f"M{x},72 L{x},77", D[1], 2.4)
    return s


# ================================================================== 小滴螺线（水）
SN = ("#8ad8f0", "#3a98c0", "#d8f8ff")
SHL = ("#5a88e8", "#2a54a8", "#9ac0ff")


def spiral(s, cx, cy, r, turns, col, w=1.2):
    pts = []
    for i in range(40):
        t = i / 39
        ang = t * turns * 2 * math.pi
        rr = r * (1 - t)
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    s.line("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), col, w)


def d072(f):
    a = anim(f)
    LINE = "#10203a"
    s = Sprite(LINE)
    s.lid_color = SN[1]
    stretch = math.sin(a["ph"]) * 2
    # 软软的身体，往前伸缩
    s.part(f"M24,{88} C22,80 28,74 36,74 L66,76 C72,78 74,86 70,89 L24,89 Z", *SN)
    with s.group(f"translate({stretch * .3:.2f} 0)"):
        # 水滴形的壳
        s.part("M58,48 C70,56 76,66 74,76 C72,86 60,88 54,82 C46,74 48,60 58,48 Z", *SHL)
        spiral(s, 62, 74, 9, 1.6, SHL[1])
        s.flat(ell(58, 64, 2, 3), "#ffffff")
    with s.group(f"translate({-stretch:.2f} 0)"):
        for side in (-1, 1):
            s.line(f"M{34 + side * 5},62 L{34 + side * 7},54", SN[1], 1.6)
            s.part(ell(34 + side * 7, 53, 2.2, 2.2), *SN)
        s.part(ell(34, 70, 11, 10), *SN)
        s.eye(30, 69, 2.8, 3.4, "#1e4a8a", a["blink"])
        s.eye(38, 69, 2.8, 3.4, "#1e4a8a", a["blink"])
        s.flat(ell(26, 74, 2, 1.1), "#ff9ac0")
        s.flat(ell(42, 74, 2, 1.1), "#ff9ac0")
        s.line("M32.5,75 Q34,76.5 35.5,75")
    return s


def d073(f):
    a = anim(f)
    LINE = "#10203a"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = SN[1]
    b = a["breath"]
    # 坐在一只大海螺里
    s.part("M20,86 C18,60 30,34 54,22 C58,30 64,34 72,36 C82,52 82,74 74,88 Z", "#f6d0b0", "#c8946a", "#fff0e0")
    for i, (x, y) in enumerate(((54, 22), (60, 30), (68, 36))):
        s.part(poly((x - 3, y + 2), (x + 2, y - 8), (x + 4, y + 3)), "#f6d0b0", "#c8946a")
    s.line("M24,70 Q46,60 76,64", "#c8946a", 1.2)
    s.line("M30,50 Q50,42 74,48", "#c8946a", 1.2)
    s.part("M30,88 C30,66 40,54 52,54 C64,54 70,66 70,88 Z", "#ff9ab8", "#d0607a")
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        s.part(ell(50, 66, 13, 12), *SN)
        s.part(ell(50, 74, 8, 5), *SN[::2], line="none")
        # 小王冠
        s.part(poly((42, 56), (42, 48), (46, 52), (50, 44), (54, 52), (58, 48), (58, 56)), "#ffd24a", "#c08a1a")
        s.flat(ell(50, 52, 1.4, 1.4), SHL[0], LINE, .6)
        for side in (-1, 1):
            s.line(f"M{50 + side * 10},60 L{50 + side * 14},54", SN[1], 1.6)
            s.part(ell(50 + side * 14, 53, 2.2, 2.2), *SN)
        s.eye(45, 66, 3, 3.6, "#1e4a8a", a["blink"], lid=.2)
        s.eye(55, 66, 3, 3.6, "#1e4a8a", a["blink"], lid=.2)
        s.line("M47.5,72 Q50,73.5 52.5,72")
        # 小触手手臂
        for side in (-1, 1):
            s.line(f"M{50 + side * 11},74 C{50 + side * 16},76 {50 + side * 18},80 {50 + side * 16 + a['sway'] * side},84", SN[1], 3.4)
            s.line(f"M{50 + side * 11},74 C{50 + side * 16},76 {50 + side * 18},80 {50 + side * 16 + a['sway'] * side},84", SN[0], 2)
    return s


# ================================================================== 幻幻鸮线（灵能）
OW = ("#e080c0", "#a84a88", "#ffc0e8")
OWb = ("#fff0f8", "#e0b8d0")


def d074(f):
    a = anim(f)
    LINE = "#2a1028"
    s = Sprite(LINE)
    s.lid_color = OW[1]
    dy = -abs(math.sin(a["ph"])) * 2
    with s.group(f"translate(0 {dy:.2f})"):
        for x in (42, 54):
            s.line(f"M{x},84 L{x},89", "#ffb43a", 2)
            s.flat(poly((x - 3, 90), (x, 87), (x + 3, 90)), "#ffb43a", LINE, .8)
        # 整只就是一个蛋形
        s.part("M30,64 C30,46 38,38 48,38 C58,38 66,46 66,64 C66,78 58,86 48,86 C38,86 30,78 30,64 Z", *OW)
        s.part("M38,70 C38,62 58,62 58,70 C58,80 54,84 48,84 C42,84 38,80 38,70 Z", *OWb, line="none")
        for y in (70, 76):
            s.line(f"M44,{y} l2,2 l2,-2 l2,2 l2,-2", OWb[1], 1)
        # 角羽
        for side in (-1, 1):
            s.part(poly((48 + side * 8, 42), (48 + side * 16, 32), (48 + side * 15, 44)), *OW)
        for side in (-1, 1):
            with s.group(rot(side * a["flap"] * 6, 48 + side * 16, 62)):
                s.part(f"M{48 + side * 16},56 C{48 + side * 22},60 {48 + side * 22},70 {48 + side * 18},76 C{48 + side * 16},70 {48 + side * 15},62 {48 + side * 16},56 Z", *OW[:2])
        # 大眼圈
        for side in (-1, 1):
            s.part(ell(48 + side * 7, 54, 7, 7), *OWb)
            s.eye(48 + side * 7, 54, 3.8, 4.4, "#7a2a8a", a["blink"])
        s.part(poly((46, 60), (50, 60), (48, 64)), "#ffb43a", "#c87a1a")
        # 额头第三只眼（宝石）
        s.flat(poly((48, 42), (50, 45), (48, 48), (46, 45)), "#7af0ff", LINE, .7)
    return s


def d075(f):
    a = anim(f)
    LINE = "#2a1028"
    s = Sprite(LINE)
    s.fit = .9
    s.lid_color = OW[1]
    y0 = float_y(a, 3)
    s.flat(ell(48, 89, 16 + y0, 2.5), "#d8c8d8")
    with s.group(f"translate(0 {y0 - 4:.2f})"):
        # 背后的光轮
        s.flat(ell(48, 40, 26, 26), "none", LINE, 3)
        s.flat(ell(48, 40, 26, 26), "none", "#ffe07a", 1.6)
        for i in range(8):
            ang = i * math.pi / 4 + a["ph"] * .25
            s.flat(ell(48 + math.cos(ang) * 26, 40 + math.sin(ang) * 26, 1.6, 1.6), "#fff8c0", LINE, .5)
        # 盘腿打坐：翅膀像长袍一样裹着
        s.part("M24,80 C22,60 30,44 48,44 C66,44 74,60 72,80 C64,86 32,86 24,80 Z", *OW)
        s.part("M36,80 C36,64 42,54 48,54 C54,54 60,64 60,80 Z", *OWb, line="none")
        s.line("M48,56 L48,80", OWb[1], 1)
        for side in (-1, 1):
            s.part(poly((48 + side * 8, 24), (48 + side * 18, 10), (48 + side * 17, 26)), *OW)
        s.part(ell(48, 32, 15, 13), *OW)
        for side in (-1, 1):
            s.part(ell(48 + side * 7, 31, 6.5, 6.5), *OWb)
            # 冥想：眼睛闭着
            s.line(f"M{48 + side * 7 - 3.5},31 Q{48 + side * 7},34 {48 + side * 7 + 3.5},31", LINE, 1.4)
        s.part(poly((46, 37), (50, 37), (48, 41)), "#ffb43a", "#c87a1a")
        s.flat(poly((48, 18), (50.5, 22), (48, 26), (45.5, 22)), "#7af0ff", LINE, .8)
    # 身边浮着三颗灵能珠
    for i in range(3):
        ang = a["ph"] + i * 2.1
        s.flat(ell(48 + math.cos(ang) * 36, 60 + math.sin(ang) * 6 + y0, 3, 3), "#ffc0e8", LINE, .8)
    return s


SPECIES = {"d056": d056, "d057": d057, "d058": d058, "d059": d059, "d060": d060, "d061": d061,
           "d062": d062, "d063": d063, "d064": d064, "d065": d065, "d066": d066, "d067": d067,
           "d068": d068, "d069": d069, "d070": d070, "d071": d071, "d072": d072, "d073": d073,
           "d074": d074, "d075": d075}
