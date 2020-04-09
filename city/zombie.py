from . import config
from .drawing import ScreenData, draw_zombie, draw_corpse, draw_label_world
from .entity import Entity

import math
import random

from .survivor import Survivor
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

        self.random_wander(speed=config.ZOMBIE_SPEED,
                           direction_change_probability=config.ZOMBIE_WANDER_DIRECTION_CHANGE_PROBABILITY)

        # check for survivors nearby
        sorted_survivors = []
        for entity in [e for e in self.road.entities if isinstance(e, Survivor)]:
            if entity.is_dead:  # or entity.is_infected:
                continue
            if distance((self.x, self.y), (entity.x, entity.y)) >= config.ZOMBIE_ATTACK_RANGE:
                continue
            if entity.is_infected:
                # add infected to end
                sorted_survivors.append(entity)
            else:
                # add uninfected to beginning
                sorted_survivors.insert(0, entity)

        if len(sorted_survivors) == 0:
            return

        entity_to_attack = sorted_survivors[0]
        if distance((self.x, self.y), (entity_to_attack.x, entity_to_attack.y)) < config.ZOMBIE_ATTACK_RANGE:
            r = random.random()
            distance_factor = 1 - distance((entity_to_attack.x, entity_to_attack.y),
                                           (self.x, self.y)) / config.ZOMBIE_ATTACK_RANGE

            if r < config.ZOMBIE_KILL_PROBABILITY * distance_factor:
                entity_to_attack.is_dead = True
            elif r < config.ZOMBIE_WOUND_PROBABILITY * distance_factor:
                entity_to_attack.infect()

            if random.random() < config.ZOMBIE_DESTRUCTION_PROBABILITY * distance_factor:
                self.is_destroyed = True





