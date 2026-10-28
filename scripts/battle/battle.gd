class_name Battle
extends CanvasLayer
## 回合制野外战斗：战斗 / 兽球 / 换人 / 逃跑。
## run() 结束后返回 true 表示全灭（需要送回治疗所）。

var dialog: DialogBox
var view: BattleView
var wild: Monster
var me: Monster
var zone := 0

# 以下状态供 BattleView 绘制
var show_enemy := true
var show_me := false
var disp_enemy_hp := 0.0
var disp_me_hp := 0.0
var shake_enemy_at := -10.0
var shake_me_at := -10.0
var faint_enemy_at := -1.0
var ball_at := -1.0
var ball_shake_at := -10.0
var flash_at := -10.0


func _ready() -> void:
	layer = 5
	view = BattleView.new()
	view.theme = Game.ui_theme
	view.battle = self
	view.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	view.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(view)
	hide()


func _process(delta: float) -> void:
	if not visible or wild == null:
		return
	disp_enemy_hp = move_toward(disp_enemy_hp, wild.hp, wild.max_hp() * delta / 0.7)
	disp_me_hp = move_toward(disp_me_hp, me.hp, me.max_hp() * delta / 0.7)
	view.queue_redraw()


static func now() -> float:
	return Time.get_ticks_msec() / 1000.0


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


static func damage(attacker: Monster, defender: Monster, move: String, rng: RandomNumberGenerator) -> Dictionary:
	var mv: Dictionary = Data.MOVES[move]
	var base := int((2.0 * attacker.level / 5.0 + 2.0) * mv["power"] * attacker.stat("atk") / defender.stat("def") / 50.0) + 2
	var stab := 1.5 if mv["type"] == attacker.type() else 1.0
	var eff := Data.effectiveness(mv["type"], defender.type())
	var crit := 1.5 if rng.randf() < 0.0625 else 1.0
	var n := maxi(1, int(base * stab * eff * crit * rng.randf_range(0.85, 1.0)))
	return {"amount": n, "eff": eff, "crit": crit > 1.0}


## 捕获概率：满血时约为 rate/3，越接近 0 血越接近 rate，再乘 1.5 并封顶 95%
static func catch_chance(m: Monster) -> float:
	var mx := float(m.max_hp())
	return minf(0.95, (3.0 * mx - 2.0 * m.hp) / (3.0 * mx) * float(m.species()["catch_rate"]) * 1.5)


func run(wild_monster: Monster, zone_index: int) -> bool:
	wild = wild_monster
	zone = zone_index
	me = Game.first_alive()
	Game.seen[wild.key] = true
	show_enemy = true
	show_me = false
	disp_enemy_hp = wild.hp
	disp_me_hp = me.hp
	faint_enemy_at = -1.0
	ball_at = -1.0
	flash_at = now()
	show()

	var blackout := false
	await dialog.say("野生的 %s 从草丛里跳了出来！" % wild.species_name())
	show_me = true
	await dialog.say("去吧，%s！" % me.species_name(), 0.9)
	while true:
		var act: Dictionary = await _choose_action()
		var ended := false
		match act["kind"]:
			"run":
				if Game.rng.randf() < 0.8 or me.stat("spd") >= wild.stat("spd"):
					await dialog.say("顺利逃走了！", 0.9)
					ended = true
				else:
					await dialog.say("没能逃掉！", 0.9)
					await _enemy_turn()
			"ball":
				if await _throw_ball():
					ended = true
				else:
					await _enemy_turn()
			"switch":
				show_me = false
				await dialog.say("回来吧，%s！" % me.species_name(), 0.8)
				_send_out(Game.party[act["index"]])
				await dialog.say("上吧，%s！" % me.species_name(), 0.8)
				await _enemy_turn()
			"fight":
				if me.stat("spd") >= wild.stat("spd"):
					await _attack(me, wild, act["move"])
					await _enemy_turn()
				else:
					await _enemy_turn()
					if not me.is_fainted():
						await _attack(me, wild, act["move"])
		if ended:
			break
		if wild.is_fainted():
			faint_enemy_at = now()
			await dialog.say("野生的 %s 倒下了！" % wild.species_name())
			await _gain_xp(me, wild)
			break
		if me.is_fainted():
			await dialog.say("%s 倒下了！" % me.species_name())
			show_me = false
			if Game.alive_count() == 0:
				await dialog.say("你身边已经没有能战斗的奇异兽了……")
				await dialog.say("你眼前一黑，慌忙跑回了治疗所。")
				Game.heal_all()
				blackout = true
				break
			var i: int = await _pick_party("换哪只上场？", false)
			_send_out(Game.party[i])
			await dialog.say("上吧，%s！" % me.species_name(), 0.8)

	hide()
	dialog.close()
	wild = null
	me = null
	return blackout


func _send_out(m: Monster) -> void:
	me = m
	disp_me_hp = m.hp
	show_me = true


func _choose_action() -> Dictionary:
	while true:
		var i: int = await dialog.choose("%s 要做什么？" % me.species_name(),
			["战斗", "兽球 ×%d" % Game.balls, "队伍", "逃跑"],
			[false, Game.balls <= 0, Game.alive_count() < 2, false])
		if i == 0:
			var labels: Array = []
			for mv in me.moves:
				labels.append("%s · %s" % [mv, Data.MOVES[mv]["type"]])
			labels.append("返回")
			var j: int = await dialog.choose("选择招式", labels)
			if j < me.moves.size():
				return {"kind": "fight", "move": me.moves[j]}
		elif i == 1:
			return {"kind": "ball"}
		elif i == 2:
			var j: int = await _pick_party("换哪只上场？", true)
			if j >= 0:
				return {"kind": "switch", "index": j}
		else:
			return {"kind": "run"}
	return {}


## 返回队伍下标；可取消时选“返回”得到 -1
func _pick_party(prompt: String, cancellable: bool) -> int:
	var labels: Array = []
	var disabled: Array = []
	for m in Game.party:
		labels.append("%s Lv.%d  %d/%d" % [m.species_name(), m.level, m.hp, m.max_hp()])
		disabled.append(m.is_fainted() or m == me)
	if cancellable:
		labels.append("返回")
		disabled.append(false)
	var i: int = await dialog.choose(prompt, labels, disabled)
	return -1 if i >= Game.party.size() else i


func _attack(attacker: Monster, defender: Monster, move: String) -> void:
	var wild_side := attacker == wild
	await dialog.say("%s%s 使用了 %s！" % ["野生的 " if wild_side else "", attacker.species_name(), move], 0.8)
	var r := damage(attacker, defender, move, Game.rng)
	defender.hp = maxi(0, defender.hp - int(r["amount"]))
	if wild_side:
		shake_me_at = now()
	else:
		shake_enemy_at = now()
	await _wait(0.65)
	if r["crit"]:
		await dialog.say("会心一击！", 0.9)
	if r["eff"] > 1.0:
		await dialog.say("效果拔群！", 0.9)
	elif r["eff"] < 1.0:
		await dialog.say("效果不太好……", 0.9)


func _enemy_turn() -> void:
	if wild.is_fainted():
		return
	var mv: String = wild.moves[Game.rng.randi_range(0, wild.moves.size() - 1)]
	await _attack(wild, me, mv)


func _throw_ball() -> bool:
	Game.balls -= 1
	ball_at = now()
	await _wait(0.35)
	show_enemy = false
	await dialog.say("你扔出了兽球！", 0.7)
	var per_shake := pow(catch_chance(wild), 1.0 / 3.0)
	var fail_lines := ["哎呀！它挣脱出来了！", "差一点就抓到了！", "可恶，就差一点！"]
	for i in 3:
		ball_shake_at = now()
		await _wait(0.65)
		if Game.rng.randf() > per_shake:
			ball_at = -1.0
			show_enemy = true
			await dialog.say(fail_lines[i], 1.0)
			return false
	await dialog.say("好耶！抓到了 %s！" % wild.species_name())
	if Game.add_caught(wild):
		await dialog.say("%s 加入了队伍。" % wild.species_name())
	else:
		await dialog.say("队伍满了，%s 被送进了存储箱。" % wild.species_name())
	return true


func _gain_xp(m: Monster, defeated: Monster) -> void:
	var gain := maxi(1, int(int(defeated.species()["xp"]) * defeated.level / 7.0))
	m.xp += gain
	await dialog.say("%s 获得了 %d 点经验值。" % [m.species_name(), gain], 1.15)
	while m.xp >= m.xp_for_next():
		var learned := m.level_up()
		disp_me_hp = m.hp
		await dialog.say("%s 升到了 Lv.%d！" % [m.species_name(), m.level])
		for mv in learned:
			if m.moves.size() < 4:
				m.moves.append(mv)
				await dialog.say("%s 学会了 %s！" % [m.species_name(), mv])
			else:
				var forgot: String = m.moves.pop_front()
				m.moves.append(mv)
				await dialog.say("%s 忘掉了 %s，学会了 %s！" % [m.species_name(), forgot, mv])
