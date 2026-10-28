extends Node
## 全局状态（自动加载为 Game）：队伍、道具、图鉴、存档与按键映射。

const SAVE_PATH := "user://save.json"
const PARTY_LIMIT := 6
const START_CELL := Vector2i(9, 8)
const FONT_PATH := "res://assets/fonts/fusion-pixel-12px.ttf"
const FONT_SIZE := 12

var party: Array[Monster] = []
var box: Array[Monster] = []
var balls := 10
var seen := {}
var caught := {}
var player_cell := START_CELL
var rng := RandomNumberGenerator.new()


func _ready() -> void:
	rng.randomize()
	_setup_input()
	_setup_theme()


func _setup_input() -> void:
	var bindings := {
		"move_up": [KEY_W, KEY_UP],
		"move_down": [KEY_S, KEY_DOWN],
		"move_left": [KEY_A, KEY_LEFT],
		"move_right": [KEY_D, KEY_RIGHT],
		"confirm": [KEY_SPACE, KEY_Z, KEY_ENTER],
		"cancel": [KEY_X, KEY_ESCAPE],
		"run": [KEY_SHIFT],
	}
	for action in bindings:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		for keycode in bindings[action]:
			var ev := InputEventKey.new()
			ev.physical_keycode = keycode
			InputMap.action_add_event(action, ev)


## 全局像素风主题：12px 像素字体（不抗锯齿）+ 扁平按钮
func _setup_theme() -> void:
	var font: FontFile = load(FONT_PATH)
	font.antialiasing = TextServer.FONT_ANTIALIASING_NONE
	font.hinting = TextServer.HINTING_NONE
	font.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
	ThemeDB.fallback_font = font
	ThemeDB.fallback_font_size = FONT_SIZE

	var theme := Theme.new()
	theme.default_font = font
	theme.default_font_size = FONT_SIZE
	var normal := _flat_box(Color("#2a3160"), Color("#3d4580"))
	theme.set_stylebox("normal", "Button", normal)
	theme.set_stylebox("pressed", "Button", normal)
	theme.set_stylebox("hover", "Button", _flat_box(Color("#333b74"), Color("#ffcd4d")))
	theme.set_stylebox("disabled", "Button", _flat_box(Color("#22284d"), Color("#2c3260")))
	var focus := _flat_box(Color(0, 0, 0, 0), Color("#ffcd4d"))
	focus.draw_center = false
	theme.set_stylebox("focus", "Button", focus)
	theme.set_color("font_color", "Button", Color("#f1f2ff"))
	theme.set_color("font_hover_color", "Button", Color("#ffffff"))
	theme.set_color("font_focus_color", "Button", Color("#ffcd4d"))
	theme.set_color("font_disabled_color", "Button", Color("#6b7099"))
	theme.set_color("font_color", "Label", Color("#f1f2ff"))
	get_tree().root.theme = theme


func _flat_box(bg: Color, border: Color) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(1)
	sb.content_margin_left = 5
	sb.content_margin_right = 5
	sb.content_margin_top = 2
	sb.content_margin_bottom = 2
	return sb


func first_alive() -> Monster:
	for m in party:
		if not m.is_fainted():
			return m
	return null


func alive_count() -> int:
	var n := 0
	for m in party:
		if not m.is_fainted():
			n += 1
	return n


func heal_all() -> void:
	for m in party:
		m.heal()


## 新捕获的奇异兽：队伍没满进队伍，满了进存储箱。返回 true 表示进了队伍。
func add_caught(m: Monster) -> bool:
	caught[m.key] = true
	if party.size() < PARTY_LIMIT:
		party.append(m)
		return true
	box.append(m)
	return false


func reset() -> void:
	party.clear()
	box.clear()
	balls = 10
	seen.clear()
	caught.clear()
	player_cell = START_CELL


func save_game() -> void:
	var data := {
		"party": party.map(func(m: Monster) -> Dictionary: return m.to_dict()),
		"box": box.map(func(m: Monster) -> Dictionary: return m.to_dict()),
		"balls": balls,
		"seen": seen.keys(),
		"caught": caught.keys(),
		"cell": [player_cell.x, player_cell.y],
	}
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(data))


func load_game() -> bool:
	if not FileAccess.file_exists(SAVE_PATH):
		return false
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		return false
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY or data.get("party", []).is_empty():
		return false
	reset()
	for d in data["party"]:
		party.append(Monster.from_dict(d))
	for d in data.get("box", []):
		box.append(Monster.from_dict(d))
	balls = int(data.get("balls", 10))
	for k in data.get("seen", []):
		seen[k] = true
	for k in data.get("caught", []):
		caught[k] = true
	var cell: Array = data.get("cell", [START_CELL.x, START_CELL.y])
	player_cell = Vector2i(int(cell[0]), int(cell[1]))
	return true


func delete_save() -> void:
	if FileAccess.file_exists(SAVE_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
