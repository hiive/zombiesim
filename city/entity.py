import random
import math

from abc import abstractmethod
from abc import ABC

from city.drawing import ScreenData


class Entity(ABC):
    current_id = 0

    def __init__(self, city, road=None, x=None, y=None):
        Entity.current_id += 1
        self.id = Entity.current_id

        if road is None or x is None or y is None:
            self.road = city.roads[random.randint(0, len(city.roads)-1)]
            sx, sy = self.road.start
            ex, ey = self.road.end
            rp = random.random()
            self.x = sx + rp * (ex - sx)
            self.y = sy + rp * (ey - sy)
        else:
            self.road = road
            self.x = x
            self.y = y

        self.road.entities.append(self)
        self.direction = 1 if random.random() > 0.5 else -1
        self.is_dead = False
        self.is_panicked = False
        self.panic_time_remaining = 0
        self.is_infected = False

    def get_unit_road_vector(self):
        sx, sy = self.road.start
        ex, ey = self.road.end
        dx, dy = ex - sx, ey - sy
        l = math.sqrt(dx * dx + dy * dy)
        dx /= l
        dy /= l
        return dx, dy

    def random_wander(self, speed, direction_change_probability=0.0):
        dx, dy = self.get_unit_road_vector()

        self.x += dx * self.direction * speed
        self.y += dy * self.direction * speed

        # is the zombie at the end of the road
        (sx, sy), (ex, ey) = self.road.start, self.road.end
        links = None
        xd = (ex - sx)
        if xd == 0.0:
            xd = 1.0
        yd = (ey - sy)
        if yd == 0.0:
            yd = 1.0

        xf = (self.x - sx) / xd
        yf = (self.y - sy) / yd

        rt = xf if math.fabs(xd) > math.fabs(yd) else yf

        if rt <= 0:
            # we're at the beginning of the road.
            links = list(self.road.links_s)
        elif rt >= 1:
            # we're at the end of the road.
            links = list(self.road.links_e)
        elif random.random() < direction_change_probability:
            self.direction = - self.direction

        if links is not None:
            # time to change roads
            if len(links) == 0:
                self.direction = - self.direction
            else:
                #if random.random() < 0.5:
                #    self.direction = -self.direction
                self.road.entities.remove(self)
                self.road = links[random.randint(0, len(links) - 1)]
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
