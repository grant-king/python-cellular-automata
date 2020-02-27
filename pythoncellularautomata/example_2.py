#This example does not save to disk
import pygame
from pygame.locals import QUIT
from models.ca_models import Grid, Capture, Control

SCREEN_SIZE = [1600, 900]
CELL_SIZE = 15
BACKGROUND_COLOR = [0, 0, 0]

def main_loop():
    pygame.init()

    clock = pygame.time.Clock()
    main_window = pygame.display.set_mode(SCREEN_SIZE)
    
    grid = Grid(CELL_SIZE, 'maze', aging=1)
    control = Control(grid)
    
    control.capture.load_image("D:/chaos/extra/smoothie.png")
    control.step_clock.set_timer(QUIT, 650) #auto off after n steps
    control.step_clock.set_timer(control.PERFSTATSEVENT, 100) #
    
    while control.running:
        grid.update()
        pygame.display.set_caption(f'{grid.rule_set.name} step {grid.rule_set.run_ticks}')
        pygame.display.flip()
    
    pygame.quit()

if __name__ == '__main__':
    main_loop()
