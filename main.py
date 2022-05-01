import math, sys

from queue import PriorityQueue



class Utils:
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
		self.me.init_me()
		self.opponent = Player(self)

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


	def init_me(self):
		self.x, self.y = Utils.get_ints_from_line()


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

			_, _, hero, action_with_arguments = self.possible_actions.get()

			if not hero.hero_base.action_with_arguments:
				hero.hero_base.action_with_arguments = action_with_arguments

		self.run_hero_actions()


	def a_hero_has_no_action_assigned(self):
		return any(my_hero.hero_base.action_with_arguments == None for my_hero in self.my_heroes)


	def recalculate_possible_actions(self):
		self.possible_actions = PriorityQueue()

		for my_hero in self.my_heroes:
			if not my_hero.hero_base.action_with_arguments:
				my_hero.add_possible_actions()


	def run_hero_actions(self):
		for my_hero in self.my_heroes:
			my_hero.hero_base.action_with_arguments["action"](my_hero, my_hero.hero_base.action_with_arguments["label"], *my_hero.hero_base.action_with_arguments["action_arguments"])



class OpponentHeroes:
	def __init__(self, parent_game):
		self.parent_game = parent_game

		self.opponent_heroes = []


	def get_opponent_hero(self, entity):
		self.opponent_heroes.append(
			OpponentHero(
				self,
				entity
			)
		)



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



class HeroBase:
	def __init__(self, parent_hero, entity):
		self.parent_hero = parent_hero

		self.entity = entity

		self.action_with_arguments = None


	def add_possible_actions(self):
		self.add_wait()
		self.add_move_to_all_monsters()
		self.add_move_to_monsters_close_to_my_base()


	def add_wait(self):
		self.add_possible_action(
			self.get_weight_action_wait,
			self.action_wait,
			self.get_action_with_arguments(HeroBase.action_wait, "wait")
		)


	def get_weight_action_wait(self, action_arguments, action_with_arguments):
		return 4242 # TODO: Does math.inf work?


	def get_action_with_arguments(self, action, label, *action_arguments):
		return {
			"action": action,
			"label": label,
			"action_arguments": action_arguments
		}


	# TODO: Change this method so it predicts where the monster will be, instead of doing the current beelining.
	def action_wait(self, label):
		self.print_wait(label)


	def print_wait(self, label=""):
		print(f"WAIT {label}")


	def add_possible_action(self, weight_method, action_method, action_with_arguments):
		self.parent_hero.parent_my_heroes.possible_actions.put((
			weight_method(action_with_arguments["action_arguments"], action_with_arguments),
			action_method.__repr__(), # This resolves equal weight collisions by essentially picking a random action.
			self.parent_hero,
			action_with_arguments
		))


	def add_move_to_all_monsters(self):
		for monster in self.parent_hero.parent_my_heroes.parent_game.monsters.monsters:
			self.add_possible_action(
				self.get_weight_action_move_to_monster,
				self.action_move_to_monster,
				self.get_action_with_arguments(HeroBase.action_move_to_monster, "closest", monster)
			)


	def get_weight_action_move_to_monster(self, action_arguments, action_with_arguments):
		return (
			self.get_locked_penalty_weight(500, action_with_arguments) +
			self.get_weight_action_move_to_monster_raw(*action_arguments) * 10
		)


	# TODO: Change this method once the heroes don't beeline the monster anymore.
	def get_weight_action_move_to_monster_raw(self, monster):
		return math.dist(
			(self.entity.x, self.entity.y),
			(monster.entity.x, monster.entity.y)
		)


	def get_locked_penalty_weight(self, penalty_weight, action_with_arguments):
		total_penalty_weight = 0

		for other_my_hero in self.parent_hero.parent_my_heroes.my_heroes:
			if other_my_hero == self.parent_hero:
				continue

			if other_my_hero.hero_base.action_with_arguments == action_with_arguments:
				total_penalty_weight += penalty_weight

		return total_penalty_weight


	# TODO: Change this method so it predicts where the monster will be, instead of doing the current beelining.
	def action_move_to_monster(self, label, monster):
		self.print_move(monster.entity.x, monster.entity.y, label)


	def print_move(self, x, y, label=""):
		print(f"MOVE {x} {y} {label}")


	def add_move_to_monsters_close_to_my_base(self):
		for monster in self.parent_hero.parent_my_heroes.parent_game.monsters.monsters:
			self.add_possible_action(
				self.get_weight_action_move_to_monster_close_to_my_base,
				self.action_move_to_monster,
				self.get_action_with_arguments(HeroBase.action_move_to_monster, "base", monster)
			)


	def get_weight_action_move_to_monster_close_to_my_base(self, action_arguments, action_with_arguments):
		return (
			self.get_locked_penalty_weight(500, action_with_arguments) +
			self.get_weight_action_move_to_monster_raw(*action_arguments) * 0.01 +
			self.get_weight_monster_distance_to_base(*action_arguments) * 0.3 +
			self.get_weight_threat_for_my_base(*action_arguments) * 2000
		)


	def get_weight_monster_distance_to_base(self, monster):
		return monster.distance_from_my_base


	def get_weight_threat_for_my_base(self, monster):
		return monster.entity.threat_for != monster.threat_for_my_base



class HeroFarmer(HeroBase):
	def __init__(self, parent_my_heroes, entity, rendezvous):
		self.parent_my_heroes = parent_my_heroes

		self.hero_base = HeroBase(self, entity)

		self.rendezvous = rendezvous


	def add_possible_actions(self):
		self.hero_base.add_possible_actions()

		# self.parent_my_heroes.add_possible_action(
		# 	Action()
		# )


	# def move(self):
	# 	if self.hero_base.target is not None:
	# 		# TODO: Lead the monster
	# 		self.hero_base.print_move(self.hero_base.target.entity.x, self.hero_base.target.entity.y)
	# 	else:
	# 		self.hero_base.move()



class HeroAttacker(HeroBase):
	def __init__(self, parent_my_heroes, entity, rendezvous):
		self.parent_my_heroes = parent_my_heroes

		self.hero_base = HeroBase(self, entity)

		self.rendezvous = rendezvous


	def add_possible_actions(self):
		self.hero_base.add_possible_actions()


	# def move(self):
	# 	self.hero_base.move()



class OpponentHero:
	def __init__(self, parent_opponent_heroes, entity):
		self.parent_opponent_heroes = parent_opponent_heroes

		self.entity = entity


if __name__ == "__main__":
	game = Game()
	game.run()
