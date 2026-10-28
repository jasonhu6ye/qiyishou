"""战斗背景：320x240 一整张，包含天空、云、远山、树林、草地和两块站台。

站台中心与 scripts/battle/battle_view.gd 里的立绘脚底位置一致：
对手 (236, 82)，自己 (84, 154)。每条道路一张：battle_bg_<区域序号>.png。
"""
import math
import random

from PIL import Image

W, H = 320, 240
HORIZON = 66
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
ENEMY_PAD = (236, 82, 50, 11)
MY_PAD = (84, 154, 64, 14)


def hexc(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


THEMES = [
    {  # 1号道路：晴朗上午
        "sky": ["#5fb4f0", "#86c9f5", "#aedcf8", "#d4eefb"], "cloud": "#ffffff", "cloud_dark": "#c9e2f2",
        "far": "#9cc7d6", "far_light": "#bfdde6", "near": "#6fae8a", "near_light": "#8cc79f",
        "trees": "#3f8a52", "trees_dark": "#2c6b40", "trees_light": "#5aa868",
        "grass": ["#8fd46e", "#7fc962", "#70bb57"], "tuft": "#5aa848", "tuft_light": "#b2e68f",
        "pad": "#b5e68e", "pad_light": "#d0f2a8", "pad_dark": "#86c066", "dirt": "#9a7a4e", "dirt_dark": "#6e5434",
    },
    {  # 2号道路：傍晚
        "sky": ["#e8885a", "#f2a568", "#f8c27e", "#fde0a6"], "cloud": "#ffe9c8", "cloud_dark": "#f0b98a",
        "far": "#c98a6e", "far_light": "#e0a988", "near": "#a6705a", "near_light": "#c08a6e",
        "trees": "#5e6b3e", "trees_dark": "#454f2c", "trees_light": "#7a8650",
        "grass": ["#b9cf72", "#a8c264", "#97b257"], "tuft": "#7f9a44", "tuft_light": "#d9e69a",
        "pad": "#d3e392", "pad_light": "#e8f0b0", "pad_dark": "#a9bf6c", "dirt": "#9a6e48", "dirt_dark": "#6a4a30",
    },
]


def _sky(px, th):
    cols = [hexc(c) for c in th["sky"]]
    n = len(cols) - 1
    for y in range(HORIZON):
        f = y / HORIZON * n
        for x in range(W):
            g = f + (BAYER[y % 4][x % 4] / 16 - 0.5) * 0.5
            px[x, y] = cols[max(0, min(n, int(g + 0.5)))]


def _cloud(px, cx, cy, parts, th):
    light, dark = hexc(th["cloud"]), hexc(th["cloud_dark"])
    for dx, dy, r in parts:
        for y in range(int(cy + dy - r), int(cy + dy + r) + 1):
            for x in range(int(cx + dx - r), int(cx + dx + r) + 1):
                if 0 <= x < W and 0 <= y < HORIZON and (x - cx - dx) ** 2 + (y - cy - dy) ** 2 <= r * r:
                    px[x, y] = dark if y > cy + 1 else light


def _ridge(px, base, amp, freq, seed, col, light, top_limit=0):
    rnd = random.Random(seed)
    ph = [rnd.random() * 6.28 for _ in range(3)]
    prev = None
    for x in range(W):
        h = base - amp * (0.55 * math.sin(x * freq + ph[0]) + 0.3 * math.sin(x * freq * 2.3 + ph[1])
                          + 0.15 * math.sin(x * freq * 5.1 + ph[2]))
        h = int(max(top_limit, h))
        for y in range(h, HORIZON):
            px[x, y] = col
        # 受光的山脊：左高右低的坡面提亮两像素
        if prev is not None and h <= prev:
            px[x, h] = light
            if h + 1 < HORIZON:
                px[x, h + 1] = light
        prev = h


def _treeline(px, th, seed):
    rnd = random.Random(seed)
    col, dark, light = hexc(th["trees"]), hexc(th["trees_dark"]), hexc(th["trees_light"])
    x = -4
    while x < W + 6:
        r = rnd.randint(4, 6)
        cy = HORIZON - r + rnd.randint(1, 3)
        for y in range(cy - r, HORIZON):
            for xx in range(x - r, x + r + 1):
                if 0 <= xx < W and (xx - x) ** 2 + (y - cy) ** 2 <= r * r or (0 <= xx < W and y >= cy):
                    if not (0 <= xx < W):
                        continue
                    d = (xx - x + (y - cy)) / r
                    px[xx, y] = light if d < -0.9 else dark if d > 0.6 else col
        x += r + rnd.randint(2, 5)


def _ground(px, th, seed):
    cols = [hexc(c) for c in th["grass"]]
    n = len(cols) - 1
    for y in range(HORIZON, H):
        f = (y - HORIZON) / (H - HORIZON) * n
        for x in range(W):
            g = f + (BAYER[y % 4][x % 4] / 16 - 0.5) * 0.5
            px[x, y] = cols[max(0, min(n, int(g + 0.5)))]
    rnd = random.Random(seed)
    tuft, tl = hexc(th["tuft"]), hexc(th["tuft_light"])
    for _ in range(160):
        x, y = rnd.randrange(2, W - 3), rnd.randrange(HORIZON + 3, H - 1)
        size = 1 + (y - HORIZON) // 60
        for k in range(size + 1):
            px[x, y - k] = tuft
            px[x + 2, y - k + 1] = tuft
        px[x + 1, y] = tuft
        px[x, y - size - 1] = tl


def _pad(px, pad, th):
    cx, cy, rx, ry = pad
    top, light, dark = hexc(th["pad"]), hexc(th["pad_light"]), hexc(th["pad_dark"])
    dirt, dirt_dark = hexc(th["dirt"]), hexc(th["dirt_dark"])
    thick = 3 if ry < 12 else 4
    # 侧面（泥土）
    for y in range(int(cy - ry), int(cy + ry + thick) + 2):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            a = (x + 0.5 - cx) / rx
            for t in range(thick + 1):
                b = (y + 0.5 - cy - t) / ry
                if a * a + b * b <= 1.0 and b > 0:
                    px[x, y] = dirt_dark if t >= thick - 1 or a > 0.55 else dirt
                    break
    # 顶面
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            a, b = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            r2 = a * a + b * b
            if r2 <= 1.0:
                d = -a * 0.6 - b * 0.8
                g = d * 1.6 + (BAYER[y % 4][x % 4] / 16 - 0.5) * 0.6
                px[x, y] = light if r2 > 0.72 and d > 0.15 else dark if (r2 > 0.8 and d < -0.2) or g < -1.0 else top
    # 边缘草丛
    rnd = random.Random(cx)
    for i in range(18):
        ang = rnd.uniform(0.15, math.pi - 0.15)
        x, y = int(cx + math.cos(ang) * rx * 0.98), int(cy + math.sin(ang) * ry + thick - 1)
        px[x, y] = dark
        px[x, y - 1] = dark
        px[x + 1, y - 2] = light


def make_battle_bgs(out_dir):
    for i, th in enumerate(THEMES):
        im = Image.new("RGBA", (W, H))
        px = im.load()
        _sky(px, th)
        _cloud(px, 150, 16, [(-10, 2, 7), (0, -2, 10), (11, 1, 8), (20, 4, 5), (-18, 5, 4)], th)
        _cloud(px, 40, 34, [(-6, 1, 5), (2, -1, 7), (10, 2, 5)], th)
        _cloud(px, 296, 12, [(-5, 1, 4), (2, -1, 6), (9, 2, 4)], th)
        _ridge(px, 50, 14, 0.021, 10 + i, hexc(th["far"]), hexc(th["far_light"]), 26)
        _ridge(px, 58, 8, 0.037, 20 + i, hexc(th["near"]), hexc(th["near_light"]), 40)
        _treeline(px, th, 30 + i)
        _ground(px, th, 40 + i)
        _pad(px, ENEMY_PAD, th)
        _pad(px, MY_PAD, th)
        im.save(out_dir / f"battle_bg_{i}.png")
