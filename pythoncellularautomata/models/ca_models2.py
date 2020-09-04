import pygame
from pygame.locals import USEREVENT, KEYDOWN, QUIT, K_ESCAPE, K_l, K_i, K_r, K_s, K_t, K_UP, K_DOWN, K_a
import os
import math
import cv2
from skimage import exposure
from .performance_monitor import PerformanceMonitor
from .ruleset_models import Ruleset
from .system_configuration_models import SystemConfigurationManager
#from models.controls_ui import ButtonWindow
import numpy as np

class Control:
    def __init__(self, grid):
        self.grid = grid
        self.capture = Capture(grid)
        self.step_clock = StepClock()
        self.perf_monitor = PerformanceMonitor(grid)
        self.STATESHOTEVENT = USEREVENT + 1
        self.PERFSTATSEVENT = USEREVENT + 2
        self.RULECYCLEEVENT = USEREVENT + 3
        self.ALLSHOTSEVENT = USEREVENT + 4
        self.fps = 30
        self.timer_rulesets = []
        self.CONTROLS = """l: load from state shot\ni: load from image
r: change ruleset\ns: save image and state shot
t: set a timer\nup/down arrow keys: control FPS
a: alternate rulesets timer shortcut
esc: end current simulation\n"""
        print(self.CONTROLS)

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
        key_monitor = {
            K_l: [self.load_state_handler],
            K_i: [self.load_image_handler],
            K_r: [self.change_ruleset_handler],
            K_s: [
                self.state_shot_handler, 
                self.screen_shot_handler, 
                self.save_image_handler
                ],
            K_t: [self.set_timer_handler],
            K_a: [self.set_ruleset_cycle_timer_handler],
            K_UP: [self.increase_fps_handler],
            K_DOWN: [self.decrease_fps_handler]
        }
        event_monitor = {
            self.STATESHOTEVENT: self.state_shot_handler,
            self.PERFSTATSEVENT: self.performance_event_handler,
            self.RULECYCLEEVENT: self.rulecycle_event_handler,
            self.ALLSHOTSEVENT: self.all_shots_handler,
        }
        
        for event in self.events:
            if event.type == KEYDOWN:
                if event.key in key_monitor.keys():
                    for key_handler in key_monitor[event.key]:
                        key_handler()
                else:
                    pass
            elif event.type in event_monitor.keys():
                event_monitor[event.type]()
            else:
                pass

    def set_allshots_timer(self, interval):
        self.step_clock.set_timer(self.ALLSHOTSEVENT, interval)

    def set_ruleset_cycle_timer(self, interval, rule_list):
        for item in rule_list:
            if item not in self.grid.rule_set.RULE_SETS.keys(): #validate input
                rule_list.pop(item)
                print(f"Invalid '{item}' removed from ruleset rotation list.")
                
        if len(rule_list) > 0:
            self.step_clock.set_timer(self.RULECYCLEEVENT, int(interval))
            self.timer_rulesets = rule_list
        else:
            print("No valid rulesets to set a timer to. Timer aborted.")

    def set_timer_handler(self):
        timer_type = input("Type the type of timer you want to set: 'end', 'allshots', or 'ruleset' : ")
        if timer_type == 'allshots':
            timer_ticks = input("How often, in steps, would you like to capture all shot types? ")
            self.step_clock.set_timer(self.ALLSHOTSEVENT, int(timer_ticks))
        elif timer_type == 'end':
            timer_ticks = input("In how many steps would you like to end the simulation? ")
            self.step_clock.set_timer(QUIT, int(timer_ticks), repeating=False)
            print(f"Simulation will end in {timer_ticks} ticks.")
        elif timer_type == 'rulesetcycle':
            self.set_ruleset_cycle_timer_handler()
        else:
            print(f"{timer_type} is not a valid option. Press 't' to try again.")

    def set_ruleset_cycle_timer_handler(self):
            timer_ticks = input("How often, in steps, would you like to alternate between rules? ")
            rule_list = input("List the rules you would like to alternate between, separate by spaces: ").split(' ')

            self.set_ruleset_cycle_timer(timer_ticks, rule_list)
    
    def state_shot_handler(self):
        self.capture.state_shot()

    def save_image_handler(self):
        self.capture.save_image()

    def screen_shot_handler(self):
        self.capture.screen_shot()

    def all_shots_handler(self):
        print('all shots handler called')
        self.capture.state_shot()
        self.capture.save_image()
        self.capture.screen_shot()

    def load_state_handler(self):
        print("------------- Load From Binary State Image -------------")
        self.map_file_dir = input(f'type the directory name to load, within {self.capture.main_dir}: ')
        self.map_file_name = input(f'type the file name to load, within {os.path.join(self.capture.main_dir, self.map_file_dir)}: ')

        if os.path.exists(os.path.join(self.capture.main_dir, self.map_file_dir, self.map_file_name)):
            self.capture.load_state_shot(os.path.join(self.capture.main_dir, self.map_file_dir, self.map_file_name))
        else:
            print(f"{os.path.join(self.capture.main_dir, self.map_file_dir, self.map_file_name)} does not exist. Press 'l' to try again")

    def load_image_handler(self):
        print("------------- Load From Color Image -------------")
        self.image_file_dir = input('type the directory name to load: ')
        self.image_file_name = input(f'type the file name to load, within {self.image_file_dir}: ')

        if os.path.exists(os.path.join(self.image_file_dir, self.image_file_name)):
            self.capture.load_image(os.path.join(self.image_file_dir, self.image_file_name))
        else:
            print(f"{os.path.join(self.image_file_dir, self.image_file_name)} does not exist. Press 'i' to try again")

    def change_ruleset_handler(self):
        new_ruleset = input("type new ruleset name: ")
        rulesets = self.grid.rule_set.RULE_SETS.keys()
        if new_ruleset in rulesets:
            self.set_rules(new_ruleset)
        else:
            print(f'{new_ruleset} not found in ruleset names')
            print(f'Please choose from any of the following:\n{list(rule_name for rule_name in rulesets)}')

    def performance_event_handler(self):
        self.perf_monitor.update()

    def rulecycle_event_handler(self):
        self.set_rules(self.timer_rulesets[-1])
        self.timer_rulesets.append(self.timer_rulesets.pop(0)) #shift queue

    def increase_fps_handler(self):
        if self.fps < 100 and self.fps > 0:
            self.fps += math.ceil((self.fps + 10) / 10)
        elif self.fps == 0:
            self.fps += 30
        else:
            self.fps = 0
        print(f'FPS cap increased to {self.fps}')

        if self.fps == 0:
            print(f'FPS unlimited')
    
    def decrease_fps_handler(self):
        if self.fps > 0:
            self.fps -= math.ceil((self.fps + 10) / 10)
            if self.fps <= 0:
                self.fps == 0
                print(f'FPS unlimited')
            else:
                print(f'FPS cap decreased to {self.fps}')

    def set_rules(self, rule_name):
        print(f'Ending ruleset: {self.grid.rule_set} after {self.grid.rule_set.run_ticks} ticks')
        self.grid.rule_set = Ruleset(rule_name)
        self.grid.ruleset_changes += 1
        print((f'Starting ruleset: {self.grid.rule_set}'))


class StepClock:
    def __init__(self):
        self.timers = []

    def set_timer(self, event_id, ticks, repeating=True):
        new_timer = StepTimer(event_id, ticks, repeating)
        self.timers.append(new_timer)

    def update(self):
        for idx, timer in enumerate(self.timers):
            timer.update()


class StepTimer:
    #post event event_id every delay_ticks ticks
    def __init__(self, event_id, ticks, repeating):
        self.event_id = event_id
        self.event = pygame.event.Event(event_id)
        self.timer_ticks = ticks
        self.ticks_remaining = ticks
        self.repeating = repeating #bool
        
    def update(self):
        if self.ticks_remaining > 1:
            self.ticks_remaining -= 1
        elif self.ticks_remaining == 1:
            pygame.event.post(self.event)
            self.reset()
        else:
            pass

    def reset(self):
        if self.repeating:
            self.ticks_remaining = self.timer_ticks
        else:
            self.ticks_remaining = 0 #turn timer off
                

class Capture:
    def __init__(self, grid):
        self.main_window = pygame.display.get_surface()
        self.rule_name = grid.rule_set.name
        self.grid = grid
        self.sys_config_manager = SystemConfigurationManager()
        self.main_dir = self.sys_config_manager.save_directory
        extension_id = len(os.listdir(self.main_dir)) + 1
        self.screenshot_dir = f'{grid.rule_set.name}_{grid.num_columns}x{grid.num_rows}_{extension_id}'

        self.shot_counter = 1

    @property
    def step_counter(self):
        return self.grid.rule_set.run_ticks

    def screen_shot(self):
        """take a shot of the pygame main window as it appears"""
        if not os.path.exists(os.path.join(self.main_dir, self.screenshot_dir)):
            os.mkdir(os.path.join(self.main_dir, self.screenshot_dir))
        filename = os.path.join(self.main_dir, self.screenshot_dir, f'shot_{self.grid.ruleset_changes}-{self.grid.rule_set.name}_{self.step_counter}.png')
        pygame.image.save(self.main_window, filename)

    def save_image(self):
        """Save all current cell colors, regardless of state, as equilized color image"""
        if not os.path.exists(os.path.join(self.main_dir, self.screenshot_dir)):
            os.mkdir(os.path.join(self.main_dir, self.screenshot_dir))
        filename = os.path.join(self.main_dir, self.screenshot_dir, f'image_{self.grid.ruleset_changes}-{self.grid.rule_set.name}_{self.step_counter}.png')
        bgr_img = cv2.cvtColor(self.grid.color_channels, cv2.COLOR_RGB2BGR)
        equalized = exposure.equalize_adapthist(np.array(bgr_img, dtype=np.uint8)) * 255
        cv2.imwrite(filename, equalized)

    def state_shot(self):
        """capture cell active states as b&w png"""
        if not os.path.exists(os.path.join(self.main_dir, self.screenshot_dir)):
            os.mkdir(os.path.join(self.main_dir, self.screenshot_dir))
        filename = os.path.join(self.main_dir, self.screenshot_dir, f'step_{self.grid.ruleset_changes}-{self.grid.rule_set.name}_{self.step_counter}.png')
        states = np.array(self.grid.current_states, dtype=np.int8) * 255
        cv2.imwrite(filename, states)

    def load_state_shot(self, map_path):
        """load from existing state map"""
        state_map = cv2.imread(map_path)
    
        for column in range(self.grid.num_columns):
            for row in range(self.grid.num_rows):
                if 0 not in state_map[row, column]:
                    self.grid.cells[column][row].toggle_cell(1)
        self.grid.manual_update_states()
            
    def aspect_resize(self, image_data):
        """preserve aspect on resize"""
        og_size = image_data.shape[:2] #height, width
        max_size = self.grid.SCREEN_SIZE #width, height
        resize_ratio = min(max_size[1] / og_size[0], max_size[0] / og_size[1])
        new_size = ((og_size[0] * resize_ratio), (og_size[1] * resize_ratio)) #height, width
        
        num_rows = round(new_size[0] / self.grid.CELL_SIZE)
        num_columns = round(new_size[1] / self.grid.CELL_SIZE)
        
        resized = cv2.resize(image_data, (num_columns, num_rows))
        
        pygame.display.set_mode([int(dim) for dim in new_size[::-1]], flags=pygame.RESIZABLE)
        self.grid.SCREEN_SIZE = new_size
        self.grid.image_size = (num_columns * self.grid.CELL_SIZE, num_rows * self.grid.CELL_SIZE) #width, height
        self.grid.num_rows = num_rows
        self.grid.num_columns = num_columns
        self.grid.current_states = np.ascontiguousarray(self.grid.current_states[:num_rows, :num_columns])
        self.grid.color_channels = np.array(resized, dtype=np.float32)
        self.grid.cells_history = np.zeros((num_rows, num_columns, 10), dtype=np.bool)

        return resized

    def load_image(self, image_path):
        image_data = cv2.imread(image_path)
        resized = self.aspect_resize(image_data)
        edges = cv2.Canny(resized, 100, 250, L2gradient=True)
        
        self.grid.color_channels = resized
        self.grid.current_states = np.array(edges, dtype=np.bool)
        self.grid.switch_channels()
        
    def save_step_data(self):
        """save state shot and color image as arrays to lmdb"""
        pass