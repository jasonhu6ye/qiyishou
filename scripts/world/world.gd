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

const HOUSES := [
	{"rect": Rect2i(4, 3, 4, 3), "roof": "#d9534f", "heal": true},
	{"rect": Rect2i(11, 3, 4, 3), "roof": "#4a7fd1", "heal": false},
	{"rect": Rect2i(3, 10, 4, 3), "roof": "#5a9e5a", "heal": false},
]

const NPCS := [
	{
		"cell": Vector2i(12, 8), "body": "#3f8f6b", "hat": "#d8d0b8",
		"lines": [
			"老爷爷：年轻人，草丛里藏着野生的奇异兽，走进去就可能遇到。",
			"先把它们打到红血，再扔兽球，成功率会高很多。",
			"打不过就回镇子左上角的红屋顶治疗所，走进门就能免费恢复。",
			"往东走是2号道路，那里的奇异兽更强。听说湖边还有会喷火的炭炭。",
		],
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
				_set(Vector2i(x, y), WATER)
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
	_set(HEAL_DOOR, DOOR)
	_set(HEAL_EXIT, PATH)


func _fill(r: Rect2i, v: int, rng: RandomNumberGenerator, p := 1.0) -> void:
	for y in range(r.position.y, r.end.y):
		for x in range(r.position.x, r.end.x):
			if rng.randf() < p:
				_set(Vector2i(x, y), v)


func _set(c: Vector2i, v: int) -> void:
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


func _draw() -> void:
	var grass_a := Color("#7cc96b")
	var grass_b := Color("#78c467")
	for y in H:
		for x in W:
			var t := tiles[y * W + x]
			var o := Vector2(x * T, y * T)
			match t:
				PATH, DOOR:
					draw_rect(Rect2(o, Vector2(T, T)), Color("#e3c88f"))
					if (x * 7 + y * 3) % 5 == 0:
						draw_rect(Rect2(o + Vector2(4, 9), Vector2(2, 1)), Color("#c9ad72"))
				WATER:
					draw_rect(Rect2(o, Vector2(T, T)), Color("#3d8fd6"))
					var shimmer := fmod(_time * 11.0 + x * 5 + y * 3, 12.0)
					draw_rect(Rect2(o + Vector2(shimmer, 5 + (y % 2) * 5), Vector2(4, 1)), Color(1, 1, 1, 0.35))
					if tile_at(Vector2i(x, y - 1)) != WATER:
						draw_rect(Rect2(o, Vector2(T, 3)), Color("#a7dcf7"))
					if tile_at(Vector2i(x, y + 1)) != WATER:
						draw_rect(Rect2(o + Vector2(0, T - 2), Vector2(T, 2)), Color("#2a6fb0"))
				_:
					draw_rect(Rect2(o, Vector2(T, T)), grass_a if (x + y) % 2 else grass_b)
					if t == FLOWER:
						Art.ellipse(self, o + Vector2(4, 5), Vector2(1.4, 1.4), Color("#fff6a8"))
						Art.ellipse(self, o + Vector2(11, 11), Vector2(1.4, 1.4), Color("#ff9fb5"))
					elif t == TALL_GRASS:
						for blade in [Vector2(2, 6), Vector2(8, 2), Vector2(9, 10), Vector2(3, 12)]:
							var bp := o + blade
							Art.poly(self, [bp + Vector2(0, 5), bp + Vector2(2, -1), bp + Vector2(3, 5)], Color("#3f9a3c"))
							Art.poly(self, [bp + Vector2(2, 5), bp + Vector2(4.5, 0), bp + Vector2(5.5, 5)], Color("#2f7f2e"))
