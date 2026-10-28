class_name BattleView
extends Control
## 战斗画面。在 320x240 的逻辑坐标里绘制（就是游戏的渲染分辨率），按控件宽度等比缩放。

const LOGICAL := Vector2(320, 240)
const ENEMY_FEET := Vector2(236, 82)
const MY_FEET := Vector2(84, 154)
const FX_TIME := 0.55  ## 招式特效时长，战斗逻辑在特效播完后才结算伤害
const FX_COLORS := {
	"火": [Color("#fff3a0"), Color("#ffb03a"), Color("#e8502a")],
	"水": [Color("#e6f7ff"), Color("#7cc6ff"), Color("#3a7fd6")],
	"草": [Color("#d8ff9a"), Color("#6cc25a"), Color("#2f7a2c")],
	"电": [Color("#ffffff"), Color("#fff06a"), Color("#f2b81a")],
	"普通": [Color("#ffffff"), Color("#ffe7a8"), Color("#c9b98a")],
}

var battle: Battle
var _k := 1.0


func _draw() -> void:
	var b := battle
	if b == null or b.wild == null:
		return
	_k = size.x / LOGICAL.x
	var t := Battle.now()
	_reset()

	draw_texture(Art.tex("battle_bg_%d" % clampi(b.zone, 0, 1)), Vector2.ZERO)

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
		dx += _lunge(t - b.lunge_enemy_at) * -10.0
		dy += _lunge(t - b.lunge_enemy_at) * 5.0
		if alpha > 0.0:
			_monster(ENEMY_FEET + Vector2(dx, dy), b.wild.key, false, alpha, t)

	if b.ball_at > 0.0:
		_ball(t - b.ball_at, t - b.ball_shake_at)

	if b.show_me and b.me:
		var dx := 0.0
		var alpha := 1.0
		var since := t - b.shake_me_at
		if since < 0.45:
			dx = sin(since * 40.0) * 3.0
			alpha = 0.35 if int(since / 0.07) % 2 else 1.0
		var lunge := _lunge(t - b.lunge_me_at)
		_monster(MY_FEET + Vector2(dx + lunge * 14.0, -lunge * 7.0), b.me.key, true, alpha, t)

	if t - b.fx_at < FX_TIME:
		_fx((t - b.fx_at) / FX_TIME, b.fx_type, b.fx_on_enemy)

	_hp_box(Vector2(8, 8), 140, b.wild, b.disp_enemy_hp, false)
	if b.show_me and b.me:
		_hp_box(Vector2(172, 98), 140, b.me, b.disp_me_hp, true)

	var flash := 1.0 - (t - b.flash_at) / 0.5
	if flash > 0.0:
		draw_rect(Rect2(Vector2.ZERO, LOGICAL), Color(1, 1, 1, flash))


func _reset() -> void:
	draw_set_transform(Vector2.ZERO, 0.0, Vector2(_k, _k))


## 立绘按整像素放置，脚下有一圈影子，再加一个上下 1 像素的呼吸起伏
func _monster(feet: Vector2, key: String, back: bool, alpha: float, t: float) -> void:
	var bob := roundf(sin(t * 3.0 + (1.5 if back else 0.0)))
	var w := Art.tex("monsters/%s_%s" % [key, "back" if back else "front"]).get_width() * 0.3
	Art.ellipse(self, feet.round() + Vector2(0, 1), Vector2(roundf(w), roundf(w * 0.22) + 1.0), Color(0.1, 0.15, 0.05, 0.28 * alpha))
	draw_set_transform((feet.round() + Vector2(0, bob)) * _k, 0.0, Vector2(_k, _k))
	Art.monster(self, key, back, alpha)
	_reset()


## 出招时向前冲一下：0 → 1 → 0，持续 0.3 秒
func _lunge(since: float) -> float:
	if since < 0.0 or since > 0.3:
		return 0.0
	return roundf(sin(since / 0.3 * PI) * 4.0) / 4.0


## 整像素方块，特效都用它画，保持像素风
func _dot(p: Vector2, sz: float, col: Color) -> void:
	draw_rect(Rect2(p.round() - Vector2(sz, sz) * 0.5, Vector2(sz, sz)).abs(), col)


## 招式特效。k 从 0 到 1；on_enemy 为 true 表示打向对手
func _fx(k: float, type: String, on_enemy: bool) -> void:
	var cols: Array = FX_COLORS.get(type, FX_COLORS["普通"])
	var target := (ENEMY_FEET + Vector2(0, -22)) if on_enemy else (MY_FEET + Vector2(0, -34))
	var source := (MY_FEET + Vector2(10, -40)) if on_enemy else (ENEMY_FEET + Vector2(-10, -20))
	match type:
		"火":
			for i in 22:
				var life := fposmod(k * 1.6 + i * 0.137, 1.0)
				var p := target + Vector2((i * 23 % 37) - 18 + sin(life * 9.0 + i) * 3.0, 18.0 - life * 44.0)
				var c: Color = cols[mini(2, int(life * 3.0))]
				_dot(p, roundf(7.0 - life * 5.0), c)
				if life < 0.4:
					_dot(p + Vector2(0, -1), 2.0, cols[0])
		"水":
			var travel := minf(1.0, k / 0.55)
			if k < 0.55:
				for i in 6:
					var q := clampf(travel - i * 0.06, 0.0, 1.0)
					var p := source.lerp(target, q) + Vector2(0, -sin(q * PI) * 16.0 + (i % 2) * 2.0)
					_dot(p, 5.0 if i % 2 == 0 else 3.0, cols[i % 3])
			else:
				var s := (k - 0.55) / 0.45
				for i in 10:
					var a := i * TAU / 10.0
					var p := target + Vector2(cos(a), sin(a) * 0.7) * (4.0 + s * 18.0) + Vector2(0, s * s * 10.0)
					_dot(p, roundf(4.0 - s * 2.0), cols[i % 2])
		"草":
			for i in 6:
				var q := clampf(k * 1.4 - i * 0.08, 0.0, 1.0)
				if q <= 0.0 or q >= 1.0:
					continue
				var spin := q * 10.0 + i
				var p := source.lerp(target, q) + Vector2(cos(spin), sin(spin)) * (8.0 - q * 6.0)
				_dot(p, 4.0, cols[1])
				_dot(p + Vector2(cos(spin * 2.0), sin(spin * 2.0)).round(), 1.0, cols[0])
				_dot(p - Vector2(cos(spin * 2.0), sin(spin * 2.0)).round(), 1.0, cols[2])
		"电":
			if int(k * 12.0) % 2 == 0:
				draw_rect(Rect2(Vector2.ZERO, LOGICAL), Color(1.0, 0.95, 0.5, 0.18))
			for bolt in 3:
				var pts := PackedVector2Array()
				var x := target.x + (bolt - 1) * 12.0
				var jit := int(k * 10.0) * 7 + bolt * 13
				for j in 7:
					var y := target.y - 60.0 + j * 10.0
					pts.append(Vector2(x + ((jit + j * 5) % 9) - 4.0, y).round())
				draw_polyline(pts, cols[1 if bolt == 1 else 2], 2.0)
				draw_polyline(pts, cols[0], 1.0)
		_:
			var s := k
			for i in 8:
				var a := i * TAU / 8.0 + 0.4
				var d := 4.0 + s * 16.0
				_dot(target + Vector2(cos(a), sin(a)) * d, roundf(5.0 - s * 3.0), cols[i % 2])
			if s < 0.4:
				_dot(target, 10.0 - s * 15.0, Color(1, 1, 1, 0.8))


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
	var h := 44.0 if mine else 31.0
	draw_rect(Rect2(at, Vector2(w, h)), Color(0.08, 0.09, 0.19, 0.92))
	draw_rect(Rect2(at + Vector2(0.5, 0.5), Vector2(w - 1, h - 1)), Color("#3d4580"), false, 1.0)
	_text(at + Vector2(6, 3), m.species_name(), Color("#f1f2ff"))
	_text(at + Vector2(w - 6, 3), "Lv.%d" % m.level, Color("#f1f2ff"), true)
	_text(at + Vector2(6, 16), "HP", Color("#ffcd4d"))
	var bar := Rect2(at + Vector2(24, 20), Vector2(w - 30, 5))
	var r := clampf(disp / m.max_hp(), 0.0, 1.0)
	draw_rect(bar, Color("#0c0f22"))
	draw_rect(Rect2(bar.position, Vector2(roundf(bar.size.x * r), bar.size.y)), _hp_color(r))
	if mine:
		_text(at + Vector2(w - 6, 27), "%d / %d" % [ceili(disp), m.max_hp()], Color("#a3a9d6"), true)
		var lo := float(m.level * m.level * m.level)
		var hi := float(m.xp_for_next())
		var xp := Rect2(at + Vector2(6, h - 4), Vector2(w - 12, 2))
		draw_rect(xp, Color("#0c0f22"))
		draw_rect(Rect2(xp.position, Vector2(roundf(xp.size.x * clampf((m.xp - lo) / (hi - lo), 0.0, 1.0)), 2)), Color("#6fb6ff"))


## 在逻辑坐标 at（文字左上角；right 为 true 时是右上角）处用像素字体绘制文字
func _text(at: Vector2, s: String, col: Color, right := false) -> void:
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	var font := get_theme_default_font()
	var px := int(Game.FONT_SIZE * _k)
	var pos := (at * _k).round()
	if right:
		pos.x -= font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	draw_string(font, pos + Vector2(0, roundf(font.get_ascent(px))), s, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
	_reset()
