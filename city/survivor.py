from . import config
from .drawing import ScreenData, draw_survivor, draw_label_world
from .entity import Entity

import random

from .vectors import distance
from .zombie import Zombie


class Survivor(Entity):
    def __init__(self, city, road=None, x=None, y=None, road_population_densities=None):
        super().__init__(city, road=road, x=x, y=y, road_population_densities=road_population_densities)
        self.is_dead = False
        self.incubation_time_remaining = None
        self.panic_time_remaining = 0
        self.panic_time_initial = 0
        self.is_panicked = False
        self.is_infected = False
        self.speed = config.SURVIVOR_SPEED
        self.target_entity_type = Zombie

    def infect(self, incubation_time=None):
        self.is_infected = True

        if incubation_time is not None:
            self.incubation_time_remaining = max(1, incubation_time)
        else:
            self.incubation_time_remaining = random.randint(0, config.INFECTED_INCUBATION_MAX_TIME)

        self.just_infected = True
        return self.incubation_time_remaining

    def draw(self, screen_data: ScreenData):
        sf = (self.speed / config.SURVIVOR_SPEED) - 1
        draw_survivor(self.x, self.y, screen_data, self.is_infected, sf)
        # if self.near_dead_things:
        #      draw_label_world((f"{self.id}", (self.x + 10, self.y)), screen_data, 1)

    def move(self):
        towards_higher_density = None
        target_entity_type = None

        if self.is_infected:
            # if we're infected, move towards higher densities of people
            towards_higher_density = True
            target_entity_type = 'Survivor'
        elif self.is_panicked:
            # if we're panicked, run away from everyone
            towards_higher_density = False
            target_entity_type = 'Entity'

        self.random_wander(speed=self.speed,
                           direction_change_probability=config.SURVIVOR_WANDER_DIRECTION_CHANGE_PROBABILITY,
                           entity_check_range=config.SURVIVOR_PANIC_RANGE,
                           towards_higher_density=towards_higher_density,
                           target_entity_type=target_entity_type,
                           target_follow_probability=config.SURVIVOR_TARGET_FOLLOW_PROBABILITY)

        self.__check_for_panic()

        speed_boost = 0
        if self.is_panicked:
            speed_boost = config.SURVIVOR_PANIC_SPEED - config.SURVIVOR_SPEED
            speed_boost *= self.panic_time_remaining / self.panic_time_initial

        self.speed = config.SURVIVOR_SPEED + speed_boost

        if self.incubation_time_remaining is not None:
            if self.incubation_time_remaining > 0:
                self.incubation_time_remaining -= 1
            if self.incubation_time_remaining <= 0:
                self.is_dead = True

    def __check_for_panic(self):
        # check for scary things nearby
        if not self.is_panicked:
            panic_time = 0

            if self.is_near_dead_things:
                panic_probability = config.SURVIVOR_SEES_DEATH_PANIC_PROBABILITY
            else:
                panic_probability = self.__check_for_secondary_panic()

            if random.random() < panic_probability:
                panic_time = random.randint(0, config.SURVIVOR_PANIC_DURATION)

            if panic_time > 0:
                if self.is_infected:
                    panic_time *= int(round(config.INFECTED_PANIC_TIME_MULTIPLIER))
                if self.panic_time_remaining == 0:
                    self.direction = -self.direction
                    self.panic_time_remaining = panic_time
                    self.panic_time_initial = panic_time

        if self.panic_time_remaining > 0:
            self.panic_time_remaining -= 1

        self.is_panicked = self.panic_time_remaining > 0

    def __check_for_secondary_panic(self):
        panic_probability = 0
        for entity in self.road.entities:
            if self == entity or entity.is_dead:
                continue
            if distance((self.x, self.y), (entity.x, entity.y)) >= config.SURVIVOR_PANIC_RANGE:
                continue
            pp = 0
            if entity.is_infected:
                # if it's infected, use the secondary panic probability, modified by closeness to death
                pp = (config.SURVIVOR_SEES_PANICKED_OR_INFECTED_PANIC_PROBABILITY *
                      (1 - float(entity.incubation_time_remaining /
                                 config.INFECTED_INCUBATION_MAX_TIME)))
            elif entity.is_panicked:
                # if it's infected, use the secondary panic probability, modified by how panicked
                pp = (config.SURVIVOR_SEES_PANICKED_OR_INFECTED_PANIC_PROBABILITY *
                      float(entity.panic_time_remaining / config.SURVIVOR_PANIC_DURATION))
            if pp > panic_probability:
                panic_probability = pp
        return panic_probability

