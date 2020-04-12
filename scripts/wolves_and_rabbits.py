import argparse
import numpy as np
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
    # Create a small world, with lots of food, rabbits and wolves.
    field_size = 225
    food_density = 0.07
    print("Creating World...")
    my_world = World(field_size,
                     food_density,
                     int(field_size**2*food_density),
                     creatures_randomly_teleport=False,
                     creature_meat_value=2)
    my_world.create_creatures(int(field_size**2*food_density/4),
                              creature_diet_type="CARNIVORE",
                              creatures_randomly_teleport=False,
                              creature_meat_value=5)
    # my_world.create_creatures(int(field_size**2*food_density/8),
    #                           creature_diet_type="SUPER_CARNIVORE",
    #                           creatures_randomly_teleport=True) # They all died if they don't....

  for i in range(40):
    my_world.pass_day(40,
                      plot_steps=(True if i < 10 else False))
    my_world.show_me(save_plot=True)
    print("days_passed:", my_world.days_passed,
          "; creatures:", len(my_world.creatures),
          "; rabbits:", len([x for x in my_world.creatures
                               if x.diet_type == "HERBIVORE"]),
          "; wolves:", len([x for x in my_world.creatures
                              if x.diet_type == "CARNIVORE"]),
          "; wolf-eaters:", len([x for x in my_world.creatures
                              if x.diet_type == "SUPER_CARNIVORE"]))

  my_world.plot_history(save_plot=True)
  save_gif("*_t_*.png", "the_first_days", delete_imgs=True, frame_duration=100)
  save_gif("world_2*.png", "each_day", delete_imgs=True, frame_duration=800)

  with open(TMP_DIR + "my_world.pkl", "wb") as f:
    pickle.dump(my_world, f)

if __name__ == "__main__":
  main()