import pygame
import random
import os
import numpy as np
import cv2
import logging
from time import time, ctime
from models.performance_monitor import PerformanceMonitor
from models.ca_models2 import Control, StepClock, StepTimer, Capture
from models.image_models import ShotTool, ShotToolCUDA
from models.ruleset_models import Ruleset

class Grid:
    def __init__(self, cell_size, rule_name, aging=False, processing_mode=2):
        self.SCREEN_SIZE = pygame.display.get_surface().get_size()
        self.CELL_SIZE = cell_size
        self.aging = aging
        self.processing_mode = processing_mode

        self.cells = []
        self.total_cells = 0
        self.num_columns = self.SCREEN_SIZE[0] // self.CELL_SIZE
        self.num_rows = self.SCREEN_SIZE[1] // self.CELL_SIZE
        self.image_size = (self.num_columns * self.CELL_SIZE, self.num_rows * self.CELL_SIZE)

        self.current_states = np.zeros((self.num_rows, self.num_columns), dtype=np.bool)
        self.next_states = np.zeros((self.num_rows, self.num_columns), dtype=np.bool)
        self.color_channels = np.zeros((self.num_rows, self.num_columns, 3), dtype=np.float32) #store current color info
        self.cells_history = np.zeros((self.num_rows, self.num_columns, 10), dtype=np.bool)
        self.rule_set = Ruleset(rule_name)
        self.set_pm_settings()
        self.build_cells()

        print(f'Grid initialized with {self.rule_set.name} rule at {ctime()} with {self.total_cells} cells')
        print(f'Using processing mode {self.processing_mode}')

    def set_pm_settings(self):
        if self.processing_mode == 1:
            self.st = ShotTool(self)
            self.grid_update_method = self.update_grid_II
        elif self.processing_mode == 2:
            self.st = ShotToolCUDA(self)
            self.grid_update_method = self.update_grid_II
        elif self.processing_mode == 0:
            self.grid_update_method = self.update_grid

    def switch_channels(self):
        """Switch red and blue color channels for proper coloring with update_grid_II 
        """
        intensity_channels = np.moveaxis(self.color_channels, -1, 0) #move axis for easy reordering
        reordered_intensity_channels = [intensity_channels[2], intensity_channels[1], intensity_channels[0]]
        self.color_channels = np.moveaxis(np.array((reordered_intensity_channels), dtype=np.float32), 0, -1) #return to standard image index format; rows, columns, channels

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
        self.grid_update_method()
        self.update_current_states()
        self.rule_set.add_tick()
        self.update_window()

    def update_current_states(self):
        self.cells_history = np.dstack((self.cells_history, self.current_states))[:, :, 1:] #add states to end of history queue, advance
        self.current_states = self.next_states.copy()

    def update_grid_II(self):
        """update grid with Shot array methods
        """
        self.next_states = self.st.calculate_next(self.current_states)
        if self.aging:
            self.color_channels = self.st.age_colors(self.color_channels, self.current_states, self.cells_history)

    def update_window(self):
        image_surface = self.get_state_surface() 
        main_window = pygame.display.get_surface()
        main_window.blit(image_surface, main_window.get_rect())
        pygame.display.set_caption(f'{self.rule_set.name} step {self.rule_set.run_ticks}')
        pygame.display.flip()

    def get_state_surface(self):
        """create image surface from current states, update to main window"""
        colored_states = np.moveaxis(self.color_channels, -1, 0) * self.current_states #make compatible for broadcast
        colored_states = colored_states + (255 - (np.moveaxis(self.color_channels, -1, 0)) * np.invert(self.current_states)) #add inverse colors for off cells
        colored_states = [cv2.resize(channel, self.image_size, interpolation=cv2.INTER_NEAREST).T for channel in colored_states] #resize, rotate each channel
        state_image = np.moveaxis(np.array((colored_states), dtype=np.int8), 0, -1) #return to standard image index format; rows, columns, channels
        state_image = pygame.pixelcopy.make_surface(state_image)
        return state_image

    def get_neighborhood(self, row_idx, col_idx):
        #copy neighborhood surrounding cell location
        neighborhood = self.current_states[row_idx-1:row_idx+2, col_idx-1:col_idx+2].copy()
        neighborhood[1, 1] = 0
        return neighborhood

    def all_on_visual_only(self):
        pass           

    def manual_update_states(self):
        #capture 2d bool array of current states
        for column in range(self.num_columns):
            for row in range(self.num_rows):
                #self.next_states[row, column] = self.cells[column][row].cell_logic.alive
                self.current_states[row, column] = self.cells[column][row].cell_logic.alive

    def set_rules(self, name):
        #logging.info(f'Ending ruleset: {self.rule_set} after {self.rule_set.run_ticks} ticks')
        print(f'Ending ruleset: {self.rule_set} after {self.rule_set.run_ticks} ticks')
        self.rule_set = Ruleset(name)
        #logging.info(f'Starting ruleset: {self.rule_set}')
        print((f'Starting ruleset: {self.rule_set}'))
    
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
                self.next_states[row_idx, col_idx] = cell.cell_logic.alive #update cell state in updates array to be copied to working array on the next run


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

