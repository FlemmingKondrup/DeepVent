import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())
path = Path(os.getcwd())
sys.path.append(str(path.parent.absolute()))

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import sem
import itertools
from d3rlpy.dataset import MDPDataset
from d3rlpy.algos import DiscreteCQL, DiscreteBC, DoubleDQN, DiscreteRandomPolicy
from d3rlpy.ope import DiscreteFQE
import numpy as np
from scipy.stats import sem
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.load_utils import *
from constants import DATA_FOLDER_PATH, FINAL_POLICIES_PATH
print("Making U Curves")
ACTION_DICT                 = {
                                'peep' : [5, 7, 9, 11, 13, 15, 1000000000],
                                'fio2' : [30, 35, 40, 45, 50, 55, 1000000000],
                                'adjusted_tidal_volume' : [0, 2.5, 5, 7.5,10,12.5,15,10000000000]
                                }

indices_lists = [[i for i in range(len(ACTION_DICT[action]))] for action in ACTION_DICT]
possibilities = list(itertools.product(*indices_lists))
inv_action_map = {}

for i, possibility in enumerate(possibilities):
  inv_action_map[i] = possibility

def make_df_diff(op_actions,phys_actions):
    op_peep_med = []
    op_fio2_med = []
    op_adjTV_med = []
    for action in op_actions:
        peep, fio2, adjTV = inv_action_map[action]
        op_peep_med.append(peep)
        op_fio2_med.append(fio2)
        op_adjTV_med.append(adjTV)
    phys_peep_med = []
    phys_fio2_med = []
    phys_adjTV_med = []
    for action in phys_actions:
        peep, fio2, adjTV = inv_action_map[action]
        phys_peep_med.append(peep)
        phys_fio2_med.append(fio2)
        phys_adjTV_med.append(adjTV)
    peep_diff = np.array(op_peep_med) - np.array(phys_peep_med)
    fio2_diff = np.array(op_fio2_med) - np.array(phys_fio2_med)
    adjTv_diff = np.array(op_adjTV_med) - np.array(phys_adjTV_med)
    
    df_diff = pd.DataFrame()
    df_diff['mort'] = np.array(mortality_outcome)
    df_diff['peep_diff'] = peep_diff
    df_diff['FiO2_diff'] = fio2_diff
    df_diff['adjTV_diff'] = adjTv_diff
    return df_diff

def make_u_plot_(df_diff, ac_num = 7, model_name_ac=None):
    bin_action_difference_levels = []
    mort_difference_level = []
    mort_stddev_difference_level = []

     # ex: start from difference of size -6 up to 6 say...
    for i in range((-1 * (ac_num - 1)), (ac_num-1), 1):
        try:
            new_df = df_diff.loc[(df_diff[model_name_ac] == i)]
            res = sum(new_df['mort'])/float(len(new_df))
            if len(new_df) >= 2:
                bin_action_difference_levels.append(i)
                mort_difference_level.append(res)
                mort_stddev_difference_level.append(sem(new_df['mort']))
        except ZeroDivisionError:
            pass
    return bin_action_difference_levels, mort_difference_level, mort_stddev_difference_level

def make_u_plot_multiple(df_diff, ac_num = 7, model_name_ac=None):
    bin_action_difference_levels = []
    mort_difference_level = []
    mort_stddev_difference_level = []

     # ex: start from difference of size -6 up to 6 say...
    for i in range((-1 * (ac_num - 1)), (ac_num-1), 1):
        try:
            new_df = df_diff.loc[(df_diff[model_name_ac] == i)]
            res = sum(new_df['mort'])/float(len(new_df))
            if len(new_df) >= 2:
                bin_action_difference_levels.append(i)
                mort_difference_level.append(res)
                mort_stddev_difference_level.append(sem(new_df['mort']))
        except ZeroDivisionError:
            pass
    return bin_action_difference_levels, mort_difference_level, mort_stddev_difference_level


#### ADDING AVERAGING OVER POLICIES HERE: Similar to `grouped_action_bar_plot.py`
# Write the paths for the folder containing multiple policies that need to be averaged:

# Plot CQL-Intermediate versus DDQN-No intermediate
POLICY_MULTIPLE_PATH_CQL = f'{FINAL_POLICIES_PATH}/raw_intermediate/CQL'
POLICY_MULTIPLE_PATH_DQN = f'{FINAL_POLICIES_PATH}/raw_no_intermediate/DQN'
CQL_POLICY_PATH_LIST = os.listdir(POLICY_MULTIPLE_PATH_CQL)
DQN_POLICY_PATH_LIST = os.listdir(POLICY_MULTIPLE_PATH_DQN)
NUM_POLICIES = len(CQL_POLICY_PATH_LIST) # Number of policies to be averaged

# Accumulated differences
CQL_POLICY_DIFF = None
DQN_POLICY_DIFF = None

ACTIONS_PATH=f"{DATA_FOLDER_PATH}/actions/1Ddiscretized_actions.npy"
STATES_PATH=f"{DATA_FOLDER_PATH}/states/raw_states.npy"
REWARDS_PATH=f"{DATA_FOLDER_PATH}/rewards/rewards_without_intermediate.npy"
DONE_FLAGS_PATH=f"{DATA_FOLDER_PATH}/done_flags/done_flags.npy"

# For each policy
for policy in range(5):
    print(f"Processing run {policy}")
    states = np.load(STATES_PATH)
    actions = np.load(ACTIONS_PATH)
    rewards = np.load(REWARDS_PATH)
    done_flags = np.load(DONE_FLAGS_PATH)
    test_data, train_data = load_data(states = "raw", rewards = "no_intermediate", index_of_split=policy)

    ### DDQN:
    model = DoubleDQN()
    model.build_with_dataset(train_data)
    model.load_model(f"{POLICY_MULTIPLE_PATH_DQN}/{DQN_POLICY_PATH_LIST[policy]}/model_2000000.pt")

    ### CQL:
    cql = DiscreteCQL()
    cql.build_with_dataset(train_data)
    cql.load_model(f"{POLICY_MULTIPLE_PATH_CQL}/{CQL_POLICY_PATH_LIST[policy]}/model_2000000.pt")
   
    #### USE THE TRAINING MDP:
    phys = test_data.actions
    ddqn = model.predict(test_data.observations)
    cons_policy = cql.predict(test_data.observations)

    dflags = done_flags
    rewards = rewards
    mortality_outcome = []
    i = 0
    lastI = 0
   
    while i < len(test_data.rewards):
        if test_data.rewards[i] == 1:
            while lastI < i:
                mortality_outcome.append(0)
                lastI+=1
            mortality_outcome.append(0)
            lastI+=1
        elif test_data.rewards[i] == -1:
            while lastI < i:
                mortality_outcome.append(1)
                lastI+=1
                #print(i, lastI)
            mortality_outcome.append(1)
            lastI+=1
        i += 1
    if policy == 0:
        CQL_POLICY_DIFF = make_df_diff(cons_policy, phys)
    else:
        pd.concat([CQL_POLICY_DIFF, make_df_diff(cons_policy, phys)], axis = 1)
    if policy == 0:
        DQN_POLICY_DIFF = make_df_diff(ddqn, phys)
    else:
        pd.concat([DQN_POLICY_DIFF, make_df_diff(ddqn, phys)], axis = 1)

##### PLOTS FOR DQN:
bin_med_peep, mort_peep, mort_std_peep = make_u_plot_(df_diff = DQN_POLICY_DIFF, model_name_ac = 'peep_diff')
bin_med_FiO2, mort_FiO2, mort_std_FiO2 = make_u_plot_(df_diff = DQN_POLICY_DIFF, model_name_ac = 'FiO2_diff')
bin_med_adjTV, mort_adjTV, mort_std_adjTV = make_u_plot_(df_diff = DQN_POLICY_DIFF, model_name_ac = 'adjTV_diff')

# general code for 1 plot
f, ax = plt.subplots(3, 2, figsize = (8.5,6))
f.tight_layout()
ax[0,0].plot(bin_med_peep, mort_peep, color = 'g')
ax[0,0].fill_between(bin_med_peep,np.array(mort_peep) - 1*mort_std_peep,  
                 np.array(mort_peep) + 1*mort_std_peep, color='lightgreen')
ax[0,0].set_title('U Curve Plot for PEEP (DDQN)')
ax[0,0].set_xticks([i for i in range(-6, 7, 1)])
ax[0,0].grid()


ax[1,0].plot(bin_med_FiO2, mort_FiO2, color = 'g')
ax[1,0].fill_between(bin_med_FiO2,np.array(mort_FiO2) - 1*mort_std_FiO2,  
                 np.array(mort_FiO2) + 1*mort_std_FiO2, color='lightgreen')
ax[1,0].set_title('U Curve Plot for FiO2 (DDQN)')
ax[1,0].set_xticks([i for i in range(-6, 7, 1)])
ax[1,0].grid()


ax[2,0].plot(bin_med_adjTV, mort_adjTV, color = 'g')
ax[2,0].fill_between(bin_med_adjTV,np.array(mort_adjTV) - 1*mort_std_adjTV,  
               np.array(mort_adjTV) + 1*mort_std_adjTV, color='lightgreen')
ax[2,0].set_title('U Curve Plot for adjTV (DDQN)')
ax[2,0].set_xticks([i for i in range(-6, 7, 1)])
ax[2,0].grid()

# Putting everything together
df_diff2 = make_df_diff(cons_policy, phys)
bin_med_peep, mort_peep, mort_std_peep = make_u_plot_(df_diff = CQL_POLICY_DIFF, model_name_ac = 'peep_diff')
bin_med_FiO2, mort_FiO2, mort_std_FiO2 = make_u_plot_(df_diff = CQL_POLICY_DIFF, model_name_ac = 'FiO2_diff')
bin_med_adjTV, mort_adjTV, mort_std_adjTV = make_u_plot_(df_diff = CQL_POLICY_DIFF, model_name_ac = 'adjTV_diff')


# general code for 1 plot
ax[0,1].plot(bin_med_peep, mort_peep, color = 'b')
ax[0,1].fill_between(bin_med_peep,np.array(mort_peep) - 1*mort_std_peep,  
                 np.array(mort_peep) + 1*mort_std_peep, color='lightblue')
ax[0,1].set_title('U Curve Plot for PEEP (DeepVent)')
ax[0,1].set_xticks([i for i in range(-6, 7, 1)])
ax[0,1].grid()


ax[1,1].plot(bin_med_FiO2, mort_FiO2, color = 'b')
ax[1,1].fill_between(bin_med_FiO2,np.array(mort_FiO2) - 1*mort_std_FiO2,  
                 np.array(mort_FiO2) + 1*mort_std_FiO2, color='lightblue')
ax[1,1].set_title('U Curve Plot for FiO2 (DeepVent)')
ax[1,1].set_xticks([i for i in range(-6, 7, 1)])
ax[1,1].grid()


ax[2,1].plot(bin_med_adjTV, mort_adjTV, color = 'b')
ax[2,1].fill_between(bin_med_adjTV,np.array(mort_adjTV) - 1*mort_std_adjTV,  
                 np.array(mort_adjTV) + 1*mort_std_adjTV, color='lightblue')
ax[2,1].set_title('U Curve Plot for adjTV (DeepVent)')
ax[2,1].set_xticks([i for i in range(-6, 7, 1)])
ax[2,1].grid()

ax[2,0].set_xlabel('Change in bins of physician from policy', fontsize = 13)
ax[2,1].set_xlabel('Change in bins of physician from policy', fontsize = 13)

ax[0,0].set_ylabel('Mortality level', fontsize = 11)
ax[1,0].set_ylabel('Mortality level', fontsize = 11)
ax[2,0].set_ylabel('Mortality level', fontsize = 11)
ax[0,1].set_ylabel('Mortality level', fontsize = 11)
ax[1,1].set_ylabel('Mortality level', fontsize = 11)
ax[2,1].set_ylabel('Mortality level', fontsize = 11)

f.subplots_adjust(hspace = 0.5)
plt.show(block = True)
# f.savefig('temp.png', bbox_inches = 'tight',dpi = 'figure')