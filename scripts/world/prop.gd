class_name Prop
extends Node2D
## 地图上的静态物件（树、房屋、NPC）。原点在物件“脚底”，供 Y 排序使用。

var kind := "tree"
var house := {}
var npc := {}
var facing := Vector2i.DOWN
## 训练师发现玩家时头顶显示感叹号
var alerted := false


func _draw() -> void:
	match kind:
		"tree":
			Art.tree(self)
		"house":
			Art.house(self, house["kind"])
		"npc":
			Art.character(self, npc["sprite"], facing, 0)
			if alerted:
				Art.alert(self)


func set_alerted(on: bool) -> void:
	alerted = on
	queue_redraw()


func face(dir: Vector2i) -> void:
	facing = dir
	queue_redraw()
