# prompts history

#1
# This is a game with a square board of 10000 by 10000 pixels.
# On it there is my drone and 5 enemy bots, all represented by circles 250 pixels in diameter.  

# my drone move 600 pixels per turn in the direction of a target I set. The enemy bots move at 500 pixels per turn.
# They move toward my current position.   

# my drone starts at (0,0) and needs to reach (9999, 9999).  
# first write the python code simulating this game. explain your reasoning.

#2
# Add code to print an overview of the game board into ascii art at every turn:
# the board is summarized into a 200 by 200 grid of characters, one character for each square of 50 by 50 pixels.
# this character is an "O" if my drone overlaps this square, an "X" if an enemy bot overlaps the square, a "$" if both overlap.

#3
# rewrite all function signatures adding the type hints. no need to rewrite the body

#4
# now explain how my drone could avoid the bots moving towards it

#5
# avoid collision using some combination of pathfinding like a* and including the future positions of the enemy bots
# (as they move toward the future drone positions) with predictive evasion or Velocity Obstacle.
# first decompose the problem, then Update the `move_drone` function to do this. 
#6
# update your approach to plan 3 turns in advance, and include the fact that the drone cannot 
# move out of the 10000 by 10000 board so it should avoid cornering itself.
# also it should save itself even if has to move away from the target to do so.
#7
# your code is wrong. at each turn the drone position and the bot position change.
# rewrite predict_bots_movement so that bots move towards updated drone positions as drone moves in the chosen angle

#8 (restarting with only full code so far)
# the function `find_safe_direction` is overly complicated and buggy, find out why and improve it

#9
# this is still wrong.  
# find_safe_direction should simulate the 3 turns in a similar way like the main loop :  
# ```  
#     drone_position = ... # move drone towards angle  
#     bots_positions = move_bots(bots_positions, previous_drone_position, BOT_SPEED)    
# ```  

#10 - back from code again
# currently `find_safe_direction` is too safe, so the bot never reaches target.
# when the enemy bots are out of the way, drone should move toward the target. modify the code.  

#11
# no, check_collision_on_path is not the right modification. pay attention to the original find_safe_direction 
# especially how we set `best_direction`.
# it should not be the furthest away from the bots, just safe enough and the closest to target

#12
# there is an error in the math code so that the bot never ends up at the target, can you find it?



## ============ MINIMAL context starts here

# This is a game with a square board of 10000 by 10000 pixels.
# On it there is my drone and 5 enemy bots, all represented by circles 250 pixels in diameter.  

# my drone move 600 pixels per turn in the direction of a target I set. The enemy bots move at 500 pixels per turn.
# They move toward my current position.   

# my drone starts at (0,0) and needs to reach (10000, 10000).  
# code: ```


import math
import random
from typing import NamedTuple, Tuple, List  
  
# Define a type alias for clarity  
# Vector = Tuple[float, float]  
class Vector(NamedTuple):
    x: float
    y: float

# Define the game parameters
MAP_SIZE = 10000

MONSTER_INTERACTION_RADIUS = 500  # to match previous sim
DRONE_MOVE_SPEED = 600
# MONSTER_AGGRESSIVE_SPEED = 500
# MONSTER_NON_AGGRESSIVE_SPEED = 270
MONSTER_AGGRESSIVE_SPEED = 400

GRID_SIZE = 50  # printing only
GRID_CHAR_WIDTH = 200

global drone_position, bots_positions

log = print







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


def predict_bots_movement(bots_positions: List[Vector], drone_position: Vector, turns_ahead: int, drone_move: Vector) -> List[List[Vector]]:
    predicted_positions = []
    for turn in range(turns_ahead):
        # Move the drone to a new predicted position
        drone_position = Vector(drone_position[0] + drone_move[0], drone_position[1] + drone_move[1])
        # Move bots towards the latest drone position
        bots_positions = move_bots(bots_positions, drone_position, MONSTER_AGGRESSIVE_SPEED)
        # Store the predicted bots' positions for this turn
        predicted_positions.append(bots_positions)
    return predicted_positions


# Helper function to move towards a direction by a certain speed
def move_towards(current_position: Vector, move: Vector) -> Vector:
    new_position = Vector(current_position[0] + move[0], current_position[1] + move[1])
    # Ensure the new position does not exceed the board size
    new_position = Vector(max(0, min(MAP_SIZE-1, new_position[0])), max(0, min(MAP_SIZE-1, new_position[1])))
    return new_position


def find_safe_direction(drone_position: Vector, bots_positions: List[Vector], target_position, turns_ahead) -> Vector:
    # turns_ahead is How many turns we are simulating
    best_direction = None
    max_score = -float('inf')  # Use a scoring system instead of just safe distance

    # Check in all directions
    for angle in range(0, 360, 10):  # Increment by 10 degrees for efficiency, can be adjusted
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
                log(f"new best angle {angle}, score {score:.0f} = safety {safety_distance:.0f}|"
                      f"{math.log(safety_distance):.0f} - distance {distance_to_target:.0f} -> direction {best_direction}")

    # If a safe direction was found, return the new position in that direction
    if best_direction is not None:
        new_drone_position = move_towards(drone_position, best_direction)
        return new_drone_position

    # If no direction is safe
    return drone_position




def move_drone_safely(drone_position: Vector, bots_positions: List[Vector], target_position) -> Vector:
    target_vector = Vector(target_position[0] - drone_position[0], target_position[1] - drone_position[1])  
    distance_to_target = math.sqrt(target_vector[0]**2 + target_vector[1]**2)  
    if distance_to_target < DRONE_MOVE_SPEED:
        return target_position

    # Find a safe direction to move that avoids predicted collisions with bots
    new_position = find_safe_direction(drone_position, bots_positions, target_position, turns_ahead=3)
    if new_position == drone_position:
        log("no safe direction found! trying with 2 turns")
        new_position = find_safe_direction(drone_position, bots_positions, target_position,turns_ahead=2)
        if new_position == drone_position:
            log("no safe direction found! trying with 1 turn")
            new_position = find_safe_direction(drone_position, bots_positions, target_position,turns_ahead=1)

    return new_position












# Function to print the game board  
def print_board(drone_position: Vector, bots_positions: List[Vector]) -> None:  
    board = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  
      
    # Place the drone on the board  
    drone_x, drone_y = drone_position  
    drone_x, drone_y = int(drone_x), int(drone_y)
    drone_x //= GRID_CHAR_WIDTH  
    drone_y //= GRID_CHAR_WIDTH  
    board[drone_y][drone_x] = 'D'  
    skull = '\u2620'
      
    # Place the bots on the board  
    for bot_pos in bots_positions:  
        bot_x, bot_y = bot_pos  
        bot_x, bot_y = int(bot_x), int(bot_y)
        bot_x //= GRID_CHAR_WIDTH  
        bot_y //= GRID_CHAR_WIDTH  
        if board[bot_y][bot_x] in ('D', skull):  # If the drone is already there, mark overlap with '$'  
            board[bot_y][bot_x] = skull
        elif '0' < board[bot_y][bot_x] < '9':  # If the drone is already there, mark overlap with '$'  
            char = board[bot_y][bot_x]
            board[bot_y][bot_x] = chr(ord(char) + 1)
        else:  
            board[bot_y][bot_x] = '1'  
      
    # Print the board  
    log('_' * (GRID_SIZE + 2))
    for row in board:  
        log('|' + ''.join(row) + '|')
    log('_' * (GRID_SIZE + 2))



def main_loop():
    # Initialize positions
    drone_position: Vector = Vector(0, 0)
    bots_positions = [Vector(*t) for t in [(1300, 500), (1500, 500), (3000, 500), (4000, 2000), (9500, 500), (500, 9500), (9500, 9500), (5000, 5000)]]

    # add random bots
    for _ in range(5): 
        bot = Vector(0, 0)
        while bot[0]**2 + bot[1]**2 < 2000**2:
            bot = Vector(random.randint(0, MAP_SIZE-1), random.randint(0, MAP_SIZE-1))
        bots_positions.append(bot)

    loop = 0
    log(f"{loop}: Drone: {drone_position}; Bots: {bots_positions}")
    print_board(drone_position, bots_positions)  

    # Main game loop  
    while True:  
        loop +=1
        the_target_position = Vector(9999, 9999)

        previous_drone_position = drone_position

        # Move the drone towards the target position  
        drone_position = move_drone_safely(drone_position, bots_positions, the_target_position)
        drone_position = Vector(int(drone_position[0]), int(drone_position[1]))
        
        # Move the bots towards the drone's current position  
        bots_positions = move_bots(bots_positions, previous_drone_position, MONSTER_AGGRESSIVE_SPEED)  
        
        # For visualization purposes, you may want to include a print statement or graphics to show positions
        log(f"{loop}: Drone: {drone_position}; Bots: {bots_positions}")

        # Check for collision  
        if check_collision(drone_position, bots_positions):  
            print_board(drone_position, bots_positions)  
            log("Game Over: The drone has been caught by an enemy bot.")  
            return 0
        
        # Check if the drone has reached the target position  
        if drone_position == the_target_position:  
            print_board(drone_position, bots_positions)  
            log("Victory: The drone has successfully reached the target position!")  
            return 1
    
        # Print the board at each turn  
        print_board(drone_position, bots_positions)  

        if loop == 100:
            log("Game Over: The drone has run out of turns.")
            return 0


def make_stats(nruns=100):
    global log
    log = lambda *args, **kwargs: None

    succ = 0
    for _ in range(nruns):
        succ += main_loop()

    print(succ * 100 / nruns, '% of success')


main_loop()
# make_stats(600)
