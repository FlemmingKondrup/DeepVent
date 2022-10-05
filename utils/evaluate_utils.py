from d3rlpy.algos import DiscreteCQL, CQL, DiscreteBC, BC, DiscreteRandomPolicy, RandomPolicy, DoubleDQN, SAC
from d3rlpy.dataset import MDPDataset
from d3rlpy.metrics.scorer import value_estimation_std_scorer, discounted_sum_of_advantage_scorer, continuous_action_diff_scorer, soft_opc_scorer, initial_state_value_estimation_scorer, average_value_estimation_scorer, discrete_action_match_scorer, td_error_scorer
from d3rlpy.ope import DiscreteFQE, FQE
import numpy as np
import pickle
from utils.load_utils import load_data

def evaluate(model_class, policy_path, label, states, rewards, index_of_split, n_epochs, n_steps_per_epoch):
    '''Evaluate a policy using FQE

    Arguments:
    model_class -- Model class of policy being evaluated
    policy_path -- Path of policy to evaluate
    label -- Label of evaluation run, will be used as directory name for logging weights/metrics
    states -- States option 
    rewards -- Rewards option ("no_intermediate" or "intermediate")
    index_of_split -- Index of train/test split (for when running multiple runs with different train/test splits)
    n_epochs -- Number of epochs to train FQE for
    n_steps_per_epoch -- Number of steps per epoch
    '''
    model = model_class()
    train_data, test_data = load_data(states, rewards, index_of_split)
    model.build_with_dataset(train_data)
    model.load_model(policy_path)
    experiment_name = label

    # off-policy evaluation algorithm
    fqe = DiscreteFQE(algo=model, gamma=0.99, learning_rate=1e-6, use_gpu=True)

    # train estimators to evaluate the trained policy
    fqe.fit(train_data,
            n_steps_per_epoch=n_steps_per_epoch,
            n_steps = n_steps_per_epoch * n_epochs,
            with_timestamp=False,
            experiment_name=experiment_name,
            eval_episodes=test_data,
            scorers={
                "initial_state_value_estimation_scorer" : initial_state_value_estimation_scorer,
                "percent identical actions between policy and dataset" : discrete_action_match_scorer
            })
    return fqe
