from . import config
from .drawing import ScreenData, draw_zombie, draw_corpse, draw_label_world
from .entity import Entity

import random

from .vectors import distance


class Zombie(Entity):

    def __init__(self, city, road=None, x=None, y=None, road_population_densities=None):
        super().__init__(city, road=road, x=x, y=y, road_population_densities=road_population_densities)
        self.init_delay = config.ZOMBIE_RAISE_DELAY
        self.is_dead = True
        self.is_infected = True
        self.is_panicked = False
        self.is_destroyed = False

    def is_corpse(self):
        return self.init_delay > 0 or self.is_destroyed

    def draw(self, screen_data: ScreenData):
        if self.is_corpse():
            draw_corpse(self.x, self.y, screen_data)
        else:
            draw_zombie(self.x, self.y, screen_data)
        # draw_label_world((f"{self.id}", (self.x+10, self.y)), screen_data, 1)
        pass

    def move(self):
        if self.is_destroyed:
            return

        if self.init_delay > 0:
            self.init_delay -= 1
            return

        speed = config.ZOMBIE_HUNT_SPEED if self.is_near_live_things else config.ZOMBIE_SPEED
        self.random_wander(speed=speed,
                           direction_change_probability=config.ZOMBIE_WANDER_DIRECTION_CHANGE_PROBABILITY,
                           entity_check_range=config.ZOMBIE_HUNT_RANGE,
                           towards_higher_density=True,
                           target_entity_type='Survivor',
                           target_follow_probability=config.ZOMBIE_TARGET_FOLLOW_PROBABILITY)

        # check for survivors nearby
        victim_and_distance = None
        #e_vs = [e for e in self.road.entities if (not e.is_dead and
        #                                          distance((self.x, self.y), (e.x, e.y)) < config.ZOMBIE_ATTACK_RANGE)]

        evs = [e for e in self.nearby_entities if (not e.is_dead and
                                                   distance((self.x, self.y), (e.x, e.y)) < config.ZOMBIE_ATTACK_RANGE)]
        for survivor in evs:
            d = distance((self.x, self.y), (survivor.x, survivor.y))
            if d >= config.ZOMBIE_ATTACK_RANGE:
                continue  # out of attack range
            victim_and_distance = (survivor, d)
            if not survivor.is_infected:
                # the loop breaks if an uninfected is selected, so the
                # victim will be uninfected by preference
                break

        # no-one to attack
        if victim_and_distance is None:
            return

        # attack the victim
        victim, victim_distance = victim_and_distance
        attack_modifier = (config.ZOMBIE_DIFFERENT_FACING_ATTACK_MODIFIER
                           if self.direction != victim.direction
                           else config.ZOMBIE_SAME_FACING_ATTACK_MODIFIER)
        distance_factor = 1.0 - (victim_distance / (attack_modifier * config.ZOMBIE_ATTACK_RANGE))

        r = random.random()
        if r < config.ZOMBIE_KILL_PROBABILITY * distance_factor:
            victim.is_dead = True
        elif r < config.ZOMBIE_WOUND_PROBABILITY * distance_factor:
            victim.infect()

        if random.random() < config.ZOMBIE_DESTRUCTION_PROBABILITY * distance_factor:
            self.nearby_entities = []
            self.is_destroyed = True
