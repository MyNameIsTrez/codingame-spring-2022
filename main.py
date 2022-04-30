import math, sys, functools

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
			self.parse()
			self.update()
			self.round += 1


	def parse(self):
		self.me.parse_health_and_mana()
		self.opponent.parse_health_and_mana()


	def update(self):
		self.my_heroes.update()
		self.entities.update()



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

		self.monsters = []


	def add_monster(self, entity):
		self.monsters.append(
			Monster(self, entity)
		)



class MyHeroes:
	def __init__(self, parent_game):
		self.parent_game = parent_game

		self.my_heroes = []

		self.possible_actions = PriorityQueue()


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
		for my_hero in self.my_heroes:
			my_hero.add_possible_actions()

		while self.a_hero_has_no_action_assigned():
			_, hero, action_with_arguments = self.possible_actions.get()

			if not hero.action_with_arguments:
				hero.action_with_arguments = action_with_arguments

		for my_hero in self.my_heroes:
			my_hero.action_with_arguments()


	def a_hero_has_no_action_assigned(self):
		return any(my_hero.action_with_arguments == None for my_hero in self.my_heroes)



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


	def update(self):
		self.parse_entities()


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

		self.threat_for_none = 0
		self.threat_for_my_base = 1
		self.threat_for_opponent_base = 2

		self.entity = entity

		self.targeted_by = []

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
		self.add_move_to_all_targets()


	def add_wait(self):
		self.add_possible_action(
			1337, # TODO: Does math.inf work?
			functools.partial(self.action_wait)
		)


	# TODO: Change this method it predicts where the monster will be, instead of the current beelining.
	def action_wait(self):
		self.print_wait()


	def print_wait(self, message=""):
		print(f"WAIT {message}")


	def add_possible_action(self, weight, action_with_arguments):
		self.parent_hero.parent_my_heroes.possible_actions.put((weight, action_with_arguments))


	def add_move_to_all_targets(self):
		for monster in self.parent_hero.parent_game.monsters.monsters:
			self.add_possible_action(
				self.get_weight_action_move_to_monster(monster),
				functools.partial(self.action_move_to_monster, monster)
			)


	# TODO: Change this method once the heroes don't beeline the monster anymore.
	def get_weight_action_move_to_monster(self, monster):
		return math.dist(
			(self.entity.x, self.entity.y),
			(monster.entity.x, monster.entity.y)
		)


	# TODO: Change this method it predicts where the monster will be, instead of the current beelining.
	def action_move_to_monster(self, monster):
		self.print_move(monster.entity.x, monster.entity.y)


	def print_move(self, x, y, message=""):
		print(f"MOVE {x} {y} {message}")


	# def get_hero_distance_to_monster(self, hero, monster):


	# def assign_heroes(self):
	# 	for my_hero in self.my_heroes:
	# 		self.speculatively_assign_hero(
	# 			my_hero,
	# 			lambda unsorted_monster:
	# 				unsorted_monster.distance_from_my_base +
	# 				self.get_hero_distance_to_monster(my_hero, unsorted_monster)
	# 		)

	# 	for my_hero in self.my_heroes:
	# 		if my_hero.hero_base.target:
	# 			# TODO: Reuse lambda above and penalize enemies that are targeted by many of my heroes.
	# 			self.optimally_reassign_hero(my_hero)


	# def speculatively_assign_hero(self, my_hero, lambda_):
	# 	for monster in sorted(self.parent_entities.monsters, key=lambda_):
	# 		if monster.entity.threat_for == monster.threat_for_my_base:
	# 			my_hero.hero_base.target = monster
	# 			monster.targeted_by.append(my_hero)
	# 			return


	# def optimally_reassign_hero(self, my_hero):
	# 	# for targeted_by in my_hero.hero_base.target.targeted_by:
	# 	# 	if targeted_by is not my_hero:
	# 	# 		if self.get_hero_distance_to_monster(targeted_by, my_hero.hero_base.target) < self.get_hero_distance_to_monster(my_hero, my_hero.hero_base.target):
	# 	# 			my_hero.hero_base.target = None # TODO: Assign to second-best target.
	# 	# 			return
	# 	pass


	# 	if self.rendezvous is not None: # Prevents yellow lines under .x and .y
	# 		self.print_move(self.rendezvous.x, self.rendezvous.y)



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
