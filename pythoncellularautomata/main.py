from models.session_models import (
    SessionConfigurationManager,
    CellularAutomatonSession, 
    SessionConfiguration
)


def main():
    """Create and run basic automaton configuration."""
    print('What would you like to do?')
    options = [
        '1. run default configuration',
        '2. create new named configuration',
        '3. run custom configuration by name'
    ]
    print(options)
    selection = int(input('Type number: '))
    session_manager = SessionConfigurationManager()
    if selection == 1:
        session_manager.play_default()
    elif selection == 2:
        session_manager.make_new()
    elif selection == 3:
        session_manager.input_config_name()
    else:
        print(f'{selection} is not a valid option. Try again.')
        main()

if __name__ == '__main__':
    main()