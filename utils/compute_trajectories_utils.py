import numpy as np
import pandas as pd
from copy import deepcopy
import keras
from sklearn.preprocessing import StandardScaler
from functools import partial
from tqdm import tqdm

APACHE_RANGES = {
    "tempc": [(41, 4), (39, 3), (38.5, 1), (36, 0), (34, 1), (32, 2), (30, 3), (0, 4)],
    "meanbp": [(160, 4), (130, 3), (110, 2), (70, 0), (50, 2), (0, 4)],
    "heartrate": [(180, 4), (140, 3), (110, 2), (70, 0), (55, 2), (40, 3), (0, 4)],
    "ph": [(7.7, 4), (7.6, 3), (7.5, 1), (7.33, 0), (7.25, 2), (7.15, 3), (0, 4)],
    "sodium": [(180, 4), (160, 3), (155, 2), (150, 1), (130, 0), (120, 2), (111, 3), (0, 4)],
    "potassium": [(7, 4), (6, 3), (5.5, 1), (3.5, 0), (3, 1), (2.5, 2), (0, 4)],
    "creatinine": [(305, 4), (170, 3), (130, 2), (53, 0), (0, 2)],
    "wbc": [(40, 4), (20, 2), (15, 1), (3, 0), (1, 2), (0, 4)],
}

MAX_APACHE_SCORE = sum([l[-1][1] for l in APACHE_RANGES.values()]) + 12 # +12 is for max GCS score
INTERMEDIATE_REWARD_SCALING = 1

#compute the reward
def compute_reward(row):
  if row['icustay_id'] != row['icustay_id_shifted_up']: # is last timestep in this icu_stay
    return 1 if row['hospmort90day'] == 0 else -1
  
  else:
    return INTERMEDIATE_REWARD_SCALING * (-(row['apache2'] - row['apache2_shifted_up']))/MAX_APACHE_SCORE

def compute_apache2(row):
  score = 0

  for measurement, range_list in APACHE_RANGES.items():
    patient_value = row[measurement]
    for pair in range_list:
      if patient_value >= pair[0]: # If this is the current range for this value
        score += pair[1]
        break

  score += (15 - row["gcs"]) # Different calculation of score for GCS

  return score

def build_trajectories(df,state_space,action_space):
  ''' 
  This assumes that the last timewise entry for a patient is the culmination of
   their episode or 72 hours from first row is culmination and that there exists a reward column
   which is always the reward of that episode

  *************IMPORTANT**********
  I assume that the dataframe has icustay_id, hadm_id, subject_id, and charttime as columns
  and it can be sorted by charttime and end up in chronological order
  I also assume that there is a reward column in the dataset
  ********************************

  param df: the dataframe you want to build trajectories from
  param state_space: the columns of the daataframe you want to include in your state space
  '''
  
  scaler = StandardScaler()
  toscale = df[state_space]
  df[state_space] = scaler.fit_transform(toscale)

  #get the combo of variables that we'll use to distinguish between episodes
  df['info'] = df.apply(lambda x: tuple([x['subject_id'],x['hadm_id'],x['icustay_id']]),axis=1)

  #list of episodes that we'll poulate in the loop below
  episode_states = []
  
  #states prime, encoded list of states, sp[i]=the encoded rerpesentation of the ith state
  actions = []
  rewards = []
  states=[]
  done_flags=[]
  #loop through every unique value of the info tuple we had

  unique_infos = df['info'].unique().tolist()
  print("Building Trajectories...")
  for k in tqdm(range(len(unique_infos)), ncols=100):
    i = unique_infos[k]
    #extract rows of the patient whos info we are iterating on
    episode_rows = df[(df['subject_id']==i[0])&(df['hadm_id'] == i[1])&(df['icustay_id']==i[2])].sort_values('start_time')
  
    #instantiate the list of states, actions,... where the ith value in the list is the value at the ith timestep
  
    #iterate through rows which are sorted by charttime at the creation of episode_rows
    tdiff = episode_rows.iloc[0]['start_time']
    for row in range(min(18, len(episode_rows))):
      end_index = min(18, len(episode_rows)) - 1
    
      #get the action, state, reward, next state, and whether or not the sequence is done in the current timestep
      state = episode_rows[state_space].iloc[row].values.tolist()

      action = episode_rows[action_space].iloc[row].values.tolist()
      
      if row == end_index:
        reward = 1 if episode_rows['hospmort90day'].iloc[row] == 0 else -1
      else:
        reward = INTERMEDIATE_REWARD_SCALING * (-(episode_rows['apache2'].iloc[row] - episode_rows['apache2_shifted_up'].iloc[row]))/MAX_APACHE_SCORE
      dflag = 1 if row == end_index else 0

      #add the current time step info to the lists for this episode
      states.append(deepcopy(state))
      actions.append(deepcopy(action))
      rewards.append(deepcopy(reward))
      done_flags.append(deepcopy(dflag)) 
    
    #add to episodes a dictionairy with the mdp info for this episode

  actions = np.array(actions)
  rewards = np.array(rewards)
  done_flags = np.array(done_flags)
  states = np.array(states)
  print(states.mean(axis=1))
  info_dict = {
      "actions":actions,
      "rewards":rewards,
      "done_flags":done_flags,
      "states":states
  }

  # Return list of np arrays of states (one for each episode), because have to pass them through the LSTM autoencoder
  return info_dict
