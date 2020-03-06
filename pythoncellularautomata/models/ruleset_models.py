import numpy as np
from time import time

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
    
    def get_next_state(self, state, neighborhood_sum):
        """use current state and cell neighborhood sum to determine next state"""
        if state:#if current state is on
            if neighborhood_sum in self.rule_survive:
                return True #cell survives
            else:#sum not found in survival rules
                return False #cell dies
        else:#if current state is off
            if neighborhood_sum in self.rule_born:
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

