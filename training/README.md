# Training

This folder contains all the files you need to train a model once the data preprocessing has been done

To do a hyperparameter search for CQL or DDQN go to `find_cql.py` or `find_dqn.py`. A hyperparameter search for another model can easily be done by using those files as template

To train a policy for a certain number of runs (and evaluate it with FQE) go into `train_eval_loop.py` and edit the MODEL_CLASS parameter to be any discrete algorithm class in d3rlpy library and run the file.

Discrete algorithms implemented in d3rlpy can be found here: https://d3rlpy.readthedocs.io/en/v1.0.0/references/algos.html 
