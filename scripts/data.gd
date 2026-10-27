class_name Data
extends RefCounted
## 静态游戏数据：招式、属性克制、物种、野外遭遇表。
## 以后数据量变大时可以迁到 Resource（.tres）或 JSON。

const MOVES := {
	"撞击": {"type": "普通", "power": 40},
	"啄": {"type": "普通", "power": 35},
	"咬住": {"type": "普通", "power": 60},
	"火花": {"type": "火", "power": 40},
	"火焰轮": {"type": "火", "power": 65},
	"水枪": {"type": "水", "power": 40},
	"泡沫光线": {"type": "水", "power": 65},
	"吸取": {"type": "草", "power": 30},
	"飞叶": {"type": "草", "power": 45},
	"飞叶快刀": {"type": "草", "power": 60},
}

## 攻击属性 -> 防守属性 -> 倍率，未列出的为 1.0
const EFFECTIVENESS := {
	"火": {"草": 2.0, "水": 0.5, "火": 0.5},
	"水": {"火": 2.0, "草": 0.5, "水": 0.5},
	"草": {"水": 2.0, "火": 0.5, "草": 0.5},
}

const SPECIES := {
	"huohu": {
		"name": "焰尾狐", "type": "火", "shape": "fox",
		"col": "#e8743b", "col2": "#ffe1a8", "dark": "#a8441c",
		"base": {"hp": 40, "atk": 55, "def": 42, "spd": 62},
		"catch_rate": 0.3, "xp": 64,
		"moves": [[1, "撞击"], [1, "火花"], [8, "咬住"], [12, "火焰轮"]],
	},
	"paowa": {
		"name": "泡泡蛙", "type": "水", "shape": "frog",
		"col": "#4c9be8", "col2": "#d6efff", "dark": "#2a6bb0",
		"base": {"hp": 46, "atk": 48, "def": 55, "spd": 45},
		"catch_rate": 0.3, "xp": 64,
		"moves": [[1, "撞击"], [1, "水枪"], [8, "咬住"], [12, "泡沫光线"]],
	},
	"yeshu": {
		"name": "叶芽鼠", "type": "草", "shape": "mouse",
		"col": "#c9b78a", "col2": "#f5c2c7", "dark": "#8d7a52",
		"base": {"hp": 44, "atk": 50, "def": 50, "spd": 50},
		"catch_rate": 0.35, "xp": 64,
		"moves": [[1, "撞击"], [1, "吸取"], [7, "飞叶"], [12, "飞叶快刀"]],
	},
	"yuanniao": {
		"name": "圆滚鸟", "type": "普通", "shape": "bird",
		"col": "#b9a3e3", "col2": "#f4ecff", "dark": "#7a62a8",
		"base": {"hp": 40, "atk": 45, "def": 40, "spd": 56},
		"catch_rate": 0.7, "xp": 50,
		"moves": [[1, "撞击"], [3, "啄"], [10, "咬住"]],
	},
	"chongchong": {
		"name": "绒绒虫", "type": "草", "shape": "worm",
		"col": "#9ad66b", "col2": "#e4ffc9", "dark": "#5c9a3a",
		"base": {"hp": 45, "atk": 30, "def": 35, "spd": 40},
		"catch_rate": 0.8, "xp": 40,
		"moves": [[1, "撞击"], [4, "吸取"], [11, "飞叶"]],
	},
	"tantan": {
		"name": "炭炭", "type": "火", "shape": "blob",
		"col": "#4a3f4f", "col2": "#ffe17a", "dark": "#2b232e",
		"base": {"hp": 45, "atk": 50, "def": 45, "spd": 35},
		"catch_rate": 0.5, "xp": 58,
		"moves": [[1, "撞击"], [5, "火花"], [13, "火焰轮"]],
	},
	"fufu": {
		"name": "浮浮母", "type": "水", "shape": "jelly",
		"col": "#8fd8e8", "col2": "#ffffff", "dark": "#4aa2b8",
		"base": {"hp": 50, "atk": 40, "def": 50, "spd": 40},
		"catch_rate": 0.5, "xp": 58,
		"moves": [[1, "撞击"], [5, "水枪"], [13, "泡沫光线"]],
	},
}

const STARTERS := ["huohu", "paowa", "yeshu"]

const ZONES := [
	{
		"name": "1号道路", "levels": [2, 5],
		"table": [["yuanniao", 40], ["chongchong", 35], ["yeshu", 25]],
	},
	{
		"name": "2号道路", "levels": [5, 9],
		"table": [["yuanniao", 20], ["chongchong", 15], ["tantan", 22], ["fufu", 18], ["paowa", 13], ["huohu", 12]],
	},
]


static func effectiveness(move_type: String, target_type: String) -> float:
	var row: Dictionary = EFFECTIVENESS.get(move_type, {})
	return row.get(target_type, 1.0)


## 按权重从区域遭遇表中抽取一只野生奇异兽
static func roll_wild(zone_index: int, rng: RandomNumberGenerator) -> Monster:
	var zone: Dictionary = ZONES[zone_index]
	var total := 0
	for entry in zone["table"]:
		total += int(entry[1])
	var r := rng.randi_range(0, total - 1)
	var key: String = zone["table"][0][0]
	for entry in zone["table"]:
		r -= int(entry[1])
		if r < 0:
			key = entry[0]
			break
	var lv := rng.randi_range(int(zone["levels"][0]), int(zone["levels"][1]))
	return Monster.create(key, lv)
