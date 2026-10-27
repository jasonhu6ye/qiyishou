extends Node2D
## 主流程：大地图行走 ↔ 对话 ↔ 战斗 ↔ 队伍菜单 之间的切换。

const ENCOUNTER_RATE := 0.12
const AUTOSAVE_STEPS := 10

enum State { WALK, TALK, BATTLE, MENU }

var state := State.WALK
var world: World
var player: Player
var dialog: DialogBox
var battle: Battle
var hud: Hud
var _area := ""


func _ready() -> void:
	RenderingServer.set_default_clear_color(Color("#141830"))
	world = World.new()
	add_child(world)
	player = world.player
	dialog = DialogBox.new()
	add_child(dialog)
	battle = Battle.new()
	battle.dialog = dialog
	add_child(battle)
	hud = Hud.new()
	add_child(hud)
	player.stepped.connect(_on_stepped)

	var loaded: bool = Game.load_game()
	if loaded and world.is_walkable(Game.player_cell):
		player.place(Game.player_cell)
	if Game.party.is_empty():
		await _choose_starter()
	_area = world.area_name(player.cell)
	hud.refresh(_area)
	hud.show_toast(_area)


func _set_state(s: State) -> void:
	state = s
	player.active = s == State.WALK
	hud.refresh(world.area_name(player.cell))


func _choose_starter() -> void:
	_set_state(State.TALK)
	await dialog.say("研究员：欢迎来到晨露镇！这里有三只奇异兽，带上一只出发吧。")
	await dialog.say("属性相克是 火 → 草 → 水 → 火，选你喜欢的就好。")
	var labels: Array = []
	for k in Data.STARTERS:
		labels.append("%s（%s）" % [Data.SPECIES[k]["name"], Data.SPECIES[k]["type"]])
	var i: int = await dialog.choose("选择你的第一只奇异兽", labels)
	var m := Monster.create(Data.STARTERS[i], 5)
	Game.party.append(m)
	Game.seen[m.key] = true
	Game.caught[m.key] = true
	await dialog.say("%s 成为了你的伙伴！" % m.species_name())
	dialog.close()
	_save()
	_set_state(State.WALK)


func _unhandled_input(event: InputEvent) -> void:
	if state != State.WALK or player.moving:
		return
	if event.is_action_pressed("confirm"):
		get_viewport().set_input_as_handled()
		_interact()
	elif event.is_action_pressed("cancel"):
		get_viewport().set_input_as_handled()
		_party_menu()


func _on_stepped(cell: Vector2i) -> void:
	var area := world.area_name(cell)
	if area != _area:
		_area = area
		hud.show_toast(area)
	hud.refresh(area)
	var t := world.tile_at(cell)
	if t == World.DOOR:
		_heal()
	elif t == World.TALL_GRASS and Game.rng.randf() < ENCOUNTER_RATE:
		_encounter(cell)
	elif player.steps % AUTOSAVE_STEPS == 0:
		_save()


func _heal() -> void:
	_set_state(State.TALK)
	await dialog.say("护士：欢迎来到治疗所！把奇异兽交给我吧……")
	Game.heal_all()
	Game.balls = maxi(Game.balls, 10)
	await dialog.say("全部恢复精神了！兽球也给你补到 10 个，路上小心。")
	dialog.close()
	player.dir = Vector2i.DOWN
	player.place(World.HEAL_EXIT)
	_save()
	_set_state(State.WALK)


func _encounter(cell: Vector2i) -> void:
	_set_state(State.BATTLE)
	var zone := world.zone_index(cell)
	var wild := Data.roll_wild(zone, Game.rng)
	var blackout: bool = await battle.run(wild, zone)
	if blackout:
		player.dir = Vector2i.DOWN
		player.place(World.HEAL_EXIT)
	_save()
	_set_state(State.WALK)


func _interact() -> void:
	var front := player.facing_cell()
	var npc := world.npc_at(front)
	if npc:
		_set_state(State.TALK)
		npc.face(-player.dir)
		for line in npc.npc["lines"]:
			await dialog.say(line)
		npc.face(Vector2i.DOWN)
		dialog.close()
		_set_state(State.WALK)
		return
	var house := world.house_at(front)
	if not house.is_empty():
		_set_state(State.TALK)
		if house["heal"]:
			await dialog.say("治疗所的大门在正下方，走进去就能恢复。")
		else:
			await dialog.say("门上挂着牌子：外出采集中，请勿打扰。")
		dialog.close()
		_set_state(State.WALK)


func _party_menu() -> void:
	_set_state(State.MENU)
	var labels: Array = []
	for m in Game.party:
		labels.append("%s Lv.%d  HP %d/%d" % [m.species_name(), m.level, m.hp, m.max_hp()])
	labels.append("返回")
	var prompt := "队伍（选一只设为首发）· 存储箱 %d 只" % Game.box.size()
	var i: int = await dialog.choose(prompt, labels)
	if i > 0 and i < Game.party.size():
		var m: Monster = Game.party.pop_at(i)
		Game.party.push_front(m)
		await dialog.say("%s 成为了首发。" % m.species_name())
		_save()
	dialog.close()
	_set_state(State.WALK)


func _save() -> void:
	Game.player_cell = player.cell
	Game.save_game()
