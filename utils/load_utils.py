# Utilities for loading data

import numpy as np
from sklearn.model_selection import train_test_split
import pickle

from d3rlpy.dataset import MDPDataset
from d3rlpy.ope import DiscreteFQE
from d3rlpy.algos import DiscreteCQL, DoubleDQN

from constants import DATA_FOLDER_PATH
def episode_list_to_mdp_dataset(episode_list):
    states = []
    actions = []
    rewards = []
    terminals = []
    for episode in episode_list:
        for i in range(len(episode.observations)):
            states.append(episode.observations[i])
            actions.append(episode.actions[i])
            rewards.append(episode.rewards[i])
            terminals.append(0)
        terminals[-1] = 1
    
    return MDPDataset(
        np.array(states),
        np.array(actions),
        np.array(rewards),
        np.array(terminals)
    )

def load_data(states, rewards, index_of_split=None, no_split=False):
    ''' Load data based on states option and rewards option.

    Keyword arguments:
    states -- the states option (possibilities: ["raw", "ood"])
    rewards -- the rewards option (possibilities: ["intermediate", "intermediatex2", "no_intermediate", "ood"]    
    index_of_split -- the index of the split we are using for the current run
    no_split -- True if just want whole dataset, not split into train/test
    '''
    if states == "ood" and rewards == "ood":
        with open(f"{DATA_FOLDER_PATH}/ood_train.pkl", "rb") as fp:
            train_data = pickle.load(fp)
        with open(f"{DATA_FOLDER_PATH}/ood_test.pkl", "rb") as fp:
            test_data = pickle.load(fp)
        test_data = episode_list_to_mdp_dataset(test_data)
        train_data = episode_list_to_mdp_dataset(train_data)
        assert(len(test_data.episodes) < len(train_data.episodes))

        return train_data, test_data
    else:
        STATES_PATH = f"{DATA_FOLDER_PATH}/states/raw_states.npy"
        if rewards == "intermediate":
            REWARDS_PATH = f"{DATA_FOLDER_PATH}/rewards/rewards_with_intermediate_fixed.npy"
        elif rewards == "intermediatex2":
            REWARDS_PATH = f"{DATA_FOLDER_PATH}/rewards/rewards_with_intermediatex2.npy"
        elif rewards == "no_intermediate":
            REWARDS_PATH = f"{DATA_FOLDER_PATH}/rewards/rewards_without_intermediate.npy"
        else:
            raise AssertionError()

        ACTIONS_PATH = f"{DATA_FOLDER_PATH}/actions/1Ddiscretized_actions.npy"
        DONE_FLAGS_PATH = f"{DATA_FOLDER_PATH}/done_flags/done_flags.npy"

        states = np.load(STATES_PATH)
        actions = np.load(ACTIONS_PATH)
        rewards = np.load(REWARDS_PATH)
        terminals = np.load(DONE_FLAGS_PATH)

        data = MDPDataset(states, actions, rewards, terminals)
        if no_split:
            return data
            
        train_data, test_data = train_test_split(data.episodes, test_size=0.2)
        train_data = episode_list_to_mdp_dataset(train_data)
        test_data = episode_list_to_mdp_dataset(test_data)

        # If no particular split
        if index_of_split == None:
            return train_data, test_data
        
        # Else get episodes specific to this train_test_split
        train_indices = np.load(f"{DATA_FOLDER_PATH}/indices/train_indices_{index_of_split}.npy")
        test_indices = np.load(f"{DATA_FOLDER_PATH}/indices/test_indices_{index_of_split}.npy")

        train_episodes = []
        for i in train_indices:
            train_episodes.append(data.episodes[i])

        test_episodes = []
        for i in test_indices:
            test_episodes.append(data.episodes[i])

        test_data = episode_list_to_mdp_dataset(test_episodes)
        train_data = episode_list_to_mdp_dataset(train_episodes)
        assert(len(test_data.episodes) < len(train_data.episodes))

        return train_data, test_data



