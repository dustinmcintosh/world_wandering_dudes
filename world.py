from creature import Creature
from field import Field
from SET_ME import TMP_DIR

import collections
from datetime import datetime
import pytz
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np

DailyHistory = collections.namedtuple(
    'DailyHistory',
    ['day',
     'num_creatures',
     'total_food_stored',
     'num_births',
     'num_deaths',
     'food_on_field',
     'creature_list']
)

class World:
  """Creates a world object consisting of a field and a list of creatures.

  The world is populated by a set of creatures and a square field.

  Arguments:
    field_size: int; Length of a side of the square field
    food_fill_factor: float; Fraction of the field that will be populated
      randomly by food each day
    num_creatures: int; Number of creatures to initally populate on the field
      with random location.
    mutation: string; Mutation type of the initial creatures.
    reproduction_mutation_chance: float; Probability that the creatures will
      mutate upon reproduction.
    food_spoils: bool; Does the food in the world, on the field and stored by
      creatures spoil (disappear) at the end of the day?
    """
  def __init__(self,
               field_size,
               food_fill_factor,
               num_creatures,
               mutation="NORMAL",
               reproduction_mutation_chance=0,
               food_spoils=False):
    self.field = Field(field_size)
    self.field.sprout(food_fill_factor)
    self.creatures = self.create_creatures(
        num_creatures,
        mutation=mutation,
        reproduction_mutation_chance=reproduction_mutation_chance
    )
    self.days_passed = 0
    self.history = []
    self.food_fill_factor = food_fill_factor
    self.food_spoils = food_spoils

  def create_creatures(self,
                       num_creatures,
                       mutation="NORMAL",
                       reproduction_mutation_chance=0):
    """Places num_creatures creatures randomly around the map.

    Arguments:
      num_creatures: int; Number of creatures to add to map.
      mutation: string; Type of mutation for the creatures (see Creature.py).
      reproduction_mutation_chance
      mutation: string; Mutation of the creature.
      reproduction_mutation_chance: Chance to mutate upor reproduction.

    Returns:
      [Creature]; A list of creatures.
    """
    all_my_creatures  = []
    for randy in np.random.choice(self.field.field_size**2,
                                  num_creatures, replace=False):
      all_my_creatures.append(
          Creature([int(np.floor(randy/self.field.field_size)),
                    randy%self.field.field_size],
                   mutation=mutation,
                   reproduction_mutation_chance=reproduction_mutation_chance)
      )
    return all_my_creatures

  def show_me(self, time_of_day=None, save_plot=False):
    """Plots the field, food, and creatures.

    Arguments:
      save_plot: bool; Whether or not to save the plot to disc.
      time_of_day: int; if set, will display in the title
    """
    increment_size = float(100/1.5)/self.field.field_size
    fig, ax = plt.subplots(1,1, figsize = (6, 6))
    ax.spy(
      [[1 for x in range(self.field.field_size)] for y in range(self.field.field_size)],
        markersize=6*increment_size, c="palegoldenrod")
    ax.spy(self.field.food_grid, markersize=3*increment_size/1.5, c="g")

    creature_loc = self.field.food_grid*0
    for dude in self.creatures:
      creature_loc[dude.location[0], dude.location[1]] = 1

    ax.spy(creature_loc, markersize=3*increment_size, c="r")
    my_title = 'Days passed: ' + str(self.days_passed)
    if type(time_of_day) == int:
      my_title += "; time: " + str(time_of_day)
    ax.set_title(my_title)

    if save_plot:
      file_name = TMP_DIR + datetime.now().strftime("world_%Y%m%d%H%M%S%f")
      if type(time_of_day) == int:
        file_name += "_t_%i" % (time_of_day)
      fig.savefig(file_name + ".png", fmt='png')
      plt.close()

  def pass_day(self, steps_in_day, plot_steps=False):
    """Pass a day of length steps_in_day throughout the world.

    Creatures will run around, grab food for each step in the day. At the end
    of the day creatures eat (or die) and reproduce (if they can).
    We mourn the dead, welcome the new babies, collect some stats for posterity,
    and everyone gets a day older.

    Arguments:
      save_plot: bool; Whether or not to save the plot to disc.
      steps_in_day: int; how many times the creatures should move today
      plot_steps: bool; should we save a pngs for every step today?
    """
    if self.days_passed == 0:
      # Record starting state (0 births or deaths).
      self._record_history(0)

    # Go, little dudes, go!!
    for t in range(steps_in_day):
      for this_creature in np.random.choice(self.creatures,
                                            len(self.creatures),
                                            replace=False):
        this_creature.move_and_grab(self.field)
      if plot_steps:
        self.show_me(save_plot=True, time_of_day=t)

    # Eat and reproduce, if you can, my dudes!
    dead_creature_indices = []
    babies = []
    for this_creature in self.creatures:
      babies += this_creature.eat_die_reproduce()

    # Goodbye, loyal dudes! :(
    num_deaths = len([x for x in self.creatures if not x.is_alive])
    self.creatures = [x for x in self.creatures if x.is_alive]

    # Welcome, little dudes! :)
    self.creatures += babies

    # Spoil food if we need to.
    if self.food_spoils:
      self.field.spoil()
      for this_creature in self.creatures:
        this_creature.food_stored=0

    # The land is fertile! :)
    self.field.sprout(self.food_fill_factor)

    # Long day...
    self.days_passed += 1
    self._record_history(num_deaths)

  def _record_history(self, deaths):
    """Record a line in the history books.

    Arguments:
      deaths: int; Number of deaths to record.
    """
    total_food_stored = 0
    for this_creature in self.creatures:
      total_food_stored += this_creature.food_stored

    births = len([x for x in self.creatures if x.age == 0])
    food_on_field = sum(sum(self.field.food_grid))

    self.history.append(DailyHistory(day=self.days_passed,
                                      num_creatures=len(self.creatures),
                                      total_food_stored=total_food_stored,
                                      num_births=births,
                                      num_deaths=deaths,
                                      creature_list=self.creatures.copy(),
                                      food_on_field=food_on_field)
    )

  def plot_history(self, save_plot=False):
    """Plot the history of the world.

    Arguments:
      save_plot: bool; Save the plot to disc?
    """
    fig,axes = plt.subplots(2, 3, figsize = (18, 7))
    day_history = [x.day for x in self.history]
    num_creatures_history = [x.num_creatures for x in self.history]
    num_births_history = [x.num_births for x in self.history]
    num_deaths_history = [x.num_deaths for x in self.history]
    total_food_stored_history = [x.total_food_stored for x in self.history]
    food_on_field_history = [x.food_on_field for x in self.history]
    upper_y = max(num_creatures_history)*1.05

    def _set_properties(ax, upper_y, y_label, x_label=None):
      ax.grid(b=True, which='major')
      if type(x_label) == str:
        ax.set_xlabel(x_label)
      ax.set_ylabel(y_label)
      ax.set_ylim(0, upper_y)

    axes[0,0].plot(day_history, num_creatures_history, 'b', label="Creatures")
    axes[0,0].plot(day_history, num_births_history, 'g', label="Births")
    axes[0,0].plot(day_history, num_deaths_history, 'r', label="Deaths")
    _set_properties(axes[0,0], upper_y, 'Num Creatures')
    axes[0,0].legend()

    mutations = set()
    # Get the set of all mutations throughout history.
    for this_day_history in self.history:
      for this_creature in this_day_history.creature_list:
        mutations.add(this_creature.mutation)

    # Get the number of creatures with each mutation throughout history
    mutation_cts_history = [dict.fromkeys(mutations, 0) for x in self.history]
    for this_day_history in self.history:
      for this_creature in this_day_history.creature_list:
        mutation_cts_history[this_day_history.day][this_creature.mutation] += 1

    running_sum = np.array([0 for x in range(len(self.history))])
    for mut in sorted(mutations):
      mut_ct_history = np.array([x[mut] for x in mutation_cts_history])
      axes[0,1].fill_between(day_history,
                             running_sum,
                             running_sum + mut_ct_history,
                             label = mut)
      running_sum += mut_ct_history

    axes[0,1].legend(loc='center left')
    _set_properties(axes[0,1], upper_y, 'Creatures')

    axes[0,2].plot(total_food_stored_history, 'b', label="Total Food Stored")
    axes[0,2].plot(food_on_field_history, 'g', label="Food on Field")
    _set_properties(axes[0,2],
                    max(food_on_field_history + total_food_stored_history)*1.05,
                    'Total Food Stored')
    axes[0,2].legend()

    axes[1,0].plot(num_births_history,
                   num_creatures_history)
    _set_properties(axes[1,0],
                    max(num_creatures_history)*1.05,
                    'Creatures', x_label='Births')


    for i, txt in enumerate(day_history):
      if i%np.floor(len(day_history)/10) == 0:
        axes[1,0].annotate(str(txt),
                           (num_births_history[i], num_creatures_history[i]))

    axes[1,1].plot(food_on_field_history,
                   total_food_stored_history)
    _set_properties(axes[1,1],
                    max(food_on_field_history)*1.05,
                    'Total Food Stored', x_label='Food on the field')

    for i, txt in enumerate(day_history):
      if i%np.floor(len(day_history)/10) == 0:
        axes[1,1].annotate(str(txt),
                           (food_on_field_history[i],
                            total_food_stored_history[i]))

    labels, counts = np.unique([x.age for x in self.history[-1].creature_list],
                               return_counts=True)
    axes[1,2].bar(labels, counts, align='center')
    axes[1,2].set_xlabel('Age')
    axes[1,2].set_ylabel('Creatures')
    axes[1,2].set_title('Final age distribution')

    fig.tight_layout()

    if save_plot:
      fig.savefig(
        TMP_DIR + datetime.now().strftime("world_history_%Y%m%d%H%M%S%f.png"),
        fmt='png'
      )
      plt.close()