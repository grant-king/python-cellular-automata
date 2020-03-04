import pygame
import random
import os
import numpy as np
import cv2
import logging
from time import time, ctime
from models.performance_monitor import PerformanceMonitor
from models.ca_models2 import Control, StepClock, StepTimer, Capture
from models.image_models import ShotTool

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
        self.color_channels = np.zeros((3, self.num_rows, self.num_columns)) #store current color info
        self.rule_set = Ruleset(rule_name)
        self.st = ShotTool()
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
        #self.update_grid()
        self.update_grid_II()
        self.update_current_states()
        self.rule_set.add_tick()

    def update_grid(self):
        for col_idx, cell_col in enumerate(self.cells):
            for row_idx, cell in enumerate(cell_col):
                # todo if first or last, wrap from edge
                if row_idx == 0 or row_idx == self.num_rows or col_idx == 0 or col_idx == self.num_columns:
                    pass    
                else:
                    neighborhood = self.get_neighborhood(row_idx, col_idx) #slice neighborhood, not including self
                    cell.cell_logic.update(neighborhood) #get, set neighboorhood sum for cell
                cell.cell_visual.update(self.aging) #alter colors of cell according to aging method, update cell visual to pygame frame buffer
                self.rule_set.apply_rules(cell) #toggle cell according to rules, to be applied on next run though
                self.current_states_updates[row_idx, col_idx] = cell.cell_logic.alive #update cell state in updates array to be copied to working array on the next run

    def update_grid_II(self):
        """update grid with Shot array methods
        """
        self.current_states_updates = self.st.calculate_next_sequential(self.current_states)
        #self.age_colors()
        self.update_window()

    def update_window(self):
        #create image surface from current states, update to main window
        state_image = np.ones_like(self.current_states, dtype=np.int8) * self.current_states * 255
        new_size = tuple(np.array(state_image.shape) * 5)
        state_image = np.transpose(state_image)
        image_surface = pygame.pixelcopy.make_surface(cv2.resize(state_image, new_size, interpolation=cv2.INTER_NEAREST))
        #image_surface = pygame.pixelcopy.make_surface(state_image)
        main_window = pygame.display.get_surface()
        main_window.blit(image_surface, main_window.get_rect())
    
    def age_colors(self):
        """get new colors by running each channel through age_channel_[...] ShotTool method
        """
        for channel in self.color_channels:
            channel = self.st.age_channel_sequential(channel, self.current_states) #operate on, return altered channel

    def refresh_cells(self, state_image):
        """
        update each cell according to corresponding pixel location on 
        the input image.
        """
        for col_idx, cell_col in enumerate(self.cells):
            for row_idx, cell in enumerate(cell_col):
                cell.cell_logic.alive = state_image[row_idx, col_idx]

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
                #self.current_states_updates[row, column] = self.cells[column][row].cell_logic.alive
                self.current_states[row, column] = self.cells[column][row].cell_logic.alive

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
        """change colors if aging. Render final cell, draw to frame buffer.
        """
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
        """toggle cell state depending on current living state and rule set setting
        """
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

