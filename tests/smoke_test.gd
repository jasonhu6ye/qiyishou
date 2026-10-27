extends Node
## 冒烟测试：godot --headless --path . res://tests/smoke_test.tscn
## 检查数据与公式，载入主场景，再自动按键打完一场野外战斗。退出码非 0 表示失败。

const TIMEOUT := 60.0

var failures := 0
var main: Node


func check(cond: bool, what: String) -> void:
	if cond:
		print("  ok   ", what)
	else:
		failures += 1
		push_error("FAIL " + what)
		print("  FAIL ", what)


func _ready() -> void:
	print("== 奇异兽 冒烟测试 ==")
	Game.delete_save()
	_unit_checks()
	await _scene_checks()
	await _battle_check()
	Game.delete_save()
	print("== 失败 %d 项 ==" % failures)
	get_tree().quit(1 if failures > 0 else 0)


func _unit_checks() -> void:
	var fox := Monster.create("huohu", 5)
	check(fox.moves.size() == 2 and fox.moves[0] == "撞击" and fox.moves[1] == "火花", "5 级焰尾狐会撞击和火花")
	check(fox.hp == fox.max_hp() and fox.hp > 0, "新建的奇异兽满血")
	var high := Monster.create("huohu", 20)
	check(high.moves.size() == 4, "高等级最多保留 4 个招式")

	check(Data.effectiveness("火", "草") == 2.0, "火克草")
	check(Data.effectiveness("水", "草") == 0.5, "水打草效果不好")
	check(Data.effectiveness("普通", "火") == 1.0, "普通属性无克制")

	var rng := RandomNumberGenerator.new()
	rng.seed = 1
	var leaf := Monster.create("yeshu", 5)
	var r: Dictionary = Battle.damage(fox, leaf, "火花", rng)
	check(int(r["amount"]) >= 1 and r["eff"] == 2.0, "火花打叶芽鼠效果拔群")

	var bird := Monster.create("yuanniao", 3)
	var full := Battle.catch_chance(bird)
	bird.hp = 1
	check(Battle.catch_chance(bird) > full, "血越少越好抓")

	var lv := fox.level
	fox.xp = fox.xp_for_next()
	fox.level_up()
	check(fox.level == lv + 1, "升级")

	for i in 50:
		var w := Data.roll_wild(1, rng)
		if w.level < 5 or w.level > 9:
			check(false, "2号道路等级应在 5–9")
			break

	Game.reset()
	Game.party.append(Monster.create("paowa", 7))
	Game.balls = 3
	Game.seen["paowa"] = true
	Game.player_cell = Vector2i(10, 7)
	Game.save_game()
	Game.reset()
	check(Game.load_game(), "能读取存档")
	check(Game.party.size() == 1 and Game.party[0].key == "paowa" and Game.party[0].level == 7, "存档保留队伍")
	check(Game.balls == 3 and Game.player_cell == Vector2i(10, 7), "存档保留兽球和位置")
	Game.delete_save()


func _scene_checks() -> void:
	Game.reset()
	Game.party.append(Monster.create("huohu", 6))
	Game.party.append(Monster.create("paowa", 6))
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	for i in 5:
		await get_tree().process_frame
	var world: World = main.world
	check(world != null and world.player != null, "主场景创建了地图和玩家")
	check(world.is_walkable(Game.START_CELL), "出生点可以行走")
	check(world.tile_at(World.HEAL_DOOR) == World.DOOR, "治疗所门口存在")
	check(not world.is_walkable(Vector2i(0, 0)), "地图边缘是树")
	check(main.state == 0 and main.player.active, "有队伍时直接进入行走状态")


func _battle_check() -> void:
	var battle: Battle = main.battle
	var dialog: DialogBox = main.dialog
	var wild := Monster.create("chongchong", 2)
	var done := [false]
	var run_battle := func():
		await battle.run(wild, 0)
		done[0] = true
	run_battle.call()
	var start := Time.get_ticks_msec()
	while not done[0] and (Time.get_ticks_msec() - start) / 1000.0 < TIMEOUT:
		await get_tree().process_frame
		if dialog._waiting:
			dialog._finish()
		elif dialog.grid.get_child_count() > 0:
			for b in dialog.grid.get_children():
				if b is Button and not b.disabled:
					b.pressed.emit()
					break
	check(done[0], "自动操作能打完一场战斗")
	check(wild.is_fainted() or Game.caught.has("chongchong"), "野生绒绒虫被打倒或被抓到")
	check(not battle.visible, "战斗结束后关闭战斗画面")
