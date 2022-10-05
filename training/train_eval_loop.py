# importing
import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())
path = Path(os.getcwd())
sys.path.append(str(path.parent.absolute()))

import numpy as np

from d3rlpy.algos import DiscreteCQL, DoubleDQN

from train_utils import train
from utils.evaluate_utils import evaluate
from utils.load_utils import load_data

from constants import FINAL_POLICIES_PATH ,TRAINING_RUNS_PATH
'''
Main training and evaluation loop for our policies:
Train and evaluate with FQE a model corresponding to MODEL_CLASS with the states corresponding to STATES and rewards corresponding to REWARDS
Do a total of N_RUNS runs and save each run in a separate folder
'''

N_RUNS = 5
N_EPOCHS_TRAIN = 20
N_STEPS_PER_EPOCH_TRAIN = 100000
N_EPOCHS_EVAL = 25
N_STEPS_PER_EPOCH_EVAL = 100000
MODEL_CLASS = DoubleDQN
STATES = "ood"
REWARDS = "ood"
for i in range(N_RUNS):
    label = f"{TRAINING_RUNS_PATH}/{STATES}_{REWARDS}/{str(MODEL_CLASS.__name__)}/run_{i}"
    train_label = f"{label}/{str(MODEL_CLASS.__name__)}_train"
    model = train(
        model_class=MODEL_CLASS, 
        learning_rate=1e-06, 
        gamma=0.75, 
        alpha=0.5, 
        states=STATES, 
        rewards=REWARDS, 
        index_of_split=i, 
        label=train_label, 
        n_epochs=N_EPOCHS_TRAIN, 
        n_steps_per_epoch=N_STEPS_PER_EPOCH_TRAIN)
    
    #initialize fqe
    fqe = evaluate(
        MODEL_CLASS, 
        f"{train_label}/model_{N_EPOCHS_EVAL * N_STEPS_PER_EPOCH_EVAL}.pt",
        f"{label}/FQE",
        STATES,
        REWARDS,
        i,
        N_EPOCHS_EVAL,
        N_STEPS_PER_EPOCH_EVAL
    )

