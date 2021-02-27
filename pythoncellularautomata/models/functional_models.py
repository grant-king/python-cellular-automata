import numpy as np
from .ruleset_models import Ruleset
from numba import cuda, types
import math, time
import os
import logging

class ShotTool:
    def __init__(self, grid):
        """Sequential methods for operating on state shots"""
        self.grid = grid
    
    def age_colors(self, color_channels, current_states, states_histories, color_headings):
        """get new colors by running each channel through age_channel_[...] ShotTool method"""
        new_channels = []
        
        #reshape to (3, rows, columns)
        headings = np.moveaxis(color_headings, -1, 0)
        for idx, channel in enumerate(np.moveaxis(color_channels, -1, 0)):
            new_channels.append(self.age_channel(channel, current_states, states_histories, headings[idx]))
        new_colors = np.array([item[0] for item in new_channels])
        new_headings = np.array([item[1] for item in new_channels])

        return np.moveaxis(new_colors, 0, -1), np.moveaxis(new_headings, 0, -1)

    def age_channel(self, input_channel, states, states_histories, channel_headings):
        """increment or decrement each element in input for similar 
        output based on states"""
        color_vals = input_channel.flatten()
        headings = channel_headings.flatten()
        output = np.full_like(color_vals, 128)
        flatter_history = states_histories.reshape(-1, states_histories.shape[-1])

        for idx, state in enumerate(states.flatten()):
            if color_vals[idx] > 250:
                headings[idx] = 0
            elif color_vals[idx] < 20:
                headings[idx] = 1
            else:
                pass

            if state:
                output[idx] = self.age_color(color_vals[idx], flatter_history[idx, :], headings[idx])
            else:
                output[idx] = color_vals[idx]
        return np.reshape(output, input_channel.shape), np.reshape(headings, channel_headings.shape)

    def age_color(self, current_color_value, current_cell_history, current_color_heading):
        """return new color value within limits"""
        #change color value
        if current_cell_history[-1]: #if alive
            if current_color_heading: 
                return current_color_value + (current_cell_history.mean() / 2)
            else:
                return current_color_value - (current_cell_history.mean() / 2)
        else: #cell is off
            return current_color_value

    def calculate_next(self, state_shot):
        """calculate next state frame, one cell at a time"""
        next_state_shot = np.zeros_like(state_shot)
        shape = state_shot.shape
        for col_idx in range(1, shape[1] - 1):
            for row_idx in range(1, shape[0] - 1): #clip edges
                rows = (row_idx - 1, row_idx + 2)
                cols = (col_idx - 1, col_idx + 2)
                neighborhood = state_shot[rows[0]:rows[1], cols[0]:cols[1]].copy()
                neighborhood[1, 1] = 0 #don't count center
                state = state_shot[row_idx, col_idx]
                new_state = self.grid.rule_set.get_next_state(state, neighborhood.sum())
                next_state_shot[row_idx, col_idx] = new_state
        
        return next_state_shot


class ShotToolCUDA:
    """CUDA parallel processing methods for operating on state shots"""
    def __init__(self, grid):
        """methods for operating on state shots, represented as 
        2d grids of binary or 8-bit values"""
        self.grid = grid
    
    def age_colors(self, color_channels, current_states, states_histories, color_headings):
        """get new colors by running each channel through age_channel_[...] ShotTool method"""
        new_channels = []
        states_histories = np.ascontiguousarray(states_histories)
        #reshape to (3, rows, columns)
        headings = np.moveaxis(color_headings, -1, 0)
        for idx, channel in enumerate(np.moveaxis(color_channels, -1, 0)):
            new_channels.append(self.age_channel(channel, current_states, states_histories, np.ascontiguousarray(headings[idx])))
        new_colors = np.array([item[0] for item in new_channels])
        new_headings = np.array([item[1] for item in new_channels])

        return np.moveaxis(new_colors, 0, -1), np.moveaxis(new_headings, 0, -1)

    def age_channel(self, input_channel, state_shot, states_histories, channel_headings):
        """increment or decrement each element in input for similar 
        output based on states"""
        blockdim = (16, 16)
        griddim = (state_shot.shape[0] // blockdim[0] + 1, state_shot.shape[1] // blockdim[1] + 1)

        color_vals = np.array(input_channel, dtype=np.float32)
        next_vals = np.zeros_like(color_vals)

        #create copies of the array on device memory
        d_color_vals = cuda.to_device(color_vals)
        d_state_shot = cuda.to_device(state_shot)
        d_states_histories = cuda.to_device(states_histories)
        d_next_vals = cuda.to_device(next_vals)
        d_color_headings = cuda.to_device(channel_headings)

        #launch kernels
        get_next_color_vals[griddim, blockdim](d_color_vals, d_state_shot, d_states_histories, d_next_vals, d_color_headings)

        #copy output back to host
        output = d_next_vals.copy_to_host(), d_color_headings.copy_to_host()
        return output
    
    def calculate_next(self, state_shot):
        """calculate next state frame in parallel"""
        blockdim = (32, 32)
        griddim = (state_shot.shape[0] // blockdim[0] + 1, state_shot.shape[1] // blockdim[1] + 1)

        survive = np.array(self.grid.rule_set.rule_survive, dtype=np.uint8)
        born = np.array(self.grid.rule_set.rule_born, dtype=np.uint8)

        neighborhoods = np.zeros_like(state_shot, dtype=np.uint8)
        next_shot = np.zeros_like(state_shot)

        #copy to device memory
        d_state_shot = cuda.to_device(state_shot)
        d_neighborhoods = cuda.to_device(neighborhoods)
        d_next_shot = cuda.to_device(next_shot)
        d_survive = cuda.to_device(survive)
        d_born = cuda.to_device(born)

        #lauch kernels 
        get_neighborhood_sums[griddim, blockdim](d_state_shot, d_neighborhoods)
        get_next_shot[griddim, blockdim](d_state_shot, d_neighborhoods, d_next_shot, d_survive, d_born)

        output = d_next_shot.copy_to_host()
        return output

@cuda.jit
def get_neighborhood_sums(state_shot, neighborhoods_output):
    thready, threadx = cuda.grid(2)
    stridey, stridex = cuda.gridsize(2)
    neighborhood = cuda.local.array((3,3), dtype=types.boolean)

    for idx in range(threadx, state_shot.shape[0] - 1, stridex):
        for idy in range(thready, state_shot.shape[1] - 1, stridey):        
            neighborhood = state_shot[idx - 1:idx + 2, idy - 1:idy + 2]

            nh_sum = 0
            for row in range(3):
                for col in range(3):
                    if not (row == 1 and col == 1): #don't count self state at center
                        nh_sum += neighborhood[col][row]
            
            neighborhoods_output[idx][idy] = nh_sum

@cuda.jit
def get_next_shot(state_shot, neighborhoods, output_shot, rules_survive, rules_born):
    """use neighborhood sum, state, and rules arrays to determine next state
    for given cell/thread location"""
    thready, threadx = cuda.grid(2)
    stridey, stridex = cuda.gridsize(2)

    for idx in range(threadx, state_shot.shape[0], stridex):
        for idy in range(thready, state_shot.shape[1], stridey):
            current_state = state_shot[idx][idy]
            nh_sum = neighborhoods[idx][idy]

            #check if nh_sum is in rules
            found = False
            if current_state: #if current state is on
                for item in rules_survive:
                    if item == nh_sum: #if nh_sum found in rules
                        found = True
            else: #current state is off
                for item in rules_born:
                    if item == nh_sum: 
                        found = True
            
            #set next state accordingly                
            if found:#if nh_sum found in rules
                output_shot[idx][idy] = 1
            else:
                output_shot[idx][idy] = 0
            
@cuda.jit
def get_next_color_vals(current_vals, state_shot, states_histories, next_vals, color_headings):
    thready, threadx = cuda.grid(2)
    stridey, stridex = cuda.gridsize(2)

    for idx in range(threadx, current_vals.shape[0], stridex):
        for idy in range(thready, current_vals.shape[1], stridey):
            current_color_value = current_vals[idx][idy]
            current_color_heading = color_headings[idx][idy]
            state = state_shot[idx][idy]
            
            #set color heading and limit changing color value range
            if current_color_value > 240:
                color_headings[idx][idy] = 0
            elif current_color_value < 20:
                color_headings[idx][idy] = 1
            else:
                pass
            #operate on cell if active
            if state:
                #calculate cell histories average
                cell_history_mean = 0
                for item in states_histories[idx][idy]:
                    cell_history_mean += item
                cell_history_mean = cell_history_mean / 10
                #change color value
                if current_color_heading: 
                    next_vals[idx][idy] = current_color_value + cell_history_mean / 2
                else:
                    next_vals[idx][idy] = current_color_value - cell_history_mean / 2
            else: #cell is off
                next_vals[idx][idy] = current_color_value

            
