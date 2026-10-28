class_name Monster
extends RefCounted
## 一只奇异兽的实例：物种、等级、当前 HP、经验与招式。

var key: String
var level: int
var hp: int
var xp: int
var moves: Array[String] = []


static func create(species_key: String, lv: int) -> Monster:
	var m := Monster.new()
	m.key = species_key
	m.level = lv
	m.xp = lv * lv * lv
	for entry in m.species()["moves"]:
		if int(entry[0]) <= lv:
			m.moves.append(entry[1])
	while m.moves.size() > 4:
		m.moves.pop_front()
	m.hp = m.max_hp()
	return m


func species() -> Dictionary:
	return Data.SPECIES[key]


func species_name() -> String:
	return species()["name"]


func type() -> String:
	return species()["type"]


func stat(stat_name: String) -> int:
	var base: int = species()["base"][stat_name]
	if stat_name == "hp":
		return int(base * 2 * level / 100.0) + level + 10
	return int(base * 2 * level / 100.0) + 5


func max_hp() -> int:
	return stat("hp")


func is_fainted() -> bool:
	return hp <= 0


func heal() -> void:
	hp = max_hp()


## 升到下一级所需的累计经验（立方曲线）
func xp_for_next() -> int:
	return (level + 1) * (level + 1) * (level + 1)


## 升一级并返回本级新学会的招式（可能为空）
func level_up() -> Array[String]:
	var old_max := max_hp()
	level += 1
	hp += max_hp() - old_max
	var learned: Array[String] = []
	for entry in species()["moves"]:
		if int(entry[0]) == level and not moves.has(entry[1]):
			learned.append(entry[1])
	return learned


## 进化：换成新物种，按最大 HP 的增量补血，招式保留
func evolve(new_key: String) -> void:
	var old_max := max_hp()
	key = new_key
	hp += max_hp() - old_max


## 用伤药回复，返回实际回复量
func restore(amount: int) -> int:
	var healed := mini(amount, max_hp() - hp)
	hp += healed
	return healed


func to_dict() -> Dictionary:
	return {"key": key, "level": level, "hp": hp, "xp": xp, "moves": Array(moves)}


static func from_dict(d: Dictionary) -> Monster:
	var m := Monster.new()
	m.key = d["key"]
	m.level = int(d["level"])
	m.hp = int(d["hp"])
	m.xp = int(d["xp"])
	for mv in d["moves"]:
		m.moves.append(str(mv))
	return m
