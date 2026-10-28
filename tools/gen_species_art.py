"""716 只幻兽的立绘：按图鉴数据（data/dex/species.json）拼部件，交给 gen_monsters 的光照渲染器画。

每条进化线共用一套设计（身体结构、耳朵、尾巴、花纹、配色、属性饰物），由线号做随机种子；
进化后头身比变小、身体变大、长出角和更多饰物，配色加深，眼神变凶。
每只输出：
  assets/sprites/dex/<key>_front.png  正面 24 帧待机动画横排（每帧 72x72）
  assets/sprites/dex/<key>_back.png   背面 96x96
坐标单位和 gen_monsters 一样：原点在脚底中心，y 向上为负。

python3 tools/gen_species_art.py            # 全部
python3 tools/gen_species_art.py d101 d102  # 只画指定的
"""
import colorsys
import json
import math
import os
import random
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image  # noqa: E402

import gen_monsters as gm  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "sprites", "dex")
FRAMES = 24
TYPE_COLOR = {
    "普通": "#c9b48a", "火": "#e8642c", "水": "#3f8fe0", "草": "#5fb04a", "电": "#f2c72e", "冰": "#8fd6e8",
    "格斗": "#c0583a", "毒": "#9a4fc0", "大地": "#c99a52", "飞行": "#8fa6e8", "灵能": "#e86a9a", "虫": "#9ab83a",
    "岩石": "#a8956a", "幽灵": "#6a5aa8", "龙": "#5a6ad8", "恶": "#4a4250", "钢": "#9aa6b8", "妖精": "#f0a0c8",
}
IRIS = {
    "普通": "#5a3a1a", "火": "#c03a10", "水": "#1b4f9a", "草": "#2f7a24", "电": "#8a5a00", "冰": "#2a7aa0",
    "格斗": "#7a1a10", "毒": "#7a1a8a", "大地": "#6a4210", "飞行": "#2a3f8a", "灵能": "#c0207a", "虫": "#4a6a10",
    "岩石": "#5a4a2a", "幽灵": "#d03a6a", "龙": "#d0a020", "恶": "#d03030", "钢": "#2a4a7a", "妖精": "#c0408a",
}


# ------------------------------------------------------------------ 颜色
def hx(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in c)


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hsv_shift(h, dh=0.0, ds=0.0, dv=0.0, mul_v=1.0):
    r, g, b = (x / 255 for x in rgb(h))
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    hh = (hh + dh) % 1.0
    ss = max(0.0, min(1.0, ss + ds))
    vv = max(0.0, min(1.0, vv * mul_v + dv))
    return hx(tuple(x * 255 for x in colorsys.hsv_to_rgb(hh, ss, vv)))


def mix(a, b, t):
    ca, cb = rgb(a), rgb(b)
    return hx(tuple(ca[i] + (cb[i] - ca[i]) * t for i in range(3)))


# ------------------------------------------------------------------ 图元小工具
def E(x, y, rx, ry, c, rot=0.0, f=""):
    return ("e" + f, x, y, rx, ry, c, rot)


def P(pts, c, f=""):
    return ("p" + f, [tuple(p) for p in pts], c)


def L(x1, y1, x2, y2, w, c, f=""):
    return ("l" + f, x1, y1, x2, y2, w, c)


def rot_about(pts, cx, cy, a):
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def mirror(prims):
    """左右镜像（用于对称部件）"""
    out = []
    for p in prims:
        k = p[0]
        if k[0] == "e":
            out.append((k, -p[1], p[2], p[3], p[4], p[5], -p[6]))
        elif k[0] == "p":
            out.append((k, [(-x, y) for x, y in p[1]], p[2]))
        else:
            out.append((k, -p[1], p[2], -p[3], p[4], p[5], p[6]))
    return out


def both(prims):
    return prims + mirror(prims)


def flame(x, y, size, ang=0.0):
    """一团火：外焰橙、内焰黄"""
    s = size
    outer = rot_about([(x - s * .55, y), (x - s * .7, y - s * .9), (x - s * .25, y - s * .6), (x, y - s * 1.6),
                       (x + s * .3, y - s * .7), (x + s * .7, y - s * 1.0), (x + s * .55, y)], x, y, ang)
    inner = rot_about([(x - s * .3, y - s * .1), (x - s * .15, y - s * .7), (x, y - s * 1.0), (x + s * .2, y - s * .6),
                       (x + s * .3, y - s * .1)], x, y, ang)
    return [P(outer, "#ff8a2a"), P(inner, "#ffe066")]


def leaf(x, y, length, ang, c="#4caf3a"):
    cx, cy = x + math.sin(ang) * length / 2, y - math.cos(ang) * length / 2
    return [E(cx, cy, length * 0.22, length / 2, c, ang), L(x, y, cx + math.sin(ang) * length * 0.35,
                                                             cy - math.cos(ang) * length * 0.35, 0.6, "#2a7429")]


def bolt(x, y, s, ang=0.0):
    pts = [(0, 0), (s * .5, -s * .9), (s * .15, -s * .9), (s * .65, -s * 1.8), (-s * .1, -s * .7),
           (s * .25, -s * .7), (-s * .2, 0)]
    return [P(rot_about([(x + px, y + py) for px, py in pts], x, y, ang), "#ffd83a")]


def crystal(x, y, s, ang=0.0, c="#bfefff"):
    pts = [(-s * .35, 0), (-s * .25, -s), (0, -s * 1.5), (s * .25, -s), (s * .35, 0)]
    return [P(rot_about([(x + px, y + py) for px, py in pts], x, y, ang), c)]


def horn(x, y, s, ang, c="#f2ead8"):
    pts = [(-s * .3, 0), (s * .05, -s * 1.4), (s * .3, 0)]
    return [P(rot_about([(x + px, y + py) for px, py in pts], x, y, ang), c)]


def spikes(x0, x1, y_of, n, h, c):
    out = []
    for i in range(n):
        t = (i + 0.5) / n
        x = x0 + (x1 - x0) * t
        y = y_of(x)
        out.append(P([(x - h * .45, y + 1), (x, y - h), (x + h * .45, y + 1)], c))
    return out


# ------------------------------------------------------------------ 一条进化线的设计
BODY_EARS = {
    "四足": ["point", "round", "long", "point", "tuft", "droop"], "人形": ["point", "round", "none", "tuft"],
    "两栖": ["none", "round", "frill"], "鸟形": ["crest", "tuft", "none"], "飞膜": ["point", "long"],
    "植物": ["leaf", "petal"], "浮游": ["none", "point", "wisp"], "龙形": ["frill", "point", "none"],
    "蛇形": ["frill", "none", "hood"], "鱼形": ["fin"], "虫形": ["antenna"], "蝶形": ["antenna"], "甲壳": ["stalk"],
}
BODY_TAILS = {
    "四足": ["fluff", "thin", "curl", "fluff", "club", "fan"], "人形": ["none", "thin", "fluff"],
    "两栖": ["none", "thin"], "鸟形": ["fan", "plume"], "飞膜": ["thin", "none"], "植物": ["none"],
    "浮游": ["wisp", "none", "tendrils"], "龙形": ["thin", "club", "fin"], "蛇形": ["coil"], "鱼形": ["fin"],
    "虫形": ["stinger", "none"], "蝶形": ["none"], "甲壳": ["none", "fan"],
}


class Design:
    def __init__(self, line, species):
        base = species[0]
        self.rng = random.Random(1000 + line)
        r = self.rng
        self.types = base["types"]
        self.body = base["model"]["body"]
        self.stages = len(species)
        self.legend = base["kind"] == "legend"
        t1 = self.types[0]
        t2 = self.types[1] if len(self.types) > 1 else None
        main = hsv_shift(TYPE_COLOR[t1], dh=r.uniform(-0.05, 0.05), ds=r.uniform(-0.15, 0.1), mul_v=r.uniform(0.9, 1.08))
        if r.random() < 0.18:  # 少数用不寻常的主色（像宝可梦里的异色感）
            main = hsv_shift(main, dh=r.choice([-0.12, 0.1, 0.5]), ds=-0.1)
        self.a = main
        if t2 and r.random() < 0.6:
            self.b = mix(TYPE_COLOR[t2], "#ffffff", 0.45)
        else:
            self.b = r.choice(["#fff4dc", "#f4f0ff", "#ffe6c8", mix(main, "#ffffff", 0.65), "#f0f7e8"])
        self.d = hsv_shift(main, dh=0.02, ds=0.1, mul_v=0.62)
        self.c = TYPE_COLOR[t2] if t2 else hsv_shift(main, dh=r.choice([0.08, -0.08, 0.5]), ds=0.1)
        self.iris = IRIS[t2 or t1] if r.random() < 0.5 else IRIS[t1]
        self.ear = r.choice(BODY_EARS.get(self.body, ["none"]))
        self.tail = r.choice(BODY_TAILS.get(self.body, ["none"]))
        self.pattern = r.choice(["none", "none", "spots", "stripes", "mask", "socks", "crown"])
        self.belly = r.random() < 0.7
        self.snout = r.random() < 0.6
        self.cheek = r.random() < 0.35
        self.mouth = r.choice(["cat", "smile", "o", "wide", "cat"])
        self.fat = r.uniform(0.9, 1.15)
        self.tall = r.uniform(0.9, 1.1)
        self.hornish = r.random() < 0.5 or "龙" in self.types or "岩石" in self.types
        self.wings = "飞行" in self.types or (self.body == "龙形" and r.random() < 0.7)
        self.gloss = 1.0 if t1 in ("水", "冰", "钢") else (0.6 if t1 in ("毒", "妖精") else 0.0)


def stage_k(d, s):
    if d.legend:
        return 1.0
    if d.stages == 1:
        return 0.55
    return s / (d.stages - 1)


# ------------------------------------------------------------------ 头部（大多数身体共用）
def head(d, k, hxp, hy, rx, ry, anim):
    """返回 (图元, 脸部信息)。头在 (hxp, hy)，半径 rx, ry"""
    a, b, dk, c = "a", "b", "d", d.c
    prims = []
    sway = anim["sway"]
    # 耳朵（画在头后面）
    ear = d.ear
    el = 1.0 + k * 0.4
    if ear == "point":
        prims += both([P([(hxp + rx * .35, hy - ry * .55), (hxp + rx * .95 + 1 * k, hy - ry - 6 * el + sway * 2),
                          (hxp + rx * .85, hy - ry * .2)], a),
                       P([(hxp + rx * .5, hy - ry * .6), (hxp + rx * .88, hy - ry - 3.8 * el), (hxp + rx * .78, hy - ry * .35)], dk, "!")])
    elif ear == "round":
        prims += both([E(hxp + rx * .72, hy - ry * .78, rx * .38, rx * .38, a), E(hxp + rx * .72, hy - ry * .78, rx * .2, rx * .2, b, 0, "!")])
    elif ear == "long":
        prims += both([E(hxp + rx * .45, hy - ry - 4.5 * el, 2.4, 6.5 * el, a, 0.2 + sway * 0.4),
                       E(hxp + rx * .45, hy - ry - 4.5 * el, 1.1, 4.5 * el, b, 0.2 + sway * 0.4, "!")])
    elif ear == "droop":
        prims += both([E(hxp + rx * .95, hy - ry * .1, 2.6, 6.0, dk, -0.35 + sway * 0.3)])
    elif ear == "tuft":
        prims += [P([(hxp - 3, hy - ry * .85), (hxp - 1 + sway * 2, hy - ry - 5 * el), (hxp + 1, hy - ry * .9),
                     (hxp + 3 + sway * 2, hy - ry - 4 * el), (hxp + 4, hy - ry * .8)], dk)]
    elif ear == "crest":
        prims += [P([(hxp - 2, hy - ry * .8), (hxp - 4 + sway * 2, hy - ry - 7 * el), (hxp + 1, hy - ry * .9),
                     (hxp + 3 + sway * 2, hy - ry - 6 * el), (hxp + 3, hy - ry * .7)], c)]
    elif ear == "frill":
        # 三根放射状的鳍刺，比整块板子更像宝可梦的头鳍
        fr = []
        for i, ang in enumerate((-0.55, 0.0, 0.55)):
            ln = (4.5 + (1.5 if i == 1 else 0)) * el
            bx_, by_ = hxp + rx * .75, hy + i * ry * .15 - ry * .2
            fr.append(P([(bx_, by_ - 1.6), (bx_ + math.cos(ang) * ln, by_ + math.sin(ang) * ln), (bx_, by_ + 1.6)], c))
        prims += both(fr)
    elif ear == "fin":
        prims += both([P([(hxp + rx * .6, hy - ry * .2), (hxp + rx + 4.5 * el, hy - ry * .9), (hxp + rx * .8, hy + ry * .4)], c)])
    elif ear == "antenna":
        prims += both([L(hxp + rx * .3, hy - ry * .8, hxp + rx * .8 + sway * 2, hy - ry - 6 * el, 1.0, dk),
                       E(hxp + rx * .8 + sway * 2, hy - ry - 6 * el, 1.6, 1.6, c)])
    elif ear == "stalk":
        pass  # 甲壳的眼柄在 crust 里画
    elif ear == "leaf":
        prims += leaf(hxp - 1, hy - ry * .85, 8 * el, -0.5 + sway * 0.3, d.c if "草" not in d.types else "#4caf3a")
        prims += leaf(hxp + 1, hy - ry * .85, 10 * el, 0.4 + sway * 0.3, "#5fc04a")
    elif ear == "petal":
        for i in range(5):
            ang = -1.2 + i * 0.6
            prims.append(E(hxp + math.sin(ang) * (rx + 1.5), hy - math.cos(ang) * (ry + 1.5), 3.2, 4.5, d.c, ang))
    elif ear == "wisp":
        prims += [P([(hxp - rx * .6, hy - ry * .6), (hxp - rx * .2 + sway * 3, hy - ry - 7 * el), (hxp + rx * .2, hy - ry * .8)], "d")]
    elif ear == "hood":
        prims += [E(hxp, hy + 1, rx * 1.55, ry * 1.25, c)]
    # 角
    if d.hornish and k >= 0.5:
        hs = 3.5 + 4 * k
        if d.legend or "龙" in d.types:
            prims += horn(hxp - rx * .45, hy - ry * .7, hs, -0.45) + horn(hxp + rx * .45, hy - ry * .7, hs, 0.45)
        else:
            prims += horn(hxp, hy - ry * .85, hs * 0.9, 0.05)
    # 头
    prims.append(E(hxp, hy, rx, ry, a))
    # 花纹
    if d.pattern == "mask":
        prims.append(E(hxp, hy - ry * .1, rx * .92, ry * .32, dk, 0, "!"))
    elif d.pattern == "crown":
        prims.append(E(hxp, hy - ry * .62, rx * .55, ry * .3, "d"))
    elif d.pattern == "stripes":
        prims += [P([(hxp - 1.5, hy - ry * .98), (hxp, hy - ry * .45), (hxp + 1.5, hy - ry * .98)], dk)]
    # 口鼻
    if d.snout and d.body in ("四足", "人形", "龙形", "飞膜"):
        prims.append(E(hxp, hy + ry * .38, rx * .5, ry * .36, b, 0, "!"))
        prims.append(E(hxp, hy + ry * .2, 1.3, 0.9, "#2a1a1a", 0, "!"))
    # 头顶属性饰物
    prims += head_accessory(d, k, hxp, hy, rx, ry, anim)
    # 背面的花纹
    prims.append(E(hxp, hy - ry * .2, rx * .45, ry * .35, "d", 0, "?"))
    # 脸
    es = 1.35 - 0.45 * k if not d.legend else 0.95
    face = {"eyes": [(hxp - rx * .42, hy - ry * .05), (hxp + rx * .42, hy - ry * .05)], "eye_size": es * rx / 9.5,
            "iris": d.iris, "mouth": (d.mouth if k < 0.8 else "cat", hxp, hy + ry * (.5 if d.snout else .42))}
    if d.cheek or "电" in d.types:
        face["blush"] = [(hxp - rx * .7, hy + ry * .35), (hxp + rx * .7, hy + ry * .35)]
    if k >= 0.75 and not d.legend:
        # 眉毛：进化完全后眼神变凶
        prims += both([P([(hxp + rx * .15, hy - ry * .42), (hxp + rx * .72, hy - ry * .62), (hxp + rx * .7, hy - ry * .45)], "#2a1a1a", "!")])
    return prims, face


def head_accessory(d, k, hxp, hy, rx, ry, anim):
    t = d.types[0]
    top = hy - ry
    out = []
    if t == "火" and d.tail not in ("fluff", "thin", "fan") or (t == "火" and k > 0.9):
        out += flame(hxp, top + 2, 3 + 3 * k, anim["sway"] * 0.5)
    elif t == "冰" and k > 0.3:
        out += crystal(hxp - 2, top + 1.5, 3 + 2 * k, -0.3) + crystal(hxp + 2, top + 1.5, 3.5 + 2 * k, 0.3)
    elif t == "灵能" or t == "妖精":
        out.append(E(hxp, hy - ry * .6, 1.8 + k, 1.6 + k, "#ff5aa0" if t == "灵能" else "#ffe066", 0, "!"))
    elif t == "钢" and k > 0.3:
        out.append(E(hxp, top + 1, rx * .7, 2.2, "#c8d0dc"))
    elif t == "岩石" and k > 0.3:
        out += [P([(hxp - 4, top + 2), (hxp - 2, top - 3 - 2 * k), (hxp + 2, top - 2 - k), (hxp + 4, top + 2)], "#8a7a5a")]
    elif t == "草" and d.ear not in ("leaf", "petal"):
        out += leaf(hxp + 1, top + 1.5, 6 + 4 * k, 0.3 + anim["sway"] * 0.3)
    return out


# ------------------------------------------------------------------ 尾巴
def tail(d, k, ax, ay, anim, scale=1.0):
    """尾巴根在 (ax, ay)，向右后方伸出，随动画摆动"""
    sw = anim["sway"] * 0.5
    L_ = (7 + 6 * k) * scale
    t = d.tail
    t1 = d.types[0]
    tipx, tipy = ax + L_ * 0.8, ay - L_ * 0.9
    tipx, tipy = rot_about([(tipx, tipy)], ax, ay, sw)[0]
    out = []
    if t == "fluff":
        mx, my = (ax + tipx) / 2, (ay + tipy) / 2
        ang = math.atan2(tipx - ax, -(tipy - ay))
        out += [E(mx, my, 4.5 * scale + k, L_ * .62, "a", ang), E(tipx - math.sin(ang) * 2, tipy + math.cos(ang) * 2, 3 * scale, 3.8 * scale, "b", ang)]
    elif t in ("thin", "club"):
        out += [L(ax, ay, tipx, tipy, 1.8 * scale, "a")]
        if t == "club":
            out.append(E(tipx, tipy, 3.5 * scale + k, 3.5 * scale + k, "d"))
    elif t == "curl":
        out += [E(ax + 4 * scale, ay - 5 * scale, 4.5 * scale, 4.5 * scale, "a"), E(ax + 5.5 * scale, ay - 8.5 * scale, 2.8 * scale, 2.8 * scale, "b")]
    elif t == "fan":
        for i in range(3 + int(k * 2)):
            ang = 0.2 + i * 0.35 + sw
            out.append(E(ax + math.sin(ang) * L_ * .5, ay - math.cos(ang) * L_ * .5, 2.4 * scale, L_ * .55, "a" if i % 2 else "d", ang))
    elif t == "plume":
        out += [E(ax + 5, ay - 6, 3, 8 + 3 * k, "d", 0.6 + sw), E(ax + 8, ay - 3, 2.5, 7 + 3 * k, "c" if False else "a", 1.0 + sw)]
    elif t == "fin":
        out += [P(rot_about([(ax, ay + 2), (ax + L_, ay - L_ * .8), (ax + L_ * .5, ay), (ax + L_, ay + L_ * .5)], ax, ay, sw), "d")]
    elif t == "stinger":
        out += [P(rot_about([(ax, ay), (ax + 6 * scale, ay - 2), (ax + 10 * scale, ay - 6 * scale), (ax + 5, ay + 1)], ax, ay, sw), "d")]
    elif t == "wisp":
        out += [P([(ax - 6, ay - 4), (ax + 2 + sw * 6, ay + 6), (ax + 5, ay - 3)], "a")]
    elif t == "tendrils":
        for i in range(4):
            x = ax - 9 + i * 6
            out.append(L(x, ay - 3, x + math.sin(anim["ph"] + i) * 2.5, ay + 5, 1.8, "d"))
    # 尾巴上的属性饰物
    if t in ("thin", "fluff", "fan", "club") and k > 0.2:
        if t1 == "火":
            out += flame(tipx, tipy + 1.5, 3 + 2.5 * k, sw)
        elif t1 == "电":
            out += bolt(tipx - 1, tipy + 2, 3.5 + 2 * k, 0.4 + sw)
        elif t1 == "草":
            out += leaf(tipx, tipy + 1, 6 + 3 * k, 0.6 + sw)
        elif t1 == "冰":
            out += crystal(tipx, tipy + 1.5, 3 + 2 * k, 0.5)
        elif t1 == "水":
            out.append(E(tipx, tipy, 3.5, 2.2, "#bfe8ff", 0.6))
    return out


def wings(d, k, cx, cy, span, anim, membrane=False):
    """一对翅膀，肩膀在 (±cx, cy)"""
    fl = anim["flap"] * 0.35
    s = span * (0.8 + 0.5 * k)
    if membrane:
        w = [P(rot_about([(cx, cy), (cx + s * .6, cy - s * .9), (cx + s, cy - s * .7), (cx + s * .85, cy - s * .2),
                          (cx + s * .65, cy + s * .05), (cx + s * .4, cy - s * .1), (cx + s * .2, cy + s * .2)], cx, cy, -fl), "d"),
             L(cx, cy, cx + s * .6, cy - s * .9, 1.0, "a")]
    else:
        w = [E(cx + s * .45, cy - s * .35, s * .32, s * .6, "d", 0.9 - fl),
             E(cx + s * .55, cy - s * .45, s * .2, s * .45, "a", 0.9 - fl)]
        if k > 0.6:
            w.append(E(cx + s * .75, cy - s * .65, s * .12, s * .3, "b", 0.9 - fl))
    return both(w)


def body_markings(d, k, bx, by, rx, ry):
    out = []
    if d.belly:
        out.append(E(bx, by + ry * .15, rx * .62, ry * .62, "b", 0, "!"))
    if d.pattern == "spots":
        r = random.Random(hash((d.a, d.body)) & 0xffff)
        for _ in range(3 + int(k * 3)):
            ang = r.uniform(0, 6.28)
            rr = r.uniform(0.3, 0.75)
            out.append(E(bx + math.cos(ang) * rx * rr, by + math.sin(ang) * ry * rr, 1.6, 1.3, "d"))
    elif d.pattern == "stripes":
        for i in range(2 + int(k * 2)):
            y = by - ry * .55 + i * ry * .4
            w = rx * math.sqrt(max(0.0, 1 - ((y - by) / ry) ** 2)) * 0.9
            out.append(P([(bx - w, y - 1), (bx - w * .4, y), (bx - w, y + 1)], "d"))
            out.append(P([(bx + w, y - 1), (bx + w * .4, y), (bx + w, y + 1)], "d"))
    out.append(E(bx, by - ry * .3, rx * .5, ry * .4, "d", 0, "?"))
    return out


def back_accessory(d, k, bx, by, rx, ry):
    """背上的属性饰物：冰晶、岩块、钢板、背鳍"""
    t = d.types[-1]
    out = []
    if k < 0.3:
        return out
    n = 2 + int(k * 2)
    top = lambda x: by - ry * math.sqrt(max(0.0, 1 - ((x - bx) / rx) ** 2))  # noqa: E731
    if t == "冰":
        out += spikes(bx - rx * .6, bx + rx * .6, top, n, 4 + 3 * k, "#bfefff")
    elif t == "岩石":
        out += spikes(bx - rx * .6, bx + rx * .6, top, n, 3 + 2 * k, "#8a7a5a")
    elif t == "龙" or t == "恶":
        out += spikes(bx - rx * .5, bx + rx * .5, top, n, 3 + 2 * k, "d")
    elif t == "钢":
        out.append(E(bx, by - ry * .55, rx * .8, ry * .4, "#c8d0dc"))
    elif t == "毒":
        out += [E(bx - rx * .4, by - ry * .7, 2, 2, "#c06ae0"), E(bx + rx * .3, by - ry * .8, 2.5, 2.5, "#c06ae0")]
    return out


# ------------------------------------------------------------------ 各种身体结构
def quad(d, k, anim):
    b, br = anim["bob"], anim["breath"]
    hr = 9.5 * (1.0 - 0.18 * k) * d.fat
    brx, bry = (9 + 4 * k) * d.fat, (7 + 3 * k) * (1 + br)
    by = -bry - 1.5
    hy = by - bry * .55 - hr * .75 + b
    prims = []
    prims += tail(d, k, brx * .6, by + 1, anim)
    if d.wings:
        prims += wings(d, k, brx * .5, by - bry * .5, 12, anim, membrane=d.body == "龙形")
    prims += both([E(brx * .6, -1.6, 2.8 + k, 2.0, "d")])  # 后脚
    prims += back_accessory(d, k, 0, by, brx, bry)
    prims.append(E(0, by, brx, bry, "a"))
    prims += body_markings(d, k, 0, by, brx, bry)
    sock = "b" if d.pattern == "socks" else "a"
    prims += both([E(brx * .38, -2.2, 2.6 + k * .8, 3.2 + k, sock), E(brx * .38, -0.8, 2.2 + k * .6, 1.2, "d", 0, "!")])  # 前脚
    if k > 0.5 and d.rng.random() < 2:  # 颈部鬃毛
        if d.ear in ("point", "tuft", "round") and d.pattern != "mask":
            prims.append(E(0, hy + hr * .75, hr * .85, hr * .45, "b"))
    hp, face = head(d, k, 0, hy, hr, hr * .92, anim)
    return prims + hp, face


def biped(d, k, anim):
    b, br = anim["bob"], anim["breath"]
    hr = 8.5 * (1.0 - 0.15 * k)
    brx, bry = (8 + 3 * k) * d.fat, (9 + 5 * k) * d.tall * (1 + br)
    by = -bry - 4
    hy = by - bry - hr * .6 + b
    prims = []
    prims += tail(d, k, brx * .5, by + bry * .4, anim)
    if d.wings:
        prims += wings(d, k, brx * .4, by - bry * .6, 12, anim)
    prims += both([L(brx * .45, by + bry * .7, brx * .5, -2, 3.2 + k, "a"), E(brx * .55, -1.2, 3 + k * .6, 1.8, "d")])
    prims += back_accessory(d, k, 0, by, brx, bry)
    prims.append(E(0, by, brx, bry, "a"))
    prims += body_markings(d, k, 0, by, brx, bry)
    arm = anim["sway"] * 1.5
    band = "#e04a3a" if "格斗" in d.types else "a"
    prims += both([L(brx * .85, by - bry * .45, brx + 3 + arm, by + bry * .2, 3 + k, "a"),
                   E(brx + 3 + arm, by + bry * .25, 2.6 + k * .6, 2.6 + k * .6, band)])
    hp, face = head(d, k, 0, hy, hr, hr * .9, anim)
    return prims + hp, face


def bird(d, k, anim):
    b, br, fl = anim["bob"], anim["breath"], anim["flap"]
    r = (10 + 3 * k) * d.fat
    by = -r - 2.5
    prims = []
    prims += tail(d, k, r * .5, by + r * .4, anim)
    w = 7 + 6 * k
    prims += both([E(r * .85 + w * .3, by - 1 - fl * 2, w * .45, w, "d", 0.5 + fl * 0.25),
                   E(r * .85 + w * .3, by - 1 - fl * 2, w * .25, w * .7, "a", 0.5 + fl * 0.25)])
    prims += both([L(r * .3, by + r * .9, r * .35, -0.5, 1.6, "#f2a33a"), E(r * .38, -0.5, 2.2, 1, "#f2a33a")])
    prims.append(E(0, by, r, r * (1 + br), "a"))
    prims += body_markings(d, k, 0, by + r * .2, r * .8, r * .7)
    # 头和身体是一体的（小鸟），进化后头分出来
    if k >= 0.5:
        hr = 7.5
        hy = by - r * .75 + b
        hp, face = head(d, k, 0, hy, hr, hr * .9, anim)
        beak_y = hy + hr * .2
        prims += hp
    else:
        hp, face = head(d, k, 0, by - r * .25 + b, r * .9, r * .85, anim)
        prims += [p for p in hp if p[0] not in ("e",) or p[3] < r * .85]  # 头不再画一遍大椭圆
        face["eyes"] = [(-r * .36, by - r * .35 + b), (r * .36, by - r * .35 + b)]
        beak_y = by - r * .15 + b
        face["mouth"] = None
    prims.append(P([(-2.5, beak_y - 1), (2.5, beak_y - 1), (0, beak_y + 3)], "#f2a33a", "!"))
    face["mouth"] = None
    return prims, face


def fish(d, k, anim):
    b = anim["bob"] * 2 - 3
    rx, ry = (13 + 4 * k) * d.fat, (8 + 3 * k)
    by = -ry - 4 + b
    prims = []
    sw = anim["sway"]
    tx = rx * .85
    prims.append(P(rot_about([(tx - 2, by), (tx + 9 + 3 * k, by - 7 - 2 * k), (tx + 6, by), (tx + 9 + 3 * k, by + 7 + 2 * k)], tx, by, sw * .5), "d"))
    prims.append(P([(-3, by - ry * .8), (3 + sw * 2, by - ry - 6 - 3 * k), (7, by - ry * .7)], "d"))
    prims += back_accessory(d, k, 0, by, rx * .8, ry)
    prims.append(E(0, by, rx, ry * (1 + anim["breath"]), "a"))
    prims.append(E(-rx * .1, by + ry * .35, rx * .7, ry * .45, "b", 0, "!"))
    prims += [E(-2, by + ry * .5, 3.5, 2, "d", 0.6 + sw * .5)]
    if d.pattern in ("stripes", "spots", "mask"):
        prims += [E(rx * .25, by - ry * .1, 1.6, ry * .7, "d"), E(rx * .5, by - ry * .1, 1.4, ry * .55, "d")]
    if d.hornish and k > 0.5:
        prims += horn(-rx * .55, by - ry * .7, 4 + 3 * k, -0.6)
    face = {"eyes": [(-rx * .55, by - ry * .2), (-rx * .15, by - ry * .25)], "eye_size": 1.25 - .35 * k, "iris": d.iris,
            "mouth": ("o", -rx * .45, by + ry * .25)}
    return prims, face


def serpent(d, k, anim):
    sw = anim["sway"]
    s = 1 + 0.35 * k
    prims = []
    prims += [E(4 * s, -4 * s, 12 * s, 4.5 * s, "d"), E(-2 * s, -9 * s, 10 * s, 4.5 * s, "a"), E(3 * s, -13.5 * s, 7 * s, 4 * s, "a")]
    prims.append(P([(10 * s, -5 * s), (17 * s + sw * 3, -9 * s), (12 * s, -2 * s)], "d"))
    prims += [E(-2 * s, -8.5 * s, 7 * s, 2.2 * s, "b", 0, "!")]
    nx, ny = -1 * s + sw * 2, -22 * s + anim["bob"]
    prims.append(L(3 * s, -14 * s, nx, ny + 4, 5 * s, "a"))
    if d.wings:
        prims += wings(d, k, 4, -16 * s, 10, anim)
    hp, face = head(d, k, nx, ny, 6.5 * s, 5.8 * s, anim)
    prims += hp
    return prims, face


def dragon(d, k, anim):
    d.hornish = True
    d.wings = d.wings or k > 0.4
    if k < 0.4:
        return quad(d, k, anim)
    return biped(d, k, anim)


def bug(d, k, anim):
    b, br = anim["bob"], anim["breath"]
    s = (1 + 0.3 * k) * d.fat
    prims = []
    ph = anim["ph"]
    # 六条腿
    for i, y in enumerate((-2.5, -5.0, -7.5)):
        dy = math.sin(ph + i * 2) * 1.0
        prims += both([L(4 * s, (y - 3) * s, 11 * s, -0.5 + dy * (i % 2), 1.2, "d")])
    prims += tail(d, k, 7 * s, -8 * s, anim)
    prims += [E(4 * s, -7 * s, 8 * s, 6.5 * s * (1 + br), "a")]
    if k > 0.4 or d.types[0] in ("钢", "岩石"):
        prims += [E(4 * s, -8 * s, 8.5 * s, 6 * s, "d"), L(4 * s, -14 * s, 4 * s, -2 * s, 0.8, "a")]  # 甲壳
    if "飞行" in d.types or (k > 0.6 and d.rng.random() < 0.6):
        fl = anim["flap"] * .4
        prims += both([E(9 * s, -15 * s, 4 * s, 8 * s, "#e8f6ff", 0.8 - fl)])
    prims += [E(-3 * s, -11 * s, 5.5 * s, 5 * s, "a")]
    if d.pattern != "none":
        prims += [E(5 * s, -7 * s, 1.8, 1.5, "c"), E(1 * s, -6 * s, 1.5, 1.3, "c")]
    hp, face = head(d, k, -6 * s, -17 * s + b, 6.5 * s, 6 * s, anim)
    if k > 0.5:  # 大颚
        hp += both([P([(-6 * s + 2, -13 * s + b), (-6 * s + 5, -10 * s + b), (-6 * s + 2.5, -11.5 * s + b)], "d", "!")])
    return prims + hp, face


def butterfly(d, k, anim):
    fl = anim["flap"]
    s = 1 + 0.35 * k
    by = -14 * s + anim["bob"] * 2 - 2
    prims = []
    for up in (True, False):
        sx, sy = (11 if up else 8) * s, (by - 6 * s) if up else (by + 3 * s)
        rx, ry = (10 if up else 7) * s * (1 - abs(fl) * 0.25), (8 if up else 6) * s
        prims += both([E(sx, sy, rx, ry, "b" if up else "c", 0.5 if up else -0.4),
                       E(sx * 1.1, sy, rx * .45, ry * .45, "#ff7a5a" if up else "a", 0.5)])
        if up:
            prims += both([E(sx * 1.35, sy - ry * .35, 1.8, 1.8, "#ffffff")])
    prims += [E(0, by, 3.5 * s, 10 * s, "d"), E(0, by + 5 * s, 3 * s, 4 * s, "a")]
    hp, face = head(d, k, 0, by - 10 * s, 5 * s, 4.6 * s, anim)
    face["eye_size"] *= 0.9
    return prims + hp, face


def frog(d, k, anim):
    br, b = anim["breath"], anim["bob"]
    rx, ry = (13 + 4 * k) * d.fat, (9 + 3 * k) * (1 + br * 2)
    by = -ry - 1
    prims = []
    prims += tail(d, k, rx * .5, by, anim)
    prims += both([E(rx * .8, -2, 5 + k, 3, "a"), E(rx * .95, -0.7, 3.5, 1.3, "d", 0, "!")])
    prims += back_accessory(d, k, 0, by, rx, ry)
    eyey = by - ry * .8 + b
    prims += both([E(rx * .5, eyey, 4.5 + k * .5, 4.5 + k * .5, "a")])
    prims.append(E(0, by, rx, ry, "a"))
    prims.append(E(0, by + ry * .4, rx * .65, ry * .45, "b", 0, "!"))
    prims += body_markings(d, k, 0, by - ry * .2, rx * .7, ry * .5)[1:]
    if d.ear == "frill":
        prims += both([P([(rx * .7, by - ry * .3), (rx + 5, by - ry * .9), (rx + 3, by), (rx * .8, by + ry * .2)], "c")])
    prims += head_accessory(d, k, 0, by - ry * .2, rx * .5, ry * .8, anim)
    face = {"eyes": [(-rx * .5, eyey), (rx * .5, eyey)], "eye_size": 1.2 - 0.3 * k, "iris": d.iris,
            "mouth": ("wide", 0, by + ry * .05), "blush": [(-rx * .75, by + ry * .05), (rx * .75, by + ry * .05)]}
    return prims, face


def crust(d, k, anim):
    s = (1 + 0.35 * k) * d.fat
    sw = anim["sway"]
    by = -9 * s
    prims = []
    for i in range(3):
        prims += both([L(6 * s, by + 2, (10 + i * 2) * s, -0.5, 1.4, "d")])
    # 钳子
    for side in (-1, 1):
        cx = side * (15 * s)
        cy = by - 3 * s - sw * 2 * side
        prims += [L(side * 8 * s, by, cx, cy, 2.6, "a"),
                  E(cx, cy - 2, 4 * s, 3 * s, "a", side * 0.4),
                  P([(cx - side * 1, cy - 4 * s), (cx + side * 4 * s, cy - 7 * s - abs(sw) * 3), (cx + side * 2, cy - 2)], "a")]
    prims += [L(-3 * s, by - 5, -4 * s, by - 13 * s, 1.2, "d"), L(3 * s, by - 5, 4 * s, by - 13 * s, 1.2, "d"),
              E(-4 * s, by - 13 * s, 2.4, 2.4, "#f4f0e8"), E(4 * s, by - 13 * s, 2.4, 2.4, "#f4f0e8")]
    prims += back_accessory(d, k, 0, by, 11 * s, 7 * s)
    prims.append(E(0, by, 11 * s, 7 * s * (1 + anim["breath"]), "a"))
    prims.append(E(0, by + 2.5 * s, 7 * s, 3.5 * s, "b", 0, "!"))
    if d.pattern != "none":
        prims += [E(-4 * s, by - 3 * s, 2, 1.5, "d"), E(4 * s, by - 3 * s, 2, 1.5, "d")]
    face = {"eyes": [(-4 * s, by - 13 * s), (4 * s, by - 13 * s)], "eye_size": 0.55 + 0.1 * k, "iris": d.iris,
            "mouth": ("cat", 0, by + 0.5)}
    return prims, face


def floater(d, k, anim):
    s = (1 + 0.3 * k) * d.fat
    by = -15 * s + anim["bob"] * 2.5 - 2
    prims = []
    prims += tail(d, k, 0, by + 9 * s, anim, scale=s)
    if d.types[0] in ("幽灵", "恶"):
        prims.append(P([(-9 * s, by), (-10 * s + anim["sway"] * 3, by + 12 * s), (-4 * s, by + 8 * s), (0, by + 13 * s),
                        (4 * s, by + 8 * s), (10 * s + anim["sway"] * 3, by + 12 * s), (9 * s, by)], "a"))
    if k > 0.4:  # 漂浮的小球/手
        for side in (-1, 1):
            prims.append(E(side * 14 * s, by + 3 + math.sin(anim["ph"] + side) * 1.5, 2.8, 2.8, "c"))
    prims.append(E(0, by, 10 * s, 10 * s * (1 + anim["breath"]), "a"))
    prims += body_markings(d, k, 0, by + 3 * s, 7 * s, 5 * s)
    hp, face = head(d, k, 0, by - 1, 10 * s, 10 * s, anim)
    hp = [p for p in hp if not (p[0] == "e" and abs(p[3] - 10 * s) < 1e-6)]
    return prims + hp, face


def plant(d, k, anim):
    s = (1 + 0.3 * k) * d.fat
    sw = anim["sway"]
    by = -9 * s
    prims = []
    # 背上的大叶子 / 花
    for i, ang in enumerate((-0.9, -0.3, 0.3, 0.9)):
        prims += leaf(0, by - 6 * s, (9 + 5 * k) * s, ang + sw * .3, "#4caf3a" if i % 2 else "#6cc25a")
    if k > 0.5:
        for i in range(6):
            ang = i * 1.047 + sw * .2
            prims.append(E(math.sin(ang) * 6 * s, by - 16 * s - math.cos(ang) * 6 * s, 3.2 * s, 4.5 * s, "c", ang))
        prims.append(E(0, by - 16 * s, 3 * s, 3 * s, "#ffe066"))
    prims += both([E(5 * s, -1.6, 3 * s, 2 * s, "d")])
    prims.append(E(0, by, 10 * s, 8.5 * s * (1 + anim["breath"]), "a"))
    prims += body_markings(d, k, 0, by, 10 * s, 8.5 * s)
    face = {"eyes": [(-3.8 * s, by - 2 * s), (3.8 * s, by - 2 * s)], "eye_size": (1.2 - 0.3 * k) * s * .9, "iris": d.iris,
            "mouth": (d.mouth, 0, by + 2.5 * s), "blush": [(-6.5 * s, by + 1.5 * s), (6.5 * s, by + 1.5 * s)]}
    return prims, face


def bat(d, k, anim):
    s = (1 + 0.3 * k)
    by = -16 * s + anim["bob"] * 2
    prims = wings(d, k, 5 * s, by - 2, 14 * s, anim, membrane=True)
    prims += both([L(3 * s, by + 6 * s, 3.5 * s, by + 10 * s, 1.4, "d")])
    prims.append(E(0, by, 8 * s, 8 * s * (1 + anim["breath"]), "a"))
    prims += body_markings(d, k, 0, by + 2, 6 * s, 5 * s)
    hp, face = head(d, k, 0, by - 3 * s, 8 * s, 7 * s, anim)
    hp = [p for p in hp if not (p[0] == "e" and abs(p[3] - 8 * s) < 1e-6)]
    face["mouth"] = ("cat", 0, by + 1.5 * s)
    prims += hp + both([P([(1.2, by + 2.5 * s), (2.2, by + 2.5 * s), (1.7, by + 4 * s)], "#ffffff", "!")])
    return prims, face


PLANS = {"四足": quad, "人形": biped, "鸟形": bird, "鱼形": fish, "蛇形": serpent, "龙形": dragon, "虫形": bug,
         "蝶形": butterfly, "两栖": frog, "甲壳": crust, "浮游": floater, "植物": plant, "飞膜": bat}


def anim_state(f):
    ph = f / FRAMES * 2 * math.pi
    # 呼吸和上下浮动一个周期，摆尾一个周期，扇翅两个周期，叠起来不显得机械
    br = (1 - math.cos(ph)) / 2
    return {"ph": ph, "bob": -br * 1.2, "breath": br * 0.045,
            "sway": math.sin(ph) * 0.35, "flap": math.sin(ph * 2)}


def build(design, sp, f):
    k = stage_k(design, sp["stage"] - 1)
    prims, face = PLANS.get(design.body, quad)(design, k, anim_state(f))
    out = {"a": design.a if k < 0.9 else hsv_shift(design.a, ds=0.05, mul_v=0.92), "b": design.b, "d": design.d,
           "shape": [p if p[0][0] != "e" or p[5] != "c" else p[:5] + (design.c,) + p[6:] for p in prims],
           "gloss": design.gloss, "scale": 0.82 + 0.3 * k + (0.1 if design.legend else 0)}
    out["shape"] = [(p[0], p[1], p[2]) if p[0][0] == "p" and p[2] == "c" and False else p for p in out["shape"]]
    out["shape"] = [_fix_color(p, design) for p in out["shape"]]
    out.update({kk: v for kk, v in face.items() if v is not None})
    if face.get("mouth") is None:
        out.pop("mouth", None)
    return out


def _fix_color(p, d):
    """把占位色 c 换成这条线的点缀色"""
    k = p[0][0]
    idx = 5 if k == "e" else (2 if k == "p" else 6)
    if p[idx] == "c":
        p = p[:idx] + (d.c,) + p[idx + 1:]
    return p


# ------------------------------------------------------------------ 渲染
def render_species(args):
    line_species, only = args
    design = Design(line_species[0]["line"], line_species)
    done = []
    for sp in line_species:
        if only and sp["key"] not in only:
            continue
        # 先按第 0 帧定好缩放，4 帧用同一个缩放，动画才不会忽大忽小
        spec0 = build(design, sp, 0)
        scale = gm.FRONT[1]
        while True:
            frames = []
            ok = True
            for f in range(FRAMES):
                spec = build(design, sp, f) if f else spec0
                im = gm.render(spec, gm.FRONT[0], scale, back=False)
                bb = im.getbbox()
                if not bb or bb[0] == 0 or bb[1] == 0 or bb[2] == gm.FRONT[0] or bb[3] == gm.FRONT[0]:
                    ok = False
                    break
                frames.append(im)
            if ok:
                break
            scale *= 0.95
        strip = Image.new("RGBA", (gm.FRONT[0] * FRAMES, gm.FRONT[0]))
        for i, im in enumerate(frames):
            strip.paste(im, (i * gm.FRONT[0], 0))
        strip.save(os.path.join(OUT, f"{sp['key']}_front.png"))
        gm.render_fit(spec0, gm.BACK[0], gm.BACK[1], back=True).save(os.path.join(OUT, f"{sp['key']}_back.png"))
        done.append(sp["key"])
    return done


def main():
    species = json.load(open(os.path.join(ROOT, "data", "dex", "species.json"), encoding="utf-8"))
    only = set(sys.argv[1:])
    os.makedirs(OUT, exist_ok=True)
    lines = {}
    for sp in species:
        lines.setdefault(sp["line"], []).append(sp)
    jobs = [(v, only) for v in lines.values() if not only or any(s["key"] in only for s in v)]
    with Pool() as pool:
        n = sum(len(r) for r in pool.imap_unordered(render_species, jobs))
    print(f"画了 {n} 只")


if __name__ == "__main__":
    main()
