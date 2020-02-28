class Shot:
    def __init__(self):
        """methods for operating on 2d grids of values"""
        pass

    def age_channel_sequential(self, input_channel, output_channel, state_shot):
        """increment or decrement each element in input for output based on states"""
        pass

    def calculate_next_sequential(self, state_shot, next_state_shot):
        """
        calculate next state frame, one cell at a time
        """
        pass

    def calculate_next_parallel(self, state_shot, next_state_shot):
        """
        calculate next state frame in parallel with CUDA 
        """
        pass