# Find best hyperparameters for DQN

from d3rlpy.algos import DoubleDQN

from train_utils import train
from constants import HYPERPARAMETER_SEARCH_PATH

# Values to try for each hyperparameter
gammas = [0.25, 0.5, 0.75, 0.9, 0.99]
learning_rates = [1e-07, 1e-06, 1e-05, 1e-04]

# Train 500 000 steps for each combination of hyperparameters
for gamma in gammas:
    for learning_rate in learning_rates:
        train(
            model_class=DoubleDQN, 
            learning_rate=learning_rate, 
            gamma=gamma,
            alpha=None,
            states="raw", 
            rewards="no_intermediate", 
            index_of_split=None,
            label=f"{HYPERPARAMETER_SEARCH_PATH}/lr={learning_rate}, gamma={gamma}",
            n_epochs=10,
            n_steps_per_epoch=50000
            )