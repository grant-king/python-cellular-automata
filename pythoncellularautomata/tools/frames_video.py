import os
import cv2

def make_video(dir_path):
    os.chdir(dir_path)
    video_name = dir_path[9:]
    img_array = []
    all_files = []
    step_files = [file for file in os.listdir() if file.startswith("shot")]
    image_files = [file for file in os.listdir() if file.startswith("image")]
    blended_files = [file for file in os.listdir() if file.startswith("blended")]
    
    step_files.sort(key=lambda x: int(x[5:-4]))
    image_files.sort(key=lambda x: int(x[6:-4]))
    if len(blended_files) > 0:
        blended_files.sort(key=lambda x: int(x[8:-4]))

    _ = [all_files.append(blended_file) for blended_file in blended_files]
    _ = [all_files.append(image_file) for image_file in image_files]
    _ = [all_files.append(step_file) for step_file in step_files]

    if len(all_files) > 1000:
        num_array_needed = len(all_files) // 1000
    else:
        num_array_needed = 1

    #set output
    img = cv2.imread(all_files[0])
    height, width, layers = img.shape
    size = (width, height)
    out = cv2.VideoWriter(f'D:/chaos/videos/{video_name}.mp4',cv2.VideoWriter_fourcc(*'mp4v'), 30, size)
    
    for array_idx in range(num_array_needed):
        img_array = []
        #collect frames
        for filename in all_files[(1000 * (array_idx)):(1000 * (array_idx + 1))]:
            img = cv2.imread(filename)
            img_array.append(img)

        #write each frame and finish
        for i in range(len(img_array)):
            out.write(img_array[i])

    if len(all_files) > 1000:
        for filename in all_files[1000*num_array_needed:]:
            img = cv2.imread(filename)
            img_array.append(img)

        #write each frame and finish
        for i in range(len(img_array)):
            out.write(img_array[i])

    out.release()

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

if __name__ == '__main__':
    main_dir = 'D:/chaos'
    subdirs = os.listdir(main_dir)
    subdirs.pop(subdirs.index('videos'))
    subdirs.pop(subdirs.index('extra'))
    for frames_directory in subdirs:
        if f'{frames_directory}.mp4' not in os.listdir(f'D:/chaos/videos'):
            print(f"\n\nWriting frames for {frames_directory}.\n")
            blend_frames(f'D:/chaos/{frames_directory}')
            make_video(f'D:/chaos/{frames_directory}')
            print(f"\n{frames_directory}.mp4 created in video directory.\n")
        else:
            print(f"\n{frames_directory}.mp4 is already in video directory, trying next frames directory")