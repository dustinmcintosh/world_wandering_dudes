import numpy as np

class Creature:
  """ Creates a creature object with specified location and mutation chars.

  Creatures take random walks, grabbing food as they go. They have a chance to
  mutate characteristics.
  Mutations include
    NORMAL: takes 1 step, eats 1 food (+1 more to reproduce).
    SPEEDY: takes 2 steps, eats 1 food (+1 more to reproduce).
    EFFICIENT: takes 1 step, eats 0.5 food (0.5 more to reproduce).
  They have a diet type:
    VEGETARIAN: Eats food that grows on the field.
    CARNIVORE: Eats creatures with diet_type VEGETARIAN.

  Arguments:
    location: list of length 2; Location of the creature.
    mutation: string; See supported mutations above.
    reproduction_mutation_chance: float; [0, 1] chance the creature will mutate
      on reproducing.
    diet_type: string; See supported diet types above.
    randomly_teleports: bool; does the creature teleport randomly at end of day?
    meat_value: float; Food value to predators.

  Other attributes:
    food_stored: float; Amount of food the creature has currently.
    age: How many days the creature has survived - controlled by the creature's
      world.
    is_alive: bool; indicates if creature is alive
  """
  def __init__(self,
               location,
               mutation="NORMAL",
               reproduction_mutation_chance=0,
               diet_type="VEGETARIAN",
               randomly_teleports=False,
               meat_value=2):
    self.location = location
    self.food_stored = 0
    self.mutation = mutation
    self.reproduction_mutation_chance = reproduction_mutation_chance
    self.age = 0
    self.diet_type = diet_type
    self.randomly_teleports = randomly_teleports
    self.is_alive = True
    self.meat_value = meat_value

  def move_and_grab(self, world):
    """Move along the field (see Field.py) and store any food you find.

    Most creatures move 1 space in random dir., fast creatures move 2 spaces.

    Arguments:
      world: world; Other creatures and a field to interact with.
    """
    # udlr = up, down, left, right - choices for movement.
    udlr = [[0,1], [0,-1], [-1,0], [1,0]]
    which_dir = udlr[np.random.choice(4)]

    # Dead creatures can't move (or grab). :(
    if not self.is_alive:
      return

    # Creatures move 1.
    steps_to_take = 1
    # Speedy creatures get a boost.
    if self.mutation == "SPEEDY":
      steps_to_take = 2

    # Pick yourself up off where you're standing.
    world.creatures_by_loc[self.location[0]][self.location[1]] = [
      x for x in world.creatures_by_loc[self.location[0]][self.location[1]]
      if x != self]

    for i in range(steps_to_take):
      if world.field.has_boundaries:
        # Move or just run into the wall.
        self.location[0] = max(
          min(self.location[0] + which_dir[0], world.field.field_size-1), 0
        )
        self.location[1] = max(
          min(self.location[1] + which_dir[1], world.field.field_size-1), 0
        )
      else:
        # Move.
        self.location[0] = self.location[0] + which_dir[0]
        if self.location[0] < 0:
          # Appear on the other side of the field.
          self.location[0] = world.field.field_size-1
        if self.location[0] > world.field.field_size-1:
          self.location[0] = 0
        self.location[1] = self.location[1] + which_dir[1]
        if self.location[1] < 0:
          self.location[1] = world.field.field_size-1
        if self.location[1] > world.field.field_size-1:
          self.location[1] = 0

      # Grab all the food from the field at this new location and store it.
      if self.diet_type == "VEGETARIAN":
        self.food_stored += world.field.remove_food(self.location)
      elif self.diet_type == "CARNIVORE":
        for prey in [
            x for x in world.creatures_by_loc[self.location[0]][self.location[1]]
            if x.diet_type == "VEGETARIAN" and x.is_alive]:
          if self.location == prey.location:
            prey.is_alive = False
            self.food_stored += prey.meat_value

    # And settle into your new location.
    world.creatures_by_loc[self.location[0]][self.location[1]].append(self)

  def eat_die_reproduce(self, world):
    """Creatures eat, possibly die, and possibly reproduce depending on food.

    Most creatures require 1 food to eat, 1 food to reproduce.  They die if they
    cannot eat. EFFICIENT creatures require 0.5 food to eat/reproduce.

    Returns: (survived, babies)
      babies: [creatures]; A list of creatures resulting from reproduction
    """
    # Got a little bit older.
    self.age += 1
    food_required = (0.5 if self.mutation=="EFFICIENT" else 1)
    # Eat, if you can (die if you can't.)
    self._eat(food_required)
    if not self.is_alive or self.food_stored < food_required:
      # No babies if, after eating, you are dead or don't have enough food.
      return []
    # Else, reproduce.
    return self._reproduce(food_required, world)

  def _eat(self, food_required):
    """Eats food_required food from food_stored; dies if not enough food.

    Arguments:
      food_required: float; amount of food the creature must eat to survive.
    """
    self.food_stored -= food_required
    if self.food_stored < 0:
      # Dead. Poor dude. :(
      self.is_alive = False

  def _reproduce(self, food_required, world):
    """Reproduces if has sufficient food.

    Arguments:
      food_required: float; Amount of food the creature must eat to survive.
      world: world; The world the creature lives in, if its babies teleport,
        they will appear somewhere else randomly on the field.
    Returns:
      [creature] length 1; A single (possibly mutated) offspring.
    """
    self.food_stored -= food_required
    return [
        Creature(
          location=self.location.copy(),
          mutation=self._get_mutation(self.reproduction_mutation_chance),
          reproduction_mutation_chance=self.reproduction_mutation_chance,
          diet_type=self.diet_type,
          randomly_teleports=self.randomly_teleports
        )
    ]

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

  def maybe_teleport(self, world):
    """If the creature teleports, teleport randomly to somewhere in the world.

    Arguments:
      world: world; The world to teleport to.
    """
    if not self.randomly_teleports:
      return

    self.location = list(np.random.choice(range(world.field.field_size), 2))