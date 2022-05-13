import os
import sys
import re
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn import metrics
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

# -------------- NESTED PATH CORRECTION -------------------------------- #

# For all script files, we add the parent directory to the system path
cwd = re.sub(r"[\\]", "/", os.getcwd())
cwd_list = cwd.split("/")
path = sys.argv[0]
path_list = path.split("/")
# either the entire filepath is entered as command i python
if cwd_list[0:3] == path_list[0:3]:
    full_path = path
# or a relative path is entered, in which case we append the path to the cwd_path
else:
    full_path = cwd + "/" + path
# remove the overlap
root_dir = re.search(r"(^.+python_road_upgrades)", full_path).group(1)
sys.path.append(root_dir)

# ---------------------------------------------------------------------- #

# 1. TRAIN THE RANDOM FOREST MODEL

# 1.1 Import the data sets

# first the manual visual identifications (true values)
visual = pd.read_excel(f'{root_dir}/Imports/visual_classification_2020_2021_05_07.xlsx').set_index(['road_id', 'subroad_id'])
visual[visual['upgrade'] != 1] = 0  # replace unclear and NaN with 0

# followed by the analysis data
def import_analysis(data_fp):
    data = pd.read_excel(data_fp,  header=[0,1], index_col=[0]).set_index(
        [('road_id', 'Unnamed: 1_level_1'), ('subroad_id', 'Unnamed: 2_level_1')])
    data.index.names = ['road_id', "subroad_id"]
    data.columns.names = [None, None]
    data = data.drop([('upgrade', 'bright_B4_diff'), ('upgrade', 'bright_B4')], axis=1)
    return data

#data_fp = f"{root_dir}/Imports/analysis_2020_2021_05_07_thresh_50.xlsx" # a copy taken from Exports/Roads/composites2
data_fp = f"{root_dir}/Exports/Roads/composites_2/analysis_2020_2021_05_07.xlsx" # a copy taken from Exports/Roads/composites2
data = import_analysis(data_fp)

print(data.columns)
# 1.2 Split the data into training and test sets
def get_regressors(df):
    return df[[
        ('B4_min', 'road_id'),
        ('B4_min', 'left_avg'),
        ('B4_min', 'right_avg'),
        ('B4_mean', 'road_id'),
        #('B4_mean', 'left_avg'),
        #('B4_mean', 'right_avg'),
        #('B4_min', 'dist_median'),
        ('B4_min', 'dist_mean'),
        ('B4_min', 'share'),
        ('B4_diff_factor', 'road_id')

    ]]

X = get_regressors(data)
y = visual['upgrade'].astype('int')  # Labels

# check for NaN and drop
nan_index = X[X.isnull().any(1)].index
X = X.drop(nan_index, axis=0)
y = y.drop(nan_index, axis=0)

seed = 5350
# Split dataset into training set and test set
#     - argument test_size = 0.3: 70% training and 30% test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=seed)

## HERE COMES THE OPTIMIZATION

# Create the parameter grid based on the results of random search
param_grid = {
    'n_estimators': [20, 50, 100], # number of trees in the forest
    'max_features': list(range(2, (len(list(get_regressors(X_train).columns))+1))),  # 7 features in the model 7+1 = 8
    'max_depth': [20, 50, 100], # max number of levels in each tree
    'bootstrap': [True, False],
    'min_samples_leaf': [2, 4, 6],
    'min_samples_split': [2, 3, 4],
}

rf = RandomForestClassifier(random_state=5350)

# Instantiate the grid search model
grid_search = GridSearchCV(estimator = rf, param_grid = param_grid,
                           cv = 5, n_jobs = -1, verbose = 1)

#grid_search = RandomizedSearchCV(estimator = rf, param_distributions = param_grid,
 #                                n_iter = 500, cv = 3, verbose=1, random_state=5350, n_jobs = -1)

#grid_search.fit(X_train, y_train)
#print(grid_search.best_params_)


#best_params = grid_search.best_params_
best_params = {'bootstrap': True, 'max_depth': 20, 'max_features': 5, 'min_samples_leaf': 2, 'min_samples_split': 2, 'n_estimators': 20}

# Create a Gaussian Classifier
clf = RandomForestClassifier(**best_params, random_state=seed)


# Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
print("Random Forest Model Accuracy:", metrics.accuracy_score(y_test, y_pred))

print(clf.feature_importances_)


# 2. PREDICT VALUES IN THE ROAD EXPORT FILES

folder_name = "Pemba_N"  # name of folder in the /Exports/Roads directory, where we will update values
prefix = folder_name
export_dir = f"{root_dir}/Exports/Roads/{folder_name}"
road_files = os.listdir(export_dir)


for f_r in road_files:

    if not re.match(r"^" + re.escape(prefix) + r"_\d+_\d+.+", f_r):
        continue

    # import the roads excel file
    fp_r = f"{export_dir}/{f_r}"
    df_r = pd.read_excel(fp_r).set_index(['road_id', 'subroad_id'])
    # import the analysis excel file
    f_a = f_r.replace(prefix, "analysis")
    fp_a = f"{export_dir}/{f_a}"
    df_a = import_analysis(fp_a)

    # predict the values based off of
    X = get_regressors(df_a)
    # skip the Nans
    not_nan_index = X[X.notnull().all(1)].index

    upgrade_prediction = clf.predict(X.loc[not_nan_index])

    df_r.loc[:, 'upgraded'] = 0 # set default to zero (including skipped Nans)
    df_r.loc[:, 'upgrade_type'] = np.NaN  # clear the column upgrade_type

    df_r.loc[not_nan_index, 'upgraded'] = upgrade_prediction
    df_r.loc[df_r['upgraded'] == 1, 'upgrade_type'] = "leveling"

    # overwrite the upgraded values
    df_r.reset_index().to_excel(fp_r, index=False)

    print(f"Predicted upgrades for: {f_r}")

