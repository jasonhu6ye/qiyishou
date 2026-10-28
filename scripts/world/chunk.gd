class_name Chunk
extends Node2D
## 一个 16x16 格的区块的地面绘制。分两层：
## - 本节点：基础地面、地面之间的过渡、道路、冰面、地面装饰（不动，只画一次）；
## - anim 子节点：水、深水、熔岩、沼泽水、桥、遭遇草丛（有动画，换帧时重画）。
## 覆盖层用四分之一自动拼接：每格拆成 4 个 8x8，按相邻格是否同类选 5 种情况之一，
## 规则与 tools/gen_terrain.py 生成图集时一致。

const T := 16
const N := WorldGen.CHUNK
const SIDES := [Vector2i(0, -1), Vector2i(0, 1), Vector2i(-1, 0), Vector2i(1, 0)]
const CORNERS := [Vector2i(-1, -1), Vector2i(1, -1), Vector2i(-1, 1), Vector2i(1, 1)]
const QUARTERS := [Vector2i(0, 0), Vector2i(1, 0), Vector2i(0, 1), Vector2i(1, 1)]
const LIQUIDS := [WorldGen.O_WATER, WorldGen.O_DEEP, WorldGen.O_LAVA, WorldGen.O_BOG]

var world: World
var coord := Vector2i.ZERO
var anim: AnimLayer
var has_anim := false


class AnimLayer:
	extends Node2D
	var chunk: Chunk

	func _draw() -> void:
		chunk.draw_anim(self)


func setup(w: World, c: Vector2i) -> void:
	world = w
	coord = c
	position = Vector2(c * N * T)
	anim = AnimLayer.new()
	anim.chunk = self
	add_child(anim)
	var data := world.chunk_data(c)
	for v in data:
		var o := WorldGen.overlay_of(v)
		if LIQUIDS.has(o) or o == WorldGen.O_BRIDGE or o >= WorldGen.O_TALL:
			has_anim = true
			break


func _cell(lx: int, ly: int) -> int:
	return world.cell(coord * N + Vector2i(lx, ly))


static func _hash(x: int, y: int) -> int:
	var h := (x * 73856093) ^ (y * 19349663)
	return absi(h) % 4


func _draw() -> void:
	var tex := Art.tex("terrain")
	var bases := TerrainAtlas.BASES
	for ly in N:
		for lx in N:
			var v := _cell(lx, ly)
			var g := WorldGen.ground_of(v)
			var o := Vector2(lx * T, ly * T)
			var by: int = TerrainAtlas.BASE_Y[bases[g]]
			var wx := coord.x * N + lx
			var wy := coord.y * N + ly
			draw_texture_rect_region(tex, Rect2(o, Vector2(T, T)), Rect2(_hash(wx, wy) * T, by, T, T))
			_draw_transitions(tex, lx, ly, g, o)
			var ov := WorldGen.overlay_of(v)
			if ov == WorldGen.O_PATH:
				_quarters(self, tex, lx, ly, "path", 0, o)
			elif ov == WorldGen.O_ICE:
				_quarters(self, tex, lx, ly, "ice", 0, o)
			var d := WorldGen.decor_of(v)
			if d != 0 and WorldGen.DECOR[d] != "lily":
				_single(self, tex, "decor_" + WorldGen.DECOR[d], o)


## 序号更大的相邻地面漫进本格：四边贴边缘片，只在斜角相邻时贴角片
func _draw_transitions(tex: Texture2D, lx: int, ly: int, g: int, o: Vector2) -> void:
	var around: Array[int] = []
	var higher: Array[int] = []
	for d in SIDES + CORNERS:
		var ng := WorldGen.ground_of(_cell(lx + d.x, ly + d.y))
		around.append(ng)
		if ng > g and not higher.has(ng):
			higher.append(ng)
	higher.sort()
	for h in higher:
		var by: int = TerrainAtlas.BASE_Y[TerrainAtlas.BASES[h]]
		for i in 4:
			if around[i] == h:
				draw_texture_rect_region(tex, Rect2(o, Vector2(T, T)), Rect2((4 + i) * T, by, T, T))
		for i in 4:
			var d: Vector2i = CORNERS[i]
			# 角上的邻居是 h，且挨着它的两条边都不是 h，才需要补角
			var vert := 0 if d.y < 0 else 1
			var hor := 2 if d.x < 0 else 3
			if around[4 + i] == h and around[vert] != h and around[hor] != h:
				draw_texture_rect_region(tex, Rect2(o, Vector2(T, T)), Rect2((8 + i) * T, by, T, T))


static func _same(o: int, n: int) -> bool:
	match o:
		WorldGen.O_WATER:
			return n == WorldGen.O_WATER or n == WorldGen.O_DEEP or n == WorldGen.O_BRIDGE
		WorldGen.O_LAVA, WorldGen.O_BOG:
			return n == o or n == WorldGen.O_BRIDGE
		WorldGen.O_PATH:
			return n == o or n == WorldGen.O_BRIDGE
	return n == o


func _quarters(ci: CanvasItem, tex: Texture2D, lx: int, ly: int, block: String, frame: int, o: Vector2, kind := -1) -> void:
	var frames: Array = TerrainAtlas.OVERLAY[block]
	var b: Vector2i = frames[frame % frames.size()]
	var me := kind if kind >= 0 else WorldGen.overlay_of(_cell(lx, ly))
	for q in 4:
		var qd: Vector2i = QUARTERS[q]
		var vy := -1 if qd.y == 0 else 1
		var hx := -1 if qd.x == 0 else 1
		var vs := _same(me, WorldGen.overlay_of(_cell(lx, ly + vy)))
		var hs := _same(me, WorldGen.overlay_of(_cell(lx + hx, ly)))
		var ds := _same(me, WorldGen.overlay_of(_cell(lx + hx, ly + vy)))
		var c := 3
		if vs and hs:
			c = 0 if ds else 4
		elif vs:
			c = 2
		elif hs:
			c = 1
		ci.draw_texture_rect_region(tex, Rect2(o + Vector2(qd * 8), Vector2(8, 8)),
			Rect2(b.x + q * 8, b.y + c * 8, 8, 8))


static func _single(ci: CanvasItem, tex: Texture2D, single_name: String, o: Vector2) -> void:
	var p: Vector2i = TerrainAtlas.SINGLE[single_name]
	ci.draw_texture_rect_region(tex, Rect2(o, Vector2(T, T)), Rect2(p.x, p.y, T, T))


## 桥下面是什么液体：看四周第一个液体格
func _under_bridge(lx: int, ly: int) -> int:
	for d in SIDES:
		var n := WorldGen.overlay_of(_cell(lx + d.x, ly + d.y))
		if LIQUIDS.has(n) and n != WorldGen.O_DEEP:
			return n
	return WorldGen.O_WATER


func draw_anim(layer: CanvasItem) -> void:
	if not has_anim:
		return
	var tex := Art.tex("terrain")
	var f3 := world.frame % 3
	var f2 := (world.frame / 2) % 2
	for ly in N:
		for lx in N:
			var v := _cell(lx, ly)
			var ov := WorldGen.overlay_of(v)
			if ov == WorldGen.O_NONE or ov == WorldGen.O_PATH or ov == WorldGen.O_ICE:
				continue
			var o := Vector2(lx * T, ly * T)
			match ov:
				WorldGen.O_WATER:
					_quarters(layer, tex, lx, ly, "water", f3, o)
				WorldGen.O_DEEP:
					_quarters(layer, tex, lx, ly, "water", f3, o, WorldGen.O_WATER)
					_quarters(layer, tex, lx, ly, "deep", f3, o)
				WorldGen.O_LAVA:
					_quarters(layer, tex, lx, ly, "lava", f3, o)
				WorldGen.O_BOG:
					_quarters(layer, tex, lx, ly, "bog", f2, o)
					if WorldGen.DECOR[WorldGen.decor_of(v)] == "lily":
						_single(layer, tex, "decor_lily", o)
				WorldGen.O_BRIDGE:
					var under := _under_bridge(lx, ly)
					var block: String = {WorldGen.O_LAVA: "lava", WorldGen.O_BOG: "bog"}.get(under, "water")
					_quarters(layer, tex, lx, ly, block, f3, o, under)
					var horizontal := _bridgeish(lx - 1, ly) or _bridgeish(lx + 1, ly)
					_single(layer, tex, "bridge_h" if horizontal else "bridge_v", o)
				_:
					if ov >= WorldGen.O_TALL:
						_quarters(layer, tex, lx, ly, WorldGen.TALL_NAMES[ov - WorldGen.O_TALL], f2, o)


func _bridgeish(lx: int, ly: int) -> bool:
	var o := WorldGen.overlay_of(_cell(lx, ly))
	return o == WorldGen.O_BRIDGE or o == WorldGen.O_PATH
