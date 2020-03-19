import time

class PerformanceMonitor:
    def __init__(self, grid):
        self.timer = Timer()
        self.grid = grid
        self.total_frames = 0
        self.total_cells = grid.total_cells
        self.log_file = '../performance.txt'
        self.report = f'Grid initialized with {self.grid.rule_set.name} rule at {time.ctime()} with {self.grid.total_cells} cells\nUsing processing mode {self.grid.processing_mode}\n'

    @property
    def tick_total(self):
        return self.grid.rule_set.run_ticks

    @property
    def average_fps(self):
        return self.tick_total / self.timer.elapsed()

    @property
    def average_fppps(self):
        #average frames per pixel per second, higher is better
        return self.average_fps / self.grid.total_cells

    def update(self):
        #make a log entry summarizing performance since last log
        av_fps = self.average_fps
        av_fppps = self.average_fppps
        message = f'Simulation running at an average {av_fps:.4} frames per second'
        print(message)
        self.add_to_report(message)

    def add_to_report(self, string):
        self.report += string + '\n'

    def write_report(self):
        with open(self.log_file, 'a') as f:
            f.write(self.report)
        print('Performance logged')
        self.report = ''

class Timer:
    def __init__(self):
        self.start_time = time.perf_counter()

    def elapsed(self):
        return time.perf_counter() - self.start_time

