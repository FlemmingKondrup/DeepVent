# Data Extraction

Software: MySQL

Database: MIMIC-III (https://mimic.mit.edu/docs/iii/)

Our data extraction process involves 3 parts in order:

(1) Preliminaries - Extraction of demographic, fluids and SIRS/SOFA scores for later use

(2) GetSubTables - Combines data into the following subtables: Fluids, LabValues, VentilationParams, VitalSigns

(3) GetFinalTable - Combines the SubTables as well as additional data into one big table and performs required processing


When running the sql scripts, if a subfolder of scripts is present, run the scripts within the subfolder first.

For the getFinalTable, the procedure is done in 4 steps (run the getOverallTable files from 1 to 4 in order).
