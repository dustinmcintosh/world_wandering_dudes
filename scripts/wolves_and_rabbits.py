import sys
sys.path.insert(1, sys.path[0]+'/..')

from world import World, DailyHistory
from SET_ME import TMP_DIR

import argparse
import glob
import numpy as np
import os
import pickle
from PIL import Image

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

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--world_pkl", "-wp", help="pickled world file")
  args = parser.parse_args()
  if args.world_pkl:
    # Reuse old world.
    print("Reusing world", args.world_pkl)
    with open(TMP_DIR + args.world_pkl, "rb") as f:
      my_world=pickle.load(f)
  else:
    # Create a small world, with lots of food and 1 creature
    field_size = 75
    food_density = 0.07
    print("Creating World...")
    my_world = World(field_size,
                     food_density,
                     int(field_size**2*food_density),
                     reproduction_mutation_chance=0)
    my_world.create_creatures(int(field_size**2*food_density/4),
                              diet_type="CARNIVORE")

  for i in range(1):
    my_world.pass_day(40,
                      plot_steps=(True if i < 15 else False))
    my_world.show_me(save_plot=True)
    print("days_passed:", my_world.days_passed,
          "; creatures:", len(my_world.creatures),
          "; carnivores:", len([x for x in my_world.creatures if x.diet_type == "CARNIVORE"]))
  my_world.plot_history(save_plot=True)
  save_gif("*_t_*.png", "the_first_days", delete_imgs=True, frame_duration=100)
  save_gif("world_2*.png", "each_day", delete_imgs=True, frame_duration=800)

  with open(TMP_DIR + "my_world.pkl", "wb") as f:
    pickle.dump(my_world, f)

if __name__ == "__main__":
  main()