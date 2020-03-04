import time
import logging

class PerformanceMonitor:
    def __init__(self, grid):
        self.timer = Timer()
        self.grid = grid
        self.total_frames = 0
        self.total_cells = grid.total_cells

    @property
    def tick_total(self):
        return self.grid.rule_set.run_ticks

    def current_fps(self):
        pass
    
    @property
    def average_fps(self):
        return self.tick_total // self.timer.elapsed()

    def rolling_average_fps(self):
        pass

    def fppps(self):
        #frames per pixel per second, higher is better
        pass

    def ppfps(self):
        #total pixels per frame per second, lower is better
        pass

    def update(self):
        #make a log entry summarizing performance since last log
        print(f'Simulation running at {self.average_fps} frames per second on average.')
        

class Timer:
    def __init__(self):
        self.start_time = time.perf_counter()

    def elapsed(self):
        return time.perf_counter() - self.start_time

