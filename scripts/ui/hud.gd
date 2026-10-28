class_name Hud
extends CanvasLayer
## 左上角状态栏 + 进入新区域时的地名提示。

var status: Label
var toast: Label
var _tween: Tween


func _ready() -> void:
	layer = 8
	status = Label.new()
	status.theme = Game.ui_theme
	status.position = Vector2(4, 2)
	status.add_theme_color_override("font_color", Color("#f1f2ff"))
	status.add_theme_color_override("font_outline_color", Color("#141830"))
	status.add_theme_constant_override("outline_size", 3)
	add_child(status)

	toast = Label.new()
	toast.theme = Game.ui_theme
	toast.anchor_left = 0.5
	toast.anchor_right = 0.5
	toast.offset_top = 22
	toast.grow_horizontal = Control.GROW_DIRECTION_BOTH
	toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	toast.add_theme_font_size_override("font_size", 24)
	toast.add_theme_color_override("font_color", Color("#ffcd4d"))
	toast.add_theme_color_override("font_outline_color", Color("#141830"))
	toast.add_theme_constant_override("outline_size", 4)
	toast.modulate.a = 0.0
	add_child(toast)


func refresh(area: String) -> void:
	status.text = "%s  %d金  兽球×%d  伤药×%d  图鉴%d/%d" % [
		area, Game.money, Game.balls, Game.potions, Game.caught.size(), Game.seen.size()]


func show_toast(text: String) -> void:
	toast.text = text
	if _tween:
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(toast, "modulate:a", 1.0, 0.3)
	_tween.tween_interval(1.4)
	_tween.tween_property(toast, "modulate:a", 0.0, 0.4)
