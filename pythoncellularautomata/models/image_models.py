import numpy as np

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

    def calculate_next_sequential(self, state_shot):
        """
        calculate next state frame, one cell at a time
        """
        next_state_shot = np.zeros_like(state_shot)
        shape = state_shot.shape
        for col_idx in range(1, shape[1] - 1):
            for row_idx in range(1, shape[0] - 1): #clip edges
                rows = (row_idx - 1, row_idx + 1)
                cols = (col_idx - 1, col_idx + 1)
                neighborhood = state_shot[rows[0]:rows[1], cols[0]:cols[1]]
                state = state_shot[row_idx, col_idx]
                new_state = self.ruleset.apply_rules(state, neighborhood)
                next_state_shot[row_idx, col_idx] = new_state
        
        return next_state_shot

    def calculate_next_parallel(self, state_shot, next_state_shot):
        """
        calculate next state frame in parallel with CUDA 
        """
        pass


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
        self.name = name
        self.rule_set = RULE_SETS[self.name]
        self.rule_survive = np.array(self.rule_set['survive'], np.int8)
        self.rule_born = np.array(self.rule_set['born'], np.int8)
        self.run_ticks = 0

    def apply_rules(self, state, neighborhood):
        """use current state and cell neighborhood sum to determine next state"""
        new_state = False
        if state:#if current state is on
            if neighborhood not in self.rule_survive:
                return False #kill cell
            else:#neighborhood says survive
                return True #cell stays on
        else:#if current state is off
            if neighborhood in self.rule_born:
                return True #activate cell
            else: #neighborhood says no birth
                return False #cell remains off

    def add_tick(self):
        self.run_ticks += 1

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def __str__(self):
        return f'{self.name}'

