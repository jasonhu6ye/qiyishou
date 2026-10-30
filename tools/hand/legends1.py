"""传说幻兽 #040-#047"""
import math

from kit import Sprite, anim, ell, poly, rot, scale_about
from fox import HIND, LEG
from mouse import leaf

FIRE = ("#ff5a1a", "#ffa02a", "#ffe066")


def flame(s, x, y, h, flick, lean=0.0, cols=FIRE, line=None):
    k = 1 + .1 * flick
    c1, c2, c3 = cols
    with s.group(f"{rot(lean, x, y)} {scale_about(1, k, x, y)}"):
        w = h * .5
        s.part(f"M{x - w},{y} C{x - w * 1.3},{y - h * .5} {x - w * .4},{y - h * .6} {x - w * .2},{y - h} "
               f"C{x + w * .2},{y - h * .65} {x + w * .7},{y - h * .75} {x + w * .75},{y - h * .4} C{x + w * 1.1},{y - h * .1} {x + w * .6},{y + 1} {x},{y + 1} Z",
               c2, c1, line=line)
        s.flat(f"M{x - w * .45},{y - 1} C{x - w * .6},{y - h * .35} {x - w * .1},{y - h * .45} {x - w * .05},{y - h * .7} "
               f"C{x + w * .25},{y - h * .4} {x + w * .45},{y - h * .3} {x + w * .35},{y - 1} Z", c3)


def face(s, cx, cy, gap, rx, ry, iris, a, lid=.3, muzzle=None, nose=None, mouth=True, line=None):
    """对称的正脸：两眼以 cx 为中线，鼻子嘴在正下方"""
    if muzzle:
        s.part(ell(cx, cy + ry * 2.2, *muzzle[:2]), muzzle[2], muzzle[3], line="none")
    if nose:
        s.flat(ell(cx, cy + ry * 1.7, 2.2, 1.6), nose)
    s.eye(cx - gap, cy, rx, ry, iris, a["blink"], lid=lid)
    s.eye(cx + gap, cy, rx, ry, iris, a["blink"], lid=lid)
    if mouth:
        my = cy + ry * (2.6 if muzzle else 2.0)
        s.line(f"M{cx - 3},{my} Q{cx},{my + 2.2} {cx + 3},{my}", line)


# ------------------------------------------------------------------ 040 森灵守护·苍古（草/妖精）：树角鹿神
def d040(f):
    a = anim(f)
    LINE = "#1e2a18"
    s = Sprite(LINE)
    s.fit = .84
    G, Gs, Gh = "#e8f0dc", "#a8bc9a", "#ffffff"   # 白鹿
    M, Ms = "#5fae4a", "#2f7a34"                    # 青苔
    BR, BRs = "#8a5a32", "#5a3618"
    P, Ps = "#ff9ac8", "#d0609a"
    s.lid_color = Gs
    b = a["breath"]
    # 远侧腿
    s.part(LEG(30, 60, 90, 5), Gs, "#7e9070")
    s.part(HIND(70, 56, 90), Gs, "#7e9070")
    with s.group(f"translate(0 {-b * .7:.2f})"):
        # 身体
        s.part("M22,54 C24,42 40,38 56,40 C70,41 80,48 80,58 C80,66 72,70 56,70 C40,70 22,66 22,54 Z", G, Gs, Gh)
        # 背上的青苔披毛，开着小花
        s.part("M26,48 C34,38 58,36 76,46 C72,52 66,50 62,54 C58,48 50,50 46,54 C42,48 34,50 30,54 C28,52 26,50 26,48 Z", M, Ms, "#9ae07a")
        for x, y in ((40, 44), (56, 42), (68, 47)):
            for k in range(5):
                ang = k * 72
                px, py = x + math.sin(math.radians(ang)) * 1.8, y - math.cos(math.radians(ang)) * 1.8
                s.flat(ell(px, py, 1.3, 1.3), P)
            s.flat(ell(x, y, 1, 1), "#ffe066")
        # 尾巴：一簇叶子
        with s.group(rot(a["sway"] * 6, 80, 52)):
            leaf(s, 80, 54, 14, 6, 60, M, Ms)
            leaf(s, 80, 54, 12, 5, 95, "#7cc85a", Ms)
    s.part(LEG(26, 56, 89, 6), G, Gs, Gh)
    s.part(ell(25.5, 89.5, 3.5, 1.8), BR, BRs)
    s.part(HIND(66, 52, 89), G, Gs, Gh)
    s.part(ell(68, 89.5, 3.5, 1.8), BR, BRs)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        # 树枝鹿角（两侧对称，开花、挂叶）
        for side in (-1, 1):
            x0 = 28 + side * 8
            with s.group(rot(a["sway"] * 2 * side, x0, 22)):
                s.line(f"M{x0},22 C{x0 + side * 4},12 {x0 + side * 12},8 {x0 + side * 16},-4", BRs, 4)
                s.line(f"M{x0},22 C{x0 + side * 4},12 {x0 + side * 12},8 {x0 + side * 16},-4", BR, 2)
                s.line(f"M{x0 + side * 6},12 C{x0 + side * 4},6 {x0 + side * 4},2 {x0 + side * 2},-4", BRs, 3)
                s.line(f"M{x0 + side * 11},7 C{x0 + side * 16},6 {x0 + side * 20},4 {x0 + side * 22},2", BRs, 3)
                leaf(s, x0 + side * 16, -3, 8, 3.5, side * 40, M, Ms)
                leaf(s, x0 + side * 22, 2, 7, 3, side * 80, "#7cc85a", Ms)
                s.flat(ell(x0 + side * 2, -3, 2.2, 2.2), P, LINE, .8)
                s.flat(ell(x0 + side * 2, -3, .9, .9), "#ffe066")
        # 耳朵（叶形）
        leaf(s, 16, 30, 11, 4.5, -70, G, Gs, False)
        leaf(s, 40, 30, 11, 4.5, 70, G, Gs, False)
        # 头和长脸
        s.part("M16,30 C16,20 22,16 28,16 C34,16 40,20 40,30 C40,40 34,48 28,48 C22,48 16,40 16,30 Z", G, Gs, Gh)
        s.part(ell(28, 42, 6, 5), "#ffffff", "#d8e4cc", line="none")
        s.flat(ell(28, 40.5, 2.2, 1.6), "#4a3a3a")
        # 额前绿宝石
        s.flat(poly((28, 20), (31, 24), (28, 28), (25, 24)), "#3fd08a", LINE)
        s.flat(ell(27.2, 23, .8, 1.2), "#c8ffe0")
        s.eye(22.5, 31, 3.2, 3.8, "#2f9a5a", a["blink"], lid=.15)
        s.eye(33.5, 31, 3.2, 3.8, "#2f9a5a", a["blink"], lid=.15)
        s.line("M25.5,45 Q28,46.5 30.5,45")
        # 脖子上的青苔领
        s.part("M18,46 C22,54 34,54 38,46 C36,52 32,50 28,54 C24,50 20,52 18,46 Z", M, Ms)
    return s


# ------------------------------------------------------------------ 041 炎帝·焚天（火/龙）：火鬃龙角狮王
def d041(f):
    a = anim(f)
    LINE = "#2a0e08"
    s = Sprite(LINE)
    s.fit = .86
    R, Rs, Rh = "#d8402a", "#962414", "#ff7a50"
    GOLD, GOLDs = "#ffcf4a", "#d08a1a"
    HORN, HORNs = "#3a2a30", "#1a1218"
    s.lid_color = Rs
    b = a["breath"]
    # 尾巴：末端一团大火
    with s.group(rot(a["sway"] * 8, 78, 56)):
        s.line("M76,58 C88,56 92,44 88,32", Rs, 4)
        s.line("M76,58 C88,56 92,44 88,32", R, 2)
        flame(s, 88, 36, 16, a["flick"], 10)
    s.part(LEG(34, 62, 90, 7), Rs, "#6e1a0e")
    s.part(HIND(72, 58, 90), Rs, "#6e1a0e")
    with s.group(f"translate(0 {-b * .7:.2f})"):
        s.part("M26,56 C28,44 44,40 60,42 C74,43 82,50 82,60 C82,68 74,72 58,72 C42,72 26,68 26,56 Z", R, Rs, Rh)
        s.part("M30,62 C36,70 50,73 62,71 C52,67 40,65 30,62 Z", GOLD, GOLDs, line="none")
        # 背上一排金色龙鳞
        for x in (46, 54, 62, 70):
            s.part(poly((x - 3, 44), (x, 37), (x + 3, 44)), GOLD, GOLDs)
    s.part(LEG(30, 58, 89, 8), R, Rs, Rh)
    s.part(ell(29, 89.5, 5, 2.2), GOLD, GOLDs)
    s.part(HIND(68, 54, 89), R, Rs, Rh)
    s.part(ell(70, 89.5, 5, 2.2), GOLD, GOLDs)
    with s.group(f"translate(0 {-b * 1.3:.2f})"):
        # 火焰鬃毛，一圈火舌
        for i in range(9):
            ang = -150 + i * 37.5
            x = 30 + math.sin(math.radians(ang)) * 17
            y = 36 - math.cos(math.radians(ang)) * 17
            flame(s, x, y + 4, 14, a["flick"] * (1 if i % 2 else -1), ang * .9)
        s.part(ell(30, 36, 17, 16), "#ff8a2a", "#e0501a")
        # 龙角
        for side in (-1, 1):
            s.part(f"M{30 + side * 7},24 C{30 + side * 12},16 {30 + side * 18},10 {30 + side * 22},2 C{30 + side * 18},12 {30 + side * 14},20 {30 + side * 12},28 Z", HORN, HORNs)
        s.part("M17,34 C17,24 23,20 30,20 C37,20 43,24 43,34 C43,44 37,50 30,50 C23,50 17,44 17,34 Z", R, Rs, Rh)
        s.part(ell(30, 43, 7.5, 5.5), GOLD, GOLDs, line="none")
        s.flat(ell(30, 40, 2.6, 1.8), LINE)
        s.eye(24, 33, 3.2, 3.6, "#ffcf4a", a["blink"], lid=.4)
        s.eye(36, 33, 3.2, 3.6, "#ffcf4a", a["blink"], lid=.4)
        s.line("M26,46 Q30,48.5 34,46")
        s.flat("M27,46.5 L28,49 L29,47 Z", "#ffffff")
        s.flat("M31,47 L32,49 L33,46.5 Z", "#ffffff")
    return s


# ------------------------------------------------------------------ 042 风神·凌霄（飞行/电）：雷羽巨鹏
def d042(f):
    a = anim(f)
    LINE = "#141a34"
    s = Sprite(LINE)
    s.fit = .84
    B, Bs, Bh = "#4a6ad8", "#2a3c90", "#8aa8ff"
    W, Ws = "#f2f4ff", "#b8c0e0"
    Y, Ys = "#ffe04a", "#d09a1a"
    s.lid_color = Bs
    b = a["breath"]
    fl = a["flap"]
    # 远侧翅膀
    with s.group(rot(-fl * 8 - 10, 52, 44)):
        s.part("M52,44 C60,26 74,12 92,6 C88,14 90,20 86,24 C90,26 88,32 82,34 C84,38 80,42 74,42 Z", Bs, "#1a2460")
    # 闪电尾羽
    with s.group(rot(a["sway"] * 5, 62, 66)):
        for i, ang in enumerate((-20, 5, 30)):
            with s.group(rot(ang, 62, 66)):
                s.part(poly((60, 66), (68, 72), (64, 76), (74, 86), (66, 80), (68, 84), (58, 72)), Y, Ys)
    # 爪
    for x in (40, 52):
        s.line(f"M{x},74 L{x},88", "#e0a020", 2.4)
        s.flat(poly((x - 4, 89), (x, 86), (x + 3, 89)), "#e0a020", LINE)
    with s.group(f"translate(0 {-b * 1:.2f})"):
        s.part("M28,52 C26,38 38,30 52,32 C66,34 72,46 70,58 C68,70 58,76 46,76 C34,76 30,66 28,52 Z", B, Bs, Bh)
        s.part("M34,58 C36,48 50,46 58,54 C60,66 54,72 46,72 C38,72 34,66 34,58 Z", W, Ws, line="none")
        s.flat(poly((44, 56), (48, 60), (45, 62), (50, 68), (43, 62), (46, 61)), Y, LINE, .8)
    # 近侧翅膀
    with s.group(rot(fl * 10, 46, 44)):
        s.part("M46,44 C38,26 24,12 4,6 C8,14 4,20 10,24 C4,26 8,32 12,34 C8,38 14,42 20,44 C24,50 34,52 40,52 Z", B, Bs, Bh)
        for x, y in ((12, 26), (16, 34), (22, 42)):
            s.line(f"M{x},{y} L{x + 14},{y + 6}", Bs, 1)
        s.part("M4,6 C8,14 4,20 10,24 C4,26 8,32 12,34 C8,30 6,26 6,22 C4,18 6,12 4,6 Z", Y, Ys, line="none")
    with s.group(f"translate(0 {-b * 1.4:.2f})"):
        # 冠羽，像闪电
        with s.group(rot(a["sway"] * 4, 48, 20)):
            s.part(poly((44, 20), (40, 4), (48, 12), (50, -2), (54, 12), (62, 6), (56, 20)), Y, Ys)
        s.part(ell(48, 26, 11, 10), B, Bs, Bh)
        s.part(ell(48, 30, 7, 5), W, Ws, line="none")
        s.part(poly((44, 30), (52, 30), (48, 37)), Y, Ys)
        s.eye(43, 25, 2.8, 3.3, "#ffe04a", a["blink"], lid=.45)
        s.eye(53, 25, 2.8, 3.3, "#ffe04a", a["blink"], lid=.45)
    return s


# ------------------------------------------------------------------ 043 镜湖之主·澈（水/灵能）：抱着镜珠的蛟
def d043(f):
    a = anim(f)
    LINE = "#10243a"
    s = Sprite(LINE)
    s.fit = .9
    B, Bs, Bh = "#7ad0f0", "#3a8ab8", "#c8f2ff"
    W, Ws = "#f4fcff", "#b8dcec"
    P, Ps = "#d890ff", "#9a50c8"
    s.lid_color = Bs
    sw = a["sway"]
    # 身体盘成 S 形，从后往前一节一节画
    pts = []
    for i in range(16):
        t = i / 15   # 0 尾尖（右下）→ 1 脖子（左上）
        pts.append((60 - t * 28 + math.sin(t * 7 + .6 + a["ph"] * .5) * 16, 86 - t * 52))
    tx, ty = pts[0]
    with s.group(rot(sw * 10, tx, ty)):
        s.part(f"M{tx},{ty} C{tx + 8},{ty - 8} {tx + 14},{ty - 4} {tx + 16},{ty - 10} C{tx + 16},{ty} {tx + 10},{ty + 6} {tx},{ty + 4} Z", P, Ps)
    wid = [4 + 6 * i / 15 for i in range(16)]
    for i in range(2, 16, 3):   # 背鳍
        x2, y2 = pts[i]
        s.part(poly((x2 - 2, y2 - wid[i] + 1), (x2 + 3, y2 - wid[i] - 5), (x2 + 4, y2 - wid[i] + 2)), P, Ps)
    segs = list(zip(pts, pts[1:]))
    for k, ((x1, y1), (x2, y2)) in enumerate(segs):
        s.line(f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}", LINE, wid[k + 1] * 2 + 2)
    for k, ((x1, y1), (x2, y2)) in enumerate(segs):
        s.line(f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}", B, wid[k + 1] * 2)
    for k, ((x1, y1), (x2, y2)) in enumerate(segs):
        w = wid[k + 1]
        s.line(f"M{x1:.1f},{y1 + w * .45:.1f} L{x2:.1f},{y2 + w * .45:.1f}", W, w * .8)
    # 镜珠（浮在身前，缓慢旋转的光）
    my = 66 + math.sin(a["ph"]) * 2
    s.flat(ell(30, my, 10, 10), "#e8f8ff", LINE, 1)
    s.flat(ell(30, my, 7.5, 7.5), "#b8e8ff")
    s.flat(ell(27, my - 3, 3, 2.4), "#ffffff")
    ang = a["ph"]
    s.flat(ell(30 + math.cos(ang) * 5, my + math.sin(ang) * 5, 1.2, 1.2), P)
    hx, hy = pts[-1]
    hx -= 2
    hy -= 6
    with s.group(f"translate(0 {-a['breath'] * 1.2:.2f})"):
        # 鳍状耳和须
        for side in (-1, 1):
            s.part(f"M{hx + side * 8},{hy - 2} C{hx + side * 18},{hy - 10} {hx + side * 20},{hy - 2} {hx + side * 22},{hy + 4} C{hx + side * 16},{hy + 2} {hx + side * 12},{hy + 4} {hx + side * 8},{hy + 4} Z", P, Ps)
            s.line(f"M{hx + side * 4},{hy + 10} C{hx + side * 10},{hy + 16} {hx + side * 8},{hy + 22} {hx + side * 14 + sw * 2},{hy + 26}", P, 1.4)
        s.part(f"M{hx - 2},{hy - 10} L{hx},{hy - 22} L{hx + 3},{hy - 10} Z", W, Ws)
        s.part(ell(hx, hy, 10, 10), B, Bs, Bh)
        s.part(ell(hx, hy + 6, 6.5, 4.5), W, Ws, line="none")
        s.flat(ell(hx, hy - 6, 2, 2), P, LINE, .8)
        s.eye(hx - 4.5, hy, 2.8, 3.3, "#9a50c8", a["blink"], lid=.2)
        s.eye(hx + 4.5, hy, 2.8, 3.3, "#9a50c8", a["blink"], lid=.2)
        s.line(f"M{hx - 2.5},{hy + 7} Q{hx},{hy + 8.5} {hx + 2.5},{hy + 7}")
    return s


# ------------------------------------------------------------------ 044 沼王·墨渊（毒/幽灵）：从毒沼里探出身子的鳄王
def d044(f):
    a = anim(f)
    LINE = "#1a0e24"
    s = Sprite(LINE)
    s.fit = .92
    P, Ps, Ph = "#6a4a9a", "#3e2864", "#9a7ad0"
    SL, SLs = "#9adf5a", "#5a9a2a"   # 毒沼
    B, Bs = "#d8c8f0", "#9a88b8"
    s.lid_color = Ps
    b = a["breath"]
    # 漂浮的鬼火
    for i in range(3):
        ang = a["ph"] + i * 2.1
        x, y = 48 + math.cos(ang) * 36, 30 + math.sin(ang) * 8
        flame(s, x, y + 4, 9, a["flick"], 0, ("#7a3ad0", "#b07aff", "#e8d8ff"))
    with s.group(f"translate(0 {-b * 1.5:.2f})"):
        # 身体从沼里探出来
        s.part("M20,80 C18,58 28,40 48,38 C68,36 80,52 78,80 Z", P, Ps, Ph)
        s.part("M32,80 C32,64 40,56 50,56 C60,56 66,64 66,80 Z", B, Bs, line="none")
        for y in (64, 70, 76):
            s.line(f"M38,{y} L62,{y}", Bs, 1)
        # 背上骨刺
        for x, y in ((26, 52), (32, 44), (40, 38)):
            s.part(poly((x - 3, y + 2), (x - 4, y - 7), (x + 3, y)), "#e8e0f0", "#a89ab8")
        # 粗短手臂
        s.part("M22,58 C14,60 12,68 14,74 L20,74 C20,68 22,64 28,62 Z", P, Ps, Ph)
        s.part("M74,58 C82,60 84,68 82,74 L76,74 C76,68 74,64 68,62 Z", P, Ps, Ph)
        # 鳄鱼头：长吻，上下颌
        s.part("M28,28 C28,16 38,10 50,10 C62,10 70,16 70,28 C70,36 64,40 50,40 C36,40 28,36 28,28 Z", P, Ps, Ph)
        s.part("M34,32 C34,40 40,48 50,48 C60,48 66,40 66,32 C60,36 40,36 34,32 Z", P, Ps)
        s.line("M34,32 Q50,38 66,32")
        for x in (38, 44, 50, 56, 62):
            s.flat(poly((x - 1.5, 33.5), (x, 37.5), (x + 1.5, 33.5)), "#ffffff")
        s.flat(ell(46, 44, 1.2, .9), LINE)
        s.flat(ell(54, 44, 1.2, .9), LINE)
        for x in (38, 62):
            s.part(ell(x, 16, 6, 5.5), P, Ps, Ph)
        s.eye(38, 15.5, 3.2, 3.6, "#c8ff5a", a["blink"], lid=.4)
        s.eye(62, 15.5, 3.2, 3.6, "#c8ff5a", a["blink"], lid=.4)
    # 毒沼表面，冒泡
    s.part("M6,82 C14,76 26,80 36,78 C48,76 58,80 70,78 C80,76 88,80 92,84 C90,90 10,90 6,82 Z", SL, SLs, "#d0ff9a")
    for i in range(3):
        t = (a["f"] / 24 + i / 3) % 1
        s.flat(ell(20 + i * 28, 80 - t * 6, 1.5 + t * 1.5, 1.5 + t * 1.5), "#d0ff9a", LINE, .8)
    return s


# ------------------------------------------------------------------ 045 沙之古王·塔鲁（大地/钢）：金甲巨蝎
def d045(f):
    a = anim(f)
    LINE = "#2a1a08"
    s = Sprite(LINE)
    s.fit = 1.0
    S_, Ss, Sh = "#d8a850", "#9a6a28", "#ffe0a0"
    G, Gs = "#ffd24a", "#c08a1a"
    D, Ds = "#5a4a3a", "#2e241a"
    s.lid_color = Ss
    sw = a["sway"]
    # 尾巴：一节节弯过头顶，毒针
    segs = []
    x, y = 66, 70
    for i in range(6):
        ang = math.radians(8 - i * 30 + sw * 5)
        x2, y2 = x + math.sin(ang) * 10, y - math.cos(ang) * 10
        segs.append((x2, y2, 7 - i * .5))
        x, y = x2, y2
    for x2, y2, r in segs:
        s.part(ell(x2, y2, r, r * .9), S_, Ss, Sh)
        s.part(f"M{x2 - r * .7},{y2 - r * .5} Q{x2},{y2 - r * 1.1} {x2 + r * .7},{y2 - r * .5}", G, Gs, line=LINE)
    s.part(f"M{x - 4},{y} C{x - 8},{y + 8} {x - 14},{y + 12} {x - 20},{y + 10} C{x - 12},{y + 8} {x - 8},{y + 4} {x - 6},{y - 4} Z", G, Gs, "#fff4b0")
    # 腿
    for i, x0 in enumerate((34, 44, 54, 64)):
        dy = math.sin(a["ph"] * 2 + i) * 1
        s.line(f"M{x0},74 L{x0 + 6},{80 + dy} L{x0 + 8},89", Ds, 3)
        s.line(f"M{x0},74 L{x0 + 6},{80 + dy} L{x0 + 8},89", D, 1.6)
    with s.group(f"translate(0 {-a['breath'] * .8:.2f})"):
        s.part("M24,70 C24,58 40,54 56,56 C70,58 76,64 74,72 C72,80 60,82 46,82 C32,82 24,78 24,70 Z", S_, Ss, Sh)
        for x in (36, 46, 56, 66):
            s.part(f"M{x - 5},60 Q{x},55 {x + 5},60 L{x + 5},64 Q{x},60 {x - 5},64 Z", G, Gs, line=LINE)
        # 钳子
        for side, (cx, cy) in ((-1, (10, 56)), (1, (34, 50))):
            op = 6 + sw * side * 3
            s.line(f"M30,66 C{cx + 6},{cy + 10} {cx + 4},{cy + 6} {cx + 2},{cy + 2}", Ss, 4.5)
            s.part(f"M{cx - 6},{cy} C{cx - 8},{cy - 8} {cx - 2},{cy - 14} {cx + 6},{cy - 12 - op * .3} C{cx},{cy - 8} {cx},{cy - 4} {cx + 6},{cy - 2} C{cx + 4},{cy + 4} {cx - 2},{cy + 4} {cx - 6},{cy} Z", G, Gs, "#fff4b0")
        # 头和王冠
        s.part("M20,60 C18,52 22,46 30,46 C38,46 42,52 40,60 C38,66 34,68 30,68 C26,68 22,66 20,60 Z", S_, Ss, Sh)
        s.part(poly((22, 48), (22, 40), (26, 44), (30, 36), (34, 44), (38, 40), (38, 48)), G, Gs, "#fff4b0")
        s.flat(ell(30, 45, 1.6, 1.6), "#3ad0e0", LINE, .7)
        s.eye(26, 56, 2.6, 3, "#3ad0e0", a["blink"], lid=.35)
        s.eye(34, 56, 2.6, 3, "#3ad0e0", a["blink"], lid=.35)
        s.line("M28,63 Q30,64.5 32,63")
    return s


# ------------------------------------------------------------------ 046 冰后·霜晶（冰/妖精）：冰晶女王
def d046(f):
    a = anim(f)
    LINE = "#16284a"
    s = Sprite(LINE)
    s.fit = .9
    I, Is, Ih = "#bfeaff", "#6aa8d8", "#ffffff"
    D, Ds = "#5a8ae0", "#2a50a0"
    P = "#ffc8ec"
    s.lid_color = Is
    fl = a["flap"]
    y0 = -math.sin(a["ph"]) * 2   # 整只上下漂浮
    with s.group(f"translate(0 {y0:.2f})"):
        # 冰晶翅膀
        for side in (-1, 1):
            with s.group(rot(side * fl * 6, 48, 40)):
                s.part(f"M48,40 L{48 + side * 34},{14} L{48 + side * 28},{32} L{48 + side * 40},{38} L{48 + side * 26},{48} L{48 + side * 30},{60} Z",
                       "#e8f8ff", "#a8d8f0")
                s.line(f"M48,40 L{48 + side * 30},{22}", "#a8d8f0", 1)
        # 礼裙（冰锥下摆）
        s.part("M36,46 C34,58 26,70 22,84 L30,80 L34,88 L40,82 L48,90 L56,82 L62,88 L66,80 L74,84 C70,70 62,58 60,46 Z", D, Ds, "#8ab0ff")
        s.part("M40,46 C40,58 38,70 36,82 L42,80 L48,86 L54,80 L60,82 C58,70 56,58 56,46 Z", I, Is, Ih)
        # 身体和手臂
        s.part("M40,36 C40,30 56,30 56,36 L58,48 C54,52 42,52 38,48 Z", I, Is, Ih)
        s.part("M40,38 C34,42 30,48 30,54 L33,55 C34,50 38,46 42,44 Z", I, Is)
        s.part("M56,38 C62,42 66,48 66,54 L63,55 C62,50 58,46 54,44 Z", I, Is)
        # 手里的冰晶权杖
        s.line("M66,56 L72,30", "#a8d8f0", 2)
        s.part(poly((72, 30), (69, 24), (72, 16), (75, 24)), "#e8f8ff", "#8ac0e8")
        # 头发（冰蓝长发）
        s.part("M34,26 C32,12 40,6 48,6 C56,6 64,12 62,26 C64,34 62,40 60,44 L56,30 L40,30 L36,44 C34,40 32,34 34,26 Z", D, Ds, "#8ab0ff")
        s.part(ell(48, 24, 10, 10), "#f4f8ff", "#c8d8ec")
        s.part("M38,20 C40,12 56,12 58,20 C54,16 50,18 48,22 C46,18 42,16 38,20 Z", D, Ds)
        # 冰晶王冠
        s.part(poly((38, 12), (40, 2), (43, 8), (48, -4), (53, 8), (56, 2), (58, 12)), "#e8f8ff", "#8ac0e8")
        s.flat(ell(48, 8, 1.8, 2.2), "#ff7ac0", LINE, .7)
        s.eye(44, 25, 2.4, 3.2, "#3a6ad8", a["blink"], lid=.1)
        s.eye(52, 25, 2.4, 3.2, "#3a6ad8", a["blink"], lid=.1)
        s.flat(ell(41, 29, 1.8, 1), P)
        s.flat(ell(55, 29, 1.8, 1), P)
        s.line("M46.5,30 Q48,31 49.5,30")
    # 身边飘落的雪花
    for i in range(4):
        t = (a["f"] / 24 + i / 4) % 1
        x, y = 14 + i * 22, 10 + t * 70
        s.flat(poly((x, y - 2), (x + .7, y - .7), (x + 2, y), (x + .7, y + .7), (x, y + 2), (x - .7, y + .7), (x - 2, y), (x - .7, y - .7)), "#ffffff", "#8ac0e8", .6)
    return s


# ------------------------------------------------------------------ 047 岩心巨像（岩石/格斗）
def d047(f):
    a = anim(f)
    LINE = "#1e1a16"
    s = Sprite(LINE)
    s.fit = .9
    R, Rs, Rh = "#a8957a", "#6e5e48", "#d8c8a8"
    D, Ds = "#7a6a58", "#4a3e32"
    CORE = ("#ff6a1a", "#ffb03a", "#fff0a0")
    s.lid_color = Rs
    b = a["breath"]
    glow = .5 + .5 * math.sin(a["ph"] * 2)
    # 远侧手臂
    s.part("M66,36 C76,40 80,52 78,62 L70,64 C70,54 68,46 62,42 Z", D, Ds)
    s.part(poly((70, 62), (82, 60), (84, 72), (72, 74)), D, Ds)
    # 腿
    s.part(poly((32, 66), (44, 66), (46, 86), (30, 86)), D, Ds)
    s.part(poly((52, 66), (64, 66), (66, 86), (50, 86)), R, Rs, Rh)
    s.part(poly((28, 84), (48, 84), (48, 90), (26, 90)), Ds, "#2e261e")
    s.part(poly((48, 84), (68, 84), (70, 90), (48, 90)), D, Ds)
    with s.group(f"translate(0 {-b * .8:.2f})"):
        # 身体：一块块石板拼起来
        s.part(poly((26, 34), (40, 24), (58, 24), (72, 34), (70, 58), (58, 70), (38, 70), (26, 58)), R, Rs, Rh)
        s.part(poly((30, 36), (40, 30), (46, 40), (36, 46)), Rh, R, line=LINE)
        s.part(poly((58, 32), (66, 38), (62, 48), (54, 40)), D, Ds)
        s.line("M38,58 L46,64 L54,58", Rs, 1)
        # 胸口的岩心，脉动发光
        s.flat(poly((48, 40), (56, 48), (48, 58), (40, 48)), LINE)
        s.flat(poly((48, 42), (54, 48), (48, 56), (42, 48)), CORE[0] if glow < .5 else CORE[1])
        s.flat(poly((48, 45), (51, 48), (48, 52), (45, 48)), CORE[2])
        for i in range(3):
            ang = i * 120 + a["f"] * 15
            s.line(f"M{48 + math.cos(math.radians(ang)) * 9:.1f},{48 + math.sin(math.radians(ang)) * 9:.1f} L{48 + math.cos(math.radians(ang)) * 12:.1f},{48 + math.sin(math.radians(ang)) * 12:.1f}", CORE[1], 1)
        # 头（小，嵌在肩膀之间）
        s.part(poly((38, 26), (40, 14), (48, 10), (56, 14), (58, 26), (48, 30)), R, Rs, Rh)
        s.flat(poly((40, 19), (56, 19), (55, 23), (41, 23)), LINE)
        s.flat(ell(44, 21, 2, 1.4), CORE[2] if not a["blink"] else LINE)
        s.flat(ell(52, 21, 2, 1.4), CORE[2] if not a["blink"] else LINE)
    # 近侧手臂：巨大的石拳
    with s.group(rot(a["sway"] * 3, 30, 36)):
        s.part("M30,34 C20,38 14,48 14,58 L22,60 C22,52 26,46 32,42 Z", R, Rs, Rh)
        s.part(poly((8, 58), (26, 56), (28, 72), (24, 76), (10, 76), (6, 70)), R, Rs, Rh)
        for y in (62, 67, 72):
            s.line(f"M10,{y} L18,{y}", Rs, 1)
    return s


SPECIES = {"d040": d040, "d041": d041, "d042": d042, "d043": d043, "d044": d044, "d045": d045, "d046": d046, "d047": d047}
