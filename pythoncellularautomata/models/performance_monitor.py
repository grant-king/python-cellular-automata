import time

class PerformanceMonitor:
    def __init__(self, pixel_count):
        self.timer = Timer()
        self.total_frames = 0
        self.total_pixels = pixel_count

    def current_fps(self):
        pass

    def average_fps(self):
        pass

    def fppps(self):
        #frames per pixel per second, higher is better
        pass

    def ppfps(self):
        #total pixels per frame per second, lower is better
        pass

    def add_frames(self, add_num):
        #add add_num to total_frmaes
        self.total_frames += add_num
        

class Timer:
    def __init__(self):
        self.start_time = time.perf_counter()

    def elapsed(self):
        return time.perf_counter() - self.start_time

