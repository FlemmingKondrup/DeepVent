import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())
path = Path(os.getcwd())
sys.path.append(str(path.parent.absolute()))

import itertools
from d3rlpy.dataset import MDPDataset
from d3rlpy.algos import DiscreteCQL, DoubleDQN
from d3rlpy.ope import DiscreteFQE
import numpy as np
import matplotlib.pyplot as plt
import pickle
from utils.load_utils import load_data
from estimator import get_final_estimator

print("Making physician action similarity plot")
NUM_RUNS = 5
total_num_close_cql = {
    "PEEP": 0,
    "FiO2": 0,
    "Adjusted Tidal Volume": 0
    }
total_num_close_dqn = {
    "PEEP": 0,
    "FiO2": 0,
    "Adjusted Tidal Volume": 0
    }
for i in range(NUM_RUNS):
    print(f"Processing run {i}")
    estimator = get_final_estimator(DiscreteCQL, "raw", "intermediate", index_of_split = i)
    for key in total_num_close_cql:
        total_num_close_cql[key] += estimator.get_actions_within_one_bin()[key]

    estimator = get_final_estimator(DoubleDQN, "raw", "no_intermediate", index_of_split = i)
    for key in total_num_close_dqn:
        total_num_close_dqn[key] += estimator.get_actions_within_one_bin()[key]

for key in total_num_close_cql:
    total_num_close_cql[key] /= NUM_RUNS
    total_num_close_dqn[key] /= NUM_RUNS

fig, ax = plt.subplots()
ind = np.arange(3)

ind = np.arange(3)
width=0.35
key_list = list(total_num_close_cql.keys())

ax.bar(ind-width/2, [total_num_close_cql[key] * 100 for key in key_list], width, color="tab:blue", label="DeepVent")
ax.bar(ind+width/2, [total_num_close_dqn[key] * 100 for key in key_list], width, color="tab:green", label="DDQN")
ax.set_xticks(ind)
ax.set_xticklabels(key_list)
ax.set_ylim(0,100)
ax.set_ylabel("%")
ax.legend()
ax.set_title("% of each setting within one bin of physician")

plt.show()