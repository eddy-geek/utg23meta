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

SAFE_SCORING = 3
RUSH_DISTANCE_WITH_FOE = 800

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
    FEUILLE_MORTE = 6
    RUSH_TOP = 7

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
    predicted_pos : Vector
    last_seen_speed : Optional[Vector]
    is_chasing_us__last_loop : Dict[int, int]
    p_distance: Dict[int, int]

    def __init__(self, fish_id, detail):
        self.fish_id = fish_id
        self.detail = detail
        self.is_monster = detail.type == CREATURE_TYPE_MONSTER
        self.last_seen_loop = 0
        self.predicted_pos = Vector(-1, -1)
        self.last_seen_speed = None
        self.is_chasing_us__last_loop = {}
        self.p_distance = {}

    def __str__(self):
        return f"FishGlobalState {self.fish_id} {self.detail} {self.is_monster} {self.last_seen_loop} {self.predicted_pos} {self.last_seen_speed} {self.is_chasing_us__last_loop} {self.p_distance}"

    __repr__ = __str__


# clamp between 0 and 10000
def clamp(value, min_value=0, max_value=10000):
    return max(min(value, max_value), min_value)

class Radar:
    detected: dict[str, list[RadarBlip]]

    def __init__(self) -> None:
        self.drone = drone
        self.detected = {
            RADAR_TOP_LEFT: [],
            RADAR_TOP_RIGHT: [],
            RADAR_BOTTOM_LEFT: [],
            RADAR_BOTTOM_RIGHT: [],
        }

    def get_blips(self, direction: str) -> list[RadarBlip]:
        return self.detected[direction]

    def scan(self, radar_blips: list[RadarBlip]) -> None:
        for blip in radar_blips:
          if blip.dir == RADAR_TOP_LEFT:
              self.detected[RADAR_TOP_LEFT].append(blip)
          elif blip.dir == RADAR_TOP_RIGHT:
              self.detected[RADAR_TOP_RIGHT].append(blip)
          elif blip.dir == RADAR_BOTTOM_LEFT:
              self.detected[RADAR_BOTTOM_LEFT].append(blip)
          elif blip.dir == RADAR_BOTTOM_RIGHT:
              self.detected[RADAR_BOTTOM_RIGHT].append(blip)
          else:
              raise ValueError("Invalid blip direction")

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
    radar: Radar

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
        self.radar = Radar()

    def get_order_move(self):
        str_light = f"{1 if self.is_light_enabled else 0}"
        if(self.waiting):
            return f"WAIT {str_light}"
        return f"MOVE {clamp(round(self.target.x))} {clamp(round(self.target.y))} {str_light}"

    def detect_close_monsters(self, max_dist=MONSTER_MAX_DETECTION_RADIUS, turns_since_seen=5):
        global loop
        return [fs for fs in fish_global_map.values() \
                if fs.is_monster \
                    and fs.predicted_pos \
                    and dist(self.pos, fs.predicted_pos) < max_dist \
                    and loop - fs.is_chasing_us__last_loop.get(self.drone_id,999) < turns_since_seen]


    # (1) 2300<>2000 : get around the monster
    # at each turn, compute the norm of diff to monster
    # choose betweeen norm and -norm based on target
    # (2) 0 <> 1000: flee!!!

    def evasion_orchestrator(self):
        # TODO handling of lights to be maggressive if bot has not seen us (+300)
        close_monsters = self.detect_close_monsters()
        if close_monsters:
            print_debug("%s detected %d monsters %s", self.name(), len(close_monsters), close_monsters)
            if len(close_monsters) == 1:
                monster = close_monsters[0]
                if dist(self.pos, monster.predicted_pos) < 700:
                    self.flee(monster)
                    self.context["evading_for_turns"] = 4
                    action = "flee"
                else:
                    # closest = min(close_monsters, key=lambda fish: dist(self.pos, fish.predicted_pos))  # type:ignore (optional)
                    self.evade_monster(monster)
                    self.context["evading_for_turns"] = 2
                    action = "evade1"
            else:
                monster_position_vectors = [monster.predicted_pos for monster in close_monsters if monster.predicted_pos]  # type:ignore (optional)
                move_drone_safely(self.pos, monster_position_vectors, self.target)
                self.context["evading_for_turns"] = 3
                action = "evade_many"
            print_debug("%s: %s !!!", self.name(), action)

    def evade_monster(self, monster: FishGlobalState):
        # Turn off lights to start evading
        self.is_light_enabled = False

        # Set the evade target to move during the current loop
        self.target = choose_best_way_around_to_target(self, monster, self.target)

    def flee(self, monster):
        vector_to_monster = monster.pos - self.pos
        direction = (-vector_to_monster).normalize()
        return target_from_direction(self.pos, direction)

    def name(self):
        return f"{self.role.name if self.role else 'ø'}-{self.drone_id}"

    def __str__(self):
        return f"""{self.name()} pos={self.pos} {"DEAD!" if self.dead else ""} batt={self.battery}
        scans#{len(self.scans)} target={self.target} {self.waiting} {self.is_light_enabled} context={self.context}"""

    __repr__ = __str__

    def current_light_radius(self):
        return DRONE_LIGHT_RADIUS_POWERFUL if self.is_light_enabled else DRONE_LIGHT_RADIUS

    #---------------------------
    #     Radar control
    #---------------------------
    def refresh_radar(self, radar_blips: list[RadarBlip]):
        self.radar.scan(radar_blips)

    def get_radar_blips(self, direction: str) -> list[RadarBlip]:
        return self.radar.get_blips(direction)

    def get_radar_blips_unscanned_fish(self, *directions: str) -> list[RadarBlip]:
        global scan_list
        unscanned_fish_blips = []
        for direction in directions:
            for blip in self.get_radar_blips(direction):
                if blip.fish_id not in scan_list and not fish_global_map[blip.fish_id].is_monster:
                    print_debug("%s found unscanned fish %d", self.name(), blip.fish_id)
                    unscanned_fish_blips.append(blip)
        return unscanned_fish_blips

    def get_radar_blips_monsters(self, *directions: str) -> list[RadarBlip]:
        global scan_list
        monsters_blips = []
        for direction in directions:
            for blip in self.get_radar_blips(direction):
                if blip.fish_id and fish_global_map[blip.fish_id].is_monster:
                    print_debug("%s found monster %d", self.name(), blip.fish_id)
                    monsters_blips.append(blip)
        return monsters_blips

    def get_radar_blips_unscanned_fish_count(self, *directions: str) -> int:
        return len(self.get_radar_blips_unscanned_fish(*directions))

    def should_enable_light(self):
        turns_off = loop - self.context.get("last_turn_light", 0)  #type:ignore
        zone =  Zone.get(self.pos.y)
        is_drone_rising = self.pos.y < self.target.y
        is_drone_sinking = self.pos.y == self.target.y
        is_drone_crossing = self.pos.y > self.target.y
        # - off above 3000
        # -- when sinking/crossing: every 5 turns when sinking & high / 3 turn middle / 1 turn if low
        # -- rising : every 6 turns low / 7 turns middle / 8 turns high
        low_batt = self.battery < BATTERY_CAPACITY / 30  # 10
        adjust = 1 if low_batt else 0
        if is_drone_sinking or is_drone_crossing:
            if zone == Zone.HIGH:
                return turns_off >= adjust + 5
            if zone == Zone.MID:
                return turns_off >= adjust + 3 
            if zone == Zone.LOW:
                return turns_off >= adjust + 1
        if is_drone_rising:
            if zone == Zone.HIGH:
                return turns_off >= adjust + 7
            if zone == Zone.MID:
                return turns_off >= adjust + 6
            if zone == Zone.LOW:
                return turns_off >= adjust + 5
        # eg if zone == Zone.SURFACE:
        return False

    def get_outpaceable_foes(self, foes: list["Drone"]):
        below_foe_drones = [foe for foe in foes if not foe.dead \
                                and foe.pos.y - self.pos.y > RUSH_DISTANCE_WITH_FOE]
        return below_foe_drones

    def get_monsters_above(self):
        blocking_monsters = [monster for monster in self.detect_close_monsters(999, 5) \
            if self.pos.y > monster.predicted_pos.y \
            and abs(self.pos.x - monster.predicted_pos.x) < MONSTER_MAX_DETECTION_RADIUS + MONSTER_NON_AGGRESSIVE_SPEED \
        ]
        return blocking_monsters

    
    def are_monsters_in_angle(self):
        going_up_position = find_safe_direction(
            drone_position=self.pos,
            bots_positions=[monster.predicted_pos for monster in self.detect_close_monsters()],
            target_position=(self.pos.x, DRONE_SURFACE_Y_THRESHOLD),
            turns_ahead=3,
            min_angle=-45,
            max_angle=55,
            step_angle=10)
        return going_up_position != self.pos

    def are_monsters_blocking_arise(self):
        if self.pos.y < 5000:
            return len(self.get_monsters_above()) >= 1
        else:
            return self.are_monsters_in_angle()
        

    def is_score_enough_to_rush(self):
        potential_score = Score.estimated_drone_save(self)
        return potential_score >= SAFE_SCORING

    def force_strategy_change(self, foes: list["Drone"]):
        # * if trying to outpace foe, rush to top
        # * if "rich" and > 1 monster on the side/below (??), rush to top

        # TODO: Centralize strategy changes here (ie the MID1>MID2>LOW could take the feuillemorte role)
        # (only if we keep those strategies)
        if not self.are_monsters_blocking_arise():
            outpaceable_foes = self.get_outpaceable_foes(foes)
            close_monsters = self.detect_close_monsters()
            
            if self.is_score_enough_to_rush() and len(outpaceable_foes) >= 1:
                self.role = DroneRole.RUSH_TOP
                print_debug("%s: RUSH_TOP: predicted score being %d and foes %s are outpaceable",
                    self.name(),
                    Score.estimated_drone_save(self), #type:ignore (optional)
                    outpaceable_foes)
            if self.is_score_enough_to_rush() and self:
                self.role = DroneRole.RUSH_TOP
                print_debug("%s: RUSH_TOP: predicted score being %d and monsters %s are close",
                            self.name(), 
                            Score.estimated_drone_save(self), 
                            close_monsters)

            




# END DRONE

                    
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
                if distance < drone.current_light_radius():  #? + 300 for monsters ?
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
    
    print_debug("FishGlobalMap %s", fish_global_map)


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

def print_blips(blips: list[RadarBlip]):
    printed_str = {
        "TL": [],
        "TR": [],
        "BL": [],
        "BR": [],
    }
    for blip in blips:
        printed_str[blip.dir].append(str(blip.fish_id))

    print_debug(printed_str)
    print_debug(len(printed_str["TL"]), "|", len(printed_str["TR"]))
    print_debug(7 * "-")
    print_debug(len(printed_str["BL"]), "|", len(printed_str["BR"]))


def dist(a: Vector, b: Vector):
    return int(math.dist(a, b))

def is_monster_close(drone):
    # get the list of blips reconciliated with fish_details via fish_id
    detected = len([fish for fish in visible_fish if fish.detail.type == CREATURE_TYPE_MONSTER and dist(drone.pos, fish.pos) < MONSTER_MAX_DETECTION_RADIUS])
    if detected:
        print_debug("%s detected Monster detected %s")
    return detected > 0

fish_details: Dict[int, FishDetail] = {}
fish_count = int(input())
for _ in range(fish_count):
    fish_id, color, _type = map(int, input().split())
    fish_details[fish_id] = FishDetail(color, _type)













#=====================================================================================
# Smart Evasion strategy
#=====================================================================================


# Function to move bots towards the drone's position
def move_bots(bots_positions: List[Vector], drone_position: Vector, speed: int) -> List[Vector]:  
    new_positions = []
    
    for bot_position in bots_positions:
        dx = drone_position[0] - bot_position[0]
        dy = drone_position[1] - bot_position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance <= speed:
            new_positions.append(drone_position)
        else:
            move_x = (dx / distance) * speed
            move_y = (dy / distance) * speed
            new_position = Vector(int(bot_position[0] + move_x), int(bot_position[1] + move_y))
            new_positions.append(new_position)
    
    return new_positions


# Function to check for collision
def check_collision(drone_position: Vector, bots_positions: List[Vector]) -> bool:  
    for bot_position in bots_positions:
        distance = math.sqrt((drone_position[0] - bot_position[0])**2 + (drone_position[1] - bot_position[1])**2)
        if distance <= MONSTER_INTERACTION_RADIUS:
            return True  # Collision detected
    return False  # No collision


# Helper function to move towards a direction by a certain speed
def move_towards(current_position: Vector, move: Vector) -> Vector:
    new_position = Vector(current_position[0] + move[0], current_position[1] + move[1])
    # Ensure the new position does not exceed the board size
    new_position = Vector(max(0, min(MAP_SIZE-1, new_position[0])), max(0, min(MAP_SIZE-1, new_position[1])))
    return new_position


def find_safe_direction(drone_position: Vector, bots_positions: List[Vector], target_position,
                        turns_ahead, min_angle=0, max_angle=360, step_angle=10) -> Vector:
    # turns_ahead is How many turns we are simulating
    best_direction = None
    max_score = -float('inf')  # Use a scoring system instead of just safe distance

    # Check in all directions
    for angle in range(min_angle,max_angle, step_angle):
        rad = math.radians(angle)
        drone_move = Vector(DRONE_MOVE_SPEED * math.cos(rad), DRONE_MOVE_SPEED * math.sin(rad))
        temp_drone_position = drone_position
        temp_bots_positions = bots_positions.copy()
        safe_for_all_turns = True

        # Simulate the movements for the number of turns ahead
        for turn in range(turns_ahead):
            # Simulate drone's movement
            temp_drone_position = move_towards(temp_drone_position, drone_move)
            
            # Ensure the drone's new position is within the board boundaries
            if not (0 <= temp_drone_position[0] < MAP_SIZE and 0 <= temp_drone_position[1] < MAP_SIZE):
                safe_for_all_turns = False
                break

            # Simulate bots' movements
            # FIXME : use MONSTER_AGGRESSIVE_SPEED on turn 1  if detected ; then MONSTER_NON_AGGRESSIVE_SPEED
            temp_bots_positions = move_bots(temp_bots_positions, temp_drone_position, MONSTER_AGGRESSIVE_SPEED)

            # Check for collision after bots' movements
            if check_collision(temp_drone_position, temp_bots_positions):
                safe_for_all_turns = False
                break

        # Calculate the score at the end of the simulation
        if safe_for_all_turns:
            # further from 1000, malus is 0 ; in a corner, malus is 2000:
            wall1_malus = lambda dist: 1000 - min(dist, 1000)
            wall_malus = wall1_malus(temp_drone_position[0]) + wall1_malus(temp_drone_position[1]) \
                + wall1_malus(MAP_SIZE - temp_drone_position[0]) + wall1_malus(MAP_SIZE - temp_drone_position[1])
            # Calculate the safety distance
            safety_distance = min(math.hypot(bot[0] - temp_drone_position[0], bot[1] - temp_drone_position[1]) for bot in temp_bots_positions)
            # Calculate the distance to the target
            distance_to_target = math.hypot(target_position[0] - temp_drone_position[0], target_position[1] - temp_drone_position[1])
            # We want to maximize safe distance and minimize distance to target
            score = math.log(safety_distance) - distance_to_target - wall_malus
            if score > max_score:
                best_direction = Vector(int(drone_move[0]), int(drone_move[1]))
                max_score = score
                print(f"new best angle {angle}, score {score:.0f} = safety {safety_distance:.0f}|"
                      f"{math.log(safety_distance):.0f} - distance {distance_to_target:.0f} -> direction {best_direction}")

    # If a safe direction was found, return the new position in that direction
    if best_direction is not None:
        new_drone_position = move_towards(drone_position, best_direction)
        return new_drone_position

    # If no direction is safe
    return drone_position


# TODO integrate if > 1 monster
# TODO simulate dynamic monster speed
# TODO tweak scoring, smarter "target" area


def move_drone_safely(drone_position: Vector, bots_positions: List[Vector], target_position) -> Vector:
    target_vector = Vector(target_position[0] - drone_position[0], target_position[1] - drone_position[1])  
    distance_to_target = math.sqrt(target_vector[0]**2 + target_vector[1]**2)  
    if distance_to_target < DRONE_MOVE_SPEED:
        return target_position

    # Find a safe direction to move that avoids predicted collisions with bots
    new_position = find_safe_direction(drone_position, bots_positions, target_position, turns_ahead=3)
    if new_position == drone_position:
        new_position = find_safe_direction(drone_position, bots_positions, target_position,turns_ahead=2)
        if new_position == drone_position:
            new_position = find_safe_direction(drone_position, bots_positions, target_position,turns_ahead=1)

    return new_position



















#===================================================================================================
#                                          Rush strategy
#===================================================================================================
def run_rush(drone):
    drone.target = Vector(drone.pos.x, 499)#===================================================================================================
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
    if drone.pos.x % 800 == 0:
        drone.target = Vector(drone.target.x + 1600, FAST_MAX_DEPTH if drone.target.y < 500 else 499)

Y_SURFACE = 99
#===================================================================================================
#                                          sinker strategy
#===================================================================================================
def run_sinker(y_max_depth, is_full=False):

    def init(drone):
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

    def inner(drone):
        if loop == 0:
            init(drone)

        next_target = drone.context["target_stack"][0]
        if dist(drone.pos, next_target) < 400:
            drone.context["target_stack"].pop(0)
            print_debug("%s reached target %s", drone.name(), next_target)
        if not drone.context["target_stack"]:
            drone.role = DroneRole.SINKER_MID2 if drone.role == DroneRole.SINKER_MID1 else DroneRole.SINKER_LOW
            init(drone)
        drone.target = drone.context["target_stack"][0]


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

#===================================================================================================
#                                          feuille morte strategy
# Each drone has a split of the map to scan
# Each drone will go to the bottom center of its split (x=2500, y=10000)/(x=7500, y=10000)
# Each drone will start the light every 5 rounds
# Each drone will use the radar to check if there is a fish above
# When a fish is found, the drone will go the a specific location in the direction of the fish (L or R)
# Once the fish is no longer detected, the drone will go back to the bottom center of its split
# TODO do not send left bot to fish on the far right
"""
|     o     |     o     |
|     ↓     |           |
|  L  ↓  R  |  L  ↓  R  |
|     ↓     |           |
|     ↓     |           |
|     ↓→→→→↟|           |
|___________|___________|
x=0         x=5000      x=10000
Left bot:
  - L:    x=1500 (X - 1000)
  - R:    x=3500 (X + 1000)
  - rise: x=R
Right bot:
  - L:    x=6500 (X - 1000)
  - R:    x=8500 (X + 1000)
  - rise: x=L
"""
#===================================================================================================
def run_feuille_morte_v2(directions=[RADAR_TOP_LEFT, RADAR_BOTTOM_RIGHT]):
    def init(drone: Drone):
      drone.context["side"] = SinkerSide.LEFT if drone.pos.x < 5000 else SinkerSide.RIGHT
      drone.context["state"] = SinkerState.SINKING

    def inner(drone: Drone):
        target_y = 10000 if directions[0] == RADAR_BOTTOM_LEFT else Y_SURFACE

        if loop == 0:
            init(drone)

        #===========================
        #     State check
        #===========================
        # Drone is at the bottom of the map, need to go to the middle
        if drone.pos.y >= 8000 and drone.context["state"] == SinkerState.SINKING:
            drone.context["state"] = SinkerState.CROSSING
        # Drone is at the middle of the map, need to go to the top
        elif 3750 <= drone.pos.x <= 6250 and drone.context["state"] == SinkerState.CROSSING:
            drone.context["state"] = SinkerState.RISING

        #===========================
        #     State resolution
        #===========================
        if(drone.context["state"] == SinkerState.SINKING):
            # Scan for fishes above/below
            drone.refresh_radar(my_radar_blips[drone.drone_id])
            # If there is a fish above, go to the specific location
            
            fishes_left = drone.get_radar_blips_unscanned_fish_count(directions[0])
            fishes_right = drone.get_radar_blips_unscanned_fish_count(directions[1])

            left_new_target = max(X_LEFT_MARGIN, drone.pos.x - 1000)
            right_new_target = min(X_RIGHT_MARGIN, drone.pos.x + 1000)

            # If both sides have fishes, go to the side of the drone
            if fishes_left and fishes_right:
                if drone.context["side"] == SinkerSide.LEFT or drone.get_radar_blips_monsters(directions[1]):
                    drone.target = Vector(left_new_target, target_y)
                else:
                    drone.target = Vector(right_new_target, target_y)
            # If only left
            elif fishes_left:
                drone.target = Vector(left_new_target, target_y)
            # If only right
            elif fishes_right:
                drone.target = Vector(right_new_target, target_y)
            # If nothing detected, go to the middle
            else:
              drone.target = Vector(2500 if drone.context["side"] == SinkerSide.LEFT else 7500, target_y)
            # if drone.get_radar_blips_unscanned_fish_count(directions[0]):  #? Can be improved by giving a drone a preference on a side to go first
            #   print_debug("%s found fish above/below left", drone.drone_id)
            #   drone.target = Vector(1500 if drone.context["side"] == SinkerSide.LEFT else 6500, 10000)
            # elif drone.get_radar_blips_unscanned_fish_count(directions[1]):
            #   print_debug("%s found fish above/below right", drone.drone_id)
            #   drone.target = Vector(3500 if drone.context["side"] == SinkerSide.LEFT else 8500, 10000)
            # else:
              # Nothing detected, go to the middle
            #   drone.target = Vector(2500 if drone.context["side"] == SinkerSide.LEFT else 7500, 10000)
        elif(drone.context["state"] == SinkerState.CROSSING):
            drone.target = Vector(3500 if drone.context["side"] == SinkerSide.LEFT else 6500, 7000)
        elif(drone.context["state"] == SinkerState.RISING):
            drone.target = Vector(3500 if drone.context["side"] == SinkerSide.LEFT else 6500, 0)
    return inner


def run_feuille_morte():
    def init(drone: Drone):
      drone.context["side"] = SinkerSide.LEFT if drone.pos.x < 5000 else SinkerSide.RIGHT
      drone.context["state"] = SinkerState.SINKING

    def inner(drone: Drone):
        if loop == 0:
            init(drone)

        #===========================
        #     State check
        #===========================
        # Drone is at the bottom of the map, need to go to the middle
        if drone.pos.y >= 8000 and drone.context["state"] == SinkerState.SINKING:
            drone.context["state"] = SinkerState.CROSSING
        # Drone is at the middle of the map, need to go to the top
        elif 3750 <= drone.pos.x <= 6250 and drone.context["state"] == SinkerState.CROSSING:
            drone.context["state"] = SinkerState.RISING

        #===========================
        #     State resolution
        #===========================
        if(drone.context["state"] == SinkerState.SINKING):
            # Scan for fishes above
            drone.refresh_radar(my_radar_blips[drone.drone_id])
            # If there is a fish above, go to the specific location
            if drone.get_radar_blips_unscanned_fish_count(RADAR_TOP_LEFT):  #? Can be improved by giving a drone a preference on a side to go first
              print_debug("%s found fish above left", drone.drone_id)
              drone.target = Vector(1500 if drone.context["side"] == SinkerSide.LEFT else 6500, 10000)
            elif drone.get_radar_blips_unscanned_fish_count(RADAR_TOP_RIGHT):
              print_debug("%s found fish above right", drone.drone_id)
              drone.target = Vector(3500 if drone.context["side"] == SinkerSide.LEFT else 8500, 10000)
            else:
              # Nothing detected, go to the middle
              drone.target = Vector(2500 if drone.context["side"] == SinkerSide.LEFT else 7500, 10000)
        elif(drone.context["state"] == SinkerState.CROSSING):
            drone.target = Vector(3500 if drone.context["side"] == SinkerSide.LEFT else 6500, 7000)
        elif(drone.context["state"] == SinkerState.RISING):
            drone.target = Vector(3500 if drone.context["side"] == SinkerSide.LEFT else 6500, 0)
    return inner

strategies = {
    DroneRole.FAST: run_fast,
    DroneRole.SINKER_LOW: run_sinker(8000),
    DroneRole.SINKER_MID1: run_sinker(3750, is_full=True),
    DroneRole.SINKER_MID2: run_sinker(6250),
    DroneRole.CHASER: run_chase,
    DroneRole.FEUILLE_MORTE: run_feuille_morte,
    DroneRole.RUSH_TOP: run_rush,
}




class Score:
    global_estimated_ally_score: int = 0
    global_estimated_enemy_score: int = 0

    drone_score_details: Dict[int, dict] = {}

    @staticmethod
    def update_global_scores(my_score, foe_score):
        Score.global_ally_score = my_score
        Score.global_enemy_score = foe_score

    @staticmethod
    def update_estimated_global_scores():
        global my_drones, foe_drones
        Score.global_estimated_ally_score = Score.estimated_drones_score(my_drones)
        Score.global_estimated_enemy_score = Score.estimated_drones_score(foe_drones)

    @staticmethod
    def estimated_drones_score(drones: List[Drone]):
        return sum([Score.estimated_drone_save(drone) for drone in drones])

    # Fishes score :
    # - type 0 : 1 point
    # - type 1 : 2 points
    # - type 2 : 3 points
    # - 3 fishes of same color : 3 points
    # - 3 fishes of same type : 4 points
    # - double the point if first to save
    @staticmethod
    def estimated_drone_save(drone: Drone) -> int:
        score = 0
        fish_types = {
            0: [],
            1: [],
            2: [],
        }
        fish_colors = {
            0: [],
            1: [],
            2: [],
            3: [],
        }

        for scan_id in drone.scans:
            fish: FishDetail = fish_details[scan_id]
            score += fish.type + 1
            fish_types[fish.type] += fish
            fish_colors[fish.color] += fish

        for f_type in fish_types.values():
            if len(f_type) == 3:
                score += 4
        for f_color in fish_colors.values():
            if len(f_color) == 3:
                score += 3

        # save values in the drone_score_details
        Score.drone_score_details[drone.drone_id] = {
            "fish_types": fish_types,
            "fish_colors": fish_colors,
        }

        return score

    @staticmethod
    def estimated_score_with_bonus(drones: list[Drone], other_drones: list[Drone]):
        score = 0
        fish_types = {
            0: [],
            1: [],
            2: [],
        }
        fish_colors = {
            0: [],
            1: [],
            2: [],
            3: [],
        }

        for drone in drones:
            score += Score.estimated_drone_save(drone)
        # update the score of the other drones
        for drone in other_drones:
            Score.estimated_drone_save(drone)

        drone_ids = [drone.drone_id for drone in drones]
        for id in drone_ids:
            for x in range(3):
                fish_types[x] += Score.drone_score_details[id]["fish_types"][x]
                score += len(fish_types[x]) * (x + 1)
            for x in range(4):
                fish_colors[x] += Score.drone_score_details[id]["fish_colors"][x]

        #================================================
        #                Score without bonus
        #================================================
        other_drone_ids = [drone.drone_id for drone in other_drones]
        for id in other_drone_ids:
            for x in range(3):
                other_fish_types = Score.drone_score_details[id]["fish_types"][x]
                for fish in other_fish_types:
                    if fish not in fish_types[x]:
                        score += x + 1  # bonus for being the first to save
                fish_types[x] += Score.drone_score_details[id]["fish_types"][x]
            for x in range(4):
                fish_colors[x] += Score.drone_score_details[id]["fish_colors"][x]
                for fish in Score.drone_score_details[id]["fish_colors"][x]:
                    if fish in fish_colors[x]:
                        # fish_colors[x].remove(fish)
                        pass

        for f_type in fish_types.values():
            if len(f_type) == 3:
                score += 4
        for f_color in fish_colors.values():
            if len(f_color) == 3:
                score += 3

        #================================================
        #                Score only with bonus
        #================================================
        for id in other_drone_ids:
            for x in range(3):
                other_fish_types = Score.drone_score_details[id]["fish_types"][x]
                for fish in other_fish_types:
                    if fish in fish_types[x]:
                        fish_types[x].remove(fish)
                fish_types[x] += Score.drone_score_details[id]["fish_types"][x]
            for x in range(4):
                fish_colors[x] += Score.drone_score_details[id]["fish_colors"][x]
                for fish in Score.drone_score_details[id]["fish_colors"][x]:
                    if fish in fish_colors[x]:
                        fish_colors[x].remove(fish)

        for f_type in fish_types.values():
            if len(f_type) == 3:
                score += 4
        for f_color in fish_colors.values():
            if len(f_color) == 3:
                score += 3

        return score

# TODO TODO light 
# monster overrides this: force turn off

class Zone(Enum):
    SURFACE = 4  # 0   -3000
    HIGH = 3     # 3000-5000
    MID = 2      # 5000-7000
    LOW = 1      # 7000-10000

    @classmethod
    def get(cls, y):
        if y < 3000:
            return Zone.SURFACE
        elif y < 5000:
            return Zone.HIGH
        elif y < 7000:
            return Zone.MID
        else:
            return Zone.LOW



#===================================================================================================
#===================================================================================================
#===================================================================================================
#===================================================================================================

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

    # Retrieve the list of all scans done by all drones and scored ones
    def update_scan_status(drones: list[Drone], my_scans: list[int]):
        scan_list = []
        for drone in drones:
            for scan in drone.scans:
                if scan not in scan_list:
                    scan_list.append(scan)
        for scan in my_scans:
            if scan not in scan_list:
                scan_list.append(scan)
        return scan_list

    # print_debug("my_radar_blips %s", my_radar_blips)
    # call once
    update_positions(my_drones, visible_fish)
    scan_list = update_scan_status(my_drones, my_scans)

    for drone in my_drones:
        if loop == 0:
            drone.role = DroneRole.SINKER_MID1 if drone.drone_id in FAST_COMPATIBLE_POSITIONS else DroneRole.SINKER_LOW

        #===========================
        #     Init each loop
        #===========================
        print_debug("Start %s", drone)
        # Turn on lights every 5 loops by default
        # drone.is_light_enabled = drone.pos.y > MINIMUM_LIGHT_DEPTH_THRESHOLD and loop % 5 == 0

        #===========================
        #     Loop strategy
        #===========================
        strategies[drone.role](drone)

        drone.is_light_enabled = drone.should_enable_light()

        drone.force_strategy_change(foes=foe_drones)

        # Detect any monsters
        # In case a monster is detected, evade it !
        drone.evasion_orchestrator()


        print(drone.get_order_move())

    loop = loop + 1
