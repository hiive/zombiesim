import random
import math

from abc import abstractmethod
from abc import ABC

from city.drawing import ScreenData
import numpy as np

from city.vectors import distance, distance2


class Entity(ABC):
    current_id = 0

    def __init__(self, city, road=None, x=None, y=None, road_population_densities=None):
        Entity.current_id += 1
        self.id = Entity.current_id
        self.road = city.roads[random.randint(0, len(city.roads) - 1)]
        if road is None:
            if road_population_densities is None:
                self.road = city.roads[random.randint(0, len(city.roads) - 1)]
            else:
                self.road = np.random.choice(city.roads, p=road_population_densities)
        else:
            self.road = road

        if x is None or y is None:
            sx, sy = self.road.start
            ex, ey = self.road.end
            rp = random.random()
            self.x = sx + rp * (ex - sx)
            self.y = sy + rp * (ey - sy)
        else:
            self.x = x
            self.y = y

        self.road.entities.append(self)
        self.direction = 1 if random.random() > 0.5 else -1
        self.is_dead = False
        self.is_panicked = False
        self.is_infected = False
        self.is_near_dead_things = False
        self.is_near_live_things = False
        self.incubation_time_remaining = None
        self.panic_time_remaining = 0
        self.panic_time_initial = 0
        self.nearby_entities = []
        self.just_infected = False

    def __str__(self):
        return f'id:{self.id} ({type(self).__name__})'

    def __repr__(self):
        return self.__str__()

    def get_unit_road_vector(self):
        sx, sy = self.road.start
        ex, ey = self.road.end
        dx, dy = ex - sx, ey - sy
        l = math.sqrt(dx * dx + dy * dy)
        dx /= l
        dy /= l
        return dx, dy

    def random_wander(self, speed, direction_change_probability=0.0, entity_check_range=0.0,
                      towards_higher_density=None, target_entity_type=None, target_follow_probability=1.9):
        dx, dy = self.get_unit_road_vector()

        self.x += dx * self.direction * speed
        self.y += dy * self.direction * speed

        # is the entity heading towards the start or end of the road
        (sx, sy), (ex, ey) = self.road.start, self.road.end
        xd = (ex - sx)
        if xd == 0.0:
            xd = 1.0
        yd = (ey - sy)
        if yd == 0.0:
            yd = 1.0

        xf = (self.x - sx) / xd
        yf = (self.y - sy) / yd

        rt = xf if math.fabs(xd) > math.fabs(yd) else yf

        # calculate links if we're near the start/end of a road
        links = None
        road_change = False
        if rt <= 0:
            # we're at the beginning of the road.
            links = list(self.road.links_s)
            road_change = True
        elif rt >= 1:
            # we're at the end of the road.
            links = list(self.road.links_e)
            road_change = True
        elif random.random() < direction_change_probability:
            self.direction = - self.direction

        # check for nearby entities
        if entity_check_range > 0:
            self.nearby_entities.clear()
            # add current road to list
            if links is None:
                links = [self.road]
            else:
                links.append(self.road)
            ignored_links = set()
            # figure out if we're near anything dead/alive
            self.is_near_dead_things = False
            self.is_near_live_things = False
            nearby_dead_entities = []
            nearby_live_entities = []
            for link in links:
                nde = [e for e in link.entities if (e.is_dead and
                                                    distance((self.x, self.y), (e.x, e.y)) < entity_check_range)]
                is_near_dead_things = any(nde)
                if is_near_dead_things:
                    nearby_dead_entities.extend(nde)
                    if not self.is_dead:
                        ignored_links.add(link)

                nle = [e for e in link.entities if (not e.is_dead and
                                                    distance((self.x, self.y), (e.x, e.y)) < entity_check_range)]
                is_near_live_things = any(nle)
                if is_near_live_things:
                    nearby_live_entities.extend(nle)
            self.is_near_live_things = any(nearby_live_entities)
            self.is_near_dead_things = any(nearby_dead_entities)
            self.nearby_entities.extend(nearby_live_entities)
            self.nearby_entities.extend(nearby_dead_entities)
            # if any(self.nearby_entities):
            #     print(f'{self}: {self.nearby_entities}')

            # remove current road from list.
            links.remove(self.road)
            # remove any dead links
            links = list(set(links) - ignored_links)

        # if links is set, then we're near the beginning/end of a road.
        # it may be empty, but we need to process it
        if road_change:
            # need to change road/direction
            if len(links) == 0:
                self.direction = - self.direction
            else:
                # time to change roads
                self.road.entities.remove(self)
                follow_target = random.random() < target_follow_probability
                if towards_higher_density is None or target_entity_type is None or follow_target:
                    self.road = links[random.randint(0, len(links) - 1)]
                else:
                    dm = -1 if towards_higher_density else 1
                    density_sorted_roads = sorted(links, key=lambda l: dm * (len([e for e in l.entities
                                                                             if type(e).__name__ == target_entity_type])
                                                                             ))

                    min_density = min([len(link.entities) for link in density_sorted_roads])
                    density_sorted_roads = [link for link in density_sorted_roads if len(link.entities) == min_density]
                    ix = random.randint(0, len(density_sorted_roads) - 1)
                    self.road = density_sorted_roads[ix]

                self.road.entities.append(self)

            # check start and end and update self position
            (sx, sy), (ex, ey) = self.road.start, self.road.end
            ds2 = math.fabs(self.x - sx) ** 2 + math.fabs(self.y - sy) ** 2
            de2 = math.fabs(self.x - ex) ** 2 + math.fabs(self.y - ey) ** 2
            if ds2 < de2:
                # starting at beginning of road
                self.x, self.y = sx, sy
                self.direction = 1
            else:
                # starting at end of road
                self.x, self.y = ex, ey
                self.direction = -1

    @abstractmethod
    def draw(self, screen_data: ScreenData):
        pass

    @abstractmethod
    def move(self):
        pass
