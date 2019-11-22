import pygame
from models.ca_models import Grid, Capture, Control

SCREEN_SIZE = [800, 450]
CELL_SIZE = 10
BACKGROUND_COLOR = [0, 0, 0]

def main_loop():
    pygame.init()

    clock = pygame.time.Clock()
    main_window = pygame.display.set_mode(SCREEN_SIZE)
    
    grid = Grid(CELL_SIZE, 'conway')
    capture = Capture(grid)
    control = Control(capture)
    
    grid.random_seed()
    
    while control.running:
        clock.tick(14)
        grid.update()
        pygame.display.set_caption(f'{grid.rule_set.name} step {grid.rule_set.run_ticks}')
        pygame.display.flip()
        
    pygame.quit()

if __name__ == '__main__':
    main_loop()
