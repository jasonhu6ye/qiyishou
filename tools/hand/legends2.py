"""传说幻兽 #048-#055"""
import math

from kit import Sprite, anim, ell, poly, rot, scale_about
from fox import HIND, LEG
from legends1 import flame
from mouse import leaf


def star(cx, cy, r1, r2, n=5, a0=0.0):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        ang = math.radians(a0 + i * 180 / n)
        pts.append((cx + math.sin(ang) * r, cy - math.cos(ang) * r))
    return poly(*pts)


# ------------------------------------------------------------------ 048 潮音海龙（水/龙）：长脖子、螺号角的海龙
def d048(f):
    a = anim(f)
    LINE = "#0e2440"
    s = Sprite(LINE)
    s.fit = .9
    B, Bs, Bh = "#3a9ad8", "#1e5e9a", "#7ad0ff"
    W, Ws = "#f0f6e0", "#c0caa8"
    SH, SHs = "#f6d8b0", "#c89a6a"   # 螺壳
    s.lid_color = Bs
    b = a["breath"]
    sw = a["sway"]
    # 海浪
    wave_y = 80
    # 远侧鳍
    with s.group(rot(-sw * 8, 64, 66)):
        s.part("M64,66 C74,60 86,62 90,70 C82,70 76,72 70,76 Z", Bs, "#123e6a")
    with s.group(f"translate(0 {-b * .8:.2f})"):
        # 背：螺壳甲
        s.part("M28,76 C26,60 40,50 58,50 C74,50 84,62 82,76 Z", SH, SHs, "#fff0d8")
        for i, x in enumerate((40, 52, 64, 74)):
            s.part(poly((x - 4, 56 + abs(i - 1.5) * 2), (x, 46 + abs(i - 1.5) * 3), (x + 4, 56 + abs(i - 1.5) * 2)), W, Ws)
        s.line("M34,66 Q56,58 78,66", SHs, 1)
        # 近侧鳍
        with s.group(rot(sw * 8, 40, 70)):
            s.part("M40,70 C30,66 18,70 14,78 C24,78 30,78 36,80 Z", B, Bs, Bh)
    # 长脖子 + 头
    with s.group(rot(sw * 3, 36, 70)):
        s.part("M30,72 C24,58 22,44 26,32 L36,32 C34,44 36,58 42,70 Z", B, Bs, Bh)
        s.part("M32,70 C28,58 27,46 29,34 L33,34 C32,46 33,58 38,70 Z", W, Ws, line="none")
        with s.group(f"translate(0 {-b * 1.2:.2f})"):
            # 螺号角
            for side in (-1, 1):
                x0 = 31 + side * 7
                s.part(f"M{x0},18 C{x0 + side * 4},10 {x0 + side * 10},6 {x0 + side * 12},0 C{x0 + side * 12},8 {x0 + side * 8},16 {x0 + side * 4},22 Z", SH, SHs)
                s.line(f"M{x0 + side * 3},16 L{x0 + side * 7},14", SHs, 1)
                s.line(f"M{x0 + side * 6},11 L{x0 + side * 10},9", SHs, 1)
            s.part(ell(31, 24, 11, 10), B, Bs, Bh)
            s.part(ell(31, 30, 7, 4.5), W, Ws, line="none")
            s.eye(26.5, 23, 3, 3.6, "#1e5e9a", a["blink"], lid=.1)
            s.eye(35.5, 23, 3, 3.6, "#1e5e9a", a["blink"], lid=.1)
            s.line("M28.5,30 Q31,31.5 33.5,30")
            s.flat(ell(31, 14.5, 1.8, 1.8), "#7af0e8", LINE, .7)
    # 水面
    s.part(f"M4,{wave_y} C12,{wave_y - 4 + sw} 20,{wave_y - 4 - sw} 28,{wave_y} C36,{wave_y + 3} 44,{wave_y - 4 + sw} 52,{wave_y} "
           f"C60,{wave_y + 3} 70,{wave_y - 4 - sw} 78,{wave_y} C84,{wave_y + 3} 90,{wave_y - 2} 92,{wave_y} L90,90 L6,90 Z", "#8ad8f8", "#4aa0d0", "#d8f6ff")
    for x in (16, 44, 72):
        s.line(f"M{x},{wave_y + 4} q3,-2 6,0", "#ffffff", 1)
    return s


# ------------------------------------------------------------------ 049 引路灯鸟（电/飞行）：尾巴挂着灯笼的鸟
def d049(f):
    a = anim(f)
    LINE = "#24180e"
    s = Sprite(LINE)
    s.fit = .95
    Y, Ys, Yh = "#ffd84a", "#d89a20", "#fff4a8"
    N, Ns = "#3a3a6a", "#20203e"   # 夜色翅膀
    W, Ws = "#fff8e8", "#e0d0b0"
    s.lid_color = Ys
    b = a["breath"]
    fl = a["flap"]
    glow = (math.sin(a["ph"] * 2) + 1) / 2
    # 长长的尾羽垂下来，尾端挂灯笼
    lx, ly = 70 + a["sway"] * 4, 68
    s.line(f"M54,56 C62,58 68,60 {lx},{ly - 8}", Ns, 3)
    s.line(f"M54,56 C62,58 68,60 {lx},{ly - 8}", N, 1.4)
    # 灯光晕
    s.flat(ell(lx, ly + 4, 12 + glow * 2, 12 + glow * 2), "#fff6c0" if glow > .5 else "#fff0a0")
    s.part(f"M{lx - 6},{ly - 6} L{lx + 6},{ly - 6} C{lx + 9},{ly} {lx + 9},{ly + 8} {lx + 6},{ly + 12} L{lx - 6},{ly + 12} C{lx - 9},{ly + 8} {lx - 9},{ly} {lx - 6},{ly - 6} Z",
           "#ff8a3a", "#c8501a", "#ffd0a0")
    s.part(poly((lx - 7, ly - 6), (lx + 7, ly - 6), (lx + 5, ly - 10), (lx - 5, ly - 10)), N, Ns)
    s.part(poly((lx - 6, ly + 12), (lx + 6, ly + 12), (lx + 4, ly + 15), (lx - 4, ly + 15)), N, Ns)
    s.flat(ell(lx, ly + 3, 3, 4), "#fff8c0")
    s.line(f"M{lx},{ly - 1} L{lx},{ly + 7}", "#ff8a3a", 1)
    # 爪
    for x in (38, 46):
        s.line(f"M{x},64 L{x},76", "#e09a20", 2)
        s.flat(poly((x - 3, 77), (x, 74), (x + 3, 77)), "#e09a20", LINE)
    # 树枝
    s.part("M10,78 C30,76 50,78 62,80 L62,83 C48,81 30,80 10,82 Z", "#8a5a32", "#5a3618")
    with s.group(f"translate(0 {-b * 1:.2f})"):
        with s.group(rot(-fl * 10 - 10, 54, 46)):
            s.part("M54,46 C64,36 76,32 86,34 C82,40 82,44 78,48 C74,52 64,54 56,54 Z", Ns, "#101024")
        s.part("M30,52 C28,40 36,32 46,32 C58,32 62,42 60,54 C58,64 52,68 44,68 C36,68 32,62 30,52 Z", Y, Ys, Yh)
        s.part("M36,56 C36,48 50,46 54,56 C54,64 48,66 44,66 C40,66 36,62 36,56 Z", W, Ws, line="none")
        with s.group(rot(fl * 10 + 10, 34, 46)):
            s.part("M34,46 C24,36 12,32 4,36 C8,40 8,46 12,48 C18,54 28,54 34,54 Z", N, Ns, "#6a6aa8")
            for x in (8, 14, 20):
                s.flat(ell(x, 42, 1, 1), "#fff4a8")
        # 头上的电光冠羽
        with s.group(rot(a["sway"] * 5, 45, 22)):
            s.part(poly((41, 24), (36, 10), (44, 16), (46, 4), (50, 16), (56, 10), (50, 24)), Y, Ys)
        s.part(ell(45, 30, 10, 9), Y, Ys, Yh)
        s.part(poly((42, 33), (48, 33), (45, 38)), "#ff8a3a", "#c8501a")
        s.eye(40.5, 29, 2.6, 3.2, "#3a3a6a", a["blink"])
        s.eye(49.5, 29, 2.6, 3.2, "#3a3a6a", a["blink"])
        s.flat(ell(37, 33.5, 1.8, 1), "#ff9a7a")
        s.flat(ell(53, 33.5, 1.8, 1), "#ff9a7a")
    return s


# ------------------------------------------------------------------ 050 试炼之狮·王冠（格斗/钢）：站立的钢甲狮子武者
def d050(f):
    a = anim(f)
    LINE = "#1e1a20"
    s = Sprite(LINE)
    s.fit = .88
    T, Ts, Th = "#e0a85a", "#a8742a", "#ffd8a0"     # 狮毛
    M, Ms = "#8a4a1e", "#5a2c0e"                    # 鬃毛
    S_, Ss, Sh = "#c8d0dc", "#7a8498", "#ffffff"    # 钢甲
    G, Gs = "#ffd24a", "#c08a1a"
    s.lid_color = Ts
    b = a["breath"]
    # 尾巴
    with s.group(rot(a["sway"] * 8, 62, 66)):
        s.line("M60,68 C72,70 80,62 80,52", Ts, 3)
        s.part(ell(80, 50, 4, 5), M, Ms)
    # 远侧手臂
    s.part("M62,40 C70,44 72,54 70,60 L64,60 C64,54 62,48 58,46 Z", Ts, "#7a5420")
    s.part(ell(67, 62, 5.5, 5), Ss, "#4a5468")
    # 腿：钢护胫
    s.part(poly((36, 66), (44, 66), (44, 88), (34, 88)), S_, Ss, Sh)
    s.part(poly((50, 66), (58, 66), (60, 88), (50, 88)), Ss, "#4a5468")
    s.part(ell(38, 89, 6, 2.3), Ss, "#4a5468")
    s.part(ell(56, 89, 6, 2.3), Ss, "#4a5468")
    with s.group(f"translate(0 {-b * .8:.2f})"):
        s.part("M34,44 C32,36 40,32 48,32 C56,32 64,36 62,44 L60,66 C56,70 40,70 36,66 Z", T, Ts, Th)
        # 胸甲
        s.part("M36,42 C40,36 56,36 60,42 L58,58 C54,62 42,62 38,58 Z", S_, Ss, Sh)
        s.line("M48,38 L48,60", Ss, 1)
        s.flat(star(48, 48, 4, 1.8), G, LINE, .8)
        s.part(poly((36, 62), (60, 62), (60, 66), (36, 66)), G, Gs)
    # 鬃毛 + 头
    with s.group(f"translate(0 {-b * 1.2:.2f})"):
        for i in range(10):
            ang = i * 36 + 18
            x = 48 + math.sin(math.radians(ang)) * 14
            y = 22 - math.cos(math.radians(ang)) * 13
            s.part(ell(x, y, 6, 6), M, Ms)
        s.part(ell(48, 22, 14, 13), M, Ms)
        # 耳朵
        s.part(ell(37, 12, 3.5, 3.5), T, Ts)
        s.part(ell(59, 12, 3.5, 3.5), T, Ts)
        s.part(ell(48, 24, 10, 10), T, Ts, Th)
        s.part(ell(48, 29, 6, 4), "#fff0d0", "#e0c898", line="none")
        s.flat(poly((46, 26.5), (50, 26.5), (48, 28.5)), LINE)
        s.eye(43.5, 22, 2.6, 3, "#c84a1a", a["blink"], lid=.4)
        s.eye(52.5, 22, 2.6, 3, "#c84a1a", a["blink"], lid=.4)
        s.line("M45.5,31 Q48,32.5 50.5,31")
        # 钢王冠
        s.part(poly((39, 14), (39, 6), (43, 10), (48, 2), (53, 10), (57, 6), (57, 14)), S_, Ss, Sh)
        s.flat(ell(48, 10, 1.6, 1.6), "#e83a3a", LINE, .7)
    # 近侧手臂：钢拳套举在胸前
    with s.group(rot(a["sway"] * 3, 34, 40)):
        s.part("M34,40 C26,44 24,52 28,58 L34,56 C32,52 34,48 38,46 Z", T, Ts, Th)
        s.part("M24,54 C24,48 34,48 36,54 C38,60 34,64 30,64 C26,64 24,60 24,54 Z", S_, Ss, Sh)
        for y in (54, 58):
            s.line(f"M26,{y} L34,{y}", Ss, 1)
    return s


# ------------------------------------------------------------------ 051 雾隐九尾（幽灵/灵能）：飘着的淡紫九尾狐
def d051(f):
    a = anim(f)
    LINE = "#24183a"
    s = Sprite(LINE)
    s.fit = .9
    P, Ps, Ph = "#e8dcff", "#a898d8", "#ffffff"
    V, Vs = "#9a7ae0", "#6a4ab0"
    s.lid_color = Ps
    y0 = -math.sin(a["ph"]) * 2.5
    with s.group(f"translate(0 {y0:.2f})"):
        # 九条雾尾，扇形展开
        for i in range(9):
            ang = -70 + i * 17.5
            sw = a["sway"] * (4 + i % 3 * 2)
            with s.group(rot(ang + sw, 56, 58)):
                s.part("M54,60 C50,48 52,34 58,24 C62,32 64,44 60,56 Z", P if i % 2 else "#d4c4f8", Ps)
                s.part(ell(58, 26, 3.5, 4.5), V, Vs, line="none")
        # 身体（团着，脚下是雾）
        s.part("M28,62 C26,50 38,44 52,46 C66,48 72,56 70,66 C68,74 58,76 46,76 C34,76 30,70 28,62 Z", P, Ps, Ph)
        for x in (36, 50, 62):
            s.part(ell(x, 74, 5, 3.5), P, Ps)
        # 头
        for x0, flip in ((32, -1), (52, 1)):
            s.part(poly((x0 - 6, 30), (x0 + flip * 3, 10), (x0 + 6, 28)), P, Ps, Ph)
            s.flat(poly((x0 - 3, 28), (x0 + flip * 2.5, 16), (x0 + 3, 27)), V)
        s.part("M28,40 C28,30 34,26 42,26 C50,26 56,30 56,40 C56,48 50,52 42,52 C34,52 28,48 28,40 Z", P, Ps, Ph)
        # 额头紫色印记
        s.flat(poly((42, 30), (44, 33), (42, 36), (40, 33)), V, LINE, .7)
        s.eye(36.5, 40, 3, 3.6, "#6a4ab0", a["blink"], lid=.3)
        s.eye(47.5, 40, 3, 3.6, "#6a4ab0", a["blink"], lid=.3)
        s.flat(ell(42, 46, 1.8, 1.3), LINE)
        s.line("M39.5,48.5 Q42,50 44.5,48.5")
        for x in (32, 52):
            s.line(f"M{x - 2},{45} L{x + 2},{46}", V, .9)
    # 脚下的雾
    for i in range(4):
        t = (a["f"] / 24 + i / 4) % 1
        x = 20 + i * 18 + t * 6
        s.flat(ell(x, 86 - t * 2, 7 - t * 2, 2.5), "#e8e0ff" if i % 2 else "#d4c8f4")
    return s


# ------------------------------------------------------------------ 052 奈尔斯始祖·源（龙/灵能）：带光环的古龙
def d052(f):
    a = anim(f)
    LINE = "#140e2a"
    s = Sprite(LINE)
    s.fit = .84
    D, Ds, Dh = "#5a4ab8", "#30247a", "#8a7ae8"
    W, Ws = "#f0e8d8", "#c0b49a"
    C, Cs = "#7af0ff", "#2aa8d0"   # 水晶
    G = "#ffe07a"
    s.lid_color = Ds
    b = a["breath"]
    fl = a["flap"]
    # 身后的光环
    ring_r = 24 + math.sin(a["ph"]) * .8
    s.flat(ell(44, 30, ring_r, ring_r), "none", LINE, 3.2)
    s.flat(ell(44, 30, ring_r, ring_r), "none", G, 1.8)
    for i in range(6):
        ang = a["ph"] * .5 + i * math.pi / 3
        s.flat(star(44 + math.cos(ang) * ring_r, 30 + math.sin(ang) * ring_r, 2.4, 1, 4), "#fffbe0", LINE, .6)
    # 远侧翅膀
    with s.group(rot(-fl * 8 - 6, 58, 44)):
        s.part("M58,44 C66,28 78,16 92,14 L86,24 L92,28 L84,34 L88,40 L74,44 Z", Ds, "#1a1450")
    # 尾巴
    with s.group(rot(a["sway"] * 6, 64, 72)):
        s.part("M60,70 C74,70 84,78 90,88 C84,86 76,84 66,80 Z", D, Ds, Dh)
        s.part(poly((86, 86), (94, 82), (92, 90)), C, Cs)
    s.part(LEG(36, 62, 89, 7), Ds, "#1a1450")
    s.part(HIND(68, 58, 89), Ds, "#1a1450")
    with s.group(f"translate(0 {-b * .8:.2f})"):
        s.part("M28,58 C28,46 40,40 54,42 C68,44 74,52 72,62 C70,72 60,76 48,76 C36,76 28,70 28,58 Z", D, Ds, Dh)
        s.part("M34,58 C38,50 52,50 58,58 C58,68 52,72 46,72 C40,72 34,66 34,58 Z", W, Ws, line="none")
        for y in (58, 63, 68):
            s.line(f"M38,{y} L56,{y}", Ws, 1)
        # 背上水晶
        for x, h in ((50, 9), (58, 12), (66, 8)):
            s.part(poly((x - 3, 45), (x, 45 - h), (x + 3, 45)), C, Cs)
    s.part(LEG(31, 58, 88, 8), D, Ds, Dh)
    s.part(ell(30, 89, 5, 2.2), W, Ws)
    s.part(HIND(63, 54, 88), D, Ds, Dh)
    s.part(ell(64, 89, 5, 2.2), W, Ws)
    # 近侧翅膀
    with s.group(rot(fl * 8 + 6, 44, 44)):
        s.part("M44,44 C36,28 24,16 8,12 L14,22 L6,26 L14,32 L8,38 L22,42 C30,48 38,50 44,50 Z", D, Ds, Dh)
        s.part("M8,12 L14,22 L6,26 L14,32 L8,38 L12,38 C14,30 12,22 8,12 Z", C, Cs, line="none")
        for x, y in ((14, 24), (16, 32), (22, 38)):
            s.line(f"M{x},{y} L{x + 16},{y + 8}", Ds, 1)
    with s.group(f"translate(0 {-b * 1.3:.2f})"):
        # 角
        for side in (-1, 1):
            s.part(f"M{44 + side * 6},18 C{44 + side * 10},10 {44 + side * 12},4 {44 + side * 10},-2 C{44 + side * 16},4 {44 + side * 16},14 {44 + side * 10},22 Z", W, Ws)
        s.part("M32,26 C32,16 38,12 44,12 C50,12 56,16 56,26 C56,34 52,40 44,40 C36,40 32,34 32,26 Z", D, Ds, Dh)
        s.part(ell(44, 34, 6.5, 4.5), W, Ws, line="none")
        s.flat(ell(42, 32.5, .9, .7), LINE)
        s.flat(ell(46, 32.5, .9, .7), LINE)
        # 额头水晶
        s.flat(poly((44, 15), (46.5, 19), (44, 23), (41.5, 19)), C, LINE, .8)
        s.flat(ell(43.3, 18, .7, 1.2), "#ffffff")
        s.eye(39, 26, 3, 3.6, "#2aa8d0", a["blink"], lid=.35)
        s.eye(49, 26, 3, 3.6, "#2aa8d0", a["blink"], lid=.35)
        s.line("M41.5,37 Q44,38.5 46.5,37")
    return s


# ------------------------------------------------------------------ 053 幻·星屑（妖精/灵能）：拖着缎带尾巴的小星星
def d053(f):
    a = anim(f)
    LINE = "#3a1a40"
    s = Sprite(LINE)
    Y, Ys, Yh = "#fff08a", "#e8b440", "#ffffff"
    P, Ps = "#ff9ad8", "#d0509a"
    s.lid_color = Ys
    y0 = 46 - math.sin(a["ph"]) * 4
    spin = math.sin(a["ph"]) * 8
    # 两条缎带尾巴，在身后波浪一样飘
    for side in (-1, 1):
        pts = [(48 + side * (4 + t * 14) + math.sin(a["ph"] + t * 6 + side) * 5 * t, y0 + 12 + t * 30) for t in [k / 8 for k in range(9)]]
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts[1:])
        s.line(d, LINE, 6)
        s.line(d, P if side < 0 else "#a8e8ff", 4)
        ex, ey = pts[-1]
        s.flat(star(ex, ey + 1, 3.6, 1.6), "#ffffff", LINE, .8)
    # 小星星绕圈
    for i in range(3):
        ang = a["ph"] + i * 2.1
        s.flat(star(48 + math.cos(ang) * 30, y0 + math.sin(ang) * 10, 2.6, 1.1), "#ffffff", LINE, .6)
    with s.group(rot(spin, 48, y0)):
        s.part(star(48, y0, 24, 12), Y, Ys, Yh)
        # 星星尖上的颜色
        for i in range(5):
            ang = math.radians(i * 72)
            s.flat(ell(48 + math.sin(ang) * 19, y0 - math.cos(ang) * 19, 2.2, 2.2), P)
    s.eye(42.5, y0 - 1, 3.4, 4.2, "#d0509a", a["blink"])
    s.eye(53.5, y0 - 1, 3.4, 4.2, "#d0509a", a["blink"])
    s.flat(ell(38, y0 + 5, 2.5, 1.4), "#ff9ab0")
    s.flat(ell(58, y0 + 5, 2.5, 1.4), "#ff9ab0")
    s.line(f"M45.5,{y0 + 6} Q48,{y0 + 8.5} 50.5,{y0 + 6}")
    return s


# ------------------------------------------------------------------ 054 幻·芽之子（草/普通）：浮着的芽宝宝
def d054(f):
    a = anim(f)
    LINE = "#1e3018"
    s = Sprite(LINE)
    G, Gs, Gh = "#9ae070", "#5aa83a", "#d8ffb0"
    L, Ls = "#3fae4a", "#1f7a34"
    C, Cs = "#fff8e0", "#e8d4a8"
    s.lid_color = Gs
    y0 = -math.sin(a["ph"]) * 3
    # 地上的影子和小花（不跟着浮动）
    s.flat(ell(48, 88, 14 - y0, 2.5), "#b8c8a0")
    with s.group(f"translate(0 {y0:.2f})"):
        # 叶子头发（三片大叶）
        with s.group(rot(a["sway"] * 6, 48, 30)):
            leaf(s, 48, 30, 26, 10, -40, L, Ls)
            leaf(s, 48, 30, 26, 10, 40, L, Ls)
            leaf(s, 48, 30, 22, 8, 0, "#5fc04a", Ls)
            s.flat(ell(48, 6, 3, 3), "#ffb0d0", LINE, .8)
            s.flat(ell(48, 6, 1.2, 1.2), "#ffe066")
        # 小身子
        s.part("M38,62 C36,70 40,78 48,78 C56,78 60,70 58,62 Z", G, Gs, Gh)
        s.part(ell(48, 70, 5, 5), C, Cs, line="none")
        # 根须一样的小脚
        for x in (43, 53):
            s.line(f"M{x},77 C{x},82 {x - 2},84 {x - 1},86", Gs, 2)
        # 叶子小手
        leaf(s, 38, 64, 12, 5, -110, "#5fc04a", Ls, False)
        leaf(s, 58, 64, 12, 5, 110, "#5fc04a", Ls, False)
        # 大圆头
        s.part(ell(48, 44, 17, 15), G, Gs, Gh)
        s.eye(41, 44, 4.4, 5.4, "#2f7a24", a["blink"])
        s.eye(55, 44, 4.4, 5.4, "#2f7a24", a["blink"])
        s.flat(ell(35, 51, 3, 1.6), "#ffa0b0")
        s.flat(ell(61, 51, 3, 1.6), "#ffa0b0")
        s.line("M45.5,53 Q48,55.5 50.5,53")
    return s


# ------------------------------------------------------------------ 055 幻·时之沙（大地/灵能）：浮着的沙漏精
def d055(f):
    a = anim(f)
    LINE = "#2a1a10"
    s = Sprite(LINE)
    s.fit = .95
    GL, GLs = "#e8f6ff", "#a8c8dc"   # 玻璃
    SA, SAs = "#f0c060", "#c08a2a"   # 沙
    WD, WDs, WDh = "#8a4a8a", "#5a2a5a", "#c07ac0"   # 紫木框
    G = "#ffe07a"
    s.lid_color = WDs
    y0 = -math.sin(a["ph"]) * 2.5
    t = a["f"] / 24
    s.flat(ell(48, 89, 16, 2.5), "#d8c8a8")
    with s.group(f"translate(0 {y0:.2f})"):
        # 绕身的星轨环（后半）
        s.flat("M10,50 A38,10 0 0,1 86,50", "none", LINE, 3)
        s.flat("M10,50 A38,10 0 0,1 86,50", "none", G, 1.6)
        # 玻璃
        s.part("M32,18 L64,18 C64,30 52,38 50,46 C52,54 64,62 64,76 L32,76 C32,62 44,54 46,46 C44,38 32,30 32,18 Z", GL, GLs)
        # 上半沙子越来越少，下半越来越多
        top = 22 + t * 12
        s.flat(f"M{36 + (top - 22) * .5},{top} L{60 - (top - 22) * .5},{top} C{58},{36} {50},{40} 48,46 C46,40 {38},{36} {36 + (top - 22) * .5},{top} Z", SA)
        h = 6 + t * 10
        s.flat(f"M34,74 C38,{74 - h} 44,{72 - h} 48,{70 - h} C52,{72 - h} 58,{74 - h} 62,74 Z", SA)
        s.line(f"M48,46 L48,{70 - h}", SAs, 1)
        s.flat(ell(38, 24, 2, 3), "#ffffff")
        # 上下木框
        s.part("M26,12 L70,12 L70,18 L26,18 Z", WD, WDs, WDh)
        s.part("M26,76 L70,76 L70,82 L26,82 Z", WD, WDs, WDh)
        for x in (28, 68):
            s.part(f"M{x - 1.5},18 L{x + 1.5},18 L{x + 1.5},76 L{x - 1.5},76 Z", WD, WDs)
        # 顶上的宝石
        s.flat(poly((48, 4), (52, 8), (48, 12), (44, 8)), "#7af0ff", LINE, .8)
        # 脸在上半玻璃里
        s.eye(42, 28, 3, 3.6, "#5a2a5a", a["blink"])
        s.eye(54, 28, 3, 3.6, "#5a2a5a", a["blink"])
        s.line("M46,33.5 Q48,35 50,33.5")
        # 星轨环（前半）
        s.flat("M10,50 A38,10 0 0,0 86,50", "none", LINE, 3)
        s.flat("M10,50 A38,10 0 0,0 86,50", "none", G, 1.6)
        ang = a["ph"]
        s.flat(star(48 + math.cos(ang) * 38, 50 + math.sin(ang) * 10, 3, 1.2), "#fffbe0", LINE, .7)
    return s


SPECIES = {"d048": d048, "d049": d049, "d050": d050, "d051": d051, "d052": d052, "d053": d053, "d054": d054, "d055": d055}
