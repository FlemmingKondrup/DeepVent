from d3rlpy.algos import DiscreteCQL, CQL, DiscreteBC, BC, DiscreteRandomPolicy, RandomPolicy, DoubleDQN, SAC
from d3rlpy.dataset import MDPDataset
from d3rlpy.ope import DiscreteFQE
from d3rlpy.algos import DiscreteCQL, DoubleDQN
from d3rlpy.metrics.scorer import continuous_action_diff_scorer, soft_opc_scorer, initial_state_value_estimation_scorer, average_value_estimation_scorer, discrete_action_match_scorer, td_error_scorer, discounted_sum_of_advantage_scorer, value_estimation_std_scorer, soft_opc_scorer, dynamics_observation_prediction_error_scorer
from d3rlpy.ope import DiscreteFQE, FQE
import numpy as np
import pickle
import pandas as pd
from scipy.stats import sem
from typing import Any, Callable, Iterator, List, Tuple, Union, cast
import matplotlib.pyplot as plt
from load_utils import load_data
import copy
from constants import FINAL_POLICIES_PATH
import os 
# Assuming load_utils.py is in the same directory 
train_data, test_data = load_data("ood", "ood", None)

def mortality_expectedReturn(data, algo, index):
    ### Loading policy 
    if algo == "CQL":
        model = DiscreteCQL()
        POLICY_PATH = os.path.join(FINAL_POLICIES_PATH, 'ood/CQL/run_' + str(index) + "/model_2000000.pt")
        FQE_POLICY_PATH = os.path.join(FINAL_POLICIES_PATH, 'ood/CQL/run_' + str(index) + "/FQE_2500000.pt")
    elif algo =="DDQN": 
        model = DoubleDQN()
        POLICY_PATH = os.path.join(FINAL_POLICIES_PATH, 'ood/DQN/run_' + str(index) + "/model_2000000.pt")
        FQE_POLICY_PATH = os.path.join(FINAL_POLICIES_PATH, 'ood/DQN/run_' + str(index) + "/FQE_2500000.pt")
    else: 
        raise "Wrong algo input. Must be CQL or DDQN"
    model.build_with_dataset(data)
    model.load_model(POLICY_PATH)
    FQEmodel = DiscreteFQE(algo=model)
    FQEmodel.build_with_dataset(data)
    FQEmodel.load_model(FQE_POLICY_PATH)
    model_eval = FQEmodel

    # evaluating the mortality
    physician_performance = []
    phys_actions = []
    phys_peep_action = []
    phys_fio2_action = []
    phys_vaso_total_action = []
    counter = 0
    total_values = []
    observatins = []
    mortalities = []
    for episode in data:
        q_val = []
        for index in range(len(episode.actions)):
            action = episode.actions[index]
            observation = episode.observations[index]
            reward = episode.rewards[index]
        if -1.0 in episode.rewards: 
            mortalities.append(1)
        else:
            mortalities.append(0)

        actions = model_eval.predict([observation])

        observatins.append(observation[0])
        values = model_eval.predict_value([observation], [action])

        q_val.append(values)
        counter = counter + len(episode.actions)
        physician_performance.append(q_val)  

    phys_score = 0.0
    for arr in physician_performance:
        phys_score += np.mean(arr)
    phys_score /= len(physician_performance)

    all_phys_performance = []
    for arr in physician_performance:
        all_phys_performance.extend(arr)

    pp = pd.Series(all_phys_performance)
    phys_df = pd.DataFrame(pp)

    mortality = []
    for mort in mortalities:
        mortality.append(mort)

    phys_df['mort'] = mortality
    return phys_df

def sliding_mean(data_array, window=2):
    new_list = []
    for i in range(len(data_array)):
        indices = range(max(i - window + 1, 0),
                        min(i + window + 1, len(data_array)))
        avg = 0
        for j in indices:
            avg += data_array[j]
        avg /= float(len(indices))
        new_list.append(avg)     
    return np.array(new_list)


def plotting(phys_df, output_name, colour):

    bin_medians = []
    mort = []
    mort_std = []
    i = -1
    while i <= 1.20:
        count =phys_df.loc[(phys_df[0]>i-0.1) & (phys_df[0]<i+0.1)]
        try:
            res = sum(count['mort'])/float(len(count))
            if len(count) >=2:
                bin_medians.append(i)
                mort.append(res)
                mort_std.append(sem(count['mort']))
        except ZeroDivisionError:
            pass
        i += 0.1

    plt.figure(figsize=(6, 4.5))
    plt.plot(bin_medians, sliding_mean(mort), color=colour[0])
    plt.fill_between(bin_medians, sliding_mean(mort) - 1*sliding_mean(mort_std),  
                    sliding_mean(mort) + 1*sliding_mean(mort_std), color=colour[1])
    plt.grid()
    plt.xticks(np.arange(-1, 1.5))
    r = [float(i)/10 for i in range(0,11,1)]
    _ = plt.yticks(r, fontsize=13)  
    _ = plt.title(output_name, fontsize=17.5)  
    _ = plt.ylabel("Proportion Mortality", fontsize=15)  
    _ = plt.xlabel("Expected Return", fontsize=15)  

    plt.savefig(output_name)


def main(train_data, test_data, algo): 
    df_train = pd.DataFrame()
    df_test = pd.DataFrame()

    for i in range(5):
        df_train = df_train.append(mortality_expectedReturn(train_data, algo, i))

    
    for i in range(5):
        df_test = df_test.append(mortality_expectedReturn(test_data, algo, i))
    
    if algo == "CQL":
        colour = ['b', 'lightblue']
    else: 
        colour = ['g', 'lightgreen']
    
    plotting(df_train, "Mortality vs Expected Return - DeepVent", colour)
    plotting(df_test, "Mortality vs Expected Return - DeepVent OOD", colour)

# Calling the function
main(train_data, test_data, "CQL")