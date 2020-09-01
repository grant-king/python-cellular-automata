import imageio
from pathlib import Path
import os
import sys
import re

def make_gif(frames_dir):
    image_path = Path(frames_dir)
    images = list(image_path.glob('image*.png'))
    images.sort(key=get_filename_key)
    image_list = []
    for file_name in images:
        image_list.append(imageio.imread(file_name))
    
    imageio.mimwrite(image_path.joinpath('animation.gif'), image_list)

def get_filename_key(filename):
    numbers = re.compile(r'(\d+)')
    filename_nums = numbers.split(filename.name)[1::2]
    image_position = list(map(int, filename_nums))
    return image_position #return list of ints in filename for comparison

if __name__ == "__main__":
    directory = sys.argv[1]
    make_gif(directory)