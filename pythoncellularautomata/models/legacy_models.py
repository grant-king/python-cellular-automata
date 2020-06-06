import numpy as np
import random
import pygame

class CellContainer:
    def __init__(self, grid):
        self.grid = grid
        self.cells = []
        self.build_cells()

    def update_grid(self):
        for col_idx, cell_col in enumerate(self.cells):
            for row_idx, cell in enumerate(cell_col):
                # todo if first or last, wrap from edge
                if row_idx == 0 or row_idx == self.grid.num_rows or col_idx == 0 or col_idx == self.grid.num_columns:
                    pass    
                else:
                    neighborhood = self.grid.get_neighborhood(row_idx, col_idx) #slice neighborhood, not including self
                    cell.cell_logic.update(neighborhood) #get, set neighboorhood sum for cell
                cell.cell_visual.update(self.grid.aging) #alter colors of cell according to aging method, update cell visual to pygame frame buffer
                self.grid.rule_set.apply_rules(cell) #toggle cell according to rules, to be applied on next run though
                self.grid.next_states[row_idx, col_idx] = cell.cell_logic.alive #update cell state in updates array to be copied to working array on the next run
    
    def manual_update_states(self):
        #capture 2d bool array of current states
        for column in range(self.num_columns):
            for row in range(self.num_rows):
                #self.next_states[row, column] = self.cells[column][row].cell_logic.alive
                self.current_states[row, column] = self.cells[column][row].cell_logic.alive

    def build_cells(self):
        self.cells = [[0 for row in range(self.grid.num_rows)] for column in range(self.grid.num_columns)]
        for col_idx in range(self.grid.num_columns):
            for row_idx in range(self.grid.num_rows):
                self.cells[col_idx][row_idx] = Cell(self.grid.CELL_SIZE, col_idx, row_idx)


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

