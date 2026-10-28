"""奈尔斯地区的世界规划：区域、城镇、道路、迷宫和地标。这是唯一的数据源。

python3 tools/world_plan.py 生成：
- scripts/world/world_plan.gd   游戏读取的常量（区域中心、城镇、道路、地点）
- docs/world-plan.md            给人看的规划文档
坐标单位是格子，(0,0) 在左上角。下面的数据按 10000x10000 的草图坐标填写，
输出时整体乘以 SCALE，得到实际地图 14080x14080（880x880 个 16 格区块）。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGION_NAME = "奈尔斯地区"
SIZE = 14080
SCALE = SIZE / 10000
START_HALF = (24, 18)  # 起始小镇手工布局 48x36 的一半


def sc(p):
    return (round(p[0] * SCALE), round(p[1] * SCALE))

# biome 取值与 scripts/world/world_gen.gd 的 Biome 枚举一致
BIOMES = ["草原", "森林", "沼泽", "海岸", "沙漠", "火山", "山地", "湖区", "雪原"]

REGIONS = [
    {"id": "cuiyuan", "name": "翠原", "biome": "草原", "center": (5000, 5000), "levels": (2, 14),
     "desc": "起点所在的温和草原，丘陵起伏、溪流交错，零星的风车和花田。适合新人训练师。"},
    {"id": "shencui", "name": "深翠森林", "biome": "森林", "center": (2200, 5000), "levels": (12, 20),
     "desc": "西部的原始森林，树冠遮天，林间有蘑菇圈、倒木和林中空地，深处常年起雾。"},
    {"id": "wuzhao", "name": "雾沼", "biome": "沼泽", "center": (2800, 7300), "levels": (18, 26),
     "desc": "西南的湿地，浑水、芦苇和枯树，夜里萤火虫漫天。毒属性和虫属性的乐园。"},
    {"id": "weilan", "name": "蔚蓝海岸", "biome": "海岸", "center": (5000, 7900), "levels": (24, 31),
     "desc": "南方的长海岸线：白沙滩、礁石、椰林和近海小岛，往南是一望无际的大海。"},
    {"id": "jinsha", "name": "金沙荒漠", "biome": "沙漠", "center": (7300, 7300), "levels": (30, 37),
     "desc": "东南的沙漠，沙丘、仙人掌、风蚀岩柱和古代遗迹，正午酷热，只有绿洲有人烟。"},
    {"id": "chiyan", "name": "赤炎火山", "biome": "火山", "center": (7900, 5000), "levels": (36, 43),
     "desc": "东部的活火山地带，黑色火山灰地面、熔岩河和温泉，枯树之间偶尔冒出火星。"},
    {"id": "cangyan", "name": "苍岩山脉", "biome": "山地", "center": (7200, 2700), "levels": (42, 49),
     "desc": "东北的崇山峻岭，碎石坡、巨岩和高山松林，山腹里有四通八达的矿洞。"},
    {"id": "bijing", "name": "碧镜湖区", "biome": "湖区", "center": (2800, 2700), "levels": (48, 55),
     "desc": "西北的湖泊群，湖面平如镜，湖心有小岛，岸边芦苇和草甸。传说湖底沉睡着古老的奇异兽。"},
    {"id": "shuangling", "name": "霜岭", "biome": "雪原", "center": (5000, 2000), "levels": (54, 65),
     "desc": "北方的雪原与冰川，针叶林披着积雪，冰湖上可以滑行。最北端是奇异兽联盟。"},
]

# kind: start 起始小镇（手工设计）, city 有道馆的城市, town 小镇, league 联盟
TOWNS = [
    {"id": "chenlu", "name": "晨露镇", "kind": "start", "region": "cuiyuan", "pos": (5000, 5000),
     "desc": "主角的家乡。研究员在这里发放第一只奇异兽。"},
    {"id": "cuiyuanshi", "name": "翠原市", "kind": "city", "region": "cuiyuan", "pos": (5000, 4250),
     "gym": {"order": 1, "type": "普通", "leader": "馆主 阿岚", "badge": "原野徽章"},
     "desc": "草原上最大的城市，集市热闹，第一座道馆在城北。"},
    {"id": "fengche", "name": "风车村", "kind": "town", "region": "cuiyuan", "pos": (5750, 5450),
     "desc": "小山坡上转着一排风车，村里有育宠屋。"},
    {"id": "senyu", "name": "森语镇", "kind": "city", "region": "shencui", "pos": (2450, 5050),
     "gym": {"order": 2, "type": "草", "leader": "馆主 青藤", "badge": "新叶徽章"},
     "desc": "建在巨树之间的木屋小镇，居民擅长与草系奇异兽沟通。"},
    {"id": "gushu", "name": "古树村", "kind": "town", "region": "shencui", "pos": (1700, 4550),
     "desc": "森林深处的隐村，守护着千年神木。"},
    {"id": "nitan", "name": "泥潭村", "kind": "city", "region": "wuzhao", "pos": (2900, 7200),
     "gym": {"order": 3, "type": "毒", "leader": "馆主 墨苔", "badge": "雾沼徽章"},
     "desc": "高脚屋连成的水上村落，靠栈桥互通。"},
    {"id": "yinghuo", "name": "萤火渡口", "kind": "town", "region": "wuzhao", "pos": (2250, 7750),
     "desc": "沼泽边的渡口，夜里萤火虫照亮整条河。"},
    {"id": "chaoxi", "name": "潮汐港", "kind": "city", "region": "weilan", "pos": (5000, 7650),
     "gym": {"order": 4, "type": "水", "leader": "馆主 海澜", "badge": "浪花徽章"},
     "desc": "南方最大的港口，渡轮通往近海小岛。"},
    {"id": "shanhu", "name": "珊瑚湾", "kind": "town", "region": "weilan", "pos": (4250, 8050),
     "desc": "海湾里的度假小镇，退潮时能走到珊瑚礁上。"},
    {"id": "lvzhou", "name": "绿洲城", "kind": "city", "region": "jinsha", "pos": (7300, 7200),
     "gym": {"order": 5, "type": "大地", "leader": "馆主 沙罗", "badge": "沙丘徽章"},
     "desc": "围绕绿洲建起的商队之城，城墙是夯土砌的。"},
    {"id": "shaxing", "name": "沙行驿站", "kind": "town", "region": "jinsha", "pos": (6550, 6750),
     "desc": "进入沙漠前最后的补给站。"},
    {"id": "rongyan", "name": "熔岩镇", "kind": "city", "region": "chiyan", "pos": (7650, 5100),
     "gym": {"order": 6, "type": "火", "leader": "馆主 赤炼", "badge": "熔火徽章"},
     "desc": "建在冷却熔岩台地上的锻造之镇，到处是工坊的炉火。"},
    {"id": "wenquan", "name": "温泉村", "kind": "town", "region": "chiyan", "pos": (7050, 4650),
     "desc": "火山脚下的温泉乡，泡温泉能让奇异兽恢复精神。"},
    {"id": "yanbao", "name": "岩堡城", "kind": "city", "region": "cangyan", "pos": (7200, 2950),
     "gym": {"order": 7, "type": "岩石", "leader": "馆主 磐石", "badge": "山岳徽章"},
     "desc": "依山而建的石头城堡，城下就是回声矿洞的入口。"},
    {"id": "kuanggong", "name": "矿工营地", "kind": "town", "region": "cangyan", "pos": (6550, 3350),
     "desc": "矿工们的临时营地，能买到挖矿得来的进化石。"},
    {"id": "jinghu", "name": "镜湖城", "kind": "city", "region": "bijing", "pos": (2900, 2950),
     "gym": {"order": 8, "type": "灵能", "leader": "馆主 镜音", "badge": "明镜徽章"},
     "desc": "湖畔的白色城市，有图书馆和古代研究所。"},
    {"id": "luwei", "name": "芦苇村", "kind": "town", "region": "bijing", "pos": (2250, 3400),
     "desc": "芦苇荡里的渔村，船夫可以送你去湖心岛。"},
    {"id": "shuangxue", "name": "霜雪村", "kind": "town", "region": "shuangling", "pos": (5000, 2450),
     "desc": "联盟前最后的村庄，雪屋连成一片。"},
    {"id": "lianmeng", "name": "奇异兽联盟", "kind": "league", "region": "shuangling", "pos": (5000, 1350),
     "desc": "四天王与冠军所在的冰雪殿堂，集齐八枚徽章才能进入。"},
]

# 道路：按编号连接两个城镇，生成器沿折线铺路，并在两侧放高草
ROUTES = [
    (1, "chenlu", "cuiyuanshi"), (2, "chenlu", "fengche"), (3, "cuiyuanshi", "senyu"),
    (4, "senyu", "gushu"), (5, "senyu", "nitan"), (6, "nitan", "yinghuo"),
    (7, "nitan", "chaoxi"), (8, "chaoxi", "shanhu"), (9, "chaoxi", "shaxing"),
    (10, "shaxing", "lvzhou"), (11, "fengche", "shaxing"), (12, "lvzhou", "rongyan"),
    (13, "rongyan", "wenquan"), (14, "wenquan", "kuanggong"), (15, "kuanggong", "yanbao"),
    (16, "cuiyuanshi", "kuanggong"), (17, "yanbao", "shuangxue"), (18, "shuangxue", "jinghu"),
    (19, "jinghu", "luwei"), (20, "luwei", "gushu"), (21, "cuiyuanshi", "shuangxue"),
    (22, "shuangxue", "lianmeng"),
]

# 迷宫与地标：kind dungeon 迷宫入口, landmark 地标
PLACES = [
    {"name": "千年神木", "kind": "landmark", "region": "shencui", "pos": (1950, 5350),
     "desc": "森林中央的巨树，树根盘成拱门，传说中的森林守护兽栖息于此。"},
    {"name": "迷雾林海", "kind": "dungeon", "region": "shencui", "pos": (1500, 5200),
     "desc": "终年起雾的密林迷宫，走错路会绕回原点。"},
    {"name": "沉没神殿", "kind": "dungeon", "region": "wuzhao", "pos": (3250, 7700),
     "desc": "半没在泥沼里的古代神殿。"},
    {"name": "白帆灯塔", "kind": "landmark", "region": "weilan", "pos": (5650, 8250),
     "desc": "海岸尽头的灯塔，塔顶能眺望整片海湾。"},
    {"name": "海蚀洞", "kind": "dungeon", "region": "weilan", "pos": (4600, 8300),
     "desc": "退潮才露出入口的海边洞窟。"},
    {"name": "流沙遗迹", "kind": "dungeon", "region": "jinsha", "pos": (7750, 7750),
     "desc": "被流沙半掩的古城遗迹，石壁上刻着奇异兽的古文字。"},
    {"name": "火山口", "kind": "dungeon", "region": "chiyan", "pos": (8250, 4900),
     "desc": "活火山的火口，熔岩湖边住着传说中的火之兽。"},
    {"name": "回声矿洞", "kind": "dungeon", "region": "cangyan", "pos": (7550, 2450),
     "desc": "山腹中的矿洞网，能挖到进化石和化石。"},
    {"name": "云巅", "kind": "landmark", "region": "cangyan", "pos": (7900, 2100),
     "desc": "山脉最高峰，云海之上，偶尔能看到飞行系的传说奇异兽。"},
    {"name": "湖心岛", "kind": "landmark", "region": "bijing", "pos": (2650, 2450),
     "desc": "镜湖中央的小岛，岛上有古老的石阵。"},
    {"name": "冰晶洞", "kind": "dungeon", "region": "shuangling", "pos": (4300, 1900),
     "desc": "冰川里的洞穴，墙壁是透明的冰晶。"},
    {"name": "冠军之路", "kind": "dungeon", "region": "shuangling", "pos": (5000, 1800),
     "desc": "通往联盟的最后考验，强大的训练师在此等候。"},
]


def _region(rid):
    return next(r for r in REGIONS if r["id"] == rid)


def _town(tid):
    return next(t for t in TOWNS if t["id"] == tid)


def write_gd():
    lines = [
        "class_name WorldPlan",
        "extends RefCounted",
        "## 由 tools/world_plan.py 生成，不要手改。世界规划：区域、城镇、道路、地点。",
        "",
        "const REGION_NAME := \"%s\"" % REGION_NAME,
        "const SIZE := %d" % SIZE,
        "## 起始小镇手工布局的左上角",
        "const START_ORIGIN := Vector2i(%d, %d)" % (sc(TOWNS[0]["pos"])[0] - START_HALF[0], sc(TOWNS[0]["pos"])[1] - START_HALF[1]),
        "",
        "## biome 是 WorldGen.Biome 的序号：" + "、".join("%d %s" % (i, b) for i, b in enumerate(BIOMES)),
        "const REGIONS := [",
    ]
    for r in REGIONS:
        lines.append('\t{"id": "%s", "name": "%s", "biome": %d, "center": Vector2i(%d, %d), "levels": [%d, %d]},'
                     % (r["id"], r["name"], BIOMES.index(r["biome"]), *sc(r["center"]), *r["levels"]))
    lines += ["]", "", "const TOWNS := ["]
    for t in TOWNS:
        gym = t.get("gym")
        gym_s = ('{"order": %d, "type": "%s", "leader": "%s", "badge": "%s"}'
                 % (gym["order"], gym["type"], gym["leader"], gym["badge"])) if gym else "{}"
        lines.append('\t{"id": "%s", "name": "%s", "kind": "%s", "region": "%s", "pos": Vector2i(%d, %d), "gym": %s},'
                     % (t["id"], t["name"], t["kind"], t["region"], *sc(t["pos"]), gym_s))
    lines += ["]", "", "## [编号, 起点城镇 id, 终点城镇 id]", "const ROUTES := ["]
    for n, a, b in ROUTES:
        lines.append('\t[%d, "%s", "%s"],' % (n, a, b))
    lines += ["]", "", "const PLACES := ["]
    for p in PLACES:
        lines.append('\t{"name": "%s", "kind": "%s", "region": "%s", "pos": Vector2i(%d, %d), "desc": "%s"},'
                     % (p["name"], p["kind"], p["region"], *sc(p["pos"]), p["desc"]))
    lines += ["]", ""]
    (ROOT / "scripts" / "world" / "world_plan.gd").write_text("\n".join(lines), encoding="utf-8")


def write_md():
    out = ["# 奈尔斯地区世界规划", "",
           "由 `tools/world_plan.py` 生成。地图 %d×%d 格（880×880 个 16 格区块），(0,0) 在左上角（北在上）。按正常步行速度，横穿整张地图约 40 分钟。" % (SIZE, SIZE),
           "外围约 460 格是海洋，南边的海更宽，海里散布着小岛。区域之间的边界由噪声扰动，地形自然过渡。", "",
           "## 冒险路线", "",
           "晨露镇出发 → 翠原市（道馆 1）→ 森语镇（2）→ 泥潭村（3）→ 潮汐港（4）→ 绿洲城（5）"
           "→ 熔岩镇（6）→ 岩堡城（7）→ 镜湖城（8）→ 霜雪村 → 冠军之路 → 奇异兽联盟。"
           "大体是从中央出发，逆时针绕外圈一周，最后北上。", "",
           "## 区域", ""]
    for r in REGIONS:
        out.append("### %s（%s，野生等级 %d–%d）" % (r["name"], r["biome"], *r["levels"]))
        out.append("")
        out.append("中心约 (%d, %d)。%s" % (*sc(r["center"]), r["desc"]))
        out.append("")
        for t in [t for t in TOWNS if t["region"] == r["id"]]:
            g = t.get("gym")
            extra = "，道馆 %d：%s（%s属性，%s）" % (g["order"], g["leader"], g["type"], g["badge"]) if g else ""
            out.append("- **%s** (%d, %d)%s。%s" % (t["name"], *sc(t["pos"]), extra, t["desc"]))
        for p in [p for p in PLACES if p["region"] == r["id"]]:
            out.append("- %s **%s** (%d, %d)。%s" % ("迷宫" if p["kind"] == "dungeon" else "地标", p["name"], *sc(p["pos"]), p["desc"]))
        out.append("")
    out += ["## 道路", "", "| 道路 | 连接 | 大致长度（格） |", "| --- | --- | --- |"]
    for n, a, b in ROUTES:
        ta, tb = _town(a), _town(b)
        d = int(((ta["pos"][0] - tb["pos"][0]) ** 2 + (ta["pos"][1] - tb["pos"][1]) ** 2) ** 0.5 * SCALE)
        out.append("| %d号道路 | %s — %s | %d |" % (n, ta["name"], tb["name"], d))
    out.append("")
    (ROOT / "docs" / "world-plan.md").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    write_gd()
    write_md()
    print("已生成 scripts/world/world_plan.gd 和 docs/world-plan.md")
