# # 
# Win more points than your opponent by scanning the most fish.

# To protect marine life, it is crucial to understand it. Explore the ocean floor using your drone to scan as many fish as possible to better understand them!
#  Rules

# The game is played turn by turn. Each turn, each player gives an action for their drone to perform.
# The Map

# The map is a square of 10,000 units on each side. Length units will be denoted as "u" in the rest of the statement. The coordinate (0, 0) is located at the top left corner of the map.
# Drones

# Each player has a drone to explore the ocean floor and scan the fish. Each turn, the player can decide to move their drone in a direction or not activate its motors.


# Your drone continuously emits light around it. If a fish is within this light radius, it is automatically scanned. You can increase the power of your light (and thus your scan radius), but this will drain your battery.

# In order to save your scans and score points, you will need to resurface with your drone.
# Fish

# On the map, different fish are present. Each fish has a specific type and color. In addition to the points earned if you scan a fish and bring the scan back to the surface, bonuses will be awarded if you scan all the fish of the same type or same color, or if you are the first to do so.

# Each fish moves within a habitat zone, depending on its type. Only fish within the light radius of your drone will be visible to you.
# Unit Details
# Drones

# Drones move towards the given point, with a maximum distance per turn of 600u. If the motors are not activated in a turn, the drone will sink by 300u.

# At the end of the turn, fish within a radius of 800u will be automatically scanned.

# If you have increased the power of your light, this radius becomes 2000u, but the battery drains by 5 points. If the powerful light is not activated, the battery recharges by 1. The battery has a capacity of 30 and is fully charged at the beginning of the game.

# If the drone is near the surface (y ≤ 500u), the scans will be automatically saved, and points will be awarded.
# Radar

# To better navigate the dark depths, drones are equipped with radars. For each creature (fish or monster) in the game zone, the radar will indicate:

#     TL: if the entity is somewhere top left of the drone.
#     TR: if the entity is somewhere top right of the drone.
#     BR: if the entity is somewhere bottom right of the drone.
#     BL: if the entity is somewhere bottom left of the drone.

# Note: If the entity shares the same x-coordinate as the drone, it will be considered as being on the left. If the entity shares the same y-coordinate as the drone, it will be considered as being on the top.
# Fish

# Fish move 200u each turn, in a randomly chosen direction at the beginning of the game. Each fish moves within a habitat zone based on its type. If it reaches the edge of its habitat zone, it will rebound off the edge.


from typing import List, NamedTuple, Dict

# Define the data structures as namedtuples
#===========================================================================
#                            Classes
#===========================================================================
class Vector(NamedTuple):
    x: int
    y: int

class FishDetail(NamedTuple):
    color: int
    type: int

class Fish(NamedTuple):
    fish_id: int
    pos: Vector
    speed: Vector
    detail: FishDetail

class RadarBlip(NamedTuple):
    fish_id: int
    dir: str

class Drone(NamedTuple):
    drone_id: int
    pos: Vector
    dead: bool
    battery: int
    scans: List[int]

# enum dronesinkerstate
class DroneSinkerState:
    SINKING = 1
    CROSSING = 2
    RISING = 3

drone_sinker_clockwise = DroneSinkerState.SINKING
drone_sinker_waiting = True

drone_sinker_target = Vector(0, 0)
drone_fast_target = Vector(0, 0)
drone_sinker = 1
drone_fast = 0

#===========================================================================
#                            Functions
#===========================================================================
def order_move(target: Vector, light: int):
    print(f"MOVE {target.x} {target.y} {light}")

def order_wait(light: int):
    print(f"WAIT {light}")


fish_details: Dict[int, FishDetail] = {}

fish_count = int(input())
for _ in range(fish_count):
    fish_id, color, _type = map(int, input().split())
    fish_details[fish_id] = FishDetail(color, _type)


loop = 0
# game loop
while True:
    loop = loop + 1
    my_scans: List[int] = []
    foe_scans: List[int] = []
    drone_by_id: Dict[int, Drone] = {}
    my_drones: List[Drone] = []
    foe_drones: List[Drone] = []
    visible_fish: List[Fish] = []
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
        visible_fish.append(Fish(fish_id, pos, speed, fish_details[fish_id]))

    my_radar_blip_count = int(input())
    for _ in range(my_radar_blip_count):
        drone_id, fish_id, dir = input().split()
        drone_id = int(drone_id)
        fish_id = int(fish_id)
        my_radar_blips[drone_id].append(RadarBlip(fish_id, dir))

    for drone in my_drones:
        x = drone.pos.x
        y = drone.pos.y
        is_light_enabled = 1 if loop % 3 == 0 else 0
        fast_depth = 3000
        # TODO: Implement logic on where to move here

        # Drone 0 should go to the middle of the map
        if drone.drone_id == drone_fast:
            if x % 800 == 0:
                drone_fast_target = Vector(drone_fast_target.x + 1600, fast_depth if drone_fast_target.y < 500 else 499)
            order_move(drone_fast_target, is_light_enabled)

        # Drone 1 should go to the bottom and racler le fond
        else:
            if loop == 0:
                drone_sinker_clockwise = drone.pos.x > 5000
            is_light_enabled = y >= 8000

            if y == 8000 and drone_sinker_state == DroneSinkerState.SINKING:
                drone_sinker_state = DroneSinkerState.CROSSING
            elif y == 8000 and drone_sinker_state == DroneSinkerState.CROSSING and (drone.pos.x in (2000, 8000)):
                drone_sinker_state == DroneSinkerState.RISING

            if(drone_sinker_state == DroneSinkerState.SINKING):
                drone_sinker_target = Vector(8000 if drone_sinker_clockwise else 2000, 8000)
            elif(drone_sinker_state == DroneSinkerState.CROSSING):
                drone_sinker_target = Vector(2000 if drone_sinker_clockwise else 8000, 8000)
            elif(drone_sinker_state == DroneSinkerState.RISING):
                drone_sinker_target = Vector(drone.pos.x, 500)
            order_move(drone_sinker_target, is_light_enabled)

        # if x > 8000 and target_x == 10000:
        #     target_x = 0
        # if x < 1000 and target_x == 0:
        #     target_y = 0
        # if x == 0 and y == 0 and target_y == 0:
        #     target_x = 10000
        #     target_y = 10000
