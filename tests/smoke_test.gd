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
		var w := Data.roll_wild(WorldGen.Biome.DESERT, [30, 37], rng)
		if w.level < 30 or w.level > 37:
			check(false, "野生等级应在区域范围内")
			break

	var bug := Monster.create("chongchong", 6)
	check(Data.evolution_for(bug) == "", "6 级绒绒虫还不会进化")
	bug.xp = bug.xp_for_next()
	bug.level_up()
	check(Data.evolution_for(bug) == "jianjian", "7 级绒绒虫会进化成茧茧")
	var hp_before := bug.hp
	bug.evolve("jianjian")
	check(bug.key == "jianjian" and bug.hp >= hp_before, "进化后换物种且不掉血")

	Game.reset()
	var money_before: int = Game.money
	check(Game.buy("伤药") and Game.potions == 3 and Game.money == money_before - 300, "商店买伤药扣钱加数量")
	Game.money = 100
	check(not Game.buy("兽球") and Game.balls == 5, "钱不够买不了")
	var hurt := Monster.create("paowa", 10)
	hurt.hp = 3
	var healed: int = Game.use_potion(hurt)
	check(healed == Data.POTION_HEAL and hurt.hp == 3 + Data.POTION_HEAL, "伤药回复 20 HP")
	hurt.hp = hurt.max_hp()
	check(Game.use_potion(hurt) == 0 and Game.potions == 2, "满血时不消耗伤药")

	for key in Data.SPECIES:
		if Art.tex("monsters/%s_front" % key) == null or Art.tex("monsters/%s_back" % key) == null:
			check(false, "%s 的立绘能载入" % key)
	for kind in ["heal", "shop", "home"]:
		check(Art.tex("house_" + kind) != null, "%s 房屋贴图能载入" % kind)

	check(Art.tex("battle_bg_0") != null and Art.tex("battle_bg_1") != null, "战斗背景能载入")
	check(Art.tex("tiles") != null and Art.tex("tree") != null and Art.tex("player") != null, "像素图都能载入")
	check(Game.ui_theme != null and Game.ui_theme.default_font.resource_path == Game.FONT_PATH, "界面主题使用像素字体")

	Game.reset()
	Game.party.append(Monster.create("paowa", 7))
	Game.balls = 3
	Game.money = 1234
	Game.flags["trainer_ajie"] = true
	Game.seen["paowa"] = true
	Game.player_cell = WorldPlan.START_ORIGIN + Vector2i(10, 7)
	Game.last_town = "senyu"
	Game.save_game()
	Game.reset()
	check(Game.load_game(), "能读取存档")
	check(Game.party.size() == 1 and Game.party[0].key == "paowa" and Game.party[0].level == 7, "存档保留队伍")
	check(Game.balls == 3 and Game.player_cell == WorldPlan.START_ORIGIN + Vector2i(10, 7), "存档保留兽球和位置")
	check(Game.last_town == "senyu", "存档保留最近的治疗所")
	check(Game.money == 1234 and Game.flags.get("trainer_ajie", false), "存档保留金钱和训练师记录")
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
	var o := WorldPlan.START_ORIGIN
	check(world.door_at(o + Vector2i(6, 5)).get("kind", "") == "heal", "晨露镇治疗所门口存在")
	check(world.door_at(o + Vector2i(13, 5)).get("kind", "") == "shop", "晨露镇商店门口存在")
	check(world.heal_exit("chenlu") == o + Vector2i(6, 6), "治疗所出口在门下方")
	check(not world.is_walkable(o + Vector2i(0, 20)), "晨露镇边缘是树")
	check(world.is_walkable(o + Vector2i(24, 0)) and world.is_walkable(o + Vector2i(47, 7)), "晨露镇北口和东口能走出去")
	check(not world.is_walkable(Vector2i(5, 5)), "地图角落是海")
	check(world.area_name(Game.START_CELL) == "晨露镇", "出生点的地名")
	check(main.state == 0 and main.player.active, "有队伍时直接进入行走状态")
	var ajie: Prop = world.trainer_spotting(o + Vector2i(36, 15))
	check(ajie != null and ajie.npc["trainer"]["id"] == "trainer_ajie", "站在阿杰视线里会被发现")
	check(world.trainer_spotting(o + Vector2i(36, 16)) == null, "不在视线里不会被发现")
	_world_checks(world)
	var dialog_font: Font = main.dialog.label.get_theme_font("font")
	check(dialog_font.resource_path == Game.FONT_PATH, "对话框实际用上了像素字体")
	check(main.dialog.label.get_theme_font_size("font_size") == Game.FONT_SIZE, "对话框字号是 12px")


## 大地图：每个城镇都有治疗所和商店，道馆城市有道馆，各区域地貌对得上，道路连通
func _world_checks(world: World) -> void:
	var gen := World.gen
	for t in WorldPlan.TOWNS:
		var kinds := {}
		for b in gen.buildings:
			if b["town"] == t["id"]:
				kinds[b["kind"]] = true
				if not world.is_walkable(b["exit"]):
					check(false, "%s 的%s门口能走" % [t["name"], b["kind"]])
		if not (kinds.has("heal") and kinds.has("shop")):
			check(false, "%s 有治疗所和商店" % t["name"])
		if t["kind"] == "city" and not kinds.has("gym"):
			check(false, "%s 有道馆" % t["name"])
		if t["kind"] != "start" and not world.is_walkable(t["pos"]):
			check(false, "%s 中心能走" % t["name"])
	for r in WorldPlan.REGIONS:
		var c: Vector2i = r["center"]
		if gen.region_index(c.x, c.y) != WorldPlan.REGIONS.find(r):
			check(false, "%s 的中心属于自己的区域" % r["name"])
	# 每条道路沿线采样：都能走（铺路或桥）
	var bad := 0
	for s in gen.route_segments:
		var a: Vector2 = s["a"]
		var b: Vector2 = s["b"]
		for i in 9:
			var p := Vector2i(a.lerp(b, (i + 0.5) / 9.0).round())
			if not world.is_walkable(p) and gen.town_at(p).is_empty() and world.building_at(p).is_empty():
				bad += 1
	check(bad == 0, "道路沿线都能走（不通的点：%d）" % bad)
	check(world.area_name(WorldPlan.TOWNS[1]["pos"]) == WorldPlan.TOWNS[1]["name"], "城镇地名")
	var ch := gen.generate_chunk(Vector2i(100, 100))
	check(ch == gen.generate_chunk(Vector2i(100, 100)), "同一区块每次生成都一样")


func _battle_check() -> void:
	var battle: Battle = main.battle
	var wild := Monster.create("chongchong", 2)
	var foes: Array[Monster] = [wild]
	var result := await _auto_battle(foes, {})
	check(result == "won" or result == "caught", "自动操作能打完一场野外战斗（结果：%s）" % result)
	check(not battle.visible, "战斗结束后关闭战斗画面")

	# 训练师战斗：用一只高等级的首发，确保能连续打倒两只对手
	Game.party.push_front(Monster.create("huohu2", 30))
	var money_before: int = Game.money
	var info: Dictionary = World.NPCS[1]["trainer"]
	var team: Array[Monster] = []
	for entry in info["team"]:
		team.append(Monster.create(entry[0], int(entry[1])))
	result = await _auto_battle(team, info)
	check(result == "won", "能打赢训练师的两只奇异兽（结果：%s）" % result)
	check(team[0].is_fainted() and team[1].is_fainted(), "训练师的两只都被打倒")
	check(Game.money == money_before + int(info["reward"]), "打赢训练师拿到奖金")


## 自动按键打完一场战斗：对话直接跳过，选项总是点第一个可用按钮
func _auto_battle(foes: Array[Monster], info: Dictionary) -> String:
	var battle: Battle = main.battle
	var dialog: DialogBox = main.dialog
	var out := [""]
	var run_battle := func():
		out[0] = await battle.run(foes, 1, info)
	run_battle.call()
	var start := Time.get_ticks_msec()
	while out[0] == "" and (Time.get_ticks_msec() - start) / 1000.0 < TIMEOUT:
		await get_tree().process_frame
		if dialog._waiting:
			dialog._finish()
		elif dialog.grid.get_child_count() > 0:
			for b in dialog.grid.get_children():
				if b is Button and not b.disabled:
					b.pressed.emit()
					break
	return out[0]
