"""#010-#024：圆滚鸟线、绒绒虫线、炭炭线、浮浮母线、电栗线、角鳄线"""
import math

from kit import Sprite, anim, ell, poly, rot, scale_about
from fox import HIND, LEG
from legends1 import flame


def hop(a, h=3):
    """原地轻跳：一个循环跳两下，落地时压扁"""
    t = abs(math.sin(a["ph"]))
    return -t * h, 1 - .06 * (1 - t)


# ================================================================== 圆滚鸟线（普通/飞行）
BR, BRs, BRh = "#c89a62", "#8a6234", "#ecc890"
CR, CRs = "#fff4dc", "#e0cca0"
LAV, LAVs = "#a98ff3", "#6a54b8"
BEAK, BEAKs = "#ffb43a", "#c87a1a"


def yuanniao(f):
    a = anim(f)
    LINE = "#2e1e10"
    s = Sprite(LINE)
    s.lid_color = BRs
    dy, sq = hop(a, 4)
    s.flat(ell(48, 89, 14 + dy, 2.5), "#c8c0a0")
    with s.group(f"translate(0 {dy:.2f}) {scale_about(1 / sq, sq, 48, 89)}"):
        # 尾巴两根翘羽
        s.part("M64,74 C72,70 78,66 80,60 C76,66 70,70 66,72 Z", BRs, "#5a3a1a")
        s.part("M64,78 C74,78 80,74 84,68 C80,76 72,80 64,80 Z", LAV, LAVs)
        for x in (42, 54):
            s.line(f"M{x},84 L{x},89", BEAK, 2)
            s.flat(poly((x - 3, 90), (x, 87), (x + 3, 90)), BEAK, LINE, .8)
        # 圆滚滚的身体就是头
        s.part(ell(48, 66, 22, 20), BR, BRs, BRh)
        s.part(ell(48, 74, 14, 11), CR, CRs, line="none")
        # 小翅膀半张扇动
        for side in (-1, 1):
            with s.group(rot(side * (10 + a["flap"] * 14), 48 + side * 20, 64)):
                s.part(f"M{48 + side * 19},60 C{48 + side * 30},58 {48 + side * 32},68 {48 + side * 28},74 C{48 + side * 24},72 {48 + side * 20},70 {48 + side * 19},66 Z", BR, BRs)
                s.flat(f"M{48 + side * 26},70 C{48 + side * 29},70 {48 + side * 30},72 {48 + side * 28},74 Z", LAV)
        # 头顶一撮呆毛
        with s.group(rot(a["sway"] * 10, 48, 47)):
            s.part("M46,47 C42,40 44,34 48,34 C46,38 48,42 50,46 Z", BRs, "#5a3a1a")
            s.part("M48,47 C50,40 54,38 56,40 C52,42 52,44 51,47 Z", LAV, LAVs)
        s.eye(41, 60, 3.6, 4.4, "#5a3a1a", a["blink"])
        s.eye(55, 60, 3.6, 4.4, "#5a3a1a", a["blink"])
        s.part(poly((45, 65), (51, 65), (48, 70)), BEAK, BEAKs)
        s.flat(ell(35, 67, 3, 1.6), "#ff9a8a")
        s.flat(ell(61, 67, 3, 1.6), "#ff9a8a")
    return s


def yuanniao2(f):
    a = anim(f)
    LINE = "#2e1e10"
    s = Sprite(LINE)
    s.fit = .95
    s.lid_color = BRs
    dy, sq = hop(a, 2.5)
    with s.group(f"translate(0 {dy:.2f})"):
        # 扇形尾羽
        with s.group(rot(a["sway"] * 4, 62, 70)):
            for ang in (-30, -10, 10):
                with s.group(rot(ang, 62, 70)):
                    s.part("M60,70 C66,76 74,82 82,82 C78,78 72,72 66,68 Z", BR if ang != -10 else LAV, BRs if ang != -10 else LAVs)
        for x in (40, 52):
            s.line(f"M{x},78 L{x},89", BEAK, 2.4)
            s.flat(poly((x - 4, 90), (x, 86), (x + 3, 90)), BEAK, LINE, .8)
        # 远侧翅膀
        with s.group(rot(-a["flap"] * 8 - 8, 58, 50)):
            s.part("M58,50 C68,42 80,40 88,44 C84,48 84,52 80,56 C74,60 66,60 60,60 Z", BRs, "#5a3a1a")
        s.part("M28,58 C26,46 34,38 46,38 C58,38 64,48 62,60 C60,72 54,80 44,80 C34,80 30,70 28,58 Z", BR, BRs, BRh)
        s.part("M34,62 C34,52 50,50 54,60 C56,72 50,78 44,78 C38,78 34,72 34,62 Z", CR, CRs, line="none")
        for y in (62, 68):
            s.line(f"M40,{y} q3,2 6,0 q3,2 6,0", CRs, 1)
        with s.group(rot(a["flap"] * 10 + 8, 32, 50)):
            s.part("M32,50 C22,42 10,40 4,44 C8,48 8,52 12,56 C18,60 26,62 32,60 Z", BR, BRs, BRh)
            s.part("M4,44 C8,48 8,52 12,56 C10,52 8,48 4,44 Z", LAV, LAVs, line="none")
            s.line("M12,48 L26,54", BRs, 1)
        # 头和往后梳的长冠羽
        with s.group(rot(a["sway"] * 5, 46, 24)):
            s.part("M44,22 C48,10 58,4 70,6 C62,10 58,14 56,20 Z", LAV, LAVs)
            s.part("M42,22 C44,12 52,8 60,10 C54,12 50,16 50,22 Z", BRs, "#5a3a1a")
        s.part(ell(46, 30, 11, 10), BR, BRs, BRh)
        s.part(ell(46, 35, 6.5, 4), CR, CRs, line="none")
        s.eye(41.5, 28.5, 2.8, 3.4, "#5a3a1a", a["blink"], lid=.25)
        s.eye(50.5, 28.5, 2.8, 3.4, "#5a3a1a", a["blink"], lid=.25)
        s.part(poly((43, 32), (49, 32), (46, 38)), BEAK, BEAKs)
    return s


def d012(f):
    a = anim(f)
    LINE = "#24180e"
    s = Sprite(LINE)
    s.fit = .84
    D, Ds, Dh = "#8a6a4a", "#56402a", "#b89a72"
    G, Gs = "#ffd24a", "#c08a1a"
    s.lid_color = Ds
    dy, _ = hop(a, 1.5)
    fl = a["flap"]
    with s.group(f"translate(0 {dy:.2f})"):
        # 远侧大翅膀
        with s.group(rot(-fl * 8 - 4, 56, 40)):
            s.part("M56,40 C66,22 80,10 94,8 L90,16 L96,20 L88,26 L94,30 L84,34 L88,40 L74,44 Z", Ds, "#3a2a1a")
        with s.group(rot(a["sway"] * 4, 56, 70)):
            for ang in (-25, 0, 25):
                with s.group(rot(ang, 56, 70)):
                    s.part("M52,70 L60,70 L62,88 L56,84 L50,88 Z", D if ang else LAV, Ds if ang else LAVs)
        for x in (40, 52):
            s.line(f"M{x},74 L{x},88", BEAK, 3)
            s.flat(poly((x - 5, 90), (x - 3, 86), (x, 85), (x + 3, 86), (x + 4, 90)), BEAK, LINE, .8)
        s.part("M30,52 C28,38 38,30 50,30 C62,30 68,40 66,54 C64,68 58,76 48,76 C38,76 32,66 30,52 Z", D, Ds, Dh)
        s.part("M36,56 C36,46 52,44 58,54 C60,66 54,72 48,72 C40,72 36,66 36,56 Z", CR, CRs, line="none")
        for y in (54, 60, 66):
            s.line(f"M41,{y} q3,2 7,0 q3,2 7,0", CRs, 1)
        # 近侧大翅膀，翼尖淡紫
        with s.group(rot(fl * 8 + 4, 40, 40)):
            s.part("M40,40 C30,22 16,10 2,8 L6,16 L0,20 L8,26 L2,30 L12,34 L8,40 L22,44 C28,48 34,50 40,50 Z", D, Ds, Dh)
            s.part("M2,8 L6,16 L0,20 L8,26 L2,30 L12,34 L8,40 L12,40 C12,28 8,18 2,8 Z", LAV, LAVs, line="none")
            for x, y in ((10, 20), (12, 28), (16, 36)):
                s.line(f"M{x},{y} L{x + 18},{y + 8}", Ds, 1)
        # 头：白色的鹰头，金色冠羽
        with s.group(rot(a["sway"] * 4, 48, 18)):
            s.part(poly((40, 18), (36, 2), (44, 10), (48, -2), (52, 10), (60, 2), (56, 18)), G, Gs)
        s.part(ell(48, 24, 11, 10), "#f6f0e4", "#c8bca4", "#ffffff")
        s.part("M44,26 L52,26 C52,32 50,34 48,36 L46,32 Z", G, Gs)
        s.eye(43, 22, 2.8, 3.2, "#c8381a", a["blink"], lid=.45)
        s.eye(53, 22, 2.8, 3.2, "#c8381a", a["blink"], lid=.45)
    return s


# ================================================================== 绒绒虫线（虫/飞行）
GR, GRs, GRh = "#c8e05a", "#86a01a", "#f0ff9a"


def chongchong(f):
    a = anim(f)
    LINE = "#1e2a0e"
    s = Sprite(LINE)
    s.lid_color = GRs
    # 毛毛虫：四节圆滚滚的身体，一节节起伏
    for i in range(3, 0, -1):
        x = 40 + i * 12
        y = 78 - abs(math.sin(a["ph"] + i * .9)) * 3
        s.part(ell(x, y, 9, 8.5), GR if i % 2 else "#b4d040", GRs, GRh)
        s.flat(ell(x, y - 6, 2, 1.6), LAV)
        s.line(f"M{x - 3},{y + 8} L{x - 3},{y + 11}", GRs, 2)
        s.line(f"M{x + 3},{y + 8} L{x + 3},{y + 11}", GRs, 2)
    # 背上一对淡紫色小翅芽
    for side in (-1, 1):
        with s.group(rot(side * a["flap"] * 12, 56, 66)):
            s.part(ell(56 + side * 6, 62, 6, 4), "#e4d8ff", LAVs)
    hy = 64 - math.sin(a["ph"]) * 1.5
    # 触角，末端绒球
    for side in (-1, 1):
        with s.group(rot(side * (8 + a["sway"] * 6), 38 + side * 6, hy - 14)):
            s.line(f"M{38 + side * 6},{hy - 14} C{38 + side * 8},{hy - 22} {38 + side * 12},{hy - 24} {38 + side * 14},{hy - 26}", GRs, 1.6)
            s.part(ell(38 + side * 14, hy - 27, 3, 3), LAV, LAVs)
    s.part(ell(38, hy, 16, 15), GR, GRs, GRh)
    # 绒毛边
    for i in range(7):
        ang = math.radians(-150 + i * 50)
        s.flat(ell(38 + math.cos(ang) * 15, hy + math.sin(ang) * 14, 2.2, 2.2), GRh)
    s.eye(32, hy - 1, 3.6, 4.4, "#3a5a0a", a["blink"])
    s.eye(44, hy - 1, 3.6, 4.4, "#3a5a0a", a["blink"])
    s.flat(ell(27, hy + 6, 2.6, 1.4), "#ff9a8a")
    s.flat(ell(49, hy + 6, 2.6, 1.4), "#ff9a8a")
    s.line(f"M35.5,{hy + 7} Q38,{hy + 9.5} 40.5,{hy + 7}")
    return s


def jianjian(f):
    a = anim(f)
    LINE = "#1e2a0e"
    s = Sprite(LINE)
    s.lid_color = GRs
    sw = a["sway"]
    # 从上面垂下来的丝
    s.line("M48,0 L48,18", "#e8f0d8", 1.2)
    with s.group(rot(sw * 6, 48, 4)):
        # 茧：一圈圈丝缠成的纺锤形
        s.part("M48,16 C64,20 68,40 66,56 C64,74 56,86 48,88 C40,86 32,74 30,56 C28,40 32,20 48,16 Z", "#e8e8b0", "#b0b070", "#ffffe0")
        for y in (28, 40, 66, 76):
            w = 16 - abs(y - 52) * .28
            s.line(f"M{48 - w},{y} Q48,{y + 4} {48 + w},{y}", "#b0b070", 1)
        # 一对翅芽从茧缝里探出来
        for side in (-1, 1):
            with s.group(rot(side * (a["flap"] * 8), 48 + side * 14, 60)):
                s.part(f"M{48 + side * 14},58 C{48 + side * 26},50 {48 + side * 30},60 {48 + side * 24},70 C{48 + side * 20},68 {48 + side * 16},64 {48 + side * 14},62 Z", "#e4d8ff", LAVs)
        # 茧开口，露出脸
        s.part(ell(48, 50, 12, 10), GR, GRs, GRh)
        s.line("M36,46 Q48,38 60,46", "#b0b070", 2)
        s.eye(43, 50, 3, 3.6, "#3a5a0a", a["blink"], lid=.35)
        s.eye(53, 50, 3, 3.6, "#3a5a0a", a["blink"], lid=.35)
        s.line("M46,56 L50,56")
    return s


def caidie(f):
    a = anim(f)
    LINE = "#24142e"
    s = Sprite(LINE)
    s.lid_color = "#3a2a4a"
    y0 = -math.sin(a["ph"]) * 3
    k = .55 + .45 * abs(math.cos(a["ph"]))   # 翅膀开合（正面看是横向收窄）
    with s.group(f"translate(0 {y0:.2f})"):
        for side in (-1, 1):
            with s.group(scale_about(k, 1, 48, 50)):
                # 上翅
                s.part(f"M48,46 C{48 + side * 14},20 {48 + side * 40},8 {48 + side * 44},22 C{48 + side * 46},36 {48 + side * 32},46 48,50 Z", LAV, LAVs, "#d8ccff")
                s.flat(ell(48 + side * 30, 24, 7, 6), "#ffe066", LINE, .8)
                s.flat(ell(48 + side * 30, 24, 3, 2.6), "#ff6aa8")
                s.flat(ell(48 + side * 18, 36, 3, 3), "#ffffff")
                # 下翅
                s.part(f"M48,52 C{48 + side * 22},50 {48 + side * 34},62 {48 + side * 28},76 C{48 + side * 22},82 {48 + side * 12},74 48,58 Z", GR, GRs, GRh)
                s.flat(ell(48 + side * 24, 68, 3.5, 3.5), "#ff6aa8", LINE, .7)
        # 身体
        s.part("M44,46 C44,40 52,40 52,46 L51,70 C50,74 46,74 45,70 Z", "#4a3a5a", "#2a1e36", "#7a6a90")
        for y in (54, 60, 66):
            s.line(f"M45,{y} L51,{y}", "#2a1e36", 1)
        # 触角
        for side in (-1, 1):
            s.line(f"M{48 + side * 3},32 C{48 + side * 6},22 {48 + side * 10},18 {48 + side * 12},14", LINE, 1.2)
            s.flat(ell(48 + side * 12, 14, 2.2, 2.2), "#ffe066", LINE, .7)
        s.part(ell(48, 38, 9, 8), "#4a3a5a", "#2a1e36", "#7a6a90")
        s.eye(44.5, 37.5, 2.8, 3.4, "#ff6aa8", a["blink"])
        s.eye(51.5, 37.5, 2.8, 3.4, "#ff6aa8", a["blink"])
        s.line("M46.5,42.5 Q48,43.5 49.5,42.5", "#ffffff", .9)
    # 鳞粉
    for i in range(3):
        t = (a["f"] / 24 + i / 3) % 1
        s.flat(ell(30 + i * 18, 70 + t * 16, .9, .9), "#ffe066")
    return s


# ================================================================== 炭炭线（火）
CH, CHs, CHh = "#4a4448", "#2a2428", "#6e666c"
EM = "#ff7a2a"


def cracks(s, pts, glow):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        s.line(f"M{x1},{y1} L{x2},{y2}", "#ffd04a" if glow > .5 else EM, 1.2)


def tantan(f):
    a = anim(f)
    LINE = "#140e10"
    s = Sprite(LINE)
    s.lid_color = CHs
    b = a["breath"]
    glow = (math.sin(a["ph"] * 2) + 1) / 2
    # 尾巴：一块冒火星的炭
    with s.group(rot(a["sway"] * 10, 66, 76)):
        s.part("M64,78 C72,76 78,70 78,62 C82,66 82,74 76,80 C72,82 68,82 64,82 Z", CH, CHs)
        flame(s, 78, 64, 10, a["flick"], 10)
    with s.group(scale_about(1 + .02 * b, 1 + .03 * b, 48, 89)):
        s.part("M30,89 C26,80 30,66 44,64 C56,62 66,68 68,78 C70,86 66,89 62,89 Z", CH, CHs, CHh)
        cracks(s, ((40, 72), (44, 76), (42, 80), (46, 84)), glow)
        cracks(s, ((58, 70), (56, 76), (60, 80)), glow)
        s.part(ell(36, 88, 5.5, 2.6), CH, CHs)
        s.part(ell(56, 88, 5.5, 2.6), CH, CHs)
        s.flat(ell(36, 88.5, 3, 1), EM)
        s.flat(ell(56, 88.5, 3, 1), EM)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        # 耳朵：三角，耳尖烧红
        for x0, flip in ((32, -1), (56, 1)):
            tw = -10 * flip if (a["f"] in (18, 19) and flip > 0) else 0
            with s.group(rot(tw, x0, 42)):
                s.part(poly((x0 - 6, 44), (x0 + flip * 3, 26), (x0 + 6, 42)), CH, CHs, CHh)
                s.flat(poly((x0 - 2, 34), (x0 + flip * 3, 26), (x0 + 3, 33)), EM)
        s.part(ell(44, 52, 17, 14), CH, CHs, CHh)
        cracks(s, ((44, 39), (42, 43), (45, 46)), glow)
        s.part(ell(44, 59, 7, 4.5), "#7a6a6a", "#4a3e3e", line="none")
        s.flat(ell(44, 56.5, 2.2, 1.6), EM)
        s.eye(37.5, 51, 3.8, 4.6, "#ff7a2a", a["blink"])
        s.eye(50.5, 51, 3.8, 4.6, "#ff7a2a", a["blink"])
        s.line("M41.5,61 Q44,63 46.5,61", EM)
        s.flat(ell(31, 57, 2.6, 1.4), "#c84a2a")
        s.flat(ell(57, 57, 2.6, 1.4), "#c84a2a")
    return s


def d017(f):
    a = anim(f)
    LINE = "#140e10"
    s = Sprite(LINE)
    s.fit = .9
    s.lid_color = CHs
    b = a["breath"]
    glow = (math.sin(a["ph"] * 2) + 1) / 2
    with s.group(rot(a["sway"] * 6, 74, 60)):
        s.part("M72,62 C82,60 88,52 86,42 C90,46 92,56 86,64 C82,68 76,68 72,68 Z", CH, CHs)
        flame(s, 86, 44, 16, a["flick"], 5)
    s.part(LEG(32, 62, 89, 7), CHs, "#140e10")
    s.part(HIND(70, 58, 89), CHs, "#140e10")
    with s.group(f"translate(0 {-b * .7:.2f})"):
        s.part("M24,56 C26,44 42,40 58,42 C72,43 80,50 80,60 C80,68 72,72 56,72 C40,72 24,68 24,56 Z", CH, CHs, CHh)
        cracks(s, ((36, 48), (40, 54), (38, 60), (42, 66)), glow)
        cracks(s, ((56, 46), (54, 52), (58, 58)), glow)
        cracks(s, ((70, 50), (72, 56), (68, 62)), glow)
        # 背上火焰
        for i, x in enumerate((44, 54, 64)):
            flame(s, x, 44, 10 + (i % 2) * 3, a["flick"] * (1 if i % 2 else -1), 0)
    s.part(LEG(28, 58, 88, 8), CH, CHs, CHh)
    s.part(ell(27, 89, 5, 2.2), EM, "#c8501a")
    s.part(HIND(66, 54, 88), CH, CHs, CHh)
    s.part(ell(67, 89, 5, 2.2), EM, "#c8501a")
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        # 弯角，角尖着火
        for side in (-1, 1):
            x0 = 28 + side * 8
            s.part(f"M{x0},22 C{x0 + side * 4},14 {x0 + side * 10},10 {x0 + side * 12},2 C{x0 + side * 14},10 {x0 + side * 10},20 {x0 + side * 4},26 Z", "#d8c8b8", "#9a8a7a")
            flame(s, x0 + side * 12, 4, 8, a["flick"], side * 10)
        s.part("M14,32 C14,22 20,18 28,18 C36,18 42,22 42,32 C42,42 36,48 28,48 C20,48 14,42 14,32 Z", CH, CHs, CHh)
        cracks(s, ((28, 19), (26, 23), (29, 26)), glow)
        s.part(ell(28, 41, 7, 5), "#7a6a6a", "#4a3e3e", line="none")
        s.flat(ell(28, 38.5, 2.4, 1.6), EM)
        s.eye(22, 31, 3.2, 3.8, "#ff7a2a", a["blink"], lid=.4)
        s.eye(34, 31, 3.2, 3.8, "#ff7a2a", a["blink"], lid=.4)
        s.line("M24,44 Q28,46.5 32,44", EM)
        s.flat("M25,44.5 L26,47 L27,45 Z", "#ffffff")
        s.flat("M29,45 L30,47 L31,44.5 Z", "#ffffff")
    return s


# ================================================================== 浮浮母线（水/毒）
JB, JBs, JBh = "#8ab8ff", "#4a78d8", "#d0e4ff"
JP, JPs = "#c060c8", "#8a2a9a"


def tentacles(s, a, xs, top, ln, col, cols, w=2.4):
    for i, x in enumerate(xs):
        ph = a["ph"] + i * .8
        d = f"M{x},{top} C{x + math.sin(ph) * 4},{top + ln * .35} {x - math.sin(ph) * 4},{top + ln * .7} {x + math.sin(ph + 1) * 3},{top + ln}"
        s.line(d, cols, w + 1.4)
        s.line(d, col, w)


def fufu(f):
    a = anim(f)
    LINE = "#141a3a"
    s = Sprite(LINE)
    s.lid_color = JBs
    y0 = -math.sin(a["ph"]) * 3
    pulse = 1 + .04 * math.sin(a["ph"] * 2)
    s.flat(ell(48, 89, 12, 2), "#c0c8d8")
    with s.group(f"translate(0 {y0:.2f})"):
        tentacles(s, a, (38, 44, 52, 58), 60, 22, JP, JPs)
        with s.group(scale_about(pulse, 1 / pulse, 48, 60)):
            s.part("M26,60 C24,40 34,30 48,30 C62,30 72,40 70,60 C66,64 62,60 58,64 C54,60 50,64 48,64 C46,64 42,60 38,64 C34,60 30,64 26,60 Z", JB, JBs, JBh)
            for x, y, r in ((36, 40, 2.6), (60, 42, 2.2), (48, 34, 2)):
                s.flat(ell(x, y, r, r), JP, LINE, .7)
        s.eye(41, 50, 3.6, 4.4, "#2a3a8a", a["blink"])
        s.eye(55, 50, 3.6, 4.4, "#2a3a8a", a["blink"])
        s.flat(ell(35, 56, 2.4, 1.3), "#ff9ac8")
        s.flat(ell(61, 56, 2.4, 1.3), "#ff9ac8")
        s.line("M46,57 Q48,58.5 50,57")
    return s


def d019(f):
    a = anim(f)
    LINE = "#140e2e"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = "#3a2a8a"
    D, Ds, Dh = "#5a6ad8", "#2e3a9a", "#9aa8ff"
    y0 = -math.sin(a["ph"]) * 3
    pulse = 1 + .05 * math.sin(a["ph"] * 2)
    glow = (math.sin(a["ph"] * 2) + 1) / 2
    with s.group(f"translate(0 {y0:.2f})"):
        tentacles(s, a, (30, 38, 46, 54, 62, 70), 54, 32, JP, JPs, 2.6)
        tentacles(s, a, (42, 50, 58), 54, 24, "#e8a8f0", JPs, 3.4)
        with s.group(scale_about(pulse, 1 / pulse, 48, 54)):
            # 头冠一样的褶边
            s.part("M18,54 C14,30 30,14 48,14 C66,14 82,30 78,54 C74,58 70,54 66,58 C62,54 58,58 54,56 C50,60 46,60 42,56 C38,58 34,54 30,58 C26,54 22,58 18,54 Z", D, Ds, Dh)
            s.part(poly((34, 18), (36, 6), (42, 14), (48, 2), (54, 14), (60, 6), (62, 18)), JP, JPs)
            for x, y in ((28, 32), (68, 32), (36, 22), (60, 22)):
                s.flat(ell(x, y, 2.6, 2.6), "#f0a0ff" if glow > .5 else JP, LINE, .7)
            s.flat(ell(48, 10, 1.8, 1.8), "#9aff7a", LINE, .6)
        s.eye(40, 40, 3.4, 4.2, "#9a2aa8", a["blink"], lid=.35)
        s.eye(56, 40, 3.4, 4.2, "#9a2aa8", a["blink"], lid=.35)
        s.line("M44,48 Q48,50.5 52,48")
    return s


# ================================================================== 电栗线（电）
EY, EYs, EYh = "#ffd84a", "#d09a1a", "#fff4a8"
NUT, NUTs = "#8a5a2a", "#5a3414"


def burr(s, cx, cy, r, n, col, cols, ln=5):
    """栗子刺壳：一圈尖刺"""
    pts = []
    for i in range(n * 2):
        ang = math.pi + i * math.pi / (n * 2 - 1)
        rr = r + (ln if i % 2 == 0 else 0)
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr * .9))
    pts.append((cx + r, cy + 2))
    pts.append((cx - r, cy + 2))
    s.part(poly(*pts), col, cols)


def dianli(f):
    a = anim(f)
    LINE = "#2a1a08"
    s = Sprite(LINE)
    s.lid_color = EYs
    b = a["breath"]
    # 闪电尾巴
    with s.group(rot(a["sway"] * 10, 64, 80)):
        s.part(poly((62, 82), (70, 74), (66, 72), (76, 62), (72, 70), (78, 70), (66, 84)), EY, EYs)
    with s.group(scale_about(1 + .03 * b, 1 - .02 * b, 48, 89)):
        s.part(ell(48, 70, 20, 18), EY, EYs, EYh)
        s.part(ell(48, 78, 11, 8), "#fff8d8", "#e8d8a0", line="none")
        # 头顶栗子刺壳，像戴了顶帽子
        burr(s, 48, 58, 21, 7, NUT, NUTs)
        s.flat(ell(40, 50, 3, 1.6), "#b07a3a")
        s.part(ell(38, 88, 5.5, 2.6), EY, EYs)
        s.part(ell(58, 88, 5.5, 2.6), EY, EYs)
        s.eye(41, 68, 3.8, 4.6, "#5a3414", a["blink"])
        s.eye(55, 68, 3.8, 4.6, "#5a3414", a["blink"])
        s.flat(ell(34, 75, 3.2, 2.2), "#ff6a3a")
        s.flat(ell(62, 75, 3.2, 2.2), "#ff6a3a")
        s.line("M45.5,76 Q48,78 50.5,76")
    # 噼啪的小电火花
    if a["f"] % 6 < 3:
        x = 24 if a["f"] % 12 < 6 else 72
        s.line(f"M{x},50 L{x + 3},54 L{x},56 L{x + 3},60", "#fff4a8", 1.4)
    return s


def d021(f):
    a = anim(f)
    LINE = "#2a1a08"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = EYs
    b = a["breath"]
    with s.group(rot(a["sway"] * 6, 74, 62)):
        s.part(poly((72, 64), (82, 52), (78, 50), (90, 34), (86, 46), (94, 46), (78, 66)), EY, EYs)
    s.part(LEG(32, 64, 89, 6), EYs, "#9a6a10")
    s.part(HIND(70, 60, 89), EYs, "#9a6a10")
    with s.group(f"translate(0 {-b * .7:.2f})"):
        s.part("M24,58 C26,46 42,42 58,44 C72,45 80,52 80,62 C80,70 72,74 56,74 C40,74 24,70 24,58 Z", EY, EYs, EYh)
        s.part("M28,64 C34,72 48,75 60,73 C50,68 38,66 28,64 Z", "#fff8d8", "#e8d8a0", line="none")
        # 背上一整块栗子刺甲
        pts = []
        for i in range(13):
            x = 34 + i * 3.6
            y = 48 - math.sin(i / 12 * math.pi) * 6 - (6 if i % 2 == 0 else 0)
            pts.append((x, y))
        s.part(poly((32, 52), *pts, (78, 54), (72, 56), (40, 56)), NUT, NUTs)
    s.part(LEG(28, 60, 88, 7), EY, EYs, EYh)
    s.part(ell(27, 89, 4.6, 2.2), NUT, NUTs)
    s.part(HIND(66, 56, 88), EY, EYs, EYh)
    s.part(ell(67, 89, 4.6, 2.2), NUT, NUTs)
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        for x0, flip in ((18, -1), (38, 1)):
            tw = -10 * flip if (a["f"] in (18, 19) and flip > 0) else 0
            with s.group(rot(tw, x0, 24)):
                s.part(poly((x0 - 5, 26), (x0 + flip * 5, 6), (x0 + 5, 24)), EY, EYs, EYh)
                s.flat(poly((x0 - 1, 14), (x0 + flip * 5, 6), (x0 + 3, 14)), LINE)
        burr(s, 28, 24, 12, 5, NUT, NUTs, 4)
        s.part("M14,34 C14,24 20,20 28,20 C36,20 42,24 42,34 C42,42 36,46 28,46 C20,46 14,42 14,34 Z", EY, EYs, EYh)
        s.flat(ell(28, 39.5, 1.8, 1.3), LINE)
        s.eye(22, 32, 3.2, 3.8, "#5a3414", a["blink"], lid=.25)
        s.eye(34, 32, 3.2, 3.8, "#5a3414", a["blink"], lid=.25)
        s.flat(ell(17, 38, 2.8, 2), "#ff6a3a")
        s.flat(ell(39, 38, 2.8, 2), "#ff6a3a")
        s.line("M25.5,42 Q28,43.5 30.5,42")
    if a["f"] % 6 < 3:
        s.line("M88,26 L91,30 L88,32 L91,36", "#fff4a8", 1.4)
    return s


# ================================================================== 角鳄线（龙/大地）
VP, VPs, VPh = "#7a52e0", "#4a2aa8", "#a88aff"
SD, SDs = "#e8c878", "#b08a3a"


def smoke(s, a, x, y):
    t = (a["f"] % 12) / 12
    s.flat(ell(x - t * 4, y - t * 8, 1.5 + t * 2, 1.5 + t * 2), "#e0dcd8" if t < .6 else "#c8c4c0")


def croc_head(s, a, cx, cy, w, horns, lid, nose_horn=True):
    """鳄鱼正脸：宽扁的吻，两只眼在头顶鼓包上"""
    s.part(f"M{cx - w},{cy} C{cx - w},{cy - w * .7} {cx - w * .5},{cy - w * .9} {cx},{cy - w * .9} C{cx + w * .5},{cy - w * .9} {cx + w},{cy - w * .7} {cx + w},{cy} "
           f"C{cx + w},{cy + w * .6} {cx + w * .5},{cy + w * .8} {cx},{cy + w * .8} C{cx - w * .5},{cy + w * .8} {cx - w},{cy + w * .6} {cx - w},{cy} Z", VP, VPs, VPh)
    s.part(f"M{cx - w * .7},{cy + w * .2} C{cx - w * .5},{cy + w * .75} {cx + w * .5},{cy + w * .75} {cx + w * .7},{cy + w * .2} C{cx + w * .3},{cy + w * .4} {cx - w * .3},{cy + w * .4} {cx - w * .7},{cy + w * .2} Z", SD, SDs, line="none")
    s.line(f"M{cx - w * .75},{cy + w * .25} Q{cx},{cy + w * .5} {cx + w * .75},{cy + w * .25}")
    for k in (-.45, -.15, .15, .45):
        x = cx + k * w
        s.flat(poly((x - 1.2, cy + w * .38), (x, cy + w * .58), (x + 1.2, cy + w * .38)), "#ffffff")
    s.flat(ell(cx - w * .18, cy + w * .02, 1, .8), s.outline)
    s.flat(ell(cx + w * .18, cy + w * .02, 1, .8), s.outline)
    if nose_horn:
        s.part(poly((cx - 2.5, cy - w * .2), (cx, cy - w * .2 - 7 - horns), (cx + 2.5, cy - w * .2)), SD, SDs)
    for side in (-1, 1):
        s.part(ell(cx + side * w * .5, cy - w * .7, w * .32, w * .3), VP, VPs, VPh)
    r = w * .2
    s.eye(cx - w * .5, cy - w * .72, r, r * 1.15, "#e8a020", a["blink"], lid=lid)
    s.eye(cx + w * .5, cy - w * .72, r, r * 1.15, "#e8a020", a["blink"], lid=lid)


def d022(f):
    a = anim(f)
    LINE = "#1a1030"
    s = Sprite(LINE)
    s.lid_color = VPs
    b = a["breath"]
    # 尾巴拍地
    tail_a = max(0, math.sin(a["ph"] * 2)) * -12
    with s.group(rot(tail_a, 66, 80)):
        s.part("M62,76 C74,74 84,78 90,86 C82,88 72,86 62,86 Z", VP, VPs, VPh)
        for x in (70, 78):
            s.part(poly((x - 2, 77), (x, 72), (x + 3, 78)), SD, SDs)
    s.part(ell(64, 86, 7, 3.5), VPs, "#2a1478")
    with s.group(scale_about(1 + .02 * b, 1 + .02 * b, 48, 89)):
        s.part(ell(48, 76, 20, 13), VP, VPs, VPh)
        s.part(ell(46, 80, 12, 8), SD, SDs, line="none")
        s.part(ell(32, 87, 6, 3), VP, VPs)
        s.part(ell(52, 88, 6, 3), VP, VPs)
    with s.group(f"translate(0 {-b * 1.5:.2f})"):
        croc_head(s, a, 42, 58, 17, 0, .1)
    smoke(s, a, 38, 54)
    smoke(s, a, 46, 54)
    return s


def d023(f):
    a = anim(f)
    LINE = "#1a1030"
    s = Sprite(LINE)
    s.fit = .92
    s.lid_color = VPs
    b = a["breath"]
    tail_a = max(0, math.sin(a["ph"] * 2)) * -10
    with s.group(f"translate(0 8) {rot(tail_a, 72, 70)}"):
        s.part("M70,66 C82,64 90,72 94,84 C86,84 78,80 70,76 Z", VP, VPs, VPh)
        for x, y in ((80, 68), (88, 74)):
            s.part(poly((x - 2, y), (x + 1, y - 6), (x + 3, y + 1)), SD, SDs)
    s.part(LEG(34, 76, 89, 9), VPs, "#2a1478")
    s.part(LEG(70, 74, 89, 10), VPs, "#2a1478")
    with s.group(f"translate(0 {8 - b * .7:.2f})"):
        s.part("M22,64 C22,52 36,46 54,48 C70,50 80,56 80,66 C80,74 70,78 54,78 C38,78 22,74 22,64 Z", VP, VPs, VPh)
        s.part("M28,70 C36,76 52,78 64,76 C54,72 40,70 28,70 Z", SD, SDs, line="none")
        # 背上的土甲片
        for i, x in enumerate((40, 50, 60, 70)):
            s.part(f"M{x - 5},52 C{x - 4},44 {x + 4},44 {x + 5},52 Z", SD, SDs, "#fff0b0")
    s.part(LEG(28, 72, 88, 10), VP, VPs, VPh)
    s.part(ell(27, 89, 5.5, 2.2), SD, SDs)
    s.part(LEG(64, 70, 88, 11), VP, VPs, VPh)
    s.part(ell(64, 89, 5.5, 2.2), SD, SDs)
    with s.group(f"translate(0 {7 - b * 1.4:.2f})"):
        for side in (-1, 1):
            s.part(f"M{30 + side * 10},30 C{30 + side * 14},22 {30 + side * 16},16 {30 + side * 14},10 C{30 + side * 20},16 {30 + side * 20},26 {30 + side * 14},34 Z", SD, SDs)
        croc_head(s, a, 30, 44, 18, 2, .3)
    smoke(s, a, 26, 47)
    smoke(s, a, 34, 47)
    return s


def d024(f):
    a = anim(f)
    LINE = "#1a1030"
    s = Sprite(LINE)
    s.fit = .84
    s.lid_color = VPs
    b = a["breath"]
    tail_a = max(0, math.sin(a["ph"] * 2)) * -8
    with s.group(f"translate(0 6) {rot(tail_a, 74, 66)}"):
        s.part("M70,60 C84,58 94,68 98,84 C88,84 78,78 70,74 Z", VP, VPs, VPh)
        for x, y in ((82, 62), (90, 70)):
            s.part(poly((x - 3, y + 1), (x + 1, y - 8), (x + 4, y + 2)), "#9a8a7a", "#5a4e44")
    s.part(LEG(32, 74, 89, 11), VPs, "#2a1478")
    s.part(LEG(72, 70, 89, 12), VPs, "#2a1478")
    with s.group(f"translate(0 {8 - b * .7:.2f})"):
        s.part("M18,62 C18,46 34,38 54,40 C72,42 84,50 84,62 C84,72 72,78 54,78 C36,78 18,72 18,62 Z", VP, VPs, VPh)
        s.part("M24,68 C34,76 52,78 66,76 C54,72 38,70 24,68 Z", SD, SDs, line="none")
        # 山岳一样的背：一排岩峰
        for x, h in ((36, 12), (46, 18), (56, 22), (66, 16), (76, 10)):
            s.part(poly((x - 6, 46), (x - 1, 46 - h), (x + 2, 46 - h + 4), (x + 6, 46)), "#9a8a7a", "#5a4e44", "#c8b8a8")
            s.flat(poly((x - 2, 46 - h + 2), (x - 1, 46 - h), (x + 1, 46 - h + 3)), "#ffffff")
    s.part(LEG(26, 70, 88, 12), VP, VPs, VPh)
    s.part(ell(25, 89, 6.5, 2.4), SD, SDs)
    s.part(LEG(66, 66, 88, 13), VP, VPs, VPh)
    s.part(ell(66, 89, 6.5, 2.4), SD, SDs)
    with s.group(f"translate(0 {7 - b * 1.4:.2f})"):
        for side in (-1, 1):
            s.part(f"M{28 + side * 10},26 C{28 + side * 16},18 {28 + side * 20},10 {28 + side * 18},2 C{28 + side * 26},10 {28 + side * 24},24 {28 + side * 16},32 Z", SD, SDs, "#fff0b0")
        croc_head(s, a, 28, 42, 19, 4, .45)
    smoke(s, a, 24, 45)
    smoke(s, a, 32, 45)
    return s


SPECIES = {"yuanniao": yuanniao, "yuanniao2": yuanniao2, "d012": d012,
           "chongchong": chongchong, "jianjian": jianjian, "caidie": caidie,
           "tantan": tantan, "d017": d017, "fufu": fufu, "d019": d019,
           "dianli": dianli, "d021": d021, "d022": d022, "d023": d023, "d024": d024}
