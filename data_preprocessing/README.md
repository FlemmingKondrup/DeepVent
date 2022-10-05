# Data Preprocessing 
In there, we provide a detail description of what each component is used for. 

1. Data Extraction from MIMIC-III

2. Imputation
- Gets raw data from csv files and imputes missing values using sample and hold and k nearest neighbours

3. Compute Trajectories
- Takes imputed data and builds all trajectories with which we train our policy. Saves each state as a 37-tuple (one value for each measurement) and each action as a 3-tuple (one value for each setting we control). Saves reward including intermediate reward.
- This script allows you to build the trajectories for training, including MDP states, intermediate rewards, MDP action space.

4. Modification of actions and rewards  
- discretize_actions.py: Transforms continuous 3-dimensional actions into 1-dimensional discrete actions and saves them in a separate file (necessary to have a discrete action space)
- remove_intermediate_reward.py: Removes intermediate rewards from rewards (only keeping terminal rewards) and saves them in a separate file (necessary to be able to train with and without intermediate rewards)

5. Split the data and create OOD 
- generate_ood_dataset.py : generate Out of Distribution (OOD) dataset of outlier patients.
- train_test_split.py : Split the training and testing data 
