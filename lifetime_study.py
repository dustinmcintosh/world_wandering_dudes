from SET_ME import TMP_DIR
from world import World, DailyHistory

import argparse
import glob
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd
import pickle
from scipy import stats

def frac_true(series):
  listy = series.tolist()
  return sum(listy)/len(listy)

def d_frac_true(series):
  listy = series.tolist()
  return np.sqrt(sum(listy)/len(listy)*(1-sum(listy)/len(listy))/len(listy))


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--data_pkl", "-dp", help="previous data pkl")
  args = parser.parse_args()
  if args.data_pkl:
    # Reuse old world.
    print("Reusing data at", args.data_pkl)
    with open(TMP_DIR + args.data_pkl, "rb") as f:
      data=pickle.load(f)
  else:
    print("Will save new data ", args.data_pkl)
    data = pd.DataFrame(columns=[
        'steps_per_day',
        'trial',
        'avg_num_creatures',
        'sem_num_creatures',
        'avg_births',
        'sem_births',
        'avg_deaths',
        'sem_deaths',
        'creatures_survived',
        'field_size']
    ).astype({
        'steps_per_day': 'int32',
        'trial': 'int32',
        'avg_num_creatures': 'float64',
        'sem_num_creatures': 'float64',
        'avg_births': 'float64',
        'sem_births': 'float64',
        'avg_deaths': 'int32',
        'sem_deaths': 'float64',
        'creatures_survived': 'bool',
        'field_size': 'int64'})

  food_density = .03
  stable_threshold=100

  x_vals = range(100, 120, 20)
  num_trials = 1
  field_size = 13

  for i, num_steps in enumerate(x_vals):
    for trial in range(num_trials):
      print("fraction done:",
            np.round((i*num_trials+trial)/(len(x_vals)*num_trials), 2))
      this_world = World(field_size,
                         food_density,
                         int(np.round(field_size**2*food_density/2)),
                         food_spoils=True)
      for j in range(200):
        this_world.pass_day(num_steps)
      this_world.plot_history(save_plot=True)
      creature_history = [x.num_creatures for x in this_world.history[stable_threshold:]]
      birth_history = [x.num_births for x in this_world.history[stable_threshold:]]
      death_history = [x.num_deaths for x in this_world.history[stable_threshold:]]
      this_df = {
          'steps_per_day': num_steps,
          'trial': trial,
          'avg_num_creatures': np.mean(creature_history),
          'sem_num_creatures': stats.sem(creature_history),
          'avg_births': np.mean(birth_history),
          'sem_births': stats.sem(birth_history),
          'avg_deaths': np.mean(death_history),
          'sem_deaths': stats.sem(death_history),
          'creatures_survived': this_world.history[-1].num_creatures > 0,
          'field_size': this_world.field.field_size}
      data = pd.concat([data, pd.DataFrame(this_df, index=[i])])

  survived_data = data[data['creatures_survived']]
  frac_survived_df = data.groupby(
      ['steps_per_day', 'field_size']).agg(
          {'creatures_survived': [frac_true, d_frac_true]}).reset_index()


  fig,ax = plt.subplots(2, 2, figsize = (12, 8))
  # data.groupby('steps_per_day').agg({'creatures_survived': frac_true}).plot(ax=ax)
  for fs in sorted(frac_survived_df['field_size'].unique()):
    this_field_size_survival_data = frac_survived_df[frac_survived_df['field_size']==fs]
    ax[0,0].errorbar(x=this_field_size_survival_data['steps_per_day'],
                y=this_field_size_survival_data['creatures_survived']['frac_true'],
                yerr=this_field_size_survival_data['creatures_survived']['d_frac_true'],
                fmt='.', label="field_size: %i" % (fs))
  # ax[0,1].errorbar(x=survived_data['steps_per_day'],
  #             y=survived_data['avg_births'],
  #             yerr=survived_data['sem_births'],
  #             fmt='b.', label='Births')'
  ax[0,0].set_xlabel('Steps per day (%f food density)' % (food_density))
  ax[0,0].set_ylabel('frac sims w/ creatures after 200 days')
  ax[0,0].legend()

  for fs in sorted(survived_data['field_size'].unique()):
    this_field_size_survived_data = survived_data[survived_data['field_size']==fs]
    ax[0,1].errorbar(x=this_field_size_survived_data['steps_per_day'],
                     y=this_field_size_survived_data['avg_num_creatures']/np.ceil(fs**2*food_density),
                     yerr=this_field_size_survived_data['sem_num_creatures']/np.ceil(fs**2*food_density),
                     fmt='.', label="field_size: %i" % (fs))
    ax[1,0].errorbar(x=this_field_size_survived_data['avg_births']/this_field_size_survived_data['avg_num_creatures'],
                     y=this_field_size_survived_data['avg_deaths']/this_field_size_survived_data['avg_num_creatures'],
                     xerr=np.sqrt((this_field_size_survived_data['sem_births']/this_field_size_survived_data['avg_num_creatures'])**2 +
                        (this_field_size_survived_data['avg_births']*this_field_size_survived_data['sem_num_creatures']/this_field_size_survived_data['avg_num_creatures']**2)**2),
                     yerr=np.sqrt((this_field_size_survived_data['sem_deaths']/this_field_size_survived_data['avg_num_creatures'])**2 +
                        (this_field_size_survived_data['avg_deaths']*this_field_size_survived_data['sem_num_creatures']/this_field_size_survived_data['avg_num_creatures']**2)**2),
                     fmt = '.', errorevery=3, label="field_size: %i" % (fs))
    ax[1,1].errorbar(x=this_field_size_survived_data['steps_per_day']+np.random.choice(range(-4, 5), this_field_size_survived_data['steps_per_day'].shape[0]),
                     y=this_field_size_survived_data['avg_births']/this_field_size_survived_data['avg_num_creatures'],
                     yerr=np.sqrt((this_field_size_survived_data['sem_births']/this_field_size_survived_data['avg_num_creatures'])**2 +
                         (this_field_size_survived_data['avg_births']*this_field_size_survived_data['sem_num_creatures']/this_field_size_survived_data['avg_num_creatures']**2)**2),
                     fmt='.', label="field_size: %i" % (fs))

  ax[0,1].set_xlabel('Steps per day (%f food density)' % (food_density))
  ax[0,1].set_ylabel('Avg creatures day 100-200 / food sprouted per day')
  ax[0,1].legend()

  ax[1,0].set_xlabel('Births per Creature')
  ax[1,0].set_ylabel('Deaths per Creature')
  ax[1,0].set_aspect('equal')
  ax[1,0].legend()

  ax[1,1].set_xlabel('Steps per day (0.01 food density)')
  ax[1,1].set_ylabel('Births per Creature')
  ax[1,1].legend()

  fig.savefig(TMP_DIR + "lifetime_summmary.png", fmt='png')
  plt.close()

  with open(TMP_DIR + "data.pkl", "wb") as f:
    pickle.dump(data, f)

if __name__ == "__main__":
  main()