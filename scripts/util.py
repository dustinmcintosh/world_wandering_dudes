import glob
import os
from PIL import Image

import sys
sys.path.insert(1, sys.path[0]+'/..')

from SET_ME import TMP_DIR

def save_gif(file_pattern, gif_name, delete_imgs=False, frame_duration=100):
  """Using Pillow image library to change alphabetical png files into gifs.

  Arguments:
    file_pattern: string; File pattern of the images to use.
    gif_name: string; Filename to save ('.gif' will be appended automatically).
  """
  frames = []
  imgs = glob.glob(TMP_DIR + file_pattern)

  # Open the images.
  for i in sorted(imgs):
    frames.append(Image.open(i))

  if len(frames) == 0:
    return

  # Save into looping gif file.
  frames[0].save(TMP_DIR + gif_name + '.gif',
                 format='GIF',
                 append_images=frames[1:],
                 save_all=True,
                 duration=frame_duration, loop=0)
  if delete_imgs:
    [os.remove(file) for file in imgs]