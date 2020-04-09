from . import config
from .drawing import ScreenData, draw_survivor, draw_label_world
from .entity import Entity

import math
import random

from .vectors import distance


class Survivor(Entity):
    def __init__(self, city, road=None, x=None, y=None):
        super().__init__(city, road, x, y)
        self.is_dead = False
        self.incubation_time_remaining = None
        self.panic_time_remaining = 0
        self.panic_time_initial = 0
        self.is_panicked = False
        self.is_infected = False
        self.speed = config.SURVIVOR_SPEED

    def infect(self):
        self.is_infected = True
        self.incubation_time_remaining = random.randint(0, config.INFECTED_INCUBATION_MAX_TIME)

    def draw(self, screen_data: ScreenData):
        sf = (self.speed / config.SURVIVOR_SPEED) - 1
        draw_survivor(self.x, self.y, screen_data, self.is_infected, sf)
        near_dead_things = False
        for e in self.road.entities:
            if e == self:
                continue
            near_dead_things |= e.is_dead

        # if near_dead_things:
        #      draw_label_world((f"{self.id}", (self.x + 10, self.y)), screen_data, 1)

    def move(self):
        self.random_wander(self.speed, config.SURVIVOR_WANDER_DIRECTION_CHANGE_PROBABILITY)

        # check for scary things nearby
        panic_time = 0
        panic_probability = 0
        if not self.is_panicked:
            for entity in self.road.entities:
                if self == entity:
                    continue
                pp = 0
                if entity.is_dead or entity.is_panicked or entity.is_infected:
                    if distance((self.x, self.y), (entity.x, entity.y)) < config.SURVIVOR_PANIC_RANGE:
                        # if the other entity is dead, use the default panic
                        if entity.is_dead:
                            pp = config.SURVIVOR_SEES_DEATH_PANIC_PROBABILITY
                        elif entity.is_infected:
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
