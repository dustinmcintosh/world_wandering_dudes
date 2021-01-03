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

import sys
sys.path.insert(1, sys.path[0]+'/..')

from SET_ME import TMP_DIR
from world import World, DailyHistory

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
    print("Will save new data")
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
        'field_size',
        'food_density']
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
        'field_size': 'int64',
        'food_density': 'float64'})

  food_density = .03
  stable_threshold=100

  num_steps_array = range(60, 70, 10)
  num_trials = 1
  field_size = 100

  for i, num_steps in enumerate(num_steps_array):
    for trial in range(num_trials):
      print("fraction done:",
            np.round((i*num_trials+trial)/(len(num_steps_array)*num_trials), 2))
      this_world = World(field_size,
                         food_density,
                         int(np.round(field_size**2*food_density)),
                         food_spoils=True,
                         creatures_randomly_teleport=True)
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
          'field_size': this_world.field.field_size,
          'food_density': food_density}
      data = pd.concat([data, pd.DataFrame(this_df, index=[i])])

  survived_data = data[data['creatures_survived']]
  frac_survived_df = data.groupby(
      ['steps_per_day', 'field_size']).agg(
          {'creatures_survived': [frac_true, d_frac_true]}).reset_index()

  fig1,ax1 = plt.subplots(1, 1, figsize = (6, 4))
  fig2,ax2 = plt.subplots(1, 1, figsize = (6, 4))
  fig3,ax3 = plt.subplots(1, 1, figsize = (6, 4))
  fig4,ax4 = plt.subplots(1, 1, figsize = (6, 4))

  ax1.plot([72.4, 72.4], [-.5, 1.5], '-.', color='0.8', label=None)
  # data.groupby('steps_per_day').agg({'creatures_survived': frac_true}).plot(ax=ax)
  for fs in sorted(frac_survived_df['field_size'].unique()):
    this_field_size_survival_data = frac_survived_df[frac_survived_df['field_size']==fs]
    ax1.errorbar(
        x=this_field_size_survival_data['steps_per_day'],
        y=this_field_size_survival_data['creatures_survived']['frac_true'],
        yerr=this_field_size_survival_data['creatures_survived']['d_frac_true'],
        fmt='.', label="%i" % (fs)
    )
  ax1.set_ylim(-0.05, 1.05)
  # ax[0,1].errorbar(x=survived_data['steps_per_day'],
  #             y=survived_data['avg_births'],
  #             yerr=survived_data['sem_births'],
  #             fmt='b.', label='Births')'
  ax1.set_xlabel('Steps per day (food density = %.02f)' % (food_density))
  ax1.set_ylabel('frac sims w/ creatures after 200 days')
  ax1.legend(title="Linear Field Size ($\sqrt{M}$)")

  ax1.plot([72.4, 72.4], [-.5, 1.5], '-.', color='0.8', label=None) # ax[0,1].
  for fs in sorted(survived_data['field_size'].unique()):
    this_field_size_survived_data = survived_data[survived_data['field_size']==fs]
    ax2.errorbar(
        x=this_field_size_survived_data['steps_per_day'],
        y=this_field_size_survived_data['avg_num_creatures']/np.ceil(fs**2*food_density),
        yerr=this_field_size_survived_data['sem_num_creatures']/np.ceil(fs**2*food_density),
        fmt='.', label="%i" % (fs)
    )
    ax3.errorbar(
        x=this_field_size_survived_data['avg_births']/this_field_size_survived_data['avg_num_creatures'],
        y=this_field_size_survived_data['avg_deaths']/this_field_size_survived_data['avg_num_creatures'],
        xerr=np.sqrt((this_field_size_survived_data['sem_births']/this_field_size_survived_data['avg_num_creatures'])**2 +
            (this_field_size_survived_data['avg_births']*this_field_size_survived_data['sem_num_creatures']/this_field_size_survived_data['avg_num_creatures']**2)**2),
        yerr=np.sqrt((this_field_size_survived_data['sem_deaths']/this_field_size_survived_data['avg_num_creatures'])**2 +
            (this_field_size_survived_data['avg_deaths']*this_field_size_survived_data['sem_num_creatures']/this_field_size_survived_data['avg_num_creatures']**2)**2),
        fmt = '.', errorevery=5, label="%i" % (fs)
    )
    ax4.errorbar(
        x=this_field_size_survived_data['steps_per_day'] +
            np.random.choice(np.arange(-1, 2.1, .1), this_field_size_survived_data['steps_per_day'].shape[0]),
        y=this_field_size_survived_data['avg_births']/this_field_size_survived_data['avg_num_creatures'],
        yerr=np.sqrt((this_field_size_survived_data['sem_births']/this_field_size_survived_data['avg_num_creatures'])**2 +
            (this_field_size_survived_data['avg_births']*this_field_size_survived_data['sem_num_creatures']/this_field_size_survived_data['avg_num_creatures']**2)**2),
        fmt='.', label="%i" % (fs)
    )
  ax4.plot([72, 200], [0.315, 0.315], '-.', color='0.8', label=None)
  ax4.plot([72, 200], [0.3333, 0.3333], '-.', color='0.8', label=None)

  n_array = np.arange(72, 200)

  avg_n = 0.908777*n_array**0.871139
  # sigma_n = 0.232983*n_array**0.776118
  p_0 = (1-food_density)**avg_n
  p_1 = avg_n*food_density*(1-food_density)**(avg_n-1)
  p_2 = avg_n**2/2*food_density**2*(1-food_density)**(avg_n-2)
  p_2plus = 1-p_0-p_1

  ax2.plot(n_array, 1/3*(p_2plus-p_0)/(food_density*avg_n*2*1/8*(p_1+p_2)), label=None)

  ax2.set_ylim(-0.05, 0.85)
  ax2.set_xlabel('Steps per day (food density = %.02f)' % (food_density))
  ax2.set_ylabel('Avg creatures / food sprout rate')
  ax2.legend(title="Linear Field Size ($\sqrt{M}$)")

  ax3.set_xlabel('Births per Creature')
  ax3.set_ylabel('Deaths per Creature')
  ax3.set_aspect('equal')
  ax3.legend(title="Linear Field Size ($\sqrt{M}$)")

  ax4.set_xlabel('Steps per day (%.02f food density)' % (food_density))
  ax4.set_ylabel('Births per Creature')
  ax4.legend(title="Linear Field Size ($\sqrt{M}$)")

  fig1.savefig(TMP_DIR + "frac_survive.png", fmt='png ')
  fig2.savefig(TMP_DIR + "equil_n.png", fmt='png')
  fig3.savefig(TMP_DIR + "births_v_deaths.png", fmt='png')
  fig4.savefig(TMP_DIR + "births_v_n.png", fmt='png')
  plt.close()

  with open(TMP_DIR + "data.pkl", "wb") as f:
    pickle.dump(data, f)

if __name__ == "__main__":
  main()