"""models for writing, reading system and individual simulation configurations"""
import configparser
import os

class SystemConfigurationHelper:
    def __init__(self):
        if os.path.isfile('system_setup.conf'):
            self.load_settings()
        else:
            print("No existing system configuration file was found. This will create a new one.")
            self.prompt_for_settings()
            self.write_system_config()

    def write_system_config(self):
        new_config = configparser.ConfigParser()
        new_config['SYSTEM'] = {'save_directory': self.save_directory}
        with open('system_setup.conf', 'w+') as config_file:
            new_config.write(config_file)

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read('system_setup.conf')
        self.save_directory = config['SYSTEM']['save_directory']

    def prompt_for_settings(self):
        input_directory = input('1. Type the full path for an existing directory where you want to save image files: ')
        if os.path.isdir(input_directory):
            print(f'setting save directory to {input_directory}')
            self.save_directory = input_directory
        else:
            print(f'{input_directory} is not a valid directory.')
            self.get_settings()

