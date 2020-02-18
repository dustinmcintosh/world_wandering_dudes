import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np

class Creature:
  """ Creates a creature object with specified location and mutation chars.

  Creatures take random walks, grabbing food as they go. They have a chance to
  mutate characteristics. 
  Mutations include
    NORMAL: takes 1 step, eats 1 food (+1 more to reproduce).
    SPEEDY: takes 2 steps, eats 1 food (+1 more to reproduce).
    EFFICIENT: takes 1 step, eats 0.5 food (0.5 more to reproduce).
  
  Arguments:
    location: list of length 2; Location of the creature.
    mutation: string; See supported mutations above.
    reproduction_mutation_chance: float; [0, 1] chance the creature will mutate
      on reproducing.

  Other attributes:
    food_stored: float; Amount of food the creature has currently.
    age: How many days the creature has survived - controlled by the creature's 
      world.
    is_alive: bool; indicates if creature is alive
  """
  def __init__(self, location, mutation="NORMAL", mutation_chance=0):
    self.location = location
    self.food_stored = 0
    self.mutation = mutation
    self.reproduction_mutation_chance = mutation_chance
    self.age = 0
    self.is_alive = True
  
  def move_and_grab(self, field):
    # udlr = up, down, left, right - choices for movement.
    udlr = [[0,1], [0,-1], [-1,0], [1,0]]
    which_dir = udlr[np.random.choice(4)]

    # Creatures move 1. 
    steps_to_take = 1
    # Speedy creatures get a boost.
    if self.mutation == "SPEEDY":
      steps_to_take = 2

    for i in range(steps_to_take):
      if field.has_boundaries:
        # Move or just run into the wall.
        self.location[0] = max(
          min(self.location[0]+which_dir[0], field.field_size-1), 0
        )
        self.location[1] = max(
          min(self.location[1]+which_dir[1], field.field_size-1), 0
        )
      else:
        # Move.
        self.location[0] = self.location[0]+which_dir[0]
        if self.location[0] < 0:
          # Teleport to the other side of the field.
          self.location[0] = field.field_size-1
        if self.location[0] > field.field_size-1:
          self.location[0] = 0
        self.location[1] = self.location[1]+which_dir[1]
        if self.location[1] < 0:
          self.location[1] = field.field_size-1
        if self.location[1] > field.field_size-1:
          self.location[1] = 0

      # Grab all the food from the field at this new location and store it.
      self.food_stored += field.remove_food(self.location)

  def eat_die_reproduce(self):
    """Creatures eat, possibly die, and possibly reproduce depending on food.

    Most creatures require 1 food to eat, 1 food to reproduce.  They die if they
    cannot eat. EFFICIENT creatures require 0.5 food to eat/reproduce. This 

    Returns: (survived, babies)
      babies: [creatures]; A list of creatures resulting from reproduction
    """
    # Got a little be it older.
    self.age += 1
    food_required = (0.5 if self.mutation=="EFFICIENT" else 1)
    # Eat, if you can (die if you can't.)
    self._eat(food_required)
    if not self.is_alive or self.food_stored < food_required:
      return []
    return self._reproduce(food_required)

  def _eat(self, food_required):
    """Eats food_required food from food_stored; dies if not enough food.

    Arguments:
      food_required: float; amount of food the creature must eat to survive.
    """
    self.food_stored -= food_required
    if self.food_stored < 0:
      # Dead. Poor dude. :(
      self.is_alive = False

  def _reproduce(self, food_required):
    """Reproduces if has sufficient food.

    Arguments:
      food_required: float; amount of food the creature must eat to survive.
    Returns:
      [creature] length 1; A single (possibly mutated) offspring.
    """
    self.food_stored -= food_required
    return [Creature(self.location.copy(),
                     mutation=_get_mutation(self.reproduction_mutation_chance),
                     mutation_chance=self.reproduction_mutation_chance
            )]

  def _get_mutation(self, mutation_chance):
    """Mutates randomly (perhaps to own species) w/ prob mutation_chance.

    Arguments:
      mutation_chance: float; Chance to mutate.
    Returns:
      mutation: string; see list of acceptable mutations above.
    """
    if np.random.rand() < mutation_chance:
      return np.random.choice(['NORMAL', 'EFFICIENT', 'SPEEDY'])
    return self.mutation