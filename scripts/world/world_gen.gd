class_name WorldGen
extends RefCounted
## 14080x14080 大地图的确定性生成。同一个格子每次算出来都一样，所以地图不用存盘，
## 按 16x16 的区块随用随算（World 负责缓存和绘制）。
##
## 每个格子是一个打包的整数：地面 | 覆盖层 | 物件 | 装饰，见 pack()。
## 地形由三层决定：
## 1. 区域：坐标经噪声扰动后，离哪个 WorldPlan.REGIONS 的中心最近就属于哪个区域（地貌类型）；
##    地图外圈和南边是海，海边是沙滩，南海里有小岛。
## 2. 地貌：每种区域有自己的地面、树种、湖泊/河流的样子（熔岩河、冰湖、沼泽水……）、山脊、
##    遭遇草丛和地面装饰。
## 3. 人工：城镇（道路十字、治疗所、商店、道馆、民居、外圈树篱）、道路（沿折线铺路，
##    过水过熔岩时架桥，两侧清出空地并多放草丛）、迷宫入口和地标。起始的晨露镇是手工布局。

enum Biome { GRASSLAND, FOREST, SWAMP, COAST, DESERT, VOLCANO, MOUNTAIN, LAKES, SNOW, OCEAN }

const SIZE := WorldPlan.SIZE
const CHUNK := 16

## 地面，序号与 TerrainAtlas.BASES 一致（序号大的在过渡时盖住序号小的）
enum { G_SAND, G_MUD, G_ASH, G_ROCK, G_GRASS, G_FOREST, G_SNOW }
## 覆盖层。O_TALL + 区域序号 是该区域的遭遇草丛
enum { O_NONE, O_PATH, O_WATER, O_DEEP, O_LAVA, O_BOG, O_ICE, O_BRIDGE, O_TALL }
const OVERLAY_NAMES := ["", "path", "water", "deep", "lava", "bog", "ice", "bridge"]
const TALL_NAMES := ["tall_grass", "tall_forest", "tall_swamp", "tall_coast", "tall_desert",
	"tall_volcano", "tall_mountain", "tall_lakes", "tall_snow"]
## 物件（都挡路）。BUILDING 是房屋占的格子，房屋本身由 World 单独放置
const PROPS := ["", "tree_oak", "tree_round", "tree_forest", "tree_pine", "tree_snowpine", "tree_palm",
	"cactus", "tree_dead", "tree_swamp", "tree_autumn", "bush", "boulder", "rock_volcanic", "rock_desert",
	"ice_crystal", "reeds", "cave", "sign", "monument"]
const BUILDING := 255
## 地面装饰（能走过去），与 tools/gen_terrain.py 的 DECOR 顺序一致
const DECOR := ["", "flower_r", "flower_y", "flower_w", "flower_b", "pebbles", "mushroom", "shell",
	"dry_bush", "ember", "lily", "snow_tuft", "bones"]

## 各区域的地貌参数
## tree: 基础树木密度；grove: 树林噪声额外加的密度；lake/lake_t: 湖泊类型与阈值（越小湖越多）；
## river: 河流类型（O_NONE 表示没有）；ridge: 山脊岩石；tall_t: 草丛阈值
const BIOME_INFO := [
	{"ground": G_GRASS, "trees": ["tree_oak", "tree_round", "tree_oak", "bush"], "tree": 0.012, "grove": 0.3,
		"lake": O_WATER, "lake_t": 0.5, "river": O_WATER, "ridge": "", "rock": "boulder", "rocks": 0.002,
		"tall_t": 0.3, "decor": ["flower_r", "flower_y", "flower_w", "flower_b"], "decor_p": 0.05},
	{"ground": G_FOREST, "trees": ["tree_forest", "tree_forest", "tree_oak", "tree_round", "tree_autumn"],
		"tree": 0.3, "grove": 0.25, "lake": O_WATER, "lake_t": 0.58, "river": O_WATER, "ridge": "",
		"rock": "boulder", "rocks": 0.004, "tall_t": 0.28, "decor": ["mushroom", "flower_w", "pebbles"], "decor_p": 0.06},
	{"ground": G_MUD, "trees": ["tree_swamp", "tree_swamp", "tree_dead", "reeds", "reeds"], "tree": 0.05,
		"grove": 0.2, "lake": O_BOG, "lake_t": 0.3, "river": O_BOG, "ridge": "", "rock": "", "rocks": 0.0,
		"tall_t": 0.25, "decor": ["mushroom", "lily", "bones"], "decor_p": 0.05},
	{"ground": G_SAND, "trees": ["tree_palm", "tree_palm", "bush"], "tree": 0.015, "grove": 0.12,
		"lake": O_WATER, "lake_t": 0.52, "river": O_WATER, "ridge": "", "rock": "boulder", "rocks": 0.003,
		"tall_t": 0.32, "decor": ["shell", "shell", "pebbles"], "decor_p": 0.04},
	{"ground": G_SAND, "trees": ["cactus", "cactus", "rock_desert"], "tree": 0.012, "grove": 0.03,
		"lake": O_WATER, "lake_t": 0.72, "river": O_NONE, "ridge": "rock_desert", "rock": "rock_desert",
		"rocks": 0.004, "tall_t": 0.36, "decor": ["dry_bush", "bones", "pebbles"], "decor_p": 0.03},
	{"ground": G_ASH, "trees": ["tree_dead", "rock_volcanic"], "tree": 0.02, "grove": 0.05,
		"lake": O_LAVA, "lake_t": 0.48, "river": O_LAVA, "ridge": "rock_volcanic", "rock": "rock_volcanic",
		"rocks": 0.01, "tall_t": 0.33, "decor": ["ember", "ember", "pebbles"], "decor_p": 0.05},
	{"ground": G_ROCK, "trees": ["tree_pine", "tree_pine", "boulder"], "tree": 0.03, "grove": 0.3,
		"lake": O_WATER, "lake_t": 0.62, "river": O_WATER, "ridge": "boulder", "rock": "boulder",
		"rocks": 0.012, "tall_t": 0.3, "decor": ["pebbles", "pebbles", "flower_w"], "decor_p": 0.05},
	{"ground": G_GRASS, "trees": ["tree_oak", "tree_autumn", "tree_round", "reeds"], "tree": 0.015, "grove": 0.25,
		"lake": O_WATER, "lake_t": 0.16, "river": O_WATER, "ridge": "", "rock": "boulder", "rocks": 0.002,
		"tall_t": 0.3, "decor": ["flower_b", "flower_w", "lily"], "decor_p": 0.05},
	{"ground": G_SNOW, "trees": ["tree_snowpine", "tree_snowpine", "ice_crystal"], "tree": 0.03, "grove": 0.28,
		"lake": O_ICE, "lake_t": 0.48, "river": O_ICE, "ridge": "ice_crystal", "rock": "ice_crystal",
		"rocks": 0.004, "tall_t": 0.32, "decor": ["snow_tuft", "snow_tuft", "pebbles"], "decor_p": 0.05},
]

## 起始小镇（手工布局）在大地图上的左上角，及其中的房屋和出口
const START_ORIGIN := WorldPlan.START_ORIGIN
const START_SIZE := Vector2i(48, 36)
const START_HOUSES := [
	{"rect": Rect2i(4, 3, 4, 3), "kind": "heal"},
	{"rect": Rect2i(11, 3, 4, 3), "kind": "shop"},
	{"rect": Rect2i(3, 10, 4, 3), "kind": "home"},
]
## 起始小镇往北（1号道路）和往东（2号道路）的出口，局部坐标
const START_EXIT_N := Vector2i(24, 0)
const START_EXIT_E := Vector2i(47, 7)

var _warp_x := FastNoiseLite.new()
var _warp_y := FastNoiseLite.new()
var _coast := FastNoiseLite.new()
var _lake := FastNoiseLite.new()
var _river := FastNoiseLite.new()
var _patch := FastNoiseLite.new()
var _grove := FastNoiseLite.new()
var _ridge := FastNoiseLite.new()
var _detail := FastNoiseLite.new()

## 城镇、道路、地点预先算好的格子：Vector2i -> 打包值
var special := {}
## 城镇范围：[{"town", "center", "radius"}]
var town_areas: Array = []
## 道路折线段：[{"a": Vector2, "b": Vector2, "route": 编号}]
var route_segments: Array = []
## 房屋：[{"rect": Rect2i（世界坐标）, "kind", "town", "door": Vector2i, "exit": Vector2i}]
var buildings: Array = []
var _pending: Array[Vector2i] = []
var _finished := 0


func _init() -> void:
	_setup_noise(_warp_x, 11, 1.0 / 1260.0, 3)
	_setup_noise(_warp_y, 12, 1.0 / 1260.0, 3)
	_setup_noise(_coast, 13, 1.0 / 400.0, 3)
	_setup_noise(_lake, 14, 1.0 / 90.0, 3)
	_setup_noise(_river, 15, 1.0 / 700.0, 2)
	_setup_noise(_patch, 16, 1.0 / 14.0, 2)
	_setup_noise(_grove, 17, 1.0 / 45.0, 2)
	_setup_noise(_ridge, 18, 1.0 / 160.0, 3)
	_setup_noise(_detail, 19, 1.0 / 25.0, 2)
	_build_routes()
	_build_start_town()
	for t in WorldPlan.TOWNS:
		if t["kind"] != "start":
			_build_town(t)
	for p in WorldPlan.PLACES:
		_build_place(p)


func _setup_noise(n: FastNoiseLite, s: int, freq: float, octaves: int) -> void:
	n.seed = 20261028 + s
	n.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	n.frequency = freq
	n.fractal_type = FastNoiseLite.FRACTAL_FBM
	n.fractal_octaves = octaves


static func pack(ground: int, overlay := O_NONE, obj := 0, decor := 0) -> int:
	return ground | (overlay << 4) | (obj << 9) | (decor << 17)


static func ground_of(v: int) -> int:
	return v & 15


static func overlay_of(v: int) -> int:
	return (v >> 4) & 31


static func object_of(v: int) -> int:
	return (v >> 9) & 255


static func decor_of(v: int) -> int:
	return (v >> 17) & 31


static func is_tall(v: int) -> bool:
	return overlay_of(v) >= O_TALL


static func walkable(v: int) -> bool:
	if object_of(v) != 0:
		return false
	var o := overlay_of(v)
	return not (o == O_WATER or o == O_DEEP or o == O_LAVA or o == O_BOG)


static func prop_id(prop_name: String) -> int:
	return PROPS.find(prop_name)


static func _hash(x: int, y: int, s: int) -> float:
	var h := (x * 374761393 + y * 668265263 + s * 982451653) & 0x7FFFFFFF
	h = ((h ^ (h >> 13)) * 1274126177) & 0x7FFFFFFF
	return float(h ^ (h >> 16)) / float(0x7FFFFFFF)


# ---------------------------------------------------------------- 区域
## 海的远近：小于 0 是海，越小越深
func ocean_metric(x: int, y: int) -> float:
	var edge := float(mini(mini(x, y), mini(SIZE - 1 - x, SIZE - 1 - y))) - SIZE * 0.033
	var south := SIZE * 0.865 - y
	var m := minf(edge, south) + _coast.get_noise_2d(x, y) * 190.0
	# 南海里的小岛
	if m < 0.0 and m > -600.0:
		var isle := _lake.get_noise_2d(x * 0.12 + 9000.0, y * 0.12)
		if isle > 0.4:
			m = (isle - 0.4) * 300.0
	return m


func region_index(x: int, y: int) -> int:
	var wx := x + _warp_x.get_noise_2d(x, y) * 590.0
	var wy := y + _warp_y.get_noise_2d(x, y) * 590.0
	var best := 0
	var best_d := INF
	for i in WorldPlan.REGIONS.size():
		var c: Vector2i = WorldPlan.REGIONS[i]["center"]
		var d := (wx - c.x) * (wx - c.x) + (wy - c.y) * (wy - c.y)
		if d < best_d:
			best_d = d
			best = i
	return best


## 地貌类型（Biome），海里返回 OCEAN
func biome_at(x: int, y: int) -> int:
	var m := ocean_metric(x, y)
	if m < 0.0:
		return Biome.OCEAN
	var b: int = WorldPlan.REGIONS[region_index(x, y)]["biome"]
	if m < 24.0 and b != Biome.SNOW and b != Biome.VOLCANO:
		return Biome.COAST
	return b


# ---------------------------------------------------------------- 道路
func _route_end(town_id: String, other: Vector2i) -> Vector2:
	for t in WorldPlan.TOWNS:
		if t["id"] == town_id:
			if t["kind"] == "start":
				var p: Vector2i = t["pos"]
				var exit := START_EXIT_N if other.y < p.y - 300 else START_EXIT_E
				return Vector2(START_ORIGIN + exit)
			return Vector2(t["pos"])
	return Vector2.ZERO


func _town_pos(town_id: String) -> Vector2i:
	for t in WorldPlan.TOWNS:
		if t["id"] == town_id:
			return t["pos"]
	return Vector2i.ZERO


func _build_routes() -> void:
	for r in WorldPlan.ROUTES:
		var a := _route_end(r[1], _town_pos(r[2]))
		var b := _route_end(r[2], _town_pos(r[1]))
		var n := int(r[0])
		# 折线：中间 5 个点垂直于主方向随机偏移，道路弯弯曲曲
		var dir := (b - a).normalized()
		var side := Vector2(-dir.y, dir.x)
		var length := a.distance_to(b)
		var pts: Array[Vector2] = [a]
		var steps := 6
		for i in range(1, steps):
			var t := float(i) / steps
			var off := (_hash(n, i, 7) - 0.5) * length * 0.16
			pts.append((a.lerp(b, t) + side * off).round())
		pts.append(b)
		for i in pts.size() - 1:
			route_segments.append({"a": pts[i], "b": pts[i + 1], "route": n})


static func _seg_dist(p: Vector2, a: Vector2, b: Vector2) -> float:
	var ab := b - a
	var t := clampf((p - a).dot(ab) / maxf(ab.length_squared(), 0.0001), 0.0, 1.0)
	return p.distance_to(a + ab * t)


## 离最近道路的距离和道路编号（只看 near 里的线段）
func route_distance(c: Vector2i, near: Array = route_segments) -> Vector2:
	var p := Vector2(c)
	var best := INF
	var num := 0
	for s in near:
		var d := _seg_dist(p, s["a"], s["b"])
		if d < best:
			best = d
			num = s["route"]
	return Vector2(best, num)


func _segments_near(rect: Rect2i, margin: float) -> Array:
	var out: Array = []
	var r := Rect2(rect).grow(margin)
	for s in route_segments:
		var sr := Rect2(s["a"], Vector2.ZERO).expand(s["b"])
		if r.intersects(sr.grow(1.0)):
			out.append(s)
	return out


# ---------------------------------------------------------------- 城镇与地点
func _add_building(rect: Rect2i, kind: String, town: String) -> void:
	var door := Vector2i(rect.position.x + rect.size.x / 2, rect.end.y - 1)
	buildings.append({"rect": rect, "kind": kind, "town": town, "door": door, "exit": door + Vector2i.DOWN})
	for y in range(rect.position.y, rect.end.y):
		for x in range(rect.position.x, rect.end.x):
			special[Vector2i(x, y)] = -1  # 占位，_finish_buildings 统一换成真正的值
			_pending.append(Vector2i(x, y))
	special[door] = -2


func _build_start_town() -> void:
	# 与旧版单张地图相同的布局和随机种子，坐标整体平移到 START_ORIGIN
	var rng := RandomNumberGenerator.new()
	rng.seed = 20261027
	var w := START_SIZE.x
	var h := START_SIZE.y
	var g := PackedInt32Array()
	g.resize(w * h)
	g.fill(pack(G_GRASS))
	var tall := pack(G_GRASS, O_TALL + Biome.GRASSLAND)
	for patch in [Rect2i(12, 9, 8, 7), Rect2i(38, 9, 7, 10), Rect2i(11, 22, 10, 6), Rect2i(24, 22, 10, 6), Rect2i(38, 22, 7, 6)]:
		for y in range(patch.position.y, patch.end.y):
			for x in range(patch.position.x, patch.end.x):
				if rng.randf() < 0.88:
					g[y * w + x] = tall
	for y in h:
		for x in w:
			var dx := (x - 28) / 4.6
			var dy := (y - 16) / 3.2
			var d := dx * dx + dy * dy
			if d < 1.0:
				g[y * w + x] = pack(G_GRASS, O_DEEP if d < 0.35 else O_WATER)
	var path := pack(G_GRASS, O_PATH)
	for road in [Rect2i(3, 7, 42, 1), Rect2i(9, 7, 1, 24), Rect2i(36, 7, 1, 24), Rect2i(9, 30, 28, 1),
			Rect2i(24, 0, 1, 7), Rect2i(44, 7, 4, 1)]:
		for y in range(road.position.y, road.end.y):
			for x in range(road.position.x, road.end.x):
				rng.randf()
				g[y * w + x] = path
	var oak := prop_id("tree_oak")
	var round_tree := prop_id("tree_round")
	for y in h:
		for x in w:
			var i := y * w + x
			var border := x < 2 or y < 2 or x >= w - 2 or y >= h - 2
			if border and overlay_of(g[i]) != O_PATH:
				g[i] = pack(G_GRASS, O_NONE, oak if (x + y) % 3 else round_tree)
				continue
			if g[i] != pack(G_GRASS):
				continue
			var r := rng.randf()
			if not (x < 18 and y < 15) and r < 0.05:
				g[i] = pack(G_GRASS, O_NONE, round_tree if (x * 7 + y) % 4 == 0 else oak)
			elif r < 0.11:
				g[i] = pack(G_GRASS, O_NONE, 0, 1 + (x + y) % 3)
	for y in h:
		for x in w:
			special[START_ORIGIN + Vector2i(x, y)] = g[y * w + x]
	for hs in START_HOUSES:
		var r: Rect2i = hs["rect"]
		_add_building(Rect2i(START_ORIGIN + r.position, r.size), hs["kind"], "chenlu")
	# NPC 脚下保证是空地
	for n in World.NPCS:
		var nc: Vector2i = START_ORIGIN + Vector2i(n["cell"])
		special[nc] = pack(G_GRASS)
		# 头顶那格的树会挡住 NPC
		if object_of(special[nc + Vector2i.UP]) != 0:
			special[nc + Vector2i.UP] = pack(G_GRASS)
	_finish_buildings(G_GRASS)


func _finish_buildings(ground: int) -> void:
	for c in _pending:
		if special[c] == -1:
			special[c] = pack(ground, O_NONE, BUILDING)
		elif special[c] == -2:
			special[c] = pack(ground, O_PATH)
	# 只处理这一批新加的房屋，免得后面的城镇把前面城镇门口的地面改掉
	for i in range(_finished, buildings.size()):
		var e: Vector2i = buildings[i]["exit"]
		if not special.has(e):
			special[e] = pack(ground, O_PATH)
		elif object_of(special[e]) == 0:
			special[e] = pack(ground_of(special[e]), O_PATH)
	_finished = buildings.size()
	_pending.clear()


func town_radius(t: Dictionary) -> int:
	match t["kind"]:
		"city":
			return 22
		"league":
			return 16
	return 17


func _build_town(t: Dictionary) -> void:
	var c: Vector2i = t["pos"]
	var r := town_radius(t)
	town_areas.append({"town": t, "center": c, "radius": r})
	var ground: int = BIOME_INFO[WorldPlan.REGIONS[region_index(c.x, c.y)]["biome"]]["ground"]
	if ground == G_MUD or ground == G_ASH or ground == G_ROCK:
		ground = G_GRASS if ground == G_MUD else G_ROCK
	var id: String = t["id"]
	var path := pack(ground, O_PATH)
	# 主干道十字，宽 3 格
	for i in range(-r + 2, r - 1):
		for k in range(-1, 2):
			special[c + Vector2i(i, k)] = path
			special[c + Vector2i(k, i)] = path
	var rects: Array = []
	if t["kind"] == "league":
		rects = [[Rect2i(-4, -9, 8, 5), "league"], [Rect2i(-10, 3, 4, 3), "heal"], [Rect2i(6, 3, 4, 3), "shop"]]
	else:
		rects = [[Rect2i(-10, -6, 4, 3), "heal"], [Rect2i(6, -6, 4, 3), "shop"],
			[Rect2i(-11, 4, 4, 3), "home"], [Rect2i(7, 4, 4, 3), "home"]]
		if t["kind"] == "city":
			rects += [[Rect2i(-3, -16, 6, 4), "gym"], [Rect2i(-16, -6, 4, 3), "home"], [Rect2i(12, 4, 4, 3), "home"]]
		else:
			rects += [[Rect2i(-5, 9, 4, 3), "home"]]
	for e in rects:
		var rr: Rect2i = e[0]
		var world_rect := Rect2i(c + rr.position, rr.size)
		_add_building(world_rect, e[1], id)
		# 门口的小路接到主干道
		var exit_cell := Vector2i(world_rect.position.x + world_rect.size.x / 2, world_rect.end.y)
		var step := 1 if exit_cell.x < c.x else -1
		var x := exit_cell.x
		while x != c.x - step * 2 and abs(x - c.x) > 1:
			special[Vector2i(x, exit_cell.y)] = path
			x += step
	# 路牌
	special[c + Vector2i(3, 3)] = pack(ground, O_NONE, prop_id("sign"))
	_finish_buildings(ground)


func _build_place(p: Dictionary) -> void:
	var c: Vector2i = p["pos"]
	var b := biome_at(c.x, c.y)
	var ground: int = BIOME_INFO[b]["ground"] if b < Biome.OCEAN else G_SAND
	for y in range(-3, 4):
		for x in range(-3, 4):
			special[c + Vector2i(x, y)] = pack(ground)
	special[c] = pack(ground, O_NONE, prop_id("cave" if p["kind"] == "dungeon" else "monument"))
	special[c + Vector2i(1, 2)] = pack(ground, O_NONE, prop_id("sign"))


func town_at(c: Vector2i) -> Dictionary:
	if Rect2i(START_ORIGIN, START_SIZE).has_point(c):
		return WorldPlan.TOWNS[0]
	for a in town_areas:
		var d: Vector2i = c - a["center"]
		if d.x * d.x + d.y * d.y <= a["radius"] * a["radius"]:
			return a["town"]
	return {}


func place_at(c: Vector2i, radius := 4) -> Dictionary:
	for p in WorldPlan.PLACES:
		var d: Vector2i = c - p["pos"]
		if abs(d.x) <= radius and abs(d.y) <= radius:
			return p
	return {}


# ---------------------------------------------------------------- 区块
func generate_chunk(chunk: Vector2i) -> PackedInt32Array:
	var out := PackedInt32Array()
	out.resize(CHUNK * CHUNK)
	var origin := chunk * CHUNK
	var near := _segments_near(Rect2i(origin, Vector2i(CHUNK, CHUNK)), 16.0)
	var towns: Array = []
	for a in town_areas:
		var d: Vector2i = (origin + Vector2i(8, 8)) - a["center"]
		if d.length() < a["radius"] + 16:
			towns.append(a)
	var start_rect := Rect2i(START_ORIGIN, START_SIZE)
	for ly in CHUNK:
		for lx in CHUNK:
			var c := origin + Vector2i(lx, ly)
			out[ly * CHUNK + lx] = _cell(c, near, towns, start_rect)
	return out


## 单独查一个格子（鸟瞰图采样用；游戏里走 generate_chunk 更快）
func sample_cell(c: Vector2i) -> int:
	var near := _segments_near(Rect2i(c, Vector2i.ONE), 16.0)
	var towns: Array = []
	for a in town_areas:
		var d: Vector2i = c - a["center"]
		if d.length() < a["radius"] + 16:
			towns.append(a)
	return _cell(c, near, towns, Rect2i(START_ORIGIN, START_SIZE))


func _cell(c: Vector2i, near: Array, towns: Array, start_rect: Rect2i) -> int:
	var x := c.x
	var y := c.y
	if x < 0 or y < 0 or x >= SIZE or y >= SIZE:
		return pack(G_SAND, O_DEEP)
	if special.has(c):
		return special[c]
	if start_rect.has_point(c):
		return pack(G_GRASS)
	var m := ocean_metric(x, y)
	var rd := route_distance(c, near).x if not near.is_empty() else INF
	if m < 0.0:
		if rd < 1.6 and m > -60.0:
			return pack(G_SAND, O_BRIDGE)
		return pack(G_SAND, O_DEEP if m < -28.0 else O_WATER)
	var region := region_index(x, y)
	var b: int = WorldPlan.REGIONS[region]["biome"]
	if m < 24.0 and b != Biome.SNOW and b != Biome.VOLCANO:
		b = Biome.COAST
	var info: Dictionary = BIOME_INFO[b]
	var ground: int = info["ground"]
	var detail := _detail.get_noise_2d(x, y)
	if b == Biome.COAST and m > 14.0 and detail > 0.15:
		ground = G_GRASS
	elif b == Biome.MOUNTAIN and detail > 0.35:
		ground = G_GRASS
	elif b == Biome.DESERT and _ridge.get_noise_2d(x, y) > 0.38:
		ground = G_ROCK  # 风蚀岩地
	elif b == Biome.SWAMP and detail < -0.3:
		ground = G_GRASS

	# 城镇：内部空地，外圈一圈树篱（道路穿过的地方留口）
	for a in towns:
		var d := Vector2(c - a["center"]).length()
		var r: float = a["radius"]
		if d <= r:
			if d > r - 2.0 and rd > 2.5:
				var trees: Array = info["trees"]
				return pack(ground, O_NONE, prop_id(trees[int(_hash(x, y, 3) * trees.size())]))
			if rd < 1.4:
				return pack(ground, O_PATH)
			return pack(ground, O_NONE, 0, _decor(x, y, info, 0.5))

	var overlay := O_NONE
	# 湖泊（深处是深水）、河流
	var lake := _lake.get_noise_2d(x, y)
	if b == Biome.LAKES:
		lake = _lake.get_noise_2d(x * 0.4 + 7000.0, y * 0.4)  # 湖区的湖更大更连片
	var lake_t: float = info["lake_t"]
	if lake > lake_t:
		overlay = info["lake"]
		if overlay == O_WATER and lake > lake_t + 0.14:
			overlay = O_DEEP
	elif info["river"] != O_NONE:
		var rv := absf(_river.get_noise_2d(x + 3000, y))
		if rv < 0.016:
			overlay = info["river"]
	# 温泉：火山区偶尔有一汪清水
	if b == Biome.VOLCANO and overlay == O_NONE and _lake.get_noise_2d(x + 5000, y) > 0.62:
		overlay = O_WATER

	# 道路：铺路，遇水架桥，两侧清空
	if rd < 1.4:
		if overlay != O_NONE and overlay != O_ICE:
			return pack(ground, O_BRIDGE)
		return pack(ground, O_PATH)
	if overlay != O_NONE:
		var dec := DECOR.find("lily") if overlay == O_BOG and _hash(x, y, 9) < 0.06 else 0
		return pack(ground, overlay, 0, dec)
	if rd < 3.0:
		return pack(ground, O_NONE, 0, _decor(x, y, info, 0.3))

	# 山脊：成片的岩石，像天然的墙
	var ridge_name: String = info["ridge"]
	if ridge_name != "":
		var rg := _ridge.get_noise_2d(x * 1.7, y * 1.7)
		var fill := 0.85 if b == Biome.MOUNTAIN or b == Biome.SNOW else 0.45
		if rg > 0.42 and _hash(x, y, 4) < fill:
			return pack(ground, O_NONE, prop_id(ridge_name))

	# 遭遇草丛：靠近道路的地方更多
	var tall_t: float = info["tall_t"]
	if rd < 14.0:
		tall_t -= 0.18
	if _patch.get_noise_2d(x, y) > tall_t:
		return pack(ground, O_TALL + b)

	# 树木：基础密度 + 树林噪声
	var grove := _grove.get_noise_2d(x, y)
	var p: float = info["tree"] + maxf(0.0, grove) * float(info["grove"])
	if b == Biome.FOREST and grove < -0.25:
		p = 0.02  # 林间空地
	var h := _hash(x, y, 1)
	if h < p:
		var trees: Array = info["trees"]
		return pack(ground, O_NONE, prop_id(trees[int(_hash(x, y, 2) * trees.size())]))
	if info["rock"] != "" and h < p + float(info["rocks"]):
		return pack(ground, O_NONE, prop_id(info["rock"]))
	return pack(ground, O_NONE, 0, _decor(x, y, info, 1.0))


func _decor(x: int, y: int, info: Dictionary, scale: float) -> int:
	if _hash(x, y, 5) < float(info["decor_p"]) * scale:
		var list: Array = info["decor"]
		return DECOR.find(list[int(_hash(x, y, 6) * list.size())])
	return 0


## 整张地图的一个采样点在鸟瞰图上的颜色（用于导出全图）
static func overview_color(v: int) -> Color:
	var obj := object_of(v)
	if obj == BUILDING:
		return Color("#c0504d")
	var o := overlay_of(v)
	match o:
		O_PATH, O_BRIDGE:
			return Color("#d9bc85")
		O_WATER:
			return Color("#47a0dc")
		O_DEEP:
			return Color("#2a68ad")
		O_LAVA:
			return Color("#ff7a1a")
		O_BOG:
			return Color("#455d3e")
		O_ICE:
			return Color("#bfe4f3")
	if obj != 0:
		var pn: String = PROPS[obj]
		if pn.begins_with("tree") or pn == "cactus" or pn == "bush" or pn == "reeds":
			return Color("#2b5a2e") if pn != "tree_snowpine" else Color("#4a6a62")
		return Color("#6a6460")
	var gcol := [Color("#e8cf98"), Color("#5a653b"), Color("#4a3f3d"), Color("#938b80"),
		Color("#6fb85a"), Color("#467f43"), Color("#e2eaf4")]
	var col: Color = gcol[ground_of(v)]
	if o >= O_TALL:
		col = col.darkened(0.18)
	return col
