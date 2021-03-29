import imageio
from pathlib import Path
import os
import sys
import re

def make_gif(frames_dir, active_animation=False):
    """generate a gif using the appropriate .pngs within the specified 
    directory. 
    
    active_animation flag to True will produce the animation 
    using the "shot" frames (these frames only show pixels of the image 
    that were corresponding to the current active cells of the 
    simulation). Otherwise "image" frames are used (which show all pixels 
    of the underlying image that the simulation was acting on)."""
    image_path = Path(frames_dir)
    if active_animation:
        images = list(image_path.glob('shot*.png'))
        animation_file = 'active_animation.gif'
    else:    
        images = list(image_path.glob('image*.png'))
        animation_file = 'animation.gif'
    images.sort(key=get_filename_key)
    image_list = []
    for file_name in images:
        image_list.append(imageio.imread(file_name))
    
    imageio.mimwrite(image_path.joinpath(animation_file), image_list)

def get_filename_key(filename):
    numbers = re.compile(r'(\d+)')
    filename_nums = numbers.split(filename.name)[1::2]
    image_position = list(map(int, filename_nums))
    return image_position #return list of ints in filename for comparison

if __name__ == "__main__":
    directory = sys.argv[1]
    try:
        active = sys.argv[2]
        make_gif(directory, active_animation=active)
    except:
        make_gif(directory)
    