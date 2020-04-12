import numpy as np
from datetime import datetime
import pytz
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

import SET_ME

class Field:
  """Create a field object which is a square 2D lattice with food on it.

  The field is specified by a square array of 0's.  Food on the field is
  specified by any number > 0 that appears on the lattice.

  Arguments:
    field_size: Int; Linear dimension (height or width) of the square field.
    has_boundaries: Bool; Does the field have boundaries? Creatures that run off
      the edge of a field without boundaries will appear on the opposite edge.
      Defaults to False (field w/ no boundaries).

  Additional Attributes:
    food_grid: np.array; Square array of floating point numbers > 0. Number
      indicates the amount of food at each location.
  """
  def __init__(self, field_size, has_boundaries=False):
    self.field_size = field_size
    self.has_boundaries = has_boundaries
    self.food_grid = np.array(
      [[0 for x in range(field_size)] for y in range(field_size)]
    )

  def sprout(self,
             food_fill_factor,
             food_value=1,
             low_grid_x_index=0, high_grid_x_index=0,
             low_grid_y_index=0, high_grid_y_index=0):
    """Fills the field (or a section of it) randomly with some food.

    Arguments:
      food_fill_factor: float; Fraction, in range [0,1], of the section of
        field to fill with food.
      food_value: float; How much food to add to each spot on the field.
        Defaults to 1.
      low_grid_x_index: int, [0, self.field_size). x-index of lower left corner
      of the section of field to sprout. Defaults to 0.
      high_grid_x_index: int, [low_grid_x_index, self.field_size). x-index of
      lower right corner of the section of field to sprout. Defaults to 0
      (which is interpreted as self.field_size).
      low_grid_y_index: int, [0, self.field_size). y-index of lower left corner
      of the section of field to sprout. Defaults to 0.
      high_grid_y_index: int, [low_grid_y_index, self.field_size). y-index of
      upper right corner of the section of field to sprout. Defaults to 0 (which
      is interpreted as self.field_size).
    """
    # Check food_fill_factor makes sense.
    if food_fill_factor < 0 or food_fill_factor > 1:
      raise(
        "food_fill_factor must be between 0 and 1, got" + str(food_fill_factor)
      )

    # High grid index defaults to 0, which is interpreted at the field size.
    if high_grid_x_index == 0:
      high_grid_x_index = self.field_size
    if high_grid_y_index == 0:
      high_grid_y_index = self.field_size

    # Calculate the width and height of the section of field to fill.
    width = (high_grid_x_index-low_grid_x_index)
    height = (high_grid_y_index-low_grid_y_index)

    # Fill the field at random with food_value worth of food.
    for r in np.random.choice(width*height,
                              int(np.ceil(width*height*food_fill_factor)),
                              replace=False):
      self.food_grid[low_grid_x_index+int(np.floor(r/(width))),
                     low_grid_y_index+r%(width)] += food_value

  def spoil(self):
    """ Spoils all food on the field.

    Sets the food grid to statee without food.
    """
    self.food_grid = np.array(
      [[0 for x in range(self.field_size)] for y in range(self.field_size)])

  def remove_food(self, location):
    """Removes all food from the specified location on the field.

    Arguments:
      location: list of length 2.  Location on field to remove food from.
    Returns:
      float; Amount of food that was removed.
    """
    removed_food = self.food_grid[location[0], location[1]]
    self.food_grid[location[0], location[1]] = 0
    return removed_food

  def show_me(self, save_plot=False):
    """Plots the field and food on the field.

    Arguments:
      save_plot: bool; Whether or not to save the plot to disc.
    """
    fig, ax = plt.subplots(1,1, figsize = (6, 6))
    # Plot the grass.
    ax.spy((self.food_grid-1)*-1, markersize=3, c="palegoldenrod")
    # Plot the food.
    ax.spy(self.food_grid, markersize=3, c="g")
    if save_plot:
      fig.savefig(
        '/mnt/c/Users/dmcin/Desktop/projects/simulations/tmp_plots/' +
        datetime.now().strftime("field_%Y%m%d%H%M%S%f.png"), fmt='png')
      plt.close()