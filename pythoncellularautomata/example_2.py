#This example does not save to disk
import pygame
from pygame.locals import QUIT
from models.ca_models import Grid, Capture, Control
import os

SCREEN_SIZE = [1920, 1080]
CELL_SIZE = 10
BACKGROUND_COLOR = [0, 0, 0]

def main_loop():
    pygame.init()

    clock = pygame.time.Clock()
    main_window = pygame.display.set_mode(SCREEN_SIZE)
    
    grid = Grid(CELL_SIZE, 'coral', aging=1, processing_mode=2)
    control = Control(grid)
    
    control.capture.load_image("D:/chaos/extra/tgcc.jpg")
    control.step_clock.set_timer(QUIT, 1950) #auto off after n steps
    control.step_clock.set_timer(control.PERFSTATSEVENT, 100) #log performance every 100 steps
    
    while control.running:
        #clock.tick(22)
        grid.update()
    
    pygame.quit()
    control.write_performance()

if __name__ == '__main__':
    main_loop()
