import math, sys

from queue import PriorityQueue



class Utils:
	infinity = 42424242


	@staticmethod
	def debug(*args, **kwargs):
		print(*args, **kwargs, file=sys.stderr)


	@staticmethod
	def get_ints_from_line():
		return [int(x) for x in input().split()]


	@staticmethod
	def get_point_to_point_distance(entity_1, entity_2):
		return math.dist(
			(entity_1.x, entity_1.y),
			(entity_2.x, entity_2.y)
		)



class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y



class Game:
	def __init__(self):
		self.round = 0

		self.me = Player(self)
		self.me.init_my_coordinates()

		self.opponent = Player(self)
		self.opponent.init_opponent_coordinates()

		self.heroes_per_player = int(input())

		self.monsters = Monsters(self)
		self.my_heroes = MyHeroes(self)
		self.opponent_heroes = OpponentHeroes(self)

		self.entities = Entities(self)


	def run(self):
		while True:
			self.clear()
			self.parse()
			self.update()
			self.round += 1


	def clear(self):
		self.my_heroes.clear()
		self.monsters.clear()
		self.opponent_heroes.clear()


	def parse(self):
		self.me.parse_health_and_mana()
		self.opponent.parse_health_and_mana()
		self.entities.parse_entities()


	def update(self):
		self.my_heroes.update()



class Player:
	def __init__(self, parent_game):
		self.parent_game = parent_game

		self.base_target_radius = 5000

		self.base_vision_radius = 6000

		self.near_base_radius = self.base_vision_radius + 1500


	def init_my_coordinates(self):
		self.x, self.y = Utils.get_ints_from_line()


	def init_opponent_coordinates(self):
		if self.parent_game.me.x == 0:
			self.x, self.y = 17630, 9000
		else:
			self.x, self.y = 0, 0


	def parse_health_and_mana(self):
		self.health, self.mana = Utils.get_ints_from_line()



class Monsters:
	def __init__(self, parent_game):
		self.parent_game = parent_game


	def clear(self):
		self.monsters = []


	def add_monster(self, entity):
		self.monsters.append(
			Monster(self, entity)
		)



class MyHeroes:
	def __init__(self, parent_game):
		self.parent_game = parent_game

		self.my_heroes = []


	def clear(self):
		self.my_hero_index = 0

		self.clear_my_heroes()


	def clear_my_heroes(self):
		for my_hero in self.my_heroes:
			my_hero.clear()


	def add_or_update_my_next_hero(self, entity):
		my_heroes_len = len(self.my_heroes)

		if my_heroes_len == 0:
			self.my_heroes.append(
				HeroDefender(
					self,
					entity,
					Point(
						7000,
						2600
					)
				)
			)
		elif my_heroes_len == 1:
			self.my_heroes.append(
				HeroDefender(
					self,
					entity,
					Point(
						4500,
						6200
					)
				)
			)
		elif my_heroes_len == 2:
			self.my_heroes.append(
				HeroAttacker(
					self,
					entity,
					Point(
						9000,
						4500
					),
					# Point(
					# 	11000,
					# 	4000
					# )
				)
			)
		else:
			self.my_heroes[self.my_hero_index].update(entity)
			self.my_hero_index += 1


	def update(self):
		while self.a_hero_has_no_action_assigned():
			self.recalculate_possible_actions()

			_, _, hero, action_info = self.possible_actions.get()

			if not hero.hero_base.action_info:
				hero.hero_base.action_info = action_info

		self.run_hero_actions()

		self.update_heroes_targeted_by_spells_in_previous_round()


	def a_hero_has_no_action_assigned(self):
		return any(my_hero.hero_base.action_info == None for my_hero in self.my_heroes)


	def recalculate_possible_actions(self):
		self.possible_actions = PriorityQueue()

		for my_hero in self.my_heroes:
			if not my_hero.hero_base.action_info:
				my_hero.add_possible_actions()


	def run_hero_actions(self):
		for my_hero in self.my_heroes:
			action_info = my_hero.hero_base.action_info
			action_info["action"](my_hero, action_info, *action_info["action_arguments"])


	def update_heroes_targeted_by_spells_in_previous_round(self):
		for my_hero in self.my_heroes:
			my_hero.update_targeted_by_spell_in_previous_round()



class OpponentHeroes:
	def __init__(self, parent_game):
		self.parent_game = parent_game


	def clear(self):
		self.opponent_heroes = []


	def add_next_opponent_hero(self, entity):
		self.opponent_heroes.append(OpponentHero(self, entity))



class OpponentHero:
	def __init__(self, parent_opponent_heroes, entity):
		self.parent_opponent_heroes = parent_opponent_heroes

		self.hero_base = OpponentHeroBase(self, entity)


class OpponentHeroBase:
	def __init__(self, parent_opponent_hero, entity):
		self.parent_opponent_hero = parent_opponent_hero

		self.entity = entity


class Entities:
	def __init__(self, parent_game):
		self.parent_game = parent_game

		self.monster_type = 0
		self.my_hero_type = 1
		self.opponent_hero_type = 2


	def parse_entities(self):
		self.entity_count = int(input())

		for _ in range(self.entity_count):
			self.add_entity(Entity(self))


	def add_entity(self, entity):
		if entity.type_ == self.monster_type:
			return self.parent_game.monsters.add_monster(entity)
		elif entity.type_ == self.my_hero_type:
			return self.parent_game.my_heroes.add_or_update_my_next_hero(entity)
		elif entity.type_ == self.opponent_hero_type:
			return self.parent_game.opponent_heroes.add_next_opponent_hero(entity)



class Entity:
	def __init__(self, parent_entities):
		self.parent_entities = parent_entities

		id_, type_, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = Utils.get_ints_from_line()

		# Unique identifier
		self.id_ = id_

		# 0 = monster, 1 = your hero, 2 = opponent hero
		self.type_ = type_

		# Position of this entity
		self.x = x
		self.y = y

		# Count down until shield spell fades
		self.shield_life = shield_life

		# Equals 1 when this entity is under a control spell
		self.is_controlled = is_controlled

		# Remaining health of this monster
		self.health = health

		# Velocity of this monster
		# self.vx = vx
		# self.vy = vy

		# If in the base's large circle
		# self.near_base = near_base

		# Given this monster's trajectory, is it a threat to 1 = my base, 2 = the opponent's base, 0 = neither
		self.threat_for = threat_for



class Monster:
	def __init__(self, parent_entities, entity):
		self.parent_entities = parent_entities

		self.entity = entity

		# self.threat_for_none = 0
		self.threat_for_my_base = 1
		self.threat_for_opponent_base = 2

		self.distance_from_my_base = Utils.get_point_to_point_distance(self.entity, self.parent_entities.parent_game.me)
		self.distance_from_opponent_base = Utils.get_point_to_point_distance(self.entity, self.parent_entities.parent_game.opponent)



class ActionBase:
	def get_action_info(self, action, label, weight_method, *action_arguments):
		return {
			"action": action,
			"label": label,
			"weight": int(weight_method(action, action_arguments)),
			"action_arguments": action_arguments
		}


	def add_possible_action(self, action_info):
		self.parent_my_heroes.possible_actions.put((
			action_info["weight"],
			self.get_uncollidable_hash(action_info),
			self,
			action_info
		))


	def get_uncollidable_hash(self, action_info):
		return self.__repr__() + action_info["action"].__repr__() + action_info["action_arguments"].__repr__()


	def get_hero_to_monster_distance(self, monster):
		return self.get_hero_to_entity_distance(monster.entity)


	# TODO: Change this method once the heroes don't beeline the monster anymore.
	def get_hero_to_entity_distance(self, entity):
		return Utils.get_point_to_point_distance(self.hero_base.entity, entity)


	# TODO: Change this method so it predicts where the monster will be, instead of doing the current beelining.
	def move_to_monster(self, action_info, monster):
		self.print_move(action_info, monster.entity.x, monster.entity.y)


	def get_locked_count(self, action, action_arguments):
		total_penalty_weight = 0

		for other_my_hero in self.parent_my_heroes.my_heroes:
			if other_my_hero == self:
				continue

			if self.action_already_locked(other_my_hero, action, action_arguments):
				total_penalty_weight += 1

		return total_penalty_weight


	def action_already_locked(self, other_my_hero, action, action_arguments):
		return (
			other_my_hero.hero_base.action_info and
			other_my_hero.hero_base.action_info["action"] == action and
			other_my_hero.hero_base.action_info["action_arguments"] == action_arguments
		)


	def get_not_threat_for_my_base(self, monster):
		return monster.entity.threat_for != monster.threat_for_my_base


	def get_threat_for_opponent_base(self, monster):
		return monster.entity.threat_for == monster.threat_for_opponent_base


	def get_not_threat_for_opponent_base(self, monster):
		return not self.get_threat_for_opponent_base(monster)


	def get_not_enough_mana_for_cast(self):
		return self.get_mana_threshold_not_reached(10)


	def get_mana_threshold_not_reached(self, mana_threshold):
		return not self.get_mana_threshold_reached(mana_threshold)


	def get_mana_threshold_reached(self, mana_threshold):
		return self.parent_my_heroes.parent_game.me.mana >= mana_threshold


	def get_hero_distance_to_my_base(self):
		return self.get_hero_to_entity_distance(self.parent_my_heroes.parent_game.me)


	def get_hero_distance_to_opponent_base(self):
		return self.get_hero_to_entity_distance(self.parent_my_heroes.parent_game.opponent)


	def get_monster_in_either_base_target_radius(self, monster):
		return self.get_weight_monster_in_my_base_target_radius(monster) or self.get_monster_in_opponent_base_target_radius(monster)


	def get_monster_in_opponent_base_target_radius(self, monster):
		return self.get_monster_distance_to_opponent_base(monster) <= self.parent_my_heroes.parent_game.opponent.base_target_radius


	def get_monster_not_near_opponent_base_radius(self, monster):
		return not self.get_monster_near_opponent_base_radius(monster)


	def get_monster_near_opponent_base_radius(self, monster):
		return self.get_monster_distance_to_opponent_base(monster) <= self.parent_my_heroes.parent_game.me.near_base_radius


	def get_weight_monster_in_my_base_target_radius(self, monster):
		return self.get_monster_distance_to_my_base(monster) <= self.parent_my_heroes.parent_game.me.base_target_radius


	def get_monster_distance_to_my_base(self, monster):
		return monster.distance_from_my_base


	def get_monster_shielded(self, monster):
		return monster.entity.shield_life > 0


	def get_not_in_wind_range(self, monster):
		return self.get_hero_to_monster_distance(monster) > self.hero_base.wind_range


	def get_opponent_not_near_base(self):
		for opponent_hero in self.parent_my_heroes.parent_game.opponent_heroes.opponent_heroes:
			if Utils.get_point_to_point_distance(opponent_hero.hero_base.entity, self.parent_my_heroes.parent_game.me) < self.parent_my_heroes.parent_game.me.near_base_radius:
				return False
		return True


	def get_opponent_not_near_my_hero(self, radius):
		for opponent_hero in self.parent_my_heroes.parent_game.opponent_heroes.opponent_heroes:
			if Utils.get_point_to_point_distance(opponent_hero.hero_base.entity, self.hero_base.entity) < radius:
				return False
		return True


	def get_opponent_near_monster(self, radius, monster):
		for opponent_hero in self.parent_my_heroes.parent_game.opponent_heroes.opponent_heroes:
			if Utils.get_point_to_point_distance(opponent_hero.hero_base.entity, monster.entity) < radius:
				return True
		return False


	def get_monster_is_not_healthy_enough(self, monster_health_threshold, monster):
		return not self.get_monster_is_healthy_enough(monster_health_threshold, monster)


	def get_monster_is_healthy_enough(self, monster_health_threshold, monster):
		return monster.entity.health >= monster_health_threshold


	def get_not_past_round(self, threshold_round):
		return not self.get_past_round(threshold_round)


	def get_past_round(self, threshold_round):
		return self.parent_my_heroes.parent_game.round > threshold_round


	def blow_monster_towards_opponent_base(self, action_info):
		self.print_blow(action_info, self.parent_my_heroes.parent_game.opponent.x, self.parent_my_heroes.parent_game.opponent.y)


	def print_wait(self, action_info):
		print(f"WAIT {action_info['label']} {action_info['weight']}")


	def print_move(self, action_info, x, y):
		print(f"MOVE {x} {y} {action_info['label']} {action_info['weight']}")


	def print_shield(self, action_info, id_):
		print(f"SPELL SHIELD {id_} {action_info['label']} {action_info['weight']}")


	def print_blow(self, action_info, x, y):
		print(f"SPELL WIND {x} {y} {action_info['label']} {action_info['weight']}")


	def print_control(self, action_info, id_, x, y):
		print(f"SPELL CONTROL {id_} {x} {y} {action_info['label']} {action_info['weight']}")



class ActionWait(ActionBase):
	def __init__(self, parent_hero, get_weight_method):
		self.parent_hero = parent_hero

		self.add_wait(get_weight_method)


	def add_wait(self, get_weight_method):
		self.parent_hero.add_possible_action(self.parent_hero.get_action_info(ActionWait.action_wait, "wait", get_weight_method))


	def action_wait(self, action_info):
		self.wait(action_info)


	def wait(self, action_info):
		self.print_wait(action_info)



class ActionRendezvous(ActionBase):
	def __init__(self, parent_hero, get_weight_method):
		self.parent_hero = parent_hero

		self.add_rendezvous(get_weight_method)


	def add_rendezvous(self, get_weight_method):
		self.parent_hero.add_possible_action(self.parent_hero.get_action_info(ActionRendezvous.action_rendezvous, "rendezvous", get_weight_method))


	def action_rendezvous(self, action_info):
		self.print_move(action_info, self.hero_base.rendezvous.x, self.hero_base.rendezvous.y)


	def get_move_to_rendezvous(self):
		return self.get_hero_to_entity_distance(self.hero_base.rendezvous)



class ActionMoveToMonsters(ActionBase):
	def __init__(self, parent_hero, get_weight_method):
		self.parent_hero = parent_hero

		self.add_move_to_monsters(get_weight_method)


	def add_move_to_monsters(self, get_weight_method):
		for monster in self.parent_hero.parent_my_heroes.parent_game.monsters.monsters:
			self.parent_hero.add_possible_action(self.parent_hero.get_action_info(ActionMoveToMonsters.action_move_to_monster, "closest", get_weight_method, monster))


	def action_move_to_monster(self, action_info, monster):
		self.move_to_monster(action_info, monster)



class MyHeroBase:
	def __init__(self, parent_hero, entity, rendezvous):
		self.parent_hero = parent_hero

		self.entity = entity

		self.rendezvous = rendezvous

		self.wind_range = 1280

		self.wind_push_units = 2200

		self.control_range = 2200

		self.shield_range = 2200

		self.action_info = None

		self.targeted_by_spell_in_previous_round = False


	def clear(self):
		self.action_info = None


	def update(self, entity):
		self.entity = entity


	def update_targeted_by_spell_in_previous_round(self):
		self.targeted_by_spell_in_previous_round = self.entity.is_controlled



class ActionMoveToMonstersCloseToMyBase(ActionBase):
	def __init__(self, parent_hero, get_weight_method):
		self.parent_hero = parent_hero

		self.add_move_to_monsters_close_to_my_base(get_weight_method)


	def add_move_to_monsters_close_to_my_base(self, get_weight_method):
		for monster in self.parent_hero.parent_my_heroes.parent_game.monsters.monsters:
			self.parent_hero.add_possible_action(self.parent_hero.get_action_info(ActionMoveToMonstersCloseToMyBase.action_move_to_monster_close_to_my_base, "base",get_weight_method, monster))


	def action_move_to_monster_close_to_my_base(self, action_info, monster):
		self.move_to_monster(action_info, monster)



class ActionBlowAwayFromBase(ActionBase):
	def __init__(self, parent_hero, get_weight_method):
		self.parent_hero = parent_hero

		self.add_blow_away_from_base(get_weight_method)


	def add_blow_away_from_base(self, get_weight_method):
		for monster in self.parent_hero.parent_my_heroes.parent_game.monsters.monsters:
			self.parent_hero.add_possible_action(self.parent_hero.get_action_info(ActionBlowAwayFromBase.action_blow_monster_away_from_base, "blow away base", get_weight_method, monster))


	def action_blow_monster_away_from_base(self, action_info, monster):
		self.blow_monster_towards_opponent_base(action_info)


	def get_monster_not_almost_at_my_base(self, monster):
		return monster.distance_from_my_base > 2000


class ActionShield(ActionBase):
	def shield(self, action_info, entity):
		self.print_shield(action_info, entity.id_)



class ActionShieldSelf(ActionShield):
	def __init__(self, parent_hero, get_weight_method):
		self.parent_hero = parent_hero

		self.add_shield_self(get_weight_method)


	def add_shield_self(self, get_weight_method):
		self.parent_hero.add_possible_action(self.parent_hero.get_action_info(ActionShieldSelf.action_shield_self, "shield self", get_weight_method))


	def action_shield_self(self, action_info):
		self.shield(action_info, self.hero_base.entity)


	def get_was_not_targeted_by_spell(self):
		return not self.hero_base.targeted_by_spell_in_previous_round


	def get_hero_shielded(self):
		return self.hero_base.entity.shield_life > 0



class ActionControlHarasser(ActionBase):
	def __init__(self, parent_hero, get_weight_method):
		self.parent_hero = parent_hero

		self.add_control_harasser(get_weight_method)


	def add_control_harasser(self, get_weight_method):
		for opponent_hero in self.parent_hero.parent_my_heroes.parent_game.opponent_heroes.opponent_heroes:
			self.parent_hero.add_possible_action(self.parent_hero.get_action_info(ActionControlHarasser.action_control_harasser, "control harasser", get_weight_method, opponent_hero))


	def action_control_harasser(self, action_info, opponent_hero):
		self.print_control(action_info, opponent_hero.hero_base.entity.id_, opponent_hero.hero_base.entity.x, opponent_hero.hero_base.entity.y)


	def get_opponent_shielded(self, opponent_hero):
		return opponent_hero.hero_base.entity.shield_life > 0



class HeroDefender(ActionWait, ActionRendezvous, ActionMoveToMonsters, ActionMoveToMonstersCloseToMyBase, ActionBlowAwayFromBase, ActionShieldSelf, ActionControlHarasser):
	def __init__(self, parent_my_heroes, entity, rendezvous):
		self.parent_my_heroes = parent_my_heroes

		self.hero_base = MyHeroBase(self, entity, rendezvous)


	def clear(self):
		self.hero_base.clear()


	def update(self, entity):
		self.hero_base.update(entity)


	def update_targeted_by_spell_in_previous_round(self):
		self.hero_base.update_targeted_by_spell_in_previous_round()


	def add_possible_actions(self):
		ActionWait(self, self.get_weight_action_wait)
		ActionRendezvous(self, self.get_weight_action_rendezvous)
		ActionMoveToMonsters(self, self.get_weight_action_move_to_monster)
		ActionMoveToMonstersCloseToMyBase(self, self.get_weight_action_move_to_monster_close_to_my_base)
		ActionBlowAwayFromBase(self, self.get_weight_action_blow_monster_away_from_base)
		ActionShieldSelf(self, self.get_weight_action_shield_self)
		ActionControlHarasser(self, self.get_weight_action_control_harasser)


	def get_weight_action_wait(self, action, action_arguments):
		return (
			Utils.infinity
		)


	def get_weight_action_rendezvous(self, action, action_arguments):
		return (
			self.get_move_to_rendezvous() * 5 +
			self.get_hero_distance_to_my_base() * 5
		)


	def get_weight_action_move_to_monster(self, action, action_arguments):
		return (
			self.get_locked_count(action, action_arguments) * 30000 +
			self.get_hero_to_monster_distance(*action_arguments) +
			self.get_hero_distance_to_my_base() +
			self.get_not_threat_for_my_base(*action_arguments) * 2000 +
			self.get_monster_distance_to_my_base(*action_arguments)
		)


	def get_weight_action_move_to_monster_close_to_my_base(self, action, action_arguments):
		return (
			self.get_locked_count(action, action_arguments) * 30000 +
			self.get_hero_to_monster_distance(*action_arguments) +
			self.get_not_threat_for_my_base(*action_arguments) * Utils.infinity +
			self.get_monster_distance_to_my_base(*action_arguments)
		)


	def get_weight_action_blow_monster_away_from_base(self, action, action_arguments):
		return (
			self.get_locked_count(action, action_arguments) * Utils.infinity +
			self.get_not_enough_mana_for_cast() * Utils.infinity +
			self.get_not_threat_for_my_base(*action_arguments) * Utils.infinity +
			self.get_not_in_wind_range(*action_arguments) * Utils.infinity +
			self.get_monster_not_almost_at_my_base(*action_arguments) * Utils.infinity +
			self.get_monster_shielded(*action_arguments) * Utils.infinity
		)


	def get_weight_action_shield_self(self, action, action_arguments):
		return (
			self.get_not_enough_mana_for_cast() * Utils.infinity +
			self.get_hero_shielded() * Utils.infinity +
			(self.get_was_not_targeted_by_spell() and self.get_opponent_not_near_base()) * Utils.infinity +
			self.get_opponent_not_near_my_hero(3100) * Utils.infinity
		)


	def get_weight_action_control_harasser(self, action, action_arguments):
		return (
			self.get_locked_count(action, action_arguments) * Utils.infinity +
			self.get_not_enough_mana_for_cast() * Utils.infinity +
			self.get_opponent_shielded(*action_arguments) * Utils.infinity +
			self.get_not_past_round(100) * Utils.infinity +
			# 10000
			Utils.infinity
		)



class ActionControl(ActionBase):
	def __init__(self, parent_hero, get_weight_method):
		self.parent_hero = parent_hero

		self.add_control(get_weight_method)


	def add_control(self, get_weight_method):
		for monster in self.parent_hero.parent_my_heroes.parent_game.monsters.monsters:
			self.parent_hero.add_possible_action(self.parent_hero.get_action_info(ActionControl.action_control, "control", get_weight_method, monster))


	def action_control(self, action_info, monster):
		self.control(action_info, monster)


	def control(self, action_info, monster):
		self.print_control(action_info, monster.entity.id_, self.parent_my_heroes.parent_game.opponent.x, self.parent_my_heroes.parent_game.opponent.y)


	def get_not_in_control_range(self, monster):
		return self.get_hero_to_monster_distance(monster) > self.hero_base.control_range



class ActionShieldMonster(ActionShield):
	def __init__(self, parent_hero, get_weight_method):
		self.parent_hero = parent_hero

		self.add_shield_monster(get_weight_method)


	def add_shield_monster(self, get_weight_method):
		for monster in self.parent_hero.parent_my_heroes.parent_game.monsters.monsters:
			self.parent_hero.add_possible_action(self.parent_hero.get_action_info(ActionShieldMonster.action_shield_monster, "shield", get_weight_method, monster))


	def action_shield_monster(self, action_info, monster):
		self.shield(action_info, monster.entity)


	def get_not_in_shield_range(self, monster):
		return self.get_hero_to_monster_distance(monster) > self.hero_base.shield_range


	def get_monster_distance_to_opponent_base(self, monster):
		return monster.distance_from_opponent_base


	def get_not_threshold_monster_count_in_radius_around_point(self, threshold_monster_count, radius, point):
		monsters_around_point = 0

		for monster in self.parent_my_heroes.parent_game.monsters.monsters:
			if Utils.get_point_to_point_distance(monster.entity, point) <= radius:
				monsters_around_point += 1

		return monsters_around_point < threshold_monster_count



class ActionDunkMonster(ActionBase):
	def __init__(self, parent_hero, get_weight_method):
		self.parent_hero = parent_hero

		self.add_dunk_monster(get_weight_method)


	def add_dunk_monster(self, get_weight_method):
		for monster in self.parent_hero.parent_my_heroes.parent_game.monsters.monsters:
			self.parent_hero.add_possible_action(self.parent_hero.get_action_info(ActionDunkMonster.action_dunk_monster, "dunk monster", get_weight_method, monster))


	def action_dunk_monster(self, action_info, monster):
		self.blow_monster_towards_opponent_base(action_info)


	def get_monster_not_in_dunking_radius(self, monster):
		return not self.get_monster_in_dunking_radius(monster)


	def get_monster_in_dunking_radius(self, monster):
		return monster.distance_from_opponent_base <= self.parent_my_heroes.parent_game.me.base_target_radius + self.hero_base.wind_push_units



class ActionYolo(ActionBase):
	def __init__(self, parent_hero, get_weight_method):
		self.parent_hero = parent_hero

		self.add_yolo(get_weight_method)


	def add_yolo(self, get_weight_method):
		self.parent_hero.add_possible_action(self.parent_hero.get_action_info(ActionYolo.action_yolo, "yolo", get_weight_method))


	def action_yolo(self, action_info):
		self.print_move(action_info, self.parent_my_heroes.parent_game.opponent.x, self.parent_my_heroes.parent_game.opponent.y)



class HeroAttacker(ActionWait, ActionRendezvous, ActionMoveToMonsters, ActionControl, ActionShieldMonster, ActionShieldSelf, ActionDunkMonster, ActionYolo):
	def __init__(self, parent_my_heroes, entity, rendezvous):
		self.parent_my_heroes = parent_my_heroes

		self.hero_base = MyHeroBase(self, entity, rendezvous)


	def clear(self):
		self.hero_base.clear()


	def update(self, entity):
		self.hero_base.update(entity)


	def update_targeted_by_spell_in_previous_round(self):
		self.hero_base.update_targeted_by_spell_in_previous_round()


	def add_possible_actions(self):
		ActionWait(self, self.get_weight_action_wait)
		ActionRendezvous(self, self.get_weight_action_rendezvous)
		ActionMoveToMonsters(self, self.get_weight_action_move_to_monster)
		ActionControl(self, self.get_weight_action_control)
		ActionShieldMonster(self, self.get_weight_action_shield_monster)
		ActionShieldSelf(self, self.get_weight_action_shield_self)
		ActionDunkMonster(self, self.get_weight_action_dunk_monster)
		ActionYolo(self, self.get_weight_action_yolo)


	def get_weight_action_wait(self, action, action_arguments):
		return (
			Utils.infinity
		)


	def get_weight_action_rendezvous(self, action, action_arguments):
		return (
			self.get_move_to_rendezvous() +
			# self.get_mana_threshold_not_reached(200) * Utils.infinity +
			self.get_past_round(130) * Utils.infinity +
			150000
		)


	def get_weight_action_move_to_monster(self, action, action_arguments):
		return (
			self.get_locked_count(action, action_arguments) * 10000 +
			self.get_hero_to_monster_distance(*action_arguments) * 2 +
			self.get_monster_distance_to_opponent_base(*action_arguments) * 7 +
			self.get_hero_distance_to_opponent_base() * 6 +
			# (self.get_monster_is_not_healthy_enough(19, *action_arguments) and self.get_threat_for_opponent_base(*action_arguments)) * 50000 +
			(self.get_monster_is_healthy_enough(10, *action_arguments) and self.get_threat_for_opponent_base(*action_arguments) and self.get_hero_to_monster_distance(*action_arguments) < 2000 and self.get_not_past_round(120)) * 100000
		)


	def get_weight_action_control(self, action, action_arguments):
		return (
			self.get_locked_count(action, action_arguments) * Utils.infinity +
			self.get_not_enough_mana_for_cast() * Utils.infinity +
			self.get_not_in_control_range(*action_arguments) * Utils.infinity +
			self.get_threat_for_opponent_base(*action_arguments) * Utils.infinity +
			self.get_mana_threshold_not_reached(100) * Utils.infinity +
			self.get_monster_shielded(*action_arguments) * Utils.infinity +
			self.get_monster_in_either_base_target_radius(*action_arguments) * Utils.infinity +
			self.get_opponent_near_monster(3000, *action_arguments) * Utils.infinity +
			self.get_not_past_round(100) * Utils.infinity +
			self.get_monster_is_not_healthy_enough(5, *action_arguments) * Utils.infinity
		)


	def get_weight_action_shield_monster(self, action, action_arguments):
		# if Utils.get_point_to_point_distance(action_arguments[0].entity, self.hero_base.entity) < 5000:
		# 	Utils.debug()
		return (
			self.get_locked_count(action, action_arguments) * Utils.infinity +
			self.get_not_enough_mana_for_cast() * Utils.infinity +
			self.get_not_in_shield_range(*action_arguments) * Utils.infinity +
			self.get_monster_shielded(*action_arguments) * Utils.infinity +
			self.get_monster_is_not_healthy_enough(10, *action_arguments) * Utils.infinity +
			self.get_monster_distance_to_opponent_base(*action_arguments) +
			self.get_not_threat_for_opponent_base(*action_arguments) * Utils.infinity +
			self.get_monster_not_near_opponent_base_radius(*action_arguments) * Utils.infinity +
			self.get_not_past_round(120) * Utils.infinity
			# self.get_mana_threshold_not_reached(200) * Utils.infinity +
			# self.get_not_threshold_monster_count_in_radius_around_point(2, self.parent_my_heroes.parent_game.opponent.base_target_radius, self.parent_my_heroes.parent_game.opponent) * Utils.infinity
		)


	def get_weight_action_shield_self(self, action, action_arguments):
		# Utils.debug(
		# 	self.get_was_not_targeted_by_spell(),
		# 	self.get_not_threshold_monster_count_in_radius_around_point(2, self.parent_my_heroes.parent_game.opponent.base_vision_radius, self.parent_my_heroes.parent_game.opponent)
		# )
		return (
			self.get_not_enough_mana_for_cast() * Utils.infinity +
			self.get_hero_shielded() * Utils.infinity +
			(self.get_was_not_targeted_by_spell() and self.get_not_threshold_monster_count_in_radius_around_point(2, self.parent_my_heroes.parent_game.opponent.base_vision_radius, self.parent_my_heroes.parent_game.opponent)) * Utils.infinity
		)


	def get_weight_action_dunk_monster(self, action, action_arguments):
		return (
			self.get_locked_count(action, action_arguments) * Utils.infinity +
			self.get_not_enough_mana_for_cast() * Utils.infinity +
			self.get_not_in_wind_range(*action_arguments) * Utils.infinity +
			self.get_monster_shielded(*action_arguments) * Utils.infinity +
			# self.get_mana_threshold_not_reached(200) * Utils.infinity +
			self.get_monster_is_not_healthy_enough(19, *action_arguments) * Utils.infinity +
			self.get_monster_not_in_dunking_radius(*action_arguments) * Utils.infinity +
			self.get_monster_distance_to_opponent_base(*action_arguments) * 2 +
			self.get_not_past_round(120) * Utils.infinity
		)


	def get_weight_action_yolo(self, action, action_arguments):
		return (
			self.get_not_past_round(140) * Utils.infinity +
			50000
		)



if __name__ == "__main__":
	game = Game()
	game.run()
