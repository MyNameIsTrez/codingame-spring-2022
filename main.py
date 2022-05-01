import math, sys

from queue import PriorityQueue



class Utils:
	infinite = 424242

	@staticmethod
	def debug(*args, **kwargs):
		print(*args, **kwargs, file=sys.stderr)

	@staticmethod
	def get_ints_from_line():
		return [int(x) for x in input().split()]



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
		self.monsters.clear()
		self.my_heroes.clear()


	def parse(self):
		self.me.parse_health_and_mana()
		self.opponent.parse_health_and_mana()
		self.entities.parse_entities()


	def update(self):
		self.my_heroes.update()



class Player:
	def __init__(self, parent_game):
		self.parent_game = parent_game


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


	def clear(self):
		self.my_heroes = []


	def add_my_next_hero(self, entity):
		my_heroes_len = len(self.my_heroes)

		if my_heroes_len == 0:
			self.my_heroes.append(
				HeroFarmer(
					self,
					entity,
					Point(
						3000,
						5300
					)
				)
			)
		elif my_heroes_len == 1:
			self.my_heroes.append(
				HeroFarmer(
					self,
					entity,
					Point(
						5300,
						3000
					)
				)
			)
		else:
			self.my_heroes.append(
				HeroAttacker(
					self,
					entity,
					Point(
						13000,
						5000
					)
				)
			)


	def update(self):
		while self.a_hero_has_no_action_assigned():
			self.recalculate_possible_actions()

			_, _, hero, action_info = self.possible_actions.get()

			if not hero.hero_base.action_info:
				hero.hero_base.action_info = action_info

		self.run_hero_actions()


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



class OpponentHeroes:
	def __init__(self, parent_game):
		self.parent_game = parent_game

		self.opponent_heroes = []


	def add_opponent_hero(self, entity):
		self.opponent_heroes.append(
			OpponentHero(
				self,
				entity
			)
		)



class OpponentHero:
	def __init__(self, parent_opponent_heroes, entity):
		self.parent_opponent_heroes = parent_opponent_heroes

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
			entity = Entity(self)

			self.add_entity(entity)


	def add_entity(self, entity):
		if entity.type_ == self.monster_type:
			return self.parent_game.monsters.add_monster(entity)
		elif entity.type_ == self.my_hero_type:
			return self.parent_game.my_heroes.add_my_next_hero(entity)
		elif entity.type_ == self.opponent_hero_type:
			return self.parent_game.opponent_heroes.add_opponent_hero(entity)



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

		# Ignore for this league; Count down until shield spell fades
		# self.shield_life = shield_life

		# Ignore for this league; Equals 1 when this entity is under a control spell
		# self.is_controlled = is_controlled

		# Remaining health of this monster
		# self.health = health

		# Velocity of this monster
		# self.vx = vx
		# self.vy = vy

		# If in the base's large circle
		# self.near_base = near_base

		# Given this monster's trajectory, is it a threat to 1 = your base, 2 = your opponent's base, 0 = neither
		self.threat_for = threat_for



class Monster:
	def __init__(self, parent_entities, entity):
		self.parent_entities = parent_entities

		self.entity = entity

		# self.threat_for_none = 0
		self.threat_for_my_base = 1
		# self.threat_for_opponent_base = 2

		# self.targeted_by = []

		self.save_distance_from_my_base()


	def save_distance_from_my_base(self):
		self.distance_from_my_base = math.dist(
			(self.entity.x, self.entity.y),
			(
				self.parent_entities.parent_game.me.x,
				self.parent_entities.parent_game.me.y
			)
		)



class ActionWait:
	def __init__(self, parent_hero_base):
		self.parent_hero_base = parent_hero_base

		self.add_wait()


	def add_wait(self):
		self.parent_hero_base.add_possible_action(self.parent_hero_base.get_action_info(ActionWait.action_wait, "wait", self.get_weight_action_wait))


	def action_wait(self, action_info):
		self.wait(action_info)


	def wait(self, action_info):
		self.print_wait(action_info)


	def print_wait(self, action_info):
		print(f"WAIT {action_info['label']} {action_info['weight']}")


	def get_weight_action_wait(self, action, action_arguments):
		return Utils.infinite



class ActionMoveToAllMonsters:
	def __init__(self, parent_hero_base):
		self.parent_hero_base = parent_hero_base

		self.add_move_to_all_monsters()


	def add_move_to_all_monsters(self):
		for monster in self.parent_hero_base.parent_hero.parent_my_heroes.parent_game.monsters.monsters:
			self.parent_hero_base.add_possible_action(self.parent_hero_base.get_action_info(HeroBase.action_move_to_monster, "closest", self.get_weight_action_move_to_monster, monster))


	def action_move_to_monster(self, action_info, monster):
		self.move_to_monster(action_info, monster)


	# TODO: Change this method so it predicts where the monster will be, instead of doing the current beelining.
	def move_to_monster(self, action_info, monster):
		self.print_move(action_info, monster.entity.x, monster.entity.y)


	def get_weight_action_move_to_monster(self, action, action_arguments):
		return (
			self.parent_hero_base.get_locked_penalty_weight(1, action, action_arguments) +
			self.parent_hero_base.get_weight_distance_to_monster(*action_arguments) * 5
		)



class HeroBase(ActionWait, ActionMoveToAllMonsters):
	def __init__(self, parent_hero, entity):
		self.parent_hero = parent_hero

		self.entity = entity

		self.action_info = None

		self.penalty_weight = 1000

		self.wind_range = 1280


	def add_possible_actions(self):
		ActionWait(self)
		ActionMoveToAllMonsters(self)
		self.add_move_to_monsters_close_to_my_base()


	def get_action_info(self, action, label, weight_method, *action_arguments):
		return {
			"action": action,
			"label": label,
			"weight": int(weight_method(action, action_arguments)),
			"action_arguments": action_arguments
		}


	def add_possible_action(self, action_info):
		self.parent_hero.parent_my_heroes.possible_actions.put((
			action_info["weight"],
			self.get_uncollidable_hash(action_info),
			self.parent_hero,
			action_info
		))


	def get_uncollidable_hash(self, action_info):
		return self.__repr__() + action_info["action"].__repr__() + action_info["action_arguments"].__repr__()


	# TODO: Change this method once the heroes don't beeline the monster anymore.
	def get_weight_distance_to_monster(self, monster):
		return math.dist(
			(self.entity.x, self.entity.y),
			(monster.entity.x, monster.entity.y)
		)


	def get_locked_penalty_weight(self, penalty_weight_multiplier, action, action_arguments):
		total_penalty_weight = 0

		for other_my_hero in self.parent_hero.parent_my_heroes.my_heroes:
			if other_my_hero == self.parent_hero:
				continue

			if self.action_already_locked(other_my_hero, action, action_arguments):
				total_penalty_weight += self.penalty_weight * penalty_weight_multiplier

		return total_penalty_weight


	def action_already_locked(self, other_my_hero, action, action_arguments):
		return (
			other_my_hero.hero_base.action_info and
			other_my_hero.hero_base.action_info["action"] == action and
			other_my_hero.hero_base.action_info["action_arguments"] == action_arguments
		)


	def print_move(self, action_info, x, y):
		print(f"MOVE {x} {y} {action_info['label']} {action_info['weight']}")


	def add_move_to_monsters_close_to_my_base(self):
		for monster in self.parent_hero.parent_my_heroes.parent_game.monsters.monsters:
			self.add_possible_action(self.get_action_info(HeroBase.action_move_to_monster_close_to_my_base, "base", self.get_weight_action_move_to_monster_close_to_my_base, monster))


	def action_move_to_monster_close_to_my_base(self, action_info, monster):
		self.move_to_monster(action_info, monster)


	def get_weight_action_move_to_monster_close_to_my_base(self, action, action_arguments):
		return (
			self.get_locked_penalty_weight(1, action, action_arguments) +
			self.get_weight_distance_to_monster(*action_arguments) +
			self.get_weight_monster_distance_to_base(*action_arguments) +
			self.get_weight_threat_for_my_base(*action_arguments)
		)


	def get_weight_monster_distance_to_base(self, monster):
		return monster.distance_from_my_base


	def get_weight_threat_for_my_base(self, monster):
		return 0 if monster.entity.threat_for == monster.threat_for_my_base else Utils.infinite


	def get_weight_enough_mana(self):
		return 0 if self.parent_hero.parent_my_heroes.parent_game.me.mana >= 10 else Utils.infinite



class HeroFarmer(HeroBase):
	def __init__(self, parent_my_heroes, entity, rendezvous):
		self.parent_my_heroes = parent_my_heroes

		self.hero_base = HeroBase(self, entity)

		self.rendezvous = rendezvous


	def add_possible_actions(self):
		self.hero_base.add_possible_actions()

		self.add_blow_away_from_base()


	def add_blow_away_from_base(self):
		for monster in self.parent_my_heroes.parent_game.monsters.monsters:
			self.hero_base.add_possible_action(self.get_action_info(HeroFarmer.action_blow_monster_away_from_base, "blow away base", self.get_weight_action_blow_monster_away_from_base, monster))


	def action_blow_monster_away_from_base(self, action_info, monster):
		self.blow_monster_towards_enemy_base(action_info)


	def blow_monster_towards_enemy_base(self, action_info):
		self.print_blow(action_info, self.parent_my_heroes.parent_game.opponent.x, self.parent_my_heroes.parent_game.opponent.y)


	def print_blow(self, action_info, x, y):
		print(f"SPELL WIND {x} {y} {action_info['label']} {action_info['weight']}")


	def get_weight_action_blow_monster_away_from_base(self, action, action_arguments):
		return (
			self.hero_base.get_locked_penalty_weight(8, action, action_arguments) +
			self.hero_base.get_weight_enough_mana() +
			self.hero_base.get_weight_threat_for_my_base(*action_arguments) +
			self.get_weight_in_wind_range(*action_arguments) +
			self.get_weight_close_to_base(*action_arguments)
		)


	def get_weight_in_wind_range(self, monster):
		return 0 if self.hero_base.get_weight_distance_to_monster(monster) <= self.hero_base.wind_range else Utils.infinite


	def get_weight_close_to_base(self, monster):
		return 0 if monster.distance_from_my_base <= 2000 else Utils.infinite



class HeroAttacker(HeroBase):
	def __init__(self, parent_my_heroes, entity, rendezvous):
		self.parent_my_heroes = parent_my_heroes

		self.hero_base = HeroBase(self, entity)

		self.rendezvous = rendezvous


	def add_possible_actions(self):
		self.hero_base.add_possible_actions()



if __name__ == "__main__":
	game = Game()
	game.run()
