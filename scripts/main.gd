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
	hud.visible = s != State.BATTLE
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
		_main_menu()


func _on_stepped(cell: Vector2i) -> void:
	var area := world.area_name(cell)
	if area != _area:
		_area = area
		hud.show_toast(area)
	hud.refresh(area)
	var door := world.door_at(cell)
	var spotter := world.trainer_spotting(cell)
	if not door.is_empty():
		_enter(door)
	elif spotter:
		_trainer_battle(spotter, true)
	elif world.is_tall_grass(cell) and Game.rng.randf() < ENCOUNTER_RATE:
		_encounter(cell)
	elif player.steps % AUTOSAVE_STEPS == 0:
		_save()


## 走进门：治疗所、商店有功能，其他房子说一句话后退出门外
func _enter(door: Dictionary) -> void:
	match door["kind"]:
		"heal":
			await _heal(door)
			return
		"shop":
			await _shop(door)
			return
	_set_state(State.TALK)
	match door["kind"]:
		"gym":
			var town: Dictionary = _town(door["town"])
			var gym: Dictionary = town.get("gym", {})
			await dialog.say("这里是%s道馆，%s擅长%s属性。" % [town.get("name", ""), gym.get("leader", "馆主"), gym.get("type", "")])
			await dialog.say("馆主正在闭关修炼，道馆挑战还没开放。")
		"league":
			await dialog.say("奇异兽联盟的大门紧闭着。集齐八枚徽章的训练师才能进入。")
		_:
			await dialog.say("门上挂着牌子：外出采集中，请勿打扰。")
	dialog.close()
	_leave(door)
	_set_state(State.WALK)


func _leave(door: Dictionary) -> void:
	player.dir = Vector2i.DOWN
	player.place(door["exit"])
	world.refresh_now()


func _town(id: String) -> Dictionary:
	for t in WorldPlan.TOWNS:
		if t["id"] == id:
			return t
	return {}


func _heal(door: Dictionary) -> void:
	_set_state(State.TALK)
	await dialog.say("护士：欢迎来到治疗所！把奇异兽交给我吧……")
	Game.heal_all()
	Game.last_town = door["town"]
	await dialog.say("全部恢复精神了！路上小心。")
	dialog.close()
	_leave(door)
	_save()
	_set_state(State.WALK)


func _shop(door: Dictionary) -> void:
	_set_state(State.TALK)
	await dialog.say("店员：欢迎光临！需要点什么？")
	while true:
		var items: Array = Data.SHOP.keys()
		var labels: Array = []
		for item in items:
			labels.append("%s  %d 金" % [item, Data.SHOP[item]])
		labels.append("离开")
		var i: int = await dialog.choose("你有 %d 金 · 兽球 %d · 伤药 %d" % [Game.money, Game.balls, Game.potions], labels)
		if i >= items.size():
			break
		if Game.buy(items[i]):
			hud.refresh(_area)
			await dialog.say("买了一个%s。谢谢惠顾！" % items[i], 0.9)
		else:
			await dialog.say("钱好像不太够呢……", 1.0)
	await dialog.say("欢迎下次光临！", 0.8)
	dialog.close()
	_leave(door)
	_save()
	_set_state(State.WALK)


func _encounter(cell: Vector2i) -> void:
	_set_state(State.BATTLE)
	var zone := world.zone_index(cell)
	var wild := Data.roll_wild(world.biome_at(cell), world.region_levels(cell), Game.rng)
	var foes: Array[Monster] = [wild]
	var result: String = await battle.run(foes, zone)
	_after_battle(result)


## 训练师对战。spotted 为 true 表示是被训练师看见（会先弹感叹号）
func _trainer_battle(npc: Prop, spotted: bool) -> void:
	var info: Dictionary = npc.npc["trainer"]
	_set_state(State.TALK)
	if spotted:
		npc.set_alerted(true)
		await get_tree().create_timer(0.6).timeout
		npc.set_alerted(false)
	else:
		npc.face(-player.dir)
	for line in info["intro"]:
		await dialog.say(line)
	dialog.close()
	_set_state(State.BATTLE)
	var team: Array[Monster] = []
	for entry in info["team"]:
		team.append(Monster.create(entry[0], int(entry[1])))
	var result: String = await battle.run(team, world.zone_index(player.cell), info)
	if result == "won":
		Game.flags[info["id"]] = true
	_after_battle(result)


func _after_battle(result: String) -> void:
	if result == "lost":
		player.dir = Vector2i.DOWN
		player.place(world.heal_exit(Game.last_town))
		world.refresh_now()
	_save()
	_set_state(State.WALK)


func _interact() -> void:
	var front := player.facing_cell()
	var npc := world.npc_at(front)
	if npc and npc.npc.has("trainer") and not Game.flags.get(npc.npc["trainer"]["id"], false):
		_trainer_battle(npc, false)
		return
	if npc:
		_set_state(State.TALK)
		npc.face(-player.dir)
		for line in npc.npc["lines"]:
			await dialog.say(line)
		npc.face(npc.npc.get("facing", Vector2i.DOWN))
		dialog.close()
		_set_state(State.WALK)
		return
	var lines := _look_at(front)
	if not lines.is_empty():
		_set_state(State.TALK)
		for line in lines:
			await dialog.say(line)
		dialog.close()
		_set_state(State.WALK)


## 对着房子、路牌、洞口、地标按确认键时的说明
func _look_at(c: Vector2i) -> Array:
	var house := world.building_at(c)
	if not house.is_empty():
		match house["kind"]:
			"heal":
				return ["治疗所的大门在正下方，走进去就能恢复。"]
			"shop":
				return ["商店的大门在正下方，兽球和伤药都在这里买。"]
			"gym":
				return ["道馆的大门在正下方。"]
			"league":
				return ["奇异兽联盟总部。"]
		return ["一户人家。"]
	var obj := WorldGen.object_of(world.cell(c))
	if obj == 0 or obj == WorldGen.BUILDING:
		return []
	match WorldGen.PROPS[obj]:
		"sign":
			var place := World.gen.place_at(c, 4)
			if not place.is_empty():
				return ["路牌：%s" % place["name"]]
			return ["路牌：%s · 奈尔斯地区" % world.area_name(c)]
		"cave", "monument":
			var p := World.gen.place_at(c, 2)
			if not p.is_empty():
				if p["kind"] == "dungeon":
					return ["%s：%s" % [p["name"], p["desc"]], "洞里黑漆漆的，现在还进不去。"]
				return ["%s：%s" % [p["name"], p["desc"]]]
	return []


func _main_menu() -> void:
	_set_state(State.MENU)
	var i: int = await dialog.choose("%d 金 · 兽球 %d · 伤药 %d" % [Game.money, Game.balls, Game.potions],
		["队伍", "背包", "返回"])
	if i == 0:
		await _party_menu()
	elif i == 1:
		await _bag_menu()
	dialog.close()
	_set_state(State.WALK)


func _bag_menu() -> void:
	var j: int = await dialog.choose("背包", ["伤药 ×%d" % Game.potions, "返回"], [Game.potions <= 0, false])
	if j != 0:
		return
	var labels: Array = []
	var disabled: Array = []
	for m in Game.party:
		labels.append("%s  %d/%d" % [m.species_name(), m.hp, m.max_hp()])
		disabled.append(m.is_fainted() or m.hp >= m.max_hp())
	labels.append("返回")
	disabled.append(false)
	var k: int = await dialog.choose("给谁用伤药？（回复 %d HP）" % Data.POTION_HEAL, labels, disabled)
	if k < Game.party.size():
		var m: Monster = Game.party[k]
		var healed: int = Game.use_potion(m)
		await dialog.say("%s 回复了 %d 点 HP。" % [m.species_name(), healed])
		_save()


func _party_menu() -> void:
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


func _save() -> void:
	Game.player_cell = player.cell
	Game.save_game()
