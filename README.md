# python-cellular-automata
A project for configuring, viewing, and recording cellular automata simulations with Python.

## About PCA
This is a work in progress. The goal is to provide Python programmers with a way to visualize and record 2D cellular automata.

This project relies most on Pygame to visualize and handle user control. It also uses NumPy for array operations, Numba for GPU processing, and opencv-python to capture and process image data. It is capable of running very slowly on just a CPU, but is meant to be run on CUDA-enabled GPUs.

## Installation with conda or pip
This pythoncellularautomata module is not yet on pypi. To use this you will have to download the code locally after you create a new environment and install the prerequisite packages:

--> Pygame: >pip install pygame

--> OpenCV-Python: >conda/pip install opencv-python

--> NumPy 

--> Numba: >conda/pip install numba ; >conda install cudatoolkit or manually download for pip version at [this site](https://developer.nvidia.com/cuda-downloads).

--> Scikit-Image: >conda/pip install scikit-image

Clone this repository with git and use the command prompt to navigate to the folder containing hello_ca.py

Run hello_ca.py with python: `..\python-cellular-automata\pythoncellularautomata> python hello_ca.py`

## Basic Usage
Open hello_ca.py or any of the example files in your text editor to explore the example configuration templates.


