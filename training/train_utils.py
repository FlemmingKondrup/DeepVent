# Utils needed to train a model

import numpy as np
import pickle
import os 
from sklearn.model_selection import train_test_split

from d3rlpy.dataset import MDPDataset
from d3rlpy.algos import DiscreteCQL, CQL, DiscreteBC, BC, RandomPolicy, DiscreteRandomPolicy, DoubleDQN, SAC
from d3rlpy.metrics.scorer import continuous_action_diff_scorer, soft_opc_scorer, initial_state_value_estimation_scorer, average_value_estimation_scorer, discrete_action_match_scorer, td_error_scorer

from utils.load_utils import load_data
def train(
    model_class, 
    learning_rate, 
    gamma, 
    alpha, 
    states, 
    rewards, 
    index_of_split,
    label,
    n_epochs,
    n_steps_per_epoch
    ):
    '''Train a model with given parameters.
    
    Args:
        model_class: Class of model to use (usually DiscreteCQL or DoubleDQN)
        learning_rate: Learning rate to use for training
        gamma: Discount factor for Q values
        alpha: Scaling factor for conservative term in CQL
        states: States option
        rewards: Rewards option
        index_of_split : Index of dataset split to use (when doing multiple runs with different train/test splits)
        label: Label of training experiment (will be used as directory name for logging weights and metrics)
        n_epochs: Number of epochs to train for
        n_steps_per_epoch: Number of steps to train for each epoch
    '''
    print(f"Training params -------\nLearning Rate: {learning_rate}\n Gamma: {gamma}")
    train_data, test_data = load_data(states, rewards, index_of_split)
    assert(len(train_data.episodes) > len(test_data.episodes))

    # Instantiate model class
    if model_class == DiscreteCQL:
        model = model_class(
            learning_rate=learning_rate,
            alpha=alpha,
            use_gpu=True,
            gamma=gamma
            )
    else:
        model = model_class(
            learning_rate=learning_rate,
            use_gpu=True,
            gamma=gamma
            )
    
    # Train
    model.fit(
        train_data,
        with_timestamp=False,
        eval_episodes=test_data, 
        n_steps = n_epochs * n_steps_per_epoch,
        n_steps_per_epoch = n_steps_per_epoch,
        experiment_name=label,
        scorers = 
        {
            "initial_state_value_estimation_scorer" : initial_state_value_estimation_scorer,
            "td_error_scorer" : td_error_scorer,
            "percent identical actions between policy and dataset" : discrete_action_match_scorer
        }
        )
    return model


