# python-cellular-automata
A small library for configuring, viewing, and recording cellular automata simulations with Python.

## About PCA
This project is made to provide Python programmers with an easy way to visualize and record 2D cellular automata for research.

This project relies most on Pygame to visualize and handle user control. It also uses NumPy to speed up processing and opencv-python to capture and process image data. It currently runs on a single thread. I hope to incorporate multiprocessing soon and eventually custom CUDA kernels so that it will run larger grids without so much lag.

## Installation
To use this library you will have to first install the prerequisite packages:

--> Pygame

--> OpenCV-Python

--> NumPy

Clone this repository with git and use the command prompt to navigate to the folder containing hello_ca.py

Run hello_ca.py with python: `..\python-cellular-automata\pythoncellularautomata> python hello_ca.py`

## Basic Usage
Open hello_ca.py or example1.py in your text editor to explore the example configuration templates.
