# Make Out of Distribution vs. In Distribution value estimation plot for DeepVent and DDQN (Figure 4 in DeepVent paper)

# importing
import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())
path = Path(os.getcwd())
sys.path.append(str(path.parent.absolute()))

from collections import Counter
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib
import pickle

from d3rlpy.ope import DiscreteFQE
from d3rlpy.algos import DiscreteCQL, DoubleDQN, DiscreteRandomPolicy
from d3rlpy.dataset import MDPDataset

from estimator import get_final_estimator
from utils.load_utils import load_data
print("Making OOD vs ID comparison plot")
N_RUNS = 5 # Number of runs in experiment that we are graphing for

# Initialize data dictionary with 2 lists for each model (1 for OOD, 1 for in distribution)
data_dict = {
    "DeepVent" : [[], []],
    "DDQN" : [[], []]
}

for i in range(N_RUNS):
    print(f"Processing run {i}")
    # For DDQN and CQL, for each run, get mean of initial value estimations for out of distribution and in distribution using estimator class
    estimator = get_final_estimator(DoubleDQN, "ood", "ood", index_of_split=i)
    data_dict["DDQN"][0].append(estimator.get_init_value_estimation(estimator.data["train"]).mean())
    data_dict["DDQN"][1].append(estimator.get_init_value_estimation(estimator.data["test"]).mean())

    estimator = get_final_estimator(DiscreteCQL, "ood", "ood", index_of_split=i)
    data_dict["DeepVent"][0].append(estimator.get_init_value_estimation(estimator.data["train"]).mean())
    data_dict["DeepVent"][1].append(estimator.get_init_value_estimation(estimator.data["test"]).mean())

# Transform list of means (one for each run) into numpy array to make it easier to take mean and variance
for key in data_dict:
    for i, _ in enumerate(data_dict[key]):
        data_dict[key][i] = np.array(data_dict[key][i])


# Set parameters for graphs
plt.rcParams.update({'font.size': 14})
ax = plt.subplot(111)
x = np.array(range(len(data_dict)))
width = 0.2
colors = ["tab:blue", "tab:green"]

# For each model in data_dict, plot mean and variance over all runs 
for i, label in enumerate(data_dict.keys()):
    means = [value.mean() for value in data_dict[label]]
    var = [value.var()  for value in data_dict[label]]
    offset = (i - len(data_dict)/2) * width

    ax.bar(x+offset, means, yerr=var, width=width, align='center', label=label, color = colors[i])

# Set title, label, legend, etc. for plot
ax.axhline(y=1, color='r', linestyle = '--', label = "Overestimation Threshold")
ax.legend(loc="upper left")
ax.set_xticklabels(["In Distribution", "Out of Distribution"])
ax.set_xticks(x-width/2)
ax.set_title("Mean Initial Q Values OOD vs ID ")
ax.set_ylabel("Mean Initial Q Value")

plt.show()