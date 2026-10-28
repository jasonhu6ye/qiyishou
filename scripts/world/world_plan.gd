class_name WorldPlan
extends RefCounted
## 由 tools/world_plan.py 生成，不要手改。世界规划：区域、城镇、道路、地点。

const REGION_NAME := "奈尔斯地区"
const SIZE := 14080
## 起始小镇手工布局的左上角
const START_ORIGIN := Vector2i(7016, 7022)

## biome 是 WorldGen.Biome 的序号：0 草原、1 森林、2 沼泽、3 海岸、4 沙漠、5 火山、6 山地、7 湖区、8 雪原
const REGIONS := [
	{"id": "cuiyuan", "name": "翠原", "biome": 0, "center": Vector2i(7040, 7040), "levels": [2, 14]},
	{"id": "shencui", "name": "深翠森林", "biome": 1, "center": Vector2i(3098, 7040), "levels": [12, 20]},
	{"id": "wuzhao", "name": "雾沼", "biome": 2, "center": Vector2i(3942, 10278), "levels": [18, 26]},
	{"id": "weilan", "name": "蔚蓝海岸", "biome": 3, "center": Vector2i(7040, 11123), "levels": [24, 31]},
	{"id": "jinsha", "name": "金沙荒漠", "biome": 4, "center": Vector2i(10278, 10278), "levels": [30, 37]},
	{"id": "chiyan", "name": "赤炎火山", "biome": 5, "center": Vector2i(11123, 7040), "levels": [36, 43]},
	{"id": "cangyan", "name": "苍岩山脉", "biome": 6, "center": Vector2i(10138, 3802), "levels": [42, 49]},
	{"id": "bijing", "name": "碧镜湖区", "biome": 7, "center": Vector2i(3942, 3802), "levels": [48, 55]},
	{"id": "shuangling", "name": "霜岭", "biome": 8, "center": Vector2i(7040, 2816), "levels": [54, 65]},
]

const TOWNS := [
	{"id": "chenlu", "name": "晨露镇", "kind": "start", "region": "cuiyuan", "pos": Vector2i(7040, 7040), "gym": {}},
	{"id": "cuiyuanshi", "name": "翠原市", "kind": "city", "region": "cuiyuan", "pos": Vector2i(7040, 5984), "gym": {"order": 1, "type": "普通", "leader": "馆主 阿岚", "badge": "原野徽章"}},
	{"id": "fengche", "name": "风车村", "kind": "town", "region": "cuiyuan", "pos": Vector2i(8096, 7674), "gym": {}},
	{"id": "senyu", "name": "森语镇", "kind": "city", "region": "shencui", "pos": Vector2i(3450, 7110), "gym": {"order": 2, "type": "草", "leader": "馆主 青藤", "badge": "新叶徽章"}},
	{"id": "gushu", "name": "古树村", "kind": "town", "region": "shencui", "pos": Vector2i(2394, 6406), "gym": {}},
	{"id": "nitan", "name": "泥潭村", "kind": "city", "region": "wuzhao", "pos": Vector2i(4083, 10138), "gym": {"order": 3, "type": "毒", "leader": "馆主 墨苔", "badge": "雾沼徽章"}},
	{"id": "yinghuo", "name": "萤火渡口", "kind": "town", "region": "wuzhao", "pos": Vector2i(3168, 10912), "gym": {}},
	{"id": "chaoxi", "name": "潮汐港", "kind": "city", "region": "weilan", "pos": Vector2i(7040, 10771), "gym": {"order": 4, "type": "水", "leader": "馆主 海澜", "badge": "浪花徽章"}},
	{"id": "shanhu", "name": "珊瑚湾", "kind": "town", "region": "weilan", "pos": Vector2i(5984, 11334), "gym": {}},
	{"id": "lvzhou", "name": "绿洲城", "kind": "city", "region": "jinsha", "pos": Vector2i(10278, 10138), "gym": {"order": 5, "type": "大地", "leader": "馆主 沙罗", "badge": "沙丘徽章"}},
	{"id": "shaxing", "name": "沙行驿站", "kind": "town", "region": "jinsha", "pos": Vector2i(9222, 9504), "gym": {}},
	{"id": "rongyan", "name": "熔岩镇", "kind": "city", "region": "chiyan", "pos": Vector2i(10771, 7181), "gym": {"order": 6, "type": "火", "leader": "馆主 赤炼", "badge": "熔火徽章"}},
	{"id": "wenquan", "name": "温泉村", "kind": "town", "region": "chiyan", "pos": Vector2i(9926, 6547), "gym": {}},
	{"id": "yanbao", "name": "岩堡城", "kind": "city", "region": "cangyan", "pos": Vector2i(10138, 4154), "gym": {"order": 7, "type": "岩石", "leader": "馆主 磐石", "badge": "山岳徽章"}},
	{"id": "kuanggong", "name": "矿工营地", "kind": "town", "region": "cangyan", "pos": Vector2i(9222, 4717), "gym": {}},
	{"id": "jinghu", "name": "镜湖城", "kind": "city", "region": "bijing", "pos": Vector2i(4083, 4154), "gym": {"order": 8, "type": "灵能", "leader": "馆主 镜音", "badge": "明镜徽章"}},
	{"id": "luwei", "name": "芦苇村", "kind": "town", "region": "bijing", "pos": Vector2i(3168, 4787), "gym": {}},
	{"id": "shuangxue", "name": "霜雪村", "kind": "town", "region": "shuangling", "pos": Vector2i(7040, 3450), "gym": {}},
	{"id": "lianmeng", "name": "奇异兽联盟", "kind": "league", "region": "shuangling", "pos": Vector2i(7040, 1901), "gym": {}},
]

## [编号, 起点城镇 id, 终点城镇 id]
const ROUTES := [
	[1, "chenlu", "cuiyuanshi"],
	[2, "chenlu", "fengche"],
	[3, "cuiyuanshi", "senyu"],
	[4, "senyu", "gushu"],
	[5, "senyu", "nitan"],
	[6, "nitan", "yinghuo"],
	[7, "nitan", "chaoxi"],
	[8, "chaoxi", "shanhu"],
	[9, "chaoxi", "shaxing"],
	[10, "shaxing", "lvzhou"],
	[11, "fengche", "shaxing"],
	[12, "lvzhou", "rongyan"],
	[13, "rongyan", "wenquan"],
	[14, "wenquan", "kuanggong"],
	[15, "kuanggong", "yanbao"],
	[16, "cuiyuanshi", "kuanggong"],
	[17, "yanbao", "shuangxue"],
	[18, "shuangxue", "jinghu"],
	[19, "jinghu", "luwei"],
	[20, "luwei", "gushu"],
	[21, "cuiyuanshi", "shuangxue"],
	[22, "shuangxue", "lianmeng"],
]

const PLACES := [
	{"name": "千年神木", "kind": "landmark", "region": "shencui", "pos": Vector2i(2746, 7533), "desc": "森林中央的巨树，树根盘成拱门，传说中的森林守护兽栖息于此。"},
	{"name": "迷雾林海", "kind": "dungeon", "region": "shencui", "pos": Vector2i(2112, 7322), "desc": "终年起雾的密林迷宫，走错路会绕回原点。"},
	{"name": "沉没神殿", "kind": "dungeon", "region": "wuzhao", "pos": Vector2i(4576, 10842), "desc": "半没在泥沼里的古代神殿。"},
	{"name": "白帆灯塔", "kind": "landmark", "region": "weilan", "pos": Vector2i(7955, 11616), "desc": "海岸尽头的灯塔，塔顶能眺望整片海湾。"},
	{"name": "海蚀洞", "kind": "dungeon", "region": "weilan", "pos": Vector2i(6477, 11686), "desc": "退潮才露出入口的海边洞窟。"},
	{"name": "流沙遗迹", "kind": "dungeon", "region": "jinsha", "pos": Vector2i(10912, 10912), "desc": "被流沙半掩的古城遗迹，石壁上刻着奇异兽的古文字。"},
	{"name": "火山口", "kind": "dungeon", "region": "chiyan", "pos": Vector2i(11616, 6899), "desc": "活火山的火口，熔岩湖边住着传说中的火之兽。"},
	{"name": "回声矿洞", "kind": "dungeon", "region": "cangyan", "pos": Vector2i(10630, 3450), "desc": "山腹中的矿洞网，能挖到进化石和化石。"},
	{"name": "云巅", "kind": "landmark", "region": "cangyan", "pos": Vector2i(11123, 2957), "desc": "山脉最高峰，云海之上，偶尔能看到飞行系的传说奇异兽。"},
	{"name": "湖心岛", "kind": "landmark", "region": "bijing", "pos": Vector2i(3731, 3450), "desc": "镜湖中央的小岛，岛上有古老的石阵。"},
	{"name": "冰晶洞", "kind": "dungeon", "region": "shuangling", "pos": Vector2i(6054, 2675), "desc": "冰川里的洞穴，墙壁是透明的冰晶。"},
	{"name": "冠军之路", "kind": "dungeon", "region": "shuangling", "pos": Vector2i(7040, 2534), "desc": "通往联盟的最后考验，强大的训练师在此等候。"},
]
