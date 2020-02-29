from models.ca_models import Ruleset

class ShotTool:
    def __init__(self):
        """methods for operating on state shots, represented as 
        2d grids of binary or 8-bit values"""
        self.ruleset = Ruleset('conway')
        self.shot_history = [] #last 20 images processed

    def age_channel_sequential(self, input_channel, states):
        """increment or decrement each element in input for similar 
        output based on states"""
        color_vals = input_channel.flatten()
        output = np.empty_like(color_vals)
        for idx, state in enumerate(states.flatten()):
            if state:
                output[idx] = self.age_color(color_vals[idx])
        return output

    def age_color(self, current_color_value):
        """return new color value within limits"""
        if current_color_value > 250:
            return 20
        else:
            return current_color_value + 1

    def calculate_next_sequential(self, state_shot, next_state_shot):
        """
        calculate next state frame, one cell at a time
        """
        shape = state_shot.shape
        for col_idx in range(1, shape[1] - 1):
            for row_idx in range(1, shape[0] - 1): #clip edges
                rows = (row_idx - 1, row_idx + 1)
                cols = (col_idx - 1, col_idx + 1)
                neighborhood = state_shot[rows[0]:rows[1], cols[0]:cols[1]]
                state = state_shot[row_idx, col_idx]
                new_state = self.apply_rules(state, neighborhood)
                next_state_shot[row_idx, col_idx] = new_state
        
        return next_state_shot

    def calculate_next_parallel(self, state_shot, next_state_shot):
        """
        calculate next state frame in parallel with CUDA 
        """
        pass

    def apply_rules(self, state, neighborhood):
        """use current state and cell neighborhood sum to determine next state"""
        return state
