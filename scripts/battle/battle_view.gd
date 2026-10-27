class_name BattleView
extends Control
## 战斗画面。在 320x240 的逻辑坐标里绘制，按控件宽度等比放大；文字按实际像素绘制以保持清晰。

const LOGICAL := Vector2(320, 240)

var battle: Battle
var _k := 1.0


func _draw() -> void:
	var b := battle
	if b == null or b.wild == null:
		return
	_k = size.x / LOGICAL.x
	var t := Battle.now()
	_reset()

	var route2 := b.zone == 1
	var sky_top := Color("#f7b267") if route2 else Color("#8fd3ff")
	var sky_bottom := Color("#ffe8c2") if route2 else Color("#e6f7ff")
	var ground := Color("#b9d27a") if route2 else Color("#9be07a")
	var hills := Color("#c98a5a") if route2 else Color("#8cc7a0")
	var pad := Color("#cfe39a") if route2 else Color("#b8ec97")
	draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(320, 0), Vector2(320, 120), Vector2(0, 120)]),
		PackedColorArray([sky_top, sky_top, sky_bottom, sky_bottom]))
	Art.poly(self, [Vector2(0, 120), Vector2(40, 96), Vector2(90, 110), Vector2(150, 88), Vector2(210, 108),
		Vector2(260, 92), Vector2(320, 104), Vector2(320, 120)], hills)
	draw_rect(Rect2(0, 120, 320, 120), ground)
	for i in 14:
		draw_rect(Rect2((i * 53 + 17) % 320, 128 + (i * 37) % 100, 6, 1.5), Color(0, 0, 0, 0.08))
	Art.ellipse(self, Vector2(236, 84), Vector2(52, 12), Color(0.27, 0.47, 0.2, 0.55))
	Art.ellipse(self, Vector2(236, 82), Vector2(48, 10), pad)
	Art.ellipse(self, Vector2(84, 154), Vector2(66, 15), Color(0.27, 0.47, 0.2, 0.55))
	Art.ellipse(self, Vector2(84, 152), Vector2(62, 13), pad)

	if b.show_enemy:
		var dx := 0.0
		var dy := 0.0
		var alpha := 1.0
		var since := t - b.shake_enemy_at
		if since < 0.45:
			dx = sin(since * 40.0) * 3.0
			alpha = 0.35 if int(since / 0.07) % 2 else 1.0
		if b.faint_enemy_at > 0.0:
			dy = minf(26.0, (t - b.faint_enemy_at) * 80.0)
			alpha = 1.0 - dy / 26.0
		if alpha > 0.0:
			_monster(Vector2(236 + dx, 82 + dy), 1.35, b.wild.key, false, alpha, t)

	if b.ball_at > 0.0:
		_ball(t - b.ball_at, t - b.ball_shake_at)

	if b.show_me and b.me:
		var dx := 0.0
		var alpha := 1.0
		var since := t - b.shake_me_at
		if since < 0.45:
			dx = sin(since * 40.0) * 3.0
			alpha = 0.35 if int(since / 0.07) % 2 else 1.0
		_monster(Vector2(84 + dx, 152), 1.9, b.me.key, true, alpha, t)

	_hp_box(Vector2(12, 12), 132, b.wild, b.disp_enemy_hp, false)
	if b.show_me and b.me:
		_hp_box(Vector2(180, 100), 128, b.me, b.disp_me_hp, true)

	var flash := 1.0 - (t - b.flash_at) / 0.5
	if flash > 0.0:
		draw_rect(Rect2(Vector2.ZERO, LOGICAL), Color(1, 1, 1, flash))


func _reset() -> void:
	draw_set_transform(Vector2.ZERO, 0.0, Vector2(_k, _k))


func _monster(feet: Vector2, s: float, key: String, back: bool, alpha: float, t: float) -> void:
	draw_set_transform(feet * _k, 0.0, Vector2(s * _k, s * _k))
	Art.monster(self, key, back, alpha, t)
	_reset()


func _ball(since_throw: float, since_shake: float) -> void:
	var pos := Vector2(236, 74)
	if since_throw < 0.35:
		var k := since_throw / 0.35
		pos = Vector2(60 + 176 * k, 150 - 120 * k + 70 * k * k)
	var rot := sin(since_shake * 25.0) * 0.5 if since_shake < 0.3 else 0.0
	draw_set_transform(pos * _k, rot, Vector2(_k, _k))
	draw_circle(Vector2.ZERO, 6, Color("#f1f2ff"))
	Art.half_disc(self, Vector2.ZERO, 6, Color("#e04848"))
	draw_rect(Rect2(-6, -0.6, 12, 1.2), Color("#2b2b45"))
	draw_circle(Vector2.ZERO, 1.8, Color("#f1f2ff"))
	_reset()


func _hp_color(r: float) -> Color:
	if r > 0.5:
		return Color("#5fd17a")
	if r > 0.2:
		return Color("#f2c94c")
	return Color("#ef6b5b")


func _hp_box(at: Vector2, w: float, m: Monster, disp: float, mine: bool) -> void:
	var h := 38.0 if mine else 30.0
	draw_rect(Rect2(at, Vector2(w, h)), Color(0.08, 0.09, 0.19, 0.9))
	draw_rect(Rect2(at, Vector2(w, h)), Color("#3d4580"), false, 1.2)
	_text(at + Vector2(7, 4), m.species_name(), 9, Color("#f1f2ff"))
	_text(at + Vector2(w - 7, 4), "Lv.%d" % m.level, 9, Color("#f1f2ff"), true)
	_text(at + Vector2(7, 16), "HP", 7, Color("#ffcd4d"))
	var bw := w - 30
	var r := clampf(disp / m.max_hp(), 0.0, 1.0)
	draw_rect(Rect2(at + Vector2(22, 19), Vector2(bw, 5)), Color("#0c0f22"))
	draw_rect(Rect2(at + Vector2(22, 19), Vector2(bw * r, 5)), _hp_color(r))
	if mine:
		_text(at + Vector2(w - 7, 25), "%d / %d" % [ceili(disp), m.max_hp()], 7, Color("#a3a9d6"), true)
		var lo := float(m.level * m.level * m.level)
		var hi := float(m.xp_for_next())
		draw_rect(Rect2(at + Vector2(7, h - 4), Vector2(w - 14, 2)), Color("#0c0f22"))
		draw_rect(Rect2(at + Vector2(7, h - 4), Vector2((w - 14) * clampf((m.xp - lo) / (hi - lo), 0.0, 1.0), 2)), Color("#6fb6ff"))


## 在逻辑坐标 at（文字左上角；right 为 true 时是右上角）处绘制清晰文字
func _text(at: Vector2, s: String, logical_size: float, col: Color, right := false) -> void:
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	var font := get_theme_default_font()
	var px := int(logical_size * _k)
	var pos := at * _k
	if right:
		pos.x -= font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	draw_string(font, pos + Vector2(0, font.get_ascent(px)), s, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
	_reset()
