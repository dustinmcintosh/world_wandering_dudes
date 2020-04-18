import argparse
import os
import pickle

from util import save_gif

import sys
sys.path.insert(1, sys.path[0]+'/..')

from world import World, DailyHistory
from SET_ME import TMP_DIR

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
    # Create a small world, with lots of food and 1 creature.
    print("Creating World...")
    field_size = 50
    food_density = 0.07
    my_world = World(field_size,
                     food_density,
                     1,
                     field_has_boundaries=False,
                     creature_reproduction_mutation_prob=0.05)
    # Overwrite location to start the creature near the middle of the map.
    my_world.creatures[0].location = [20, 20]

  for i in range(40):
    my_world.pass_day(40,
                      plot_steps=(True if my_world.days_passed < 7 else False))
    my_world.show_me(save_plot=True)
    print("days_passed: ", my_world.days_passed,
          "; creatures: ", len(my_world.creatures))

  my_world.plot_history(save_plot=True)
  save_gif("*_t_*.png", "the_first_days", delete_imgs=True, frame_duration=100)
  save_gif("world_2*.png", "each_day", delete_imgs=True, frame_duration=800)

  with open(TMP_DIR + "my_world.pkl", "wb") as f:
    pickle.dump(my_world, f)

if __name__ == "__main__":
  main()