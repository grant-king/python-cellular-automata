import pygame
from pygame.locals import QUIT
from models.ca_models import Grid, Capture, Control

SCREEN_SIZE = [1920, 1080]#[960, 540] 
CELL_SIZE = 2
BACKGROUND_COLOR = [0, 0, 0]

def main_loop():
    pygame.init()

    clock = pygame.time.Clock()
    main_window = pygame.display.set_mode(SCREEN_SIZE)
    
    grid = Grid(CELL_SIZE, 'walledcities', show_colors=1, aging=1)
    control = Control(grid)

    #grid.random_seed()
    control.capture.load_image("D:/chaos/extra/utah.jpg")
    #control.step_clock.set_timer(QUIT, 5500) #auto off after n steps

    #frame update loop
    while control.running:
        clock.tick(control.fps)
        grid.update()

    pygame.quit()

if __name__ == '__main__':
    main_loop()
