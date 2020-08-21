# python-cellular-automata
A project for configuring, viewing, and recording cellular automata simulations with Python.

## About PCA
This is a work in progress. It has only been tested on a Windows 10 machine with a CUDA-enabled GPU.

The goal is to provide Python programmers with a way to run colorful 2D cellular automata.

This project relies most on Pygame to visualize and handle user control. It also uses NumPy for array operations, Numba for GPU processing, and opencv-python to capture and process image data.

## Installation with pip
This pythoncellularautomata module is not yet on pypi. You can still install it with pip in debug mode after downloading this source. Create a new Python environment, activate the environment from your command prompt, and navigate to the root directory where you cloned this repository. 

Install the PCA package into your environment from the python-cellular-automata project root directory with:
```shell
pip install -e .
```

Before use, you must also install cudatoolkit onto your system. I recommend installing it manually from [this site](https://developer.nvidia.com/cuda-downloads).

You can now use the PCA CLI by running this in your command prompt, from within the pythoncellularautomata source code subdirectory:
```shell
python main.py
``` 

Or import it into another project to use the API with:
```python
import pythoncellularautomata.models.session_models as pca
```

## The API
The API has one high-level class with three main methods. These methods and their use is demonstrated in `main.py`. The most basic use of the primary method would be:
```python
import pythoncellularautomata.models.session_models as pca

def start_default_automaton():
    session_manager = pca.SessionConfigurationManager()
    print("Starting simulation from the default configuration. Switch focus to the Pygame window to use keyboard controls.")
    session_manager.play_default()

start_default_automaton()

```


