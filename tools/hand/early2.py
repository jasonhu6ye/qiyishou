"""#025-#039：小鳞蛟线、小砾蜥线、小铁偶线、幼蛇线、雪龙线"""
import math

from kit import Sprite, anim, ell, poly, rot, scale_about
from fox import HIND, LEG
from early1 import smoke
from legends2 import star


def dragon_head(s, a, cx, cy, w, C, horn, lid=0.0, iris="#e8a020", belly=None, horn_len=1.0):
    """正脸的龙头：圆脑袋、往前的鼻吻、一对后掠的角。C=(主, 暗, 高光)"""
    m, ms, mh = C
    for side in (-1, 1):
        x0 = cx + side * w * .5
        s.part(f"M{x0},{cy - w * .6} C{x0 + side * w * .3},{cy - w * (1 + .3 * horn_len)} {x0 + side * w * .6},{cy - w * (1.1 + .3 * horn_len)} {x0 + side * w * .7},{cy - w * (1.3 + .4 * horn_len)} "
               f"C{x0 + side * w * .8},{cy - w * .9} {x0 + side * w * .5},{cy - w * .5} {x0 + side * w * .3},{cy - w * .3} Z", horn[0], horn[1])
    s.part(f"M{cx - w},{cy} C{cx - w},{cy - w * .8} {cx - w * .5},{cy - w} {cx},{cy - w} C{cx + w * .5},{cy - w} {cx + w},{cy - w * .8} {cx + w},{cy} "
           f"C{cx + w},{cy + w * .7} {cx + w * .5},{cy + w * .9} {cx},{cy + w * .9} C{cx - w * .5},{cy + w * .9} {cx - w},{cy + w * .7} {cx - w},{cy} Z", m, ms, mh)
    s.flat(ell(cx - w * .12, cy + w * .42, .8, .6), s.outline)
    s.flat(ell(cx + w * .12, cy + w * .42, .8, .6), s.outline)
    r = w * .24
    s.eye(cx - w * .45, cy - w * .15, r, r * 1.2, iris, a["blink"], lid=lid)
    s.eye(cx + w * .45, cy - w * .15, r, r * 1.2, iris, a["blink"], lid=lid)
    s.line(f"M{cx - w * .25},{cy + w * .68} Q{cx},{cy + w * .8} {cx + w * .25},{cy + w * .68}")


def wing(s, x, y, side, span, C, ang, membrane=None):
    """蝙蝠翼：翼根在 (x, y)，side=-1 往左张"""
    m, ms = C[0], C[1]
    with s.group(rot(ang * side, x, y)):
        s.part(f"M{x},{y} C{x + side * span * .3},{y - span * .6} {x + side * span * .7},{y - span * .8} {x + side * span},{y - span * .7} "
               f"L{x + side * span * .8},{y - span * .35} L{x + side * span * .85},{y - span * .1} L{x + side * span * .55},{y - span * .05} L{x + side * span * .5},{y + span * .15} Z",
               membrane[0] if membrane else m, membrane[1] if membrane else ms)
        s.line(f"M{x},{y} C{x + side * span * .3},{y - span * .6} {x + side * span * .7},{y - span * .8} {x + side * span},{y - span * .7}", ms, 2)
        s.line(f"M{x + side * span * .55},{y - span * .6} L{x + side * span * .55},{y - span * .05}", ms, 1)


# ================================================================== 小鳞蛟线（龙/飞行）
DV = ("#7a52e0", "#4a2aa8", "#a88aff")
LV = ("#d8ccff", "#a08ae0")
HORN = ("#f4ecd8", "#b8a888")


def d025(f):
    a = anim(f)
    LINE = "#1a1030"
    s = Sprite(LINE)
    s.lid_color = DV[1]
    b = a["breath"]
    with s.group(rot(max(0, math.sin(a["ph"] * 2)) * -10, 62, 82)):
        s.part("M60,80 C70,78 80,82 86,76 C86,84 76,90 62,88 Z", *DV)
        s.part(poly((84, 78), (90, 72), (88, 80)), LV[0], LV[1])
    for side in (-1, 1):
        wing(s, 48 + side * 10, 66, side, 16, DV, -10 + a["flap"] * 8, LV)
    with s.group(scale_about(1 + .02 * b, 1 + .03 * b, 48, 89)):
        s.part(ell(48, 76, 16, 13), *DV)
        s.part(ell(48, 79, 10, 9), LV[0], LV[1], line="none")
        for y in (75, 80, 85):
            s.line(f"M42,{y} L54,{y}", LV[1], 1)
        s.part(ell(36, 88, 6, 2.8), *DV[:2])
        s.part(ell(60, 88, 6, 2.8), *DV[:2])
    with s.group(f"translate(0 {-b * 1.3:.2f})"):
        dragon_head(s, a, 48, 50, 16, DV, HORN, iris="#e8a020", belly=LV, horn_len=.5)
    smoke(s, a, 44, 53)
    return s


def d026(f):
    a = anim(f)
    LINE = "#1a1030"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = DV[1]
    b = a["breath"]
    with s.group(rot(max(0, math.sin(a["ph"] * 2)) * -8, 72, 66)):
        s.part("M70,64 C82,62 90,70 94,82 C86,82 78,78 70,72 Z", *DV)
        s.part(poly((90, 78), (96, 74), (94, 84)), LV[0], LV[1])
    wing(s, 58, 48, 1, 30, DV, -10 - a["flap"] * 8, LV)
    s.part(LEG(36, 64, 89, 7), DV[1], "#2a1478")
    s.part(HIND(70, 60, 89), DV[1], "#2a1478")
    with s.group(f"translate(0 {-b * .7:.2f})"):
        s.part("M26,58 C28,46 44,42 58,44 C72,45 80,52 80,62 C80,70 72,74 56,74 C40,74 26,70 26,58 Z", *DV)
        s.part("M30,64 C36,72 50,75 62,73 C52,68 40,66 30,64 Z", LV[0], LV[1], line="none")
        for x in (48, 56, 64, 72):
            s.part(poly((x - 2, 46), (x, 40), (x + 3, 47)), LV[0], LV[1])
    s.part(LEG(31, 60, 88, 8), *DV)
    s.part(ell(30, 89, 5, 2.2), HORN[0], HORN[1])
    s.part(HIND(65, 56, 88), *DV)
    s.part(ell(66, 89, 5, 2.2), HORN[0], HORN[1])
    wing(s, 44, 48, -1, 28, DV, -10 - a["flap"] * 8, LV)
    with s.group(f"translate(0 {-b * 1.3:.2f})"):
        # 脖子
        s.part("M26,54 C22,46 24,38 26,32 L34,32 C33,38 34,46 38,52 Z", *DV)
        dragon_head(s, a, 30, 26, 13, DV, HORN, lid=.2, belly=LV)
    smoke(s, a, 27, 28)
    return s


def d027(f):
    a = anim(f)
    LINE = "#1a1030"
    s = Sprite(LINE)
    s.fit = .86
    s.lid_color = DV[1]
    b = a["breath"]
    fl = a["flap"]
    # 双足站立，大翅膀张开
    for side in (-1, 1):
        wing(s, 48 + side * 8, 44, side, 40, DV, -6 + fl * 8, LV)
    with s.group(rot(a["sway"] * 5, 58, 78)):
        s.part("M56,74 C70,74 82,80 90,88 C78,90 66,88 54,84 Z", *DV)
        s.part(poly((86, 84), (94, 82), (90, 90)), LV[0], LV[1])
    s.part("M36,72 C30,76 30,84 32,89 L42,89 C42,84 44,80 46,76 Z", *DV)
    s.part("M60,72 C66,76 66,84 64,89 L54,89 C54,84 52,80 50,76 Z", *DV)
    s.part(ell(36, 89, 6.5, 2.4), HORN[0], HORN[1])
    s.part(ell(60, 89, 6.5, 2.4), HORN[0], HORN[1])
    with s.group(f"translate(0 {-b * .8:.2f})"):
        s.part("M32,52 C30,40 38,34 48,34 C58,34 66,40 64,52 C64,66 60,78 48,78 C36,78 32,66 32,52 Z", *DV)
        s.part("M38,54 C38,44 58,44 58,54 C58,68 54,76 48,76 C42,76 38,68 38,54 Z", LV[0], LV[1], line="none")
        for y in (52, 58, 64, 70):
            s.line(f"M41,{y} L55,{y}", LV[1], 1)
        # 手臂
        for side in (-1, 1):
            s.part(f"M{48 + side * 14},44 C{48 + side * 20},48 {48 + side * 22},56 {48 + side * 20},62 L{48 + side * 15},60 C{48 + side * 16},56 {48 + side * 14},52 {48 + side * 10},50 Z", *DV)
    with s.group(f"translate(0 {-b * 1.3:.2f})"):
        dragon_head(s, a, 48, 22, 14, DV, HORN, lid=.4, belly=LV, horn_len=1.4)
        for side in (-1, 1):   # 耳鳍
            s.part(f"M{48 + side * 13},20 L{48 + side * 22},14 L{48 + side * 20},24 Z", LV[0], LV[1])
    smoke(s, a, 46, 24)
    return s


# ================================================================== 小砾蜥线（岩石/恶）
RK = ("#b6a14a", "#7a6a2a", "#e0d080")
DK = ("#5a463a", "#33261e", "#86705e")
RED = "#e83a3a"


def pebble(s, x, y, r):
    s.part(ell(x, y, r * 1.1, r), "#a89a88", "#6e6052", "#d8ccbc")


def d028(f):
    a = anim(f)
    LINE = "#1a120c"
    s = Sprite(LINE)
    s.lid_color = DK[1]
    b = a["breath"]
    with s.group(rot(a["sway"] * 10, 62, 82)):
        s.part("M60,80 C70,80 80,76 86,68 C86,78 76,88 60,88 Z", *RK)
        pebble(s, 82, 72, 3)
    with s.group(scale_about(1 + .02 * b, 1 + .03 * b, 48, 89)):
        s.part(ell(48, 77, 17, 12), *RK)
        s.part(ell(48, 81, 10, 7), "#f0e4b8", "#c8b884", line="none")
        for x, y, r in ((36, 70, 3.2), (48, 67, 3.6), (60, 70, 3)):
            pebble(s, x, y, r)
        for x in (34, 62):
            s.part(ell(x, 88, 6, 2.6), *RK[:2])
            for k in (-3, 0, 3):
                s.line(f"M{x + k},89 L{x + k},91", LINE, 1)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        s.part(ell(48, 54, 17, 14), *RK)
        # 恶系：眼睛上一条深色面罩
        s.part("M32,44 C38,38 58,38 64,44 L64,47 C58,44 52,46 48,48 C44,46 38,44 32,47 Z", DK[0], DK[1])
        for x, y, r in ((40, 41, 2.4), (48, 39, 3), (56, 41, 2.4)):
            pebble(s, x, y, r)
        s.eye(41, 51, 3.4, 4, RED, a["blink"], lid=.2)
        s.eye(55, 51, 3.4, 4, RED, a["blink"], lid=.2)
        s.line("M44,62 Q48,63.5 52,62")
        s.flat("M45,62.3 L46,64.5 L47,62.6 Z", "#ffffff")
        s.flat("M49,62.6 L50,64.5 L51,62.3 Z", "#ffffff")
    return s


def d029(f):
    a = anim(f)
    LINE = "#1a120c"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = DK[1]
    b = a["breath"]
    with s.group(rot(a["sway"] * 6, 74, 66)):
        s.part("M72,64 C84,62 92,70 94,82 C86,82 78,78 72,72 Z", *RK)
        for x, y in ((82, 66), (90, 74)):
            s.part(poly((x - 3, y + 1), (x + 1, y - 7), (x + 4, y + 2)), "#a89a88", "#6e6052")
    s.part(LEG(34, 68, 89, 9), RK[1], "#4a3e1a")
    s.part(LEG(70, 66, 89, 10), RK[1], "#4a3e1a")
    with s.group(f"translate(0 {6 - b * .7:.2f})"):
        s.part("M22,60 C22,48 38,42 56,44 C72,46 82,52 82,62 C82,70 72,74 56,74 C38,74 22,70 22,60 Z", *RK)
        s.part("M28,66 C36,72 52,74 66,72 C54,68 40,66 28,66 Z", "#f0e4b8", "#c8b884", line="none")
        for x, h in ((38, 9), (48, 13), (58, 15), (68, 11), (76, 7)):
            s.part(poly((x - 5, 48), (x, 48 - h), (x + 5, 48)), "#a89a88", "#6e6052", "#d8ccbc")
    s.part(LEG(28, 64, 88, 10), *RK)
    s.part(ell(27, 89, 6, 2.2), DK[0], DK[1])
    s.part(LEG(64, 62, 88, 11), *RK)
    s.part(ell(64, 89, 6, 2.2), DK[0], DK[1])
    with s.group(f"translate(0 {6 - b * 1.2:.2f})"):
        for side in (-1, 1):
            s.part(f"M{28 + side * 8},28 L{28 + side * 16},18 L{28 + side * 14},32 Z", "#a89a88", "#6e6052")
        s.part("M12,40 C12,30 20,24 28,24 C36,24 44,30 44,40 C44,50 36,56 28,56 C20,56 12,50 12,40 Z", *RK)
        s.part("M13,31 C18,26 38,26 43,31 L43,34 C38,31 32,33 28,35 C24,33 18,31 13,34 Z", DK[0], DK[1])
        s.eye(21.5, 38, 3, 3.6, RED, a["blink"], lid=.45)
        s.eye(34.5, 38, 3, 3.6, RED, a["blink"], lid=.45)
        s.flat(ell(26, 47, .9, .7), LINE)
        s.flat(ell(30, 47, .9, .7), LINE)
        s.line("M22,51 Q28,53 34,51")
        s.flat("M23,51.3 L24.5,54 L26,51.8 Z", "#ffffff")
        s.flat("M30,51.8 L31.5,54 L33,51.3 Z", "#ffffff")
    return s


def d030(f):
    a = anim(f)
    LINE = "#1a120c"
    s = Sprite(LINE)
    s.fit = .86
    s.lid_color = DK[1]
    b = a["breath"]
    with s.group(rot(a["sway"] * 5, 76, 62)):
        s.part("M72,58 C86,56 96,66 98,82 C88,82 80,76 72,70 Z", *DK)
        for x, y in ((84, 60), (92, 68)):
            s.part(poly((x - 3, y + 1), (x + 1, y - 9), (x + 5, y + 2)), *RK)
    s.part(LEG(32, 70, 89, 11), DK[1], "#1a120c")
    s.part(LEG(72, 68, 89, 12), DK[1], "#1a120c")
    with s.group(f"translate(0 {6 - b * .7:.2f})"):
        s.part("M18,58 C18,44 34,36 56,38 C74,40 86,48 86,60 C86,70 74,76 56,76 C36,76 18,70 18,58 Z", *DK)
        s.part("M24,66 C34,74 52,76 68,74 C56,70 40,68 24,66 Z", "#c8b890", "#9a8a62", line="none")
        # 背上一座座金色岩山
        for x, h in ((34, 12), (44, 20), (56, 26), (68, 18), (78, 10)):
            s.part(poly((x - 7, 44), (x - 1, 44 - h), (x + 2, 44 - h + 5), (x + 7, 44)), *RK)
            s.flat(poly((x - 2, 44 - h + 2), (x - 1, 44 - h), (x + 1, 44 - h + 3)), "#ffffff")
    s.part(LEG(26, 66, 88, 12), *DK)
    s.part(ell(25, 89, 7, 2.4), *RK[:2])
    s.part(LEG(66, 64, 88, 13), *DK)
    s.part(ell(66, 89, 7, 2.4), *RK[:2])
    with s.group(f"translate(0 {5 - b * 1.2:.2f})"):
        # 岩石王冠
        s.part(poly((14, 26), (14, 12), (20, 18), (28, 6), (36, 18), (42, 12), (42, 26)), *RK)
        s.flat(ell(28, 18, 2, 2), RED, LINE, .7)
        s.part("M10,36 C10,26 18,22 28,22 C38,22 46,26 46,36 C46,48 38,54 28,54 C18,54 10,48 10,36 Z", *DK)
        s.part("M11,27 C18,22 38,22 45,27 L45,30 C38,27 32,29 28,31 C24,29 18,27 11,30 Z", "#33261e", "#1a120c")
        s.eye(20.5, 34, 3.2, 3.6, RED, a["blink"], lid=.5)
        s.eye(35.5, 34, 3.2, 3.6, RED, a["blink"], lid=.5)
        s.flat(ell(26, 44, .9, .7), LINE)
        s.flat(ell(30, 44, .9, .7), LINE)
        s.line("M20,48 Q28,51 36,48")
        for x in (21, 25, 31, 35):
            s.flat(poly((x - 1, 48.5), (x, 51), (x + 1, 48.8)), "#ffffff")
    return s


# ================================================================== 小铁偶线（钢/灵能）
ST = ("#c8ccdc", "#7e849c", "#ffffff")
STd = ("#9aa0b8", "#5a607a")
PK, PKs = "#f95587", "#b82a5a"


def gem(s, x, y, r, glow):
    s.flat(poly((x, y - r), (x + r * .8, y), (x, y + r), (x - r * .8, y)), PK if glow < .5 else "#ff9ab8", s.outline, .8)
    s.flat(ell(x - r * .2, y - r * .3, r * .2, r * .3), "#ffffff")


def d031(f):
    a = anim(f)
    LINE = "#1a1a2a"
    s = Sprite(LINE)
    s.lid_color = ST[1]
    sw = a["sway"]
    glow = (math.sin(a["ph"] * 2) + 1) / 2
    # 重心左右换脚
    lift_l, lift_r = max(0, sw) * 2, max(0, -sw) * 2
    s.part(poly((38, 76), (44, 76), (44, 88 - lift_l), (36, 88 - lift_l)), *STd)
    s.part(poly((52, 76), (58, 76), (60, 88 - lift_r), (52, 88 - lift_r)), *STd)
    with s.group(f"translate({sw * 1:.2f} 0)"):
        s.part("M34,62 C34,56 62,56 62,62 L60,78 C56,80 40,80 36,78 Z", *ST)
        gem(s, 48, 68, 4, glow)
        for side in (-1, 1):
            with s.group(rot(side * sw * 12, 48 + side * 14, 62)):
                s.part(f"M{48 + side * 13},60 L{48 + side * 19},62 L{48 + side * 20},72 L{48 + side * 15},72 Z", *STd)
                s.part(ell(48 + side * 17.5, 74, 3.5, 3), *ST[:2])
        # 大圆脑袋，两边螺栓
        s.part(ell(48, 42, 18, 16), *ST)
        for side in (-1, 1):
            s.part(ell(48 + side * 18, 42, 3, 3), *STd)
        s.line("M48,26 L48,20", ST[1], 1.6)
        s.flat(ell(48, 18, 2.6, 2.6), PK, LINE, .8)
        s.part("M34,40 C34,34 62,34 62,40 L62,48 C62,52 34,52 34,48 Z", "#2a3048", "#1a1e30", line="none")
        s.flat(ell(41, 43, 3, 3.4), "#ff9ab8" if not a["blink"] else "#2a3048")
        s.flat(ell(55, 43, 3, 3.4), "#ff9ab8" if not a["blink"] else "#2a3048")
        if not a["blink"]:
            s.flat(ell(40, 42, 1, 1.2), "#ffffff")
            s.flat(ell(54, 42, 1, 1.2), "#ffffff")
        s.line("M45,54 Q48,55.5 51,54")
    return s


def d032(f):
    a = anim(f)
    LINE = "#1a1a2a"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = ST[1]
    sw = a["sway"]
    glow = (math.sin(a["ph"] * 2) + 1) / 2
    lift_l, lift_r = max(0, sw) * 2, max(0, -sw) * 2
    s.part(poly((38, 66), (44, 66), (42, 88 - lift_l), (34, 88 - lift_l)), *STd)
    s.part(poly((52, 66), (58, 66), (62, 88 - lift_r), (54, 88 - lift_r)), *STd)
    with s.group(f"translate({sw:.2f} 0)"):
        # 刃臂
        for side in (-1, 1):
            with s.group(rot(side * (10 + sw * 8), 48 + side * 14, 40)):
                s.part(f"M{48 + side * 12},38 L{48 + side * 18},40 L{48 + side * 18},54 L{48 + side * 14},54 Z", *STd)
                s.part(f"M{48 + side * 14},54 L{48 + side * 20},54 L{48 + side * 24},76 L{48 + side * 17},66 Z", "#eef2ff", "#9aa4c8", "#ffffff")
        s.part("M34,40 C34,34 62,34 62,40 L58,66 C54,70 42,70 38,66 Z", *ST)
        # 胸口一面镜子
        s.flat(ell(48, 50, 8, 9), LINE)
        s.flat(ell(48, 50, 6.5, 7.5), "#d8f0ff")
        s.flat("M44,46 L50,44 L46,54 Z", "#ffffff")
        gem(s, 48, 62, 3, glow)
        # 头：尖顶头盔
        s.part("M36,24 C36,14 60,14 60,24 L58,32 C54,36 42,36 38,32 Z", *ST)
        s.part(poly((44, 16), (48, 4), (52, 16)), PK, PKs)
        s.part("M38,22 C42,20 54,20 58,22 L58,28 C54,26 42,26 38,28 Z", "#2a3048", "#1a1e30", line="none")
        s.eye(43, 24.5, 2.4, 2.6, PK, a["blink"], lid=.3)
        s.eye(53, 24.5, 2.4, 2.6, PK, a["blink"], lid=.3)
    return s


def d033(f):
    a = anim(f)
    LINE = "#1a1a2a"
    s = Sprite(LINE)
    s.fit = .86
    s.lid_color = ST[1]
    sw = a["sway"]
    glow = (math.sin(a["ph"] * 2) + 1) / 2
    # 身边绕着三颗粉色灵能球
    orbs = []
    for i in range(3):
        ang = a["ph"] + i * 2.1
        orbs.append((48 + math.cos(ang) * 40, 40 + math.sin(ang) * 8, math.sin(ang)))
    for x, y, z in orbs:
        if z < 0:
            s.flat(ell(x, y, 4, 4), "#ff9ab8", LINE, 1)
    lift_l, lift_r = max(0, sw) * 2, max(0, -sw) * 2
    s.part(poly((32, 68), (44, 68), (44, 88 - lift_l), (30, 88 - lift_l)), *STd)
    s.part(poly((52, 68), (64, 68), (66, 88 - lift_r), (52, 88 - lift_r)), *STd)
    s.part(poly((28, 84 - lift_l), (46, 84 - lift_l), (46, 90 - lift_l), (26, 90 - lift_l)), *ST[:2])
    s.part(poly((50, 84 - lift_r), (68, 84 - lift_r), (70, 90 - lift_r), (50, 90 - lift_r)), *ST[:2])
    with s.group(f"translate({sw:.2f} 0)"):
        for side in (-1, 1):
            with s.group(rot(side * sw * 8, 48 + side * 22, 38)):
                s.part(ell(48 + side * 22, 38, 8, 7), *ST)
                s.part(f"M{48 + side * 20},42 L{48 + side * 28},44 L{48 + side * 28},60 L{48 + side * 20},60 Z", *STd)
                s.part(ell(48 + side * 24, 64, 7, 6), *ST)
                for k in (-3, 0, 3):
                    s.line(f"M{48 + side * 24 + k},60 L{48 + side * 24 + k},68", ST[1], 1)
        s.part("M28,40 C28,32 68,32 68,40 L62,68 C58,72 38,72 34,68 Z", *ST)
        s.part(poly((34, 64), (62, 64), (62, 70), (34, 70)), PK, PKs)
        s.flat(ell(48, 50, 9, 9), LINE)
        s.flat(ell(48, 50, 7.5, 7.5), PK if glow < .5 else "#ff9ab8")
        s.flat(star(48, 50, 5, 2.2), "#ffffff")
        # 头和王冠
        s.part("M36,22 C36,12 60,12 60,22 L58,32 C54,36 42,36 38,32 Z", *ST)
        s.part(poly((36, 14), (36, 2), (42, 8), (48, -2), (54, 8), (60, 2), (60, 14)), "#ffd24a", "#c08a1a", "#fff4b0")
        s.flat(ell(48, 7, 1.8, 1.8), PK, LINE, .7)
        s.part("M38,20 C42,18 54,18 58,20 L58,28 C54,26 42,26 38,28 Z", "#2a3048", "#1a1e30", line="none")
        s.eye(43, 23.5, 2.6, 3, PK, a["blink"], lid=.35)
        s.eye(53, 23.5, 2.6, 3, PK, a["blink"], lid=.35)
    for x, y, z in orbs:
        if z >= 0:
            s.flat(ell(x, y, 4.5, 4.5), "#ff9ab8", LINE, 1)
            s.flat(ell(x - 1.3, y - 1.3, 1.3, 1.3), "#ffffff")
    return s


# ================================================================== 幼蛇线（龙/水）
SN = ("#5a6ae8", "#2e3aa8", "#9aa8ff")
SNb = ("#c8e8ff", "#88b8e0")
FIN = ("#5ad0e8", "#2a90b0")


def coil(s, cx, cy, rings, C, belly):
    """盘起来的蛇身：从下往上一圈比一圈小"""
    for i, (rx, ry) in enumerate(rings):
        y = cy - i * ry * 1.1
        s.part(ell(cx, y, rx, ry), *C)
        s.part(f"M{cx - rx * .7},{y + ry * .3} Q{cx},{y + ry * 1.05} {cx + rx * .7},{y + ry * .3} Q{cx},{y + ry * .6} {cx - rx * .7},{y + ry * .3} Z", belly[0], belly[1], line="none")


def tongue(s, a, x, y):
    if a["f"] % 12 in (4, 5, 6):
        s.line(f"M{x},{y} L{x},{y + 4} L{x - 1.5},{y + 6} M{x},{y + 4} L{x + 1.5},{y + 6}", "#e83a5a", 1)


def d034(f):
    a = anim(f)
    LINE = "#141a3a"
    s = Sprite(LINE)
    s.lid_color = SN[1]
    sw = a["sway"]
    coil(s, 48, 82, [(22, 7), (17, 6)], SN, SNb)
    with s.group(rot(-12, 66, 84)):
        s.part("M64,84 C72,82 78,78 82,72 C82,80 76,86 66,88 Z", *SN)
    # 脖子 S 形摆动
    nx = 48 + sw * 4
    s.line(f"M48,72 C{48 - 8 + sw * 4},62 {nx + 8},52 {nx},44", LINE, 14)
    s.line(f"M48,72 C{48 - 8 + sw * 4},62 {nx + 8},52 {nx},44", SN[0], 12)
    s.line(f"M48,72 C{48 - 8 + sw * 4},62 {nx + 8},52 {nx},44", SNb[0], 5)
    with s.group(f"translate({sw * 4:.2f} 0)"):
        s.part("M44,30 C46,22 50,22 52,30 L48,32 Z", *FIN)
        for side in (-1, 1):
            s.part(f"M{48 + side * 10},38 L{48 + side * 17},32 L{48 + side * 15},42 Z", *FIN)
        s.part(ell(48, 40, 12, 10), *SN)
        s.part(ell(48, 45, 7, 4), SNb[0], SNb[1], line="none")
        s.eye(43, 38, 3.2, 3.8, "#2a90b0", a["blink"])
        s.eye(53, 38, 3.2, 3.8, "#2a90b0", a["blink"])
        s.line("M45.5,46 Q48,47 50.5,46")
        tongue(s, a, 48, 47)
    return s


def d035(f):
    a = anim(f)
    LINE = "#141a3a"
    s = Sprite(LINE)
    s.fit = .94
    s.lid_color = SN[1]
    sw = a["sway"]
    coil(s, 50, 82, [(26, 7), (22, 6.5), (17, 6)], SN, SNb)
    with s.group(rot(-15, 72, 84)):
        s.part("M70,84 C80,82 86,76 90,68 C92,78 84,86 72,88 Z", *SN)
        s.part(poly((88, 70), (94, 64), (92, 74)), *FIN)
    nx = 48 + sw * 5
    path = f"M50,66 C{40 + sw * 4},56 {nx + 10},42 {nx},30"
    # 身侧一对鳍翼
    for side in (-1, 1):
        with s.group(rot(side * (a["flap"] * 6), 48 + side * 6, 52)):
            s.part(f"M{48 + side * 6},52 C{48 + side * 20},40 {48 + side * 30},42 {48 + side * 34},48 C{48 + side * 26},50 {48 + side * 20},56 {48 + side * 8},58 Z", *FIN)
            s.line(f"M{48 + side * 10},54 L{48 + side * 28},46", FIN[1], 1)
    s.line(path, LINE, 15)
    s.line(path, SN[0], 13)
    s.line(path, SNb[0], 5)
    with s.group(f"translate({sw * 5:.2f} 0)"):
        s.part("M42,16 C44,6 52,6 54,16 L48,20 Z", *FIN)
        for side in (-1, 1):
            s.part(f"M{48 + side * 10},24 L{48 + side * 20},16 L{48 + side * 17},28 Z", *FIN)
        s.part(ell(48, 26, 12, 10), *SN)
        s.part(ell(48, 31, 7, 4), SNb[0], SNb[1], line="none")
        s.eye(43, 24, 3, 3.6, "#2a90b0", a["blink"], lid=.2)
        s.eye(53, 24, 3, 3.6, "#2a90b0", a["blink"], lid=.2)
        s.line("M45.5,32 Q48,33 50.5,32")
        tongue(s, a, 48, 33)
    return s


def d036(f):
    a = anim(f)
    LINE = "#141a3a"
    s = Sprite(LINE)
    s.fit = .86
    s.lid_color = SN[1]
    sw = a["sway"]
    coil(s, 50, 84, [(30, 7), (26, 7), (22, 6.5), (18, 6)], SN, SNb)
    with s.group(rot(-15, 76, 86)):
        s.part("M74,86 C86,84 92,76 94,66 C98,78 90,88 76,90 Z", *SN)
        s.part(poly((92, 66), (98, 58), (98, 70)), *FIN)
    nx = 48 + sw * 5
    path = f"M50,62 C{38 + sw * 4},50 {nx + 12},36 {nx},24"
    # 背鳍沿脖子一路排下来
    for t in (.25, .5, .75):
        x = 50 + (nx - 50) * t + math.sin(t * math.pi) * 8
        y = 62 - 38 * t
        s.part(poly((x + 4, y), (x + 12, y - 4), (x + 6, y + 4)), *FIN)
    s.line(path, LINE, 17)
    s.line(path, SN[0], 15)
    s.line(path, SNb[0], 6)
    with s.group(f"translate({sw * 5:.2f} 0)"):
        for side in (-1, 1):
            s.part(f"M{48 + side * 12},20 L{48 + side * 26},12 L{48 + side * 22},26 Z", *FIN)
            s.line(f"M{48 + side * 4},28 C{48 + side * 12},34 {48 + side * 14},40 {48 + side * 18 + sw * 2},44", FIN[0], 1.4)
        dragon_head(s, a, 48, 20, 13, SN, ("#f4ecd8", "#b8a888"), lid=.35, iris="#2a90b0", belly=SNb, horn_len=1.2)
        tongue(s, a, 48, 31)
    return s


# ================================================================== 雪龙线（冰/龙）
IC = ("#b8ecf0", "#6ab0c0", "#ffffff")
ID = ("#7a62d8", "#4a3aa0")
CRY = ("#e8fcff", "#8ad0e8")


def icicles(s, xs, y, h):
    for i, x in enumerate(xs):
        hh = h * (.7 + .3 * (i % 2))
        s.part(poly((x - 3, y), (x, y - hh), (x + 3, y)), *CRY)


def frost(s, a, x, y):
    t = (a["f"] % 12) / 12
    s.flat(ell(x - t * 3, y - t * 6, 1.4 + t * 1.6, 1.4 + t * 1.6), "#ffffff" if t < .5 else "#d8f4ff")


def d037(f):
    a = anim(f)
    LINE = "#142a3a"
    s = Sprite(LINE)
    s.lid_color = IC[1]
    b = a["breath"]
    with s.group(rot(max(0, math.sin(a["ph"] * 2)) * -10, 62, 82)):
        s.part("M60,80 C70,78 80,82 86,76 C86,84 76,90 62,88 Z", *IC)
        s.part(poly((84, 78), (92, 70), (90, 80)), *CRY)
    with s.group(scale_about(1 + .02 * b, 1 + .03 * b, 48, 89)):
        s.part(ell(48, 76, 17, 13), *IC)
        s.part(ell(48, 79, 10, 9), ID[0], ID[1], line="none")
        for y in (75, 80, 85):
            s.line(f"M42,{y} L54,{y}", ID[1], 1)
        icicles(s, (36, 42, 54, 60), 66, 7)
        s.part(ell(35, 88, 6, 2.8), *IC[:2])
        s.part(ell(61, 88, 6, 2.8), *IC[:2])
    with s.group(f"translate(0 {-b * 1.3:.2f})"):
        dragon_head(s, a, 48, 50, 16, IC, ID, iris="#4a3aa0", belly=(ID[0], ID[1]), horn_len=.4)
        icicles(s, (44, 48, 52), 36, 6)
    frost(s, a, 44, 54)
    return s


def d038(f):
    a = anim(f)
    LINE = "#142a3a"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = IC[1]
    b = a["breath"]
    with s.group(rot(max(0, math.sin(a["ph"] * 2)) * -8, 72, 66)):
        s.part("M70,64 C82,62 90,70 94,82 C86,82 78,78 70,72 Z", *IC)
        s.part(poly((90, 76), (98, 70), (96, 84)), *CRY)
    s.part(LEG(34, 64, 89, 8), IC[1], "#3a7a8a")
    s.part(HIND(70, 60, 89), IC[1], "#3a7a8a")
    with s.group(f"translate(0 {-b * .7:.2f})"):
        s.part("M24,58 C26,46 42,42 58,44 C72,45 80,52 80,62 C80,70 72,74 56,74 C40,74 24,70 24,58 Z", *IC)
        s.part("M28,64 C34,72 48,75 60,73 C50,68 38,66 28,64 Z", ID[0], ID[1], line="none")
        icicles(s, (42, 50, 58, 66, 74), 47, 10)
    s.part(LEG(29, 60, 88, 9), *IC)
    s.part(ell(28, 89, 5, 2.2), *ID)
    s.part(HIND(65, 56, 88), *IC)
    s.part(ell(66, 89, 5, 2.2), *ID)
    with s.group(f"translate(0 {-b * 1.3:.2f})"):
        s.part("M26,54 C22,46 24,38 26,32 L34,32 C33,38 34,46 38,52 Z", *IC)
        dragon_head(s, a, 28, 26, 13, IC, ID, lid=.25, iris="#4a3aa0", belly=(ID[0], ID[1]))
        icicles(s, (24, 28, 32), 14, 6)
    frost(s, a, 25, 28)
    return s


def d039(f):
    a = anim(f)
    LINE = "#142a3a"
    s = Sprite(LINE)
    s.fit = .86
    s.lid_color = IC[1]
    b = a["breath"]
    fl = a["flap"]
    # 冰晶翅膀：一片片尖晶体
    for side in (-1, 1):
        with s.group(rot(side * (-6 + fl * 6), 48 + side * 8, 44)):
            x0 = 48 + side * 8
            s.part(poly((x0, 44), (x0 + side * 20, 10), (x0 + side * 26, 22), (x0 + side * 40, 14), (x0 + side * 34, 32), (x0 + side * 42, 36), (x0 + side * 24, 48)), *CRY)
            s.line(f"M{x0},44 L{x0 + side * 20},10 M{x0 + side * 4},44 L{x0 + side * 40},14 M{x0 + side * 8},46 L{x0 + side * 42},36", CRY[1], 1)
    with s.group(rot(a["sway"] * 5, 58, 78)):
        s.part("M56,74 C70,74 82,80 90,88 C78,90 66,88 54,84 Z", *IC)
        s.part(poly((86, 84), (96, 80), (92, 90)), *CRY)
    s.part("M36,72 C30,76 30,84 32,89 L42,89 C42,84 44,80 46,76 Z", *IC)
    s.part("M60,72 C66,76 66,84 64,89 L54,89 C54,84 52,80 50,76 Z", *IC)
    s.part(ell(36, 89, 6.5, 2.4), *ID)
    s.part(ell(60, 89, 6.5, 2.4), *ID)
    with s.group(f"translate(0 {-b * .8:.2f})"):
        s.part("M32,52 C30,40 38,34 48,34 C58,34 66,40 64,52 C64,66 60,78 48,78 C36,78 32,66 32,52 Z", *IC)
        s.part("M38,54 C38,44 58,44 58,54 C58,68 54,76 48,76 C42,76 38,68 38,54 Z", ID[0], ID[1], line="none")
        for y in (52, 58, 64, 70):
            s.line(f"M41,{y} L55,{y}", ID[1], 1)
        for side in (-1, 1):
            s.part(f"M{48 + side * 14},44 C{48 + side * 20},48 {48 + side * 22},56 {48 + side * 20},62 L{48 + side * 15},60 C{48 + side * 16},56 {48 + side * 14},52 {48 + side * 10},50 Z", *IC)
    with s.group(f"translate(0 {-b * 1.3:.2f})"):
        dragon_head(s, a, 48, 22, 14, IC, CRY, lid=.45, iris="#4a3aa0", belly=(ID[0], ID[1]), horn_len=1.4)
        s.flat(poly((48, 8), (50.5, 12), (48, 16), (45.5, 12)), ID[0], LINE, .8)
    frost(s, a, 46, 24)
    return s


SPECIES = {"d025": d025, "d026": d026, "d027": d027, "d028": d028, "d029": d029, "d030": d030,
           "d031": d031, "d032": d032, "d033": d033, "d034": d034, "d035": d035, "d036": d036,
           "d037": d037, "d038": d038, "d039": d039}
