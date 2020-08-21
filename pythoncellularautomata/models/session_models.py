import configparser
import os
from .ca_models import Grid, Capture, Control
import pygame
from pygame.locals import QUIT

class SessionConfigurationManager:
    def __init__(self):
        self.base_dir = os.getcwd()        
        self.input_dict = {}
        self.config_dict = {}

    def input_config_name(self):
        load_name = input('Type the session config name you want to load: ')
        if os.path.isfile(os.path.join(self.base_dir, f'{load_name}.conf')):
            self.current_session = self.start_config(os.path.join(self.base_dir, f'{load_name}.conf'))

    def start_config(self, config_filename):
        """start session from config name and return session object"""        
        self.load_config_settings(config_filename)
        session = CellularAutomatonSession(self.get_session_config())
        return session

    def load_config_settings(self, config_filename):
        config = configparser.ConfigParser()
        config.read(config_filename)
        self.config_dict = config['SESSION_SETUP']

    def get_session_config(self):
        """create and return new SessionConfiguration object from 
        variables held in config_dict that can be used for making a new 
        session"""
        session_config = SessionConfiguration(
            list(map(int, self.config_dict['screen_size'].split(','))),
            int(self.config_dict['cell_size']),
            self.config_dict['initial_ruleset'],
            aging=int(self.config_dict['aging']),
            processing_mode=int(self.config_dict['processing_mode']),
            show_colors=int(self.config_dict['show_colors']),
            seed_image_path=self.config_dict['seed_image_path']
        )
        return session_config

    def play_default(self):
        """Start default simulation from configuration file"""
        #if default sim doesn't exist, create new one
        if os.path.isfile('default_simulation_settings.conf'):
            self.current_session = self.start_config('default_simulation_settings.conf')
        else:
            self.make_base()
            self.current_session = self.start_config('default_simulation_settings.conf')

    def make_new(self, new_name=None):
        """interactively create new named automaton config"""
        if new_name == None:
            self.input_dict['name'] = input('Type a new name for this config: ')
        else:
            self.input_dict['name'] = new_name

        if os.path.isfile(f"{self.input_dict['name']}.conf"):
            print(f"There is already a configuration called {self.input_dict['name']}. Please choose a new name for this configuraiton.")
            self.make_new()
        else:
            print(f"You are about to create a new simulation configuration named {self.input_dict['name']}.conf")
            self.input_settings()
            self.save_config()
            
    def input_settings(self):
        self.input_dict['screen_size'] = input("type maximum screen size as width, height: ")
        self.input_dict['cell_size'] = input("how many pixels square do you want the cells to be? ")
        self.input_dict['initial_ruleset'] = input("What ruleset do you want to start with? ")
        self.input_dict['aging'] = input('Do you want cell aging on? 1 or 0: ')
        self.input_dict['processing_mode'] = input('Select processing mode 1 (CPU) or 2 (CUDA): ')
        self.input_dict['show_colors'] = input("Do you want to show colors? 1 or 0: ")
        self.input_dict['seed_image_path'] = input("Type the full path for the seed image: ")

    def save_config(self):
        """save configuration to file"""
        new_config = configparser.ConfigParser()
        new_config['SESSION_SETUP'] = self.input_dict
        with open(f"{self.input_dict['name']}.conf", 'w+') as save_file:
            new_config.write(save_file)

    def make_base(self):
        """create new base configuration"""
        print('This will create a new base configuration to be run by default.')
        self.make_new('default_simulation_settings')


class SessionConfiguration:
    def __init__(self, screen_size, cell_size, ruleset_name, 
    aging=1, processing_mode=2,  show_colors=1, seed_image_path=''):
        self.screen_size = screen_size
        self.cell_size = cell_size
        self.ruleset_name = ruleset_name
        self.aging = aging
        self.processing_mode = processing_mode
        self.show_colors = show_colors
        if seed_image_path == '':
            self.seed_image_path = None
        else:
            self.seed_image_path = seed_image_path


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

        if session_config.seed_image_path is None:
            self.grid.random_seed(0.5)
        else:
            self.control.capture.load_image(session_config.seed_image_path)

        self.run_sim()
        
    def run_sim(self):
        while self.control.running:
            self.clock.tick(self.control.fps)
            self.grid.update()

        pygame.quit()
