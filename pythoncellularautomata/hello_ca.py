import pygame
from models.ca_models import Grid, Capture, Control

SCREEN_SIZE = [800, 450]
CELL_SIZE = 4
BACKGROUND_COLOR = [0, 0, 0]

def main_loop():
    pygame.init()

    clock = pygame.time.Clock()
    main_window = pygame.display.set_mode(SCREEN_SIZE)
    
    grid = Grid(CELL_SIZE, 'coral')
    control = Control(grid)
    
    grid.random_seed()
    
    while control.running:
        clock.tick(control.fps)
        grid.update()
        
    pygame.quit()

if __name__ == '__main__':
    main_loop()
