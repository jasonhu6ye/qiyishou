class_name World
extends Node2D
## 奈尔斯地区大地图。地形由 WorldGen 按区块确定性生成，这里负责：
## - 缓存区块数据，只给玩家附近 3x3 个区块建绘制节点和物件；
## - 把树、岩石、房屋、NPC 与玩家放进按 Y 排序的物件层（2.5D 遮挡）；
## - 提供格子查询：能不能走、草丛、门、地名、地貌。

const T := 16
const W := WorldGen.SIZE
const H := WorldGen.SIZE
const N := WorldGen.CHUNK
## 绘制半径（区块）：玩家所在区块周围 1 圈；超过 UNLOAD 圈就卸载
const VIEW := 1
const UNLOAD := 2
const DATA_LIMIT := 900

## 起始小镇里的 NPC，cell 是手工布局里的局部坐标
const NPCS := [
	{
		"cell": Vector2i(12, 8), "sprite": "npc_elder",
		"lines": [
			"老爷爷：年轻人，草丛里藏着野生的奇异兽，走进去就可能遇到。",
			"先把它们打到红血，再扔兽球，成功率会高很多。",
			"打不过就回镇子左上角的红屋顶治疗所，走进门就能免费恢复。",
			"奈尔斯地区大得很：往北是翠原市，往东是风车村，再往外还有森林、沙漠、火山和雪原。",
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

static var gen: WorldGen

var ground: Node2D
var objects: Node2D
var player: Player
var npc_props: Array[Prop] = []
## 动画帧（水面、熔岩每 0.25 秒一帧）
var frame := 0
var _time := 0.0
var _data := {}
var _loaded := {}
var _center := Vector2i(-999, -999)


static func generator() -> WorldGen:
	if gen == null:
		gen = WorldGen.new()
	return gen


func _ready() -> void:
	generator()
	ground = Node2D.new()
	add_child(ground)
	objects = Node2D.new()
	objects.y_sort_enabled = true
	add_child(objects)
	for n in NPCS:
		var p := Prop.new()
		p.kind = "npc"
		p.npc = n.duplicate()
		p.npc["cell"] = WorldGen.START_ORIGIN + Vector2i(n["cell"])
		p.position = Player.cell_to_pos(p.npc["cell"])
		p.facing = n.get("facing", Vector2i.DOWN)
		objects.add_child(p)
		npc_props.append(p)
	player = Player.new()
	player.world = self
	objects.add_child(player)


func _process(delta: float) -> void:
	_time += delta
	var f := int(_time * 4.0)
	if f != frame:
		frame = f
		for c in _loaded:
			var ch: Chunk = _loaded[c]["node"]
			if ch.has_anim:
				ch.anim.queue_redraw()
	update_chunks()


# ---------------------------------------------------------------- 区块
static func chunk_of(c: Vector2i) -> Vector2i:
	return Vector2i(floori(c.x / float(N)), floori(c.y / float(N)))


func chunk_data(ch: Vector2i) -> PackedInt32Array:
	if not _data.has(ch):
		if _data.size() > DATA_LIMIT:
			_trim_data()
		_data[ch] = gen.generate_chunk(ch)
	return _data[ch]


func _trim_data() -> void:
	for k in _data.keys():
		var d: Vector2i = k - _center
		if absi(d.x) > 6 or absi(d.y) > 6:
			_data.erase(k)


## 格子的打包值（见 WorldGen.pack）
func cell(c: Vector2i) -> int:
	var ch := chunk_of(c)
	var data := chunk_data(ch)
	return data[(c.y - ch.y * N) * N + (c.x - ch.x * N)]


## 让玩家附近的区块就绪，远处的卸载
func update_chunks() -> void:
	if player == null:
		return
	var center := chunk_of(player.cell)
	if center == _center:
		return
	_center = center
	for y in range(-VIEW, VIEW + 1):
		for x in range(-VIEW, VIEW + 1):
			var ch := center + Vector2i(x, y)
			if not _loaded.has(ch) and ch.x >= 0 and ch.y >= 0 and ch.x * N < W and ch.y * N < H:
				_load_chunk(ch)
	for ch in _loaded.keys():
		var d: Vector2i = ch - center
		if absi(d.x) > UNLOAD or absi(d.y) > UNLOAD:
			_unload_chunk(ch)


func _load_chunk(ch: Vector2i) -> void:
	var node := Chunk.new()
	node.setup(self, ch)
	ground.add_child(node)
	var props: Array[Node2D] = []
	var data := chunk_data(ch)
	for i in data.size():
		var obj := WorldGen.object_of(data[i])
		if obj == 0 or obj == WorldGen.BUILDING:
			continue
		var c := ch * N + Vector2i(i % N, i / N)
		var p := Prop.new()
		p.kind = "prop"
		p.prop_name = WorldGen.PROPS[obj]
		p.position = Vector2(c.x * T + 8, c.y * T + 15)
		objects.add_child(p)
		props.append(p)
	var rect := Rect2i(ch * N, Vector2i(N, N))
	for b in gen.buildings:
		var r: Rect2i = b["rect"]
		if rect.has_point(Vector2i(r.position.x, r.end.y - 1)):
			var p := Prop.new()
			p.kind = "house"
			p.house = b
			p.position = Vector2(r.position.x * T, r.end.y * T)
			objects.add_child(p)
			props.append(p)
	_loaded[ch] = {"node": node, "props": props}


func _unload_chunk(ch: Vector2i) -> void:
	var entry: Dictionary = _loaded[ch]
	(entry["node"] as Node).queue_free()
	for p in entry["props"]:
		(p as Node).queue_free()
	_loaded.erase(ch)


## 传送后调用：立刻按玩家新位置准备区块
func refresh_now() -> void:
	_center = Vector2i(-999, -999)
	update_chunks()


# ---------------------------------------------------------------- 查询
func in_bounds(c: Vector2i) -> bool:
	return c.x >= 0 and c.y >= 0 and c.x < W and c.y < H


func npc_at(c: Vector2i) -> Prop:
	for p in npc_props:
		if p.npc["cell"] == c:
			return p
	return null


func is_walkable(c: Vector2i) -> bool:
	return in_bounds(c) and WorldGen.walkable(cell(c)) and npc_at(c) == null


func is_tall_grass(c: Vector2i) -> bool:
	return WorldGen.is_tall(cell(c))


## 站在草丛里时盖住脚的叶片贴图名（不在草丛里返回空串）
func grass_front(c: Vector2i) -> String:
	var o := WorldGen.overlay_of(cell(c))
	if o < WorldGen.O_TALL:
		return ""
	return "front_" + String(WorldGen.TALL_NAMES[o - WorldGen.O_TALL]).trim_prefix("tall_")


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


## 门：返回房屋信息 {"kind": heal/shop/home/gym, "town", "door", "exit", "rect"}，不是门返回空字典
func door_at(c: Vector2i) -> Dictionary:
	for b in gen.buildings:
		if b["door"] == c:
			return b
	return {}


func building_at(c: Vector2i) -> Dictionary:
	for b in gen.buildings:
		if (b["rect"] as Rect2i).has_point(c):
			return b
	return {}


## 地貌（WorldGen.Biome）
func biome_at(c: Vector2i) -> int:
	return gen.biome_at(c.x, c.y)


## 所在区域的野生等级范围 [最低, 最高]
func region_levels(c: Vector2i) -> Array:
	return WorldPlan.REGIONS[gen.region_index(c.x, c.y)]["levels"]


## 战斗背景：草原、森林、湖区用晴天，其余用傍晚
func zone_index(c: Vector2i) -> int:
	var b := biome_at(c)
	return 0 if b == WorldGen.Biome.GRASSLAND or b == WorldGen.Biome.FOREST or b == WorldGen.Biome.LAKES else 1


func area_name(c: Vector2i) -> String:
	var town := gen.town_at(c)
	if not town.is_empty():
		return town["name"]
	var place := gen.place_at(c, 6)
	if not place.is_empty():
		return place["name"]
	var rd := gen.route_distance(c)
	if rd.x < 8.0:
		return "%d号道路" % int(rd.y)
	if biome_at(c) == WorldGen.Biome.OCEAN:
		return "奈尔斯海"
	return WorldPlan.REGIONS[gen.region_index(c.x, c.y)]["name"]


## 某个城镇治疗所的门口（全灭后送回这里）
func heal_exit(town_id: String) -> Vector2i:
	for b in gen.buildings:
		if b["kind"] == "heal" and b["town"] == town_id:
			return b["exit"]
	return WorldGen.START_ORIGIN + Vector2i(6, 6)
