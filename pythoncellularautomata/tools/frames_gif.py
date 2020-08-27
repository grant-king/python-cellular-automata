import imageio
from pathlib import Path
import os
import sys

def make_gif(frames_dir):
    image_path = Path(frames_dir)
    images = list(image_path.glob('image*.png'))
    image_list = []
    for file_name in images:
        image_list.append(imageio.imread(file_name))
    
    imageio.mimwrite(os.path.join(image_path ,'animation.gif'), image_list)


if __name__ == "__main__":
    directory = sys.argv[1]
    make_gif(directory)