class_name Battle
extends CanvasLayer
## 回合制战斗：战斗 / 背包 / 换人 / 逃跑。野外战斗一只对手；训练师战斗按顺序派出整队。
## run() 返回结果："won" 打赢、"caught" 抓到、"fled" 逃跑、"lost" 全灭（已回满血，需要送回治疗所）。

var dialog: DialogBox
var view: BattleView
var wild: Monster  ## 当前在场的对手（训练师战斗时也用这个字段）
var me: Monster
var zone := 0
var trainer := {}

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
var lunge_enemy_at := -10.0
var lunge_me_at := -10.0
var fx_at := -10.0
var fx_type := ""
var fx_on_enemy := true


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


func is_trainer_battle() -> bool:
	return not trainer.is_empty()


func _foe_name() -> String:
	return ("对手的 " if is_trainer_battle() else "野生的 ") + wild.species_name()


func run(enemies: Array[Monster], zone_index: int, trainer_info := {}) -> String:
	zone = zone_index
	trainer = trainer_info
	var queue := enemies.duplicate()
	wild = queue.pop_front()
	me = Game.first_alive()
	for e in enemies:
		Game.seen[e.key] = true
	show_enemy = true
	show_me = false
	disp_enemy_hp = wild.hp
	disp_me_hp = me.hp
	faint_enemy_at = -1.0
	ball_at = -1.0
	flash_at = now()
	show()

	var result := ""
	if is_trainer_battle():
		await dialog.say("%s 发起了对战！" % trainer["name"])
		await dialog.say("%s 派出了 %s！" % [trainer["name"], wild.species_name()], 1.0)
	else:
		await dialog.say("野生的 %s 从草丛里跳了出来！" % wild.species_name())
	show_me = true
	await dialog.say("去吧，%s！" % me.species_name(), 0.9)
	while result == "":
		var act: Dictionary = await _choose_action()
		var kind: String = act["kind"]
		if kind == "run":
			if is_trainer_battle():
				await dialog.say("不能从训练师对战中逃跑！", 1.0)
			elif Game.rng.randf() < 0.8 or me.stat("spd") >= wild.stat("spd"):
				await dialog.say("顺利逃走了！", 0.9)
				result = "fled"
			else:
				await dialog.say("没能逃掉！", 0.9)
				await _enemy_turn()
		elif kind == "ball":
			if await _throw_ball():
				result = "caught"
			else:
				await _enemy_turn()
		elif kind == "potion":
			var target: Monster = Game.party[act["index"]]
			var healed: int = Game.use_potion(target)
			if target == me:
				disp_me_hp = me.hp - healed
			await dialog.say("%s 回复了 %d 点 HP。" % [target.species_name(), healed], 1.0)
			await _enemy_turn()
		elif kind == "switch":
			show_me = false
			await dialog.say("回来吧，%s！" % me.species_name(), 0.8)
			_send_out(Game.party[act["index"]])
			await dialog.say("上吧，%s！" % me.species_name(), 0.8)
			await _enemy_turn()
		elif kind == "fight":
			if me.stat("spd") >= wild.stat("spd"):
				await _attack(me, wild, act["move"])
				await _enemy_turn()
			else:
				await _enemy_turn()
				if not me.is_fainted():
					await _attack(me, wild, act["move"])
		if result != "":
			break
		if wild.is_fainted():
			faint_enemy_at = now()
			await dialog.say("%s 倒下了！" % _foe_name())
			await _gain_xp(me, wild)
			if not queue.is_empty():
				wild = queue.pop_front()
				disp_enemy_hp = wild.hp
				faint_enemy_at = -1.0
				show_enemy = true
				await dialog.say("%s 派出了 %s！" % [trainer["name"], wild.species_name()], 1.0)
				continue
			result = "won"
			if is_trainer_battle():
				await dialog.say("你打败了 %s！" % trainer["name"])
				await dialog.say(trainer["defeat"])
				Game.money += int(trainer["reward"])
				await dialog.say("获得了 %d 金币。" % int(trainer["reward"]))
			else:
				var coins := wild.level * 4
				Game.money += coins
				await dialog.say("在草丛里捡到了 %d 金币。" % coins, 1.0)
			break
		if me.is_fainted():
			await dialog.say("%s 倒下了！" % me.species_name())
			show_me = false
			if Game.alive_count() == 0:
				await dialog.say("你身边已经没有能战斗的幻兽了……")
				await dialog.say("你眼前一黑，慌忙跑回了治疗所。")
				Game.heal_all()
				result = "lost"
				break
			var i: int = await _pick_party("换哪只上场？", false)
			_send_out(Game.party[i])
			await dialog.say("上吧，%s！" % me.species_name(), 0.8)

	hide()
	dialog.close()
	wild = null
	me = null
	trainer = {}
	return result


func _send_out(m: Monster) -> void:
	me = m
	disp_me_hp = m.hp
	show_me = true


func _choose_action() -> Dictionary:
	while true:
		var i: int = await dialog.choose("%s 要做什么？" % me.species_name(),
			["战斗", "背包", "队伍", "逃跑"],
			[false, false, Game.alive_count() < 2, false])
		if i == 0:
			var labels: Array = []
			for mv in me.moves:
				labels.append("%s · %s" % [mv, Data.MOVES[mv]["type"]])
			labels.append("返回")
			var j: int = await dialog.choose("选择招式", labels)
			if j < me.moves.size():
				return {"kind": "fight", "move": me.moves[j]}
		elif i == 1:
			var act: Dictionary = await _bag_menu()
			if not act.is_empty():
				return act
		elif i == 2:
			var j: int = await _pick_party("换哪只上场？", true)
			if j >= 0:
				return {"kind": "switch", "index": j}
		else:
			return {"kind": "run"}
	return {}


## 背包：返回要执行的动作，取消返回空字典
func _bag_menu() -> Dictionary:
	var j: int = await dialog.choose("背包", ["兽球 ×%d" % Game.balls, "伤药 ×%d" % Game.potions, "返回"],
		[Game.balls <= 0, Game.potions <= 0, false])
	if j == 0:
		if is_trainer_battle():
			await dialog.say("不能抓别人的幻兽！", 1.0)
			return {}
		return {"kind": "ball"}
	if j == 1:
		var labels: Array = []
		var disabled: Array = []
		for m in Game.party:
			labels.append("%s  %d/%d" % [m.species_name(), m.hp, m.max_hp()])
			disabled.append(m.is_fainted() or m.hp >= m.max_hp())
		labels.append("返回")
		disabled.append(false)
		var k: int = await dialog.choose("给谁用伤药？（回复 %d HP）" % Data.POTION_HEAL, labels, disabled)
		if k < Game.party.size():
			return {"kind": "potion", "index": k}
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
	var foe_side := attacker == wild
	var who := _foe_name() if foe_side else attacker.species_name()
	await dialog.say("%s 使用了 %s！" % [who, move], 0.8)
	if foe_side:
		lunge_enemy_at = now()
	else:
		lunge_me_at = now()
	fx_type = Data.MOVES[move]["type"]
	fx_on_enemy = not foe_side
	fx_at = now()
	await _wait(BattleView.FX_TIME)
	var r := damage(attacker, defender, move, Game.rng)
	defender.hp = maxi(0, defender.hp - int(r["amount"]))
	if foe_side:
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
	if is_trainer_battle():
		gain = int(gain * 1.5)
	m.xp += gain
	await dialog.say("%s 获得了 %d 点经验值。" % [m.species_name(), gain], 1.15)
	while m.xp >= m.xp_for_next():
		var learned := m.level_up()
		disp_me_hp = m.hp
		await dialog.say("%s 升到了 Lv.%d！" % [m.species_name(), m.level])
		await _learn(m, learned)
	await _maybe_evolve(m)


func _learn(m: Monster, learned: Array[String]) -> void:
	for mv in learned:
		if m.moves.has(mv):
			continue
		if m.moves.size() < 4:
			m.moves.append(mv)
			await dialog.say("%s 学会了 %s！" % [m.species_name(), mv])
		else:
			var forgot: String = m.moves.pop_front()
			m.moves.append(mv)
			await dialog.say("%s 忘掉了 %s，学会了 %s！" % [m.species_name(), forgot, mv])


func _maybe_evolve(m: Monster) -> void:
	var into := Data.evolution_for(m)
	if into == "":
		return
	var old_name := m.species_name()
	await dialog.say("咦？%s 的样子发生了变化……" % old_name)
	for i in 3:
		flash_at = now()
		shake_me_at = now()
		await _wait(0.5)
	m.evolve(into)
	disp_me_hp = m.hp
	flash_at = now()
	Game.seen[into] = true
	Game.caught[into] = true
	await dialog.say("恭喜！%s 进化成了 %s！" % [old_name, m.species_name()])
	# 新形态在当前等级会的招式（比如进化等级正好是学招等级）
	var learned: Array[String] = []
	for entry in m.species()["moves"]:
		if int(entry[0]) == m.level:
			learned.append(entry[1])
	await _learn(m, learned)
