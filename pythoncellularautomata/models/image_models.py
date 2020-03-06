import numpy as np
from models.ruleset_models import Ruleset

class ShotTool:
    def __init__(self, rule_set):
        """methods for operating on state shots, represented as 
        2d grids of binary or 8-bit values"""
        self.rule_set = rule_set
        self.shot_history = [] #last 20 images processed

    def age_colors(self, color_channels, current_states):
        """get new colors by running each channel through age_channel_[...] ShotTool method"""
        new_channels = []
        for channel in np.moveaxis(color_channels, -1, 0):
            new_channels.append(self.age_channel_sequential(channel, current_states))
        new_channels = np.array(new_channels)
        return np.moveaxis(new_channels, 0, -1)

    def age_channel_sequential(self, input_channel, states):
        """increment or decrement each element in input for similar 
        output based on states"""
        color_vals = input_channel.flatten()
        output = np.empty_like(color_vals)
        for idx, state in enumerate(states.flatten()):
            if state:
                output[idx] = self.age_color(color_vals[idx])
        return np.reshape(output, input_channel.shape)

    def age_color(self, current_color_value):
        """return new color value within limits"""
        if current_color_value > 250:
            return 40
        else:
            return current_color_value + 1

    def calculate_next_sequential(self, state_shot):
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
                new_state = self.rule_set.get_next_state(state, neighborhood.sum())
                next_state_shot[row_idx, col_idx] = new_state
        
        return next_state_shot


class ShotToolCUDA:
    """CUDA parallel processing methods for operating on state shots"""
    def __init__(self):
        pass
    
    def age_channel(self, input_channel, states):
        pass

    def age_color(self, current_color_value):
        pass 

    def calculate_next(self, state_shot):
        """calculate next state frame in parallel with CUDA """
        pass

