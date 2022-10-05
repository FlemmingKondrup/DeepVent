# Remove intermediate rewards from rewards file and save as separate file
import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())
path = Path(os.getcwd())
sys.path.append(str(path.parent.absolute()))
import numpy as np

from constants import DATA_FOLDER_PATH

rewards = np.load(os.path.join(DATA_FOLDER_PATH, "rewards/rewards_with_intermediate_fixed.npy"))

# Return 0 if reward is not 1 or -1 (i.e. the reward is intermediate and not terminal)
def remove_intermediate(num):
    if num != 1 and num != -1:
        return 0
    
    return num

# For each reward in rewards, set to 0 if isn't terminal reward
new_rewards = np.array([remove_intermediate(num) for num in rewards])

np.save(os.path.join(DATA_FOLDER_PATH, "rewards/rewards_without_intermediate.npy"), new_rewards)