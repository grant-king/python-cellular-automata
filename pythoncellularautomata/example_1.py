import pygame
from pygame.locals import QUIT
from models.ca_models import Grid, Capture, Control

SCREEN_SIZE = [1920, 1080]
CELL_SIZE = 3
BACKGROUND_COLOR = [0, 0, 0]

def main_loop():
    pygame.init()

    clock = pygame.time.Clock()
    main_window = pygame.display.set_mode(SCREEN_SIZE)
    
    grid = Grid(CELL_SIZE, 'coagulations', show_colors=True, aging=True)
    control = Control(grid)
    print(control.CONTROLS)

    #grid.random_seed()
    control.capture.load_image("D:/chaos/extra/fish.jpg")
    control.step_clock.set_timer(QUIT, 1650) #auto off after n steps
    
    #capture stateshot of seed
    control.capture.state_shot()

    #frame update loop
    while control.running:
        clock.tick(control.fps)
        grid.update()

    pygame.quit()

if __name__ == '__main__':
    main_loop()
