class_name Player
extends Node2D
## 网格移动的玩家角色。每走完一格发出 stepped 信号。

signal stepped(cell: Vector2i)

const WALK_TIME := 0.18
const RUN_TIME := 0.105

var world: World
var cell := Vector2i(9, 8)
var target := Vector2i(9, 8)
var dir := Vector2i.DOWN
var moving := false
var active := true
var steps := 0
var _progress := 0.0
var _duration := WALK_TIME


func _ready() -> void:
	var cam := Camera2D.new()
	cam.offset = Vector2(0, -8)
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = World.W * World.T
	cam.limit_bottom = World.H * World.T
	add_child(cam)
	cam.make_current()
	place(cell)


func place(c: Vector2i) -> void:
	cell = c
	target = c
	moving = false
	position = cell_to_pos(c)
	queue_redraw()


static func cell_to_pos(c: Vector2i) -> Vector2:
	return Vector2(c.x * World.T + 8, (c.y + 1) * World.T)


func facing_cell() -> Vector2i:
	return cell + dir


func _process(delta: float) -> void:
	if moving:
		_progress += delta / _duration
		if _progress >= 1.0:
			moving = false
			cell = target
			position = cell_to_pos(cell)
			steps += 1
			queue_redraw()
			stepped.emit(cell)
		else:
			position = cell_to_pos(cell).lerp(cell_to_pos(target), _progress)
			queue_redraw()
	if not moving and active:
		var d := _input_dir()
		if d != Vector2i.ZERO:
			try_move(d)


func _input_dir() -> Vector2i:
	if Input.is_action_pressed("move_up"):
		return Vector2i.UP
	if Input.is_action_pressed("move_down"):
		return Vector2i.DOWN
	if Input.is_action_pressed("move_left"):
		return Vector2i.LEFT
	if Input.is_action_pressed("move_right"):
		return Vector2i.RIGHT
	return Vector2i.ZERO


func try_move(d: Vector2i) -> void:
	dir = d
	queue_redraw()
	var next := cell + d
	if world.is_walkable(next):
		target = next
		moving = true
		_progress = 0.0
		_duration = RUN_TIME if Input.is_action_pressed("run") else WALK_TIME


func _draw() -> void:
	var step := 0
	if moving:
		step = 1 if (steps + (1 if _progress > 0.5 else 0)) % 2 else 2
	Art.character(self, "player", dir, step)
	# 站在高草里时，在脚前补画一层草叶，看起来像被草挡住
	var here := target if moving and _progress > 0.5 else cell
	if world and world.tile_at(here) == World.TALL_GRASS:
		Art.tall_grass_front(self)
