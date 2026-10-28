extends Node
## 导出奈尔斯地区全图鸟瞰图：每 STEP 格采样一个像素，再标出道路和城镇。
## godot --headless --path . res://tests/map_overview.tscn
## 图片保存在 user://screenshots/overview.png。

const STEP := 16


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute("user://screenshots")
	var gen := World.generator()
	var n := WorldGen.SIZE / STEP
	var img := Image.create(n, n, false, Image.FORMAT_RGB8)
	var t0 := Time.get_ticks_msec()
	for py in n:
		for px in n:
			var c := Vector2i(px * STEP + STEP / 2, py * STEP + STEP / 2)
			img.set_pixel(px, py, WorldGen.overview_color(gen.sample_cell(c)))
	print("overview sampled in %d ms" % (Time.get_ticks_msec() - t0))
	for seg in gen.route_segments:
		var a: Vector2 = Vector2(seg["a"]) / STEP
		var b: Vector2 = Vector2(seg["b"]) / STEP
		var steps := int(a.distance_to(b)) + 1
		for i in steps + 1:
			var p := a.lerp(b, float(i) / steps)
			_dot(img, Vector2i(p), 0, Color("#7a4a22"))
	for t in WorldPlan.TOWNS:
		var col := Color("#ffffff")
		if not (t["gym"] as Dictionary).is_empty():
			col = Color("#ff4040")
		if t["kind"] == "league":
			col = Color("#ffd700")
		_dot(img, Vector2i(t["pos"]) / STEP, 3, Color.BLACK)
		_dot(img, Vector2i(t["pos"]) / STEP, 2, col)
	img.save_png("user://screenshots/overview.png")
	print("saved overview ", img.get_size())
	get_tree().quit()


func _dot(img: Image, p: Vector2i, r: int, col: Color) -> void:
	for y in range(-r, r + 1):
		for x in range(-r, r + 1):
			var q := p + Vector2i(x, y)
			if q.x >= 0 and q.y >= 0 and q.x < img.get_width() and q.y < img.get_height():
				img.set_pixelv(q, col)
