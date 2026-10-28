class_name DialogBox
extends CanvasLayer
## 屏幕底部的对话框。say() 显示一句话并等待确认（或自动跳过），
## choose() 显示一组按钮并返回所选下标。两者都用 await 调用。

signal advanced
signal chosen(index: int)

const MIN_SHOW_TIME := 0.15

var panel: PanelContainer
var label: Label
var grid: GridContainer
var _waiting := false
var _token := 0
var _shown_at := 0.0


func _ready() -> void:
	layer = 10
	panel = PanelContainer.new()
	panel.theme = Game.ui_theme
	panel.anchor_left = 0.0
	panel.anchor_right = 1.0
	panel.anchor_top = 1.0
	panel.anchor_bottom = 1.0
	panel.offset_left = 4
	panel.offset_right = -4
	panel.offset_top = -62
	panel.offset_bottom = -4
	panel.grow_vertical = Control.GROW_DIRECTION_BEGIN
	var style := StyleBoxFlat.new()
	style.bg_color = Color("#20264aee")
	style.border_color = Color("#3d4580")
	style.set_border_width_all(2)
	style.set_corner_radius_all(3)
	style.content_margin_left = 8
	style.content_margin_right = 8
	style.content_margin_top = 5
	style.content_margin_bottom = 5
	panel.add_theme_stylebox_override("panel", style)
	add_child(panel)

	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 4)
	panel.add_child(vb)
	label = Label.new()
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_color_override("font_color", Color("#f1f2ff"))
	vb.add_child(label)
	grid = GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 4)
	grid.add_theme_constant_override("v_separation", 3)
	vb.add_child(grid)

	panel.gui_input.connect(_on_panel_input)
	panel.hide()


func say(text: String, auto_seconds := 0.0) -> void:
	_clear_buttons()
	panel.show()
	label.text = text if auto_seconds > 0.0 else text + "  ▼"
	_waiting = true
	_token += 1
	var my_token := _token
	_shown_at = _now()
	if auto_seconds > 0.0:
		get_tree().create_timer(auto_seconds).timeout.connect(func():
			if _waiting and _token == my_token:
				_finish()
		)
	await advanced


func choose(prompt: String, labels: Array, disabled: Array = []) -> int:
	_clear_buttons()
	panel.show()
	label.text = prompt
	var first: Button = null
	for i in labels.size():
		var b := Button.new()
		b.text = str(labels[i])
		b.disabled = i < disabled.size() and bool(disabled[i])
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.pressed.connect(func(): chosen.emit(i))
		grid.add_child(b)
		if first == null and not b.disabled:
			first = b
	if first:
		first.call_deferred("grab_focus")
	var index: int = await chosen
	_clear_buttons()
	return index


func close() -> void:
	_clear_buttons()
	panel.hide()


func is_busy() -> bool:
	return panel.visible


func _clear_buttons() -> void:
	for c in grid.get_children():
		grid.remove_child(c)
		c.queue_free()


func _finish() -> void:
	_waiting = false
	advanced.emit()


func _now() -> float:
	return Time.get_ticks_msec() / 1000.0


func _unhandled_input(event: InputEvent) -> void:
	if _waiting and event.is_action_pressed("confirm") and _now() - _shown_at > MIN_SHOW_TIME:
		get_viewport().set_input_as_handled()
		_finish()


func _on_panel_input(event: InputEvent) -> void:
	if _waiting and event is InputEventMouseButton and event.pressed and _now() - _shown_at > MIN_SHOW_TIME:
		_finish()
