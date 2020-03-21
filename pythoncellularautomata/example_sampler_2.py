"""This example steps through each rule, without initializing a new grid"""
import pygame
from pygame.locals import QUIT
from models.ca_models import Grid, Capture, Control

SCREEN_SIZE = [1920, 1080]
CELL_SIZE = 4
BACKGROUND_COLOR = [0, 0, 0]

def main_loop():
    pygame.init()

    clock = pygame.time.Clock()
    main_window = pygame.display.set_mode(SCREEN_SIZE)
    
    grid = Grid(CELL_SIZE, 'conway', show_colors=True, aging=True)
    control = Control(grid)
        
    rule_names = list(grid.rule_set.RULE_SETS.keys())

    for rule_name in rule_names:
        
        #grid.random_seed()
        control.set_rules(rule_name)
        control.capture.load_image("D:/chaos/extra/fish.jpg")
        control.step_clock.set_timer(QUIT, 100) #auto off after n steps

        #frame update loop
        while control.running:
            clock.tick(control.fps)
            grid.update()

    pygame.quit()

if __name__ == '__main__':
    main_loop()
