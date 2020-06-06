import pygame
import random
import os
import numpy as np
import cv2
import logging
from time import time, ctime
from models.performance_monitor import PerformanceMonitor
from models.ca_models2 import Control, StepClock, StepTimer, Capture
from models.functional_models import ShotTool, ShotToolCUDA
from models.ruleset_models import Ruleset
from models.legacy_models import CellContainer

class Grid:
    def __init__(self, cell_size, rule_name, aging=False, processing_mode=2, show_colors=False, show_inverse=False):
        #set grid settings
        self.SCREEN_SIZE = pygame.display.get_surface().get_size() #width, height
        self.CELL_SIZE = cell_size
        self.aging = aging
        self.processing_mode = processing_mode
        self.show_inverse = show_inverse
        self.show_colors = show_colors

        self.num_columns = self.SCREEN_SIZE[0] // self.CELL_SIZE
        self.num_rows = self.SCREEN_SIZE[1] // self.CELL_SIZE
        self.total_cells = self.num_rows * self.num_columns
        self.image_size = (self.num_columns * self.CELL_SIZE, self.num_rows * self.CELL_SIZE) #width, height

        self.current_states = np.zeros((self.num_rows, self.num_columns), dtype=np.bool)
        self.next_states = np.zeros((self.num_rows, self.num_columns), dtype=np.bool)
        self.color_channels = np.random.uniform(low=100, high=155, size=(self.num_rows, self.num_columns, 3))
        self.cells_history = np.zeros((self.num_rows, self.num_columns, 10), dtype=np.bool)
        self.color_headings = np.ones((self.num_rows, self.num_columns, 3), dtype=np.bool) #is the color going forwards or backwards?
        self.rule_set = Ruleset(rule_name)
        self.set_pm_settings()
        

        print(f'Grid initialized with {self.rule_set.name} rule at {ctime()} with {self.total_cells} cells')
        print(f'Using processing mode {self.processing_mode}')

    def set_pm_settings(self):
        if self.processing_mode == 1:
            self.st = ShotTool(self)
            self.grid_update_method = self.update_grid
        elif self.processing_mode == 2:
            self.st = ShotToolCUDA(self)
            self.grid_update_method = self.update_grid
        elif self.processing_mode == 0:
            self.legacy_cells_object = CellContainer(self)
            self.grid_update_method = self.legacy_cells_object.update_grid

    def switch_channels(self):
        """Switch red and blue color channels for proper coloring with update_grid_II 
        """
        intensity_channels = np.moveaxis(self.color_channels, -1, 0) #move axis for easy reordering
        reordered_intensity_channels = [intensity_channels[2], intensity_channels[1], intensity_channels[0]]
        self.color_channels = np.moveaxis(np.array((reordered_intensity_channels), dtype=np.float32), 0, -1) #return to standard image index format; rows, columns, channels

    def random_seed(self, living_ratio=0.3):
        self.current_states = np.random.rand(self.num_rows, self.num_columns) < living_ratio

    def update(self):
        self.grid_update_method()
        self.update_current_states()
        self.rule_set.add_tick()
        self.update_window()

    def update_current_states(self):
        self.cells_history = np.dstack((self.cells_history, self.current_states))[:, :, 1:] #add states to end of history queue, advance
        self.current_states = self.next_states.copy()

    def update_grid(self):
        """update grid with Shot array methods
        """
        self.next_states = self.st.calculate_next(self.current_states)
        if self.aging:
            self.color_channels, self.color_headings = self.st.age_colors(self.color_channels, self.current_states, self.cells_history, self.color_headings)

    def update_window(self):
        image_surface = self.get_state_surface() 
        main_window = pygame.display.get_surface()
        main_window.blit(image_surface, main_window.get_rect())
        pygame.display.set_caption(f'{self.rule_set.name} step {self.rule_set.run_ticks}')
        pygame.display.flip()

    def get_state_surface(self):
        """create image surface from current states, update to main window"""
        colored_states = np.moveaxis(self.color_channels, -1, 0) * self.current_states #make compatible for broadcast
        
        if self.show_inverse:
            colored_states = colored_states + (255 - (np.moveaxis(self.color_channels, -1, 0)) * np.invert(self.current_states)) #add inverse colors for off cells
        if self.show_colors:
            colored_states = [cv2.resize(channel, self.image_size, interpolation=cv2.INTER_NEAREST).T for channel in colored_states] #resize, rotate each channel
            state_image = np.moveaxis(np.array((colored_states), dtype=np.int8), 0, -1) #return to standard image index format; rows, columns, channels
        else:
            state_image = cv2.resize(np.array(self.current_states * 255, dtype=np.uint8), self.image_size, interpolation=cv2.INTER_NEAREST).T
        
        state_image = pygame.pixelcopy.make_surface(state_image)
        return state_image

    def get_neighborhood(self, row_idx, col_idx):
        #copy neighborhood surrounding cell location
        neighborhood = self.current_states[row_idx-1:row_idx+2, col_idx-1:col_idx+2].copy()
        neighborhood[1, 1] = 0
        return neighborhood        

    def set_rules(self, name):
        print(f'Ending ruleset: {self.rule_set} after {self.rule_set.run_ticks} ticks')
        self.rule_set = Ruleset(name)
        print((f'Starting ruleset: {self.rule_set}'))        

