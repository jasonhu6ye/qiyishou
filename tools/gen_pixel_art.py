"""生成奇异兽的像素美术：地面图块、树、玩家与 NPC 行走图。

用法：python3 tools/gen_pixel_art.py
输出到 assets/sprites/。需要 Pillow（pip install pillow）。

这些是程序生成的过渡美术，换成手绘图时保持同样的尺寸和排布即可，
游戏代码按下面注释里的格子位置读取。
"""
from pathlib import Path
import random

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "assets" / "sprites"
T = 16


def hexc(s, a=255):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


# ---------------------------------------------------------------- 地面图块
# tiles.png 一行 16x16：
# 0 草地  1 草地变体  2 花  3 高草  4 小路  5-7 水面三帧  8 高草前景（盖在角色脚上）
GRASS = hexc("#78c467")
GRASS_DARK = hexc("#5fae55")
GRASS_LIGHT = hexc("#93d97c")
TALL = hexc("#3f9a3c")
TALL_DARK = hexc("#2a7429")
TALL_LIGHT = hexc("#6cc25a")
PATH = hexc("#e3c88f")
PATH_DARK = hexc("#c9ad72")
PATH_LIGHT = hexc("#f0dcaa")
WATER = hexc("#3d8fd6")
WATER_DARK = hexc("#2f78bf")
WATER_LIGHT = hexc("#9fd4f5")


def grass_tile(seed):
    im = Image.new("RGBA", (T, T), GRASS)
    rnd = random.Random(seed)
    px = im.load()
    for _ in range(6):
        x, y = rnd.randrange(1, T - 2), rnd.randrange(2, T - 1)
        # 小草簇：两个深色像素 + 一个亮色尖
        px[x, y] = GRASS_DARK
        px[x + 1, y] = GRASS_DARK
        px[x, y - 1] = GRASS_LIGHT
    return im


def flower_tile():
    im = grass_tile(3)
    px = im.load()
    for (cx, cy, petal) in [(4, 5, hexc("#fff6a8")), (11, 11, hexc("#ff9fb5")), (12, 3, hexc("#ffffff"))]:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            px[cx + dx, cy + dy] = petal
        px[cx, cy] = hexc("#f2a33a")
    return im


def blade(px, x, y, h, col, tip):
    """从 (x, y) 向上画一根草叶"""
    for i in range(h):
        px[x, y - i] = col
    px[x, y - h] = tip


def tall_grass_tile():
    im = Image.new("RGBA", (T, T), TALL_DARK)
    px = im.load()
    for x in range(T):
        for y in range(T):
            if (x + y * 3) % 7 == 0:
                px[x, y] = TALL
    # 三排错开的草丛，每丛是一个“W”形
    for row, y in enumerate([5, 10, 15]):
        for cx in range(1 + (row % 2) * 4, T, 8):
            for dx, h in [(-2, 3), (-1, 4), (0, 5), (1, 4), (2, 3)]:
                x = cx + dx
                if 0 <= x < T:
                    blade(px, x, y, h, TALL if dx else TALL_LIGHT, TALL_LIGHT)
    return im


def tall_grass_front():
    """角色站在高草里时盖在脚上的草叶，只占下半格"""
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    px = im.load()
    for cx in [3, 8, 13]:
        for dx, h in [(-2, 3), (-1, 4), (0, 5), (1, 4), (2, 3)]:
            x = cx + dx
            if 0 <= x < T:
                blade(px, x, T - 1, h, TALL if dx else TALL_LIGHT, TALL_LIGHT)
    return im


def path_tile():
    im = Image.new("RGBA", (T, T), PATH)
    rnd = random.Random(7)
    px = im.load()
    for _ in range(5):
        x, y = rnd.randrange(1, T - 2), rnd.randrange(1, T - 1)
        px[x, y] = PATH_DARK
        px[x + 1, y] = PATH_DARK
        px[x, y - 1] = PATH_LIGHT
    return im


def water_tile(frame):
    im = Image.new("RGBA", (T, T), WATER)
    px = im.load()
    for y in range(T):
        for x in range(T):
            if (x + y * 2) % 11 == 0:
                px[x, y] = WATER_DARK
    for (x0, y0) in [(2, 4), (9, 9), (4, 13)]:
        x0 = (x0 + frame * 2) % T
        for i in range(4):
            px[(x0 + i) % T, y0] = WATER_LIGHT
    return im


def make_tiles():
    tiles = [grass_tile(1), grass_tile(2), flower_tile(), tall_grass_tile(), path_tile(),
             water_tile(0), water_tile(1), water_tile(2), tall_grass_front()]
    sheet = Image.new("RGBA", (T * len(tiles), T), (0, 0, 0, 0))
    for i, im in enumerate(tiles):
        sheet.paste(im, (i * T, 0))
    sheet.save(OUT / "tiles.png")


# ---------------------------------------------------------------- 树
OUTLINE = hexc("#1e3b24")


def outline(im, col):
    """给不透明区域外圈描一像素边"""
    w, h = im.size
    src = im.copy().load()
    px = im.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3]:
                continue
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] and src[nx, ny] != hexc("#000000", 64):
                    px[x, y] = col
                    break


def disc(px, cx, cy, r, col, w, h):
    for y in range(h):
        for x in range(w):
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                px[x, y] = col


def make_tree():
    """16x32，原点在底边中心；下半格是树干和影子，上方是树冠"""
    w, h = 16, 32
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for x in range(6, 10):
        for y in range(21, 28):
            px[x, y] = hexc("#7a4f2a")
    px[6, 22] = px[6, 24] = hexc("#5a3a1f")
    disc(px, 8, 14, 7.5, hexc("#2e7537"), w, h)
    disc(px, 8, 10, 6, hexc("#3a8b44"), w, h)
    disc(px, 6, 8, 3, hexc("#56a95c"), w, h)
    for (x, y) in [(5, 6), (4, 8), (10, 12), (11, 15)]:
        px[x, y] = hexc("#7bc77a")
    outline(im, OUTLINE)
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sp = shadow.load()
    for x in range(1, 15):
        for y in range(28, 32):
            if ((x - 7.5) / 7) ** 2 + ((y - 29.5) / 2) ** 2 <= 1:
                sp[x, y] = (0, 0, 0, 64)
    shadow.alpha_composite(im)
    shadow.save(OUT / "tree.png")


# ---------------------------------------------------------------- 角色
# 行走图 3 列（站立、迈左脚、迈右脚）x 4 行（下、左、右、上），每帧 16x20，脚底在帧底边。
CHAR_W, CHAR_H = 16, 20

HEAD_DOWN = [
    "................",
    "................",
    ".....KKKKKK.....",
    "....KRRRRRRK....",
    "...KRRWWRRRRK...",
    "...KRRRRRRRRK...",
    "...KKKKKKKKKK...",
    "...KDSSSSSSDK...",
    "...KSKSSSSKSK...",
    "...KSSSSSSSSK...",
    "....KSSSSSSK....",
]
BODY_DOWN = [
    "...KBBBBBBBBK...",
    "..KSBBbBBbBBSK..",
    "..KSKBBBBBBKSK..",
    "..KK.KBBBBK.KK..",
]
HEAD_UP = [
    "................",
    "................",
    ".....KKKKKK.....",
    "....KRRRRRRK....",
    "...KRRRRRRRRK...",
    "...KRRRRRRRRK...",
    "...KRRRRRRRRK...",
    "...KDDDDDDDDK...",
    "...KDDDDDDDDK...",
    "...KDDDDDDDDK...",
    "....KDDDDDDK....",
]
BODY_UP = [
    "...KBBBBBBBBK...",
    "..KSBBBBBBBBSK..",
    "..KSKBbbbbBKSK..",
    "..KK.KBBBBK.KK..",
]
LEGS_FRONT = [
    [
        "....KPPPPPPK....",
        "....KPPKKPPK....",
        "....KPK..KPK....",
        "....KKK..KKK....",
        "................",
    ],
    [
        "....KPPPPPPK....",
        "....KPPKKPPK....",
        "....KPK..KKK....",
        "....KKK.........",
        "................",
    ],
    [
        "....KPPPPPPK....",
        "....KPPKKPPK....",
        "....KKK..KPK....",
        ".........KKK....",
        "................",
    ],
]
HEAD_LEFT = [
    "................",
    "................",
    ".....KKKKKK.....",
    "....KRRRRRRK....",
    "...KRRRRWRRRK...",
    "..KRRRRRRRRRK...",
    ".KKKKKKRRRRRK...",
    "...KSSSSDDDDK...",
    "...KKSSSSDDDK...",
    "...KSSSSSSDDK...",
    "....KSSSSSSK....",
]
BODY_LEFT = [
    "....KBBBBBBK....",
    "....KBBSBBBK....",
    "....KBBSBBBK....",
    ".....KBBBBK.....",
]
LEGS_SIDE = [
    [
        ".....KPPPPK.....",
        ".....KPPPPK.....",
        ".....KPKKPK.....",
        ".....KKKKKK.....",
        "................",
    ],
    [
        ".....KPPPPK.....",
        "....KPPKKPPK....",
        "...KPK....KPK...",
        "...KKK....KKK...",
        "................",
    ],
    [
        ".....KPPPPK.....",
        ".....KPPPPK.....",
        "....KPK..KPK....",
        "....KKK..KKK....",
        "................",
    ],
]

PLAYER_PALETTE = {
    "K": "#2b2b45", "R": "#d84a4a", "W": "#ffffff", "D": "#3a2a24", "S": "#ffd9b3",
    "B": "#3d6fd1", "b": "#9cc0ff", "P": "#3a3a5c",
}
NPC_PALETTE = {
    "K": "#2b2b45", "R": "#d8d0b8", "W": "#f5f0e0", "D": "#c8c2b0", "S": "#f0c9a0",
    "B": "#3f8f6b", "b": "#7fc9a3", "P": "#5a4a3a",
}


def frame(rows, palette):
    assert len(rows) == CHAR_H, len(rows)
    im = Image.new("RGBA", (CHAR_W, CHAR_H), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(rows):
        assert len(row) == CHAR_W, (y, row)
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = hexc(palette[ch])
    return im


def make_character(palette, name):
    sheet = Image.new("RGBA", (CHAR_W * 3, CHAR_H * 4), (0, 0, 0, 0))
    for col in range(3):
        down = frame(HEAD_DOWN + BODY_DOWN + LEGS_FRONT[col], palette)
        left = frame(HEAD_LEFT + BODY_LEFT + LEGS_SIDE[col], palette)
        right = left.transpose(Image.FLIP_LEFT_RIGHT)
        up = frame(HEAD_UP + BODY_UP + LEGS_FRONT[col], palette)
        for row, im in enumerate([down, left, right, up]):
            sheet.paste(im, (col * CHAR_W, row * CHAR_H))
    sheet.save(OUT / f"{name}.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    make_tiles()
    make_tree()
    make_character(PLAYER_PALETTE, "player")
    make_character(NPC_PALETTE, "npc_elder")
    print("已生成：", ", ".join(sorted(p.name for p in OUT.glob("*.png"))))


if __name__ == "__main__":
    main()
