# importing
import sys
import os
from pathlib import Path
import os
import pandas as pd

sys.path.append(os.getcwd())
path = Path(os.getcwd())
sys.path.append(str(path.parent.absolute()))

from utils.imputation_utils import preprocess_imputation
from constants import DATA_FOLDER_PATH

IMPUTED_DATA_DIR_PATH       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
IMPUTATION_N                = 1
IMPUTATION_K                = 3
DATA_TABLE_FILE_NAME        = os.path.join(DATA_FOLDER_PATH,"december_table_projectx.csv")
IMPUTED_DATAFRAME_PATH      = os.path.join(DATA_FOLDER_PATH,"imputed.pkl")
# Get data into pandas dataframe
df = pd.read_csv(DATA_TABLE_FILE_NAME)
# Impute missing values
df = preprocess_imputation(df, IMPUTATION_N, IMPUTATION_K)
df = df.dropna()
df.to_pickle(IMPUTED_DATAFRAME_PATH)
