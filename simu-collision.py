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


import math
from typing import Tuple, List  
  
# Define a type alias for clarity  
Position = Tuple[int, int]  

# Define the game parameters
BOARD_SIZE = 10000
DRONE_DIAMETER = 250
BOT_DIAMETER = 250
DRONE_SPEED = 600
BOT_SPEED = 500
TARGET_POSITION = (10000, 10000)

GRID_SIZE = 200  # printing only

# Initialize positions
drone_position: Tuple[int, int] = (0, 0)
bots_positions = [(500, 500), (9500, 500), (500, 9500), (9500, 9500), (5000, 5000)]  # Example positions for bots

# Function to move the drone towards a target position
def move_drone(current_position: Position, target_position: Position, speed: int) -> Position:  
    dx = target_position[0] - current_position[0]
    dy = target_position[1] - current_position[1]
    distance = math.sqrt(dx**2 + dy**2)
    
    if distance <= speed:
        return target_position
    
    move_x = (dx / distance) * speed
    move_y = (dy / distance) * speed
    new_position = (int(current_position[0] + move_x), int(current_position[1] + move_y))
    
    return new_position

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
def check_collision(drone_position: Position, bots_positions: List[Position], drone_diameter: int, bot_diameter: int) -> bool:  
    drone_radius = drone_diameter / 2
    bot_radius = bot_diameter / 2
    
    for bot_position in bots_positions:
        distance = math.sqrt((drone_position[0] - bot_position[0])**2 + (drone_position[1] - bot_position[1])**2)
        if distance <= (drone_radius + bot_radius):
            return True  # Collision detected
    return False  # No collision



# Function to print the game board  
def print_board(drone_position: Position, bots_positions: List[Position]) -> None:  
    board = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  
      
    # Place the drone on the board  
    drone_x, drone_y = drone_position  
    drone_x //= 50  
    drone_y //= 50  
    board[drone_y][drone_x] = 'O'  
      
    # Place the bots on the board  
    for bot_pos in bots_positions:  
        bot_x, bot_y = bot_pos  
        bot_x //= 50  
        bot_y //= 50  
        if board[bot_y][bot_x] == 'O':  # If the drone is already there, mark overlap with '$'  
            board[bot_y][bot_x] = '$'  
        else:  
            board[bot_y][bot_x] = 'X'  
      
    # Print the board  
    for row in board:  
        print(''.join(row))  


    

loop = 0

# Main game loop  
while True:  
    loop +=1

    # Move the drone towards the target position  
    drone_position = move_drone(drone_position, TARGET_POSITION, DRONE_SPEED)  
      
    # Move the bots towards the drone's current position  
    bots_positions = move_bots(bots_positions, drone_position, BOT_SPEED)  
      
     # For visualization purposes, you may want to include a print statement or graphics to show positions
    print(f"{loop}: Drone: {drone_position}; Bots: {bots_positions}")

    # Check for collision  
    if check_collision(drone_position, bots_positions, DRONE_DIAMETER, BOT_DIAMETER):  
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
