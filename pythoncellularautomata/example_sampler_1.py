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
    rule_names = ['coral', 'coagulations']

    #just show states, then show colors and aging for above rulesets
    for repeat in range(len(rule_names) * 2):
        grid = Grid(CELL_SIZE, rule_names[repeat // 2], show_colors=(repeat % 2), aging=(repeat % 2))
        control = Control(grid)
        print(control.CONTROLS)

        #grid.random_seed()
        control.capture.load_image("D:/chaos/extra/fish.jpg")
        control.step_clock.set_timer(QUIT, 200 + (repeat % 2 * 200)) #auto off after n steps

        #frame update loop
        while control.running:
            clock.tick(control.fps)
            grid.update()

    pygame.quit()

if __name__ == '__main__':
    main_loop()
