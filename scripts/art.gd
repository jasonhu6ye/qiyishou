class_name Art
extends RefCounted
## 美术入口：所有像素图都在 assets/sprites 下，由 tools/gen_pixel_art.py 生成。

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


## 房屋，原点在房子所占格子的左下角。kind 为 heal / shop / home。
## 贴图 72x60：左右各伸出 4 像素屋檐，屋顶高出格子 12 像素。
static func house(ci: CanvasItem, kind: String) -> void:
	ci.draw_texture(tex("house_" + kind), Vector2(-4, -60))


## 奇异兽立绘，原点在脚底中心（贴图底边往上 5 像素）。正面 64x64，背面 80x80。
static func monster(ci: CanvasItem, key: String, back := false, alpha := 1.0) -> void:
	var t := tex("monsters/%s_%s" % [key, "back" if back else "front"])
	var sz := t.get_size()
	ci.draw_texture(t, Vector2(-sz.x / 2.0, -(sz.y - 5)), Color(1, 1, 1, alpha))


## 头顶的感叹号气泡（训练师发现你时）
static func alert(ci: CanvasItem) -> void:
	ci.draw_rect(Rect2(-4, -31, 8, 10), Color("#2b2b45"))
	ci.draw_rect(Rect2(-3, -30, 6, 8), Color.WHITE)
	ci.draw_rect(Rect2(-1, -29, 2, 4), Color("#d9534f"))
	ci.draw_rect(Rect2(-1, -24, 2, 1), Color("#d9534f"))
