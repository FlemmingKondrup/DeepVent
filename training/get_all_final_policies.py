# Get correct policies from TRAINING_RUNS_PATH into FINAL_POLICIES_PATH in structured way
import os,string
import shutil
import json
from constants import TRAINING_RUNS_PATH, FINAL_POLICIES_PATH
path = '.'
path = os.path.normpath(path)
res = []

# Get all folders with policies we are interested in
for root,dirs,files in os.walk(TRAINING_RUNS_PATH, topdown=True):
    if "train" in root or "FQE" in root:
        res += [root]

def clean_path(path):
    return path.replace("/", "~").replace("\\", "~")
model_num = 2000000
fqe_model_num = 2500000

# Build path to copy into
def build_copy_path(path):
    copy_path = f"{FINAL_POLICIES_PATH}/"
    if "ood" in model_path:
        copy_path+="ood/"
    elif "raw_intermediate" in model_path:
        copy_path += "raw_intermediate/"
    elif "raw_no_intermediate" in model_path:
        copy_path += "raw_no_intermediate/"
    else:
        return "failure"

    if "CQL" in model_path:
        copy_path += "CQL/"
    elif "DQN" in model_path:
        copy_path += "DQN/"
    else:
        return "failure"
    
    for j in range(5):
        run_path = f"run_{j}"
        if run_path in path:
            copy_path += f"{run_path}/"

    if "FQE" in model_path:
        copy_path += f"FQE_{fqe_model_num}.pt"
    else:
        copy_path += f"model_{model_num}.pt"
    
    return copy_path

if not os.path.isdir(FINAL_POLICIES_PATH):
    os.mkdir(FINAL_POLICIES_PATH)
state_types = ["raw_no_intermediate", "ood", "raw_intermediate"]
model_types = ["CQL", "DQN"]
run_num = 5
# Create all subdirectories
for state_type in state_types:
    if not os.path.isdir(f"{FINAL_POLICIES_PATH}/{state_type}"):
        os.mkdir(f"{FINAL_POLICIES_PATH}/{state_type}")
    for model_type in model_types:
        if not os.path.isdir(f"{FINAL_POLICIES_PATH}/{state_type}/{model_type}"):
            os.mkdir(f"{FINAL_POLICIES_PATH}/{state_type}/{model_type}")
        for i in range(run_num):
            if not os.path.isdir(f"{FINAL_POLICIES_PATH}/{state_type}/{model_type}/run_{i}"):
                os.mkdir(f"{FINAL_POLICIES_PATH}/{state_type}/{model_type}/run_{i}")

# Copy all relevant policies to FINAL_POLICIES_PATH
for path in res:
    print(path)
    if "FQE" in path:
        model_path = f"{path}/model_{fqe_model_num}.pt"
    else:
        model_path = f"{path}/model_{model_num}.pt"
    model_copy_path = build_copy_path(model_path)
    shutil.copy(model_path, model_copy_path)