extends Node
## 截图脚本：在有显示环境时运行（CI 里用 xvfb），截取起始小镇、训练师、各地貌野外、训练师战斗和招式特效画面。
## godot --path . --rendering-driver opengl3 res://tests/screenshot.tscn
## 图片保存在 user://screenshots/，CI 会作为构建产物上传。

var main: Node


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute("user://screenshots")
	Game.delete_save()
	Game.reset()
	Game.party.append(Monster.create("huohu2", 18))
	Game.party.append(Monster.create("paowa", 9))
	Game.player_cell = WorldGen.START_ORIGIN + Vector2i(10, 8)
	Game.save_game()
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await _frames(10)
	main.player.dir = Vector2i.UP
	main.player.queue_redraw()
	main.dialog.say("老爷爷：年轻人，草丛里藏着野生的奇异兽，走进去就可能遇到。")
	await _frames(5)
	await _capture("world")

	main.dialog.close()
	main.player.place(WorldGen.START_ORIGIN + Vector2i(34, 15))
	main.player.dir = Vector2i.RIGHT
	main._area = main.world.area_name(main.player.cell)
	main.hud.refresh(main._area)
	if main.hud._tween:
		main.hud._tween.kill()
	main.hud.toast.modulate.a = 0.0
	var ajie: Prop = main.world.npc_props[1]
	ajie.set_alerted(true)
	await _frames(5)
	await _capture("route2")
	ajie.set_alerted(false)

	# 各地貌：传送到几个城镇附近的野外
	for t in ["senyu", "nitan", "chaoxi", "lvzhou", "rongyan", "yanbao", "jinghu", "shuangxue"]:
		var spot := _wild_spot(t)
		if spot == Vector2i(-1, -1):
			continue
		main.player.place(spot)
		main.world.refresh_now()
		main._area = main.world.area_name(spot)
		main.hud.refresh(main._area)
		if main.hud._tween:
			main.hud._tween.kill()
		main.hud.toast.modulate.a = 0.0
		await _frames(4)
		await _capture("biome_" + t)

	main._set_state(main.State.BATTLE)
	var info: Dictionary = World.NPCS[1]["trainer"]
	var team: Array[Monster] = []
	for entry in info["team"]:
		team.append(Monster.create(entry[0], int(entry[1])))
	main.battle.run(team, 1, info)
	var start := Time.get_ticks_msec()
	while main.dialog.grid.get_child_count() == 0 and Time.get_ticks_msec() - start < 8000:
		await _frames(2)
		if main.dialog._waiting:
			main.dialog._finish()
	await get_tree().create_timer(0.8).timeout
	await _capture("battle")
	main.battle.lunge_me_at = Battle.now() - 0.15
	main.battle.fx_type = "火"
	main.battle.fx_on_enemy = true
	main.battle.fx_at = Battle.now() - 0.25
	await _capture("battle_fx")
	Game.delete_save()
	get_tree().quit()


## 城镇外 30 格左右、能走的一个格子
func _wild_spot(town_id: String) -> Vector2i:
	var pos := Vector2i(-1, -1)
	for t in WorldPlan.TOWNS:
		if t["id"] == town_id:
			pos = t["pos"]
	if pos.x < 0:
		return pos
	for r in range(30, 60, 3):
		for d in [Vector2i(r, 0), Vector2i(-r, 0), Vector2i(0, r), Vector2i(0, -r), Vector2i(r, r), Vector2i(-r, r)]:
			var c: Vector2i = pos + d
			if main.world.is_walkable(c) and main.world.gen.town_at(c).is_empty():
				return c
	return Vector2i(-1, -1)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _capture(shot_name: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var path := "user://screenshots/%s.png" % shot_name
	img.save_png(path)
	print("saved ", ProjectSettings.globalize_path(path), " ", img.get_size())
