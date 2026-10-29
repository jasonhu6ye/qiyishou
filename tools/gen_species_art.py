"""716 只幻兽的立绘：按图鉴数据（data/dex/species.json）拼部件，交给 gen_monsters 的光照渲染器画。

1. 物种原型：名字里的动物（狐、熊、鹿、犀、象、鹰、鸮、蝎、螳螂、水母……约 90 种）决定骨架，
   各有自己的耳朵、口鼻、角、尾巴、腿长和特殊部件（龟壳、象鼻、驼峰、鬃毛、羊毛……）。
2. 进化线设计：同一条线用线号做随机种子，再随机身形比例、花纹、配色方案、眼型和属性饰物，
   所以同是「狐」的几条线也长得不一样；同一条线的各阶段共用这套设计。
3. 进化阶段：初阶头大腿短，进化后身体变大、头身比变小、长出角和更多饰物、颜色加深、眼神变凶。
视角是 3/4 侧身朝左（像宝可梦的正面立绘），背面图把形状左右翻转、只保留背面部件。
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
INK = "#2a1a1a"


# ------------------------------------------------------------------ 颜色
def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hx(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in c)


def hsv(h, dh=0.0, ds=0.0, dv=0.0, mv=1.0):
    r, g, b = (x / 255 for x in rgb(h))
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    hh = (hh + dh) % 1.0
    ss = max(0.0, min(1.0, ss + ds))
    vv = max(0.0, min(1.0, vv * mv + dv))
    return hx(tuple(x * 255 for x in colorsys.hsv_to_rgb(hh, ss, vv)))


def mix(a, b, t):
    ca, cb = rgb(a), rgb(b)
    return hx(tuple(ca[i] + (cb[i] - ca[i]) * t for i in range(3)))


# ------------------------------------------------------------------ 图元
def E(x, y, rx, ry, c, rot=0.0, f=""):
    return ("e" + f, x, y, max(0.3, rx), max(0.3, ry), c, rot)


def P(pts, c, f=""):
    return ("p" + f, [tuple(p) for p in pts], c)


def L(x1, y1, x2, y2, w, c, f=""):
    if abs(x1 - x2) < 1e-3 and abs(y1 - y2) < 1e-3:
        y2 += 0.01
    return ("l" + f, x1, y1, x2, y2, max(0.6, w), c)


def rot(pts, cx, cy, a):
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def polar(x, y, ang, ln):
    """从 (x, y) 沿角度 ang（0 朝上，顺时针为正）走 ln"""
    return x + math.sin(ang) * ln, y - math.cos(ang) * ln


def curve(x, y, ang, ln, bend, w0, w1, c, n=4, f=""):
    """一条弯曲渐细的「触手」：返回 n 段线段，以及末端坐标"""
    out = []
    for i in range(n):
        a = ang + bend * i / n
        x2, y2 = polar(x, y, a, ln / n)
        out.append(L(x, y, x2, y2, w0 + (w1 - w0) * i / max(1, n - 1), c, f))
        x, y = x2, y2
    return out, (x, y)


def spike_row(pts, h, c, ang_of=None, w=0.45):
    """沿一串点立起尖刺"""
    out = []
    for i, (x, y) in enumerate(pts):
        a = ang_of(i) if ang_of else 0.0
        tx, ty = polar(x, y, a, h)
        bx1, by1 = polar(x, y, a - math.pi / 2, h * w)
        bx2, by2 = polar(x, y, a + math.pi / 2, h * w)
        out.append(P([(bx1, by1), (tx, ty), (bx2, by2)], c))
    return out


def flame(x, y, s, ang=0.0, flick=0.0):
    pts = [(-.55, 0), (-.75, -.85), (-.3, -.6), (-.05 + flick * .2, -1.6), (.3, -.7), (.7, -1.05), (.55, 0)]
    inner = [(-.3, -.1), (-.18, -.7), (0 + flick * .15, -1.05), (.2, -.6), (.3, -.1)]
    return [P(rot([(x + px * s, y + py * s) for px, py in pts], x, y, ang), "#ff8a2a"),
            P(rot([(x + px * s, y + py * s) for px, py in inner], x, y, ang), "#ffe066")]


def leaf(x, y, ln, ang, c="#4caf3a", vein="#2a7429"):
    cx, cy = polar(x, y, ang, ln / 2)
    tx, ty = polar(x, y, ang, ln * 0.85)
    return [E(cx, cy, ln * 0.24, ln / 2, c, ang), L(x, y, tx, ty, 0.6, vein)]


def bolt(x, y, s, ang=0.0, c="#ffd83a"):
    pts = [(0, 0), (.5, -.9), (.15, -.9), (.65, -1.8), (-.1, -.7), (.25, -.7), (-.2, 0)]
    return [P(rot([(x + px * s, y + py * s) for px, py in pts], x, y, ang), c)]


def crystal(x, y, s, ang=0.0, c="#bfefff"):
    pts = [(-.35, 0), (-.28, -1), (0, -1.55), (.28, -1), (.35, 0)]
    return [P(rot([(x + px * s, y + py * s) for px, py in pts], x, y, ang), c)]


def horn(x, y, ln, ang, w, c, bend=0.0):
    """尖角：底宽 w，长 ln，可以弯"""
    pts = []
    n = 5
    for i in range(n + 1):
        t = i / n
        a = ang + bend * t
        px, py = polar(x, y, a, ln * t)
        pts.append((px, py, w * (1 - t) * 0.5, a))
    left = [polar(px, py, a - math.pi / 2, hw) for px, py, hw, a in pts]
    right = [polar(px, py, a + math.pi / 2, hw) for px, py, hw, a in pts]
    return [P(left + right[::-1], c)]


def star(x, y, r, c, n=5, inner=0.45, a0=0.0):
    pts = []
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * inner
        pts.append(polar(x, y, a0 + i * math.pi / n, rr))
    return [P(pts, c)]


def ell_top(cx, cy, rx, ry, t):
    """椭圆上缘的点：t 从 -1（左）到 1（右）"""
    x = cx + rx * t
    return x, cy - ry * math.sqrt(max(0.0, 1 - t * t))


# ------------------------------------------------------------------ 物种原型
# 四足：hr 头大小 · sn 口鼻长度 · ear 耳朵 · horn 角 · body (长, 高) · legs (长, 粗) · tail 尾巴 · neck 脖子
# pose 姿势（stand 站、sit 坐、low 趴低、slope 前高后低）· ex 特殊部件 · nat (天然主色, 天然副色)
Q = dict
QUAD = {
    "鼠": Q(hr=1.15, sn=.45, ear="round", body=(.8, .9), legs=(.55, .8), tail="thin", pose="sit", ex={"whisker"}, nat=("#b8a88a", "#f2e6d0")),
    "兔": Q(hr=1.1, sn=.25, ear="long", body=(.8, 1.0), legs=(.55, .9), tail="puff", pose="sit", ex={"whisker"}, nat=("#e8e0d4", "#ffffff")),
    "犬": Q(hr=1.0, sn=.75, ear="droop", body=(1.0, .95), legs=(.95, 1.0), tail="wag", nat=("#c89a62", "#f4e6cc")),
    "猫": Q(hr=1.0, sn=.2, ear="point", body=(1.0, .85), legs=(.9, .8), tail="long", pose="sit", ex={"whisker"}, nat=("#e0a050", "#fff2dc")),
    "猪": Q(hr=1.05, sn=.45, sw=1.2, ear="small", body=(1.15, 1.15), legs=(.55, 1.1), tail="curl", ex={"pignose"}, nat=("#f0a8b0", "#ffe0e4")),
    "牛": Q(hr=1.0, sn=.55, sw=1.25, ear="side", horn="twin", body=(1.3, 1.2), legs=(.9, 1.3), tail="tuft", nat=("#8a5a3a", "#f4e8d8")),
    "羊": Q(hr=.85, sn=.5, ear="side", horn="ram", body=(1.1, 1.1), legs=(.8, .8), tail="stub", ex={"wool"}, nat=("#f4f0e4", "#5a4a40")),
    "猴": Q(hr=1.0, sn=.15, ear="round", body=(.8, 1.0), legs=(.85, .8), tail="curl_long", pose="sit", ex={"face"}, nat=("#a0703a", "#f0c8a0")),
    "熊": Q(hr=1.05, sn=.5, ear="round", body=(1.25, 1.25), legs=(.75, 1.35), tail="stub", nat=("#7a5030", "#d8b088")),
    "獾": Q(hr=.95, sn=.6, ear="small", body=(1.25, .9), legs=(.5, 1.1), tail="stub", pose="low", ex={"stripe_head", "claws"}, nat=("#808080", "#f0f0f0")),
    "狸": Q(hr=1.0, sn=.45, ear="point", body=(1.1, 1.0), legs=(.65, .9), tail="ring", ex={"mask"}, nat=("#8a7a68", "#e8e0d0")),
    "貂": Q(hr=.85, sn=.4, ear="round", body=(1.5, .7), legs=(.5, .7), tail="bushy", pose="low", nat=("#8a5a30", "#f4e0c0")),
    "鼬": Q(hr=.85, sn=.4, ear="round", body=(1.55, .65), legs=(.5, .7), tail="thin_bushy", pose="low", nat=("#b07a40", "#fff0d8")),
    "鹿": Q(hr=.85, sn=.6, ear="side", horn="antler", body=(1.1, .9), legs=(1.5, .7), tail="stub", neck=.7, ex={"dapples"}, nat=("#b07a48", "#f4e4cc")),
    "狐": Q(hr=1.0, sn=.7, ear="tall", body=(1.05, .85), legs=(.9, .8), tail="bushy", ex={"ruff"}, nat=("#e8823a", "#fff4e4")),
    "狼": Q(hr=1.0, sn=.85, ear="tall", body=(1.25, .95), legs=(1.15, .95), tail="bushy_low", ex={"ruff"}, nat=("#8a92a0", "#e8ecf0")),
    "驹": Q(hr=.8, sn=1.0, sw=.9, ear="point", body=(1.3, .95), legs=(1.5, .85), tail="hair", neck=.85, ex={"mane", "hooves"}, nat=("#a86a3a", "#f0e0c8")),
    "狮": Q(hr=1.05, sn=.55, ear="round", body=(1.3, 1.0), legs=(1.1, 1.15), tail="tuft", ex={"bigmane"}, nat=("#e0b060", "#f8e8c0")),
    "蜥": Q(hr=1.0, sn=.7, ear="none", body=(1.1, .8), legs=(.7, .95), tail="taper", pose="low", ex={"crest_opt", "scales_opt"}, nat=("#6aa858", "#e8f0c8")),
    "豹": Q(hr=.9, sn=.35, ear="round", body=(1.35, .8), legs=(1.1, .85), tail="long", ex={"whisker"}, nat=("#e8c060", "#fff4dc")),
    "虎": Q(hr=1.05, sn=.45, ear="round", body=(1.4, 1.0), legs=(1.0, 1.2), tail="long", ex={"whisker", "ruff"}, nat=("#e88a30", "#fff4e4")),
    "龟": Q(hr=.8, sn=.3, ear="none", body=(1.1, .8), legs=(.4, 1.3), tail="stub", pose="low", ex={"shell"}, nat=("#7aa860", "#e8e0b0")),
    "獭": Q(hr=.95, sn=.35, ear="small", body=(1.3, .85), legs=(.5, .9), tail="flat", pose="sit", ex={"whisker"}, nat=("#7a5838", "#e8d0b0")),
    "犀": Q(hr=.95, sn=.8, sw=1.15, ear="small", horn="nose", body=(1.45, 1.2), legs=(.8, 1.45), tail="tuft", ex={"plates"}, nat=("#8a8a90", "#c8c8cc")),
    "象": Q(hr=1.15, sn=.2, ear="fan", horn="tusk", body=(1.4, 1.3), legs=(.9, 1.55), tail="tuft", ex={"trunk"}, nat=("#9098a8", "#d0d4dc")),
    "驼": Q(hr=.75, sn=.75, ear="small", body=(1.25, .9), legs=(1.5, .8), tail="tuft", neck=1.0, ex={"hump"}, nat=("#d0a868", "#f4e4c0")),
    "鳄": Q(hr=.75, sn=1.6, sw=.75, ear="none", body=(1.5, .7), legs=(.4, .95), tail="thick", pose="low", ex={"teeth", "ridge"}, nat=("#5a8048", "#d8d8a0")),
    "鼹": Q(hr=1.0, sn=.5, ear="none", body=(1.05, 1.0), legs=(.4, 1.1), tail="stub", pose="low", ex={"bigclaws", "pinknose", "tinyeyes"}, nat=("#5a4a48", "#d0a0a0")),
    "穿山甲": Q(hr=.75, sn=.75, ear="none", body=(1.3, .9), legs=(.5, .95), tail="thick", pose="low", ex={"scales", "claws"}, nat=("#a07848", "#e0c098")),
    "鬣": Q(hr=1.0, sn=.65, ear="round", body=(1.2, 1.0), legs=(1.0, 1.0), tail="stub", pose="slope", ex={"spots", "ridge_hair"}, nat=("#b09468", "#e8dcc0")),
    "豺": Q(hr=.95, sn=.75, ear="tall", body=(1.15, .85), legs=(1.05, .85), tail="bushy_low", nat=("#c06a38", "#f4dcc0")),
    "犰狳": Q(hr=.75, sn=.7, ear="point", body=(1.15, 1.0), legs=(.45, .9), tail="taper", pose="low", ex={"bands"}, nat=("#a89070", "#e8d8c0")),
    "龙": Q(hr=1.05, sn=.75, ear="none", horn="dragon", body=(1.0, 1.0), legs=(.75, 1.15), tail="thick", pose="kanga", ex={"ridge", "claws"}, nat=("#5a6ad8", "#f0e8c8")),
    "袋鼠": Q(hr=.9, sn=.6, ear="tall", body=(.9, 1.2), legs=(.7, 1.2), tail="thick", pose="kanga", ex={"pouch"}, nat=("#c08850", "#f0dcc0")),
}
BIRD = {  # beak 喙 · neck 脖子 · legs 腿 · wing 翅膀 · tail 尾 · crest 冠羽
    "雀": Q(beak="short", neck=0, legs=.6, wing="fold", tail="short", body=(1.0, 1.0), nat=("#a07848", "#f0dcc0")),
    "鸽": Q(beak="short", neck=.2, legs=.6, wing="fold", tail="fan", body=(1.15, 1.0), ex={"neckshine"}, nat=("#9098b0", "#e0e4f0")),
    "鸭": Q(beak="bill", neck=.3, legs=.5, wing="fold", tail="short", body=(1.2, .9), nat=("#f0e0a0", "#fff8e0")),
    "鹅": Q(beak="bill", neck=1.2, legs=.6, wing="fold", tail="short", body=(1.2, .9), nat=("#f4f4f4", "#ffffff")),
    "鸟": Q(beak="short", neck=.1, legs=.7, wing="half", tail="fan", body=(1.0, 1.0), nat=("#6a9ae0", "#f0f4ff")),
    "鹰": Q(beak="hook", neck=.2, legs=.8, wing="spread", tail="fan", body=(1.0, 1.0), ex={"brow"}, nat=("#8a5a30", "#f4ecdc")),
    "隼": Q(beak="hook", neck=.1, legs=.7, wing="half", tail="short", body=(.9, 1.0), ex={"brow", "tearmark"}, nat=("#6a7488", "#f0f0f4")),
    "燕": Q(beak="short", neck=0, legs=.4, wing="swept", tail="fork", body=(1.0, .85), nat=("#2a3460", "#f4f0e8")),
    "鸮": Q(beak="tiny", neck=0, legs=.5, wing="fold", tail="short", body=(1.0, 1.2), ex={"owlface", "tufts"}, nat=("#9a7a58", "#f0e0c8")),
    "鹤": Q(beak="long", neck=1.4, legs=1.9, wing="fold", tail="plume", body=(1.0, .85), ex={"redcap"}, nat=("#f4f4f4", "#ffffff")),
    "鸦": Q(beak="long_short", neck=.1, legs=.7, wing="half", tail="fan", body=(1.0, 1.0), ex={"crest"}, nat=("#3a3a50", "#6a6a88")),
    "鹏": Q(beak="hook", neck=.4, legs=.8, wing="spread", tail="plume", body=(1.1, 1.0), ex={"crest", "brow"}, nat=("#c08a40", "#fff0d0")),
    "蝠": None,
}
FISH = {  # shape 体形 · dorsal 背鳍 · tailf 尾鳍
    "鱼": Q(shape="oval", dorsal="soft", tailf="fork", nat=("#e8a040", "#fff0d0")),
    "鲤": Q(shape="oval", dorsal="soft", tailf="flowing", ex={"barbels", "scales"}, nat=("#e85a3a", "#fff4e8")),
    "鲨": Q(shape="long", dorsal="shark", tailf="crescent", ex={"teeth", "gills"}, nat=("#7088a8", "#f0f4f8")),
    "鲸": Q(shape="round", dorsal="none", tailf="fluke", ex={"spout", "grooves"}, nat=("#4a6890", "#e8f0f8")),
    "鳐": Q(shape="ray", dorsal="none", tailf="whip", nat=("#6a7a98", "#f0f0f4")),
    "豚": Q(shape="long", dorsal="curve", tailf="fluke", ex={"beak"}, nat=("#7aa0c8", "#f0f8ff")),
}
SERPENT = {
    "蛇": Q(kind="snake", nat=("#6a9848", "#e8f0c0")),
    "鳗": Q(kind="eel", nat=("#4a6a88", "#e0ecf0")),
    "蛟": Q(kind="dragon", nat=("#4a88a0", "#e8f4f0")),
}
BUG = {
    "蛾": "moth", "蜂": "bee", "蚁": "ant", "甲": "beetle", "螳": "mantis", "蛛": "spider", "蚕": "worm", "萤": "firefly",
    "蜓": "dragonfly", "蝉": "cicada", "蟋": "cricket", "蜗": "snail", "蝎": "scorpion", "蜈": "centipede", "锹": "stag",
}
CRUST = {"蟹": "crab", "虾": "shrimp", "贝": "clam", "螺": "conch", "菊石": "ammonite"}
FLOAT = {"母": "jelly", "灵": "spirit", "魂": "soul", "影": "shadow", "灯": "lantern", "面": "mask", "精": "fairy", "铃": "bell", "晶": "crystal"}
PLANT = {"苗": "sprout", "花": "flower", "藤": "vine", "菇": "mushroom", "果": "fruit"}
BIPED = {"猿": "ape", "偶": "doll", "石像": "golem", "钟": "bellbody"}
NOUNS = sorted(list(QUAD) + [k for k in BIRD] + list(FISH) + list(SERPENT) + list(BUG) + list(CRUST) + list(FLOAT)
               + list(PLANT) + list(BIPED) + ["蛙", "蝶"], key=len, reverse=True)
LEGEND_NOUN = {"炭炭": "魂", "电栗": "鼠", "炎帝": "狮", "风神": "鹏", "镜湖之主": "蛟", "沼王": "鳄", "沙之古王": "蝎",
               "岩心巨像": "石像", "雾隐九尾": "狐", "奈尔斯始祖": "龙", "星屑": "精", "芽之子": "苗", "时之沙": "晶"}
BODY_DEFAULT = {"四足": "狼", "鸟形": "鸟", "鱼形": "鱼", "蛇形": "蛇", "龙形": "龙", "虫形": "甲", "蝶形": "蝶", "两栖": "蛙",
                "甲壳": "蟹", "浮游": "灵", "植物": "花", "人形": "猿", "飞膜": "蝠"}


def noun_of(line):
    for sp in line:
        for k, v in LEGEND_NOUN.items():
            if k in sp["name"]:
                return v
    for sp in line:
        for n in NOUNS:
            if n in sp["name"]:
                return n
    return BODY_DEFAULT.get(line[0]["model"]["body"], "狼")


# ------------------------------------------------------------------ 一条进化线的设计
class Design:
    def __init__(self, line):
        base = line[0]
        self.rng = r = random.Random(7919 * base["line"] + 17)
        self.types = base["types"]
        self.t1 = self.types[0]
        self.t2 = self.types[1] if len(self.types) > 1 else None
        self.stages = len(line)
        self.legend = base["kind"] == "legend" or base["category"] in ("传说", "幻", "准传说")
        self.noun = noun_of(line)
        self.body = base["model"]["body"]
        self.dragonish = self.body == "龙形" or "龙" in self.types
        self.winged = "飞行" in self.types
        self.nine = "九尾" in "".join(s["name"] for s in line)
        # 身形比例的随机偏移（同原型不同线拉开差距）
        u = r.uniform
        self.v = {"hr": u(.85, 1.2), "bl": u(.85, 1.2), "bh": u(.85, 1.15), "ll": u(.8, 1.25), "sn": u(.75, 1.3),
                  "ear": u(.8, 1.35), "tail": u(.8, 1.35), "eye": u(.85, 1.2), "neck": u(.8, 1.3)}
        self.eye_style = r.choice(["round", "round", "round", "sharp", "sleepy", "tiny"] if self.t1 not in ("妖精", "普通") else ["round", "round", "sleepy"])
        self.pattern = r.choice(["none", "none", "spots", "stripes", "saddle", "socks", "tipped", "bands", "belly"])
        self.mouth = r.choice(["cat", "smile", "o", "cat", "smile", "fang"])
        self.cheek = r.random() < 0.3 or self.t1 == "电"
        self.feature = r.random()  # 原型内部的小变体开关
        self.palette()
        self.accessories()

    def palette(self):
        r = self.rng
        T1, T2 = TYPE_COLOR[self.t1], TYPE_COLOR[self.t2] if self.t2 else None
        nat = self.nat()
        scheme = r.choices(["type", "natural", "split", "pastel", "dark"],
                           [5, 4 if nat else 0, 3 if T2 else 0, 1.5 if self.t1 in ("妖精", "普通", "水", "冰", "灵能") else 0.4,
                            2 if self.t1 in ("恶", "幽灵", "毒", "龙", "钢") else 0.4])[0]
        jit = lambda c: hsv(c, dh=r.uniform(-.06, .06), ds=r.uniform(-.12, .1), mv=r.uniform(.88, 1.1))  # noqa: E731
        if scheme == "natural":
            a = mix(jit(nat[0]), T1, r.uniform(.1, .35))
            b = nat[1]
            acc = hsv(T1, ds=.1, mv=1.05)
        elif scheme == "split":
            a = jit(T1)
            b = mix(T2, "#ffffff", .55)
            acc = jit(T2)
        elif scheme == "pastel":
            a = mix(jit(T1), "#ffffff", .35)
            b = "#ffffff"
            acc = hsv(T2 or T1, dh=r.choice([.0, .5, .15]), ds=.15)
        elif scheme == "dark":
            a = hsv(jit(T1), ds=-.05, mv=.62)
            b = mix(T2 or T1, "#ffffff", .3) if r.random() < .5 else hsv(T1, mv=1.1, ds=.1)
            acc = hsv(T2 or IRIS[self.t1], ds=.2, mv=1.2)
        else:
            a = jit(T1)
            b = r.choice(["#fff4dc", "#f4f0ff", "#ffe6c8", mix(a, "#ffffff", .62), "#f0f7e8", mix(T2 or a, "#ffffff", .5)])
            acc = T2 if T2 and r.random() < .7 else hsv(T1, dh=r.choice([.08, -.08, .5, .33]), ds=.1)
        self.a, self.b, self.acc = a, b, acc
        self.d = hsv(a, dh=.02, ds=.08, mv=.62)
        self.acc2 = hsv(acc, mv=.7, ds=.05)
        self.horn_c = r.choice(["#f2ead8", "#e8dcc0", hsv(acc, mv=1.1), "#d8d0c8"]) if self.t1 not in ("钢", "冰", "岩石", "恶") else \
            {"钢": "#c8d0dc", "冰": "#d8f4ff", "岩石": "#a89878", "恶": "#3a3040"}[self.t1]
        self.iris = IRIS[self.t2] if self.t2 and r.random() < .5 else IRIS[self.t1]
        if scheme == "dark" or self.t1 in ("幽灵", "恶") and r.random() < .5:
            self.iris = r.choice(["#e03a3a", "#f0c020", "#30d0f0"])
        self.gloss = 1.0 if self.t1 in ("水", "冰", "钢") else (0.5 if self.t1 in ("毒", "妖精") else 0.0)
        self.scheme = scheme

    def nat(self):
        for table in (QUAD, BIRD, FISH, SERPENT):
            if self.noun in table and table[self.noun]:
                return table[self.noun].get("nat")
        return None

    def accessories(self):
        """属性饰物：每种属性有好几种放法，每条线挑 1~2 种"""
        r = self.rng
        opts = {
            "火": ["tail_flame", "head_flame", "back_flames", "mane_flame", "feet_flame"],
            "水": ["back_fin", "ear_fin", "bubbles", "wave_marks", "tail_fin"],
            "草": ["head_leaf", "back_bulb", "leaf_collar", "back_flower", "tail_leaf"],
            "电": ["tail_bolt", "bolt_marks", "spiky_crest", "antenna_balls", "cheeks"],
            "冰": ["back_crystals", "ice_crown", "frost_ruff", "icicles"],
            "格斗": ["wristbands", "headband", "belt", "scar"],
            "毒": ["poison_spots", "back_spikes", "drip", "gas"],
            "大地": ["rock_armor", "mud_marks", "big_claws", "nose_horn"],
            "飞行": ["wings", "crest_feathers"],
            "灵能": ["forehead_gem", "orbs", "third_eye", "halo"],
            "虫": ["antennae", "small_wings", "bands"],
            "岩石": ["back_rocks", "armor_plates", "crystal_horn"],
            "幽灵": ["ghost_tail", "wisps", "stitches"],
            "龙": ["dragon_horns", "back_ridge", "small_wings", "whiskers"],
            "恶": ["mask", "spiky_ruff", "claw_marks"],
            "钢": ["armor_plates", "helmet", "blade_fins", "bolts"],
            "妖精": ["ribbon", "star_mark", "fairy_wings", "flower_crown", "heart_cheeks"],
            "普通": ["scarf", "patch", "tuft", "collar"],
        }
        acc = [r.choice(opts[self.t1])]
        if r.random() < .55:
            acc.append(r.choice([o for o in opts[self.t1] if o != acc[0]] or acc))
        if self.t2:
            acc.append(r.choice(opts[self.t2]))
        if self.winged or (self.dragonish and r.random() < .7):
            acc.append("wings")
        if self.dragonish:
            acc.append("dragon_horns")
        if self.noun == "龙" and "wings" not in acc:
            acc.append("wings")
        self.acc_list = acc

    def has(self, a):
        return a in self.acc_list


def stage_k(d, s):
    if d.legend:
        return 1.0
    if d.stages == 1:
        return 0.6
    return s / (d.stages - 1)


def acc_on(d, k, name, need=0.0):
    return d.has(name) and k >= need


# ------------------------------------------------------------------ 脸
def eyes_spec(d, k, hx_, hy, hr, look=1.0, far=True):
    """侧脸朝左：近眼在头中线偏左，远眼更靠左、小一点"""
    es = d.v["eye"] * (hr / 6.5) * (1.05 - 0.3 * k if not d.legend else 0.8)
    if d.eye_style == "tiny":
        es *= 0.65
    eyes = [(hx_ + hr * .02 * look, hy - hr * .1, 1.0)]
    if far:
        eyes.append((hx_ - hr * .64 * look, hy - hr * .12, 0.8))
    spec = {"eyes": eyes, "eye_size": es, "iris": d.iris}
    if d.eye_style == "sharp" or (k >= .9 and not d.legend and d.eye_style != "sleepy"):
        spec["eye_ry"] = 0.72
    elif d.eye_style == "sleepy":
        spec["eye_ry"] = 0.6
    return spec


def brows(d, k, eyes, es):
    """进化完全或凶相：眼睛上方的眉骨"""
    if not (k >= .8 or d.eye_style == "sharp") or d.legend and d.t1 in ("妖精",):
        return []
    out = []
    for ex, ey, m in eyes:
        w = 2.2 * es * m
        out.append(P([(ex - w, ey - 2.6 * es * m - .4), (ex + w, ey - 3.4 * es * m), (ex + w, ey - 2.4 * es * m)], INK, "!"))
    return out


# ------------------------------------------------------------------ 属性饰物（放在身体上的通用部件）
def body_acc(d, k, an, body, head, tail_tip):
    """body = (cx, cy, rx, ry) 身体椭圆；head = (hx, hy, hr)；tail_tip 尾巴末端或 None。
    返回 (画在身体后面的, 画在身体上面的, 画在头上面的)"""
    bx, by, brx, bry = body
    hx_, hy, hr = head
    back, over, top = [], [], []
    fl = math.sin(an["ph"] * 3) * .5
    top_pts = lambda n, a=-.7, b=.6: [ell_top(bx, by, brx, bry, a + (b - a) * (i + .5) / n) for i in range(n)]  # noqa: E731
    n = 2 + int(k * 2.5)
    if acc_on(d, k, "tail_flame") and tail_tip:
        top += flame(tail_tip[0], tail_tip[1] + 1.5, 3 + 3 * k, an["sway"] * .4, fl)
    if acc_on(d, k, "head_flame"):
        top += flame(hx_ + hr * .1, hy - hr * .85, 2.5 + 3 * k, an["sway"] * .3, fl)
    if acc_on(d, k, "back_flames", .3):
        for i, (x, y) in enumerate(top_pts(n)):
            back += flame(x, y + 1.5, 2.5 + 2 * k, .15 * (i - n / 2), fl * (1 if i % 2 else -1))
    if acc_on(d, k, "mane_flame", .4):
        for i in range(4 + int(k * 2)):
            a = -1.2 + i * .45
            x, y = polar(hx_ + hr * .3, hy + hr * .2, a + 0.6, hr * 1.0)
            back += flame(x, y + 1, 2.5 + 2.5 * k, a + 0.6, fl)
    if acc_on(d, k, "feet_flame", .5):
        for x in (bx - brx * .6, bx + brx * .55):
            over += flame(x, 0.5, 2 + 1.5 * k, 0, fl)
    if acc_on(d, k, "back_fin"):
        x0, y0 = ell_top(bx, by, brx, bry, -.1)
        back.append(P([(x0 - brx * .45, y0 + 1.5), (x0 - brx * .1 + an["sway"] * 2, y0 - 5 - 4 * k), (x0 + brx * .3, y0 - 2 - 2 * k), (x0 + brx * .45, y0 + 1.5)], d.acc))
    if acc_on(d, k, "ear_fin"):
        back.append(P([(hx_ + hr * .3, hy - hr * .2), (hx_ + hr * 1.6, hy - hr * 1.0 + an["sway"]), (hx_ + hr * 1.2, hy + hr * .1), (hx_ + hr * .5, hy + hr * .35)], d.acc))
    if acc_on(d, k, "bubbles"):
        for i in range(3):
            t = (an["ph"] / (2 * math.pi) + i / 3) % 1.0
            top.append(E(hx_ - hr * (1.2 + .3 * i), hy - hr * (.5 + t * 2.2), .9 + .4 * i, .9 + .4 * i, "#d8f0ff"))
    if acc_on(d, k, "wave_marks", .2) or acc_on(d, k, "bands"):
        for i in range(2 + int(k * 2)):
            x = bx - brx * .5 + i * brx * .35
            over.append(E(x, by - bry * .25, .9, bry * .45, d.acc2 if d.has("bands") else "#d8f0ff", .2))
    if acc_on(d, k, "tail_fin") and tail_tip:
        top.append(P([(tail_tip[0] - 1, tail_tip[1]), (tail_tip[0] + 4 + 2 * k, tail_tip[1] - 4 - 2 * k), (tail_tip[0] + 2, tail_tip[1] + 1),
                      (tail_tip[0] + 4 + 2 * k, tail_tip[1] + 4)], d.acc))
    if acc_on(d, k, "head_leaf"):
        top += leaf(hx_ + hr * .1, hy - hr * .85, 5 + 5 * k, .35 + an["sway"] * .4)
        if k > .5:
            top += leaf(hx_ - hr * .2, hy - hr * .85, 4 + 4 * k, -.4 + an["sway"] * .4, "#6cc25a")
    if acc_on(d, k, "back_bulb"):
        x, y = ell_top(bx, by, brx, bry, .05)
        sz = 3.5 + 4.5 * k
        for a in (-1.0, -.3, .4, 1.1):
            back += leaf(x, y + 1, sz * 1.4, a + an["sway"] * .2, "#4caf3a" if a < 0 else "#5fc04a")
        back.append(E(x, y - sz * .4, sz * .7, sz * .75, "#7ac86a" if k < .6 else d.acc))
        if k > .6:
            back += [E(x + math.sin(a) * sz * .7, y - sz * .4 - math.cos(a) * sz * .7, sz * .35, sz * .5, "#f070a0", a) for a in (-1.2, -.4, .4, 1.2)]
    if acc_on(d, k, "leaf_collar", .2):
        for i in range(5):
            a = 2.0 + i * .55
            over += leaf(hx_ + hr * .2, hy + hr * .55, 3 + 3 * k, a, "#5fb04a")
    if acc_on(d, k, "back_flower", .3):
        x, y = ell_top(bx, by, brx, bry, .1)
        for i in range(6):
            a = i * 1.047 + an["sway"] * .2
            back.append(E(x + math.sin(a) * (2.5 + 2 * k), y - 3 - 2 * k - math.cos(a) * (2.5 + 2 * k), 1.6 + k, 2.4 + 1.5 * k, d.acc, a))
        back.append(E(x, y - 3 - 2 * k, 1.5 + k, 1.5 + k, "#ffe066"))
    if acc_on(d, k, "tail_leaf") and tail_tip:
        top += leaf(tail_tip[0], tail_tip[1], 6 + 4 * k, .7 + an["sway"] * .4)
    if acc_on(d, k, "tail_bolt") and tail_tip:
        top += bolt(tail_tip[0] - 1, tail_tip[1] + 2, 3.5 + 2.5 * k, .4 + an["sway"] * .3)
    if acc_on(d, k, "bolt_marks", .2):
        over += bolt(bx - brx * .1, by + bry * .1, 2.5 + 1.5 * k, .2, d.acc if d.acc != d.a else "#ffd83a")
    if acc_on(d, k, "spiky_crest", .2):
        pts = [(hx_ + hr * (-.3 + .35 * i), hy - hr * (.9 - .05 * i)) for i in range(3)]
        back += spike_row(pts, 3 + 2.5 * k, d.acc, lambda i: .3 + i * .35)
    if acc_on(d, k, "antenna_balls") or acc_on(d, k, "antennae"):
        for dx, lean in ((-.35, -.35), (.15, .25)):
            seg, tip = curve(hx_ + hr * dx, hy - hr * .8, lean, 5 + 3 * k, .5, .9, .7, d.d)
            back += seg
            if d.has("antenna_balls"):
                back.append(E(tip[0], tip[1], 1.5 + .5 * k, 1.5 + .5 * k, "#ffd83a"))
    if acc_on(d, k, "cheeks") or acc_on(d, k, "heart_cheeks"):
        pass  # 腮红在 face 里画
    if acc_on(d, k, "back_crystals", .2):
        back += [c for i, (x, y) in enumerate(top_pts(n)) for c in crystal(x, y + 1.5, 3 + 2.5 * k, -.4 + .8 * i / max(1, n - 1))]
    if acc_on(d, k, "ice_crown", .3):
        for i in range(3):
            top += crystal(hx_ + hr * (-.45 + i * .4), hy - hr * .8, 2 + 2 * k + (1.5 if i == 1 else 0), -.35 + i * .35)
    if acc_on(d, k, "frost_ruff", .2):
        over += spike_row([(hx_ + hr * (.2 + .25 * i), hy + hr * (.6 + .1 * i)) for i in range(3)], 2.5 + 2 * k, "#e8f8ff", lambda i: 2.4 - i * .3, .6)
        over.append(E(hx_ + hr * .4, hy + hr * .8, hr * .8, hr * .4, "#e8f8ff"))
    if acc_on(d, k, "icicles", .4):
        for i in range(3):
            x = hx_ - hr * (.3 + .25 * i)
            top.append(P([(x - .8, hy + hr * .75), (x, hy + hr * .75 + 2.5 + k), (x + .8, hy + hr * .75)], "#d8f4ff", "!"))
    if acc_on(d, k, "wristbands") or acc_on(d, k, "belt"):
        if d.has("belt"):
            over.append(E(bx, by + bry * .25, brx * .95, 1.4, "#3a3048", 0, "!"))
            over.append(E(bx - brx * .2, by + bry * .25, 1.6, 1.6, "#f0c040", 0, "!"))
    if acc_on(d, k, "headband"):
        top.append(E(hx_, hy - hr * .45, hr * 1.0, hr * .2, "#e04a3a"))
        top += [L(hx_ + hr * .9, hy - hr * .45, hx_ + hr * 1.6, hy - hr * .2 + an["sway"] * 2, 1.2, "#e04a3a")]
    if acc_on(d, k, "scar", .5):
        top.append(L(hx_ - hr * .5, hy - hr * .55, hx_ - hr * .1, hy - hr * .05, .7, "#f0e0e0", "!"))
    if acc_on(d, k, "poison_spots") or (d.t1 == "毒" and d.pattern == "spots"):
        for i in range(3 + int(k * 3)):
            a = -2.5 + i * 1.1
            over.append(E(bx + math.cos(a) * brx * .5, by + math.sin(a) * bry * .45, 1.2 + .4 * (i % 2), 1.0 + .3 * (i % 2), "#c06ae0"))
    if acc_on(d, k, "back_spikes", .2) or acc_on(d, k, "back_ridge") or acc_on(d, k, "spiky_ruff", .3):
        c = {"back_spikes": "#c06ae0", "back_ridge": d.acc2, "spiky_ruff": d.d}
        key = "back_spikes" if d.has("back_spikes") else "back_ridge" if d.has("back_ridge") else "spiky_ruff"
        back += spike_row(top_pts(n + 1), 2.5 + 2.5 * k, c[key], lambda i: -.4 + .8 * i / max(1, n))
    if acc_on(d, k, "drip"):
        top.append(E(hx_ - hr * .5, hy + hr * .85 + (an["ph"] % 1), .8, 1.2, "#c06ae0", 0, "!"))
    if acc_on(d, k, "gas", .4):
        for i in range(3):
            t = (an["ph"] / (2 * math.pi) + i / 3) % 1.0
            back.append(E(bx + brx * (.6 - .4 * i), by - bry - 2 - t * 6, 1.5 + t * 2, 1.2 + t * 1.6, "#b890d0"))
    if acc_on(d, k, "rock_armor", .3) or acc_on(d, k, "back_rocks", .1):
        for i, (x, y) in enumerate(top_pts(n, -.6, .6)):
            s = 2.2 + 1.8 * k
            over.append(P([(x - s, y + s * .6), (x - s * .6, y - s * .7), (x + s * .4, y - s), (x + s, y + s * .4)], "#a89070" if d.t1 != "岩石" else d.acc2))
    if acc_on(d, k, "mud_marks"):
        over += [E(bx - brx * .3, by + bry * .3, 2, 1.3, "#8a6a40"), E(bx + brx * .3, by + bry * .1, 1.6, 1.1, "#8a6a40")]
    if acc_on(d, k, "forehead_gem"):
        top.append(E(hx_ - hr * .35, hy - hr * .55, 1.2 + .6 * k, 1.0 + .5 * k, "#ff4a8a", 0, "!"))
    if acc_on(d, k, "third_eye", .4):
        top.append(E(hx_ - hr * .38, hy - hr * .6, 1.0 + .5 * k, 1.4 + .5 * k, "#ffe066", 0, "!"))
        top.append(E(hx_ - hr * .38, hy - hr * .6, .5, .8, INK, 0, "!"))
    if acc_on(d, k, "orbs", .3):
        for i in range(2 + int(k)):
            a = an["ph"] + i * 2.1
            back.append(E(bx + math.cos(a) * (brx + 4), by - bry - 1 + math.sin(a) * 2.5, 1.5 + .5 * k, 1.5 + .5 * k, d.acc))
    if acc_on(d, k, "halo", .5):
        back.append(E(hx_, hy - hr * 1.3, hr * .9, hr * .25, "#ffe9a0"))
        back.append(E(hx_, hy - hr * 1.3, hr * .65, hr * .12, d.a))
    if acc_on(d, k, "small_wings", .3) or acc_on(d, k, "fairy_wings"):
        c = "#e8f6ff" if not d.has("fairy_wings") else mix(d.acc, "#ffffff", .6)
        x, y = ell_top(bx, by, brx, bry, .15)
        fl2 = an["flap"] * .4
        back += [E(x + 3, y - 3, 2.5 + 1.5 * k, 5 + 3 * k, c, .6 - fl2), E(x + 1, y - 2, 2 + k, 4 + 2 * k, c, -.1 - fl2)]
    if acc_on(d, k, "armor_plates", .3):
        for i, (x, y) in enumerate(top_pts(max(2, n - 1), -.5, .5)):
            over.append(E(x, y + 2, 3 + 1.5 * k, 2 + k, "#c0c8d4" if d.t1 != "岩石" else "#8a7a5a", .3 * (i - 1)))
    if acc_on(d, k, "crystal_horn", .4):
        top += crystal(hx_ - hr * .25, hy - hr * .85, 3 + 3 * k, -.25, mix(d.acc, "#ffffff", .5))
    if acc_on(d, k, "ghost_tail") and tail_tip:
        pass
    if acc_on(d, k, "wisps", .2):
        for i in range(2 + int(k)):
            a = an["ph"] * .8 + i * 2.4
            x, y = bx + math.cos(a) * (brx + 5), by - bry + math.sin(a) * 3
            back += flame(x, y, 1.6 + k, 0, .3) if False else [E(x, y, 1.5 + .5 * k, 2 + .6 * k, "#9a8aff"), E(x, y + .5, .7, 1, "#e8e0ff")]
    if acc_on(d, k, "stitches", .3):
        x0 = bx - brx * .3
        over += [L(x0, by - bry * .4, x0 + brx * .6, by - bry * .2, .5, INK)] + [L(x0 + brx * .15 * i, by - bry * .55, x0 + brx * .15 * i, by - bry * .05, .5, INK) for i in range(1, 4)]
    if acc_on(d, k, "dragon_horns", .2) and not d.has("no_head_horns"):
        ln = 3 + 4.5 * k
        top += horn(hx_ + hr * .35, hy - hr * .75, ln, .9, 1.6 + .6 * k, d.horn_c, .4)
        top += horn(hx_ - hr * .15, hy - hr * .82, ln * .85, .5, 1.4 + .5 * k, d.horn_c, .4)
    if acc_on(d, k, "whiskers", .4):
        for i in range(2):
            seg, _ = curve(hx_ - hr * .9, hy + hr * .15, -1.9 - .3 * i, 5 + 4 * k, -.8 + an["sway"], .8, .5, d.acc)
            top += seg
    if acc_on(d, k, "mask", .1):
        top.append(E(hx_ - hr * .38, hy - hr * .12, hr * .72, hr * .3, "#3a3040", -.05, "!"))
    if acc_on(d, k, "claw_marks", .5):
        over += [L(bx - brx * .2 + i * 1.3, by - bry * .4, bx - brx * .2 + i * 1.3 + 1.5, by + bry * .1, .6, "#c03040") for i in range(3)]
    if acc_on(d, k, "helmet", .3):
        top.append(E(hx_ + hr * .1, hy - hr * .5, hr * .95, hr * .55, "#c0c8d4"))
        top.append(P([(hx_ - hr * .1, hy - hr * 1.0), (hx_ + hr * .2, hy - hr * 1.6 - k * 2), (hx_ + hr * .5, hy - hr * .95)], "#c0c8d4"))
    if acc_on(d, k, "blade_fins", .3):
        x, y = ell_top(bx, by, brx, bry, .2)
        back += [P([(x - 2, y + 1), (x + 5 + 3 * k, y - 6 - 4 * k), (x + 3, y + 1)], "#d8e0ea"), P([(x - 5, y + 1), (x - 1 + 2 * k, y - 4 - 3 * k), (x - 1, y + 1)], "#d8e0ea")]
    if acc_on(d, k, "bolts"):
        over += [E(bx - brx * .4, by - bry * .2, .9, .9, "#e8ecf0"), E(bx + brx * .3, by - bry * .3, .9, .9, "#e8ecf0")]
    if acc_on(d, k, "ribbon"):
        x, y = hx_ + hr * .55, hy - hr * .7
        top += [P([(x, y), (x - 3.5, y - 2.5), (x - 3.5, y + 2)], "#ff7ab0"), P([(x, y), (x + 3.5, y - 2.5), (x + 3.5, y + 2)], "#ff7ab0"),
                E(x, y, 1.2, 1.2, "#ff4a8a")]
    if acc_on(d, k, "star_mark"):
        over += star(bx - brx * .2, by - bry * .05, 2 + k, "#fff0a0")
    if acc_on(d, k, "flower_crown", .3):
        for i in range(4):
            x = hx_ + hr * (-.6 + i * .4)
            top.append(E(x, hy - hr * .82, 1.4, 1.4, ["#ff9ac0", "#fff0a0", "#a0d8ff", "#ffffff"][i]))
    if acc_on(d, k, "scarf", .2):
        over.append(E(hx_ + hr * .35, hy + hr * .85, hr * .85, hr * .35, d.acc, .2))
        over.append(L(hx_ + hr * .9, hy + hr * .9, hx_ + hr * 1.6 + an["sway"] * 2, hy + hr * 1.8, 1.8, d.acc))
    if acc_on(d, k, "collar"):
        over.append(E(hx_ + hr * .35, hy + hr * .85, hr * .75, hr * .22, "#c03a3a", .2))
        over.append(E(hx_ + hr * .0, hy + hr * 1.0, 1.1, 1.1, "#f0c040"))
    if acc_on(d, k, "patch"):
        over.append(E(bx + brx * .2, by - bry * .3, brx * .3, bry * .32, d.acc2, .3))
    if acc_on(d, k, "tuft"):
        top.append(P([(hx_ - hr * .2, hy - hr * .8), (hx_ - hr * .1 + an["sway"], hy - hr * 1.5 - k), (hx_ + hr * .15, hy - hr * .9),
                      (hx_ + hr * .4 + an["sway"], hy - hr * 1.35 - k), (hx_ + hr * .45, hy - hr * .7)], d.d))
    if acc_on(d, k, "crest_feathers"):
        for i in range(2 + int(k * 2)):
            seg, _ = curve(hx_ + hr * .1, hy - hr * .8, .3 + i * .3, 4 + 3 * k, .6 + an["sway"] * .3, 1.4, .8, d.acc if i % 2 else d.d)
            back += seg
    return back, over, top


def wings(d, k, x, y, span, an, style="feather", c1=None, c2=None):
    """一对翅膀，肩膀在 (x, y)，往右上方张开；远的那只先画、偏右、颜色暗"""
    fl = an["flap"] * .35
    s = span
    pal = {"a": d.a, "b": d.b, "d": d.d}
    c1 = pal.get(c1, c1) or d.d
    c2 = pal.get(c2, c2) or d.a
    out = []
    for far in (True, False):
        ox, oy = (2.5, -1.5) if far else (0, 0)
        cx, cy = x + ox, y + oy
        a0 = (-.15 if far else .35) - fl
        if style == "membrane":
            pts = [(0, 0), (s * .25, -s * .95), (s * .6, -s * .85), (s * .62, -s * .45), (s * .9, -s * .5), (s * .72, -s * .1), (s * .45, -s * .15), (s * .3, s * .15)]
            pts = rot([(cx + px, cy + py) for px, py in pts], cx, cy, a0)
            out.append(P(pts, d.acc2 if far else (c1 if c1 != d.d else d.acc)))
            out.append(L(cx, cy, pts[1][0], pts[1][1], 1.1, d.d))
            out.append(L(pts[1][0], pts[1][1], pts[3][0], pts[3][1], .7, d.d))
        else:
            # 羽翼：一根翼骨，末端张开 5 根飞羽，根部盖一层覆羽
            col1 = c1 if not far else hsv(c1, mv=.8)
            col2 = c2 if not far else hsv(c2, mv=.8)
            ex_, ey_ = polar(cx, cy, a0 + .5, s * .55)
            for i in range(5):
                fa = a0 + .25 + i * .32
                mx, my = polar(ex_, ey_, fa, s * (.42 - .03 * i))
                out.append(E(mx, my, s * .11, s * (.42 - .04 * i), col1, fa))
            out.append(L(cx, cy, ex_, ey_, s * .22, col2))
            mx, my = polar(cx, cy, a0 + .75, s * .32)
            out.append(E(mx, my, s * .24, s * .34, col2, a0 + .9))
    return out


# ------------------------------------------------------------------ 四足
def build_quad(d, k, an):
    q = QUAD[d.noun]
    v = d.v
    ex = set(q.get("ex", ()))
    g = 0.78 + 0.6 * k + (0.15 if d.legend else 0)
    pose = q.get("pose", "stand")
    if pose == "sit" and k > .7 and d.feature < .5:
        pose = "stand"  # 一部分坐姿原型进化后站起来
    if d.noun == "蜥" and d.feature > .45:
        pose = "kanga"  # 一半的蜥蜴线是直立的（像小火龙）
    bl = 7.2 * q["body"][0] * v["bl"] * g
    bh = 5.4 * q["body"][1] * v["bh"] * g * (1 + an["breath"])
    ll = 5.0 * q["legs"][0] * v["ll"] * (0.75 + 0.5 * k)
    lw = 2.4 * q["legs"][1] * (0.85 + 0.5 * k)
    hr = 5.6 * q["hr"] * v["hr"] * (1.0 + 0.32 * k) * (1.1 if d.legend else 1)
    sn = q.get("sn", .5) * v["sn"] * (0.75 + 0.35 * k)
    neck = q.get("neck", 0) * v["neck"]
    a, b, dk = "a", "b", "d"
    bob = an["bob"] * .7
    prims = []
    if pose == "low":
        ll *= .7
    if pose == "sit":
        bx, by = 2.0, -bh * 1.25 - 1
        brx, bry = bl * .62, bh * 1.25
    elif pose == "kanga":
        bx, by = 2.0, -ll - bh * 1.1
        brx, bry = bl * .6, bh * 1.2
    else:
        bx, by = 1.5, -(ll + bh * .65)
        brx, bry = bl, bh
    by += bob
    # 头的位置
    if pose == "sit" or pose == "kanga":
        hx_, hy = bx - brx * .55, by - bry * .85 - hr * .55
    elif pose == "low":
        hx_, hy = bx - brx * .95 - hr * .45, by - bry * .3 - hr * .2
    else:
        hx_ = bx - brx * .9 - neck * 4 - hr * .15
        hy = by - bry * .6 - neck * 6.5 - hr * .35
        if pose == "slope":
            hy -= 2
    hy += an["bob"] * .4
    head = (hx_, hy, hr)
    # 尾巴根
    if pose in ("sit", "kanga"):
        tx, ty = bx + brx * .75, by + bry * .55
    else:
        tx, ty = bx + brx * .92, by - bry * .25 + (2 if pose == "slope" else 0)
    tail_prims, tip = quad_tail(d, k, q, tx, ty, g, an, pose)
    back, over, top = body_acc(d, k, an, (bx, by, brx, bry), head, tip)

    # 远侧的腿（暗色）
    legs_far, legs_near = quad_legs(d, k, q, pose, bx, by, brx, bry, ll, lw, ex)
    prims += [p for p in legs_far]
    if "wings" in d.acc_list:
        prims += wings(d, k, bx - brx * .1, by - bry * .55, 8 + 9 * k, an, "membrane" if d.dragonish or d.t1 in ("恶", "幽灵") else "feather")
    prims += back
    prims += tail_prims
    if "hump" in ex:
        prims.append(E(bx + brx * .1, by - bry * .85, brx * .42, bry * .7, a))
        if k > .6:
            prims.append(E(bx - brx * .35, by - bry * .8, brx * .32, bry * .55, a))
    if "bigmane" in ex or "mane_flame" in d.acc_list and k > .4:
        mc = d.acc2 if d.scheme != "natural" else hsv(d.a, mv=.7, dh=-.03)
        mr = hr * (1.25 + .45 * k)
        for i in range(9):
            ang = -2.6 + i * .62
            prims.append(E(hx_ + hr * .35 + math.sin(ang) * mr * .55, hy + hr * .1 - math.cos(ang) * mr * .55, mr * .42, mr * .58, mc, ang))
        prims.append(E(hx_ + hr * .35, hy + hr * .15, mr * .85, mr * .9, mc))
    if "ruff" in ex and k > .3:
        prims.append(E(hx_ + hr * .55, hy + hr * .75, hr * (.7 + .3 * k), hr * (.55 + .2 * k), b, .4))
    # 身体
    if "wool" in ex:
        wc = "b" if d.scheme != "dark" else "a"
        for i in range(7):
            ang = i * .9
            prims.append(E(bx + math.cos(ang) * brx * .6, by + math.sin(ang) * bry * .55, brx * .5, bry * .55, wc))
        prims.append(E(bx, by, brx * .95, bry * .95, wc))
    else:
        prims.append(E(bx, by, brx, bry, a))
        prims += body_pattern(d, k, bx, by, brx, bry, pose, ex)
    if "shell" in ex or "bands" in ex or "scales" in ex or "plates" in ex:
        prims += quad_armor(d, k, ex, bx, by, brx, bry)
    if "mane" in ex and not neck:
        mc = d.acc if d.scheme != "natural" else hsv(d.a, mv=.55)
        pts = [(hx_ + hr * .5, hy - hr * .7)] + [(bx - brx * (.7 - .25 * i), by - bry * (1.05 - .05 * i)) for i in range(4)]
        for i, (x, y) in enumerate(pts):
            prims.append(E(x + 1, y + 1, 1.8 + k, 3.5 + 1.5 * k, mc, .9 + an["sway"] * .3))
    if "ridge" in ex or "ridge_hair" in ex or ("crest_opt" in ex and d.feature > .5):
        n = 4 + int(k * 3)
        pts = [ell_top(bx, by, brx, bry, -.8 + 1.6 * (i + .5) / n) for i in range(n)]
        prims += spike_row(pts, 1.8 + 1.8 * k, dk if "ridge_hair" not in ex else d.acc2, lambda i: -.5 + i / n)
    if neck > 0 and pose not in ("sit", "kanga", "low"):
        prims.append(L(bx - brx * .7, by - bry * .3, hx_ + hr * .25, hy + hr * .35, hr * .95, "a"))
        if "mane" in ex:
            mc = d.acc if d.scheme != "natural" else hsv(d.a, mv=.55)
            for i in range(4):
                t = i / 3
                x, y = bx - brx * .7 + (hx_ + hr * .3 - (bx - brx * .7)) * t, by - bry * .6 + (hy - hr * .6 - (by - bry * .6)) * t
                prims.append(E(x + 1.5, y, 1.8 + k, 3.2 + 1.2 * k, mc, .7 + an["sway"] * .3))
    prims += over
    prims += legs_near
    if pose == "kanga" and "pouch" in ex:
        prims.append(E(bx - brx * .35, by + bry * .35, brx * .45, bry * .4, b, .2, "!"))
    if "ruff" in ex or "frost_ruff" in d.acc_list:
        pass
    hp, face = quad_head(d, k, q, ex, hx_, hy, hr, sn, an)
    prims += hp + top
    return prims, face


def body_pattern(d, k, bx, by, brx, bry, pose, ex):
    out = []
    pat = d.pattern
    if "spots" in ex or d.noun == "豹":
        pat = "spots"
    if d.noun == "虎":
        pat = "stripes"
    if "dapples" in ex and k < .7:
        pat = "spots"
    # 肚皮 / 胸口
    if pat != "belly" and d.noun not in ("龟",):
        out.append(E(bx - brx * .45, by + bry * .35, brx * .5, bry * .55, "b", .4, "!"))
    else:
        out.append(E(bx, by + bry * .45, brx * .8, bry * .45, "b", 0, "!"))
    rr = random.Random(int(d.rng.random() * 1e9))
    if pat == "spots":
        c = "d" if d.t1 != "毒" else "#c06ae0"
        for i in range(4 + int(k * 4)):
            ang = rr.uniform(-2.8, -.2)
            rad = rr.uniform(.25, .75)
            out.append(E(bx + math.cos(ang) * brx * rad, by + math.sin(ang) * bry * rad * .9, 1.0 + .4 * k, .8 + .3 * k, c))
    elif pat == "stripes":
        for i in range(3 + int(k * 2)):
            x = bx - brx * .45 + i * brx * .3
            out.append(E(x, by - bry * .45, .8 + .3 * k, bry * .45, "d", .25))
    elif pat == "saddle":
        out.append(E(bx + brx * .1, by - bry * .55, brx * .65, bry * .38, d.acc2))
    elif pat == "bands":
        for i in range(2):
            out.append(E(bx - brx * .15 + i * brx * .4, by - bry * .1, 1.3, bry * .8, d.acc))
    return out


def quad_armor(d, k, ex, bx, by, brx, bry):
    out = []
    sc = d.acc2 if d.scheme in ("type", "split", "pastel") else hsv(d.a, dh=.05, mv=.75)
    if "shell" in ex:
        out.append(E(bx + .5, by - bry * .25, brx * 1.12, bry * 1.05, sc))
        out.append(E(bx + .5, by + bry * .55, brx * 1.12, bry * .22, "b"))
        for i in range(3):
            x = bx - brx * .45 + i * brx * .45
            out.append(E(x, by - bry * .45, brx * .2, bry * .3, hsv(sc, mv=1.15)))
        if k > .6:
            out += spike_row([ell_top(bx + .5, by - bry * .25, brx * 1.12, bry * 1.05, t) for t in (-.4, 0, .4)], 2 + 2 * k, d.horn_c)
    elif "bands" in ex:
        out.append(E(bx, by - bry * .2, brx * 1.05, bry * 1.0, sc))
        for i in range(4):
            x = bx - brx * .6 + i * brx * .4
            out.append(E(x, by - bry * .3, .6, bry * .75, hsv(sc, mv=.7)))
    elif "scales" in ex:
        for row in range(3):
            for i in range(4 - row):
                x = bx - brx * .6 + i * brx * .42 + row * brx * .2
                y = by - bry * .55 + row * bry * .45
                out.append(E(x, y, brx * .22, bry * .3, sc if (i + row) % 2 else hsv(sc, mv=1.12)))
    elif "plates" in ex and k > .3:
        out.append(E(bx - brx * .1, by - bry * .5, brx * .55, bry * .4, hsv(d.a, mv=1.12)))
        out.append(E(bx + brx * .45, by - bry * .35, brx * .35, bry * .38, hsv(d.a, mv=1.12)))
    return out


def quad_legs(d, k, q, pose, bx, by, brx, bry, ll, lw, ex):
    far, near = [], []
    paw = "d"
    sock = "b" if d.pattern == "socks" else "a"
    hoof = "hooves" in ex
    claws = "claws" in ex or "bigclaws" in ex or d.has("big_claws")
    if pose == "sit":
        # 后腿是一大块大腿，前腿直立
        far.append(E(bx + brx * .55 + 2, -2.2, lw * 1.0 + 1, 1.8, "d"))
        near += [E(bx + brx * .3, by + bry * .45, brx * .55, bry * .55, "a"), E(bx + brx * .05, -1.6, lw * 1.0 + 1.2, 1.9, sock)]
        for i, x in enumerate((bx - brx * .5 + 1.8, bx - brx * .5)):
            tgt = far if i == 0 else near
            tgt.append(L(x, by + bry * .1, x - .5, -1.6, lw, "d" if i == 0 else sock))
            tgt.append(E(x - .8, -1.4, lw * .75, 1.4, paw if i == 0 else sock))
    elif pose == "kanga":
        far.append(E(bx + 2, -1.6, lw * 2.2, 1.7, "d"))
        near += [E(bx + brx * .25, by + bry * .55, brx * .6, bry * .5, "a"), E(bx - 1, -1.8, lw * 2.4, 1.9, sock)]
        near.append(L(bx - brx * .6, by - bry * .2, bx - brx * 1.0, by + bry * .3, lw * .8, "a"))
    else:
        top_y = by + bry * .35
        slope = 1.5 if pose == "slope" else 0
        spread = 1.4 if pose == "low" else 0
        legs = [(bx - brx * .6, ll + slope), (bx + brx * .58, ll - slope)]
        for far_side in (True, False):
            tgt = far if far_side else near
            ox = 2.2 if far_side else 0
            for i, (x, _) in enumerate(legs):
                x = x + ox + (spread * (-1 if i == 0 else 1))
                c = "d" if far_side else sock
                if i == 1 and not far_side:
                    tgt.append(E(x - .5, top_y - bry * .2, brx * .32, bry * .55, "a", .2))  # 大腿
                tgt.append(L(x, top_y, x - spread * .6, -1.4, lw, c))
                if hoof:
                    tgt.append(E(x - spread * .6, -.9, lw * .62, 1.0, "#3a3030"))
                else:
                    tgt.append(E(x - spread * .6 - .6, -1.2, lw * .72, 1.3, c if far_side else sock))
                if claws and not far_side:
                    tgt += [P([(x - lw * .6 + j * 1.0, -.6), (x - lw * .6 + j * 1.0 - 1.0, .4), (x - lw * .6 + j * 1.0 + .3, -.3)], "#f4f0e8") for j in range(3)]
    return far, near


def quad_tail(d, k, q, tx, ty, g, an, pose):
    t = q.get("tail", "thin")
    sw = an["sway"] * (0.8 if t not in ("taper", "thick") else .25)
    tv = d.v["tail"] * (0.8 + .4 * k)
    out = []
    tip = None
    if d.nine and k >= .9:
        for i in range(9):
            a = .1 + i * .19 + sw * .4
            mx, my = polar(tx, ty, a, 7 * tv)
            out.append(E(mx, my, 2.6 * tv, 7 * tv, "a" if i % 2 else d.acc2, a))
            ex_, ey_ = polar(tx, ty, a, 13 * tv)
            out.append(E(ex_, ey_, 1.3 * tv, 1.8 * tv, "b", a))
        return out, polar(tx, ty, .9, 14 * tv)
    if t in ("bushy", "bushy_low", "thin_bushy", "ring"):
        a = (.55 if t == "bushy" else 1.25 if t == "bushy_low" else .9) + sw * .5
        ln = (11 if t != "thin_bushy" else 12) * tv
        w = (4.2 if t != "thin_bushy" else 2.6) * tv
        mx, my = polar(tx, ty, a, ln * .5)
        out.append(E(mx, my, w, ln * .55, "a", a))
        tip = polar(tx, ty, a, ln * .95)
        if t == "ring":
            for i in range(3):
                px, py = polar(tx, ty, a, ln * (.3 + .22 * i))
                out.append(E(px, py, w * .9, 1.0, "d", a + math.pi / 2))
        elif d.pattern == "tipped" or t == "bushy":
            px, py = polar(tx, ty, a, ln * .85)
            out.append(E(px, py, w * .75, ln * .2, "b", a))
    elif t in ("thin", "long", "wag"):
        a0 = {"thin": .9, "long": .4, "wag": .3}[t] + sw * (1.6 if t == "wag" else .8)
        seg, tip = curve(tx, ty, a0, (13 if t != "wag" else 7) * tv, (-.9 if t == "long" else .6), 1.8 * tv, 1.1 * tv, "a")
        out += seg
        if t == "long" and d.pattern == "tipped":
            out.append(E(tip[0], tip[1], 1.4, 1.4, "d"))
    elif t == "curl_long":
        seg, tip = curve(tx, ty, .3 + sw, 12 * tv, -2.6, 1.6, 1.2, "a", 7)
        out += seg
    elif t == "stub":
        out.append(E(tx + 1, ty - .5, 2.2 * tv, 2.0 * tv, "a", .5))
        tip = (tx + 2, ty - 1)
    elif t == "puff":
        out.append(E(tx + 1, ty - 1, 3.2 * tv, 3.0 * tv, "b"))
        tip = (tx + 2, ty - 2)
    elif t == "curl":
        out += [E(tx + 2, ty - 1.5, 2.2, 2.2, "a"), E(tx + 2, ty - 1.5, 1.0, 1.0, "d")]
        tip = (tx + 3, ty - 2)
    elif t == "tuft":
        seg, tip = curve(tx, ty, 1.9 + sw * .6, 9 * tv, .5, 1.1, .9, "a")
        out += seg + [E(tip[0], tip[1], 1.6 * tv, 2.4 * tv, "d", 2.2)]
    elif t == "hair":
        for i in range(3):
            a = 1.8 + i * .25 + sw * .5
            mx, my = polar(tx, ty, a, 5 * tv)
            out.append(E(mx, my, 1.6 * tv, 6 * tv, d.acc if d.scheme != "natural" else "d", a))
        tip = polar(tx, ty, 2.0, 10 * tv)
    elif t in ("taper", "thick"):
        w0 = (3.2 if t == "thick" else 2.2) * (0.8 + .5 * k)
        ln = (13 if t == "thick" else 14) * tv
        ang = 1.75 + sw * .4
        x2, y2 = polar(tx, ty, ang, ln)
        x2, y2 = x2, min(y2, -1.2)
        nx_, ny_ = -(y2 - ty) / ln, (x2 - tx) / ln
        out.append(P([(tx + nx_ * w0, ty + ny_ * w0), (x2, y2), (tx - nx_ * w0, ty - ny_ * w0)], "a"))
        tip = (x2, y2)
        if t == "thick" and k > .3:
            out += spike_row([(tx + (x2 - tx) * f, ty + (y2 - ty) * f - w0 * (1 - f) * .8) for f in (.2, .45, .7)], 1.5 + k, "d", lambda i: .6)
    elif t == "flat":
        out.append(E(tx + 4 * tv, ty + 2.5, 5 * tv, 2 * tv, "d", .2 + sw * .2))
        tip = (tx + 8 * tv, ty + 2.5)
    return out, tip


def quad_head(d, k, q, ex, hx_, hy, hr, sn, an):
    out = []
    ear = q.get("ear", "point")
    ev = d.v["ear"]
    twitch = .35 if 16 <= an["f"] <= 17 else 0.0
    behind, front = [], []
    # 耳朵
    if ear in ("point", "tall", "small"):
        h = hr * {"point": .85, "tall": 1.25, "small": .45}[ear] * ev
        for far, (bxe, bye, a) in ((True, (hx_ - hr * .45, hy - hr * .65, -.35)), (False, (hx_ + hr * .3, hy - hr * .75, .25 + twitch))):
            c = "d" if far else "a"
            behind += horn(bxe, bye, h, a, hr * .62, c)
            if not far:
                behind += horn(bxe, bye - .4, h * .65, a, hr * .34, "b" if d.scheme != "dark" else d.acc, 0)
    elif ear == "round":
        for far, (bxe, bye) in ((True, (hx_ - hr * .5, hy - hr * .75)), (False, (hx_ + hr * .4, hy - hr * .8))):
            r_ = hr * .38 * ev
            behind.append(E(bxe, bye - (twitch if not far else 0), r_, r_, "d" if far else "a"))
            if not far:
                behind.append(E(bxe, bye - twitch, r_ * .55, r_ * .55, "b"))
    elif ear == "long":
        for far, (bxe, bye, a) in ((True, (hx_ - hr * .25, hy - hr * .8, -.15)), (False, (hx_ + hr * .3, hy - hr * .85, .3 + twitch))):
            ln = hr * 1.6 * ev
            cx, cy = polar(bxe, bye, a, ln * .5)
            behind.append(E(cx, cy, hr * .3, ln * .5, "d" if far else "a", a))
            if not far:
                behind.append(E(cx, cy + .3, hr * .15, ln * .38, "b", a))
    elif ear == "droop":
        front.append(E(hx_ + hr * .55, hy + hr * .1, hr * .32 * ev, hr * .72 * ev, "d", .35 + twitch * .3))
        behind.append(E(hx_ - hr * .6, hy - hr * .05, hr * .28 * ev, hr * .6 * ev, "d", -.4))
    elif ear == "side":
        for far, (bxe, bye, a) in ((True, (hx_ - hr * .7, hy - hr * .4, -1.3)), (False, (hx_ + hr * .55, hy - hr * .45, 1.25 + twitch))):
            cx, cy = polar(bxe, bye, a, hr * .5 * ev)
            behind.append(E(cx, cy, hr * .25 * ev, hr * .55 * ev, "d" if far else "a", a))
    elif ear == "fan":
        front.append(E(hx_ + hr * .45, hy + hr * .05, hr * .75 * ev, hr * .95 * ev, "a", .15 + an["sway"] * .25))
        front.append(E(hx_ + hr * .5, hy + hr * .05, hr * .5 * ev, hr * .7 * ev, hsv(d.a, mv=.85, dh=-.02), .15 + an["sway"] * .25, "!"))
    # 角
    hn = q.get("horn")
    if hn == "twin":
        ln = hr * (.6 + .9 * k)
        behind += horn(hx_ - hr * .55, hy - hr * .6, ln, -.9, hr * .3, hsv(d.horn_c, mv=.85), .9)
        front += horn(hx_ + hr * .3, hy - hr * .7, ln, .9, hr * .32, d.horn_c, -.9)
    elif hn == "ram" and k > .2:
        rr = hr * (.35 + .3 * k)
        front += [E(hx_ + hr * .35, hy - hr * .2, rr, rr, d.horn_c), E(hx_ + hr * .35, hy - hr * .2, rr * .55, rr * .55, hsv(d.horn_c, mv=.75)),
                  E(hx_ + hr * .35, hy - hr * .2, rr * .25, rr * .25, d.horn_c)]
    elif hn == "antler" and k > .25:
        for far, (x0, y0, a) in ((True, (hx_ - hr * .35, hy - hr * .7, -.35)), (False, (hx_ + hr * .2, hy - hr * .8, .3))):
            c = hsv(d.horn_c, mv=.85) if far else d.horn_c
            ln = hr * (.8 + 1.1 * k)
            seg, tip = curve(x0, y0, a, ln, .5 * (1 if not far else -1), 1.3, 1.0, c, 3)
            behind += seg
            for j in range(1 + int(k * 2)):
                px, py = polar(x0, y0, a, ln * (.4 + .25 * j))
                s2, _ = curve(px, py, a + (.9 if not far else -.9), ln * .35, 0, 1.0, .8, c, 2)
                behind += s2
    elif hn == "nub" and k > .3:
        front += horn(hx_ - hr * .3, hy - hr * .85, 2 + 2 * k, -.1, 1.6, d.horn_c)
    # 头
    out += behind
    out.append(E(hx_, hy, hr * 1.04, hr, "a"))
    if "face" in ex:
        out.append(E(hx_ - hr * .35, hy + hr * .05, hr * .62, hr * .7, "b", 0, "!"))
    if "mask" in ex:
        out.append(E(hx_ - hr * .4, hy - hr * .1, hr * .66, hr * .28, "#3a3040", 0, "!"))
    if "stripe_head" in ex:
        out.append(E(hx_ - hr * .1, hy - hr * .45, hr * .9, hr * .22, "b", -.15))
    if d.pattern == "stripes" and k > .3:
        out += [E(hx_ + hr * .1 + i * hr * .3, hy - hr * .7, .7, hr * .25, "d", .2) for i in range(2)]
    # 口鼻
    if sn > .05:
        sw_ = q.get("sw", 1.0)
        sx = hx_ - hr * (.55 + .4 * sn)
        sy = hy + hr * .25
        srx, sry = hr * (.32 + .4 * sn), hr * .4 * sw_ * (1.0 if sn < 1.2 else .7)
        snout_c = "b" if d.feature < .45 and "teeth" not in ex else "a"
        out.append(E(sx, sy, srx, sry, snout_c, -.05))
        nx_, ny_ = sx - srx * .85, sy - sry * .45
        if "pignose" in ex:
            out += [E(sx - srx * .75, sy, srx * .35, sry * .7, "#f0b0b8"), E(sx - srx * .85, sy - sry * .2, .5, .7, INK, 0, "!"), E(sx - srx * .65, sy - sry * .2, .5, .7, INK, 0, "!")]
        elif "pinknose" in ex:
            out.append(E(nx_, ny_, 1.9, 1.5, "#f08aa0"))
        else:
            out.append(E(nx_, ny_, 1.3 + .3 * k, 1.0, INK, 0, "!"))
        if "teeth" in ex:
            out += [P([(sx - srx * .8 + i * srx * .4, sy + sry * .35), (sx - srx * .8 + i * srx * .4 + .5, sy + sry * .95), (sx - srx * .8 + i * srx * .4 + 1, sy + sry * .35)], "#fff8f0", "!") for i in range(4)]
        mouth = (d.mouth if d.mouth != "fang" else "cat", sx - srx * .15, sy + sry * .5)
        if "trunk" in ex:
            mouth = None
        if "whisker" in ex:
            out += [L(sx - srx * .3, sy + .3 * i, sx - srx * 1.3, sy - 1 + 1.2 * i, .5, "#f4f0e8", "!") for i in range(2)]
    else:
        mouth = (d.mouth if d.mouth != "fang" else "cat", hx_ - hr * .45, hy + hr * .48)
        if "trunk" in ex:
            mouth = None
        if "whisker" in ex:
            out += [L(hx_ - hr * .6, hy + hr * .3 + .4 * i, hx_ - hr * 1.5, hy + hr * .1 + 1.2 * i, .5, "#f4f0e8", "!") for i in range(2)]
    if hn == "nose":
        nx0 = hx_ - hr * (.55 + .4 * sn) - hr * (.32 + .4 * sn) * .55
        out += horn(nx0, hy - hr * .05, hr * (.55 + .7 * k), -.25, hr * .45, d.horn_c, .35)
        if k > .6:
            out += horn(nx0 + hr * .55, hy - hr * .3, hr * .45, -.1, hr * .3, d.horn_c, .2)
    if hn == "tusk" and k > .3:
        out += horn(hx_ - hr * .65, hy + hr * .55, hr * (.4 + .5 * k), -1.9, hr * .22, "#fff8e8", -.6)
    out += front
    if "trunk" in ex:
        seg, _ = curve(hx_ - hr * .75, hy + hr * .15, 3.6 + an["sway"] * .3, hr * (1.5 + .6 * k), -1.3 + an["sway"] * .8, hr * .62, hr * .36, "a", 6)
        out += seg
    face = eyes_spec(d, k, hx_, hy, hr)
    if "tinyeyes" in ex:
        face["eye_size"] *= .55
    face["mouth"] = mouth
    if d.cheek or d.has("cheeks"):
        face["blush"] = [(hx_ - hr * .45, hy + hr * .32)]
        out.append(E(hx_ - hr * .1, hy + hr * .35, hr * .22, hr * .2, "#ff6a5a" if d.t1 == "电" else "#ff9aa8", 0, "!"))
    out += brows(d, k, face["eyes"], face["eye_size"])
    if d.mouth == "fang" and mouth:
        out.append(P([(mouth[1] + .5, mouth[2] + .6), (mouth[1] + 1.2, mouth[2] + 2.2), (mouth[1] + 1.8, mouth[2] + .6)], "#ffffff", "!"))
    return out, face


# ------------------------------------------------------------------ 鸟
def build_bird(d, k, an):
    q = BIRD[d.noun]
    ex = set(q.get("ex", ()))
    g = .8 + .55 * k + (.15 if d.legend else 0)
    v = d.v
    br = 6.8 * g * q["body"][1] * v["bh"] * (1 + an["breath"])
    bl = 7.5 * g * q["body"][0] * v["bl"]
    ll = 4.5 * q["legs"] * v["ll"] * (.8 + .4 * k)
    neck = q["neck"] * v["neck"] * (5 + 3 * k)
    hop = -abs(math.sin(an["ph"])) * 1.2 if d.noun in ("雀", "鸟") and k < .5 else an["bob"] * .5
    bx, by = 1.5, -ll - br + hop
    hr = (4.6 + 1.2 * k) * v["hr"] * (1.25 if "owlface" in ex else 1)
    if d.noun == "鸮":
        hx_, hy = bx - .5, by - br * .75 - hr * .4
    elif neck > 1:
        hx_, hy = bx - bl * .55 - neck * .45, by - br * .5 - neck
    else:
        hx_, hy = bx - bl * .55, by - br * .65 - hr * .25
    hy += an["bob"] * .3
    out = []
    # 远腿、尾、远翼
    for i, x in enumerate((bx + 1.5, bx - 1.2)):
        c = "#d8902a" if i == 0 else "#f2a33a"
        out.append(L(x, by + br * .7, x, -1.0, 1.0 + .4 * k, c))
        out.append(P([(x - 2.2, 0), (x, -1.4), (x + 1.2, 0)], c))
    tx, ty = bx + bl * .8, by + br * .1
    tl = 7 * v["tail"] * (.8 + .5 * k)
    tt = q["tail"]
    sw = an["sway"] * .3
    if tt == "fan":
        for i in range(3 + int(k * 2)):
            a = 1.5 + (i - 1.5) * .25 + sw
            mx, my = polar(tx, ty, a, tl * .55)
            out.append(E(mx, my, 1.8, tl * .6, "d" if i % 2 else "a", a))
    elif tt == "fork":
        for a in (1.75, 2.15):
            seg, _ = curve(tx, ty, a + sw, tl * 1.4, .1, 2.2, .6, "d", 4)
            out += seg
    elif tt == "plume":
        for i in range(3):
            seg, tip = curve(tx, ty, 1.0 + i * .35 + sw, tl * (1.4 + .4 * k), .7, 2.2, 1.0, d.acc if i == 1 else "d", 5)
            out += seg + [E(tip[0], tip[1], 1.6, 1.6, d.acc)]
    else:
        out.append(P([(tx - 1, ty - 2), (tx + tl * .8, ty + 1 + sw * 3), (tx - 1, ty + 2.5)], "d"))
    wing = q["wing"]
    if wing == "spread" and k < .4:
        wing = "half"
    if wing in ("spread", "swept"):
        out += wings(d, k, bx + bl * .1, by - br * .35, (9 + 9 * k) * (1.2 if d.noun == "鹏" else 1), an, "feather", "d", "a")[:2]
    # 脖子和身体
    back, over, top = body_acc(d, k, an, (bx, by, bl, br), (hx_, hy, hr), (tx + tl * .8, ty))
    out += back
    if neck > 1:
        out.append(L(bx - bl * .4, by - br * .3, hx_ + hr * .2, hy + hr * .3, hr * 1.1, "a"))
    out.append(E(bx, by, bl, br, "a", -.15))
    out.append(E(bx - bl * .3, by + br * .25, bl * .6, br * .62, "b", -.15, "!"))
    if "neckshine" in ex:
        out.append(E(hx_ + hr * .4, hy + hr * 1.0, hr * .8, hr * .5, mix(d.acc, "#a0e0c0", .5)))
    if d.pattern in ("spots", "stripes"):
        out += [E(bx - bl * .35 + i * 2.2, by + br * .15 + (i % 2) * 2, .8, 1.2, "d", 0, "!") for i in range(3)]
    out += over
    # 近翼
    if wing in ("spread", "swept"):
        out += wings(d, k, bx + bl * .1, by - br * .35, (9 + 9 * k) * (1.2 if d.noun == "鹏" else 1), an, "feather", "d", "a")[2:]
    else:
        fl = an["flap"] * (.25 if wing == "half" else .06)
        wl = bl * (1.0 if wing == "fold" else 1.2)
        out.append(E(bx + bl * .25, by - br * .05, wl * .62, br * .55, "d", .35 - fl))
        out.append(E(bx + bl * .15, by - br * .2, wl * .42, br * .38, d.acc if d.feature < .4 else "a", .35 - fl))
    # 头
    if "tufts" in ex:
        out += horn(hx_ - hr * .55, hy - hr * .7, hr * .7, -.4, hr * .4, "d") + horn(hx_ + hr * .55, hy - hr * .7, hr * .7, .4, hr * .4, "d")
    if "crest" in ex or d.feature > .7 or "redcap" in ex and False:
        for i in range(2 + int(k * 2)):
            seg, _ = curve(hx_ + hr * .2, hy - hr * .75, .4 + i * .32 + an["sway"] * .3, hr * (.9 + .5 * k), .6, 1.5, .8, d.acc if i % 2 == 0 else "d")
            out += seg
    out.append(E(hx_, hy, hr * 1.05, hr, "a"))
    if "owlface" in ex:
        out += [E(hx_ - hr * .55, hy, hr * .55, hr * .62, "b", 0, "!"), E(hx_ + hr * .3, hy, hr * .55, hr * .62, "b", 0, "!")]
    if "redcap" in ex:
        out.append(E(hx_ + hr * .1, hy - hr * .7, hr * .5, hr * .3, "#e04040"))
    if "tearmark" in ex:
        out.append(E(hx_ - hr * .25, hy + hr * .45, hr * .15, hr * .4, "d", -.2, "!"))
    beak = q["beak"]
    bc = "#f2b33a" if d.feature < .7 else d.horn_c
    by_ = hy + hr * .15
    bxl = hx_ - hr * .85
    if beak == "short":
        out.append(P([(bxl + 1, by_ - 1.6), (bxl - 3 - k, by_ + .2), (bxl + 1, by_ + 1.4)], bc))
    elif beak == "tiny":
        out.append(P([(hx_ - hr * .2, by_ - .4), (hx_ - hr * .3, by_ + 2), (hx_ - hr * .05, by_ - .2)], bc, "!"))
    elif beak == "bill":
        out.append(E(bxl - 1.5, by_ + .4, 3.5 + k, 1.6, "#f2a33a", -.1))
    elif beak == "hook":
        out += [P([(bxl + 1.5, by_ - 2.2), (bxl - 2.5 - k, by_ - 1.0), (bxl - 3 - k, by_ + 1.8), (bxl - 1, by_ + .6), (bxl + 1.5, by_ + 1.2)], "#f2c84a")]
    elif beak in ("long", "long_short"):
        ln = (9 + 4 * k) if beak == "long" else (4 + 1.5 * k)
        out.append(P([(bxl + 1, by_ - 1.3), (bxl - ln, by_ + .8), (bxl + 1, by_ + 1.2)], bc if beak == "long" else "#3a3040"))
    out += top
    face = eyes_spec(d, k, hx_, hy, hr, look=(.6 if "owlface" in ex else 1))
    if "owlface" in ex:
        face["eyes"] = [(hx_ - hr * .55, hy - hr * .05, 1.0), (hx_ + hr * .3, hy - hr * .05, 1.0)]
        face["eye_size"] *= 1.15
    face["mouth"] = None
    if "brow" in ex and k > .3:
        out += [P([(e[0] - 2.5, e[1] - 2.6), (e[0] + 2.5, e[1] - 3.6), (e[0] + 2.3, e[1] - 1.8)], "d", "!") for e in face["eyes"][:1]]
    out += brows(d, k, face["eyes"], face["eye_size"])
    return out, face


# ------------------------------------------------------------------ 鱼
def build_fish(d, k, an):
    q = FISH[d.noun]
    ex = set(q.get("ex", ()))
    g = .8 + .6 * k + (.15 if d.legend else 0)
    shape = q["shape"]
    rx = {"oval": 10, "long": 12.5, "round": 11.5, "ray": 11}[shape] * g * d.v["bl"]
    ry = {"oval": 7, "long": 5.5, "round": 8.5, "ray": 4.5}[shape] * g * d.v["bh"]
    sw = an["sway"]
    by = -ry - 5 + math.sin(an["ph"]) * 1.5
    bx = 1.5
    out = []
    tx = bx + rx * .85
    tf = q["tailf"]
    if tf == "fork":
        out.append(P(rot([(tx - 2, by), (tx + 7 + 3 * k, by - 6 - 2 * k), (tx + 4, by), (tx + 7 + 3 * k, by + 6 + 2 * k)], tx, by, sw * .4), "d"))
    elif tf == "flowing":
        for i, a in enumerate((-.5, .0, .5)):
            out.append(E(tx + 5 + 2 * k, by + a * 8, 6 + 2 * k, 2.5, d.acc if i == 1 else "d", a * .8 + sw * .5))
    elif tf == "crescent":
        out.append(P(rot([(tx - 2, by), (tx + 6 + 2 * k, by - 9 - 3 * k), (tx + 3, by), (tx + 7 + 2 * k, by + 6 + 2 * k)], tx, by, sw * .3), "a"))
    elif tf == "fluke":
        out.append(P(rot([(tx - 2, by - 1), (tx + 5, by - 3 - 3 * k), (tx + 10 + 3 * k, by - 5 - 2 * k), (tx + 8, by), (tx + 10 + 3 * k, by + 4), (tx + 4, by + 2)], tx, by, sw * .3 - .2), "a"))
    elif tf == "whip":
        seg, _ = curve(tx, by + 1, 1.6 + sw * .5, 16 + 6 * k, .5, 1.6, .5, "d", 6)
        out += seg
    # 背鳍
    dt = q["dorsal"]
    if dt == "soft" or (dt == "none" and shape == "oval"):
        out.append(P([(bx - rx * .3, by - ry * .85), (bx + sw * 2, by - ry - 5 - 3 * k), (bx + rx * .45, by - ry * .75)], d.acc))
    elif dt == "shark":
        out.append(P([(bx - rx * .2, by - ry * .9), (bx + rx * .05, by - ry - 7 - 4 * k), (bx + rx * .35, by - ry * .8)], "a"))
    elif dt == "curve":
        out.append(P([(bx - rx * .1, by - ry * .9), (bx + rx * .25, by - ry - 4 - 2 * k), (bx + rx * .35, by - ry * .8)], "a"))
    if shape == "ray":
        out.append(P([(bx - rx, by), (bx - rx * .2, by - ry * 1.6 - sw * 3), (bx + rx * .9, by), (bx - rx * .2, by + ry * 1.2 + sw * 3)], "a"))
        out.append(P([(bx - rx * .7, by + 1), (bx - rx * .2, by - ry * .6), (bx + rx * .5, by + 1), (bx - rx * .2, by + ry * .8)], "b", "!"))
    back, over, top = body_acc(d, k, an, (bx, by, rx, ry), (bx - rx * .6, by - ry * .1, ry * .8), (tx + 6, by))
    out += back
    if shape != "ray":
        out.append(E(bx, by, rx, ry * (1 + an["breath"]), "a"))
        out.append(E(bx - rx * .15, by + ry * .4, rx * .72, ry * .45, "b", 0, "!"))
    if "scales" in ex or d.pattern in ("spots", "saddle"):
        out += [E(bx - rx * .2 + i * rx * .25, by - ry * .3 + (i % 2) * ry * .3, ry * .22, ry * .2, d.acc if "scales" in ex else "d") for i in range(4)]
    if d.pattern in ("stripes", "bands"):
        out += [E(bx + rx * (.0 + .28 * i), by - ry * .05, 1.2, ry * .75, "d") for i in range(3)]
    if "grooves" in ex:
        out += [L(bx - rx * .8, by + ry * (.35 + .15 * i), bx - rx * .1, by + ry * (.5 + .15 * i), .5, "d", "!") for i in range(3)]
    if "gills" in ex:
        out += [L(bx - rx * .35 + i * 1.3, by - ry * .2, bx - rx * .4 + i * 1.3, by + ry * .25, .6, "d") for i in range(3)]
    # 胸鳍
    out.append(E(bx - rx * .15, by + ry * .45, 3.5 + k, 2, "d", .6 + sw * .5))
    out += over
    hx_ = bx - rx * .62
    hy = by - ry * .15
    if "beak" in ex:
        out.append(E(bx - rx * 1.05, by + ry * .2, rx * .25, ry * .25, "a"))
    if "barbels" in ex:
        out += curve(bx - rx * .9, by + ry * .25, -2.3 + sw * .4, 5 + 3 * k, -.6, .8, .5, d.acc)[0]
    if "teeth" in ex:
        out += [P([(bx - rx * .95 + i * 1.2, by + ry * .35), (bx - rx * .95 + i * 1.2 + .5, by + ry * .65), (bx - rx * .95 + i * 1.2 + 1, by + ry * .35)], "#ffffff", "!") for i in range(4)]
    if "spout" in ex:
        t = (an["ph"] / (2 * math.pi)) % 1.0
        out += [E(bx - rx * .2 + dx, by - ry - 2 - t * 6 - abs(dx), 1.2, 1.6, "#bfe8ff") for dx in (-2, 0, 2)]
    out += top
    face = eyes_spec(d, k, hx_, hy, ry * .9, far=shape != "ray")
    face["mouth"] = ("o" if shape != "long" else "smile", bx - rx * .85, by + ry * .25)
    if shape == "ray":
        face["eyes"] = [(bx - rx * .35, by - ry * .5, 1.0), (bx - rx * .05, by - ry * .55, .85)]
        face["mouth"] = ("smile", bx - rx * .5, by + ry * .1)
    out += brows(d, k, face["eyes"], face["eye_size"])
    return out, face


# ------------------------------------------------------------------ 蛇 / 鳗 / 蛟龙
def build_serpent(d, k, an):
    q = SERPENT.get(d.noun) or SERPENT["蛇"]
    kind = q["kind"]
    g = .8 + .6 * k + (.15 if d.legend else 0)
    ph = an["ph"]
    out = []
    if kind == "snake":
        w = (2.4 + 1.3 * k) * d.v["bh"]
        # 盘起来的两圈 + 竖起的脖子
        R = (7 + 4 * k) * d.v["bl"]
        rings = []
        for lvl, (rr, yy) in enumerate(((R, -w - .5), (R * .72, -w * 2.6 - .5))):
            n = 12
            for i in range(n):
                a1, a2 = i / n * 2 * math.pi, (i + 1) / n * 2 * math.pi
                p1 = (1 + math.cos(a1) * rr, yy + math.sin(a1) * rr * .32)
                p2 = (1 + math.cos(a2) * rr, yy + math.sin(a2) * rr * .32)
                rings.append((math.sin((a1 + a2) / 2), lvl, p1, p2))
        rings.sort(key=lambda t: (t[1], t[0]))  # 后半圈先画
        tail_tip = None
        for depth, lvl, p1, p2 in rings:
            c = "a" if depth > 0 else "d"
            out.append(L(p1[0], p1[1], p2[0], p2[1], w * 2, c))
            if d.pattern in ("bands", "stripes", "spots") and depth > .3:
                out.append(E(p2[0], p2[1], w * .45, w * .8, d.acc2))
        # 脖子 S 形竖起
        nx0, ny0 = 1 - R * .55, -w * 2.6 - .5
        pts = [(nx0 - math.sin(t * 2.6 + ph * .5) * 2.5 * (1 - t) - t * 3, ny0 - t * (11 + 6 * k)) for t in (0, .25, .5, .75, 1.0)]
        for i in range(1, len(pts)):
            out.append(L(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], w * 2 * (1 - .1 * i), "a"))
            out.append(E(pts[i][0] - w * .35, pts[i][1] + 1, w * .55, w * .9, "b", 0, "!"))
        tail_tip = (1 + R * .9, -w * 1.2)
        out += horn(1 + R * .9, -w * 1.5, 4 + 2 * k, 1.2, w * 1.4, "a", .6)
        hx_, hy = pts[-1][0] - 1, pts[-1][1] - w * .6 + an["bob"] * .4
        hr = w * 1.45 + .8
        if d.feature < .45 or k > .7:  # 眼镜蛇的兜帽
            out.append(E(hx_ + 1.5, hy + hr * 1.0, hr * 1.5, hr * 1.4, d.acc if d.scheme != "natural" else "a"))
            out.append(E(hx_ + .5, hy + hr * 1.1, hr * .8, hr * .9, "b", 0, "!"))
        back, over, top = body_acc(d, k, an, (1, -w * 2, R, w * 2), (hx_, hy, hr), tail_tip)
        out = back + out + over
        out.append(E(hx_, hy, hr * 1.2, hr, "a", -.1))
        out.append(E(hx_ - hr * .8, hy + hr * .25, hr * .65, hr * .55, "a"))
        if 4 <= an["f"] <= 7:
            tx0 = hx_ - hr * 1.4
            out += [L(tx0, hy + hr * .45, tx0 - 2.5, hy + hr * .55, .6, "#e03a4a"), L(tx0 - 2.5, hy + hr * .55, tx0 - 3.5, hy + hr * .25, .5, "#e03a4a"),
                    L(tx0 - 2.5, hy + hr * .55, tx0 - 3.5, hy + hr * .85, .5, "#e03a4a")]
        out += top
        face = eyes_spec(d, k, hx_, hy, hr)
        face["mouth"] = ("smile", hx_ - hr * .9, hy + hr * .55)
        face["eye_ry"] = face.get("eye_ry", 1.0) * .85
        out += brows(d, k, face["eyes"], face["eye_size"])
        return out, face
    if kind == "eel":
        w = (2.6 + 1.4 * k) * d.v["bh"]
        n = 10
        length = (24 + 10 * k) * d.v["bl"]
        by = -10 - 3 * k + math.sin(ph) * 1.2
        pts = [(-length * .45 + length * i / (n - 1), by + math.sin(ph + i * .8) * 2.2 * (i / n)) for i in range(n)]
        for i in range(1, n):
            (x1, y1), (x2, y2) = pts[i - 1], pts[i]
            ww = w * (1 - .55 * (i / n))
            out.append(P([(x1, y1 - ww * 1.0), (x2, y2 - ww - 2.2 * (1 - i / n)), (x2, y2), (x1, y1)], d.acc))
            out.append(P([(x1, y1), (x2, y2), (x2, y2 + ww + 1.6 * (1 - i / n)), (x1, y1 + ww * 1.0)], d.acc2))
        for i in range(n - 1, 0, -1):
            (x1, y1), (x2, y2) = pts[i - 1], pts[i]
            out.append(L(x1, y1, x2, y2, w * 2 * (1 - .55 * (i / n)), "a"))
        for i in range(1, n - 1, 2):
            out.append(E(pts[i][0], pts[i][1] + w * .45, w * .7, w * .35, "b", 0, "!"))
            if d.pattern != "none":
                out.append(E(pts[i][0], pts[i][1] - w * .3, w * .4, w * .4, d.acc2))
        hx_, hy = pts[0][0] - w * .6, pts[0][1] - w * .2
        hr = w * 1.4
        out.append(E(hx_, hy, hr * 1.3, hr, "a"))
        if d.t1 == "电" or d.t2 == "电":
            out += bolt(pts[-1][0], pts[-1][1], 3 + 2 * k, 1.2)
        out.append(E(hx_ + hr * .2, hy + hr * .6, 2.4, 1.2, "d", .5))
        face = eyes_spec(d, k, hx_, hy, hr)
        face["mouth"] = ("smile", hx_ - hr * .9, hy + hr * .45)
        out += brows(d, k, face["eyes"], face["eye_size"])
        return out, face
    # 蛟：东方龙，S 形飞在空中，背上一排鬃，四只小爪
    w = (3.0 + 1.5 * k) * d.v["bh"]
    n = 12
    pts = []
    for i in range(n):
        t = i / (n - 1)  # 0 头 → 1 尾
        x = -11 * g + t * 24 * g
        y = -21 * g + t * 14 * g - math.sin(t * 2 * math.pi * 1.1 + ph) * 4 * g
        pts.append((x, y))
    if "wings" in d.acc_list:
        out += wings(d, k, pts[3][0], pts[3][1], 8 + 6 * k, an, "membrane")
    for i in range(n - 1, 0, -1):
        (x1, y1), (x2, y2) = pts[i - 1], pts[i]
        ww = w * (1 - .6 * (i / n))
        out += spike_row([((x1 + x2) / 2, (y1 + y2) / 2 - ww * .8)], 1.6 + 1.6 * k, d.acc, lambda j: -.4)
        out.append(L(x1, y1, x2, y2, ww * 2, "a"))
        if i % 2 == 0:
            out.append(E(x1, y1 + ww * .5, ww * .7, ww * .45, "b", 0, "!"))
    tx, ty = pts[-1]
    out.append(P([(tx, ty), (tx + 4 + 2 * k, ty - 4), (tx + 3, ty + 1), (tx + 5 + 2 * k, ty + 3)], d.acc))
    for j in (3, 7):
        x, y = pts[j]
        out += [L(x, y + w * .6, x - 1.5, y + w * 1.8, 1.3, "a"), E(x - 2, y + w * 1.9, 1.3, .9, "d")]
    hx_, hy = pts[0][0] - w * .8, pts[0][1] - w * .5 + an["bob"] * .4
    hr = w * 1.7 + 1
    for i in range(4):
        out.append(E(hx_ + hr * .8, hy + hr * (-.3 + .35 * i), 1.6 + .4 * k, hr * .7, d.acc, .8 + an["sway"] * .3))
    out.append(E(hx_, hy, hr * 1.15, hr, "a"))
    out.append(E(hx_ - hr * .85, hy + hr * .3, hr * .7, hr * .5, "a"))
    out += horn(hx_ + hr * .3, hy - hr * .7, 3 + 4 * k, .9, 1.5, d.horn_c, .4) + horn(hx_ - hr * .15, hy - hr * .8, 2.5 + 3.5 * k, .5, 1.3, d.horn_c, .4)
    for i in range(2):
        out += curve(hx_ - hr * 1.4, hy + hr * .3, -2.0 - .5 * i, 4 + 5 * k, -.8 + an["sway"], .8, .5, d.acc)[0]
    if d.t1 in ("火", "电", "冰", "水"):
        out += {"火": flame, "电": bolt, "冰": crystal, "水": lambda x, y, s_, a_=0: [E(x, y - s_ * .5, s_ * .6, s_ * .6, "#bfe8ff")]}[d.t1](tx + 3, ty - 1, 2.5 + 2 * k)
    face = eyes_spec(d, k, hx_, hy, hr)
    face["mouth"] = ("cat", hx_ - hr * 1.1, hy + hr * .6)
    out += brows(d, k, face["eyes"], face["eye_size"])
    return out, face


# ------------------------------------------------------------------ 虫
def bug_legs(x0, x1, y_top, n, ln, w, c, an, splay=1.0, far_shift=1.5):
    far, near = [], []
    for i in range(n):
        x = x0 + (x1 - x0) * i / max(1, n - 1)
        dy = math.sin(an["ph"] * 2 + i * 2.1) * .8
        for fside in (True, False):
            tgt = far if fside else near
            ox = far_shift if fside else 0
            kx, ky = x + ox + ((i - (n - 1) / 2) * 2.4 - 1.2) * splay, y_top - ln * .25 + dy * .3
            tgt.append(L(x + ox, y_top, kx, ky, w, "d" if fside else c))
            tgt.append(L(kx, ky, kx + ((i - (n - 1) / 2) * 1.4 - .8) * splay, -.4, w * .85, "d" if fside else c))
    return far, near


def build_bug(d, k, an):
    kind = BUG.get(d.noun, "beetle")
    g = .8 + .6 * k + (.15 if d.legend else 0)
    out = []
    ph = an["ph"]
    fl = an["flap"]
    bh = d.v["bh"]
    if kind in ("beetle", "stag", "firefly", "cicada", "ant", "cricket"):
        rx, ry = 9 * g * d.v["bl"], 6 * g * bh
        if kind == "ant":
            rx *= .7
        by = -ry - 3.2 * g
        bx = 3
        far, near = bug_legs(bx - rx * .6, bx + rx * .5, by + ry * .5, 3, 5 * g, 1.1 + .3 * k, "d", an)
        out += far
        if kind == "cricket":
            out += [L(bx + rx * .3, by, bx + rx * 1.1, by - ry * 1.1, 2.2, "a"), L(bx + rx * 1.1, by - ry * 1.1, bx + rx * 1.4, -.6, 1.4, "a")]
        if kind in ("firefly", "cicada") or (k > .4 and kind != "ant"):
            wc = "#e8f6ff" if kind != "firefly" else "#f4f8e0"
            out += [E(bx + rx * .4, by - ry * .9, rx * .55, ry * .55 + fl * .5, wc, .5 - fl * .3), E(bx + rx * .2, by - ry * .7, rx * .5, ry * .5, wc, .2 - fl * .2)]
        if kind == "ant":
            out += [E(bx + rx * 1.1, by + ry * .1, rx * .75, ry * .8, "a"), E(bx, by + ry * .15, rx * .5, ry * .5, "a")]
            if d.pattern != "none":
                out.append(E(bx + rx * 1.1, by - ry * .1, rx * .35, ry * .3, d.acc))
        else:
            out.append(E(bx, by, rx, ry, "a"))
            if kind in ("beetle", "stag"):
                out.append(E(bx + rx * .05, by - ry * .1, rx * .95, ry * .9, d.acc2 if d.scheme != "natural" else "d"))
                out.append(L(bx - rx * .25, by - ry * .95, bx + rx * .9, by + ry * .1, .7, "d"))
                if d.pattern in ("spots", "saddle"):
                    out += [E(bx + rx * .2, by - ry * .3, 1.6, 1.4, d.acc), E(bx + rx * .55, by - ry * .05, 1.4, 1.2, d.acc)]
            if kind == "firefly":
                glow = .5 + .5 * math.sin(ph * 2)
                out.append(E(bx + rx * .7, by + ry * .2, rx * .45, ry * .55, mix("#c8e060", "#fff8a0", glow)))
            if kind == "cicada":
                out += [L(bx - rx * .3 + i * rx * .35, by - ry * .2, bx - rx * .3 + i * rx * .35, by + ry * .6, .6, "d") for i in range(3)]
        out += near
        hx_, hy = bx - rx * .95, by - ry * .35 + an["bob"] * .3
        hr = 4.3 * g * d.v["hr"] * (1.15 - .2 * k)
        if kind == "cricket":
            out += curve(hx_ - hr * .2, hy - hr * .7, -.3, 12 + 6 * k, 1.6 + an["sway"] * .5, .7, .5, "d", 6)[0]
        elif kind not in ("cicada",):
            for lean in (-.45, .05):
                seg, tip = curve(hx_ + hr * (lean + .1), hy - hr * .8, lean, 5 + 4 * k, .7 + an["sway"] * .4, .8, .6, "d", 3 if kind != "ant" else 2)
                out += seg
                if kind == "ant":
                    out += curve(tip[0], tip[1], lean - 1.2, 3 + 2 * k, 0, .7, .6, "d", 1)[0]
        out.append(E(hx_, hy, hr, hr * .95, "a" if kind != "beetle" else "d"))
        if kind == "beetle" and (k > .3 or d.feature > .5):
            out += horn(hx_ - hr * .3, hy - hr * .5, 4 + 6 * k, -.4, 2.2, "d", 1.0)
        if kind == "stag" or (kind == "ant" and k > .2):
            for i, s in enumerate((-1, 1)):
                c = "d" if i == 0 else "a"
                out += horn(hx_ - hr * .6, hy + hr * .2 + s * 1.2, 4 + 6 * k, -1.7 - s * .5, 2, c, s * .9)
    elif kind in ("bee", "moth", "dragonfly"):
        by = -14 * g + math.sin(ph * 2) * 1.5
        bx = 2
        rr = 4.5 * g
        wingc = "#e8f6ff" if kind != "moth" else "b"
        if kind == "moth":
            for far in (True, False):
                o = (2, -1) if far else (0, 0)
                a0 = (-.4 if far else .3) - fl * .3
                out.append(E(bx + 5 + o[0], by - 6 + o[1], 9 * g * .8, 6 * g * .8, "d" if far else "b", a0))
                if not far:
                    out += [E(bx + 7, by - 7, 2 + k, 2 + k, d.acc, a0), E(bx + 7, by - 7, .9 + .4 * k, .9 + .4 * k, INK)]
                    out.append(E(bx + 3, by + 3, 5 * g * .8, 4 * g * .8, "a", -.3 - fl * .2))
        elif kind == "dragonfly":
            for i, a in enumerate((-.25, .25)):
                out.append(E(bx + 8 * g, by - 4 + i * 2.5, 9 * g, 2.2, "#e8f6ff", a - fl * .15))
        else:
            out += [E(bx + 4, by - 6, 3.5 * g, 5 * g, wingc, .5 - fl * .5), E(bx + 2, by - 5, 3 * g, 4.5 * g, wingc, -.1 - fl * .4)]
        if kind == "dragonfly":
            out += curve(bx + 3, by + 1, 1.75, 16 + 6 * k, .15, 2, 1.2, "a", 6)[0]
            out += [E(bx + 3 + i * 3, by + 1.2, .5, 1.2, "d") for i in range(1, 5)]
        elif kind == "bee":
            ax, ay = bx + rr * 1.2, by + rr * .5
            out.append(E(ax, ay, rr * 1.3, rr * 1.05, "#ffd83a" if d.scheme != "dark" else d.acc, .4))
            out += [E(ax - rr * .25 + i * rr * .55, ay - .2 + i * .4, 1.1, rr * .95, INK, .4) for i in range(2)]
            out.append(P([(ax + rr * 1.1, ay + rr * .5), (ax + rr * 1.9, ay + rr * 1.3), (ax + rr * .9, ay + rr * .9)], INK))
        out.append(E(bx, by, rr, rr * 1.05, "a"))
        if kind == "moth":
            out.append(E(bx - rr * .4, by - rr * .3, rr * .8, rr * .55, "b"))
        for i in range(3):
            out.append(L(bx - 1 + i * 1.5, by + rr * .8, bx - 2 + i * 2, by + rr * 1.8, .8, "d"))
        hx_, hy = bx - rr * 1.1, by - rr * .55
        hr = 3.8 * g * d.v["hr"]
        if kind == "moth":
            for lean in (-.5, .15):
                tip = polar(hx_ + hr * (lean + .1), hy - hr * .8, lean, 5 + 3 * k)
                out.append(L(hx_ + hr * (lean + .1), hy - hr * .8, tip[0], tip[1], .7, "d"))
                out.append(E(tip[0], tip[1] + 1.2, 1.2, 2.4, "d", lean))
        else:
            for lean in (-.5, .1):
                out += curve(hx_ + hr * (lean + .1), hy - hr * .8, lean, 3 + 2 * k, .5, .7, .6, "d", 2)[0]
        out.append(E(hx_, hy, hr, hr, "a"))
        if kind == "dragonfly":
            out += [E(hx_ - hr * .4, hy - hr * .2, hr * .7, hr * .75, d.acc), E(hx_ + hr * .3, hy - hr * .25, hr * .6, hr * .7, hsv(d.acc, mv=.8))]
        far, near = [], []
    elif kind == "mantis":
        bx, by = 2, -6 * g
        far, near = bug_legs(bx, bx + 6 * g, by + 2, 2, 4 * g, 1, "d", an, 1.3)
        out += far
        out.append(E(bx + 7 * g, by - 1, 8 * g, 4 * g, "a", -.2))
        if k > .3:
            out.append(E(bx + 6 * g, by - 3, 6.5 * g, 2.6 * g, mix(d.a, "#ffffff", .3), -.35))
        out += near
        out.append(L(bx, by, bx - 3 * g, by - 6 * g, 2.6 * g, "a"))
        hx_, hy = bx - 4.5 * g, by - 8 * g + an["bob"] * .4
        for s, c in ((1.8, "d"), (0, "a")):
            ax, ay = bx - 2.5 * g + s, by - 6 * g
            ex2, ey2 = ax - 4 * g, ay + 1 + an["sway"] * 2
            sc = c if s else d.acc
            out += [L(ax, ay, ex2, ey2, 2.2, sc), L(ex2, ey2, ex2 + 1.5, ey2 - 7 * g, 2.0, sc)]
            out += spike_row([(ex2 + .5, ey2 - 2 * g), (ex2 + .7, ey2 - 4 * g)], 1.5, "#f4f0e8", lambda i: -1.4)
        hr = 4.2 * g * d.v["hr"]
        for lean in (-.6, .2):
            out += curve(hx_ + hr * lean, hy - hr * .7, lean - .6, 4 + 2 * k, .9, .5, .5, "d", 3)[0]
        out.append(P([(hx_ - hr * 1.3, hy - hr * .6), (hx_ + hr * 1.1, hy - hr * .6), (hx_ - hr * .1, hy + hr * 1.1)], "a"))
        face = {"eyes": [(hx_ - hr * .75, hy - hr * .2, 1.0), (hx_ + hr * .45, hy - hr * .2, .9)], "eye_size": hr / 5.2 * (1.2 - .25 * k), "iris": d.iris,
                "mouth": ("o", hx_ - hr * .1, hy + hr * .55)}
        return out, face
    elif kind == "spider":
        bx, by = 3, -9 * g
        ar = 7 * g * d.v["bh"]
        legs = []
        for i in range(4):
            for fside in (True, False):
                x = bx - 2 + i * 2 + (2 if fside else 0)
                kx, ky = x - 6 + i * 4, by - ar * (.9 - .1 * i) + math.sin(ph * 2 + i) * .6
                fx = kx - 4 + i * 3
                legs.append((fside, [L(x, by, kx, ky, 1.3 + .3 * k, "d" if fside else "a"), L(kx, ky, fx, -.4, 1.1, "d" if fside else "a")]))
        out += [p for f, ls in legs if f for p in ls]
        out.append(E(bx + ar * .8, by - 1, ar, ar * .9 * (1 + an["breath"]), "a"))
        if d.pattern != "none" or k > .4:
            out += [E(bx + ar * .8, by - ar * .3, ar * .35, ar * .3, d.acc), E(bx + ar * 1.1, by + ar * .2, ar * .2, ar * .2, d.acc)]
        out += [p for f, ls in legs if not f for p in ls]
        hx_, hy = bx - ar * .45, by + 1 + an["bob"] * .3
        hr = 4.5 * g * d.v["hr"]
        out.append(E(hx_, hy, hr, hr * .9, "a"))
        out += [P([(hx_ - hr * .7, hy + hr * .6), (hx_ - hr * .5, hy + hr * 1.3), (hx_ - hr * .3, hy + hr * .6)], "#f4f0e8", "!"),
                P([(hx_ - hr * .05, hy + hr * .6), (hx_ + hr * .15, hy + hr * 1.3), (hx_ + hr * .35, hy + hr * .6)], "#f4f0e8", "!")]
        face = eyes_spec(d, k, hx_, hy, hr)
        if k > .4:
            face["eyes"] += [(hx_ - hr * .5, hy - hr * .6, .45), (hx_ + hr * .05, hy - hr * .65, .45)]
        face["mouth"] = None
        return out, face
    elif kind in ("worm", "centipede"):
        n = 5 + int(k * 3) + (3 if kind == "centipede" else 0)
        seg_r = (3.6 + 1.8 * k) * d.v["bh"]
        pts = []
        for i in range(n):
            t = i / (n - 1)
            x = 14 * g - t * 22 * g
            y = -seg_r - (max(0, t - .55) / .45) ** 1.5 * 10 * g + math.sin(ph + t * 6) * .8 * (1 - t)
            pts.append((x, y))
        if kind == "centipede":
            for i, (x, y) in enumerate(pts[:-1]):
                for fside in (True, False):
                    o = 1.2 if fside else 0
                    out.append(L(x + o, y + seg_r * .5, x + o - 1.5 + math.sin(ph * 2 + i * 1.7) * .8, -.3 if y > -seg_r * 2.5 else y + seg_r * 2, 1.0, "d" if fside else "a"))
        if kind == "worm" and k > .2:
            out += horn(pts[0][0], pts[0][1] - seg_r * .6, 3 + 2 * k, .6, 1.4, d.acc)
        for i, (x, y) in enumerate(pts[:-1]):
            c = "a" if i % 2 == 0 or d.pattern == "none" else d.acc2
            out.append(E(x, y, seg_r * 1.05, seg_r * (1 + an["breath"] * (i % 2)), c))
            if kind == "worm":
                out.append(E(x - .5, y + seg_r * .7, 1.0, .8, "d"))
                if d.pattern in ("spots", "saddle") and i % 2 == 0:
                    out.append(E(x + .5, y - seg_r * .45, 1.3, 1.1, d.acc))
        hx_, hy = pts[-1]
        hr = seg_r * 1.25
        if kind == "centipede":
            out += [L(hx_ - hr * .3, hy - hr * .7, hx_ - hr * .6 - 3, hy - hr * 1.7 - 2 * k, .8, "d"), L(hx_ + hr * .3, hy - hr * .7, hx_ + hr * .4 + 2, hy - hr * 1.8 - 2 * k, .8, "d")]
        out.append(E(hx_, hy, hr, hr * .95, "a" if kind == "worm" else "d"))
        if kind == "centipede":
            out += horn(hx_ - hr * .8, hy + hr * .5, 3 + 2 * k, -2.3, 1.2, "#e8c060", -.6)
        far, near = [], []
    elif kind == "snail":
        bx, by = 1, -3.5 * g
        sr = (6 + 4 * k) * d.v["bh"]
        out.append(E(bx - 2, by + 1, 11 * g, 2.6 * g, "b"))
        out.append(E(bx + 3, by - sr * .9, sr, sr, d.acc2 if d.scheme != "natural" else "#c08a50"))
        for i in range(3):
            rr = sr * (.75 - .22 * i)
            out.append(E(bx + 3 + i * .9, by - sr * .9 - i * .5, rr, rr, hsv(d.acc2 if d.scheme != "natural" else "#c08a50", mv=1.0 + .12 * (i % 2 * 2 - 1))))
        hx_, hy = bx - 8 * g, by - 3 * g + an["bob"] * .3
        hr = 3.6 * g * d.v["hr"]
        out.append(L(bx - 5 * g, by, hx_, hy, hr * 1.4, "b"))
        for lean in (-.5, .1):
            seg, tip = curve(hx_ + hr * (lean + .2), hy - hr * .7, lean, 4 + 3 * k + math.sin(ph + lean * 3) * .6, .2, .8, .7, "b", 2)
            out += seg + [E(tip[0], tip[1], 1, 1, "d")]
        out.append(E(hx_, hy, hr, hr, "b"))
        face = eyes_spec(d, k, hx_, hy, hr)
        face["mouth"] = ("smile", hx_ - hr * .4, hy + hr * .5)
        return out, face
    elif kind == "scorpion":
        bx, by = 2, -5 * g
        rx, ry = 8 * g * d.v["bl"], 4 * g * d.v["bh"]
        far, near = bug_legs(bx - rx * .4, bx + rx * .5, by + ry * .4, 4, 4 * g, 1, "a", an, .6)
        out += far
        # 尾巴弯过头顶
        tail = []
        x, y = bx + rx * .9, by
        for i in range(5 + int(k * 2)):
            a = .4 - i * .5 + an["sway"] * .3
            x2, y2 = polar(x, y, a, 3.2 * g)
            tail.append(E(x2, y2, 2.2 * g * (1 - i * .08), 2 * g * (1 - i * .08), "a" if i % 2 else "d"))
            x, y = x2, y2
        out += tail
        out += horn(x, y, 3 + 3 * k, -1.8, 2, d.acc, -.5)
        out.append(E(bx, by, rx, ry, "a"))
        out += [L(bx - rx * .5 + i * rx * .35, by - ry * .9, bx - rx * .5 + i * rx * .35, by - ry * .1, .6, "d") for i in range(4)]
        out += near
        hx_, hy = bx - rx * .95, by - ry * .2
        hr = 3.6 * g * d.v["hr"]
        for s, c in ((1.5, "d"), (0, "a")):
            cx, cy = hx_ - 4 * g + s, hy + 1 - s + an["sway"] * s
            out += [L(hx_ + s, hy + 1, cx, cy, 1.6 + k * .4, c), E(cx - 1.5, cy - .5, 2.8 * g, 2 * g, c, -.3),
                    P([(cx - 2.5 * g, cy - 1), (cx - 5 * g, cy - 2.5 * g - abs(an["sway"]) * 3), (cx - 1, cy - 1.5 * g)], c)]
        out.append(E(hx_, hy, hr, hr * .85, "a"))
        far, near = [], []
    if kind not in ("mantis", "spider", "snail"):
        out += near if kind in ("bee", "moth", "dragonfly", "worm", "centipede", "scorpion") else []
        hr_ = locals().get("hr", 4)
        back, over, top = body_acc(d, k, an, (hx_ + 6, hy + 2, 6, 4), (hx_, hy, hr_), None)
        out = back + out + top
        face = eyes_spec(d, k, hx_, hy, hr_)
        face["mouth"] = ("smile" if kind not in ("ant", "stag") else None, hx_ - hr_ * .45, hy + hr_ * .5) if kind not in ("ant", "stag", "beetle") else None
        if kind in ("bee", "dragonfly"):
            face["eye_size"] *= 1.15
        out += brows(d, k, face["eyes"], face["eye_size"])
        return out, face
    return out, {}


def build_butterfly(d, k, an):
    g = .8 + .55 * k + (.15 if d.legend else 0)
    fl = an["flap"]
    by = -15 * g + math.sin(an["ph"]) * 1.5 - 2
    bx = 0
    out = []
    shape = d.feature
    up_c, lo_c = ("b", d.acc) if d.scheme != "split" else (d.acc, "b")
    vein = hsv(d.a, mv=.5)
    for far in (True, False):
        s = -1 if far else 1
        squash = 1 - abs(fl) * .45 if not far else 1 - abs(fl) * .25
        ox = 1.5 if far else 0
        ux, uy = bx + s * 8 * g * squash + ox, by - 5 * g
        lx, ly = bx + s * 6 * g * squash + ox, by + 4 * g
        uc = up_c if not far else hsv(d.b if up_c == "b" else up_c, mv=.8)
        if shape < .33:
            out.append(E(ux, uy, 8.5 * g * squash, 7 * g, uc, .5 * s))
        elif shape < .66:
            out.append(P([(bx + ox, by - 2), (bx + s * 15 * g * squash + ox, by - 11 * g), (bx + s * 13 * g * squash + ox, by - 1), (bx + ox, by + 1)], uc))
        else:
            out.append(E(ux, uy, 9 * g * squash, 6 * g, uc, .8 * s))
        out.append(E(lx, ly, 6 * g * squash, 5 * g, lo_c if not far else hsv(lo_c if lo_c != "b" else d.b, mv=.8), -.4 * s))
        if shape > .5 and k > .4:
            out.append(L(lx + s * 3 * g * squash, ly + 3 * g, lx + s * 4 * g * squash, ly + 8 * g, 1.6, lo_c))
        if not far:
            out.append(E(ux + s * 2 * g * squash, uy - 1, 2.2 * g * squash, 2.2 * g, "a" if d.pattern != "none" else d.acc))
            out.append(E(ux + s * 2 * g * squash, uy - 1, 1.0 * g * squash, 1.0 * g, INK if d.feature > .5 else "#ffffff"))
            out.append(L(bx, by - 1, ux + s * 5 * g * squash, uy - 3 * g, .5, vein))
    out += [E(bx, by + 3 * g, 2.6 * g, 7 * g, "d"), E(bx, by + 6 * g, 2 * g, 4 * g, "a")]
    hr = 4 * g * d.v["hr"]
    hx_, hy = bx, by - 5 * g
    for lean in (-.4, .4):
        tip = polar(hx_ + lean * 3, hy - hr * .7, lean, 5 + 4 * k)
        out += [L(hx_ + lean * 3, hy - hr * .7, tip[0], tip[1], .7, "d"), E(tip[0], tip[1], 1.2, 1.2, "d")]
    out.append(E(hx_, hy, hr, hr * .95, "a"))
    face = eyes_spec(d, k, hx_ + hr * .35, hy, hr)
    face["mouth"] = ("smile", hx_ - hr * .1, hy + hr * .5)
    return out, face


def build_frog(d, k, an):
    g = .8 + .6 * k + (.15 if d.legend else 0)
    out = []
    if k < .2 and d.stages > 1:  # 蝌蚪
        by = -7 + math.sin(an["ph"]) * 1.2
        out += curve(4, by, 1.6 + an["sway"] * .6, 12, .6 * math.sin(an["ph"] * 2), 4, 1, "a", 5)[0]
        out.append(E(-1, by, 7, 6, "a"))
        out.append(E(-2, by + 2.5, 4.5, 2.5, "b", 0, "!"))
        face = eyes_spec(d, k, -2, by - 1, 6)
        face["mouth"] = ("o", -5, by + 2.5)
        return out, face
    toad = d.feature < .4
    rx, ry = (10 + 4 * k) * g * .75 * d.v["bl"] * (1.15 if toad else 1), (7 + 3 * k) * g * .75 * d.v["bh"] * (1 + an["breath"] * 1.5)
    bx, by = 2, -ry - 1
    out += [E(bx + rx * .55 + 2, -2.4, rx * .4, 2.6, "d"), E(bx + rx * .8, -1, rx * .45, 1.3, "d")]
    out.append(E(bx, by, rx, ry, "a", -.15))
    if toad:
        out += [E(bx - rx * .2 + i * 2.5, by - ry * .5 + (i % 2) * 2, 1.0, .9, "d") for i in range(4)]
    out.append(E(bx + rx * .5, by + ry * .25, rx * .45, ry * .6, "a"))
    out += [L(bx - rx * .55, by + ry * .4, bx - rx * .8, -1, 1.8 + k, "a"), E(bx - rx * .9, -.8, 2 + k * .5, 1, "b" if not toad else "a")]
    if d.pattern in ("spots", "stripes", "saddle"):
        out += [E(bx + rx * .1 + i * 2.8, by - ry * .6, 1.3, 1.1, d.acc) for i in range(3)]
    hx_, hy = bx - rx * .5, by - ry * .45 + an["bob"] * .3
    hr = ry * .85
    out.append(E(hx_, hy, hr * 1.2, hr * .85, "a"))
    for ex_, m in ((hx_ - hr * .6, .85), (hx_ + hr * .3, 1.0)):
        out.append(E(ex_, hy - hr * .65, hr * .45 * m, hr * .45 * m, "a"))
    sac = .5 + .5 * math.sin(an["ph"] * 2)
    if d.feature > .7:
        out.append(E(hx_ - hr * .2, hy + hr * .75, hr * .5 * (.6 + .4 * sac), hr * .4 * (.6 + .4 * sac), mix(d.b, d.acc, .4), 0, "!"))
    out.append(E(hx_ - hr * .1, hy + hr * .35, hr * .9, hr * .35, "b", 0, "!"))
    back, over, top = body_acc(d, k, an, (bx, by, rx, ry), (hx_, hy, hr), None)
    out = back + out + over + top
    face = {"eyes": [(hx_ - hr * .6, hy - hr * .7, .85), (hx_ + hr * .3, hy - hr * .7, 1.0)], "eye_size": hr / 6 * (1.25 - .3 * k), "iris": d.iris,
            "mouth": ("wide", hx_ - hr * .2, hy + hr * .15)}
    if not toad:
        face["blush"] = [(hx_ - hr * .9, hy + hr * .05)]
    out += brows(d, k, face["eyes"], face["eye_size"])
    return out, face


def build_crust(d, k, an):
    kind = CRUST.get(d.noun, "crab")
    g = .8 + .6 * k + (.15 if d.legend else 0)
    out = []
    sw = an["sway"]
    shell = d.acc2 if d.scheme not in ("natural",) else hsv(d.a, mv=.8)
    if kind == "crab":
        rx, ry = 10 * g * d.v["bl"], 6.5 * g * d.v["bh"]
        bx, by = 0, -ry - 3 * g
        far, near = bug_legs(bx - rx * .5, bx + rx * .6, by + ry * .4, 3, 5 * g, 1.3, "a", an, 1.4)
        out += far
        big = 1.35 if d.feature < .35 else 1.0
        for i, s in enumerate((1, -1)):
            m = big if s == -1 else 1.0
            cx, cy = bx + s * rx * 1.0, by - ry * .6 - sw * 2 * s
            out += [L(bx + s * rx * .6, by, cx, cy, 2.4, "a"), E(cx, cy - 2 * m, 3.8 * g * m, 3 * g * m, "a", s * .4),
                    P([(cx - s * 1, cy - 4 * g * m), (cx + s * 4 * g * m, cy - 7 * g * m - abs(sw) * 3), (cx + s * 1.5, cy - 2.2 * g * m)], "a")]
        out.append(E(bx, by, rx, ry * (1 + an["breath"]), "a"))
        out.append(E(bx, by - ry * .2, rx * .85, ry * .65, shell))
        if k > .5:
            out += spike_row([ell_top(bx, by, rx, ry, t) for t in (-.6, -.2, .2, .6)], 1.5 + k, shell)
        out += near
        hx_, hy = bx, by - ry * .1
        out += [L(bx - 3, by - ry * .7, bx - 3.5, by - ry - 5 * g, 1.2, "d"), L(bx + 3, by - ry * .7, bx + 3.5, by - ry - 5 * g, 1.2, "d"),
                E(bx - 3.5, by - ry - 5 * g, 2.4, 2.4, "#f4f0e8"), E(bx + 3.5, by - ry - 5 * g, 2.4, 2.4, "#f4f0e8")]
        face = {"eyes": [(bx - 3.5, by - ry - 5 * g, 1.0), (bx + 3.5, by - ry - 5 * g, 1.0)], "eye_size": .55 + .1 * k, "iris": d.iris,
                "mouth": ("cat", bx, by + ry * .25)}
        return out, face
    if kind == "shrimp":
        bx, by = 2, -10 * g
        pts = [polar(bx + 3 * g, by + 1, 1.2 + i * .25 + sw * .15, 2.6 * g * i) for i in range(5)]
        for i, (x, y) in enumerate(pts[::-1]):
            out.append(E(x, y, 3.6 * g * (1 - i * .08), 3.2 * g * (1 - i * .08), "a" if i % 2 else shell))
        tx, ty = pts[-1]
        out.append(P([(tx, ty), (tx + 5 * g, ty + 2), (tx + 2, ty + 4 * g), (tx - 1, ty + 3 * g)], d.acc))
        hx_, hy = bx - 3 * g, by - 1
        for i in range(4):
            out.append(L(bx - 2 + i * 2.5, by + 2 * g, bx - 3 + i * 2.5, -.4, .9, "d"))
        out += curve(hx_ - 2, hy - 3, -1.0, 12 + 6 * k, 1.8 + sw, .7, .5, "d", 6)[0]
        out += curve(hx_ - 1, hy - 3, -.4, 10 + 5 * k, 1.4 + sw, .7, .5, "d", 5)[0]
        out.append(E(hx_, hy, 5 * g, 4 * g, "a"))
        out.append(P([(hx_ - 4 * g, hy - 1), (hx_ - 9 * g, hy - 2), (hx_ - 4 * g, hy + 1)], shell))
        face = eyes_spec(d, k, hx_ + 1, hy - 1, 4.5 * g)
        face["mouth"] = None
        return out, face
    if kind == "clam":
        bx, by = 0, -8 * g
        r = 10 * g * d.v["bl"]
        open_ = .5 + .3 * math.sin(an["ph"])
        out.append(P([(bx - r, by + 2), (bx - r * .6, by - r * (.6 + open_ * .3)), (bx, by - r * (.8 + open_ * .3)), (bx + r * .6, by - r * (.6 + open_ * .3)), (bx + r, by + 2)], shell))
        out.append(E(bx, by - 1, r * .6, r * .45 * open_ + 1.5, "#f4c8d0"))
        if k > .4:
            out.append(E(bx + r * .3, by - r * .3, 1.8 + k, 1.8 + k, "#ffffff"))
        out.append(P([(bx - r, by + 2), (bx - r * .6, by + r * .5), (bx, by + r * .6), (bx + r * .6, by + r * .5), (bx + r, by + 2)], "a"))
        out += [L(bx + i * r * .3, by + 2, bx + i * r * .35, by + r * .55, .6, "d") for i in (-2, -1, 0, 1, 2)]
        if k > .6:
            out += spike_row([(bx + t * r * .9, by - r * .55 - abs(t) * -2) for t in (-.6, 0, .6)], 2 + k * 2, shell)
        face = {"eyes": [(bx - r * .2, by - 1.5, 1.0), (bx + r * .2, by - 1.5, 1.0)], "eye_size": .8 + .1 * k, "iris": d.iris, "mouth": ("smile", bx, by + 1.5)}
        return out, face
    # 海螺 / 菊石
    bx, by = 2, -9 * g
    r = (7 + 4 * k) * d.v["bh"] * (.75 if kind == "conch" else 1)
    if kind == "conch":
        out.append(P([(bx - r * .2, by + r * .8), (bx + r * 1.1, by - r * .4), (bx + r * .3, by - r * 1.8 - k * 3), (bx - r * .6, by - r * .5)], shell))
        out += [L(bx - r * .4, by - r * (.2 + .4 * i), bx + r * .8, by - r * (.5 + .3 * i), .7, hsv(shell, mv=.7)) for i in range(3)]
        out += spike_row([(bx + r * .5, by - r * .9), (bx + r * .8, by - r * .4)], 2 + k * 2, shell, lambda i: .8)
    else:
        out.append(E(bx + 1, by - 1, r, r, shell))
        for i in range(3):
            rr = r * (.72 - .22 * i)
            out.append(E(bx + 1 + i * .8, by - 1 - i * .4, rr, rr, hsv(shell, mv=1.12 if i % 2 == 0 else .9)))
        out += [L(bx + 1, by - 1, *polar(bx + 1, by - 1, a, r * .95), .5, hsv(shell, mv=.7)) for a in (0.5, 1.6, 2.7, 3.8, 4.9)]
    hx_, hy = bx - r * .8, by + r * .45
    for i in range(3 + int(k * 2)):
        out += curve(hx_ + i * 1.5 - 2, hy + 2, 3.0 + i * .12, 5 + 2 * k, math.sin(an["ph"] + i) * .8, 1.4, .8, "a", 3)[0]
    out.append(E(hx_, hy, 4.5 * g, 4 * g, "a"))
    face = eyes_spec(d, k, hx_, hy - 1, 4.2 * g)
    face["mouth"] = None
    return out, face


def build_float(d, k, an):
    kind = FLOAT.get(d.noun, "spirit")
    g = .8 + .55 * k + (.15 if d.legend else 0)
    out = []
    bob = math.sin(an["ph"]) * 2
    sw = an["sway"]
    by = -16 * g + bob - 2
    bx = 0
    r = 8 * g * d.v["bh"]
    if kind == "jelly":
        for i in range(4 + int(k * 2)):
            x = bx - r * .7 + i * r * 1.4 / (3 + int(k * 2))
            out += curve(x, by + r * .4, 3.1 + math.sin(an["ph"] + i) * .2, 8 + 6 * k, math.sin(an["ph"] * 2 + i) * .7, 1.6, .7, "a" if i % 2 else d.acc, 4)[0]
        out.append(E(bx, by, r * 1.1, r * .85 * (1 - an["breath"] * 2), "a"))
        out.append(E(bx, by + r * .55, r * 1.0, r * .25, "b"))
        if k > .4:
            out += [E(bx - r * .5 + i * r * .5, by - r * .5, r * .18, r * .15, d.acc) for i in range(3)]
        face = {"eyes": [(bx - r * .35, by - r * .05, 1.0), (bx + r * .3, by - r * .05, 1.0)], "eye_size": r / 7 * (1.2 - .3 * k), "iris": d.iris, "mouth": ("smile", bx, by + r * .3)}
        out += brows(d, k, face["eyes"], face["eye_size"])
        return out, face
    if kind in ("spirit", "soul", "shadow"):
        if kind == "soul":
            out += flame(bx + 1, by - r * .3, r * (1.4 + .4 * k), sw * .3, math.sin(an["ph"] * 3))
        tail = [(bx - r, by), (bx - r * .9 + sw * 3, by + r * 1.4), (bx - r * .3, by + r * .9), (bx + sw * 4, by + r * 1.9), (bx + r * .3, by + r * .9),
                (bx + r * .9 + sw * 3, by + r * 1.4), (bx + r, by)]
        if kind == "shadow":
            tail = [(bx - r * 1.1, by), (bx - r * 1.4, by + r * .9), (bx - r * .6, by + r * .7), (bx - r * .5, by + r * 1.6), (bx, by + r * .9),
                    (bx + r * .5, by + r * 1.6), (bx + r * .6, by + r * .7), (bx + r * 1.4, by + r * .9), (bx + r * 1.1, by)]
            out += spike_row([ell_top(bx, by, r * 1.05, r, t) for t in (-.7, -.25, .25, .7)], 3 + 3 * k, "a", lambda i: -.7 + i * .45)
        out.append(P(tail, "a"))
        out.append(E(bx, by, r * 1.05, r, "a"))
        if k > .4 and kind != "shadow":
            for s in (-1, 1):
                out.append(E(bx + s * (r + 3), by + 2 + math.sin(an["ph"] + s) * 1.5, 2.2 + k, 2.2 + k, d.acc))
        back, over, top = body_acc(d, k, an, (bx, by + r * .4, r * .7, r * .5), (bx, by, r), None)
        out = back + out + over + top
        face = {"eyes": [(bx - r * .35, by - r * .1, 1.0), (bx + r * .3, by - r * .1, 1.0)], "eye_size": r / 7.5 * (1.2 - .3 * k), "iris": d.iris}
        if kind == "shadow":
            face["eye_ry"] = .6
            face["mouth"] = ("wide", bx, by + r * .45)
        else:
            face["mouth"] = ("o", bx, by + r * .4)
        out += brows(d, k, face["eyes"], face["eye_size"])
        return out, face
    if kind == "lantern":
        out.append(L(bx, by - r * 1.4, bx, by - r * 2.0, 1.0, "d"))
        out.append(E(bx, by - r * 2.1, 2, 1.2, "d"))
        out.append(E(bx, by - r * .9, r * .6, r * .25, "d"))
        out.append(E(bx, by, r * .85, r * 1.0, mix("#fff0a0", d.a, .35)))
        out += [L(bx + t * r * .55, by - r * .85, bx + t * r * .55, by + r * .85, .6, "d") for t in (-1, 0, 1)]
        out += flame(bx, by + r * .3, r * .55, sw * .3, math.sin(an["ph"] * 3))
        out.append(E(bx, by + r * .95, r * .6, r * .25, "d"))
        out += curve(bx, by + r * 1.1, 3.14 + sw * .4, 5 + 3 * k, .3, 1.2, .8, d.acc, 3)[0]
        face = {"eyes": [(bx - r * .3, by - r * .3, 1.0), (bx + r * .3, by - r * .3, 1.0)], "eye_size": r / 8, "iris": d.iris, "mouth": ("o", bx, by + r * .05)}
        return out, face
    if kind == "mask":
        out += [L(bx + s * r * .7, by + r * .5, bx + s * r * .9 + sw * 3, by + r * 1.8, 1.4, d.acc) for s in (-1, 1)]
        out.append(E(bx, by, r * .95, r * 1.15, "b" if d.scheme != "dark" else "a"))
        out += [E(bx + s * r * .45, by - r * .15, r * .35, r * .28, "a", s * -.3) for s in (-1, 1)]
        out.append(E(bx, by + r * .6, r * .3, r * .12, d.acc))
        if k > .4:
            out += horn(bx - r * .5, by - r * .9, 3 + 3 * k, -.3, 2, d.acc) + horn(bx + r * .5, by - r * .9, 3 + 3 * k, .3, 2, d.acc)
        face = {"eyes": [(bx - r * .45, by - r * .15, 1.0), (bx + r * .45, by - r * .15, 1.0)], "eye_size": r / 9, "iris": d.iris, "eye_ry": .7, "mouth": None}
        return out, face
    if kind == "fairy":
        fl = an["flap"]
        out += [E(bx + s * 6 * g, by - 3, 4 * g * (1 - abs(fl) * .4), 7 * g, mix(d.acc, "#ffffff", .6), s * .5) for s in (-1, 1)]
        out += [E(bx, by + r * .55, r * .55, r * .6, "a"), P([(bx - r * .7, by + r * 1.2), (bx, by + r * .4), (bx + r * .7, by + r * 1.2)], "b")]
        hr = r * .75
        out.append(E(bx, by - r * .3, hr * 1.2, hr * 1.1, d.acc))
        out.append(E(bx, by - r * .2, hr, hr, "#ffe8d8"))
        out += star(bx + hr * .7, by - r * .3 - hr, 2 + k, "#fff0a0")
        face = {"eyes": [(bx - hr * .4, by - r * .2, 1.0), (bx + hr * .4, by - r * .2, 1.0)], "eye_size": hr / 6.5, "iris": d.iris, "mouth": ("smile", bx, by + hr * .1),
                "blush": [(bx - hr * .65, by + hr * .05), (bx + hr * .65, by + hr * .05)]}
        return out, face
    if kind == "bell":
        swing = sw * .3
        out.append(L(bx, by - r * 1.1, bx, by - r * 1.5, 1.6, "d"))
        out.append(P(rot([(bx - r * .55, by - r * .9), (bx + r * .55, by - r * .9), (bx + r * .7, by + r * .2), (bx + r * 1.05, by + r * .8), (bx - r * 1.05, by + r * .8),
                          (bx - r * .7, by + r * .2)], bx, by - r * 1.1, swing), "a"))
        out.append(E(bx + math.sin(swing) * r, by + r * .95, r * .3, r * .3, d.acc))
        out.append(E(bx + r * .4, by - r * 1.15, 2.5, 1.5, "#ff7ab0"))
        face = {"eyes": [(bx - r * .3, by - r * .1, 1.0), (bx + r * .3, by - r * .1, 1.0)], "eye_size": r / 8, "iris": d.iris, "mouth": ("o", bx, by + r * .35)}
        return out, face
    # 晶
    out.append(E(bx, by + r * .9, r * .9, r * .3, "d"))
    for i, (dx, h, a) in enumerate(((-.6, 1.3, -.4), (.6, 1.2, .45), (0, 1.9, 0), (-.25, 1.0, -.15), (.3, 1.1, .2))):
        out += crystal(bx + dx * r, by + r * .9, r * h * (.8 + .3 * k) * .8, a, mix(d.a, "#ffffff", .2 * (i % 2)))
    face = {"eyes": [(bx - r * .3, by - r * .1, 1.0), (bx + r * .25, by - r * .1, 1.0)], "eye_size": r / 8, "iris": d.iris, "mouth": ("o", bx, by + r * .35)}
    return out, face


def build_plant(d, k, an):
    kind = PLANT.get(d.noun, "flower")
    g = .8 + .55 * k + (.15 if d.legend else 0)
    out = []
    sw = an["sway"]
    r = 8 * g * d.v["bh"]
    bx, by = 0, -r - 1.5
    out += [E(bx - r * .5, -1.4, 2.6 * g, 1.6, "d"), E(bx + r * .5, -1.4, 2.6 * g, 1.6, "d")]
    if kind == "mushroom":
        out.append(E(bx, by + 1, r * .75, r * .85, "b"))
        cap_y = by - r * .55
        out.append(E(bx, cap_y, r * (1.4 + .3 * k), r * (.85 + .1 * k), "a"))
        out += [E(bx + dx * r, cap_y - r * .35 + abs(dx) * r * .3, r * .2, r * .16, "b" if d.scheme != "pastel" else d.acc) for dx in (-.8, -.25, .35, .9)]
        face = {"eyes": [(bx - r * .35, by + r * .15, 1.0), (bx + r * .25, by + r * .15, .9)], "eye_size": r / 7.5, "iris": d.iris, "mouth": ("smile", bx - r * .05, by + r * .55)}
        out += brows(d, k, face["eyes"], face["eye_size"])
        return out, face
    if kind == "vine":
        for i in range(5):
            a = -1.5 + i * .75 + sw * .3
            seg, tip = curve(bx, by, a, r * (1.3 + .6 * k), .8 * (1 if i % 2 else -1), 1.6, .9, "d", 4)
            out += seg + leaf(tip[0], tip[1], 4 + 2 * k, a + .6, "#5fb04a")
    if kind == "fruit":
        out.append(E(bx, by, r * 1.05, r, "a"))
        out += leaf(bx + 1, by - r * .9, 6 + 4 * k, .5 + sw * .4) + [L(bx, by - r * .85, bx + .5, by - r * 1.2, 1.2, "#6a4a2a")]
        out += [E(bx + r * .45, by - r * .45, r * .2, r * .15, "#ffffff")]
    else:
        out.append(E(bx, by, r, r * .9, "a"))
    if kind == "sprout":
        for a in (-.5, .5):
            out += leaf(bx, by - r * .8, (5 + 6 * k) * g * .9, a + sw * .4, "#5fc04a")
        if k > .5:
            out += [E(bx + math.sin(a) * 4, by - r * 1.3 - math.cos(a) * 4, 2.2, 3.2, d.acc, a) for a in (-.9, 0, .9)]
    elif kind == "flower":
        n = 5 + int(k * 3)
        pr = r * (.65 + .2 * k)
        cy = by - r * .9 - pr * .5
        for i in range(n):
            a = i * 2 * math.pi / n + sw * .2
            out.append(E(bx + math.sin(a) * pr, cy - math.cos(a) * pr, pr * .45, pr * .7, d.acc, a))
        out.append(E(bx, cy, pr * .45, pr * .45, "#ffe066"))
        out += leaf(bx - r * .8, by + r * .2, 5 + 3 * k, -1.3 + sw * .3) + leaf(bx + r * .8, by + r * .2, 5 + 3 * k, 1.3 + sw * .3)
    out += body_pattern(d, k, bx, by, r, r * .9, "stand", set())[:1]
    face = {"eyes": [(bx - r * .35, by - r * .15, 1.0), (bx + r * .25, by - r * .15, .9)], "eye_size": r / 7.5 * (1.2 - .3 * k), "iris": d.iris,
            "mouth": (d.mouth if d.mouth != "fang" else "smile", bx - r * .05, by + r * .3), "blush": [(bx - r * .65, by + r * .15), (bx + r * .55, by + r * .15)]}
    out += brows(d, k, face["eyes"], face["eye_size"])
    return out, face


def build_biped(d, k, an):
    kind = BIPED.get(d.noun, "ape")
    g = .8 + .55 * k + (.15 if d.legend else 0)
    out = []
    sw = an["sway"]
    if kind == "bellbody":
        r = 9 * g
        by = -r - 2
        out.append(P([(-r * .55, by - r * 1.1), (r * .55, by - r * 1.1), (r * .75, by), (r * 1.1, by + r * .9), (-r * 1.1, by + r * .9), (-r * .75, by)], "a"))
        out.append(E(0, by + r * .9, r * 1.1, r * .2, "d"))
        out += [L(s * r * .8, by - r * .1, s * (r + 3) + sw * 2, by + r * .3, 2.2, "a") for s in (-1, 1)]
        out.append(E(0, by - r * 1.15, r * .25, r * .2, d.acc))
        face = {"eyes": [(-r * .3, by - r * .4, 1.0), (r * .3, by - r * .4, 1.0)], "eye_size": r / 8, "iris": d.iris, "mouth": ("o", 0, by + r * .1)}
        return out, face
    golem = kind == "golem"
    brx = (7 + 4 * k) * d.v["bl"] * (1.3 if golem else 1) * (1.15 if kind == "ape" else 1)
    bry = (8 + 5 * k) * d.v["bh"] * (1 + an["breath"])
    ll = (4 + 2 * k) * d.v["ll"] * (.7 if kind == "ape" else 1)
    by = -ll - bry * .9 + an["bob"] * .4
    bx = 1
    c_body = "a"
    for fside in (True, False):
        o = 2 if fside else 0
        c = "d" if fside else c_body
        out.append(L(bx + o + brx * .25, by + bry * .6, bx + o + brx * .3, -1.5, 3 + 1.5 * k, c))
        out.append(E(bx + o + brx * .2, -1.2, 3 + k, 1.6, c if not golem else "d"))
        if fside:
            out.append(L(bx + brx * .8, by - bry * .5, bx + brx * 1.1 + 2, by + bry * (.8 if kind == "ape" else .2), 2.8 + 1.4 * k, "d"))
    if "wings" in d.acc_list:
        out += wings(d, k, bx + brx * .3, by - bry * .6, 9 + 7 * k, an, "membrane" if d.dragonish else "feather")
    back, over, top = body_acc(d, k, an, (bx, by, brx, bry), (bx - brx * .1, by - bry - 4, 6), None)
    out += back
    if golem:
        out.append(P([(bx - brx, by - bry * .6), (bx - brx * .6, by - bry), (bx + brx * .7, by - bry * .9), (bx + brx, by - bry * .2), (bx + brx * .7, by + bry * .9),
                      (bx - brx * .7, by + bry), (bx - brx * 1.05, by + bry * .3)], c_body))
        out += [P([(bx - brx * .4, by - bry * .3), (bx - brx * .1, by - bry * .5), (bx + brx * .2, by - bry * .1), (bx - brx * .2, by + bry * .1)], hsv(d.a, mv=1.15))]
        out.append(E(bx - brx * .1, by + bry * .1, 2 + k, 2 + k, d.acc))
    else:
        out.append(E(bx, by, brx, bry, c_body))
        out.append(E(bx - brx * .25, by + bry * .2, brx * .55, bry * .6, "b", 0, "!"))
    if kind == "doll":
        out += [L(bx - brx * .5, by - bry * .2 + i * 2.5, bx - brx * .2, by - bry * .2 + i * 2.5, .5, INK) for i in range(3)]
        out += [E(bx - brx * .1, by - bry * .5 + i * 3, .8, .8, "#f0e0a0") for i in range(3)]
    out += over
    arm_y = by - bry * .5
    reach = (.95 if kind == "ape" else .25)
    hand_x, hand_y = bx - brx * 1.1 - 2 + sw * 1.5, by + bry * reach
    out.append(L(bx - brx * .7, arm_y, hand_x, hand_y, 3 + 1.6 * k * (1.4 if kind == "ape" else 1), c_body))
    hc = "#e04a3a" if d.has("wristbands") else (c_body if not golem else "d")
    out.append(E(hand_x, hand_y, 2.4 + k * (1.3 if kind in ("ape", "golem") else .6), 2.4 + k * (1.3 if kind in ("ape", "golem") else .6), hc))
    hr = (5.8 + 1.0 * k) * d.v["hr"] * (.8 if golem else 1)
    hx_, hy = bx - brx * .2, by - bry - hr * .55 + an["bob"] * .3
    if kind == "ape":
        out += [E(hx_ + hr * .7, hy - hr * .1, hr * .35, hr * .35, "a")]
    out.append(E(hx_, hy, hr * 1.05, hr, c_body))
    if kind == "ape":
        out.append(E(hx_ - hr * .3, hy + hr * .15, hr * .65, hr * .65, "b", 0, "!"))
        out.append(E(hx_ - hr * .3, hy - hr * .45, hr * .7, hr * .2, "d"))
    if kind == "doll":
        out.append(E(hx_ + hr * .1, hy - hr * .6, hr * 1.1, hr * .55, d.acc))
        out += [L(hx_ - hr * .8, hy + hr * .55, hx_ - hr * .1, hy + hr * .55, .5, INK, "!")] + [L(hx_ - hr * .7 + i * hr * .2, hy + hr * .45, hx_ - hr * .7 + i * hr * .2, hy + hr * .65, .5, INK, "!") for i in range(4)]
    out += top
    face = eyes_spec(d, k, hx_, hy, hr)
    face["mouth"] = None if kind == "doll" else (d.mouth if d.mouth != "fang" else "cat", hx_ - hr * .4, hy + hr * .5)
    if golem:
        face["iris"] = "#40e0ff" if d.t1 != "火" else "#ffb030"
        face["eye_ry"] = .55
    out += brows(d, k, face["eyes"], face["eye_size"])
    return out, face


def build_bat(d, k, an):
    g = .8 + .55 * k + (.15 if d.legend else 0)
    r = 7 * g * d.v["bh"]
    by = -17 * g + math.sin(an["ph"]) * 2
    bx = 0
    out = []
    fl = an["flap"] * .4
    for s in (1, -1):
        sp = 13 * g * d.v["bl"]
        pts = [(0, 0), (s * sp * .4, -sp * .55), (s * sp, -sp * .4), (s * sp * .9, sp * .1), (s * sp * .65, -sp * .02), (s * sp * .5, sp * .25), (s * sp * .25, sp * .1), (0, sp * .35)]
        pts = rot([(bx + x, by + y) for x, y in pts], bx, by, -s * fl)
        out.append(P(pts, d.acc2 if s == 1 else d.acc))
        out.append(L(bx, by, pts[1][0], pts[1][1], 1.1, "d"))
        out.append(L(pts[1][0], pts[1][1], pts[2][0], pts[2][1], .9, "d"))
    out += [L(bx + s * 2, by + r * .8, bx + s * 2.5, by + r * 1.4, 1, "d") for s in (-1, 1)]
    out.append(E(bx, by, r, r * (1 + an["breath"]), "a"))
    out.append(E(bx, by + r * .3, r * .6, r * .5, "b", 0, "!"))
    ev = d.v["ear"]
    for s in (-1, 1):
        out += horn(bx + s * r * .45, by - r * .6, r * (.8 + .4 * k) * ev, s * .3, r * .6, "a")
        out += horn(bx + s * r * .45, by - r * .65, r * (.5 + .3 * k) * ev, s * .3, r * .3, "b", 0)
    if d.feature > .6:
        out.append(P([(bx - 1.2, by + r * .05), (bx, by - r * .35), (bx + 1.2, by + r * .05)], "d", "!"))
    back, over, top = body_acc(d, k, an, (bx, by + r * .2, r * .8, r * .6), (bx, by - r * .2, r), None)
    out += over + top
    face = {"eyes": [(bx - r * .4, by - r * .2, 1.0), (bx + r * .4, by - r * .2, 1.0)], "eye_size": r / 7 * (1.15 - .3 * k), "iris": d.iris, "mouth": ("cat", bx, by + r * .4)}
    if k > .5:
        face["eye_ry"] = .7
    out += brows(d, k, face["eyes"], face["eye_size"])
    out += [P([(bx - 1.4, by + r * .5), (bx - .8, by + r * .85), (bx - .3, by + r * .5)], "#ffffff", "!")]
    return out, face


def build(d, sp, f):
    k = stage_k(d, sp["stage"] - 1)
    an = anim_state(f)
    n = d.noun
    if n in QUAD:
        prims, face = build_quad(d, k, an)
    elif n == "蝠":
        prims, face = build_bat(d, k, an)
    elif n in BIRD:
        prims, face = build_bird(d, k, an)
    elif n in FISH:
        prims, face = build_fish(d, k, an)
    elif n in SERPENT:
        prims, face = build_serpent(d, k, an)
    elif n in BUG:
        prims, face = build_bug(d, k, an)
    elif n == "蝶":
        prims, face = build_butterfly(d, k, an)
    elif n == "蛙":
        prims, face = build_frog(d, k, an)
    elif n in CRUST:
        prims, face = build_crust(d, k, an)
    elif n in FLOAT:
        prims, face = build_float(d, k, an)
    elif n in PLANT:
        prims, face = build_plant(d, k, an)
    else:
        prims, face = build_biped(d, k, an)
    deep = k >= .9 and not d.legend
    out = {"a": hsv(d.a, ds=.06, mv=.92) if deep else d.a, "b": d.b, "d": hsv(d.d, mv=.92) if deep else d.d,
           "shape": prims, "gloss": d.gloss}
    blink = an["f"] in (10, 11)
    out.update({kk: v for kk, v in face.items() if v is not None})
    if blink:
        out["blink"] = True
    return out


def anim_state(f):
    ph = f / FRAMES * 2 * math.pi
    br = (1 - math.cos(ph)) / 2
    return {"f": f, "ph": ph, "bob": -br * 1.2, "breath": br * 0.045, "sway": math.sin(ph) * 0.35, "flap": math.sin(ph * 2)}


def mirror_spec(spec):
    """背面：左右翻转（转过身去朝右后方）"""
    out = dict(spec)
    sh = []
    for p in spec["shape"]:
        k = p[0][0]
        if k == "e":
            sh.append((p[0], -p[1], p[2], p[3], p[4], p[5], -p[6]))
        elif k == "p":
            sh.append((p[0], [(-x, y) for x, y in p[1]], p[2]))
        else:
            sh.append((p[0], -p[1], p[2], -p[3], p[4], p[5], p[6]))
    out["shape"] = sh
    out.pop("blink", None)
    return out


# ------------------------------------------------------------------ 渲染
def fit_scale(specs, size, scale):
    while True:
        ims = []
        ok = True
        for spec in specs:
            im = gm.render(spec, size, scale, back=False)
            bb = im.getbbox()
            if not bb or bb[0] == 0 or bb[1] == 0 or bb[2] == size or bb[3] == size:
                ok = False
                break
            ims.append(im)
        if ok:
            return ims
        scale *= 0.95


def render_species(args):
    line, only = args
    d = Design(line)
    done = []
    for sp in line:
        if only and sp["key"] not in only:
            continue
        specs = [build(d, sp, f) for f in range(FRAMES)]
        frames = fit_scale(specs, gm.FRONT[0], gm.FRONT[1])
        strip = Image.new("RGBA", (gm.FRONT[0] * FRAMES, gm.FRONT[0]))
        for i, im in enumerate(frames):
            strip.paste(im, (i * gm.FRONT[0], 0))
        strip.save(os.path.join(OUT, f"{sp['key']}_front.png"))
        gm.render_fit(mirror_spec(specs[0]), gm.BACK[0], gm.BACK[1], back=True).save(os.path.join(OUT, f"{sp['key']}_back.png"))
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
