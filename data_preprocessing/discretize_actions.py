# Separate each action setting into bins (see ACTION_DICT below) and assign an index to each 
# possible combination of bins. Save actions encoded using this index.
import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())
path = Path(os.getcwd())
sys.path.append(str(path.parent.absolute()))

import itertools
from functools import partial
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from constants import DATA_FOLDER_PATH

ACTION_DICT                 = {
                                'peep' : [5, 7, 9, 11, 13, 15, 1000000000],
                                'fio2' : [30, 35, 40, 45, 50, 55, 1000000000],
                                'adjusted_tidal_volume' : [0, 5, 7.5, 10, 12.5, 15, 10000000000]
                                }
          
def bin_action(bin_list, value):
  # Bin action
  idx = 0
  while value > bin_list[idx] and idx < len(bin_list):
    idx += 1

  return idx

actions = np.load(os.path.join(DATA_FOLDER_PATH, "actions/3dactions_not_binned.npy"))

# Get all possible combinations of bin indices (i.e. [[0,0,0], [0,0,1],...])
indices_lists = [[i for i in range(len(ACTION_DICT[action]))] for action in ACTION_DICT]
possibilities = list(itertools.product(*indices_lists))
possibility_dict = {}

# Create dictionary mapping each possible combination to an index
for i, possibility in enumerate(possibilities):
  possibility_dict[possibility] = i

df = pd.DataFrame(data=actions, columns=["peep", "fio2", "adjusted_tidal_volume"])

# Bin actions in dataframe
for action in ACTION_DICT:
    df[action] = df[action].apply(partial(bin_action, ACTION_DICT[action]))

binned_actions_array = df.to_numpy()

# Save 3D binned actions
np.save(os.path.join(DATA_FOLDER_PATH, "actions/3Ddiscretized_actions.npy"), binned_actions_array)

int_actions = []
# Get corresponding index for each action 
for ele in binned_actions_array:
  int_actions.append(possibility_dict[tuple(ele)])

int_actions = np.array(int_actions)

# Save 1D discretized actions
np.save(os.path.join(DATA_FOLDER_PATH, "actions/1Ddiscretized_actions.npy"), int_actions)
