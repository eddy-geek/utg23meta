# prompts history

#1
# This is a game with a square board of 10000 by 10000 pixels.
# On it there is my drone and 5 enemy bots, all represented by circles 250 pixels in diameter.  

# my drone move 600 pixels per turn in the direction of a target I set. The enemy bots move at 500 pixels per turn.
# They move toward my current position.   

# my drone starts at (0,0) and needs to reach (10000, 10000).  
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



## ============ MINIMAL context starts here

# This is a game with a square board of 10000 by 10000 pixels.
# On it there is my drone and 5 enemy bots, all represented by circles 250 pixels in diameter.  

# my drone move 600 pixels per turn in the direction of a target I set. The enemy bots move at 500 pixels per turn.
# They move toward my current position.   

# my drone starts at (0,0) and needs to reach (10000, 10000).  
# code: ```


import math
from typing import Tuple, List  
  
# Define a type alias for clarity  
Position = Tuple[float, float]  

# Define the game parameters
BOARD_SIZE = 10000
DRONE_DIAMETER = 250
BOT_DIAMETER = 250
DRONE_SPEED = 600
BOT_SPEED = 500
TARGET_POSITION = (10000, 10000)

GRID_SIZE = 50  # printing only
GRID_CHAR_WIDTH = 200

# Initialize positions
drone_position: Position = (0, 0)
bots_positions = [(1300, 500), (1500, 500), (3000, 500), (4000, 2000), (9500, 500), (500, 9500), (9500, 9500), (5000, 5000)]  # Example positions for bots

# Function to move the drone towards a target position
# def move_drone(current_position: Position, target_position: Position, speed: int) -> Position:  
#     dx = target_position[0] - current_position[0]
#     dy = target_position[1] - current_position[1]
#     distance = math.sqrt(dx**2 + dy**2)
#     if distance <= speed:
#         return target_position
#     move_x = (dx / distance) * speed
#     move_y = (dy / distance) * speed
#     new_position = (int(current_position[0] + move_x), int(current_position[1] + move_y))
#     return new_position

# Function to move bots towards the drone's position
def move_bots(bots_positions: List[Position], drone_position: Position, speed: int) -> List[Position]:  
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
            new_position = (int(bot_position[0] + move_x), int(bot_position[1] + move_y))
            new_positions.append(new_position)
    
    return new_positions




# Function to check for collision
def check_collision(drone_position: Position, bots_positions: List[Position]) -> bool:  
    drone_radius = DRONE_DIAMETER / 2
    bot_radius = BOT_DIAMETER / 2
    
    for bot_position in bots_positions:
        distance = math.sqrt((drone_position[0] - bot_position[0])**2 + (drone_position[1] - bot_position[1])**2)
        if distance <= (drone_radius + bot_radius):
            return True  # Collision detected
    return False  # No collision


def predict_bots_movement(bots_positions: List[Position], drone_position: Position, turns_ahead: int, drone_move: Position) -> List[List[Position]]:
    predicted_positions = []
    for turn in range(turns_ahead):
        # Move the drone to a new predicted position
        drone_position = (drone_position[0] + drone_move[0], drone_position[1] + drone_move[1])
        # Move bots towards the latest drone position
        bots_positions = move_bots(bots_positions, drone_position, BOT_SPEED)
        # Store the predicted bots' positions for this turn
        predicted_positions.append(bots_positions)
    return predicted_positions


# Helper function to move towards a direction by a certain speed
def move_towards(current_position: Position, move: Position) -> Position:
    new_position = (current_position[0] + move[0], current_position[1] + move[1])
    # Ensure the new position does not exceed the board size
    new_position = (max(0, min(BOARD_SIZE-1, new_position[0])), max(0, min(BOARD_SIZE-1, new_position[1])))
    return new_position


def find_safe_direction(drone_position: Position, bots_positions: List[Position]) -> Position:
    best_direction = None
    max_safe_distance = -1
    turns_ahead = 3  # How many turns ahead we are checking

    # Check in all directions
    for angle in range(0, 360, 10):  # Increment by 10 degrees for efficiency, can be adjusted
        rad = math.radians(angle)
        drone_move = (DRONE_SPEED * math.cos(rad), DRONE_SPEED * math.sin(rad))
        temp_drone_position = drone_position
        temp_bots_positions = bots_positions.copy()
        safe_for_all_turns = True

        # Simulate the movements for the number of turns ahead
        for turn in range(turns_ahead):
            # Simulate drone's movement
            temp_drone_position = move_towards(temp_drone_position, drone_move)
            
            # Ensure the drone's new position is within the board boundaries
            if not (0 <= temp_drone_position[0] < BOARD_SIZE and 0 <= temp_drone_position[1] < BOARD_SIZE):
                safe_for_all_turns = False
                break

            # Simulate bots' movements
            temp_bots_positions = move_bots(temp_bots_positions, temp_drone_position, BOT_SPEED)

            # Check for collision after bots' movements
            if check_collision(temp_drone_position, temp_bots_positions):
                safe_for_all_turns = False
                break

        # Calculate the safety distance at the end of the simulation
        if safe_for_all_turns:
            min_safe_distance = min(math.hypot(bot[0] - temp_drone_position[0], bot[1] - temp_drone_position[1]) for bot in temp_bots_positions)
            if min_safe_distance > max_safe_distance:
                best_direction = drone_move
                max_safe_distance = min_safe_distance

    # If a safe direction was found, return the new position in that direction
    if best_direction is not None:
        new_drone_position = move_towards(drone_position, best_direction)
        return new_drone_position

    return drone_position




def move_drone(drone_position: Position, bots_positions: List[Position]) -> Position:
    # Find a safe direction to move that avoids predicted collisions with bots
    new_position = find_safe_direction(drone_position, bots_positions)
    
    return new_position


# Function to print the game board  
def print_board(drone_position: Position, bots_positions: List[Position]) -> None:  
    board = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  
      
    # Place the drone on the board  
    drone_x, drone_y = drone_position  
    drone_x, drone_y = int(drone_x), int(drone_y)
    drone_x //= GRID_CHAR_WIDTH  
    drone_y //= GRID_CHAR_WIDTH  
    board[drone_y][drone_x] = 'O'  
      
    # Place the bots on the board  
    for bot_pos in bots_positions:  
        bot_x, bot_y = bot_pos  
        bot_x, bot_y = int(bot_x), int(bot_y)
        bot_x //= GRID_CHAR_WIDTH  
        bot_y //= GRID_CHAR_WIDTH  
        if board[bot_y][bot_x] == 'O':  # If the drone is already there, mark overlap with '$'  
            board[bot_y][bot_x] = '$'  
        elif '0' < board[bot_y][bot_x] < '9':  # If the drone is already there, mark overlap with '$'  
            char = board[bot_y][bot_x]
            board[bot_y][bot_x] = chr(ord(char) + 1)
        else:  
            board[bot_y][bot_x] = '1'  
      
    # Print the board  
    print('_' * (GRID_SIZE + 2))
    for row in board:  
        print('|' + ''.join(row) + '|')
    print('_' * (GRID_SIZE + 2))

loop = 0
print(f"{loop}: Drone: {drone_position}; Bots: {bots_positions}")
print_board(drone_position, bots_positions)  

# Main game loop  
while True:  
    loop +=1

    previous_drone_position = drone_position

    # Move the drone towards the target position  
    drone_position = move_drone(drone_position, bots_positions)
    drone_position = (int(drone_position[0]), int(drone_position[1]))
      
    # Move the bots towards the drone's current position  
    bots_positions = move_bots(bots_positions, previous_drone_position, BOT_SPEED)  
      
     # For visualization purposes, you may want to include a print statement or graphics to show positions
    print(f"{loop}: Drone: {drone_position}; Bots: {bots_positions}")

    # Check for collision  
    if check_collision(drone_position, bots_positions):  
        print_board(drone_position, bots_positions)  
        print("Game Over: The drone has been caught by an enemy bot.")  
        break  
      
    # Check if the drone has reached the target position  
    if drone_position == TARGET_POSITION:  
        print_board(drone_position, bots_positions)  
        print("Victory: The drone has successfully reached the target position!")  
        break  
  
    # Print the board at each turn  
    print_board(drone_position, bots_positions)  

    if loop == 100:
        print("Game Over: The drone has run out of turns.")
        break
