import pygame
from pygame.locals import QUIT
from models.ca_models import Grid, Capture, Control

SCREEN_SIZE = [1600, 900]
CELL_SIZE = 10
BACKGROUND_COLOR = [0, 0, 0]

def main_loop():
    pygame.init()

    clock = pygame.time.Clock()
    main_window = pygame.display.set_mode(SCREEN_SIZE)
    
    grid = Grid(CELL_SIZE, 'life34', aging=1)
    control = Control(grid)
    
    #grid.random_seed()
    control.capture.load_image("D:/chaos/extra/smoothie.png")
    control.step_clock.set_timer(QUIT, 650) #auto off after n steps
    control.step_clock.set_timer(control.STATESHOTEVENT, 1) #capture state every n steps
    
    control.capture.state_shot()
    while control.running:
        grid.update()
        control.capture.screen_shot()
        pygame.display.set_caption(f'{grid.rule_set.name} step {grid.rule_set.run_ticks}')
        pygame.display.flip()
        control.capture.save_image()
    #capture last state before quit        
    control.capture.state_shot()
    pygame.quit()

if __name__ == '__main__':
    main_loop()
