class_name Art
extends RefCounted
## 美术入口：地面、树和人物用 assets/sprites 下的像素图（由 tools/gen_pixel_art.py 生成），
## 房屋和奇异兽暂时还是矢量占位图，在 320x240 下渲染后同样呈像素风。

const CHAR_SIZE := Vector2(16, 20)
const TILE_TALL_FRONT := 8

static var _textures := {}



static func ellipse(ci: CanvasItem, c: Vector2, r: Vector2, col: Color, rot := 0.0) -> void:
	var pts := PackedVector2Array()
	for i in 24:
		var a := TAU * i / 24.0
		pts.append(c + Vector2(cos(a) * r.x, sin(a) * r.y).rotated(rot))
	ci.draw_colored_polygon(pts, col)


static func poly(ci: CanvasItem, pts: Array, col: Color) -> void:
	ci.draw_colored_polygon(PackedVector2Array(pts), col)


static func half_disc(ci: CanvasItem, c: Vector2, r: float, col: Color) -> void:
	var pts := PackedVector2Array()
	for i in 13:
		var a := PI + PI * i / 12.0
		pts.append(c + Vector2(cos(a), sin(a)) * r)
	ci.draw_colored_polygon(pts, col)


static func tex(sprite_name: String) -> Texture2D:
	if not _textures.has(sprite_name):
		_textures[sprite_name] = load("res://assets/sprites/%s.png" % sprite_name)
	return _textures[sprite_name]


## 行走图中朝向对应的行：下、左、右、上
static func _dir_row(dir: Vector2i) -> int:
	if dir == Vector2i.LEFT:
		return 1
	if dir == Vector2i.RIGHT:
		return 2
	if dir == Vector2i.UP:
		return 3
	return 0


## 人物，原点在脚底中心。sheet 为 assets/sprites 下的行走图名，step 为 0/1/2 的走路帧。
static func character(ci: CanvasItem, sheet: String, dir: Vector2i, step: int) -> void:
	ellipse(ci, Vector2(0, -1.5), Vector2(5, 2), Color(0, 0, 0, 0.28))
	var src := Rect2(Vector2(step * CHAR_SIZE.x, _dir_row(dir) * CHAR_SIZE.y), CHAR_SIZE)
	ci.draw_texture_rect_region(tex(sheet), Rect2(Vector2(-8, -18), CHAR_SIZE), src)


## 站在高草里时盖在脚上的草叶
static func tall_grass_front(ci: CanvasItem) -> void:
	ci.draw_texture_rect_region(tex("tiles"), Rect2(-8, -16, 16, 16), Rect2(TILE_TALL_FRONT * 16, 0, 16, 16))


## 树，原点在所在格子的底边中心。树冠高出一格，形成 2.5D 遮挡。
static func tree(ci: CanvasItem) -> void:
	ci.draw_texture(tex("tree"), Vector2(-8, -32))


## 房屋，原点在左下角。size 以像素计。
static func house(ci: CanvasItem, size: Vector2, roof: Color, heal: bool, door_x: float) -> void:
	var w := size.x
	var h := size.y
	var top := -h
	var wall_top := top + h * 0.42
	ci.draw_rect(Rect2(w, wall_top + 4, 4, h * 0.58 - 2), Color(0, 0, 0, 0.2))
	ci.draw_rect(Rect2(0, wall_top, w, h * 0.58), Color("#efe3cb"))
	ci.draw_rect(Rect2(0, -3, w, 3), Color("#cdbb98"))
	poly(ci, [Vector2(-3, wall_top + 2), Vector2(w + 3, wall_top + 2), Vector2(w - 4, top - 9), Vector2(4, top - 9)], roof)
	ci.draw_rect(Rect2(-3, wall_top, w + 6, 3), Color(0, 0, 0, 0.22))
	for i in range(1, 4):
		ci.draw_rect(Rect2(2, top - 9 + i * (wall_top - top + 9) / 4.0, w - 4, 1), Color(1, 1, 1, 0.13))
	var glass := Color("#9fd7f2")
	ci.draw_rect(Rect2(4, wall_top + 6, 8, 6), glass)
	ci.draw_rect(Rect2(w - 12, wall_top + 6, 8, 6), glass)
	if heal:
		ci.draw_rect(Rect2(door_x + 2, -14, 12, 14), glass)
		ci.draw_rect(Rect2(door_x + 7.5, -14, 1, 14), Color("#6aa9c8"))
		var cx := w / 2.0
		ci.draw_rect(Rect2(cx - 4, top - 4, 8, 8), Color.WHITE)
		ci.draw_rect(Rect2(cx - 1, top - 3, 2, 6), Color("#d9534f"))
		ci.draw_rect(Rect2(cx - 3, top - 1, 6, 2), Color("#d9534f"))
	else:
		ci.draw_rect(Rect2(door_x + 3, -13, 10, 13), Color("#7a4f2a"))


## 奇异兽，原点在脚底中心，坐标约在 [-20, 20] x [-32, 2] 内。
## 调用前用 draw_set_transform 设好位置和缩放。
static func monster(ci: CanvasItem, key: String, back := false, alpha := 1.0, t := 0.0) -> void:
	var sp: Dictionary = Data.SPECIES[key]
	var a := Color(sp["col"], alpha)
	var b := Color(sp["col2"], alpha)
	var d := Color(sp["dark"], alpha)
	var eye_dark := Color(0.106, 0.106, 0.169, alpha)
	var bob := Vector2(0, sin(t * 3.0) * 0.8)
	var eyes := [Vector2(-5, -14), Vector2(5, -14)]
	match sp["shape"]:
		"fox":
			ellipse(ci, bob + Vector2(13, -13), Vector2(9, 5), a, -0.7)
			ellipse(ci, bob + Vector2(18, -18), Vector2(4, 3), b, -0.7)
			poly(ci, [bob + Vector2(-11, -18), bob + Vector2(-8, -30), bob + Vector2(-3, -21)], a)
			poly(ci, [bob + Vector2(11, -18), bob + Vector2(8, -30), bob + Vector2(3, -21)], a)
			ellipse(ci, bob + Vector2(0, -12), Vector2(12, 11), a)
			if not back:
				ellipse(ci, bob + Vector2(0, -7), Vector2(7, 4.5), b)
		"frog":
			ellipse(ci, bob + Vector2(-7, -19), Vector2(5, 5), a)
			ellipse(ci, bob + Vector2(7, -19), Vector2(5, 5), a)
			ellipse(ci, bob + Vector2(0, -10), Vector2(15, 10), a)
			if not back:
				ellipse(ci, bob + Vector2(0, -6), Vector2(9, 4.5), b)
			eyes = [Vector2(-7, -20), Vector2(7, -20)]
		"mouse":
			for sx in [-9, 9]:
				ellipse(ci, bob + Vector2(sx, -21), Vector2(5, 5), a)
				ellipse(ci, bob + Vector2(sx, -21), Vector2(2.5, 2.5), b)
			ellipse(ci, bob + Vector2(0, -11), Vector2(11, 11), a)
			ellipse(ci, bob + Vector2(-1, -25), Vector2(2.6, 5.5), Color("#4fb34f", alpha), 0.5)
			ellipse(ci, bob + Vector2(3, -26), Vector2(2, 4), Color("#7bd36b", alpha), -0.6)
			if not back:
				ellipse(ci, bob + Vector2(0, -8), Vector2(2, 1.5), Color("#d77a86", alpha))
		"bird":
			ellipse(ci, bob + Vector2(0, -12), Vector2(12, 12), a)
			ellipse(ci, bob + Vector2(-10, -11), Vector2(4.5, 7), d, 0.3)
			ellipse(ci, bob + Vector2(10, -11), Vector2(4.5, 7), d, -0.3)
			poly(ci, [bob + Vector2(-2, -23), bob + Vector2(0, -30), bob + Vector2(3, -23)], d)
			if not back:
				ellipse(ci, bob + Vector2(0, -6), Vector2(7, 5), b)
				poly(ci, [bob + Vector2(-3, -11), bob + Vector2(3, -11), bob + Vector2(0, -7)], Color("#f2a33a", alpha))
		"worm":
			ellipse(ci, bob + Vector2(-12, -5), Vector2(6, 5), d)
			ellipse(ci, bob + Vector2(-3, -7), Vector2(7, 6.5), a)
			ellipse(ci, bob + Vector2(8, -11), Vector2(9, 9), a)
			ci.draw_line(bob + Vector2(5, -19), bob + Vector2(2, -25), d, 1.3)
			ci.draw_line(bob + Vector2(11, -19), bob + Vector2(14, -25), d, 1.3)
			ellipse(ci, bob + Vector2(2, -25), Vector2(1.6, 1.6), d)
			ellipse(ci, bob + Vector2(14, -25), Vector2(1.6, 1.6), d)
			eyes = [Vector2(4, -12), Vector2(12, -12)]
		"jelly":
			for i in range(-2, 3):
				var pts := PackedVector2Array()
				for s in 7:
					var k := s / 6.0
					pts.append(bob + Vector2(i * 4 + sin(t * 5.0 + i) * 3.0 * sin(k * PI), -9 + k * 10))
				ci.draw_polyline(pts, d, 2.0)
			ellipse(ci, bob + Vector2(0, -14), Vector2(12, 9), a)
			ellipse(ci, bob + Vector2(-4, -18), Vector2(4, 2), b)
			eyes = [Vector2(-4, -13), Vector2(4, -13)]
		"blob":
			ellipse(ci, bob + Vector2(0, -11), Vector2(12, 11), a)
			var flicker := sin(t * 8.0) * 2.0
			poly(ci, [bob + Vector2(-6, -19), bob + Vector2(0, -31 - flicker), bob + Vector2(6, -19)], Color("#ff9b3a", alpha))
			poly(ci, [bob + Vector2(-3, -20), bob + Vector2(0, -26), bob + Vector2(3, -20)], b)
			eyes = [Vector2(-4, -11), Vector2(4, -11)]
	if not back:
		for e in eyes:
			ellipse(ci, bob + e, Vector2(1.8, 2.4), eye_dark)
			ellipse(ci, bob + e + Vector2(0.6, -0.9), Vector2(0.7, 0.7), Color(1, 1, 1, alpha))
