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
MINIMUM_LIGHT_DEPTH_THRESHOLD = 3000  # units (u)
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
CHASER_DISTANCE_FROM_FOE = 800

X_LEFT_MARGIN = 1000
X_RIGHT_MARGIN = 9000


# Define the data structures as namedtuples
#===========================================================================
#                            Classes
#===========================================================================

class Vector(NamedTuple):
    x: float
    y: float

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    # override unary minus
    def __neg__(self):
        return Vector(-self.x, -self.y)

    def perpendicular(self):
        return Vector(-self.y, self.x)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def dot(self, vector2):   # dot_product
        return self.x * vector2.x + self.y * vector2.y

    def normalize(self):
        norm = math.sqrt(self.x ** 2 + self.y ** 2)
        if norm == 0:
            return self
        return Vector(self.x / norm, self.y / norm)

    def is_behind(self, vector2):
        return self.dot(vector2) < 0

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
    SINKER_LOW = 1
    SINKER_MID1 = 2
    SINKER_MID2 = 3
    FAST = 4
    CHASER = 5

SINKER_COMPATIBLE_POSITIONS = (1, 2)
FAST_COMPATIBLE_POSITIONS = (0, 3)

class SinkerSide(Enum):
    LEFT = 1
    RIGHT = 2
    FULL_LEFT = 3
    FULL_RIGHT = 4

class SinkerState(Enum):
    SINKING = 1
    CROSSING = 2
    RISING = 3

class FastState(Enum):
    CROSSING_TOP_RIGHT = 1
    CROSSING_TOP_LEFT = 2

class FishGlobalState:
    fish_id : int
    detail : FishDetail
    is_monster : int
    last_seen_loop : Optional[int]
    predicted_pos : Optional[Vector]
    last_seen_speed : Optional[Vector]
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
        
    def __str__(self):
        return f"FishGlobalState {self.fish_id} {self.detail} {self.is_monster} {self.last_seen_loop} {self.predicted_pos} {self.last_seen_speed} {self.is_chasing_us__last_loop} {self.p_distance}"

    __repr__ = __str__


# clamp between 0 and 10000
def clamp(value, min_value=0, max_value=10000):
    return max(min(value, max_value), min_value)


class Drone:
    drone_id: int
    pos: Vector
    dead: bool
    battery: int
    scans: List[int]
    role: DroneRole
    target: Vector  # Target is the target that might dodge a monster or just follow the strategy_target
    waiting: bool
    is_light_enabled: bool
    context: Dict[str, object]
    monsters_nearby = Dict[int, int]

    def __init__(self, drone_id, pos: Vector, dead, battery, scans):
        self.drone_id = drone_id
        self.pos = pos
        self.dead = dead
        self.battery = battery
        self.scans = scans
        self.role = None # type:ignore (optional)
        self.target = pos
        self.waiting = False
        self.is_light_enabled = False
        self.state = None
        self.context = {}
        self.monsters_nearby = {}

    def get_order_move(self):
        str_light = f"{1 if self.is_light_enabled else 0}"
        if(self.waiting):
            return f"WAIT {str_light}"
        return f"MOVE {clamp(round(self.target.x))} {clamp(round(self.target.y))} {str_light}"

    def detect_close_monsters(self):
        MAX_EVASION_LOOPS = 5
        return [fs for fs in fish_global_map.values() \
                if fs.detail.type == CREATURE_TYPE_MONSTER \
                    and fs.predicted_pos \
                    and dist(self.pos, fs.predicted_pos) < MONSTER_MAX_DETECTION_RADIUS \
                    and loop - fs.is_chasing_us__last_loop.get(self.drone_id,999) < MAX_EVASION_LOOPS]


    # (1) 2300<>2000 : get around the monster
    # at each turn, compute the norm of diff to monster
    # choose betweeen norm and -norm based on target
    # (2) 0 <> 1000: flee!!!

    def evade_all_monsters(self):
        # 0. Detect all monsters
        close_monsters = self.detect_close_monsters()
        if close_monsters:
            print_debug("%s detected %d monsters %s", self.name(), len(close_monsters), close_monsters)
            # 1. Evade only one monster
            # if dist(self.pos, fish.pos) < 700:
            #     flee(monster)
            closest = min(close_monsters, key=lambda fish: dist(self.pos, fish.predicted_pos))  # type:ignore (optional)
            self.evade_monster(closest)
            # 2. Evade all monsters

    def evade_monster(self, monster: FishGlobalState):
        # Turn off lights to start evading
        self.is_light_enabled = False

        # Set the evade target to move during the current loop
        self.target = choose_best_way_around_to_target(self, monster, self.target)

    def name(self):
        return f"{self.role.name if self.role else 'ø'}-{self.drone_id}"

    def __str__(self):
        return f"""{self.name()} pos={self.pos} {"DEAD!" if self.dead else ""} batt={self.battery}
        scans#{len(self.scans)} target={self.target} {self.waiting} {self.is_light_enabled} context={self.context}"""

    __repr__ = __str__

    def current_light_radius(self):
        return DRONE_LIGHT_RADIUS_POWERFUL if self.is_light_enabled else DRONE_LIGHT_RADIUS


# FishId is type alias int
FishId = int

# Map of all fish with capture status: 
# type: Dict[int, Fish]
fish_global_map: Dict[FishId, FishGlobalState] = {}

def update_positions(drones, visible_fish):

    # for fish_id in my_radar_blips:
    # future: identify 9 zones.

    def update_dist(fs: FishGlobalState):
        for drone in drones:
            distance = dist(fs.predicted_pos, drone.pos) # type:ignore (optional)
            fs.p_distance[drone]  = distance
            if fs.is_monster:
                fs.is_chasing_us__last_loop[drone] = True
                if distance < drone.current_light_radius():
                    drone.monsters_nearby[fs.fish_id] = distance
                    fs.is_chasing_us__last_loop[drone] = False

    # update visible fish
    for fish in visible_fish:
        id = fish.fish_id
        if id not in fish_global_map:
            fish_global_map[id] = FishGlobalState(id, fish.detail)
        fs = fish_global_map[id]
        fs.last_seen_loop = loop
        fs.predicted_pos = fish.pos
        fs.last_seen_speed = fish.speed
        update_dist(fs)

    # update unseen fish with speed
    for id, fs in fish_global_map.items():
        if fs.last_seen_loop and fs.last_seen_loop != loop:
            fs.predicted_pos = fs.predicted_pos + fs.last_seen_speed  #type:ignore (optional)
            update_dist(fs)

    for drone in drones:
        for monster_id, distance in drone.monsters_nearby.items():
            print_debug("%s chased by Monster %d at dist %d", drone.drone_id, monster_id, distance)

        closest_objects = sorted(fish_global_map.values(), key=lambda fs: fs.p_distance.get(drone, 999))[:3]
        s = drone.name() + " closest fishes"
        for o in closest_objects:
            s += "| %s=%s %s d=%d " % ("M" if o.is_monster else "F", o.fish_id,
                                 "chase_since=%d" % o.is_chasing_us__last_loop.get(drone.drone_id, 999) if o.is_monster else "",
                                 o.p_distance[drone],
                                 )
        print_debug(s)

def flee(drone, monster, strategic_target):
    vector_to_monster = monster.pos - drone.pos
    direction = (-vector_to_monster).normalize()
    return target_from_direction(drone.pos, direction)


def target_from_direction(pos, direction):
    direction = direction.normalize() * 600
    target = pos + direction
    initial_target = target
    if target.x < 0:
        direction = direction / (direction.x/pos.x)
        target = pos + direction
    if target.y < 0:
        direction = direction / (direction.y/pos.y)
        target = pos + direction
    if target.x > 10000:
        direction = direction / (direction.x/(10000-pos.x))
        target = pos + direction
    if target.y > 10000:
        direction = direction / (direction.y/(10000-pos.y))
        target = pos + direction
    
    if target != initial_target:
        print_debug("Target adjusted from %s to %s", initial_target, target)

    return target

def choose_best_way_around_to_target(drone: Drone, monster: FishGlobalState, strategic_target: Vector) -> Vector:
    """
    In Python, you can determine which of two vectors points more directly towards a target 
    from your position by calculating the dot product of the vectors created 
    from your position to the target and from your position to the end of each vector.
    The dot product will tell you about the alignment of the vectors.
    The vector with the larger dot product (when normalized) points more directly toward the target.

    *Calculate the vectors from your current position to the target and from your position to the tip of each vector.
    *Normalize these vectors (make their length equal to 1) to ensure a fair comparison.
    *Calculate the dot product of the normalized vector from your position to the target with each of the other normalized vectors.
    *Compare the dot products, and choose the vector with the higher dot product value.

    """
    assert monster.predicted_pos

    # Your position
    pos = drone.pos
    
    # Calculate vectors from position to target and to the tips of the vectors  
    to_target_vector = strategic_target - pos
    vector_to_monster = monster.predicted_pos - pos

    print_debug("%s, DOT: %d", drone.name(), to_target_vector.dot(vector_to_monster))
    if to_target_vector.is_behind(vector_to_monster):
        print_debug("%s: No need to go around the monster", drone.name())
        return strategic_target

    around1 = vector_to_monster.perpendicular()
    around2 = -around1

    # Normalize the vectors  
    to_target_vector_norm = to_target_vector.normalize()  
    around_norm1 = around1.normalize()  
    around_norm2 = around2.normalize()    

    # Choose the vector that has the larger dot product  
    dot_product1 = to_target_vector_norm.dot(around_norm1)
    dot_product2 = to_target_vector_norm.dot(around_norm2)
    if dot_product1 > dot_product2:  
        print_debug("%s: avoiding monster by right", drone.name())
        direction: Vector = around_norm1
    else:
        print_debug("%s: avoiding monster by left", drone.name())
        direction: Vector = around_norm2

    return target_from_direction(pos, direction)
#
# evasion strategy:
# - activate strategy if there is a monster *detected**:
#   - turn light down
#   - avoid detection

#===========================================================================
#                            Functions
#===========================================================================
def order_move(target: Vector, light: int):
    print(f"MOVE {target.x} {target.y} {1 if light else 0}")

def order_wait(light: int):
    print(f"WAIT {1 if light else 0}")

def print_debug(message, *a):
    print("#%d| %s" %(loop + 1, message % a) if a else message, flush= True, file= sys.stderr)

def dist(a: Vector, b: Vector):
    return int(math.dist(a, b))

fish_details: Dict[int, FishDetail] = {}
def is_monster_close(drone):
    # get the list of blips reconciliated with fish_details via fish_id
    detected = len([fish for fish in visible_fish if fish.detail.type == CREATURE_TYPE_MONSTER and dist(drone.pos, fish.pos) < MONSTER_MAX_DETECTION_RADIUS])
    if detected:
        print_debug("%s detected Monster detected %s")
    return detected > 0

fish_count = int(input())
for _ in range(fish_count):
    fish_id, color, _type = map(int, input().split())
    fish_details[fish_id] = FishDetail(color, _type)

#===================================================================================================
#                                          Chase strategy
#===================================================================================================
def run_chase(drone):
    # Follow foe drone associated to your drone
    # Assign the drone target just behind the foe drone y - 100
    # If the foe is dead, evade and leave the zone
    if(loop == 0):
        foes_by_distance = sorted(foe_drones, key=lambda foe: dist(drone.pos, foe.pos))
        drone.context["chasing_id"] = foes_by_distance[0].drone_id
    
    foe = [foe for foe in foe_drones if foe.drone_id == drone.context["chasing_id"]][0]
    if foe.dead:
        drone.target = Vector(foe.pos.x, 500)
    else:
        drone.target = Vector(foe.pos.x, foe.pos.y - CHASER_DISTANCE_FROM_FOE)
        
def run_fast(drone):
    drone.is_light_enabled = not is_monster_close(drone) and drone.is_light_enabled
    if drone.pos.x % 800 == 0:
        drone.target = Vector(drone.target.x + 1600, FAST_MAX_DEPTH if drone.target.y < 500 else 499)

Y_SURFACE = 499
#===================================================================================================
#                                          sinker strategy
#===================================================================================================
def run_sinker(y_max_depth, is_full=False):
    def inner(drone):
        #===========================
        #     INIT First loop
        #===========================
        if loop == 0:
            if not is_full:
                drone.context["side"] = SinkerSide.RIGHT if drone.pos.x > 5000 else SinkerSide.LEFT
                if drone.context["side"] == SinkerSide.LEFT:
                    drone.context["target_stack"] = [Vector(X_LEFT_MARGIN, y_max_depth), Vector(5000, y_max_depth), Vector(5000, Y_SURFACE)]
                else:
                    drone.context["target_stack"] = [Vector(X_RIGHT_MARGIN, y_max_depth), Vector(5000, y_max_depth), Vector(5000, Y_SURFACE)]
            else:
                drone.context["side"] = SinkerSide.FULL_RIGHT if drone.pos.x > 5000 else SinkerSide.FULL_LEFT
                if drone.context["side"] == SinkerSide.FULL_LEFT:
                    drone.context["target_stack"] = [Vector(X_LEFT_MARGIN, y_max_depth), Vector(X_RIGHT_MARGIN, y_max_depth), Vector(X_RIGHT_MARGIN, Y_SURFACE)]
                else:
                    drone.context["target_stack"] = [Vector(X_RIGHT_MARGIN, y_max_depth), Vector(X_LEFT_MARGIN, y_max_depth), Vector(X_LEFT_MARGIN, Y_SURFACE)]
            drone.context["state"] = SinkerState.SINKING

        

        #===========================
        #     Change state
        #===========================
        # target1 = if SinkerSide.FULL_RIGHT else

        # if drone.pos.y >= y_max_depth and drone.context["state"] == SinkerState.SINKING:
        #     drone.context["state"] = SinkerState.CROSSING
        # elif drone.pos.y >= y_max_depth and drone.context["state"] == SinkerState.CROSSING \
        #         and checkpoints - 400 <= drone.pos.x <= checkpoints + 400:
        #     drone.context["state"] = SinkerState.RISING
        # elif drone.pos.y <= 500 and drone.context["state"] == SinkerState.RISING:
        #     drone.context["state"] = SinkerState.SINKING
        #     drone.role = DroneRole.SINKER_MID2 if drone.role == DroneRole.SINKER_MID1 else DroneRole.SINKER_LOW
        #     drone.context["side"] = SinkerSide.RIGHT if drone.context["side"] == SinkerSide.LEFT else SinkerSide.LEFT

        # #===========================
        # #     state -> target
        # #===========================
        # if(drone.context["state"] == SinkerState.SINKING):
        #     drone.target = Vector(X_RIGHT_MARGIN if drone.context["side"] == SinkerSide.RIGHT else X_LEFT_MARGIN, y_max_depth)
        # elif(drone.context["state"] == SinkerState.CROSSING):
        #     drone.target = Vector(X_LEFT_MARGIN if drone.context["side"] == SinkerSide.RIGHT else X_RIGHT_MARGIN, y_max_depth)
        # elif(drone.context["state"] == SinkerState.RISING):
        #     drone.target = Vector(drone.pos.x, 499)
    return inner

strategies = {
    DroneRole.FAST: run_fast,
    DroneRole.SINKER_LOW: run_sinker(8000),
    DroneRole.SINKER_MID1: run_sinker(3500, is_full=True),
    DroneRole.SINKER_MID2: run_sinker(6000, is_full=True),
    DroneRole.CHASER: run_chase,
}

loop = 0
drone_by_id: Dict[int, Drone] = {}
# position and battery/dead of my drones
my_drones: List[Drone] = []
# position and battery/dead of the enemy drones
foe_drones: List[Drone] = []

# game loop
while True:
    my_scans: List[int] = []
    foe_scans: List[int] = []
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
        if loop == 0:
            drone = Drone(drone_id, pos, dead == '1', battery, [])
            drone_by_id[drone_id] = drone
            my_drones.append(drone)
        else:
            drone_by_id[drone_id].pos = pos
            drone_by_id[drone_id].dead = dead == '1'
            drone_by_id[drone_id].battery = battery
        my_radar_blips[drone_id] = []

    foe_drone_count = int(input())
    for _ in range(foe_drone_count):
        drone_id, drone_x, drone_y, dead, battery = map(int, input().split())
        pos = Vector(drone_x, drone_y)
        if loop == 0:
            drone = Drone(drone_id, pos, dead == '1', battery, [])
            drone_by_id[drone_id] = drone
            foe_drones.append(drone)
        else:
            # update existing drone
            drone_by_id[drone_id].pos = pos
            drone_by_id[drone_id].dead = dead == '1'
            drone_by_id[drone_id].battery = battery


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

    # call once
    update_positions(my_drones, visible_fish)

    for drone in my_drones:
        if loop == 0:
            drone.role = DroneRole.SINKER_MID1 if drone.drone_id in FAST_COMPATIBLE_POSITIONS else DroneRole.SINKER_MID2

        #===========================
        #     Init each loop
        #===========================
        print_debug("Start %s", drone)
        # Turn on lights every 5 loops by default
        drone.is_light_enabled = drone.pos.y > MINIMUM_LIGHT_DEPTH_THRESHOLD and loop % 5 == 0

        #===========================
        #     Loop strategy
        #===========================
        strategies[drone.role](drone)

        # Detect any monsters
        # In case a monster is detected, evade it !
        drone.evade_all_monsters()


        print(drone.get_order_move())

    loop = loop + 1
