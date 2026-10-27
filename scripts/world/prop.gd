class_name Prop
extends Node2D
## 地图上的静态物件（树、房屋、NPC）。原点在物件“脚底”，供 Y 排序使用。

var kind := "tree"
var house := {}
var npc := {}
var facing := Vector2i.DOWN


func _draw() -> void:
	match kind:
		"tree":
			Art.tree(self)
		"house":
			var r: Rect2i = house["rect"]
			var door_x := float(int(r.size.x / 2) * World.T)
			Art.house(self, Vector2(r.size) * World.T, Color(house["roof"]), house["heal"], door_x)
		"npc":
			Art.person(self, facing, 0, Color(npc["body"]), Color(npc["hat"]))


func face(dir: Vector2i) -> void:
	facing = dir
	queue_redraw()
