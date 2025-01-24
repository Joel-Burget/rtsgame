import math
import pygame
import sys
from heapq import heappush, heappop

#init pygame
pygame.init()

#window variables
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1200
FPS = 240
TITLE = "TDB RTS GAME"

#color variables
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (0, 0, 255, 128)
BLUE = (0, 0, 255)
RED = (255,0,0)

#debugging tools 
DEBUG = False
FONT = pygame.font.Font(None, 50)

#init screen
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)

#FPS clock
clock = pygame.time.Clock()
#delta time
dt = 0

#Grid Settings
TILE_WIDTH = 40
TILE_HEIGHT = 40
GRID_ROWS = SCREEN_HEIGHT // TILE_HEIGHT
GRID_COLS = SCREEN_WIDTH // TILE_WIDTH

#init variables
UNIT_POSITION = (1, 1)

#obstacle settings 
obstacles = [
    (5, 5), (6, 5), (7, 5),  # Vertical wall
    (10, 10), (10, 11), (10, 12), (10, 13), (10, 14),  # Horizontal wall
    (15, 15), (16, 15), (17, 15), (18, 15),  # Another vertical wall
    (20, 20), (21, 21), (22, 22), (23, 23),  # Diagonal wall
    (12, 7), (12, 8), (12, 9), (13, 7), (13, 8), (13, 9)  # Block-shaped obstacle
]

#unit settings
UNITS = [{'postion': (300,100), 'target': None, 'path':[] },{'postion': (100,100), 'target': None, 'path': []}]
UNIT_SPEED = 60
COLLISION_RADIUS = TILE_WIDTH // 2
SELECTED_UNITS = []


#selection settings
IS_SELECTING = False
SELECTION_START = None
SELECTION_END = None

#Game Loop
def main():
    global DEBUG
    global IS_SELECTING, SELECTION_START, SELECTION_END
    global dt
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKQUOTE:
                    DEBUG = not DEBUG

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    IS_SELECTING = True
                    SELECTION_START = event.pos
                    SELECTION_END = event.pos
                if event.button == 3:
                    targetx, targety = event.pos
                    for unit in SELECTED_UNITS:
                        unit['target'] = (targetx, targety)
                        unit['path'] = None
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button ==1:
                    IS_SELECTING = False
                    check_selection()
            if event.type == pygame.MOUSEMOTION:
                if IS_SELECTING:
                    SELECTION_END = event.pos
                    
        #Game Logic goes here
        move_units()
        resolve_collisions()
        #Rendering
        SCREEN.fill(BLACK)
        draw_grid()
        draw_units()
        draw_selection_box()
        draw_obstacles()
        #pygame.draw.rect(SCREEN, GREEN, (1, 175, 100, 100))

        #debug
        if DEBUG:
            fps = int(clock.get_fps())
            fps_text = FONT.render(f"FPS: {fps}", True, WHITE )
            SCREEN.blit(fps_text, (SCREEN_WIDTH - 150, 10))

        #flip updates the display
        pygame.display.flip()
        dt = clock.tick(FPS) / 1000.0
    pygame.quit()
    sys.exit()

#ASTAR pathfinding algorithm
def astar(start, end):
    #heuristic
    def heuristic(cell, target):
        return abs(cell[0] - target[0]) + abs(cell[1] - target[1])
    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_cost = {start: 0}
    f_cost = {start: heuristic(start, end)}

    while(open_set):
        _, current = heappop(open_set)

        if current == end:
            #reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        for neighbor in get_neighbors(current):
            tenative_g_cost = g_cost[current] + 1
            if neighbor not in g_cost or tenative_g_cost < g_cost[neighbor]:
                came_from[neighbor] = current
                g_cost[neighbor] = tenative_g_cost
                f_cost[neighbor] = tenative_g_cost + heuristic(neighbor, end)
                if neighbor not in [cell[1] for cell in open_set]:
                    heappush(open_set, (f_cost[neighbor], neighbor))
    return []

def get_neighbors(cell):
    row, col = cell
    neighbors = [(row-1, col), (row+1, col), #up / down
                 (row, col-1), (row, col+1), #left / right
                 (row-1, col-1), (row-1,col+1), #top diagonals
                 (row+1, col-1), (row+1,col+1) #botton diagonals 
                 ]
    return [(r,c) for r,c in neighbors if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS and (r,c) not in obstacles]


#method to draw a grid on the screen
def draw_grid():
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            rect = pygame.Rect(col * TILE_WIDTH, row * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
            pygame.draw.rect(SCREEN, GRAY, rect, 1)

#method to draw unit
def draw_units():
    for unit in UNITS:
        x, y = unit['postion']
        color = BLUE if unit not in SELECTED_UNITS else GREEN
        pygame.draw.circle(SCREEN, color, (int(x) , int(y)), TILE_WIDTH // 3)

def draw_selection_box():
    if IS_SELECTING and SELECTION_START and SELECTION_END:
        selection_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        x1 , y1 = SELECTION_START
        x2, y2  = SELECTION_END
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 -y1))
        pygame.draw.rect(selection_surface, LIGHT_BLUE, rect)
        pygame.draw.rect(selection_surface, WHITE, rect, 1)
        SCREEN.blit(selection_surface, (0, 0))

def check_selection():
    global SELECTED_UNITS
    if SELECTION_START and SELECTION_END:
        x1 , y1 = SELECTION_START
        x2, y2  = SELECTION_END
        selected_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 -y1))
        SELECTED_UNITS = []
        for unit in UNITS:
            x, y = unit['postion']

            if selected_rect.collidepoint(x, y):
                SELECTED_UNITS.append(unit)

def move_units():
    for unit in UNITS:
        if unit["target"]:
            if not unit.get("path"):
                start = (int(unit["postion"][1] // TILE_HEIGHT), int(unit['postion'][0] // TILE_WIDTH))
                target = (int(unit["target"][1] // TILE_HEIGHT), int(unit['target'][0] // TILE_WIDTH))
                unit["path"] = astar(start, target)
            if unit["path"]:
                next_cell = unit['path'][0]
                target_x = next_cell[1] * TILE_WIDTH + TILE_WIDTH // 2
                target_y = next_cell[0] * TILE_HEIGHT + TILE_HEIGHT // 2
                x, y = unit['postion']

                #Calculate Direction to move
                dx = target_x - x
                dy = target_y - y
                distance = math.sqrt(dx**2 + dy**2)
                if distance < UNIT_SPEED * dt:
                    unit['postion'] = (target_x, target_y)
                    unit['path'].pop(0)
                else:
                    dx /= distance
                    dy /= distance
                    unit['postion'] = (x + dx * UNIT_SPEED * dt, y + dy * UNIT_SPEED * dt)

def resolve_collisions():
    occupied_positions = set()
    for unit in UNITS:
        if not unit['target']:
            x, y = unit['postion']
            grid_x = round(x // TILE_WIDTH) * TILE_WIDTH + TILE_WIDTH // 2
            grid_y = round(x // TILE_HEIGHT) * TILE_HEIGHT + TILE_HEIGHT // 2


            while(grid_x, grid_y) in occupied_positions:
                grid_x += TILE_WIDTH // 2
                grid_y += TILE_HEIGHT // 2
            occupied_positions.add((grid_x, grid_y))
            unit['postion'] = (grid_x, grid_y)

def draw_obstacles():
        for row, col in obstacles:
            rect = pygame.Rect(col * TILE_WIDTH, row * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
            pygame.draw.rect(SCREEN, RED, rect)

if __name__ == "__main__":
    main()