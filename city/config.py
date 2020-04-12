ROAD_SEED = 200972
MAX_SEGS = 1000
SCREEN_RES = (1200, 950)
HIGHWAY_LENGTH = 400
STREET_LENGTH = 300

PATH_HIGHWAY_WEIGHT = 0.75

MIN_DIST_EDGE_CROSS = 350
MIN_DIST_EDGE_CONTAINED = 50

SECTOR_SIZE = 550

HIGHWAY_BRANCH_POP = 0.1
HIGHWAY_BRANCH_CHANCE = 0.1
STREET_BRANCH_POP = 0.45
STREET_BRANCH_CHANCE = 0.8
STREET_EXTEND_POP = 0.4

SNAP_VERTEX_RADIUS = 50
SNAP_EXTEND_RADIUS = 50

MIN_ANGLE_DIFF = 30

HIGHWAY_MAX_ANGLE_DEV = 15
BRANCH_MAX_ANGLE_DEV = 1

ROAD_WIDTH = 6
ROAD_WIDTH_HIGHWAY = 6
ROAD_WIDTH_SELECTION = 6
ROAD_WIDTH_PATH = 6
ROAD_WIDTH_THRESHOLD = 6

ZOOM_GRANULARITY = 30


# zombie sim additions
ENTITY_SIZE = 3

INIT_ZOMBIES = 1
INIT_SURVIVORS = 4000
INIT_INFECTED = 0

ZOMBIE_ATTACK_RANGE = 30
ZOMBIE_SPEED = 2
ZOMBIE_HUNT_SPEED = 4
ZOMBIE_HUNT_RANGE = 100
ZOMBIE_RAISE_DELAY = 50
ZOMBIE_RAISE_CHANCE = 0.99
ZOMBIE_WANDER_DIRECTION_CHANGE_PROBABILITY = 0.00005
ZOMBIE_KILL_PROBABILITY = 0.5
ZOMBIE_TARGET_FOLLOW_PROBABILITY = 0.5
ZOMBIE_WOUND_PROBABILITY = 0.99
ZOMBIE_DESTRUCTION_PROBABILITY = 0.0025
ZOMBIE_SAME_FACING_ATTACK_MODIFIER = 1.0
ZOMBIE_DIFFERENT_FACING_ATTACK_MODIFIER = 3.0

INFECTED_PANIC_TIME_MULTIPLIER = 4
INFECTED_INCUBATION_MAX_TIME = 2000

SURVIVOR_SPEED = 5
SURVIVOR_PANIC_RANGE = 25
SURVIVOR_PANIC_SPEED = 15
SURVIVOR_PANIC_DURATION = 60
SURVIVOR_SEES_DEATH_PANIC_PROBABILITY = 0.995
SURVIVOR_SEES_PANICKED_OR_INFECTED_PANIC_PROBABILITY = 0.2
SURVIVOR_TARGET_FOLLOW_PROBABILITY = 0.9
SURVIVOR_WANDER_DIRECTION_CHANGE_PROBABILITY = 0.00001



"""
Zombies are grey, move very slowly and change direction randomly and frequently unless they can see something moving in 
front of them, in which case they start walking towards it. After a while they get bored and wander randomly again.

If a zombie finds a survivor standing directly in front of it, it bites and infects them; the survivor immediately joins
 the ranks of the undead.

Survivors are pink and run five times as fast as zombies, occasionally changing direction at random. 
If they see a zombie directly in front of them, they turn around and panic.

Panicked survivors are bright pink and run twice as fast as other survivors. 
If a survivor sees another panicked survivor, it starts panicking as well. A panicked survivor who has seen nothing to 
panic about for a while will calm down again.
"""