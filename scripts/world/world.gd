class_name World
extends Node2D
## 地图：生成地块、绘制地面，并把树、房屋、NPC 与玩家放进按 Y 排序的物件层，
## 让角色可以走到树冠和屋顶后面（2.5D 遮挡）。

enum { GRASS, TALL_GRASS, WATER, TREE, PATH, HOUSE, DOOR, FLOWER }

const T := 16
const W := 48
const H := 36
const WALKABLE := [GRASS, TALL_GRASS, PATH, DOOR, FLOWER]
const HEAL_DOOR := Vector2i(6, 5)
const HEAL_EXIT := Vector2i(6, 6)
const SHOP_DOOR := Vector2i(13, 5)
const SHOP_EXIT := Vector2i(13, 6)

const HOUSES := [
	{"rect": Rect2i(4, 3, 4, 3), "kind": "heal"},
	{"rect": Rect2i(11, 3, 4, 3), "kind": "shop"},
	{"rect": Rect2i(3, 10, 4, 3), "kind": "home"},
]

const NPCS := [
	{
		"cell": Vector2i(12, 8), "sprite": "npc_elder",
		"lines": [
			"老爷爷：年轻人，草丛里藏着野生的奇异兽，走进去就可能遇到。",
			"先把它们打到红血，再扔兽球，成功率会高很多。",
			"打不过就回镇子左上角的红屋顶治疗所，走进门就能免费恢复。",
			"往东走是2号道路，那里的奇异兽更强。听说湖边还有会喷火的炭炭。",
			"对了，红屋顶旁边蓝屋顶的是商店，兽球和伤药都在那儿买。",
		],
	},
	{
		"cell": Vector2i(37, 15), "sprite": "npc_trainer", "facing": Vector2i.LEFT,
		"lines": ["阿杰：输给你我心服口服。再往前走走，说不定能碰到更厉害的奇异兽！"],
		"trainer": {
			"id": "trainer_ajie", "name": "训练师 阿杰", "sight": 4, "reward": 480,
			"team": [["yuanniao", 8], ["dianli", 9]],
			"intro": ["阿杰：喂！眼神对上了就是要对战！", "让你见识一下我精心培养的奇异兽！"],
			"defeat": "阿杰：怎么会……我的奇异兽明明那么强！",
		},
	},
]

var tiles := PackedInt32Array()
var objects: Node2D
var player: Player
var npc_props: Array[Prop] = []
var _time := 0.0


func _ready() -> void:
	_generate()
	objects = Node2D.new()
	objects.y_sort_enabled = true
	add_child(objects)
	for y in H:
		for x in W:
			if tiles[y * W + x] == TREE:
				var p := Prop.new()
				p.kind = "tree"
				p.position = Vector2(x * T + 8, (y + 1) * T)
				objects.add_child(p)
	for h in HOUSES:
		var r: Rect2i = h["rect"]
		var p := Prop.new()
		p.kind = "house"
		p.house = h
		p.position = Vector2(r.position.x * T, r.end.y * T)
		objects.add_child(p)
	for n in NPCS:
		var p := Prop.new()
		p.kind = "npc"
		p.npc = n
		p.position = Vector2(n["cell"].x * T + 8, (n["cell"].y + 1) * T)
		p.facing = n.get("facing", Vector2i.DOWN)
		objects.add_child(p)
		npc_props.append(p)
	player = Player.new()
	player.world = self
	objects.add_child(player)


func _process(delta: float) -> void:
	_time += delta
	queue_redraw()


func _generate() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 20261027
	tiles.resize(W * H)
	tiles.fill(GRASS)
	for patch in [Rect2i(12, 9, 8, 7), Rect2i(38, 9, 7, 10), Rect2i(11, 22, 10, 6), Rect2i(24, 22, 10, 6), Rect2i(38, 22, 7, 6)]:
		_fill(patch, TALL_GRASS, rng, 0.88)
	for y in H:
		for x in W:
			var dx := (x - 28) / 4.6
			var dy := (y - 16) / 3.2
			if dx * dx + dy * dy < 1.0:
				_set_tile(Vector2i(x, y), WATER)
	for road in [Rect2i(3, 7, 42, 1), Rect2i(9, 7, 1, 24), Rect2i(36, 7, 1, 24), Rect2i(9, 30, 28, 1)]:
		_fill(road, PATH, rng)
	for y in H:
		for x in W:
			if x < 2 or y < 2 or x >= W - 2 or y >= H - 2:
				tiles[y * W + x] = TREE
				continue
			if tiles[y * W + x] != GRASS:
				continue
			var r := rng.randf()
			if not is_town(Vector2i(x, y)) and r < 0.05:
				tiles[y * W + x] = TREE
			elif r < 0.11:
				tiles[y * W + x] = FLOWER
	for h in HOUSES:
		_fill(h["rect"], HOUSE, rng)
	_set_tile(HEAL_DOOR, DOOR)
	_set_tile(HEAL_EXIT, PATH)
	_set_tile(SHOP_DOOR, DOOR)
	_set_tile(SHOP_EXIT, PATH)
	# NPC 脚下保证是空地，不会被随机生成的树或草挡住
	for n in NPCS:
		_set_tile(n["cell"], GRASS)


func _fill(r: Rect2i, v: int, rng: RandomNumberGenerator, p := 1.0) -> void:
	for y in range(r.position.y, r.end.y):
		for x in range(r.position.x, r.end.x):
			if rng.randf() < p:
				_set_tile(Vector2i(x, y), v)


func _set_tile(c: Vector2i, v: int) -> void:
	if in_bounds(c):
		tiles[c.y * W + c.x] = v


func in_bounds(c: Vector2i) -> bool:
	return c.x >= 0 and c.y >= 0 and c.x < W and c.y < H


func tile_at(c: Vector2i) -> int:
	return tiles[c.y * W + c.x] if in_bounds(c) else TREE


func npc_at(c: Vector2i) -> Prop:
	for p in npc_props:
		if p.npc["cell"] == c:
			return p
	return null


## 玩家走到 cell 时，返回看见了他的、还没被打败的训练师（没有则返回 null）。
## 训练师沿面朝方向看 sight 格，视线会被不能走的格子挡住。
func trainer_spotting(c: Vector2i) -> Prop:
	for p in npc_props:
		var info: Dictionary = p.npc.get("trainer", {})
		if info.is_empty() or Game.flags.get(info["id"], false):
			continue
		var look: Vector2i = p.npc["cell"]
		for i in int(info["sight"]):
			look += p.facing
			if look == c:
				return p
			if not is_walkable(look) and look != c:
				break
	return null


func is_walkable(c: Vector2i) -> bool:
	return WALKABLE.has(tile_at(c)) and npc_at(c) == null


func is_town(c: Vector2i) -> bool:
	return c.x < 18 and c.y < 15


## 0 = 1号道路，1 = 2号道路
func zone_index(c: Vector2i) -> int:
	return 0 if c.x < 22 else 1


func area_name(c: Vector2i) -> String:
	if is_town(c):
		return "晨露镇"
	return Data.ZONES[zone_index(c)]["name"]


func house_at(c: Vector2i) -> Dictionary:
	for h in HOUSES:
		if (h["rect"] as Rect2i).has_point(c):
			return h
	return {}


## tiles.png 中的格子：0/1 草地  2 花  3 高草  4 小路  5-7 水面三帧
func _tile_frame(t: int, x: int, y: int) -> int:
	match t:
		PATH, DOOR:
			return 4
		WATER:
			return 5 + int(_time * 3.0) % 3
		FLOWER:
			return 2
		TALL_GRASS:
			return 3
	return 1 if (x * 7 + y * 3) % 5 == 0 else 0


func _draw() -> void:
	var sheet := Art.tex("tiles")
	var size := Vector2(T, T)
	for y in H:
		for x in W:
			var t := tiles[y * W + x]
			var o := Vector2(x * T, y * T)
			draw_texture_rect_region(sheet, Rect2(o, size), Rect2(_tile_frame(t, x, y) * T, 0, T, T))
			if t == WATER:
				if tile_at(Vector2i(x, y - 1)) != WATER:
					draw_rect(Rect2(o, Vector2(T, 2)), Color("#cdeeff"))
				if tile_at(Vector2i(x, y + 1)) != WATER:
					draw_rect(Rect2(o + Vector2(0, T - 2), Vector2(T, 2)), Color("#2a6fb0"))
