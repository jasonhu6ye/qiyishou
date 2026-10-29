"""716 只幻兽的外观设定和生图提示词：data/dex/designs.json 和 docs/dex-designs.md。

设定来自 gen_species_art 的进化线设计（原型动物、配色、属性饰物、花纹、眼型），
写成中文外观描述（给画师）和英文提示词（给图像生成模型），同一条线共用一段「线设定」，
每个阶段再说明体型和新增的部件，保证进化前后看得出是同一只。

python3 tools/dex_designs.py
"""
import colorsys
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import gen_species_art as ga  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STYLE = ("Pokemon-style official creature sprite, Gen 5 Black/White pixel art, 96x96, clean 1px dark outline, "
         "3/4 front view facing left, full body, simple cel shading with 3-4 tones per color, limited palette, "
         "plain white background, single creature, no text")
EN = {
    "鼠": "mouse", "兔": "rabbit", "犬": "puppy dog", "猫": "cat", "猪": "pig", "牛": "bull", "羊": "sheep", "猴": "monkey", "熊": "bear",
    "獾": "badger", "狸": "raccoon dog", "貂": "marten", "鼬": "weasel", "鹿": "deer", "狐": "fox", "狼": "wolf", "驹": "pony horse",
    "狮": "lion", "蜥": "lizard", "豹": "leopard", "虎": "tiger", "龟": "turtle", "獭": "otter", "犀": "rhinoceros", "象": "elephant",
    "驼": "camel", "鳄": "crocodile", "鼹": "mole", "穿山甲": "pangolin", "鬣": "hyena", "豺": "dhole wild dog", "犰狳": "armadillo",
    "袋鼠": "kangaroo", "龙": "western dragon", "雀": "sparrow", "鸽": "pigeon", "鸭": "duck", "鹅": "goose", "鸟": "songbird",
    "鹰": "eagle", "隼": "falcon", "燕": "swallow", "鸮": "owl", "鹤": "crane", "鸦": "crow", "鹏": "giant roc bird", "蝠": "bat",
    "鱼": "fish", "鲤": "carp koi", "鲨": "shark", "鲸": "whale", "鳐": "manta ray", "豚": "dolphin", "蛇": "snake", "鳗": "eel",
    "蛟": "eastern serpent dragon", "蛾": "moth", "蜂": "bee", "蚁": "ant", "甲": "beetle", "螳": "praying mantis", "蛛": "spider",
    "蚕": "caterpillar", "萤": "firefly", "蜓": "dragonfly", "蝉": "cicada", "蟋": "cricket", "蜗": "snail", "蝎": "scorpion",
    "蜈": "centipede", "锹": "stag beetle", "蝶": "butterfly", "蛙": "frog", "蟹": "crab", "虾": "shrimp", "贝": "clam", "螺": "sea snail",
    "菊石": "ammonite", "母": "jellyfish", "灵": "wisp spirit", "魂": "fire soul ghost", "影": "shadow ghost", "灯": "lantern ghost",
    "面": "floating mask spirit", "精": "fairy", "铃": "living bell", "晶": "crystal creature", "苗": "seedling bulb", "花": "flower",
    "藤": "vine plant", "菇": "mushroom", "果": "fruit", "猿": "ape", "偶": "doll puppet", "石像": "stone golem", "钟": "temple bell",
}
ACC = {  # 饰物 -> (中文, 英文)
    "tail_flame": ("尾巴尖燃着火焰", "flame burning on its tail tip"), "head_flame": ("头顶一簇火苗", "a small flame on its head"),
    "back_flames": ("背上一排火焰", "a row of flames along its back"), "mane_flame": ("火焰鬃毛", "a mane made of fire"),
    "feet_flame": ("脚下冒火", "flames around its feet"), "back_fin": ("背鳍", "a dorsal fin on its back"), "ear_fin": ("鳍状耳朵", "fin-shaped ears"),
    "bubbles": ("身边冒泡泡", "bubbles floating around it"), "wave_marks": ("身上有波浪纹", "wave patterns on its body"),
    "tail_fin": ("尾巴末端是鱼鳍", "a fish fin at the end of its tail"), "head_leaf": ("头顶长着叶子", "leaves sprouting from its head"),
    "back_bulb": ("背上长着花苞", "a plant bulb growing on its back"), "leaf_collar": ("脖子一圈叶子领", "a collar of leaves around its neck"),
    "back_flower": ("背上开着一朵花", "a flower blooming on its back"), "tail_leaf": ("尾巴尖是一片叶子", "a leaf at the tip of its tail"),
    "tail_bolt": ("闪电形尾巴", "a lightning-bolt shaped tail"), "bolt_marks": ("身上有闪电纹", "lightning bolt markings"),
    "spiky_crest": ("头顶炸开的尖刺毛", "spiky electric fur on its head"), "antenna_balls": ("头上两根带光球的触角", "two antennae tipped with glowing orbs"),
    "cheeks": ("红色电气脸颊", "red electric cheek pouches"), "back_crystals": ("背上长着冰晶", "ice crystals on its back"),
    "ice_crown": ("头顶冰晶冠", "an ice crystal crown"), "frost_ruff": ("脖子一圈霜毛", "a frosty white fur ruff"), "icicles": ("下巴挂冰柱", "icicles hanging from its chin"),
    "wristbands": ("手腕缠着护腕", "red wristbands"), "headband": ("系着头带", "a red headband with trailing ends"), "belt": ("腰间系着腰带", "a champion belt"),
    "scar": ("脸上有伤疤", "a scar across its face"), "poison_spots": ("紫色毒斑", "purple poison spots"), "back_spikes": ("背上毒刺", "toxic spikes on its back"),
    "drip": ("嘴角滴着毒液", "dripping poison"), "gas": ("身上冒毒气", "toxic gas clouds rising from it"), "rock_armor": ("背上岩石铠甲", "rocky armor plates on its back"),
    "mud_marks": ("身上沾着泥巴", "mud patches"), "big_claws": ("大爪子", "big digging claws"), "nose_horn": ("鼻子上有角", "a horn on its nose"),
    "wings": ("一对翅膀", "a pair of wings"), "crest_feathers": ("头顶冠羽", "crest feathers on its head"), "forehead_gem": ("额头宝石", "a gem on its forehead"),
    "orbs": ("身边漂浮着灵能球", "psychic orbs orbiting it"), "third_eye": ("额头第三只眼", "a third eye on its forehead"), "halo": ("头顶光环", "a halo above its head"),
    "antennae": ("触角", "insect antennae"), "small_wings": ("一对小薄翅", "small translucent insect wings"), "bands": ("身上横纹", "banded stripes"),
    "back_rocks": ("背上嵌着石块", "rocks embedded in its back"), "armor_plates": ("身上装甲板", "armor plates"), "crystal_horn": ("水晶角", "a crystal horn"),
    "ghost_tail": ("下半身化成幽灵尾巴", "a wispy ghost tail instead of legs"), "wisps": ("身边飘着鬼火", "ghostly will-o-wisps around it"),
    "stitches": ("身上有缝线", "stitched seams on its body"), "dragon_horns": ("一对龙角", "a pair of dragon horns"), "back_ridge": ("背脊尖刺", "spiky ridge along its back"),
    "whiskers": ("龙须", "long dragon whiskers"), "mask": ("眼部黑色面罩花纹", "a dark bandit mask marking over its eyes"), "spiky_ruff": ("脖子一圈尖刺毛", "a spiky dark fur ruff"),
    "claw_marks": ("身上爪痕纹", "claw-mark patterns"), "helmet": ("金属头盔", "a metal helmet"), "blade_fins": ("背上刀刃鳍", "blade-like steel fins"),
    "bolts": ("身上铆钉", "metal rivets"), "ribbon": ("头上蝴蝶结", "a ribbon bow on its head"), "star_mark": ("身上星形印记", "a star mark on its body"),
    "fairy_wings": ("妖精翅膀", "sparkly fairy wings"), "flower_crown": ("花冠", "a flower crown"), "heart_cheeks": ("心形腮红", "heart-shaped blush"),
    "scarf": ("围巾", "a scarf"), "patch": ("身上一块花斑", "a colored patch on its body"), "tuft": ("头顶一撮毛", "a tuft of hair on its head"), "collar": ("项圈和铃铛", "a collar with a bell"),
}
PATTERN = {"spots": ("斑点", "spots"), "stripes": ("条纹", "stripes"), "saddle": ("背上一块深色鞍纹", "a darker saddle marking"),
           "socks": ("四只脚是浅色袜子", "light-colored socks on its feet"), "tipped": ("尾巴尖是另一种颜色", "a differently colored tail tip"),
           "bands": ("环纹", "ring bands"), "belly": ("浅色肚皮", "a light belly")}
EYES = {"round": ("大圆眼", "big round eyes"), "sharp": ("锐利的眼神", "sharp narrow eyes"), "sleepy": ("半睁的困倦眼", "sleepy half-closed eyes"), "tiny": ("豆豆眼", "small bead eyes")}
STAGE = [("幼小、圆滚滚、头大身小，表情可爱", "baby form, small and chubby, big head, cute expression"),
         ("少年体，身体拉长，部件变大，表情自信", "middle evolution, leaner and taller, larger features, confident expression"),
         ("完全体，体型高大威武，部件最华丽，表情凶悍", "final evolution, large and powerful, most elaborate features, fierce expression")]


def color_name(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hh, s, v = colorsys.rgb_to_hsv(r, g, b)
    if v < .22:
        return "黑", "black"
    if s < .12:
        return ("白", "white") if v > .85 else ("灰", "gray")
    hue = hh * 360
    names = [(15, "红", "red"), (40, "橙", "orange"), (65, "黄", "yellow"), (160, "绿", "green"), (200, "青", "teal"), (250, "蓝", "blue"),
             (290, "紫", "purple"), (340, "粉", "pink"), (361, "红", "red")]
    for lim, zh, en in names:
        if hue < lim:
            light = ("浅", "light ") if v > .8 and s < .45 else ("深", "dark ") if v < .5 else ("", "")
            return light[0] + zh, light[1] + en
    return "红", "red"


def stage_idx(d, sp):
    if d.legend or d.stages == 1:
        return 2 if d.legend else 1
    k = ga.stage_k(d, sp["stage"] - 1)
    return 0 if k < .3 else 1 if k < .8 else 2


def main():
    species = json.load(open(os.path.join(ROOT, "data", "dex", "species.json"), encoding="utf-8"))
    lines = {}
    for sp in species:
        lines.setdefault(sp["line"], []).append(sp)
    out, md = {}, ["# 幻兽外观设定", "", "由 `tools/dex_designs.py` 生成。每条进化线一段线设定，每只再写阶段差异。英文提示词见 `data/dex/designs.json`。", ""]
    for line_no, line in sorted(lines.items()):
        d = ga.Design(line)
        animal = EN.get(d.noun, "creature")
        ca, cb, cc = color_name(d.a), color_name(d.b), color_name(d.acc)
        acc = [ACC[a] for a in dict.fromkeys(d.acc_list) if a in ACC]
        pat = PATTERN.get(d.pattern)
        eye = EYES[d.eye_style]
        zh_line = f"以{d.noun}为原型的{'/'.join(d.types)}属性幻兽。主色{ca[0]}，副色{cb[0]}，点缀色{cc[0]}；{eye[0]}"
        en_line = f"a {'/'.join(ga_type_en(t) for t in d.types)}-type creature based on a {animal}, main color {ca[1]}, secondary {cb[1]}, accent {cc[1]}, {eye[1]}"
        if pat:
            zh_line += f"，{pat[0]}"
            en_line += f", {pat[1]}"
        md += [f"## {' → '.join(s['name'] for s in line)}", "", zh_line + "。", ""]
        for sp in line:
            si = stage_idx(d, sp)
            # 饰物随阶段逐渐长出来：初阶只有第一个，中阶两个，完全体全部
            n_acc = len(acc) if si == 2 else min(len(acc), si + 1)
            parts = acc[:n_acc]
            zh = f"{STAGE[si][0]}。" + ("特征：" + "、".join(p[0] for p in parts) + "。" if parts else "")
            if d.legend:
                zh = "传说级，体型巨大、姿态庄严，带一圈光晕。" + zh
            en = f"{en_line}, {STAGE[si][1]}" + ("".join(", " + p[1] for p in parts))
            if d.legend:
                en += ", legendary, majestic pose, subtle glowing aura"
            out[sp["key"]] = {"name": sp["name"], "line": line_no, "archetype": d.noun, "colors": {"main": d.a, "secondary": d.b, "accent": d.acc},
                              "appearance": zh_line + "。" + zh, "prompt": f"{STYLE}. {en}."}
            md.append(f"- **#{sp['dex']:03d} {sp['name']}**：{zh}")
        md.append("")
    with open(os.path.join(ROOT, "data", "dex", "designs.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "docs", "dex-designs.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(len(out))


TYPE_EN = {"普通": "normal", "火": "fire", "水": "water", "草": "grass", "电": "electric", "冰": "ice", "格斗": "fighting", "毒": "poison",
           "大地": "ground", "飞行": "flying", "灵能": "psychic", "虫": "bug", "岩石": "rock", "幽灵": "ghost", "龙": "dragon", "恶": "dark",
           "钢": "steel", "妖精": "fairy"}


def ga_type_en(t):
    return TYPE_EN[t]


if __name__ == "__main__":
    main()
