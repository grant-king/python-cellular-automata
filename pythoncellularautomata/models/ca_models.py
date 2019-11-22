import pygame
import random
import os
import logging
import numpy as np
import cv2
#from pygame.locals import *
from pygame.locals import USEREVENT, KEYDOWN, QUIT, K_ESCAPE, K_l, K_i, K_r, K_s, K_t
from time import time, ctime

logging.basicConfig(
    filename = 'simulation.log', 
    level = logging.DEBUG, 
    format = '%(levelname)s: %(message)s', 
    filemode='a'
    )

class Control:
    def __init__(self, capture):
        self.capture = capture
        self.step_clock = StepClock()
        self.STATESHOTEVENT = USEREVENT + 1

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
                    self.save_image_handler()
                if event.key == K_t:
                    self.set_timer_handler()
            if event.type == self.STATESHOTEVENT:
                self.state_shot_handler()

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
        self.capture.grid.set_rules(new_ruleset)


class StepClock:
    def __init__(self):
        self.timers = []

    def set_timer(self, event_id, ticks):
        new_timer = StepTimer(event_id, ticks)
        self.timers.append(new_timer)

    def update(self):
        for timer in self.timers:
            timer.update()


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
            self.ticks_remaining = self.timer_ticks - 1


class Grid:
    def __init__(self, cell_size, rule_name, aging=False):
        self.SCREEN_SIZE = pygame.display.get_surface().get_size()
        self.CELL_SIZE = cell_size
        self.aging = aging

        self.cells = []
        self.total_cells = 0
        self.cells_history = [] #list of sum of bools state history
        self.num_columns = self.SCREEN_SIZE[0] // self.CELL_SIZE
        self.num_rows = self.SCREEN_SIZE[1] // self.CELL_SIZE
        self.current_states = np.zeros((self.num_rows, self.num_columns), dtype=np.bool)
        self.current_states_updates = np.zeros((self.num_rows, self.num_columns), dtype=np.bool)
        self.rule_set = Ruleset(rule_name)
        self.build_cells()

        logging.info(f'Grid initialized with {self.rule_set.name} rule at {ctime()} with {self.total_cells} cells')
        print(f'Grid initialized with {self.rule_set.name} rule at {ctime()} with {self.total_cells} cells')

    def build_cells(self):
        self.cells = [[0 for row in range(self.num_rows)] for column in range(self.num_columns)]
        for col_idx in range(self.num_columns):
            for row_idx in range(self.num_rows):
                self.cells[col_idx][row_idx] = Cell(self.CELL_SIZE, col_idx, row_idx)
                self.total_cells += 1

    def random_seed(self):
        DEAD_RATIO = 2 / 7
        chances = list([1 for dead in range(int(1 / DEAD_RATIO - 1))])
        chances.append(0)
        seedline_cols = set([random.randrange(self.num_columns) for column in range(random.randrange(10, self.num_columns//5))])
        for col_idx, cell_col in enumerate(self.cells):
            if col_idx in seedline_cols:
                for cell in cell_col:
                    cell.toggle_cell(random.choice(chances))
        
        self.manual_update_states()

    def update(self):
        self.update_current_states()

        for col_idx, cell_col in enumerate(self.cells):
            for row_idx, cell in enumerate(cell_col):
                # todo if first or last, wrap from edge
                if row_idx == 0 or row_idx == self.num_rows or col_idx == 0 or col_idx == self.num_columns:
                    pass    
                else:
                    neighborhood = self.get_neighborhood(row_idx, col_idx)
                    cell.cell_logic.update(neighborhood)
                cell.cell_visual.update(self.aging)
                self.rule_set.apply_rules(cell)
                self.current_states_updates[row_idx, col_idx] = cell.cell_logic.alive
        
        self.rule_set.add_tick()

    def get_neighborhood(self, row_idx, col_idx):
        #copy neighborhood surrounding cell location
        neighborhood = self.current_states[row_idx-1:row_idx+2, col_idx-1:col_idx+2].copy()
        neighborhood[1, 1] = 0
        return neighborhood

    def update_current_states(self):
        self.current_states = self.current_states_updates.copy()

    def all_on_visual_only(self):
        pass           

    def manual_update_states(self):
        #capture 2d bool array of current states
        for column in range(self.num_columns):
            for row in range(self.num_rows):
                self.current_states_updates[row, column] = self.cells[column][row].cell_logic.alive

    def set_rules(self, name):
        logging.info(f'Ending ruleset: {self.rule_set} after {self.rule_set.run_ticks} ticks')
        self.rule_set = Ruleset(name)
        logging.info(f'Starting ruleset: {self.rule_set}')

    def wrap_screen(self, ridx, cidx):
        #wrap screen
        if ridx == grid.num_rows - 1:
            rplus = 0
        else:
            rplus = ridx + 1
        if ridx == 0:
            rminus = grid.num_rows - 1
        else:
            rminus = ridx - 1
        if cidx == grid.num_columns - 1:
            cplus = 0
        else:
            cplus = cidx + 1
        if cidx == 0:
            cminus = grid.num_columns - 1
        else:
            cminus = cidx - 1

        #north, ne, e, se, s, sw, w, nw
        neighbors = [
            self.current_states[rminus, cidx],
            self.current_states[rminus, cplus],
            self.current_states[ridx, cplus],
            self.current_states[rplus, cplus],
            self.current_states[rplus, cidx],
            self.current_states[rplus, cminus],
            self.current_states[ridx, cminus], 
            self.current_states[rminus, cminus],
            ]


class Cell:
    def __init__(self, square_size, column_idx, row_idx, living=False):
        
        self.cell_logic = CellLogic(column_idx, row_idx, living=living)
        self.cell_visual = CellVisual(square_size, column_idx, row_idx, living=living)
        
    @property
    def neighborhood_sum(self):
        return self.cell_logic.neighborhood_sum

    def update(self):
        self.cell_visual.update()

    def set_neighbors(self, neighborhood):
        self.cell_logic.set_neighbors(neighborhood)

    def set_color(self, new_color):
        self.cell_visual.set_color(new_color)

    def toggle_cell(self, revive):
        if revive:
            self.cell_logic.alive = True
            self.cell_visual.alive = True
        else:
            self.cell_logic.alive = False
            self.cell_visual.alive = False


class CellVisual:
    def __init__(self, square_size, column_idx, row_idx, living=False):
        
        startx = square_size * column_idx
        starty = square_size * row_idx

        self.START_LOC = [startx, starty]

        self.column_idx = column_idx
        self.row_idx = row_idx

        red = random.randint(150, 250)
        green = random.randint(20, 50)
        blue = random.randint(green, red)
        
        self.color_floats = [float(red), float(green), float(blue)]
        self.original_color = [red, green, blue]
        self.size = [square_size, square_size]
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.color)
        
        self.rect = self.surface.get_rect()
        self.rect.move_ip(self.START_LOC)

        self.alive = living
        self.history = np.zeros(10, dtype=np.bool)

    @property
    def color(self):
        return [int(self.color_floats[idx]) for idx in range(3)]

    @property
    def history_avg(self):
        return self.history.sum() / len(self.history)

    def update(self, aging):
        if aging:
            self.age_color()
        self.update_visual()
        self.draw()

    def draw(self):
        main_window = pygame.display.get_surface()
        main_window.blit(self.surface, self.rect)

    def set_color(self, new_color):
        blue, green, red = new_color
        
        self.color_floats = [float(red), float(green), float(blue)]
        self.original_color = [red, green, blue]

    def age_color(self):
        #get current state
        self.history = np.append(self.history, self.alive)
    
        for idx, component in enumerate(self.color):
            if self.history[-2]: # if last state was alive, age towards white
                if component < 250:
                    self.color_floats[idx] += self.history_avg / 2 #add according to average of last n states
            else:# otherwise decrease color components
                if component > 20: 
                    self.color_floats[idx] -= component / 250 #control darkening rate
                else:
                    self.color_floats[idx] = self.original_color[idx]
        #shift history
        self.history = np.delete(self.history, 0)

    def update_visual(self):
        if self.alive:
            self.surface.fill(self.color)
        else:
            inverse = [255-component for component in self.color]
            self.surface.fill(inverse)
            

class CellLogic:
    def __init__(self, column_idx, row_idx, living=False):
        self.column_idx = column_idx
        self.row_idx = row_idx

        self.alive = living
        self.neighborhood_array = np.zeros((3, 3), dtype=np.bool)
        self.neighborhood_sum = 0

    def update(self, neighborhood_array): 
        self.neighborhood_array = neighborhood_array
        self.neighborhood_sum = neighborhood_array.sum()


class Ruleset:
    def __init__(self, name):
        RULE_SETS = {
            '2x2': {'survive': [1, 2, 5], 'born': [3, 6]}, 
            'amoeba': {'survive': [1, 3, 5, 8], 'born': [3, 5, 7]},
            'assimilation': {'survive': [4, 5, 6, 7], 'born': [3, 4, 5]},
            'coagulations': {'survive': [2, 3, 5, 6, 7, 8], 'born': [3, 7, 8]},
            'coral': {'survive': [4, 5, 6, 7, 8], 'born': [3]},
            'conway': {'survive': [2, 3], 'born': [3]},
            'daynight': {'survive': [3, 4, 6, 7, 8], 'born': [3, 6, 7, 8]},
            'diamoeba': {'survive': [5, 6, 7, 8], 'born': [3, 5, 6, 7, 8]},
            'electrifiedmaze': {'survive': [1, 2, 3, 4, 5], 'born': [4, 5]}, 
            'flakes': {'survive': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'born': [3]},
            'flock': {'survive': [1, 2], 'born': [3]},
            'fredkin': {'survive': [0, 2, 4, 6, 8], 'born': [1, 3, 5, 7]}, 
            'gnarl': {'survive': [1], 'born': [1]}, 
            'highlife': {'survive': [2, 3], 'born': [3, 6]}, 
            'honeylife': {'survive': [2, 3, 8], 'born': [3, 8]}, 
            'inverselife': {'survive': [3, 4, 6, 7, 8], 'born': [0, 1, 2, 3, 4, 7, 8]}, 
            'ironflock': {'survive': [0, 2, 3], 'born': [3]},
            'longlife': {'survive': [5], 'born': [3, 4, 5]},
            'life34': {'survive': [3, 4], 'born': [3, 4]},
            'lfod': {'survive': [0], 'born': [2]},
            'maze': {'survive': [1, 2, 3, 4, 5], 'born': [3]}, 
            'mazectric': {'survive': [1, 2, 3, 4], 'born': [3]}, 
            'move': {'survive': [2, 4, 5], 'born': [3, 6, 8]},
            'pedestrianlife': {'survive': [2, 3], 'born': [3, 8]},
            'pseudolife': {'survive': [2, 3, 8], 'born': [3, 5, 7]}, 
            'replicator': {'survive': [1, 3, 5, 7], 'born': [1, 3, 5, 7]}, 
            'replicatorlog': {'survive': [2, 4, 5], 'born': [3, 6]}, 
            'seeds': {'survive': [], 'born': [2]}, 
            'serviettes': {'survive': [], 'born': [2, 3, 4]},
            'stains': {'survive': [2, 3, 5, 6, 7, 8], 'born': [3, 6, 7, 8]},
            'walledcities': {'survive': [2, 3, 4, 5], 'born': [4, 5, 6, 7, 8]},
        }
        self.init_time = time()
        self.name = name
        self.rule_set = RULE_SETS[self.name]
        self.rule_survive = np.array(self.rule_set['survive'], np.int8)
        self.rule_born = np.array(self.rule_set['born'], np.int8)
        self.run_ticks = 0
    
    def apply_rules(self, cell):
        if cell.cell_logic.alive:
            if cell.neighborhood_sum not in self.rule_survive:
                cell.toggle_cell(False) #kill cell
        else:
            if cell.neighborhood_sum in self.rule_born:
                cell.toggle_cell(True) #revive cell

    def add_tick(self):
        self.run_ticks += 1

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def __str__(self):
        return f'{self.name}'


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
        os.mkdir(f'./{self.screenshot_dir}/')
        os.chdir(f'./{self.screenshot_dir}/')

    @property
    def step_counter(self):
        return self.grid.rule_set.run_ticks

    def screen_shot(self):
        filename = f'{self.main_dir}/{self.screenshot_dir}/shot_{self.shot_counter}.png'
        pygame.image.save(self.main_window, filename)
        self.shot_counter += 1

    def state_shot(self):
        #capture cell active states as b&w png
        filename = f'step_{self.step_counter}.png'
        states = np.array(self.grid.current_states, dtype=np.int8) * 255
        cv2.imwrite(filename, states)

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
        edges = cv2.Canny(resized, 100, 250, L2gradient=True)

        for column in range(self.grid.num_columns):
            for row in range(self.grid.num_rows):
                self.grid.cells[column][row].set_color(resized[row, column])
                if edges[row, column]: #activate cells corresponding to edges mask
                    self.grid.cells[column][row].toggle_cell(1)
                else:
                    self.grid.cells[column][row].toggle_cell(0)
        self.grid.manual_update_states()

    def save_image(self):
        filename = f'{self.main_dir}/{self.screenshot_dir}/image_{self.shot_counter}.png'

        save_states = self.grid.current_states.copy()
        all_on = np.full_like(save_states, 1)
        self.grid.current_states = all_on

        for cell_col in self.grid.cells:
            for cell in cell_col:
                cell.cell_visual.surface.fill(cell.cell_visual.color)
                cell.cell_visual.draw()
        pygame.image.save(self.main_window, filename)

        self.grid.current_states = save_states
