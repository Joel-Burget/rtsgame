import math
import pygame
import sys

#init pygame
pygame.init()

#window variables
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1200
FPS = 120
TITLE = "TDB RTS GAME"

#color variables
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (0, 0, 255, 128)
BLUE = (0, 0, 255)

#debugging tools 
DEBUG = False
FONT = pygame.font.Font(None, 50)

#init screen
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)

#FPS clock
clock = pygame.time.Clock()

#Grid Settings
TILE_WIDTH = 40
TILE_HEIGHT = 40
GRID_ROWS = SCREEN_HEIGHT // TILE_HEIGHT
GRID_COLS = SCREEN_WIDTH // TILE_WIDTH

#init variables
UNIT_POSITION = (1, 1)


UNITS = [{'postion': (200,200), 'target': None },{'postion': (300,300), 'target': None}]
UNIT_SPEED = 1
COLLISION_RADIUS = TILE_WIDTH // 2
SELECTED_UNITS = []
IS_SELECTING = False
SELECTION_START = None
SELECTION_END = None


#Game Loop
def main():
    global DEBUG
    global IS_SELECTING, SELECTION_START, SELECTION_END
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
        #pygame.draw.rect(SCREEN, GREEN, (1, 175, 100, 100))

        #debug
        if DEBUG:
            fps = int(clock.get_fps())
            fps_text = FONT.render(f"FPS: {fps}", True, WHITE )
            SCREEN.blit(fps_text, (SCREEN_WIDTH - 150, 10))

        #flip updates the display
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

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
        if unit['target']:
            target_x, target_y = unit['target']
            x, y = unit['postion']
            
            #Calcuate Direction to move
            dx = target_x - x
            dy = target_y -y

            distance = math.sqrt(dx**2 + dy**2)

            if distance < UNIT_SPEED:
                unit['postion'] = (target_x, target_y)
                unit['target'] = None
            else:
                dx /= distance
                dy /= distance

                for other_units in UNITS:
                    if other_units == unit:
                        continue
                    other_x, other_y = other_units['postion']
                    other_distance = math.sqrt((other_x - x)**2 + (other_y - y)**2)

                    if other_distance < COLLISION_RADIUS:
                        avoidance_dx = x - other_x
                        avoidance_dy = y - other_y
                        avoidance_distance = math.sqrt((avoidance_dx)**2 + (avoidance_dy)**2)
                        if avoidance_distance > 0:
                            avoidance_dx /= avoidance_distance
                            avoidance_dy /= avoidance_distance
                            dx += avoidance_dx * .5
                            dy += avoidance_dy * .5
                

                adjusted_distance = math.sqrt(dx**2 + dy**2)
                if adjusted_distance > 0:
                    dx /= adjusted_distance
                    dy /= adjusted_distance
                x += dx * UNIT_SPEED
                y += dy * UNIT_SPEED
                unit['postion'] = (x, y)

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

if __name__ == "__main__":
    main()