#  coding challenge  on a platform  CodinGame.
# Here's a summary of the game mechanics and what players need to consider when creating a strategy or writing code to control their drones:
# Objective

#     Win more points than your opponent by scanning the most fish within a 200-turn game or until one player can no longer catch up in points.

# The Map

#     A square ocean floor with sides of 10,000 units (u).
#     Coordinates (0, 0) are at the top left corner.

# Drones

#     Each player has two drones.
#     Drones can move each turn up to 600u if motors are activated or sink 300u if not.
#     Scanning radius is 800u, extendable to 2000u by increasing light power, which drains the battery.
#     Drones must resurface to save scans and score points.
#     Battery starts at 30 points, recharges by 1 if light is not increased, and drains by 5 with increased light.

# Fish

#     Fish have specific types and colors and move within defined habitat zones.
#     Fish move 200u each turn or 400u if frightened by nearby drone activity.
#     Scanning all fish of the same type or color grants bonus points, especially if you're the first.

# Depth Monsters

#     Monsters chase drones if blinded by the light.
#     Monsters can cause drones to enter "emergency" mode, losing all unsaved scans.
#     Monsters swim aggressively towards drones within light range.

# Scoring

#     Points are awarded for scanning fish, with more points for rarer types.
#     Bonus points for being the first to save a scan or a combination.

# Victory Conditions

#     The game ends after 200 turns or if a player secures an unassailable lead.
#     Saving scans of all remaining fish also ends the game.

# Defeat Conditions

#     Failing to provide a valid command within the time limit for each drone.

# Game Protocol

#     The game provides initialization input with details about creatures.
#     Each game turn provides scores, drone and creature status, and allows players to issue commands.
#     Players command their drones by sending MOVE or WAIT instructions, with optional light power adjustments.

# Constraints

#     There's a creature count range and a fixed number of drones.
#     Response time per turn is capped at 100ms, with a longer allowance for the first turn.


from typing import List, NamedTuple, Dict, Optional, TypeAlias
import sys
import math
from enum import Enum


# Map dimensions  
MAP_SIZE = 10000  # units (u)  
  
# Drones  
DRONE_MOVE_SPEED = 600  # units (u) per turn  
DRONE_SINK_SPEED = 300  # units (u) if motors not activated  
DRONE_LIGHT_RADIUS = 800  # units (u)  
DRONE_LIGHT_RADIUS_POWERFUL = 2000  # units (u)  
BATTERY_DRAIN_POWERFUL_LIGHT = 5  # points  
BATTERY_RECHARGE_RATE = 1  # point per turn  
BATTERY_CAPACITY = 30  # full capacity  
DRONE_SURFACE_Y_THRESHOLD = 500  # units (u)  
  
# Fish  
FISH_MOVE_DISTANCE = 200  # units (u) per turn  
FISH_FRIGHTENED_MOVE_DISTANCE = 400  # units (u) per turn  
FISH_FRIGHTENED_DISTANCE_THRESHOLD = 1400  # units (u)  
  
# Fish types and habitat zones  
FISH_TYPE_0_MIN_Y = 2500  
FISH_TYPE_0_MAX_Y = 5000  
FISH_TYPE_1_MIN_Y = 5000  
FISH_TYPE_1_MAX_Y = 7500  
FISH_TYPE_2_MIN_Y = 7500  
FISH_TYPE_2_MAX_Y = 10000  
  
# Monsters  
MONSTER_AGGRESSIVE_SPEED = 540  # units (u) per turn  
MONSTER_NON_AGGRESSIVE_SPEED = 270  # units (u) per turn  
MONSTER_MIN_DETECTION_RADIUS = DRONE_LIGHT_RADIUS + 300  # units (u)  
MONSTER_MAX_DETECTION_RADIUS = DRONE_LIGHT_RADIUS_POWERFUL + 300  # units (u)  
MONSTER_INTERACTION_RADIUS = 500  # units (u)  
  
# Scoring  
SCAN_POINTS_TYPE_0 = 1  
SCAN_POINTS_TYPE_1 = 2  
SCAN_POINTS_TYPE_2 = 3  
BONUS_POINTS_SAME_COLOR = 3  
BONUS_POINTS_SAME_TYPE = 4  
  
# Multipliers for first to save  
FIRST_TO_SAVE_MULTIPLIER = 2  
  
# Game conditions  
MAX_TURNS = 200  
  
# Creature and monster types  
CREATURE_TYPE_MONSTER = -1  
  
# Radar indicators  
RADAR_TOP_LEFT = "TL"  
RADAR_TOP_RIGHT = "TR"  
RADAR_BOTTOM_RIGHT = "BR"  
RADAR_BOTTOM_LEFT = "BL"  
  
# Time constraints  
TIME_PER_TURN_MS = 100  # milliseconds  
TIME_FIRST_TURN_MS = 1000  # milliseconds  
  
# Initialization details  
CREATURE_COUNT_MIN = 13  
CREATURE_COUNT_MAX = 20  
DRONE_COUNT = 2  

FAST_MAX_DEPTH = 5000


# Define the data structures as namedtuples
#===========================================================================
#                            Classes
#===========================================================================

class Vector(NamedTuple):
    x: int
    y: int

    def __sum__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

class FishDetail(NamedTuple):
    color: int
    type: int

# visible_fish = List[Fish]
class VisibleFish(NamedTuple):
    fish_id: int
    pos: Vector
    speed: Vector
    detail: FishDetail

class RadarBlip(NamedTuple):
    fish_id: int
    dir: str  # "TL"RADAR_TOP_LEFT etc.

class DroneRole(Enum):
    SINKER = 1
    FAST = 2

SINKER_COMPATIBLE_POSITIONS = (1, 2)
FAST_COMPATIBLE_POSITIONS = (0, 3)

# enum dronesinkerstate
class DroneState(Enum):
    SINKER_SINKING = 1
    SINKER_CROSSING = 2
    SINKER_RISING = 3
    FAST_CROSSING_TOP_RIGHT = 1
    FAST_CROSSING_TOP_LEFT = 2

class Drone:
    drone_id: int
    pos: Vector
    dead: bool
    battery: int
    scans: List[int]
    role: DroneRole
    target: Vector
    clockwise: bool
    waiting: bool
    is_light_enabled: bool
    state: Optional[DroneState]

    def __init__(self, drone_id, pos, dead, battery, scans):
        self.drone_id = drone_id
        self.pos = pos
        self.dead = dead
        self.battery = battery
        self.scans = scans
        self.role = None # type:ignore (optional)
        self.target = pos
        self.clockwise = False
        self.waiting = False
        self.is_light_enabled = False
        self.state = None
    
    def get_order_move(self):
        str_light = f"{1 if self.is_light_enabled else 0}"
        if(self.waiting):
            return f"WAIT {str_light}"
        return f"MOVE {self.target.x} {self.target.y} {str_light}"
    
    def is_monster_close(self):
        # get the list of blips reconciliated with fish_details via fish_id
        detected = len([fish for fish in visible_fish if fish.detail.type == CREATURE_TYPE_MONSTER and dist(self.pos, fish.pos) < MONSTER_MAX_DETECTION_RADIUS])
        if detected:
            print_debug("%rone s detected monster %s", self.role, detected)
        return detected > 0

class FishGlobalState:
    fish_id : int
    detail : int
    is_monster : int
    last_seen_loop : Optional[int]
    predicted_pos : Optional[int]
    last_seen_speed : Optional[int]
    is_chasing_us__last_loop : Dict[int, int]
    p_distance: Dict[int, int]


    def __init__(self, fish_id, detail):
        self.fish_id = fish_id
        self.detail = detail
        self.is_monster = detail.type == CREATURE_TYPE_MONSTER
        self.last_seen_loop = 0
        self.predicted_pos = None
        self.last_seen_speed = None
        self.is_chasing_us__last_loop = {}
        self.p_distance = {}

# FishId is type alias int
FishId = int

# Map of all fish with capture status: 
# type: Dict[int, Fish]
fish_global_map: Dict[FishId, FishGlobalState] = {}

def update_positions(drones, visible_fish, my_radar_blips):

    # for fish_id in my_radar_blips:
    # future: identify 9 zones.

    # update visible fish
    for fish in visible_fish:
        id = fish.fish_id
        if id not in fish_global_map:
            fish_global_map[id] = FishGlobalState(id, fish.detail)
        fs = fish_global_map[id]
        fs.last_seen_loop = loop
        fs.predicted_pos = fish.pos
        fs.last_seen_speed = fish.speed
        for drone in drones:
            distance = dist(fish.pos, drone.pos)
            fs.p_distance[drone]  = distance
            if fs.is_monster:
                fs.is_chasing_us__last_loop[drone] = True
                if distance < drone.light_radius:
                    fs.is_chasing_us__last_loop[drone] = False
 

    # update unseen fish with speed
    for id, fs in fish_global_map.items():
        if fs.last_seen_loop and fs.last_seen_loop != loop:
            fs.predicted_pos = fs.predicted_pos + fs.last_seen_speed  #type:ignore (optional)


# TODO monster evasion strategy:
# - activate strategy if there is a monster *detected**:
#   - turn light down
#   - avoid detection
#   - where would 

#===========================================================================
#                            Functions
#===========================================================================
def order_move(target: Vector, light: int):
    print(f"MOVE {target.x} {target.y} {1 if light else 0}")

def order_wait(light: int):
    print(f"WAIT {1 if light else 0}")

def print_debug(message, *a):
    print(message % a if a else message, flush= True, file= sys.stderr)

def dist(a: Vector, b: Vector):
    return int(math.dist(a, b))

fish_details: Dict[int, FishDetail] = {}
def is_monster_close(drone):
    # get the list of blips reconciliated with fish_details via fish_id
    detected = len([fish for fish in visible_fish if fish.detail.type == CREATURE_TYPE_MONSTER and dist(drone.pos, fish.pos) < MONSTER_MAX_DETECTION_RADIUS])
    if detected:
        print_debug("Monster detected %s", detected)
    return detected > 0

fish_count = int(input())
for _ in range(fish_count):
    fish_id, color, _type = map(int, input().split())
    fish_details[fish_id] = FishDetail(color, _type)

def run_fast(drone):
    drone.is_light_enabled = not is_monster_close(drone) and drone.is_light_enabled
    if drone.pos.x % 800 == 0:
        drone.target = Vector(drone.target.x + 1600, FAST_MAX_DEPTH if drone.target.y < 500 else 499)

def run_sinker(drone):
    if loop == 0:
        drone.clockwise = drone.pos.x > 5000
    drone.is_light_enabled = not is_monster_close(drone) and loop % 5 == 0

    if drone.state == None:
        drone.state = DroneState.SINKER_SINKING
        drone.clockwise = drone.pos.x > 5000 
    if drone.pos.y == 8000 and drone.state == DroneState.SINKER_SINKING:
        drone.state = DroneState.SINKER_CROSSING
    elif drone.pos.y == 8000 and drone.state == DroneState.SINKER_CROSSING and (drone.pos.x in (2000, 8000)):
        drone.state = DroneState.SINKER_RISING
    elif drone.pos.y == 500 and drone.state == DroneState.SINKER_RISING:
        drone.state = DroneState.SINKER_SINKING

    BOTTOM_POWERFUL_LIGHT_THRESHOLD = 8000  # units (u) 
    bottom_left_corner_light = Vector(DRONE_LIGHT_RADIUS_POWERFUL, BOTTOM_POWERFUL_LIGHT_THRESHOLD)
    bottom_right_corner_light = Vector(10000 - DRONE_LIGHT_RADIUS_POWERFUL, BOTTOM_POWERFUL_LIGHT_THRESHOLD)

    if(drone.state == DroneState.SINKER_SINKING):
        drone.target = Vector(8000 if drone.clockwise else 2000, 8000)
    elif(drone.state == DroneState.SINKER_CROSSING):
        drone.target = Vector(2000 if drone.clockwise else 8000, 8000)
    elif(drone.state == DroneState.SINKER_RISING):
        drone.target = Vector(drone.pos.x, 500)

strategies = {
    DroneRole.FAST: run_fast,
    DroneRole.SINKER: run_sinker,
}

loop = 0
# game loop
while True:
    loop = loop + 1
    my_scans: List[int] = []
    foe_scans: List[int] = []
    drone_by_id: Dict[int, Drone] = {}
    # position and battery/dead of my drones
    my_drones: List[Drone] = []
    # position and battery/dead of the enemy drones
    foe_drones: List[Drone] = []
    # all fish visible (within DRONE_LIGHT_RADIUS or more for monsters) by both drones
    visible_fish: List[VisibleFish] = []
    # for each drone_id, a list of blips (TL=TopLeft etc.)
    my_radar_blips: Dict[int, List[RadarBlip]] = {}

    my_score = int(input())
    foe_score = int(input())

    my_scan_count = int(input())
    for _ in range(my_scan_count):
        fish_id = int(input())
        my_scans.append(fish_id)

    foe_scan_count = int(input())
    for _ in range(foe_scan_count):
        fish_id = int(input())
        foe_scans.append(fish_id)

    my_drone_count = int(input())
    for _ in range(my_drone_count):
        drone_id, drone_x, drone_y, dead, battery = map(int, input().split())
        pos = Vector(drone_x, drone_y)
        drone = Drone(drone_id, pos, dead == '1', battery, [])
        drone_by_id[drone_id] = drone
        my_drones.append(drone)
        my_radar_blips[drone_id] = []

    foe_drone_count = int(input())
    for _ in range(foe_drone_count):
        drone_id, drone_x, drone_y, dead, battery = map(int, input().split())
        pos = Vector(drone_x, drone_y)
        drone = Drone(drone_id, pos, dead == '1', battery, [])
        drone_by_id[drone_id] = drone
        foe_drones.append(drone)

    drone_scan_count = int(input())
    for _ in range(drone_scan_count):
        drone_id, fish_id = map(int, input().split())
        drone_by_id[drone_id].scans.append(fish_id)

    visible_fish_count = int(input())
    for _ in range(visible_fish_count):
        fish_id, fish_x, fish_y, fish_vx, fish_vy = map(int, input().split())
        pos = Vector(fish_x, fish_y)
        speed = Vector(fish_vx, fish_vy)
        visible_fish.append(VisibleFish(fish_id, pos, speed, fish_details[fish_id]))

    my_radar_blip_count = int(input())
    for _ in range(my_radar_blip_count):
        drone_id, fish_id, dir = input().split()
        drone_id = int(drone_id)
        fish_id = int(fish_id)
        my_radar_blips[drone_id].append(RadarBlip(fish_id, dir))

    for drone in my_drones:
        # Init loop
        if loop == 0:
            drone.role = DroneRole.FAST if drone.drone_id in FAST_COMPATIBLE_POSITIONS else DroneRole.SINKER

        # Init each loop
        drone.is_light_enabled = loop % 3 == 0

        # Loop strategy
        strategies[drone.role](drone)
        print(drone.get_order_move())



        # TODO: Implement logic on where to move here

        # Drone 0 should go to the middle of the map
        if drone.role == DroneRole.FAST:
            drone.is_light_enabled = not is_monster_close(drone) and drone.is_light_enabled
            if drone.pos.x % 800 == 0:
                drone.target = Vector(drone.target.x + 1600, FAST_MAX_DEPTH if drone.target.y < 500 else 499)
            print(drone.get_order_move())

        # Drone 1 should go to the bottom and racler le fond
        else:
            if loop == 0:
                drone_sinker_clockwise = drone.pos.x > 5000
            drone.is_light_enabled = not is_monster_close(drone) and loop % 5 == 0

            if drone.state == None:
                drone.state = DroneState.SINKER_SINKING
                drone.clockwise = drone.pos.x > 5000 
            if drone.pos.y == 8000 and drone.state == DroneState.SINKER_SINKING:
                drone.state = DroneState.SINKER_CROSSING
            elif drone.pos.y == 8000 and drone.state == DroneState.SINKER_CROSSING and (drone.pos.x in (2000, 8000)):
                drone.state = DroneState.SINKER_RISING
            elif drone.pos.y == 500 and drone.state == DroneState.SINKER_RISING:
                drone.state = DroneState.SINKER_SINKING

            BOTTOM_POWERFUL_LIGHT_THRESHOLD = 8000  # units (u) 
            bottom_left_corner_light = Vector(DRONE_LIGHT_RADIUS_POWERFUL, BOTTOM_POWERFUL_LIGHT_THRESHOLD)
            bottom_right_corner_light = Vector(10000 - DRONE_LIGHT_RADIUS_POWERFUL, BOTTOM_POWERFUL_LIGHT_THRESHOLD)

            if(drone.state == DroneState.SINKER_SINKING):
                drone.target = Vector(8000 if drone.clockwise else 2000, 8000)
            elif(drone.state == DroneState.SINKER_CROSSING):
                drone.target = Vector(2000 if drone.clockwise else 8000, 8000)
            elif(drone.state == DroneState.SINKER_RISING):
                drone.target = Vector(drone.pos.x, 500)
            print(drone.get_order_move())

        print_debug("Drone %s Light: %s", drone.role, drone.is_light_enabled)


        # if x > 8000 and target_x == 10000:
        #     target_x = 0
        # if x < 1000 and target_x == 0:
        #     target_y = 0
        # if x == 0 and y == 0 and target_y == 0:
        #     target_x = 10000
        #     target_y = 10000

def run_super_strategy(drone):
    passinker,
}
