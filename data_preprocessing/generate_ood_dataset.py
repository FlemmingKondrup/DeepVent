# Generate out-of-distribution dataset corresponding to patients that have one feature in top or bottom 1% 
# of entire dataset
# importing
import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())
path = Path(os.getcwd())
sys.path.append(str(path.parent.absolute()))
import pandas as pd
import numpy as np
import scipy.stats as st
import pickle

from d3rlpy.dataset import MDPDataset

from utils.load_utils import load_data
from constants import DATA_FOLDER_PATH

# Get full dataset without split
mdpdataset = load_data("raw", "no_intermediate", no_split=True)

print(len(mdpdataset.observations))
print(len(mdpdataset.actions))
print(len(mdpdataset.rewards))
print(len(mdpdataset.terminals))

print(np.count_nonzero(np.isnan(mdpdataset.observations)))
print(np.count_nonzero(np.isnan(mdpdataset.actions)))
print(np.count_nonzero(np.isnan(mdpdataset.rewards)))
print(np.count_nonzero(np.isnan(mdpdataset.terminals)))

# All features in our state space
STATE_SPACE                 = [
                                'first_admit_age', # 0
                                'gender', #1
                                'weight',#2
                                'icu_readm',           #3
                                'elixhauser_score', #4
                                'sofa',#5
                                'sirs',#6
                                'gcs',#7
                                'heartrate',#8
                                'sysbp',#9
                                'diasbp',#10
                                'meanbp',#11
                                'shockindex',#12
                                'resprate',#13
                                'tempc',#14
                                'spo2',#15
                                'potassium', #16
                                'sodium',#17
                                'chloride',#18
                                'glucose',#19
                                'bun',#20
                                'creatinine', #21
                                'magnesium',#22
                                'carbondioxide',#23
                                'hemoglobin',#24
                                'wbc',#25
                                'platelet',#26
                                'ptt',#27
                                'pt',#28
                                'inr',#29
                                'ph',#30
                                'paco2', #31
                                'base_excess', #32
                                'bicarbonate',#33
                                'urineoutput',#34
                                'iv_total',#35
                                'cum_fluid_balance',#36
                                'vaso_total',#37
    ]

train_indices = []
test_indices = []
def split_non_binary(proportion, param_name, param_index):
    # Split episodes according to if initial state has parameter param_name in top or bottom x% (where x = proportion) of whole dataset

    threshhold = st.norm.ppf(1-proportion) # States are normalized according to standard normal distribution

    # Get indices of episodes corresponding to top x% (where x = proportion)
    for i, episode in enumerate(mdpdataset.episodes):
        if episode.observations[0][param_index] > threshhold:
            test_indices.append(i)
        else:
            train_indices.append(i)

    threshhold = st.norm.ppf(proportion)

    # Get indices of episodes corresponding to bottom % (where x = proportion)
    for i, episode in enumerate(mdpdataset.episodes):
        if episode.observations[0][param_index] > threshhold:
            train_indices.append(i)
        else:
            test_indices.append(i)

# Indices not to be considered because get imputed out 
FORBIDDEN_INDICES = [16,17,18,19,20,21,22,24,26,32]
for i in range(len(STATE_SPACE)):
    print("Splitting", STATE_SPACE[i])
    # First condition checks if this is a binary feature in which case we can't get top and bottom 1% because there are only 2 possible values
    if len(np.unique(mdpdataset.observations[:, i])) <= 2 or i in FORBIDDEN_INDICES:
        continue
    split_non_binary(0.0001, STATE_SPACE[i], i)
    
train_indices = np.unique(np.array(train_indices))
test_indices = np.unique(np.array(test_indices))

test_episodes = []
train_episodes = []
for i, episode in enumerate(mdpdataset.episodes):
    if i in test_indices:
        test_episodes.append(episode)
    else:
        train_episodes.append(episode)

print("OOD no. episodes:", len(test_episodes))
print("In distribution no. episodes:", len(train_episodes))
with open(f"{DATA_FOLDER_PATH}/ood_test.pkl", "wb") as fp:
    pickle.dump(test_episodes, fp)

with open(f"{DATA_FOLDER_PATH}/ood_train.pkl", "wb") as fp:
    pickle.dump(train_episodes, fp)