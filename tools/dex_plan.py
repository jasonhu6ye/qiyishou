"""幻兽规划：18 种属性、招式、特性、716 只幻兽（种族值、进化、招式表、动态模型）以及奈尔斯地区的刷新地点。

所有数据由固定随机种子生成，重复运行结果完全一样。手工设定的部分（初始幻兽、已有的 14 只、
准神、传说）写在本文件里；其余按属性和区域的规则批量生成。改规则后重新运行即可。

输出：
  data/dex/types.json      属性和克制表
  data/dex/moves.json      招式
  data/dex/abilities.json  特性
  data/dex/species.json    716 只幻兽
  data/dex/spawns.json     每个地点刷新什么、几级、多稀有
  docs/dex-plan.md         规划说明和统计

python3 tools/dex_plan.py
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import world_plan as wp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "dex")
TOTAL = 716
rng = random.Random(20261028)

# ---------------------------------------------------------------- 属性
TYPES = ["普通", "火", "水", "草", "电", "冰", "格斗", "毒", "大地", "飞行", "灵能", "虫", "岩石", "幽灵", "龙", "恶", "钢", "妖精"]
TYPE_COLOR = {
    "普通": "#a8a77a", "火": "#ee8130", "水": "#6390f0", "草": "#7ac74c", "电": "#f7d02c", "冰": "#96d9d6",
    "格斗": "#c22e28", "毒": "#a33ea1", "大地": "#e2bf65", "飞行": "#a98ff3", "灵能": "#f95587", "虫": "#a6b91a",
    "岩石": "#b6a136", "幽灵": "#735797", "龙": "#6f35fc", "恶": "#705746", "钢": "#b7b7ce", "妖精": "#d685ad",
}
# 攻击属性 -> {防守属性: 倍率}，未列出的为 1
CHART = {
    "普通": {"岩石": .5, "幽灵": 0, "钢": .5},
    "火": {"火": .5, "水": .5, "草": 2, "冰": 2, "虫": 2, "岩石": .5, "龙": .5, "钢": 2},
    "水": {"火": 2, "水": .5, "草": .5, "大地": 2, "岩石": 2, "龙": .5},
    "草": {"火": .5, "水": 2, "草": .5, "毒": .5, "大地": 2, "飞行": .5, "虫": .5, "岩石": 2, "龙": .5, "钢": .5},
    "电": {"水": 2, "草": .5, "电": .5, "大地": 0, "飞行": 2, "龙": .5},
    "冰": {"火": .5, "水": .5, "草": 2, "冰": .5, "大地": 2, "飞行": 2, "龙": 1, "钢": .5},
    "格斗": {"普通": 2, "冰": 2, "毒": .5, "飞行": .5, "灵能": .5, "虫": .5, "岩石": 2, "幽灵": 0, "恶": 2, "钢": 2, "妖精": .5},
    "毒": {"草": 2, "毒": .5, "大地": .5, "岩石": .5, "幽灵": .5, "钢": 0, "妖精": 2},
    "大地": {"火": 2, "草": .5, "电": 2, "毒": 2, "飞行": 0, "虫": .5, "岩石": 2, "钢": 2},
    "飞行": {"草": 2, "电": .5, "格斗": 2, "虫": 2, "岩石": .5, "钢": .5},
    "灵能": {"格斗": 2, "毒": 2, "灵能": .5, "恶": 0, "钢": .5},
    "虫": {"火": .5, "草": 2, "格斗": .5, "毒": .5, "飞行": .5, "灵能": 2, "幽灵": .5, "恶": 2, "钢": .5, "妖精": .5},
    "岩石": {"火": 2, "冰": 2, "格斗": .5, "大地": .5, "飞行": 2, "虫": 2, "钢": .5},
    "幽灵": {"普通": 0, "灵能": 2, "幽灵": 2, "恶": .5},
    "龙": {"龙": 1, "钢": .5, "妖精": 0},
    "恶": {"格斗": .5, "灵能": 2, "幽灵": 2, "恶": .5, "妖精": .5},
    "钢": {"火": .5, "水": .5, "电": .5, "冰": 2, "岩石": 2, "钢": .5, "妖精": 2},
    "妖精": {"火": .5, "格斗": 2, "毒": .5, "龙": 1, "恶": 2, "钢": .5},
}
STATS = ["hp", "atk", "def", "spa", "spd", "spe"]
STAT_NAMES = {"hp": "体力", "atk": "攻击", "def": "防御", "spa": "特攻", "spd": "特防", "spe": "速度"}

# ---------------------------------------------------------------- 起名用的字
# 每种属性三档修饰字（弱、中、强），进化后换更强的一档
MORPH = {
    "普通": [["团", "毛", "圆", "咕", "嘟", "绒"], ["壮", "疾", "长", "大", "灵"], ["霸", "巨", "雄", "王"]],
    "火": [["火", "焰", "炭", "烛", "暖"], ["炎", "烈", "赤", "灼", "焚"], ["炽", "煌", "爆", "熔", "炎狱"]],
    "水": [["泡", "滴", "湿", "涟", "汐"], ["浪", "潮", "涌", "澜", "渊"], ["海", "沧", "溟", "瀑", "怒涛"]],
    "草": [["芽", "叶", "苗", "嫩", "籽"], ["森", "藤", "蔓", "荆", "翠"], ["古木", "繁", "茂", "林", "荫"]],
    "电": [["电", "麻", "闪", "微光"], ["雷", "霆", "伏", "磁"], ["轰", "霹", "天雷", "极电"]],
    "冰": [["雪", "霜", "凉", "冰"], ["寒", "凛", "冻", "晶"], ["极寒", "冰封", "玄冰", "凛冬"]],
    "格斗": [["拳", "蛮", "斗", "力"], ["武", "刚", "猛", "强"], ["霸拳", "宗师", "破", "狂"]],
    "毒": [["毒", "斑", "紫", "酸"], ["瘴", "蚀", "腐", "剧"], ["魔毒", "瘟", "邪", "冥毒"]],
    "大地": [["沙", "泥", "土", "尘"], ["地", "壤", "裂", "震"], ["大地", "崩", "岳", "厚土"]],
    "飞行": [["羽", "风", "翔", "啾"], ["疾风", "翼", "云", "翱"], ["苍穹", "天", "飓", "凌霄"]],
    "灵能": [["梦", "念", "幻", "星"], ["灵", "玄", "心", "镜"], ["圣", "神念", "冥想", "天启"]],
    "虫": [["绒", "茧", "蠕", "芝"], ["甲", "刺", "翅", "织"], ["铠", "霸翅", "虹", "千足"]],
    "岩石": [["石", "砾", "卵", "岩"], ["磐", "岗", "峭", "硬"], ["巨岩", "山", "磐岳", "坚"]],
    "幽灵": [["影", "幽", "鬼", "夜"], ["魂", "冥", "魅", "寂"], ["冥王", "怨", "幽冥", "无相"]],
    "龙": [["鳞", "角", "幼"], ["龙", "蛟", "翔"], ["苍龙", "真龙", "天龙", "龙王"]],
    "恶": [["暗", "黑", "狡", "偷"], ["恶", "邪", "魇", "诡"], ["魔", "夜王", "暴", "深渊"]],
    "钢": [["铁", "钉", "铜", "锈"], ["钢", "铠", "锋", "刃"], ["合金", "重钢", "铁壁", "钢王"]],
    "妖精": [["萌", "糖", "铃", "棉"], ["仙", "妖", "月", "花冠"], ["星辉", "圣光", "彩", "仙后"]],
}
# 每种属性常见的形体名
NOUNS = {
    "普通": ["鼠", "兔", "犬", "猫", "猪", "牛", "羊", "雀", "鸽", "猴", "熊", "獾", "狸", "貂", "鸭", "鹿"],
    "火": ["狐", "狼", "犬", "驹", "狮", "蜥", "雀", "猴", "豹", "虎", "龟", "蜗", "蛾", "鼬"],
    "水": ["蛙", "鱼", "鲤", "鳗", "鲨", "鲸", "獭", "龟", "蟹", "虾", "贝", "鸭", "母", "鳐", "豚", "螺"],
    "草": ["鼠", "苗", "花", "藤", "菇", "果", "鹿", "羊", "蜥", "龟", "猴", "蛇", "兔", "蛙"],
    "电": ["鼠", "鸟", "犬", "羊", "鳗", "蛛", "蜂", "狼", "豹", "猫", "蛾", "鼬"],
    "冰": ["熊", "狐", "鸟", "鹅", "豹", "鹿", "狼", "鲸", "鸮", "兔", "蛾"],
    "格斗": ["猿", "熊", "虎", "牛", "犀", "螳", "蟹", "鹤", "猴", "蛙", "袋鼠"],
    "毒": ["蛇", "蛛", "蝎", "蛙", "菇", "蛾", "蜂", "蜈", "母", "鼠", "蜥", "鳗"],
    "大地": ["鼹", "鼠", "驼", "犀", "象", "蜥", "鳄", "龟", "猪", "穿山甲", "牛"],
    "飞行": ["鹰", "雀", "燕", "隼", "鸮", "鹤", "鸦", "蝠", "鹏", "鸟", "鸽", "蜓"],
    "灵能": ["猫", "狐", "鹿", "鸮", "偶", "晶", "蝶", "狸", "兔", "象", "猴"],
    "虫": ["蝶", "蛾", "蜂", "蚁", "甲", "螳", "蛛", "蚕", "萤", "蜓", "蝉", "蟋", "蜗"],
    "岩石": ["龟", "蟹", "犀", "晶", "石像", "偶", "蜥", "甲", "螺", "菊石"],
    "幽灵": ["灵", "魂", "影", "偶", "灯", "猫", "鸦", "蝠", "狐", "面", "蛇"],
    "龙": ["龙", "蜥", "蛟", "鳄", "鲨", "蛇", "鹰"],
    "恶": ["狼", "鸦", "猫", "狐", "狸", "鼬", "鬣", "蝠", "豺", "蛇"],
    "钢": ["甲", "蟹", "偶", "鹰", "犀", "狼", "锹", "蛇", "钟", "犰狳"],
    "妖精": ["兔", "蝶", "羊", "灵", "花", "狐", "猫", "鹿", "精", "铃"],
}
# 形体名 -> 动态模型的身体结构
BODY = {}
for k, ns in {
    "四足": "鼠兔犬猫猪牛羊猴熊獾狸貂鹿狐狼驹狮蜥豹虎龟獭犀象驼鳄鼹穿山甲鬣豺犰狳鼬袋鼠",
    "鸟形": "雀鸽鸭鹅鸟鹰燕隼鸮鹤鸦鹏",
    "鱼形": "鱼鲤鲨鲸鳐豚",
    "蛇形": "蛇鳗蛟龙",
    "虫形": "蛾蜂蚁甲螳蛛蚕萤蜓蝉蟋蜗蝎蜈锹",
    "蝶形": "蝶",
    "两栖": "蛙",
    "甲壳": "蟹虾贝螺菊石",
    "浮游": "母灵魂影灯面精铃晶",
    "植物": "苗花藤菇果",
    "人形": "猿偶石像钟",
    "飞膜": "蝠",
}.items():
    i = 0
    while i < len(ns):
        for w in ("穿山甲", "犰狳", "袋鼠", "石像", "菊石"):
            if ns.startswith(w, i):
                BODY[w] = k
                i += len(w)
                break
        else:
            BODY[ns[i]] = k
            i += 1
IDLE = {
    "四足": "呼吸起伏，尾巴左右摆动，偶尔竖耳", "鸟形": "原地轻跳，翅膀半张扇动", "鱼形": "身体波浪摆动，鳍片拍打",
    "蛇形": "身体 S 形缓慢游动，吐信", "虫形": "触角抖动，脚轮流踏步", "蝶形": "翅膀开合，上下漂浮",
    "两栖": "鼓腮，身体一蹲一起", "甲壳": "钳子开合，眼柄转动", "浮游": "上下漂浮，周身光晕闪烁",
    "植物": "叶片随风摇摆，花瓣开合", "人形": "重心左右换脚，手臂摆动", "飞膜": "倒挂摇晃，翼膜张合",
    "龙形": "长颈起伏，尾巴拍地，鼻孔冒烟",
}

# ---------------------------------------------------------------- 招式
PHYS = ["撞击", "拳", "爪", "牙", "踢", "尾击", "刃", "冲锋", "突击", "重锤"]
SPEC = ["弹", "波", "光线", "风暴", "炮", "漩涡", "吐息", "之歌", "冲击", "球"]
STATUS_MOVES = {
    "普通": [("叫声", "降低对手攻击 1 级"), ("变圆", "提高自己防御 1 级"), ("睡觉", "睡 2 回合并回满 HP")],
    "火": [("鬼火", "让对手灼伤"), ("大晴天", "5 回合晴天，火属性招式威力提升")],
    "水": [("求雨", "5 回合下雨，水属性招式威力提升"), ("水之环", "每回合回复 1/16 HP")],
    "草": [("寄生种子", "每回合吸取对手 1/8 HP"), ("催眠粉", "让对手睡着")],
    "电": [("电磁波", "让对手麻痹"), ("充电", "下一招电属性威力翻倍，特防提高 1 级")],
    "冰": [("白雾", "5 回合内能力不会被降低"), ("冰雹", "5 回合冰雹，每回合伤害非冰属性")],
    "格斗": [("健美", "提高攻击和防御各 1 级"), ("看穿", "本回合不受攻击")],
    "毒": [("剧毒", "让对手中剧毒"), ("溶化", "提高自己防御 2 级")],
    "大地": [("撒沙", "降低对手命中 1 级"), ("沙暴", "5 回合沙暴")],
    "飞行": [("顺风", "4 回合内己方速度翻倍"), ("羽栖", "回复一半 HP")],
    "灵能": [("冥想", "提高特攻和特防各 1 级"), ("催眠术", "让对手睡着")],
    "虫": [("吐丝", "降低对手速度 2 级"), ("蝶舞", "提高特攻、特防、速度各 1 级")],
    "岩石": [("隐形岩", "对手换上场时受到岩石伤害"), ("岩石打磨", "提高速度 2 级")],
    "幽灵": [("奇异之光", "让对手混乱"), ("诅咒", "每回合扣对手 1/4 HP")],
    "龙": [("龙之舞", "提高攻击和速度各 1 级")],
    "恶": [("挑衅", "3 回合内对手只能用攻击招式"), ("诡计", "提高特攻 2 级")],
    "钢": [("铁壁", "提高防御 2 级"), ("金属音", "降低对手特防 2 级")],
    "妖精": [("撒娇", "降低对手攻击 2 级"), ("月光", "回复一半 HP")],
}
SECONDARY = {
    "火": "10% 灼伤", "水": "", "草": "吸取伤害的一半", "电": "10% 麻痹", "冰": "10% 冰冻", "格斗": "",
    "毒": "30% 中毒", "大地": "", "飞行": "", "灵能": "10% 降低特防", "虫": "", "岩石": "30% 畏缩",
    "幽灵": "20% 降低特防", "龙": "", "恶": "20% 畏缩", "钢": "10% 提高防御", "妖精": "30% 降低特攻", "普通": "",
}
# 已有的招式名保留
LEGACY_MOVES = {
    "撞击": ("普通", "物理", 40), "啄": ("飞行", "物理", 35), "咬住": ("恶", "物理", 60),
    "疾风翼": ("飞行", "物理", 60), "火花": ("火", "特殊", 40), "火焰轮": ("火", "物理", 65),
    "烈焰冲撞": ("火", "物理", 90), "水枪": ("水", "特殊", 40), "泡沫光线": ("水", "特殊", 65),
    "激流炮": ("水", "特殊", 90), "吸取": ("草", "特殊", 30), "飞叶": ("草", "物理", 45),
    "飞叶快刀": ("草", "物理", 60), "叶刃风暴": ("草", "特殊", 90), "电击": ("电", "特殊", 40),
    "雷电球": ("电", "特殊", 65),
}


def build_moves():
    moves = {}
    for name, (t, cat, p) in LEGACY_MOVES.items():
        moves[name] = {"type": t, "category": cat, "power": p, "accuracy": 100, "pp": 25 if p < 60 else 15,
                       "effect": SECONDARY.get(t, "") if cat == "特殊" else ""}
    powers = [35, 50, 65, 80, 95, 120]
    for t in TYPES:
        m = MORPH[t]
        for cat, acts in (("物理", PHYS), ("特殊", SPEC)):
            acts = acts[:]
            rng.shuffle(acts)
            for i, p in enumerate(powers):
                tier = m[min(2, i // 2)]
                for _ in range(40):
                    name = rng.choice(tier) + acts[i % len(acts)]
                    if name not in moves:
                        break
                    acts[i % len(acts)] = rng.choice(PHYS if cat == "物理" else SPEC)
                eff = SECONDARY[t] if p < 100 and rng.random() < 0.6 else ""
                if p >= 120:
                    eff = "使用后下回合不能行动" if cat == "特殊" else "自己受到 1/3 反伤"
                moves[name] = {"type": t, "category": cat, "power": p,
                               "accuracy": 100 if p <= 80 else (90 if p < 120 else 85),
                               "pp": 30 if p <= 50 else (15 if p <= 95 else 5), "effect": eff}
        for name, eff in STATUS_MOVES[t]:
            moves[name] = {"type": t, "category": "变化", "power": 0, "accuracy": 100, "pp": 15, "effect": eff}
    return moves


# ---------------------------------------------------------------- 特性
GENERIC_ABILITIES = [
    ("坚韧", "满 HP 时不会被一招打倒"), ("威吓", "出场时降低对手攻击 1 级"), ("加速", "每回合结束速度提高 1 级"),
    ("再生", "换下场时回复 1/3 HP"), ("适应力", "本系加成从 1.5 倍变为 2 倍"), ("巧手", "威力 60 以下的招式威力提升 50%"),
    ("厚脂肪", "受到火和冰属性招式伤害减半"), ("逃脱", "野外战斗一定能逃走"), ("夜行", "夜晚时速度提高 50%"),
    ("慢热", "出场后 5 回合内攻击和速度减半"), ("鲁莽", "有反伤的招式威力提升 20%"), ("激励", "被击中要害后攻击提高到最大"),
    ("毅力", "异常状态时攻击提升 50%"), ("锐目", "命中率不会被降低"), ("精神力", "不会畏缩"),
    ("贪吃", "HP 低于一半就吃掉携带的果实"), ("拾荒", "战斗后有 10% 几率捡到道具"), ("天然", "无视对手的能力变化"),
    ("免疫", "不会中毒"), ("不眠", "不会睡着"), ("柔软", "不会麻痹"), ("熔点", "不会冰冻"), ("迟钝", "不会着迷和被挑衅"),
    ("瞬发", "每场战斗第一招优先出手"), ("硬壳", "不会被击中要害"), ("强运", "容易击中要害"), ("怒火", "被击中后攻击提高 1 级"),
    ("好奇心", "遇到没见过的幻兽时速度提高 1 级"), ("磁力", "让钢属性的对手无法逃走"), ("光合", "晴天时速度翻倍"),
    ("游泳", "下雨时速度翻倍"), ("挖沙", "沙暴时速度翻倍"), ("滑雪", "冰雹时速度翻倍"), ("伪装", "第一次受到的攻击伤害变为 0"),
    ("多重鳞", "满 HP 时受到的伤害减半"), ("压迫感", "对手招式的 PP 多消耗 1 点"), ("同步", "让对手也陷入自己的异常状态"),
    ("连续攻击", "连续招式一定打满次数"), ("唱反调", "能力变化反过来"), ("轻装", "失去道具后速度翻倍"),
]
TYPE_ABILITY_FORMS = [
    ("{a}之心", "HP 低于 1/3 时，{t}属性招式威力提升 50%"),
    ("{a}吸收", "受到{t}属性招式时不受伤害，回复 1/4 HP"),
    ("{a}之息", "接触到自己的对手有 30% 几率{s}"),
    ("{a}领域", "出场后 5 回合内，场上{t}属性招式威力提升 30%"),
    ("{a}之铠", "受到效果拔群的招式时伤害减少 25%"),
]
STATUS_OF = {"火": "灼伤", "电": "麻痹", "毒": "中毒", "冰": "冰冻", "草": "睡着", "灵能": "混乱", "幽灵": "混乱",
             "妖精": "着迷", "恶": "畏缩", "水": "降低速度", "格斗": "降低防御", "大地": "降低命中", "飞行": "降低命中",
             "虫": "降低速度", "岩石": "受到 1/8 伤害", "龙": "降低攻击", "钢": "受到 1/8 伤害", "普通": "降低攻击"}


def build_abilities():
    abil = {n: {"type": "", "effect": e} for n, e in GENERIC_ABILITIES}
    by_type = {}
    for t in TYPES:
        by_type[t] = []
        heads = MORPH[t][0] + MORPH[t][1]
        for i, (form, eff) in enumerate(TYPE_ABILITY_FORMS):
            for _ in range(20):
                name = form.format(a=rng.choice(heads))
                if name not in abil:
                    break
            abil[name] = {"type": t, "effect": eff.format(t=t, s=STATUS_OF[t])}
            by_type[t].append(name)
    return abil, by_type


# ---------------------------------------------------------------- 种族值
ARCHETYPES = {
    "物攻手": [1.0, 1.35, 0.95, 0.7, 0.85, 1.1], "特攻手": [0.95, 0.7, 0.85, 1.35, 1.0, 1.1],
    "物理速攻": [0.85, 1.25, 0.75, 0.8, 0.8, 1.5], "特殊速攻": [0.85, 0.8, 0.75, 1.25, 0.85, 1.5],
    "物盾": [1.0, 0.9, 1.5, 0.75, 1.0, 0.7], "特盾": [1.05, 0.75, 0.9, 0.95, 1.45, 0.8],
    "肉盾": [1.6, 0.95, 0.95, 0.8, 1.0, 0.6], "均衡": [1, 1, 1, 1, 1, 1],
}
TYPE_ARCH = {
    "普通": ["均衡", "肉盾", "物攻手", "物理速攻"], "火": ["特攻手", "物攻手", "特殊速攻"], "水": ["特攻手", "肉盾", "均衡", "特盾"],
    "草": ["特攻手", "特盾", "均衡", "物攻手"], "电": ["特殊速攻", "物理速攻", "特攻手"], "冰": ["特攻手", "肉盾", "物攻手"],
    "格斗": ["物攻手", "物理速攻", "肉盾"], "毒": ["特盾", "物盾", "特攻手"], "大地": ["物攻手", "物盾", "肉盾"],
    "飞行": ["物理速攻", "特殊速攻", "物攻手"], "灵能": ["特攻手", "特殊速攻", "特盾"], "虫": ["物理速攻", "物盾", "特殊速攻"],
    "岩石": ["物盾", "物攻手"], "幽灵": ["特攻手", "特殊速攻", "特盾"], "龙": ["物攻手", "特攻手", "均衡"],
    "恶": ["物理速攻", "物攻手", "特殊速攻"], "钢": ["物盾", "物攻手", "特盾"], "妖精": ["特盾", "特攻手", "均衡"],
}


def make_stats(bst, arch, noise=0.12):
    w = [x * rng.uniform(1 - noise, 1 + noise) for x in ARCHETYPES[arch]]
    s = sum(w)
    vals = [max(15, round(bst * x / s)) for x in w]
    vals[0] += bst - sum(vals)
    return dict(zip(STATS, vals))


def scale_stats(prev, bst):
    s = sum(prev.values())
    vals = {k: max(15, round(v * bst / s * rng.uniform(0.95, 1.05))) for k, v in prev.items()}
    vals["hp"] += bst - sum(vals.values())
    return vals


# ---------------------------------------------------------------- 区域与刷新地点
REGION_IDS = [r["id"] for r in wp.REGIONS]
REGION = {r["id"]: r for r in wp.REGIONS}
TOWN_REGION = {t["id"]: t["region"] for t in wp.TOWNS}
TOWN_NAME = {t["id"]: t["name"] for t in wp.TOWNS}
# 每个区域偏爱的属性（权重）
AFFINITY = {
    "cuiyuan": {"普通": 5, "草": 3, "虫": 3, "飞行": 3, "电": 2, "妖精": 2, "水": 1, "火": 1, "格斗": 1},
    "shencui": {"草": 5, "虫": 5, "妖精": 2, "毒": 2, "恶": 2, "幽灵": 1, "普通": 2, "飞行": 1},
    "wuzhao": {"毒": 5, "水": 3, "虫": 3, "幽灵": 3, "恶": 2, "大地": 2, "草": 1},
    "weilan": {"水": 6, "飞行": 3, "岩石": 2, "冰": 1, "钢": 1, "电": 1, "普通": 1},
    "jinsha": {"大地": 5, "岩石": 3, "火": 2, "龙": 1, "恶": 2, "钢": 1, "虫": 1, "毒": 1},
    "chiyan": {"火": 6, "岩石": 3, "龙": 1, "大地": 2, "格斗": 2, "钢": 1},
    "cangyan": {"岩石": 4, "格斗": 4, "钢": 3, "飞行": 2, "大地": 2, "龙": 1, "冰": 1},
    "bijing": {"水": 4, "灵能": 4, "妖精": 3, "龙": 1, "飞行": 2, "草": 1},
    "shuangling": {"冰": 6, "钢": 2, "幽灵": 2, "灵能": 2, "龙": 1, "水": 1},
}


TOWN_POS = {t["id"]: t["pos"] for t in wp.TOWNS}


def _route_region(a, b):
    """道路中点离哪个区域中心最近，就算哪个区域的道路"""
    mx = (TOWN_POS[a][0] + TOWN_POS[b][0]) / 2
    my = (TOWN_POS[a][1] + TOWN_POS[b][1]) / 2
    return min(wp.REGIONS, key=lambda r: (r["center"][0] - mx) ** 2 + (r["center"][1] - my) ** 2)["id"]


ROUTE_REGION = {f"{n}号道路": _route_region(a, b) for n, a, b in wp.ROUTES}


def routes_of(region):
    """区域里能刷野生幻兽的地方：属于它的道路，加上区域里道路以外的野外"""
    return [k for k, r in ROUTE_REGION.items() if r == region] + [REGION[region]["name"] + "野外"]


PLACES_OF = {r: [p for p in wp.PLACES if p["region"] == r] for r in REGION_IDS}
WATER_REGIONS = {"cuiyuan", "shencui", "wuzhao", "weilan", "bijing", "cangyan", "shuangling"}


def pick_methods(types):
    t = types[0]
    if t == "水" or (len(types) > 1 and types[1] == "水" and rng.random() < 0.5):
        return rng.choice([["冲浪"], ["钓鱼"], ["冲浪", "钓鱼"], ["草丛", "冲浪"]])
    if t in ("岩石", "钢", "大地") and rng.random() < 0.5:
        return ["洞窟"]
    if t == "幽灵" or (t == "恶" and rng.random() < 0.5):
        return rng.choice([["夜晚草丛"], ["洞窟"], ["夜晚草丛", "洞窟"]])
    return ["草丛"]


# ---------------------------------------------------------------- 物种
class Namer:
    def __init__(self):
        self.used = set()

    def take(self, cands):
        for c in cands:
            if c not in self.used and 2 <= len(c) <= 5:
                self.used.add(c)
                return c
        for _ in range(200):
            c = rng.choice(cands) + rng.choice("儿仔子灵兽")
            if c not in self.used:
                self.used.add(c)
                return c
        raise RuntimeError("起名失败")

    def line(self, types, noun, stages, crown=False):
        t1 = types[0]
        t2 = types[1] if len(types) > 1 else t1
        m1, m2 = MORPH[t1], MORPH[t2]
        names = []
        if stages == 1:
            tiers = [1]
        elif stages == 2:
            tiers = [0, 2]
        else:
            tiers = [0, 1, 2]
        for i, tier in enumerate(tiers):
            cands = []
            for _ in range(30):
                a = rng.choice(m1[tier])
                b = rng.choice(m2[tier])
                if len(a + b + noun) > 4:
                    b = a
                forms = [a + noun]
                if tier == 0:
                    forms += [a + a + noun if len(a) == 1 else a + noun, "小" + a + noun]
                else:
                    forms += [a + b + noun if a != b else a + noun]
                if tier == 2 and (crown or rng.random() < 0.25):
                    forms.insert(0, a + noun + rng.choice(["王", "皇", "尊", "君"]))
                cands += forms
            rng.shuffle(cands)
            names.append(self.take(cands))
        return names


def bst_plan(stages, kind="normal"):
    if kind == "pseudo":
        return [300, 420, 600]
    if stages == 3:
        b0 = rng.randrange(290, 330, 5)
        return [b0, b0 + rng.randrange(95, 125, 5), rng.randrange(495, 540, 5)]
    if stages == 2:
        b0 = rng.randrange(290, 360, 5)
        return [b0, rng.randrange(450, 510, 5)]
    return [rng.randrange(330, 500, 5)]


def learnset(types, moves, by_type, stage_count):
    """一条进化线共用的升级招式表：[[等级, 招式名], ...]"""
    def pool(t, cat=None):
        return sorted([n for n, m in moves.items() if m["type"] == t and m["power"] > 0 and (cat is None or m["category"] == cat)],
                      key=lambda n: moves[n]["power"])
    t1 = types[0]
    main = pool(t1)
    sec = pool(types[1]) if len(types) > 1 else []
    normal = pool("普通")
    status = [n for n, m in moves.items() if m["type"] in types and m["category"] == "变化"]
    ls = [[1, rng.choice(normal[:3])], [1, rng.choice(STATUS_MOVES["普通"])[0]]]
    lvls = [5, 9, 14, 19, 25, 31, 38, 45, 53, 62]
    picks = []
    for i, lv in enumerate(lvls):
        if i in (2, 6) and status:
            picks.append([lv, rng.choice(status)])
        elif sec and i in (4, 8):
            picks.append([lv, sec[min(len(sec) - 1, i // 2)]])
        else:
            k = min(len(main) - 1, int(i / len(lvls) * len(main) + 0.5))
            picks.append([lv, main[k]])
    out, seen = [], set()
    for lv, n in ls + picks:
        if n not in seen:
            seen.add(n)
            out.append([lv, n])
    return out


def main():
    moves = build_moves()
    abil, abil_by_type = build_abilities()
    generic = [n for n, _ in GENERIC_ABILITIES]
    namer = Namer()
    for n in ["焰尾狐", "烈焰狐", "泡泡蛙", "巨浪蛙", "叶芽鼠", "森叶鼠", "圆滚鸟", "疾风鸟", "绒绒虫", "茧茧", "彩翼蝶",
              "炭炭", "浮浮母", "电栗"]:
        namer.used.add(n)

    lines = []  # 每条进化线：{types, noun, names, keys, stages, kind, region, arch}

    def add_line(types, noun, names, kind="normal", region=None, keys=None, evo=None, arch=None, bst=None):
        lines.append({"types": types, "noun": noun, "names": names, "kind": kind, "region": region,
                      "keys": keys, "evo": evo, "arch": arch, "bst": bst})

    # 已有的幻兽（保留名字和代号），补齐第三段
    third = namer.take(["炽阳九尾", "炽焰狐王"])
    add_line(["火"], "狐", ["焰尾狐", "烈焰狐", third], "starter", "cuiyuan", ["huohu", "huohu2", None], [16, 36], "特攻手")
    third = namer.take(["怒涛蛙皇", "海啸蛙王"])
    add_line(["水"], "蛙", ["泡泡蛙", "巨浪蛙", third], "starter", "cuiyuan", ["paowa", "paowa2", None], [16, 36], "肉盾")
    third = namer.take(["古木鼠王", "森罗鼠王"])
    add_line(["草"], "鼠", ["叶芽鼠", "森叶鼠", third], "starter", "cuiyuan", ["yeshu", "yeshu2", None], [16, 36], "物攻手")
    third = namer.take(["苍穹鹏", "凌霄鹏"])
    add_line(["普通", "飞行"], "鸟", ["圆滚鸟", "疾风鸟", third], "normal", "cuiyuan", ["yuanniao", "yuanniao2", None], [14, 34], "物理速攻")
    add_line(["虫", "飞行"], "蝶", ["绒绒虫", "茧茧", "彩翼蝶"], "normal", "cuiyuan", ["chongchong", "jianjian", "caidie"], [7, 10], "特殊速攻",
             [195, 205, 395])
    add_line(["火"], "炭", ["炭炭", namer.take(["炎炭魔", "熔炭魔"])], "normal", "chiyan", ["tantan", None], [30], "物盾")
    add_line(["水", "毒"], "母", ["浮浮母", namer.take(["深海母", "沧溟母"])], "normal", "weilan", ["fufu", None], [28], "特盾")
    add_line(["电"], "栗", ["电栗", namer.take(["雷栗", "霆栗"])], "normal", "cuiyuan", ["dianli", None], [22], "物理速攻")

    # 准神：每条三段，600 总和
    pseudo = [(["龙", "大地"], "鳄", "jinsha"), (["龙", "飞行"], "蛟", "cangyan"), (["岩石", "恶"], "蜥", "chiyan"),
              (["钢", "灵能"], "偶", "shuangling"), (["龙", "水"], "蛇", "bijing"), (["冰", "龙"], "龙", "shuangling")]
    for types, noun, region in pseudo:
        add_line(types, noun, namer.line(types, noun, 3, crown=True), "pseudo", region, evo=[rng.choice([30, 32, 35]), rng.choice([50, 55])])

    # 传说与幻之幻兽（手工命名），放在地标与迷宫
    legends = [
        ("千年神木", "森灵守护·苍古", ["草", "妖精"], 600), ("火山口", "炎帝·焚天", ["火", "龙"], 680),
        ("云巅", "风神·凌霄", ["飞行", "电"], 600), ("湖心岛", "镜湖之主·澈", ["水", "灵能"], 600),
        ("沉没神殿", "沼王·墨渊", ["毒", "幽灵"], 580), ("流沙遗迹", "沙之古王·塔鲁", ["大地", "钢"], 600),
        ("冰晶洞", "冰后·霜晶", ["冰", "妖精"], 600), ("回声矿洞", "岩心巨像", ["岩石", "格斗"], 580),
        ("海蚀洞", "潮音海龙", ["水", "龙"], 600), ("白帆灯塔", "引路灯鸟", ["电", "飞行"], 580),
        ("冠军之路", "试炼之狮·王冠", ["格斗", "钢"], 600), ("迷雾林海", "雾隐九尾", ["幽灵", "灵能"], 600),
        ("冠军之路", "奈尔斯始祖·源", ["龙", "灵能"], 720), ("湖心岛", "幻·星屑", ["妖精", "灵能"], 600),
        ("千年神木", "幻·芽之子", ["草", "普通"], 600), ("流沙遗迹", "幻·时之沙", ["大地", "灵能"], 600),
    ]
    for place, name, types, bst in legends:
        namer.used.add(name)
        pl = next(p for p in wp.PLACES if p["name"] == place)
        add_line(types, "龙" if "龙" in types else rng.choice(NOUNS[types[0]]), [name], "legend", pl["region"],
                 bst=[bst], arch=rng.choice(TYPE_ARCH[types[0]]))
        lines[-1]["place"] = place

    # 剩下的按区域偏好批量生成：三段、两段、单段
    count = sum(len(l["names"]) for l in lines)
    remain = TOTAL - count
    plan = []
    n3 = 108
    n2 = 132
    n1 = remain - n3 * 3 - n2 * 2
    plan = [3] * n3 + [2] * n2 + [1] * n1
    rng.shuffle(plan)
    # 区域配额：前期区域多放三段线（玩家更早接触），后期多单段和两段
    region_cycle = REGION_IDS[:]
    for i, stages in enumerate(plan):
        if stages == 3:
            region = rng.choices(REGION_IDS, weights=[10, 9, 8, 7, 6, 5, 4, 3, 3])[0]
        else:
            region = region_cycle[i % len(region_cycle)]
        aff = AFFINITY[region]
        t1 = rng.choices(list(aff), weights=list(aff.values()))[0]
        types = [t1]
        if rng.random() < 0.45:
            t2 = rng.choices(list(aff), weights=list(aff.values()))[0]
            if t2 == t1 or rng.random() < 0.35:
                t2 = rng.choice([t for t in TYPES if t != t1 and t != "龙"])
            types.append(t2)
        noun = rng.choice(NOUNS[t1] if rng.random() < 0.8 or len(types) == 1 else NOUNS[types[1]])
        add_line(types, noun, namer.line(types, noun, stages), "normal", region)

    # ---------------------------------------------------------------- 展开成物种
    species = []
    spawns = {}  # 地点 -> [条目]
    dex = 0

    def spawn(loc, region, entry):
        spawns.setdefault(loc, {"region": REGION[region]["name"], "list": []})["list"].append(entry)

    for li, line in enumerate(lines):
        stages = len(line["names"])
        types = line["types"]
        region = line["region"]
        lv_lo, lv_hi = REGION[region]["levels"]
        arch = line["arch"] or rng.choice(TYPE_ARCH[types[0]])
        bsts = line["bst"] or bst_plan(stages, "pseudo" if line["kind"] == "pseudo" else "normal")
        # 进化等级：第一次在区域等级之后几级，第二次再往后
        evo = line["evo"]
        if evo is None and stages > 1:
            e1 = max(lv_lo + rng.randint(5, 12), 12)
            evo = [e1] if stages == 2 else [e1, max(e1 + rng.randint(14, 22), 30)]
        methods_evo = []
        for i in range(stages - 1):
            r = rng.random()
            if line["kind"] in ("starter", "pseudo") or r < 0.82:
                methods_evo.append({"method": "等级", "level": evo[i]})
            elif r < 0.92:
                stone = {"火": "火之石", "水": "水之石", "草": "叶之石", "电": "雷之石", "冰": "冰之石", "妖精": "月之石",
                         "幽灵": "暗之石", "恶": "暗之石", "灵能": "日之石"}.get(types[0], "觉醒石")
                methods_evo.append({"method": "道具", "item": stone})
            elif r < 0.97:
                methods_evo.append({"method": "亲密度", "note": "亲密度高时升级"})
            else:
                methods_evo.append({"method": "地点", "note": f"在{REGION[region]['name']}升级", "level": evo[i]})
        abil_pool = abil_by_type[types[0]] + (abil_by_type[types[1]] if len(types) > 1 else [])
        abilities = rng.sample(abil_pool, 1) + rng.sample(generic, 1)
        if line["kind"] == "starter":
            abilities[0] = abil_by_type[types[0]][0]  # 初始幻兽固定是“X之心”
        hidden = rng.choice([a for a in generic + abil_pool if a not in abilities])
        ls = learnset(types, moves, abil_by_type, stages)
        stats = None
        keys = []
        body = BODY.get(line["noun"], "四足")
        if types[0] == "龙" or line["noun"] in ("龙", "蛟") and body == "蛇形" and line["kind"] in ("pseudo", "legend"):
            body = "龙形" if line["noun"] not in ("鲨", "鹰", "蛇") else body
        for s in range(stages):
            dex += 1
            key = (line["keys"][s] if line["keys"] and line["keys"][s] else f"d{dex:03d}")
            keys.append(key)
            stats = make_stats(bsts[s], arch) if stats is None else scale_stats(stats, bsts[s])
            size = ["小", "中", "大", "巨"][min(3, s + (1 if line["kind"] == "legend" else 0) + (1 if stages == 1 and line["kind"] == "normal" and bsts[0] > 440 else 0))]
            sp = {
                "dex": dex, "key": key, "name": line["names"][s], "types": types, "stage": s + 1, "stages": stages,
                "line": li + 1, "kind": line["kind"], "category": {"starter": "初始", "pseudo": "准传说", "legend": "传说" if not line["names"][s].startswith("幻·") else "幻"}.get(line["kind"], "普通"),
                "base": stats, "bst": sum(stats.values()), "abilities": abilities, "hidden_ability": hidden,
                "catch_rate": 3 if line["kind"] == "legend" else [190, 90, 45][min(2, s if stages > 1 else (1 if bsts[0] > 420 else 0))],
                "xp": round(sum(stats.values()) * (0.2 + 0.07 * s)),
                "evolves_from": keys[s - 1] if s > 0 else None,
                "evolution": None,
                "learnset": ls if s == 0 else ls + [[evo[s - 1] if s - 1 < len(evo) else 1, rng.choice([n for n, m in moves.items() if m["type"] == types[-1] and m["power"] >= 80])]],
                "model": {"body": body, "size": size, "idle": IDLE[body],
                          "colors": [TYPE_COLOR[t] for t in types], "frames": 4},
                "home": REGION[region]["name"],
            }
            species.append(sp)
        for s in range(stages - 1):
            species[-stages + s]["evolution"] = dict(to=keys[s + 1], **methods_evo[s])

        # 刷新地点
        base = species[-stages]
        if line["kind"] == "legend":
            spawn(line["place"], region, {"key": base["key"], "name": base["name"], "levels": [max(50, lv_hi), max(50, lv_hi)],
                                         "method": "固定", "rarity": "唯一"})
            base["spawns"] = [line["place"]]
            continue
        if line["kind"] == "starter":
            base["spawns"] = ["晨露镇（研究员赠送）"]
            continue
        locs = []
        methods = pick_methods(types)
        routes = routes_of(region)
        places = PLACES_OF[region]
        rarity = "稀有" if line["kind"] == "pseudo" else rng.choices(["常见", "一般", "少见", "稀有"], weights=[4, 4, 2, 1])[0]
        if line["keys"]:
            rarity = "常见"  # 游戏里已有的几只，早期就能遇到
        hi = min(lv_hi, (evo[0] - 1) if evo else lv_hi)
        if hi < lv_lo + 3:
            hi = lv_hi  # 进化等级比区域还低的（准传说、早期就定好的线），野生的还没进化
        lo = rng.randint(lv_lo, max(lv_lo, hi - 4))
        for m in methods:
            if m in ("冲浪", "钓鱼") and region not in WATER_REGIONS:
                m = "草丛"
            if m == "洞窟":
                cands = [p["name"] for p in places if p["kind"] == "dungeon"] or routes
                where = rng.sample(cands, min(len(cands), rng.randint(1, 2)))
            else:
                where = rng.sample(routes, min(len(routes), rng.randint(1, 3)))
            for w in where:
                spawn(w, region, {"key": base["key"], "name": base["name"], "levels": [lo, min(hi, lo + rng.randint(2, 5))],
                                  "method": m, "rarity": rarity})
                locs.append(f"{w}（{m}）")
        base["spawns"] = locs
        # 中段在后面的区域也会野生出现
        if stages > 1 and rng.random() < 0.45:
            later = [r for r in REGION_IDS if REGION[r]["levels"][0] >= evo[0] and r != region]
            if later:
                r2 = rng.choice(later)
                mid = species[-stages + 1]
                w = rng.choice(routes_of(r2))
                l2 = REGION[r2]["levels"]
                spawn(w, r2, {"key": mid["key"], "name": mid["name"], "levels": [l2[0], min(l2[1], l2[0] + 6)],
                              "method": methods[0] if methods[0] != "洞窟" else "草丛", "rarity": "少见"})
                mid["spawns"] = [f"{w}（{methods[0]}）"]

    assert len(species) == TOTAL, len(species)
    assert len({s["name"] for s in species}) == TOTAL

    os.makedirs(OUT, exist_ok=True)
    chart = {a: {d: CHART[a].get(d, 1) for d in TYPES} for a in TYPES}

    def dump(name, obj):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)

    dump("types.json", {"types": TYPES, "colors": TYPE_COLOR, "chart": chart, "stats": STAT_NAMES})
    dump("moves.json", moves)
    dump("abilities.json", abil)
    dump("species.json", species)
    dump("spawns.json", spawns)
    write_md(species, moves, abil, spawns)
    print(f"{len(species)} 只幻兽，{len(lines)} 条进化线，{len(moves)} 个招式，{len(abil)} 个特性，{len(spawns)} 个刷新地点")


def write_md(species, moves, abil, spawns):
    from collections import Counter
    by_type = Counter(t for s in species for t in s["types"])
    by_cat = Counter(s["category"] for s in species)
    by_home = Counter(s["home"] for s in species)
    lines3 = Counter((s["line"], s["stages"]) for s in species)
    st = Counter(v for (_, v) in lines3)
    out = ["# 幻兽规划", "",
           f"由 `tools/dex_plan.py` 生成：{len(species)} 只幻兽、{len(lines3)} 条进化线（三段 {st[3]}、两段 {st[2]}、单段 {st[1]}），"
           f"{len(moves)} 个招式、{len(abil)} 个特性、{len(spawns)} 个刷新地点。数据在 `data/dex/`。", "",
           "## 系统", "",
           "- 18 种属性：" + "、".join(TYPES) + "。克制表见 `data/dex/types.json`。",
           "- 六项种族值：体力、攻击、防御、特攻、特防、速度。招式分物理、特殊、变化三类，物理用攻击/防御，特殊用特攻/特防。",
           "- 每只幻兽有两个普通特性中的一个，外加一个隐藏特性。",
           "- 种族值总和：三段线约 300 → 420 → 520，两段线约 320 → 480，准传说 600，传说 580–720。", "",
           "## 分类", ""]
    out += [f"- {k}：{v} 只" for k, v in by_cat.most_common()]
    out += ["", "## 各属性数量（双属性两边都算）", "", "| 属性 | 数量 |", "| --- | --- |"]
    out += [f"| {t} | {by_type[t]} |" for t in TYPES]
    out += ["", "## 各区域的原生幻兽", "", "| 区域 | 数量 |", "| --- | --- |"]
    out += [f"| {r['name']} | {by_home[r['name']]} |" for r in wp.REGIONS]
    out += ["", "## 刷新地点", ""]
    for loc, info in sorted(spawns.items(), key=lambda kv: (REGION_IDS.index(next(r['id'] for r in wp.REGIONS if r['name'] == kv[1]['region'])), kv[0])):
        lst = "、".join(f"{e['name']}（{e['method']} Lv{e['levels'][0]}–{e['levels'][1]} {e['rarity']}）" for e in info["list"])
        out.append(f"- **{loc}**（{info['region']}）：{lst}")
    with open(os.path.join(ROOT, "docs", "dex-plan.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
