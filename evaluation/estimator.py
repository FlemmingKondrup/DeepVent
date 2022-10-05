import numpy as np
import itertools
from collections import Counter

from d3rlpy.ope import DiscreteFQE
from d3rlpy.algos import DiscreteCQL, DoubleDQN
from utils.load_utils import load_data
from constants import FINAL_POLICIES_PATH
ACTION_DICT                 = {
                                'peep' : [5, 7, 9, 11, 13, 15, 1000000000],
                                'fio2' : [30, 35, 40, 45, 50, 55, 1000000000],
                                'adjusted_tidal_volume' : [0, 5, 7.5, 10, 12.5, 15, 10000000000]
                                }

def get_reverse_action_dict():
    '''Get dictionary that takes action index and returns indices of bins for 3 settings'''
    indices_lists = [[i for i in range(len(ACTION_DICT[action]))] for action in ACTION_DICT]
    possibilities = list(itertools.product(*indices_lists))
    possibility_dict = {}

    for i, possibility in enumerate(possibilities):
        possibility_dict[i] = possibility
	
    return possibility_dict

class Estimator():
    def __init__(self, label, data):
        self.label = label
        self.data = {"train" : data[0], "test" : data[1]}
        assert(len(self.data["train"].episodes) > len(self.data["test"].episodes))

class ModelEstimator(Estimator):
    def __init__(self, label, model_class, data, policy_path, fqe_policy_path):
        super().__init__(label, data)
        self.policy_path = policy_path
        self.model_class = model_class
        self.policy = self.load_policy(policy_path)
        self.fqe_policy = self.load_fqe_policy(fqe_policy_path)
        # print("MODEL ESTIMATOR")
        # print(self.data['test'].observations)

    def load_policy(self, policy_path):
        model = self.model_class()
        model.build_with_dataset(self.data["train"])
        model.load_model(policy_path)
        return model
    
    def load_fqe_policy(self, fqe_policy_path):
        model = DiscreteFQE(algo=self.policy)
        model.build_with_dataset(self.data["train"])
        model.load_model(fqe_policy_path)
        return model

    def get_init_value_estimation(self, data):
        init_states = np.array([episode.observations[0] for episode in data.episodes])
        return self.fqe_policy.predict_value(init_states, self.fqe_policy.predict(init_states))

    def get_action_count(self):
        return Counter(self.data["test"].actions)
    
    def get_actions_within_one_bin(self):
        actions = self.policy.predict(self.data["test"].observations)
        reverse_action_dict = get_reverse_action_dict()
        model_setting = {
            "PEEP": np.array([reverse_action_dict[action][0] for action in actions]),
            "FiO2": np.array([reverse_action_dict[action][1] for action in actions]),
            'Adjusted Tidal Volume': np.array([reverse_action_dict[action][2] for action in actions])
        }

        phys_setting = {
            "PEEP" :np.array([reverse_action_dict[action][0] for action in self.data["test"].actions]),
            "FiO2" :np.array([reverse_action_dict[action][1] for action in self.data["test"].actions]),
            'Adjusted Tidal Volume' :np.array([reverse_action_dict[action][2] for action in self.data["test"].actions])
        }
        num_close = {}
        key_list = list(model_setting.keys())

        for setting in key_list:
            num_close[setting] = 0
            for i in range(len(model_setting["PEEP"])):
                model_ind = model_setting[setting][i]
                phys_ind = phys_setting[setting][i]
                if model_ind <= phys_ind + 1 and model_ind >= phys_ind - 1:
                    num_close[setting] += 1

            num_close[setting] /= len(phys_setting[setting])
        return num_close

class PhysicianEstimator(Estimator):
    def __init__(self, data):
        super().__init__("Physician", data)


    def get_init_value_estimation(self, data):
        values = []
        for episode in data.episodes:
            if episode.rewards[-1] == 1:
                values.append(0.99 ** (len(episode)))
            elif episode.rewards[-1] == -1:
                values.append(-(0.99 ** (len(episode))))

        return np.array(values)

class MaxEstimator(Estimator):
    def __init__(self, data):
        super().__init__("Max", data)

    def get_init_value_estimation(self, data):
        values = []
        for episode in data.episodes:
            values.append(0.99 ** (len(episode)))

        return np.array(values)


def get_final_estimator(model_class, states, rewards, index_of_split):
    model_num = 2000000
    fqe_model_num = 2500000
    train_data, test_data = load_data(states, rewards, index_of_split=index_of_split)
    model = model_class()
    path = FINAL_POLICIES_PATH + "/"
    if states == "ood" and rewards == "ood":
        path += "ood/"
    else:
        path += f"{states}_{rewards}/"
    if model_class == DiscreteCQL:
        path += "CQL/"
    elif model_class == DoubleDQN:
        path += "DQN/"
    else:
        raise AssertionError()
    path += f"run_{index_of_split}/"
    model_path = f"{path}model_{model_num}.pt"
    fqe_model_path = f"{path}FQE_{fqe_model_num}.pt"
    return ModelEstimator("", model_class, [train_data, test_data], model_path, fqe_model_path)