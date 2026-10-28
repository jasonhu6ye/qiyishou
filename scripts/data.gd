class_name Data
extends RefCounted
## 静态游戏数据：招式、属性克制、物种与进化、各地貌的遭遇表、商店。
## 以后数据量变大时可以迁到 Resource（.tres）或 JSON。

const MOVES := {
	"撞击": {"type": "普通", "power": 40},
	"啄": {"type": "普通", "power": 35},
	"咬住": {"type": "普通", "power": 60},
	"疾风翼": {"type": "普通", "power": 60},
	"火花": {"type": "火", "power": 40},
	"火焰轮": {"type": "火", "power": 65},
	"烈焰冲撞": {"type": "火", "power": 90},
	"水枪": {"type": "水", "power": 40},
	"泡沫光线": {"type": "水", "power": 65},
	"激流炮": {"type": "水", "power": 90},
	"吸取": {"type": "草", "power": 30},
	"飞叶": {"type": "草", "power": 45},
	"飞叶快刀": {"type": "草", "power": 60},
	"叶刃风暴": {"type": "草", "power": 90},
	"电击": {"type": "电", "power": 40},
	"雷电球": {"type": "电", "power": 65},
}

## 攻击属性 -> 防守属性 -> 倍率，未列出的为 1.0
const EFFECTIVENESS := {
	"火": {"草": 2.0, "水": 0.5, "火": 0.5},
	"水": {"火": 2.0, "草": 0.5, "水": 0.5},
	"草": {"水": 2.0, "火": 0.5, "草": 0.5},
	"电": {"水": 2.0, "草": 0.5, "电": 0.5},
}

## evolves: [进化后的物种, 进化等级]。立绘在 assets/sprites/monsters/<key>_front.png / _back.png
const SPECIES := {
	"huohu": {
		"name": "焰尾狐", "type": "火", "base": {"hp": 40, "atk": 55, "def": 42, "spd": 62},
		"catch_rate": 0.3, "xp": 64, "evolves": ["huohu2", 16],
		"moves": [[1, "撞击"], [1, "火花"], [8, "咬住"], [12, "火焰轮"]],
	},
	"huohu2": {
		"name": "烈焰狐", "type": "火", "base": {"hp": 58, "atk": 80, "def": 60, "spd": 82},
		"catch_rate": 0.1, "xp": 142,
		"moves": [[1, "撞击"], [1, "火花"], [8, "咬住"], [12, "火焰轮"], [22, "烈焰冲撞"]],
	},
	"paowa": {
		"name": "泡泡蛙", "type": "水", "base": {"hp": 46, "atk": 48, "def": 55, "spd": 45},
		"catch_rate": 0.3, "xp": 64, "evolves": ["paowa2", 16],
		"moves": [[1, "撞击"], [1, "水枪"], [8, "咬住"], [12, "泡沫光线"]],
	},
	"paowa2": {
		"name": "巨浪蛙", "type": "水", "base": {"hp": 68, "atk": 70, "def": 78, "spd": 58},
		"catch_rate": 0.1, "xp": 142,
		"moves": [[1, "撞击"], [1, "水枪"], [8, "咬住"], [12, "泡沫光线"], [22, "激流炮"]],
	},
	"yeshu": {
		"name": "叶芽鼠", "type": "草", "base": {"hp": 44, "atk": 50, "def": 50, "spd": 50},
		"catch_rate": 0.35, "xp": 64, "evolves": ["yeshu2", 16],
		"moves": [[1, "撞击"], [1, "吸取"], [7, "飞叶"], [12, "飞叶快刀"]],
	},
	"yeshu2": {
		"name": "森叶鼠", "type": "草", "base": {"hp": 62, "atk": 74, "def": 70, "spd": 70},
		"catch_rate": 0.1, "xp": 142,
		"moves": [[1, "撞击"], [1, "吸取"], [7, "飞叶"], [12, "飞叶快刀"], [22, "叶刃风暴"]],
	},
	"yuanniao": {
		"name": "圆滚鸟", "type": "普通", "base": {"hp": 40, "atk": 45, "def": 40, "spd": 56},
		"catch_rate": 0.7, "xp": 50, "evolves": ["yuanniao2", 14],
		"moves": [[1, "撞击"], [3, "啄"], [10, "咬住"]],
	},
	"yuanniao2": {
		"name": "疾风鸟", "type": "普通", "base": {"hp": 55, "atk": 70, "def": 55, "spd": 85},
		"catch_rate": 0.35, "xp": 120,
		"moves": [[1, "撞击"], [3, "啄"], [10, "咬住"], [14, "疾风翼"]],
	},
	"chongchong": {
		"name": "绒绒虫", "type": "草", "base": {"hp": 45, "atk": 30, "def": 35, "spd": 40},
		"catch_rate": 0.8, "xp": 40, "evolves": ["jianjian", 7],
		"moves": [[1, "撞击"], [4, "吸取"], [11, "飞叶"]],
	},
	"jianjian": {
		"name": "茧茧", "type": "草", "base": {"hp": 50, "atk": 20, "def": 70, "spd": 15},
		"catch_rate": 0.5, "xp": 60, "evolves": ["caidie", 10],
		"moves": [[1, "撞击"], [4, "吸取"]],
	},
	"caidie": {
		"name": "彩翼蝶", "type": "草", "base": {"hp": 60, "atk": 60, "def": 50, "spd": 70},
		"catch_rate": 0.3, "xp": 130,
		"moves": [[1, "吸取"], [10, "飞叶"], [12, "疾风翼"], [18, "飞叶快刀"]],
	},
	"tantan": {
		"name": "炭炭", "type": "火", "base": {"hp": 45, "atk": 50, "def": 45, "spd": 35},
		"catch_rate": 0.5, "xp": 58,
		"moves": [[1, "撞击"], [5, "火花"], [13, "火焰轮"]],
	},
	"fufu": {
		"name": "浮浮母", "type": "水", "base": {"hp": 50, "atk": 40, "def": 50, "spd": 40},
		"catch_rate": 0.5, "xp": 58,
		"moves": [[1, "撞击"], [5, "水枪"], [13, "泡沫光线"]],
	},
	"dianli": {
		"name": "电栗", "type": "电", "base": {"hp": 42, "atk": 52, "def": 40, "spd": 72},
		"catch_rate": 0.4, "xp": 62,
		"moves": [[1, "撞击"], [4, "电击"], [13, "雷电球"]],
	},
}

const STARTERS := ["huohu", "paowa", "yeshu"]

## 各地貌（WorldGen.Biome 的序号）的野生遭遇表：[物种, 权重]。等级由所在区域决定（WorldPlan.REGIONS 的 levels）
const BIOME_TABLES := [
	[["yuanniao", 30], ["chongchong", 25], ["yeshu", 20], ["huohu", 8], ["paowa", 8], ["dianli", 9]],
	[["chongchong", 30], ["yeshu", 25], ["jianjian", 15], ["yuanniao", 15], ["huohu", 10], ["caidie", 5]],
	[["paowa", 30], ["chongchong", 25], ["jianjian", 15], ["fufu", 15], ["tantan", 15]],
	[["fufu", 35], ["paowa", 30], ["yuanniao", 25], ["dianli", 10]],
	[["tantan", 35], ["dianli", 30], ["yuanniao", 20], ["huohu", 15]],
	[["tantan", 50], ["huohu", 35], ["dianli", 15]],
	[["yuanniao", 35], ["tantan", 20], ["dianli", 20], ["yuanniao2", 15], ["yeshu", 10]],
	[["paowa", 35], ["fufu", 30], ["yeshu", 15], ["caidie", 10], ["paowa2", 10]],
	[["fufu", 35], ["yuanniao", 25], ["dianli", 20], ["paowa", 20]],
	[["fufu", 60], ["paowa", 40]],
]

## 商店商品：名字 -> 价格
const SHOP := {"兽球": 200, "伤药": 300}
const POTION_HEAL := 20


static func effectiveness(move_type: String, target_type: String) -> float:
	var row: Dictionary = EFFECTIVENESS.get(move_type, {})
	return row.get(target_type, 1.0)


## 按地貌的遭遇表抽取一只野生奇异兽，等级在 levels = [最低, 最高] 之间
static func roll_wild(biome: int, levels: Array, rng: RandomNumberGenerator) -> Monster:
	var table: Array = BIOME_TABLES[clampi(biome, 0, BIOME_TABLES.size() - 1)]
	var total := 0
	for entry in table:
		total += int(entry[1])
	var r := rng.randi_range(0, total - 1)
	var key: String = table[0][0]
	for entry in table:
		r -= int(entry[1])
		if r < 0:
			key = entry[0]
			break
	return Monster.create(key, rng.randi_range(int(levels[0]), int(levels[1])))


## 达到进化等级时返回进化后的物种，否则返回空字符串
static func evolution_for(m: Monster) -> String:
	var evo: Array = m.species().get("evolves", [])
	if evo.size() == 2 and m.level >= int(evo[1]):
		return evo[0]
	return ""
