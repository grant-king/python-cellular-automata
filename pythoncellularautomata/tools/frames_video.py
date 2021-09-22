import os
import cv2
from pathlib import Path
import re
import sys

def make_video(frames_directory):
    directory_path = Path(frames_directory)
    image_files = list(directory_path.glob('*.png'))
    video_name = 'animation.mp4'

    image_files.sort(key=get_filename_key)

    if len(image_files) > 1000:
        num_array_needed = len(image_files) // 1000
    else:
        num_array_needed = 1

    #set output
    sample_image = cv2.imread(str(image_files[0].absolute()))
    height, width, layers = sample_image.shape
    size = (width, height)
    output = cv2.VideoWriter(directory_path.joinpath(video_name), cv2.VideoWriter_fourcc(*'mp4v'), 30, size)
    
    for array_idx in range(num_array_needed):
        img_array = []
        #collect frames
        for filename in image_files[(1000 * (array_idx)):(1000 * (array_idx + 1))]:
            img = cv2.imread(filename)
            img_array.append(img)

        #write each frame and finish
        for i in range(len(img_array)):
            output.write(img_array[i])

    if len(image_files) > 1000:
        for filename in image_files[1000*num_array_needed:]:
            img = cv2.imread(filename)
            img_array.append(img)

        #write each frame and finish
        for i in range(len(img_array)):
            output.write(img_array[i])

    output.release()

def get_filename_key(filename):
    numbers = re.compile(r'(\d+)')
    filename_nums = numbers.split(filename.name)[1::2]
    image_position = list(map(int, filename_nums))
    return image_position #return list of ints in filename for comparison

def blend_frames(dir_path):
    os.chdir(dir_path)
    
    shot_files = [file for file in os.listdir() if file.startswith("shot")]
    image_files = [file for file in os.listdir() if file.startswith("image")]
    shot_files.sort(key=lambda x: int(x[5:-4]))
    image_files.sort(key=lambda x: int(x[6:-4]))

    #combine frames
    for idx, image_file in enumerate(image_files):
        image_data = cv2.imread(image_file)
        shot_data = cv2.imread(shot_files[idx])
    
        combined = cv2.addWeighted(image_data, 0.5, shot_data, 0.5, 0)
        cv2.imwrite(f'blended_{idx + 1}.png', combined)
"""
if __name__ == '__main__':
    frames_directory = sys.argv[1]

    print(f"\n\nWriting frames for {frames_directory}.\n")
    make_video(frames_directory)
    print(f"\n{frames_directory}.mp4 created in video directory.\n")
""" 
make_video('D:\\chaos\\test_dir')