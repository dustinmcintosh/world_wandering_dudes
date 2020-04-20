import collections
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np

from creature import Creature
from field import Field
from SET_ME import TMP_DIR

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
    creature_mutation: string; Mutation type of the initial creatures.
    creature_reproduction_mutation_prob: float; Probability that the creatures
      willmutate upon reproduction.
    creatures_randomly_teleport: Do the creatures teleport to a random location
      on the field every day?
    field_has_boundaries: bool; Does the world's field have boundaries?
    food_spoils: bool; Does the food in the world, on the field and stored by
      creatures spoil (disappear) at the end of the day?
    creature_meat_value: float; how much food do I get if I eat a creature?
    """
  def __init__(self,
               field_size,
               food_fill_factor,
               num_initial_creatures,
               creature_mutation="NORMAL",
               creature_reproduction_mutation_prob=0,
               creatures_randomly_teleport=False,
               field_has_boundaries=False,
               food_spoils=False,
               creature_meat_value=2):
    self.field = Field(field_size, has_boundaries=field_has_boundaries)
    self.field.sprout(food_fill_factor)
    self.creatures = []
    self.creatures_by_loc = [
        [[] for x in range(field_size)] for y in range(field_size)
    ]
    self.create_creatures(
        num_initial_creatures,
        creature_mutation=creature_mutation,
        creature_reproduction_mutation_prob=creature_reproduction_mutation_prob,
        creatures_randomly_teleport=creatures_randomly_teleport,
        creature_meat_value=creature_meat_value
    )
    self.days_passed = 0
    self.history = []
    self.food_fill_factor = food_fill_factor
    self.food_spoils = food_spoils

  def create_creatures(self,
                       num_creatures,
                       creature_mutation="NORMAL",
                       creature_reproduction_mutation_prob=0,
                       creatures_randomly_teleport=False,
                       creature_diet_type="HERBIVORE",
                       creature_meat_value=2):
    """Places num_creatures creatures randomly around the world.

    Arguments:
      num_creatures: int; Number of creatures to add to world.
      creature_mutation: string; Type of mutation for the creatures (see
        Creature.py).
      creature_reproduction_mutation_prob: float; probability the creature
        will mutate upon reproduction.
      mutation: string; Mutation of the creature.
      creatures_randomly_teleport: bool; Do the creatures teleport to a random
        location on the field every day?
      creature_diet_type: "HERBIVORE" or "CARNIVORE" or "SUPER_CARNIVORE"
    """
    all_my_creatures  = []
    for randy in np.random.choice(self.field.field_size**2,
                                  num_creatures,
                                  replace=False):
      x_loc = int(np.floor(randy/self.field.field_size))
      y_loc = randy%self.field.field_size
      self.add_creature(
          Creature(
              location=[x_loc, y_loc],
              mutation=creature_mutation,
              reproduction_mutation_chance=creature_reproduction_mutation_prob,
              diet_type=creature_diet_type,
              randomly_teleports=creatures_randomly_teleport,
              meat_value=creature_meat_value
      ))

  def add_creature(self, creature):
    """Adds the creature to the world.

    Arguments:
      creature: int; Creature to add.
    """
    self.creatures.append(creature)
    self.creatures_by_loc[creature.location[0]][creature.location[1]].append(
        creature
    )

  def remove_creature(self, creature):
    """Removes the creature from the world.

    Arguments:
      creature: int; Creature to remove.
    """
    self.creatures = [x for x in self.creatures if x != creature]
    self.creatures_by_loc[creature.location[0]][creature.location[1]] = [
        x for x in
        self.creatures_by_loc[creature.location[0]][creature.location[1]]
        if x != creature
    ]

  def show_me(self, time_of_day=None, save_plot=False):
    """Plots the field, food, and creatures.

    Arguments:
      save_plot: bool; Whether or not to save the plot to disc.
      time_of_day: int; if set, will display in the title
    """
    increment_size = float(100/1.5)/self.field.field_size
    fig, ax = plt.subplots(1,1, figsize = (6, 6))
    ax.spy(
        [
            [1 for x in range(self.field.field_size)]
            for y in range(self.field.field_size)
        ],
        markersize=6*increment_size, c="palegoldenrod")
    ax.spy(self.field.food_grid, markersize=1*increment_size, c="g")

    herbivore_loc = self.field.food_grid*0
    dead_herbivore_loc = self.field.food_grid*0
    for dude in self.creatures:
      if dude.diet_type == "HERBIVORE":
        if dude.is_alive:
          herbivore_loc[dude.location[0], dude.location[1]] = 1
        else:
          dead_herbivore_loc[dude.location[0], dude.location[1]] = 1

    ax.spy(herbivore_loc, markersize=2*increment_size, c="m")
    ax.spy(dead_herbivore_loc, markersize=2*increment_size, c="k")

    carnivore_loc = self.field.food_grid*0
    dead_carnivore_loc = self.field.food_grid*0
    for dude in [x for x in self.creatures if x.diet_type == "CARNIVORE"]:
      if dude.is_alive:
        carnivore_loc[dude.location[0], dude.location[1]] = 1
      else:
        dead_carnivore_loc[dude.location[0], dude.location[1]] = 1

    ax.spy(carnivore_loc, markersize=4*increment_size, c="r")
    ax.spy(dead_carnivore_loc, markersize=4*increment_size, c="k")

    super_carnivore_loc = self.field.food_grid*0
    for dude in [x for x in self.creatures if x.diet_type == "SUPER_CARNIVORE"]:
      super_carnivore_loc[dude.location[0], dude.location[1]] = 1

    ax.spy(super_carnivore_loc, markersize=6*increment_size, c="royalblue")

    my_title = 'Days passed: ' + str(self.days_passed)
    if type(time_of_day) == int:
      my_title += "; time: " + str(time_of_day)
    ax.set_title(my_title)
    ax.set_xticks([], [])
    ax.set_yticks([], [])
    if not self.field.has_boundaries:
      ax.axis('off')

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
      steps_in_day: int; How many times the creatures should move today.
      plot_steps: bool; should we save a png for every step today?
    """
    if self.days_passed == 0:
      # Record starting state (0 births or deaths).
      self._record_history(0)

    # Go, little dudes, go!!
    for t in range(steps_in_day):
      for this_creature in np.random.choice(self.creatures,
                                            len(self.creatures),
                                            replace=False):
        this_creature.move_and_grab(self)
      if plot_steps:
        self.show_me(save_plot=True, time_of_day=t)

    # Eat and reproduce, if you can, my dudes!
    babies = []
    for this_creature in self.creatures:
      babies += this_creature.eat_die_reproduce(self)

    # Welcome little dudes!
    [self.add_creature(baby) for baby in babies]

    # Goodbye, loyal dudes! :(
    deaths = [x for x in self.creatures if not x.is_alive]
    num_deaths = len(deaths)
    [self.remove_creature(death) for death in deaths]

    # Spoil food if we need to.
    if self.food_spoils:
      self.field.spoil()
      for this_creature in self.creatures:
        this_creature.food_stored=0

    # The land is fertile! :)
    self.field.sprout(self.food_fill_factor)

    # Everybody who can teleport, does.
    [creature.maybe_teleport(self) for creature in self.creatures]

    # Long day...
    self.days_passed += 1
    self._record_history(num_deaths)

  def _record_history(self, deaths):
    """Record a line in the history books.

    Arguments:
      deaths: int; Number of deaths to record. These dudes are gone...
    """
    self.history.append(
        DailyHistory(
            day=self.days_passed,
            num_creatures=len(self.creatures),
            total_food_stored=sum([x.food_stored for x in self.creatures]),
            num_births=(0 if self.days_passed == 0 else
                len([x for x in self.creatures if x.age == 0])),
            num_deaths=deaths,
            creature_list=self.creatures.copy(),
            food_on_field=sum(sum(self.field.food_grid))
        )
    )

  def plot_history(self, save_plot=False):
    """Plot the history of the world.

    Arguments:
      save_plot: bool; Save the plot to disc?
    """
    fig,axes = plt.subplots(4, 3, figsize = (18, 15))
    day_history = np.array([x.day for x in self.history])
    num_creatures_history = np.array([x.num_creatures for x in self.history])
    num_births_history = np.array([x.num_births for x in self.history])
    num_deaths_history = np.array([x.num_deaths for x in self.history])
    total_food_stored_history = np.array(
        [x.total_food_stored for x in self.history])
    food_on_field_history = np.array([x.food_on_field for x in self.history])

    def _set_properties(ax, upper_y, y_label, x_label="Time (days)"):
      ax.grid(b=True, which='major')
      if type(x_label) == str:
        ax.set_xlabel(x_label)
      ax.set_ylabel(y_label)
      ax.set_ylim(0, max(upper_y, 1))

    diet_types = set()
    # Get the set of all mutations throughout history.
    for this_day_history in self.history:
      for this_creature in this_day_history.creature_list:
        diet_types.add(this_creature.diet_type)

    # If only 1 diet type, plot creatures, births, deaths.
    if len(diet_types) < 2:
      axes[0,0].plot(day_history, num_creatures_history, 'b', label="Creatures")
      axes[0,0].plot(day_history, num_births_history, 'g', label="Births")
      axes[0,0].plot(day_history, num_deaths_history, 'r', label="Deaths")
    # Otherwise, plot time series of diet types.
    else:
      diet_type_cts_hist = [dict.fromkeys(diet_types, 0) for x in self.history]
      for this_day_history in self.history:
        for this_creature in this_day_history.creature_list:
          diet_type_cts_hist[this_day_history.day][this_creature.diet_type] += 1
      for dt in sorted(diet_types):
        dtch = np.array([x[dt] for x in diet_type_cts_hist])
        axes[0,0].plot(dtch, label=dt)

    _set_properties(axes[0,0], max(num_creatures_history)*1.05, 'Creatures')
    axes[0,0].legend()


    mutations = set()
    # Get the set of all mutations throughout history.
    for this_day_history in self.history:
      for this_creature in this_day_history.creature_list:
        mutations.add(this_creature.mutation)

    # If there's only one type of mutation and we didn't already plot it above,
    # plot creatures, births, and deaths.
    if len(mutations) < 2 and len(diet_types) >= 2:
      axes[0,1].plot(day_history, num_creatures_history, 'b', label="Creatures")
      axes[0,1].plot(day_history, num_births_history, 'g', label="Births")
      axes[0,1].plot(day_history, num_deaths_history, 'r', label="Deaths")
      axes[0,1].legend()
    # Otherwise, plot mutations.
    else:
      # Get the number of creatures with each mutation throughout history
      mut_cts_history = [dict.fromkeys(mutations, 0) for x in self.history]
      for this_day_history in self.history:
        for this_creature in this_day_history.creature_list:
          mut_cts_history[this_day_history.day][this_creature.mutation] += 1

      running_sum = np.array([0 for x in range(len(self.history))])
      for mut in sorted(mutations):
        mut_ct_history = np.array([x[mut] for x in mut_cts_history])
        axes[0,1].fill_between(day_history,
                               running_sum,
                               running_sum + mut_ct_history,
                               label=mut)
        running_sum += mut_ct_history
        handles, labels = axes[0,1].get_legend_handles_labels()
        axes[0,1].legend(handles[::-1], labels[::-1], title='Mutation')

    _set_properties(axes[0,1], max(num_creatures_history)*1.05, 'Creatures')


    # On each day, let's see what happened to the dudes that were running
    # around (not the dudes present at the end of the day).
    today_creatures = num_creatures_history + (
        -num_births_history + num_deaths_history
    )

    # The 0th entry in the history is actually just the starting state.
    days_with_creatures = np.array(
        [i for i in np.where(today_creatures>0)[0] if i !=0])

    axes[0,2].fill_between(
        [day_history[i-1] for i in days_with_creatures],
        [0 for x in days_with_creatures],
        [0 for x in days_with_creatures],
        label=None)
    axes[0,2].fill_between(
        [day_history[i-1] for i in days_with_creatures],
        [num_births_history[i]/today_creatures[i] for i in days_with_creatures],
        [(today_creatures[i]-num_deaths_history[i])/today_creatures[i]
            for i in days_with_creatures],
        label='barely made it')
    axes[0,2].fill_between(
        [day_history[i-1] for i in days_with_creatures],
        [0 for x in days_with_creatures],
        [num_births_history[i]/today_creatures[i]
            for i in days_with_creatures],
        label='reproduced')
    axes[0,2].fill_between(
        [day_history[i-1] for i in days_with_creatures],
        [(today_creatures[i]-num_deaths_history[i])/today_creatures[i]
            for i in days_with_creatures],
        [1 for i in days_with_creatures],
        label = 'died')

    handles, labels = axes[0,2].get_legend_handles_labels()
    axes[0,2].legend(handles[::-1], labels[::-1])
    _set_properties(axes[0,2], 1, 'Frac. Population')


    # Plot the total number of creatures at the end of each day and show how
    # many died also.  (The order below is to get the right colors.)
    axes[1,0].plot(day_history,
                   num_creatures_history,
                   'b',
                   linewidth=4,
                   label='total creatures')
    axes[1,0].fill_between(day_history,
                           num_births_history,
                           num_births_history*2,
                           label='new parents')
    axes[1,0].fill_between(day_history,
                           num_births_history*2,
                           num_creatures_history,
                           label='barely made it')
    axes[1,0].fill_between(day_history,
                           [0 for x in day_history],
                           num_births_history,
                           label='newborns')
    axes[1,0].fill_between(day_history,
                           num_creatures_history,
                           num_creatures_history + num_deaths_history,
                           label='deaths')

    handles, labels = axes[1,0].get_legend_handles_labels()
    axes[1,0].legend(handles[::-1], labels[::-1])
    todays_creatures = np.array(num_creatures_history)

    _set_properties(axes[1,0],
                    max(num_creatures_history + num_deaths_history)*1.05,
                    'Creatures')


    # Plot creatures, births, deaths, food stored, food on field on same axes.
    axes[1,1].plot(day_history, num_creatures_history, 'b', label="Creatures")
    axes[1,1].plot(day_history, num_births_history, 'g', label="Births")
    axes[1,1].plot(day_history, num_deaths_history, 'r', label="Deaths")
    axes[1,1].plot(total_food_stored_history, 'b--', label="Total Food Stored")
    axes[1,1].plot(food_on_field_history, 'g--', label="Food on Field")
    _set_properties(axes[1,1],
                    max(max(num_creatures_history),
                        max(food_on_field_history),
                        max(total_food_stored_history))*1.05,
                    '')
    axes[1,1].legend()


    # Plot births/creature, deaths/creature, food stored/food on field.
    days_w_creats = np.array(
        [i for i in np.where(num_creatures_history>0)[0]
            if i != self.days_passed])
    axes[1,2].plot(
        [day_history[i] for i in days_w_creats],
        [num_births_history[i]/num_creatures_history[i] for i in days_w_creats],
        'g', label="Births/Starting Creatures")
    axes[1,2].plot(
        [day_history[i] for i in days_w_creats],
        [num_deaths_history[i+1]/num_creatures_history[i]
            for i in days_w_creats],
        'r', label="Deaths/Starting Creatures")
    max_y = 1

    days_w_food = np.array(
        [i for i in np.where(food_on_field_history>0)[0] if i !=0])
    if len(days_w_food) > 1:

      axes[1,2].plot(
          [day_history[i] for i in days_w_food],
          [total_food_stored_history[i]/food_on_field_history[i]
              for i in days_w_food],
          'b--', label="Food stored/Food on field")
      max_y = max(
          max_y,
          max([total_food_stored_history[i]/food_on_field_history[i]
              for i in days_w_food])
      )
    _set_properties(axes[1,2], 1.05*max_y, '')
    axes[1,2].legend()


    # Gotta figure out how to plot the autocorrelation...
    # axes[2,0].acorr(num_creatures_history[1:],
    #                 usevlines=True,
    #                 normed=True,
    #                 lw=2)
    # ax.grid(b=True, which='major')


    # Plot avg food stored per creature.
    axes[2,1].plot(
        [day_history[i] for i in days_w_creats],
        [total_food_stored_history[i]/num_creatures_history[i]
            for i in days_w_creats],
        'g--')
    _set_properties(
        axes[2,1],
        1.05*max([total_food_stored_history[i]/num_creatures_history[i]
            for i in days_w_creats]),
        'Avg Food Stored/Creature'
    )


    # Plot the final distribution of amount of food stored by creatures.
    labels, counts = np.unique(
        [x.food_stored for x in self.history[-1].creature_list if x.age>0],
        return_counts=True)
    axes[2,2].bar(labels, counts, align='center')
    axes[2,2].set_xlabel('Food Stored')
    axes[2,2].set_ylabel('Creatures (non-newborns)')
    axes[2,2].set_title('Final Food Stored distribution ')


    # Plot the final distribution of amount of food stored by non-newborn
    # creatures.
    axes[3,0].plot(num_births_history,
                   num_deaths_history)
    _set_properties(axes[3,0],
                    max(num_deaths_history)*1.05,
                    'Deaths', x_label='Births')

    for i, txt in enumerate(day_history):
      if self.days_passed < 10 or i%np.floor(len(day_history)/10) == 0:
        axes[3,0].annotate(str(txt),
                           (num_births_history[i], num_deaths_history[i]))


    # Plot food on field vs food stored parametric plot.
    axes[3,1].plot(food_on_field_history,
                   total_food_stored_history)
    _set_properties(axes[3,1],
                    max(total_food_stored_history)*1.05,
                    'Total Food Stored',
                    x_label='Food on the field')

    for i, txt in enumerate(day_history):

      if self.days_passed < 10 or i%np.floor(len(day_history)/10) == 0:
        axes[3,1].annotate(str(txt),
                           (food_on_field_history[i],
                            total_food_stored_history[i]))


    # Plot final age distribution of the creatures.
    labels, counts = np.unique([x.age for x in self.history[-1].creature_list],
                               return_counts=True)
    axes[3,2].bar(labels, counts, align='center')
    axes[3,2].set_xlabel('Age')
    axes[3,2].set_ylabel('Creatures')
    axes[3,2].set_title('Final age distribution')


    fig.tight_layout()

    if save_plot:
      fig.savefig(
        TMP_DIR + datetime.now().strftime("world_history_%Y%m%d%H%M%S%f.png"),
        fmt='png'
      )
      plt.close()