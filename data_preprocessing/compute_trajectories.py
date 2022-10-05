# importing
import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())
path = Path(os.getcwd())
sys.path.append(str(path.parent.absolute()))

import pandas as pd
import numpy as np
from functools import partial
from utils.compute_trajectories_utils import compute_reward, build_trajectories, compute_apache2
from constants import DATA_FOLDER_PATH
from copy import deepcopy
from tqdm import tqdm
from datetime import datetime
from datetime import timedelta
import time
STATE_SPACE                 = [
                                'first_admit_age',
                                'gender',
                                'weight',
                                'icu_readm',
                                'elixhauser_score',
                                'sofa',
                                'sirs',
                                'gcs',
                                'heartrate',
                                'sysbp',
                                'diasbp',
                                'meanbp',
                                'shockindex',
                                'resprate',
                                'tempc',
                                'spo2',
                                'potassium',
                                'sodium',
                                'chloride',
                                'glucose',
                                'bun',
                                'creatinine',
                                'magnesium',
                                'calcium',
                                'ionizedcalcium',
                                'carbondioxide',
                                'bilirubin',
                                'albumin',
                                'hemoglobin',
                                'wbc',
                                'platelet',
                                'ptt',
                                'pt',
                                'inr',
                                'ph',
                                'pao2',
                                'paco2',
                                'base_excess',
                                'bicarbonate',
                                'lactate',
                                'urineoutput',
                                'iv_total',
                                'cum_fluid_balance',
                                'vaso_total',
    ]

ICUTIME_CUTOFF_DAYS         = 5
IMPUTED_DATAFRAME_PATH      = os.path.join(DATA_FOLDER_PATH, "imputed.pkl")
# ACTION_DICT IS SHARED WITH discretize_actions.py
ACTION_DICT                 = {
                                'peep' : [5, 7, 9, 11, 13, 15, 1000000000],
                                'fio2' : [30, 35, 40, 45, 50, 55, 1000000000],
                                'adjusted_tidal_volume' : [0, 5, 7.5, 10, 12.5, 15, 10000000000]
                                }
df = pd.read_pickle(IMPUTED_DATAFRAME_PATH)

# Change gender to numerical data
print("Transforming gender into numerical data...")
df['gender'] = df['gender'].apply(lambda x: 1 if x == 'F' else 0)

# Compute reward 
print("Computing intermediate reward...")
df = df.sort_values(by=['icustay_id','start_time'])
df['icustay_id_shifted_up'] = df['icustay_id'].shift(-1)
df['icustay_id_shifted_down'] = df['icustay_id'].shift(1)
df['apache2'] = df.apply(compute_apache2, axis=1)
df['apache2_shifted_up'] = df['apache2'].shift(-1)

# Compute trajectories
MDP_dataset_dict = build_trajectories(
  df,
  state_space=list(filter(lambda x: x in list(df.columns), STATE_SPACE)),   # Remove from state space columns that were removed by imputation
  action_space=list(ACTION_DICT.keys())
  )

DATA_DIR_PATH       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

make_dir = ['states', 'rewards', 'actions', 'done_flags']

for directory in make_dir: 
  if not os.path.exists(os.path.join(DATA_FOLDER_PATH,directory)):
      os.makedirs(os.path.join(DATA_FOLDER_PATH,directory))

print("Building of trajectories completed")
np.save(os.path.join(DATA_FOLDER_PATH,"states/raw_states.npy"), MDP_dataset_dict["states"])
np.save(os.path.join(DATA_FOLDER_PATH,"rewards/rewards_with_intermediate_fixed.npy"), MDP_dataset_dict["rewards"])
np.save(os.path.join(DATA_FOLDER_PATH,"actions/3dactions_not_binned.npy"), MDP_dataset_dict["actions"])
np.save(os.path.join(DATA_FOLDER_PATH,"done_flags/done_flags.npy"), MDP_dataset_dict["done_flags"])
print("Saved data to files in data folder")
