import math, sys



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

		self.entities = Entities(self)


	def run(self):
		while True:
			self.parse()
			self.update()
			self.round += 1


	def parse(self):
		self.me.parse_health_and_mana()
		self.opponent.parse_health_and_mana()

		self.entities.my_heroes = MyHeroes(self.entities)


	def update(self):
		self.entities.update()



class Player(Game):
	def __init__(self, parent_game):
		self.parent_game = parent_game


	def init_me(self):
		self.x, self.y = Utils.get_ints_from_line()


	def parse_health_and_mana(self):
		self.health, self.mana = Utils.get_ints_from_line()



class Entities(Game):
	def __init__(self, parent_game):
		self.parent_game = parent_game

		self.monster_type = 0
		self.my_hero_type = 1
		self.opponent_hero_type = 2

		self.my_heroes = MyHeroes(self)


	def update(self):
		self.parse_entities()
		# self.sort_entities()
		self.my_heroes.update()


	def parse_entities(self):
		self.entity_count = int(input())

		self.monsters = []
		self.opponent_heroes = []

		for _ in range(self.entity_count):
			entity = Entity(self)

			self.add_entity(entity)


	def add_entity(self, entity):
		entities_sublist = self.get_entities_sublist(entity)

		instantiated_entity = self.get_instantiated_entity(entity)

		entities_sublist.append(instantiated_entity)


	def get_entities_sublist(self, entity):
		if entity.type_ == self.monster_type:
			return self.monsters
		elif entity.type_ == self.my_hero_type:
			return self.my_heroes.heroes
		return self.opponent_heroes


	def get_instantiated_entity(self, entity):
		if entity.type_ == self.monster_type:
			return Monster(self, entity)
		elif entity.type_ == self.my_hero_type:
			return self.my_heroes.get_next_hero(entity)
		return HeroBase(self, entity)


	# def sort_entities(self):
	# 	self.monsters.sort()
	# 	self.opponent_heroes.sort()
	# 	self.my_heroes.heroes.sort()



class MyHeroes(Entities):
	def __init__(self, parent_entities):
		self.parent_entities = parent_entities

		self.heroes = []


	def get_next_hero(self, entity):
		my_heroes_len = len(self.heroes)

		if my_heroes_len == 0:
			return HeroFarmer(
				self,
				entity,
				Point(
					3000,
					5300
				),
				1000
		)
		elif my_heroes_len == 1:
			return HeroFarmer(
				self,
				entity,
				Point(
					5300,
					3000
				),
				200
		)
		return HeroAttacker(self, entity, Point(
			13000,
			5000
		))


	def update(self):
		self.assign_heroes()

		for hero in self.heroes:
			hero.update()


	def assign_heroes(self):
		for hero in self.heroes:
			self.speculatively_assign_hero(
				hero,
				lambda unsorted_monster:
					unsorted_monster.distance_from_my_base +
					self.hero_distance_to_monster(hero, unsorted_monster)
			)

		for hero in self.heroes:
			if hero.hero_base.target:
				# TODO: Reuse lambda above and penalize enemies that are targeted by many heroes.
				self.optimally_reassign_hero(hero)


	def hero_distance_to_monster(self, hero, monster):
		return math.dist(
			(
				hero.hero_base.entity.x,
				hero.hero_base.entity.y
			),
			(
				monster.entity.x,
				monster.entity.y
			)
		)


	def speculatively_assign_hero(self, hero, lambda_):
		for monster in sorted(self.parent_entities.monsters, key=lambda_):
			if monster.entity.threat_for == monster.threat_for_my_base:
				hero.hero_base.target = monster
				monster.targeted_by.append(hero)
				return


	def optimally_reassign_hero(self, hero):
		# for targeted_by in hero.hero_base.target.targeted_by:
		# 	if targeted_by is not hero:
		# 		if self.hero_distance_to_monster(targeted_by, hero.hero_base.target) < self.hero_distance_to_monster(hero, hero.hero_base.target):
		# 			hero.hero_base.target = None # TODO: Assign to second-best target.
		# 			return
		pass



class Entity(Entities):
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



class Monster(Entities):
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



class HeroBase(Entities):
	def __init__(self, parent_entities, entity, rendezvous=None):
		self.parent_entities = parent_entities

		self.entity = entity

		self.rendezvous = rendezvous

		self.target = None


	def update(self):
		self.move()


	def move(self):
		if self.rendezvous is not None: # Prevents yellow lines under .x and .y
			self.print_move(self.rendezvous.x, self.rendezvous.y)


	def print_move(self, x, y):
		print(f"MOVE {x} {y} {':)' if self.target != None else ''}")



class HeroFarmer(HeroBase):
	def __init__(self, parent_entities, entity, rendezvous, maximum_distance_from_rendezvous):
		self.parent_entities = parent_entities

		self.hero_base = HeroBase(parent_entities, entity, rendezvous)


	def move(self):
		if self.hero_base.target is not None:
			# TODO: Lead the enemy, like how
			self.hero_base.print_move(self.hero_base.target.entity.x, self.hero_base.target.entity.y)
		else:
			self.hero_base.move()



class HeroAttacker(HeroBase):
	def __init__(self, parent_entities, entity, rendezvous):
		self.parent_entities = parent_entities

		self.hero_base = HeroBase(parent_entities, entity, rendezvous)


	def move(self):
		self.hero_base.move()



if __name__ == "__main__":
	game = Game()
	game.run()
