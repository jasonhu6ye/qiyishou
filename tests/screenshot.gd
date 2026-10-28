extends Node
## 截图脚本：在有显示环境时运行（CI 里用 xvfb），把大地图和战斗画面各截一张。
## godot --path . --rendering-driver opengl3 res://tests/screenshot.tscn
## 图片保存在 user://screenshots/，CI 会作为构建产物上传。

var main: Node


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute("user://screenshots")
	Game.delete_save()
	Game.reset()
	Game.party.append(Monster.create("huohu", 6))
	Game.party.append(Monster.create("paowa", 5))
	Game.player_cell = Vector2i(13, 9)
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
	main.battle.run(Monster.create("tantan", 6), 1)
	var start := Time.get_ticks_msec()
	while main.dialog.grid.get_child_count() == 0 and Time.get_ticks_msec() - start < 8000:
		await _frames(2)
		if main.dialog._waiting:
			main.dialog._finish()
	await get_tree().create_timer(0.8).timeout
	await _capture("battle")
	Game.delete_save()
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _capture(shot_name: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var path := "user://screenshots/%s.png" % shot_name
	img.save_png(path)
	print("saved ", ProjectSettings.globalize_path(path), " ", img.get_size())
