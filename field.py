import numpy as np
from datetime import datetime
import pytz
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

class Field:
  def __init__(self, field_size, food_fill_factor=0, has_boundaries=False):
    self.field_size = field_size
    self.has_boundaries = has_boundaries
    self.food_grid = np.array(
      [[0 for x in range(field_size)] for y in range(field_size)]
    )
    
    for r in np.random.choice(field_size**2, 
                              int(np.round(field_size**2*food_fill_factor)),
                              replace=False):
      self.food_grid[int(np.floor(r/field_size)), r%field_size] = 1
  
  def sprout(self,
             food_fill_factor, 
             low_grid_x_index=0, high_grid_x_index=0, 
             low_grid_y_index=0, high_grid_y_index=0):
    if high_grid_x_index == 0:
      high_grid_x_index = self.field_size
    if high_grid_y_index == 0:
      high_grid_y_index = self.field_size
    width = (high_grid_x_index-low_grid_x_index)
    height = (high_grid_y_index-low_grid_y_index)

    for r in np.random.choice(width*height,
                              int(np.ceil(width*height*food_fill_factor)),
                              replace=False):
      self.food_grid[low_grid_x_index+int(np.floor(r/(width))),
                     low_grid_y_index+r%(width)] += 1

  def spoil(self):
    self.food_grid = np.array([[0 for x in range(self.field_size)] for y in range(self.field_size)])

  def remove_food(self, location):
    # removes all food from the specified location on the field.
    # returns amount of food removed
    removed_food = self.food_grid[location[0], location[1]]
    self.food_grid[location[0], location[1]] = 0
    return removed_food

  def show_me(self, save_plot=False):
    fig, ax = plt.subplots(1,1, figsize = (6, 6))
    ax.spy((self.food_grid-1)*-1, markersize=3, c="palegoldenrod")
    ax.spy(self.food_grid, markersize=3, c="g")
    if save_plot:
      fig.savefig(
        '/mnt/c/Users/dmcin/Desktop/projects/simulations/tmp_plots/' + 
        datetime.now().strftime("field_%Y%m%d%H%M%S%f.pdf"), fmt='pdf')