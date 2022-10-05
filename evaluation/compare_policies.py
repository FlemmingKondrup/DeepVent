import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())
path = Path(os.getcwd())
sys.path.append(str(path.parent.absolute()))

# Output average initial value estimations for DeepVent, DeepVent- and physician (mean and variance over 5 runs) 
# (Corresponds to Table 1 in DeepVent paper)
import numpy as np

from d3rlpy.algos import DoubleDQN, DiscreteCQL

from estimator import ModelEstimator, PhysicianEstimator, get_final_estimator
from utils.load_utils import load_data

print("Getting initial value estimations for DeepVent, DeepVent- and Physician")
N_RUNS = 5
# Initialize data dictionary with 2 lists for each model (1 for train 1 for test)
data_dict = {
    "DeepVent" : [[], []],
    "DeepVent-": [[], []],
    "Physician": [[], []]
}

# Get initial value estimations for each model for each run using estimator clas
for i in range(N_RUNS):
    print(f"Processing run {i}")
    estimator = get_final_estimator(DiscreteCQL, "raw", "intermediate", index_of_split=i)
    data_dict["DeepVent"][0].append(estimator.get_init_value_estimation(estimator.data["train"]).mean())
    data_dict["DeepVent"][1].append(estimator.get_init_value_estimation(estimator.data["test"]).mean())

    estimator = get_final_estimator(DiscreteCQL, "raw", "no_intermediate", index_of_split=i)
    data_dict["DeepVent-"][0].append(estimator.get_init_value_estimation(estimator.data["train"]).mean())
    data_dict["DeepVent-"][1].append(estimator.get_init_value_estimation(estimator.data["test"]).mean())

    train_data, test_data = load_data("raw", "no_intermediate", index_of_split=i)
    estimator = PhysicianEstimator([train_data, test_data])
    data_dict["Physician"][0].append(estimator.get_init_value_estimation(estimator.data["train"]).mean())
    data_dict["Physician"][1].append(estimator.get_init_value_estimation(estimator.data["test"]).mean())

# Transform all results into numpy arrays
for key in data_dict:
    for i, _ in enumerate(data_dict[key]):
        data_dict[key][i] = np.array(data_dict[key][i])

# Print formatted results
for i, label in enumerate(data_dict.keys()):
    print(label)
    print("-------------------------")
    means = [value.mean() for value in data_dict[label]]
    var = [value.var()  for value in data_dict[label]]
    print(f"Train mean: {means[0]}, Train variance: {var[0]}")
    print(f"Test mean: {means[1]}, Test variance: {var[1]}")
    print("-------------------------")
