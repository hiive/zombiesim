import enum
import collections
from . import drawing
from . import population
from . import sectors
from . import config


class RoadViews(enum.Enum):
    No = enum.auto()
    Snaps = enum.auto()
    Branches = enum.auto()


def labels(screen_data, input_data, path_data, selection, city, survivors, zombies, eligible_count, iteration):
    mouse_world_pos = drawing.screen_to_world(input_data.pos, screen_data.pan, screen_data.zoom)

    debug_labels_left = []
    debug_labels_right = []

    mx, my = input_data.pos
    debug_labels_left.append(f"Pointer (screen): {mx}, {my}")
    wx, wy = mouse_world_pos
    debug_labels_left.append(f"    (world): {wx:.2f}, {wy:.2f}")
    # debug_labels_left.append("    pop_at: {}".format(city.pop.at_point(mouse_world_pos)))
    debug_labels_left.append("    sec_at: {}".format(sectors.containing_sector(mouse_world_pos)))
    px, py = screen_data.pan
    debug_labels_left.append(f"Pan: {px:.2f}, {py:.2f}")
    debug_labels_left.append(f"Zoom: {screen_data.zoom:.2f}")

    survivor_count = len(survivors)  # sum([1 for s in survivors if not s.is_infected])
    infected_count = sum([1 for s in survivors if s.is_infected])
    panicked_count = sum([1 for s in survivors if s.is_panicked])
    corpse_count = sum([1 for z in zombies if z.is_destroyed])
    pending_zombie_count = sum([1 for z in zombies if z.is_corpse()]) - corpse_count
    zombie_count = sum([1 for z in zombies if not z.is_corpse()])

    debug_labels_left.append("")
    debug_labels_left.append("")
    debug_labels_left.append(f"Iteration: {iteration}")
    debug_labels_left.append("")
    debug_labels_left.append(f"Survivors: {survivor_count}")
    debug_labels_left.append(f"  Eligible: {eligible_count}")
    debug_labels_left.append(f"  Infected: {infected_count}")
    debug_labels_left.append(f"  Panicked: {panicked_count}")
    debug_labels_left.append(f"Corpses: {corpse_count}")
    debug_labels_left.append(f"Pre-Z  : {pending_zombie_count}")
    debug_labels_left.append(f"Zombies: {zombie_count}")


    """
    if selection is not None:
        debug_labels_left.append("Selected: {}".format(str(selection.road.global_id)))
        if selection.road.parent is not None:
            debug_labels_left.append("    Parent: {}".format(str(selection.road.parent.global_id)))
        else:
            debug_labels_left.append("    Parent: None")
        debug_labels_left.append("    dir: {}".format(str(selection.road.dir())))
        debug_labels_left.append("    links_s: {}".format(str(selection.start_ids)))
        debug_labels_left.append("    links_e: {}".format(str(selection.end_ids)))
        debug_labels_left.append("    has_snapped: {}".format(str(selection.road.has_snapped)))
        debug_labels_left.append("    sectors: {}".format(str(selection.selected_sectors)))
        debug_labels_left.append("    length: {}".format(selection.road.length()))
    else:
        debug_labels_left.append("Selected: None")
    debug_labels_left.append("Path Length: {}".format(path_data.length))
    """
    debug_labels_right.append("Seed: {}".format(str(config.ROAD_SEED)))

    # debug_labels_right.append("# of segments: {}".format(str(config.MAX_SEGS)))

    return debug_labels_left, debug_labels_right


SHOW_INFO = True
SHOW_ROAD_VIEW = RoadViews.No
SHOW_ROAD_ORDER = False
SHOW_HEATMAP = False
SHOW_SECTORS = False
SHOW_ISOLATE_SECTOR = False
SHOW_MOUSE_SECTOR = False
