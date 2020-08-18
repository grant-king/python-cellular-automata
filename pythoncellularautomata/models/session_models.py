from models.ca_models import Grid, Capture, Control
import pygame
from pygame.locals import QUIT

class SessionConfigurationManager:
    def __init__(self):
        #todo if base config exists, load settings
        #todo else make new base config
        self.settings_dict = {}

    def play_config(self):
        pass

    def play_default(self):
        """Start default simulation from configuration file"""
        #todo if default sim doesn't exist, create new one
        if os.path.isfile('default_simulation_settings.conf'):
            #todo load settings
            #todo play settings
            pass
        else:
            self.make_base()

    def make_new(self, name):
        """interactively create new named automaton config"""
        if os.path.isfile(f'{name}.conf'):
            print(f'There is already a configuration called {name}. Please choose a new name for this configuraiton.')
            #todo call to whatever takes name input to recall this method
        else:
            print(f'You are about to create a new simulation configuration named {name}.conf')
            self.input_settings()
            
    def input_settings(self):
        self.settings_dict['screen_size'] = input("type maximum screen size as width, height: ")
        self.settings_dict['cell_size'] = input("how many pixels square do you want the cells to be? ")
        self.settings_dict['initial_ruleset'] = input("What ruleset do you want to start with? ")
        self.settings_dict['show_colors'] = input("Do you want to show colors? 1 or 0: ")
        self.settings_dict['aging'] = input('Do you want cell aging on? 1 or 0: ')
        self.settings_dict['processing_mode'] = input('Do you have a CUDA-enabled GPU? 1 or 0: ')

    def make_base(self):
        """create new base configuration"""
        print('This will create a new base configuration to be run by default.')
        self.make_new('default_simulation_settings')


class SessionConfiguration:
    def __init__(self, screen_size, cell_size, ruleset_name, 
    aging=1, processing_mode=2,  show_colors=1, seed_file_path=None):
        self.screen_size = screen_size
        self.cell_size = cell_size
        self.ruleset_name = ruleset_name
        self.aging = aging
        self.processing_mode = processing_mode
        self.show_colors = show_colors
        self.seed_file_path = seed_file_path


class CellularAutomatonSession:
    def __init__(self, session_config):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.main_window = pygame.display.set_mode(session_config.screen_size)
        self.grid = Grid(
            session_config.cell_size, session_config.ruleset_name, 
            aging=session_config.aging, 
            processing_mode=session_config.processing_mode,
            show_colors=session_config.show_colors
            )
        self.control = Control(self.grid)

        if session_config.seed_file_path is None:
            self.grid.random_seed(0.05)
        else:
            self.control.capture.load_image(session_config.seed_file_path)

        self.run_sim()
        
    def run_sim(self):
        while self.control.running:
            self.clock.tick(self.control.fps)
            self.grid.update()

        pygame.quit()
