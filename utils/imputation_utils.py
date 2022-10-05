from sklearn import metrics
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
from dateutil.parser import parse
from datetime import datetime
import argparse
import fancyimpute
import pyprind
import pytz
from fancyimpute import KNN
import math

def sample_and_hold(input: pd.DataFrame, hold_period: np.array, adjust = 0):
  '''
    Implementation of "sample-and_hold" imputation, for time-varying clinical trial data such as MIMIC-III. 
    Args:
      input: pd.DataFrame, w/ charttimes in correct order
      hold_period: specific holding period, if need be specified for vitalSigns
      adjust = 0: adjusting level
  '''
  icustayid_list = list(input['icustay_id'])
  i_icustay_id = input.columns.get_loc('icustay_id')
  i_charttime = input.columns.get_loc('start_time')
  temp = np.copy(input)
  n_row, n_col = temp.shape
  last_charttime = np.empty_like(input.iloc[0, i_charttime], shape = n_row)
  last_charttime[0] = parse(temp[0, i_charttime])
  last_value = np.empty(n_col)
  last_value.fill(-float(math.inf))
  curr_stay_id = temp[0, i_icustay_id]
  
  mean_sah = np.nanmean(input.iloc[:, 4:n_col], axis = 0)
  # loop through each column
  for i in range(4,n_col):
    for j in range(n_row):
      if curr_stay_id != temp[j, i_icustay_id]:
        # start over since we've seen a new icustay_id
        last_charttime[j] = parse(temp[j, i_charttime])
        last_value = np.empty(n_col)
        last_value.fill(-float(math.inf))
        curr_stay_id = temp[j, i_icustay_id]
      if not np.isnan(temp[j, i]):
        # set the replacement if we observe one later
        last_charttime[j] = parse(temp[j,i_charttime])
        last_value[i] = temp[j, i]
      if j >= 0: 
        time_del = 0
        if (np.isnan(temp[j,i])) and (temp[j, i_icustay_id] == curr_stay_id) and (time_del <= hold_period[i-3]):
          # replacement if NaN via SAH
          if last_value[i] == -float(math.inf):
            k = j
            while (k < temp.shape[0] and np.isnan(temp[k,i]) and curr_stay_id == temp[k, i_icustay_id]):
              k += 1
            # If entire episode is Nan then replace by mean
            if k == temp.shape[0] or curr_stay_id != temp[k, i_icustay_id]:
              temp[j,i] = mean_sah[i-4]
              last_value[i] = mean_sah[i-4]
            # Else there is at least one not Nan in this episode
            else:
              last_value[i] = temp[k,i]
              temp[j,i] = temp[k,i]
          else:
            temp[j,i] = last_value[i]
    print("completed preprocessing {}".format(i))
  return temp

def preprocess_imputation(df: pd.DataFrame,  N: int, k_param: int, weights = None,  col_names_knn = None, col_names_sah = None):
  """
  Preprocesses input data frame `df` via SAH and KNN imputation
    N - KNN block size
    k - KNN parameter 
    df - initial dataframe in correct column name representation
  """
  miss_level = df.drop(labels=['subject_id', 'icustay_id', 'hadm_id','start_time'], axis = 1).isnull().sum() / df.shape[0]
  column_names = df.drop(labels = ['subject_id', 'icustay_id', 'hadm_id','start_time'], axis = 1).columns[miss_level >= 0.95]
  df_drop = df.drop(labels = ['subject_id', 'icustay_id', 'hadm_id','start_time'], axis = 1).loc[:, miss_level < 0.95] # with subject_id, icustay_id, hadm_id, start_time
  df_drop = pd.concat([df_drop, df[['subject_id', 'icustay_id', 'hadm_id','start_time']]], axis=1)
  n_count = sum(miss_level > 0.95)
  print("Removed", n_count, end= " ")
  print("columns with variable names:", *column_names, sep = "\n")
  
  # separate data for SAH and KNN imputation, keeping 'subject_id', 'icustay_id', 'hadm_id','start_time' columns intact:
  miss_level = df_drop.isnull().sum() / df_drop.shape[0]
  id_part = df_drop[['subject_id', 'icustay_id', 'hadm_id','start_time']]
  df_sah = df_drop.loc[:, (miss_level >= 0.3)]
  df_sah = pd.concat([id_part, df_sah], axis = 1)

  # remove deathtime as it doesn't need to be imputed in our case
  df_sah.drop(labels = 'deathtime', axis = 1, inplace = True)
  df_knn = df_drop.loc[:, (miss_level < 0.3)]
  
  # for high levels of missingness: sah
  hp = np.full(len(df_sah.columns),np.inf)
  temp = sample_and_hold(df_sah, hold_period = hp)
  df_sah = pd.DataFrame(data = temp, columns=df_sah.columns) # new imputed version (to combine later)
  
  # for small level of missingness: knn
  c_s = N*1000
  knn_removed_cols = df_knn[['subject_id', 'icustay_id', 'hadm_id','start_time','gender', 'dischtime']]
  df_knn_dropped_columns = df_knn.drop(labels=['subject_id', 'icustay_id', 'hadm_id','start_time','gender', 'dischtime'], axis = 1).columns
  temp = df_knn.drop(labels=['subject_id', 'icustay_id', 'hadm_id','start_time','gender', 'dischtime'], axis = 1).to_numpy()
  for i in range(0, temp.shape[0], (N*1000)):
    if (i + (N*1000) > temp.shape[0]-1):
      temp[i:temp.shape[0]-1, :] = KNN(k = k_param).fit_transform(temp[i:temp.shape[0]-1, :])
    else:
      temp[i:i+c_s, :] = KNN(k = k_param).fit_transform(temp[i:i+c_s, :]) # inputes via kNN
  df_knn_imp = pd.DataFrame(data=temp, columns = df_knn_dropped_columns)
  df_knn = knn_removed_cols.join(df_knn_imp)
  final = df_sah.set_index(['subject_id','icustay_id', 'hadm_id', 'start_time']).join(other=df_knn.set_index(['subject_id','icustay_id', 'hadm_id', 'start_time']))
  return final.reset_index(drop=False)
