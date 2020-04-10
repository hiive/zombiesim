from . import config, sectors
from . import debug
from . import pathing
from . import snap_type as st
import pygame
import math
from . import population
from . import vectors
from . import generation
from . import roads
from typing import Tuple, List


class ScreenData:
    def __init__(self, screen, pan, zoom_increment=1):
        self.screen = screen
        self.pan = pan
        self._zoom_increment = zoom_increment
        self.zoom = self._zoom_at(zoom_increment)

    @staticmethod
    def _zoom_at(step):
        return math.pow((step / config.ZOOM_GRANULARITY) + 1, 2)

    def zoom_in(self, center):
        self._zoom_change(1, center)

    def zoom_out(self, center):
        if self._zoom_increment > (-config.ZOOM_GRANULARITY) + 3:
            self._zoom_change(-1, center)

    def _zoom_change(self, step, center):
        new_level = self._zoom_at(self._zoom_increment + step)

        old_world = screen_to_world(center, self.pan, self.zoom)
        new_world = screen_to_world(center, self.pan, new_level)

        world_pan = vectors.sub(new_world, old_world)

        self.zoom = new_level
        self.pan = vectors.add(self.pan, world_to_screen(world_pan, (0, 0), new_level))

        self._zoom_increment += step
        return


def init():
    global font
    font = pygame.font.SysFont("gohufont, terminusttf, couriernew", 20)


def world_to_screen(world_pos: tuple, pan: tuple, zoom: float) -> Tuple[float, float]:
    """ Converts world coordinates to screen coordinates using the pan and
    zoom of the screen """
    result = ((world_pos[0] * zoom) + pan[0],
              (world_pos[1] * zoom) + pan[1])
    return result


def screen_to_world(screen_pos: tuple, pan: tuple, zoom: float) -> Tuple[float, float]:
    """ Converts screen coordinates to world coordinates using the pan and
    zoom of the screen """
    result = (((screen_pos[0] - pan[0]) / zoom),
              ((screen_pos[1] - pan[1]) / zoom))
    return result


def draw_all_roads(all_roads: List[roads.Segment], data: ScreenData):
    """ Draws the roads in all_roads to the surface in data"""
    for road in all_roads:
        width = config.ROAD_WIDTH
        color = (64, 64, 64)

        if road.is_highway:
            width = config.ROAD_WIDTH_HIGHWAY
            color = (96, 96, 96)
        elif debug.SHOW_ROAD_VIEW == debug.RoadViews.Snaps:
            if road.has_snapped == st.SnapType.Cross:
                color = (96, 64, 64)
            elif road.has_snapped == st.SnapType.End:
                color = (64, 96, 64)
            elif road.has_snapped == st.SnapType.Extend:
                color = (64, 64, 96)
            elif road.has_snapped == st.SnapType.CrossTooClose:
                color = (64, 96, 96)
        elif debug.SHOW_ROAD_VIEW == debug.RoadViews.Branches:
            if road.is_branch:
                color = (64, 96, 64)
        if road.has_snapped == st.SnapType.DebugDeleted:
            color = (0, 96, 0)

        draw_road(road, color, width, data)


def draw_roads_selected(selection: 'debug.Selection', data: ScreenData):
    if selection is not None:
        draw_road(selection[0], (255, 255, 0), config.ROAD_WIDTH_SELECTION, data)

        for road in selection[1]:
            draw_road(road, (0, 255, 0), config.ROAD_WIDTH_SELECTION, data)


def draw_roads_path(path_data: pathing.PathData, data: ScreenData):
    if len(path_data.searched) != 0:
        width = config.ROAD_WIDTH_PATH
        color = (255, 0, 255)

        for road in path_data.searched:
            draw_road(road, color, width, data)

    if len(path_data.path) != 0:
        width = config.ROAD_WIDTH_PATH
        color = (0, 255, 255)
        for road in path_data.path:
            draw_road(road, color, width, data)

    width = config.ROAD_WIDTH_PATH
    if path_data.start is not None:
        draw_road(path_data.start, (0, 255, 0), width, data)
    if path_data.end is not None:
        draw_road(path_data.end, (255, 0, 0), width, data)


def draw_road(road: roads.Segment, color: Tuple[int, int, int], width: int, data: ScreenData):
    pygame.draw.line(data.screen, color, world_to_screen(road.start, data.pan, data.zoom),
                     world_to_screen(road.end, data.pan, data.zoom), width)


def draw_label_world(label, data, justify):
    label_pos = world_to_screen(label[1], data.pan, data.zoom)
    draw_label_screen((label[0], label_pos), data, justify)


def draw_zombie(x, y, data: ScreenData):
    pygame.draw.circle(data.screen, (0, 192, 0), world_to_screen((x, y), data.pan, data.zoom), config.ENTITY_SIZE)


def draw_corpse(x, y, data: ScreenData):
    pygame.draw.circle(data.screen, (0, 128, 255), world_to_screen((x, y), data.pan, data.zoom), config.ENTITY_SIZE)


def lerp_(v1, v2, f):
    while f > 1:
        f -= 1
    return int(round(v1 + (v2 - v1) * f))


def draw_survivor(x, y, data: ScreenData, incubating, speed_factor=0):
    r1, g1, b1 = (192, 192, 0) if incubating else (160, 96, 160)
    r2, g2, b2 = (255, 255, 0) if incubating else (255, 0, 255)

    color = (max(0, min(lerp_(r1, r2, speed_factor), 255)),
             max(0, min(lerp_(g1, g2, speed_factor), 255)),
             max(0, min(lerp_(b1, b2, speed_factor), 255)))

    pygame.draw.circle(data.screen, color, world_to_screen((x, y), data.pan, data.zoom), config.ENTITY_SIZE)


def draw_label_screen(label, data, justify):
    label_pos = label[1]
    if -20 < label_pos[0] < config.SCREEN_RES[0] and \
            -20 < label_pos[1] < config.SCREEN_RES[1]:
        rendered_text = font.render(label[0], True, (255, 255, 255))
        if justify == 0:
            label_pos = (label_pos[0] - rendered_text.get_width() / 2, label_pos[1])
        elif justify == -1:
            label_pos = (label_pos[0] - rendered_text.get_width(), label_pos[1])
        data.screen.blit(rendered_text, label_pos)


def draw_heatmap(square_size: int, city: generation.City, data: ScreenData):
    """ Draws the population heatmap to the screen in the given ScreenData """
    x_max = math.ceil(config.SCREEN_RES[0] / square_size) + 1
    y_max = math.ceil(config.SCREEN_RES[1] / square_size) + 1

    for x in range(0, x_max):
        for y in range(0, y_max):
            screen_point = (x * square_size,
                            y * square_size)
            world_point = screen_to_world(screen_point, data.pan, data.zoom)
            intensity = city.pop.at_point(world_point)
            color = (0, max(min(intensity * 83, 255), 0), 0)
            pos = (screen_point[0] - (square_size / 2), screen_point[1] - (square_size / 2))
            dim = (square_size, square_size)

            pygame.draw.rect(data.screen, color, pygame.Rect(pos, dim))


def draw_popmap(square_size: int, survivors, zombies, data: ScreenData):
    return
    sector_counts = {}
    s_max_val = 0
    z_max_val = 0
    for s in survivors:
        sector = sectors.containing_sector((s.x, s.y))
        if sector not in sector_counts.keys():
            sector_counts[sector] = (0, 0)
        s, z = sector_counts[sector]
        s += 1
        sector_counts[sector] = s, z
        if s > s_max_val:
            s_max_val = s

    for z in zombies:
        sector = sectors.containing_sector((z.x, z.y))
        if sector not in sector_counts.keys():
            sector_counts[sector] = (0, 0)
        s, z = sector_counts[sector]
        z += 1
        sector_counts[sector] = s, z
        if z > z_max_val:
            z_max_val = z

    total_pop = len(survivors) + len(zombies)
    # z_max_val /= total_pop
    # s_max_val /= total_pop
    """ Draws the population map to the screen in the given ScreenData """
    for sector in sector_counts:
        s, z = sector_counts[sector]
        # world_point, s_intensity, z_intensity = plot

        s_intensity = 0 if s_max_val == 0 else int(max(min(96 * s / s_max_val, 255), 0))
        z_intensity = 0 if z_max_val == 0 else int(max(min(96 * z / z_max_val, 255), 0))
        color = (s_intensity, z_intensity, 0)

        world_point = sectors.to_point(sector)
        screen_point = world_to_screen(world_point, data.pan, data.zoom)
        dim = world_to_screen((square_size, square_size), data.pan, data.zoom)
        pos = (screen_point[0] - (dim[0] / 2), screen_point[1] - (dim[1] / 2))
        pygame.draw.rect(data.screen, color, pygame.Rect(pos, dim))


def draw_sectors(data: ScreenData):
    """ Draws sector grid onto the surface of the given ScreenData"""
    x_min = round(screen_to_world((0, 0), data.pan, data.zoom)[0] // config.SECTOR_SIZE) + 1
    x_max = round(screen_to_world((config.SCREEN_RES[0], 0), data.pan, data.zoom)[0] // config.SECTOR_SIZE) + 1

    x_range = range(x_min, x_max)
    for x in x_range:
        pos_x = world_to_screen((config.SECTOR_SIZE * x, 0), data.pan, data.zoom)[0]

        pygame.draw.line(data.screen, (200, 200, 200), (pos_x, 0), (pos_x, config.SCREEN_RES[1]))

    y_min = round(screen_to_world((0, 0), data.pan, data.zoom)[1] // config.SECTOR_SIZE) + 1
    y_max = round(screen_to_world((0, config.SCREEN_RES[1]), data.pan, data.zoom)[1] // config.SECTOR_SIZE) + 1

    y_range = range(y_min, y_max)
    for y in y_range:
        pos_y = world_to_screen((0, config.SECTOR_SIZE * y), data.pan, data.zoom)[1]

        pygame.draw.line(data.screen, (200, 200, 200), (0, pos_y), (config.SCREEN_RES[0], pos_y))
