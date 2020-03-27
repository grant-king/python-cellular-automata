import pygame
from pygame.locals import USEREVENT, KEYDOWN, QUIT, K_ESCAPE, K_l, K_i, K_r, K_s, K_t, K_UP, K_DOWN
import os
import cv2
from skimage import exposure
from models.performance_monitor import PerformanceMonitor
from models.ruleset_models import Ruleset
import numpy as np

class Control:
    def __init__(self, grid):
        self.grid = grid
        self.capture = Capture(grid)
        self.step_clock = StepClock()
        self.perf_monitor = PerformanceMonitor(grid)
        self.STATESHOTEVENT = USEREVENT + 1
        self.PERFSTATSEVENT = USEREVENT + 2
        self.fps = 30
        self.CONTROLS = """l: load from state shot\ni: load from image
r: change ruleset\ns: save image and state shot
t: set a timer\nup/down arrow keys: control FPS
esc: end current simulation\n"""

    def write_performance(self):
        self.perf_monitor.write_report()

    def catch_events(self, events):
        self.events = events

    @property
    def running(self):
        self.step_clock.update()
        self.catch_events(pygame.event.get())
        self.listen()
        return self.listen_quit()

    def listen_quit(self):
        #return condition to continue game
        for event in self.events:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
            elif event.type == QUIT:
                return False
        return True

    def listen(self):
        #listen for button presses and refer to handlers
        for event in self.events:
            if event.type == KEYDOWN:
                if event.key == K_l:
                    self.load_state_handler()
                if event.key == K_i:
                    self.load_image_handler()
                if event.key == K_r:
                    self.change_ruleset_handler()
                if event.key == K_s:
                    self.state_shot_handler()
                    self.screen_shot_handler()
                    self.save_image_handler()
                if event.key == K_t:
                    self.set_timer_handler()
                if event.key == K_UP:
                    self.increase_fps_handler()
                if event.key == K_DOWN:
                    self.decrease_fps_handler()
            if event.type == self.STATESHOTEVENT:
                self.state_shot_handler()
            if event.type == self.PERFSTATSEVENT:
                self.performance_event_handler()

    def set_timer_handler(self):
        stateshot = input('type 1 to set stateshot timer or 0 to set end timer: ')
        if int(stateshot):
            timer_ticks = input("Type the steps frequency in to take a stateshot: ")
            self.step_clock.set_timer(self.STATESHOTEVENT, int(timer_ticks))
        else:
            timer_ticks = input("In how many steps would you like to end the simulation? ")
            self.step_clock.set_timer(QUIT, int(timer_ticks))
            print(f"Simulation will end in {timer_ticks} ticks.")
    
    def state_shot_handler(self):
        self.capture.state_shot()

    def save_image_handler(self):
        self.capture.save_image()

    def screen_shot_handler(self):
        self.capture.screen_shot()

    def load_state_handler(self):
        self.map_file_dir = input("type the directory name to load, within D:/chaos/: ")
        self.map_file_name = input(f"type the file name to load, within within D:/chaos/{self.map_file_dir}/: ")

        self.capture.load_state_shot(f'D:/chaos/{self.map_file_dir}/{self.map_file_name}')

    def load_image_handler(self):
        self.image_file_dir = input("type the directory name to load: ")
        self.image_file_name = input(f"type the file name to load, within within {self.image_file_dir}/: ")

        self.capture.load_image(f'{self.image_file_dir}/{self.image_file_name}')

    def change_ruleset_handler(self):
        new_ruleset = input("type new ruleset name: ")
        self.set_rules(new_ruleset)

    def performance_event_handler(self):
        self.perf_monitor.update()

    def increase_fps_handler(self):
        if self.fps < self.perf_monitor.average_fps:
            self.fps += 3
            print(f'FPS cap increased to {self.fps}')
    
    def decrease_fps_handler(self):
        if self.fps > 0:
            self.fps -= 3
            print(f'FPS cap decreased to {self.fps}')

    def set_rules(self, rule_name):
        print(f'Ending ruleset: {self.grid.rule_set} after {self.grid.rule_set.run_ticks} ticks')
        self.grid.rule_set = Ruleset(rule_name)
        print((f'Starting ruleset: {self.grid.rule_set}'))


class StepClock:
    def __init__(self):
        self.timers = []

    def set_timer(self, event_id, ticks):
        new_timer = StepTimer(event_id, ticks)
        self.timers.append(new_timer)

    def update(self):
        for idx, timer in enumerate(self.timers):
            timer.update()
            if timer.ticks_remaining == -1:
                self.timers.pop(idx)


class StepTimer:
    #post event event_id every delay_ticks ticks
    def __init__(self, event_id, ticks):
        self.event_id = event_id
        self.event = pygame.event.Event(event_id)
        self.timer_ticks = ticks
        self.ticks_remaining = ticks
        
    def update(self):
        if self.ticks_remaining > 0:
            self.ticks_remaining -= 1
        else:
            pygame.event.post(self.event)
            self.ticks_remaining = -1
        


class Capture:
    def __init__(self, grid):
        self.main_window = pygame.display.get_surface()
        self.rule_name = grid.rule_set.name
        self.grid = grid
        self.main_dir = 'D:/chaos'
        extension_id = len(os.listdir(self.main_dir)) + 1
        self.screenshot_dir = f'{grid.rule_set.name}_{grid.num_columns}x{grid.num_rows}_{extension_id}'

        self.shot_counter = 1

        os.chdir(self.main_dir)

    @property
    def step_counter(self):
        return self.grid.rule_set.run_ticks

    def screen_shot(self):
        if not os.path.exists(f'./{self.screenshot_dir}/'):
            os.mkdir(f'./{self.screenshot_dir}/')
        filename = f'{self.main_dir}/{self.screenshot_dir}/shot_{self.step_counter}.png'
        pygame.image.save(self.main_window, filename)

    def state_shot(self):
        #capture cell active states as b&w png
        if not os.path.exists(f'./{self.screenshot_dir}/'):
            os.mkdir(f'./{self.screenshot_dir}/')
        os.chdir(f'./{self.screenshot_dir}/')
        filename = f'step_{self.step_counter}.png'
        states = np.array(self.grid.current_states, dtype=np.int8) * 255
        cv2.imwrite(filename, states)
        os.chdir('../')

    def load_state_shot(self, map_path):
        #load from existing state map
        state_map = cv2.imread(map_path)
    
        for column in range(self.grid.num_columns):
            for row in range(self.grid.num_rows):
                if 0 not in state_map[row, column]:
                    self.grid.cells[column][row].toggle_cell(1)
        self.grid.manual_update_states()
            
    def load_image(self, image_path):
        image_data = cv2.imread(image_path)
        resized = cv2.resize(image_data, (self.grid.num_columns, self.grid.num_rows))
        self.grid.color_channels = np.array(resized, dtype=np.float32)
        edges = cv2.Canny(resized, 100, 250, L2gradient=True)

        for column in range(self.grid.num_columns):
            for row in range(self.grid.num_rows):
                self.grid.cells[column][row].set_color(resized[row, column])
                if edges[row, column]: #activate cells corresponding to edges mask
                    self.grid.cells[column][row].toggle_cell(1)
                else:
                    self.grid.cells[column][row].toggle_cell(0)
        self.grid.manual_update_states()
        self.grid.switch_channels()

    def save_image(self):
        """Save all current cell colors, regardless of state, as equilized color image"""
        if not os.path.exists(f'./{self.screenshot_dir}/'):
            os.mkdir(f'./{self.screenshot_dir}/')
        filename = f'{self.main_dir}/{self.screenshot_dir}/image_{self.step_counter}.png'
        bgr_img = cv2.cvtColor(self.grid.color_channels, cv2.COLOR_RGB2BGR)
        equalized = exposure.equalize_adapthist(np.array(bgr_img, dtype=np.uint8))
        cv2.imwrite(filename, equalized * 255)
        
