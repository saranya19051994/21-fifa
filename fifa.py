
# -*- coding: utf-8 -*-
"""Review4_FIFA.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1R6FqOZWyB1cpoc--EBi7qin75GgoLbET

# **IMPORTING LIBRARIES**
"""



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency,chi2
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold

"""# **FUNCTIONS**"""

# Function to categorize player positions
def categorize_position(positions):
    position = positions.split(', ') [0] # Split positions if multiple
    if 'GK' in position:
        return 'GK'
    elif any(pos in position for pos in ['LCM', 'RCM', 'CDM', 'LDM', 'RDM', 'CM', 'LM','RM', 'LAM', 'RAM','MID']):
      return 'MID'
    elif any(pos in position for pos in ['LCB','RCB', 'LB', 'RB', 'LWB', 'RWB', 'CB','DEF']):
        return 'DEF'
    elif any(pos in position for pos in ['CAM','LS', 'ST','RS', 'LW', 'RW','CF', 'RF', 'LF', 'FW']):
        return 'FW'
    else:
        return 'Other'

# Function to categorize body types
def categorize_body_type(body_type):
  if 'Lean' in body_type:
    return 'Lean'
  elif 'Stocky' in body_type:
    return 'Stocky'
  elif 'Normal' in body_type:
    return 'Normal'
  elif 'Messi' in body_type:
    return 'Messi'
  elif 'C. Ronaldo' in body_type:
    return 'C. Ronaldo'
  elif 'Akinfenwa' in body_type:
    return 'Akinfenwa'
  elif 'Shaqiri' in body_type:
    return 'Shaqiri'
  elif 'Neymar' in body_type:
    return 'Neymar'
  elif 'Mohamed Salah' in body_type:
    return 'Mohamed Salah'
  elif 'Courtois' in body_type:
    return 'Courtois'
  else:
    return 'Other'

def chi2_test(df1, df2):
  alpha = 0.05
  cont_table = pd.crosstab(index=df1,columns=df2)
  #cont_table.head()
  # chi2 value, p value, degree of freedom , expected_table
  chi2_value, p, dof, expected_table = chi2_contingency(cont_table)

  print(f'chi2 value: {chi2_value}')
  print(f'p value: {p}')
  print(f'degree of freedom: {dof}')
  if p <= alpha:
    print(f'Reject null hypothesis. There exist some relation between features')
  else:
    print(f'Accept null hypothesis. Two features are not related')

#function to display null value percentage
def get_miss_percent(null_to_handle, df):
  percent_missing = []
  col_name = []
  for col in null_to_handle:
    percent_missing.append(df[col].isna().sum() * 100 / len(df[col]))
    col_name.append(col)
  missing_value_df = pd.DataFrame({'column_name': col_name,
                                 'percent_missing': percent_missing})
  return missing_value_df

def compare_models(models):
  # Assign weights to R2 and MSE
  weight_r2 = 0.7
  weight_mse = 0.3

  # Calculate rankings for R2 and MSE
  rank_r2 = sorted(models, key=lambda x: x['r2'], reverse=True)
  rank_mse = sorted(models, key=lambda x: x['mse'])

  # Calculate weighted rankings
  weighted_rank = []
  for model in models:
    weighted_rank.append({
        'model_name': model['Name'],
        'overall_rank': (rank_r2.index(model) * weight_r2) + (rank_mse.index(model) * weight_mse)
    })
  print(pd.DataFrame(weighted_rank))
  # Choose the model with the lowest overall ranking as the best model
  best_model = min(weighted_rank, key=lambda x: x['overall_rank'])

  print("\nBest Model:", best_model['model_name'])
  model_df = pd.DataFrame(models)
  model_df

"""# **DATASET UNDERSTANDING AND NULL HANDLING**"""

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)



df = pd.read_csv("players_21.csv")

df.head(30)

null_to_handle=[]
for col in df.columns:
  if df[col].isna().sum() > 0:
    null_to_handle.append(col)
print(f"columns to handle null values: {null_to_handle}")

get_miss_percent(null_to_handle, df)

#column dropped as so many null values 'player_tags','defending_marking'
df.drop(['player_tags','defending_marking'],axis=1,inplace=True)
null_to_handle.remove('player_tags')
null_to_handle.remove('defending_marking')

#columns dropped as they are id values 'club_name', 'league_name','nation_position', 'nation_jersey_number','team_jersey_number'
df.drop(['club_name','nation_position','team_jersey_number', 'nation_jersey_number'],axis=1,inplace=True)
null_to_handle.remove('club_name')
null_to_handle.remove('nation_position')
null_to_handle.remove('nation_jersey_number')
null_to_handle.remove('team_jersey_number')

#columns dropped as they derived from target column 'release_clause_eur'
df.drop(['release_clause_eur'],axis=1,inplace=True)
null_to_handle.remove('release_clause_eur')

#column to handle not affecting overall 'loaned_from', 'joined', 'contract_valid_until'
df.drop(['loaned_from','joined', 'contract_valid_until'],axis=1,inplace=True)
null_to_handle.remove('joined')
null_to_handle.remove('contract_valid_until')
null_to_handle.remove('loaned_from')

"""We found that
* 'pace','shooting','passing','dribbling','defending','physic' have null values for player_position = 'GK'
* 'gk_diving','gk_handling','gk_kicking','gk_reflexes','gk_speed','gk_positioning' have null values for all other player_position

**Conclusion: We need to handle and select features based on player_position**
"""

#filling those columns with 0
for col in ['pace','shooting','passing','dribbling','defending','physic','gk_diving','gk_handling','gk_kicking','gk_reflexes','gk_speed','gk_positioning']:
  df[col].fillna(0,inplace=True)
  null_to_handle.remove(col)

null_to_handle

print("Rows with null laegue_rank: ", df.loc[df['league_rank'].isnull(),['league_name','team_position']].index.size)
df.loc[df['league_rank'].isnull(),['league_name','team_position']]

"""**Conclusion**: League_rank and team_position are given null only where there is no league_name. We can drop those rows (225 rows) from prediction dataset (to confirm)"""

df.dropna(subset=['league_rank'], inplace = True)

df.isna().sum()[df.isna().sum() != 0]

"""data split to 2 sets: 1. player_traits = null 2. not null"""

null_df = df[df['player_traits'].isnull()]
non_null_df = df[df['player_traits'].notnull()]

"""To start with data preprocessing, deleting insignificant features from dataset"""

final_withoutplayertraits = df.drop(['sofifa_id', 'player_url', 'short_name', 'long_name', 'age', 'dob', 'height_cm',
       'weight_kg', 'nationality', 'league_name','potential',
       'value_eur', 'wage_eur','real_face','ls', 'st', 'rs', 'lw', 'lf', 'cf', 'rf', 'rw', 'lam', 'cam', 'ram',
       'lm', 'lcm', 'cm', 'rcm', 'rm', 'lwb', 'ldm', 'cdm', 'rdm', 'rwb', 'lb', 'lcb', 'cb', 'rcb',
       'rb', 'player_traits'], axis = 1)

print(final_withoutplayertraits.shape)

"""# **FEATURE REDUCTION AND OPTIMIZAION**

Team_position is a subset of player_positions.
* player_positions- potential versatility of players
* team_position- actual role assigned in a team setup/match

Hence choosing player_positions over team_position

**Conclusion**: We can drop team_position and group player_positions to sub categories.
"""

final_withoutplayertraits["player_positions"].value_counts().head(30)

# Apply categorization function to 'Position' column
final_withoutplayertraits['grouped_position'] = final_withoutplayertraits['player_positions'].apply(categorize_position)

print(final_withoutplayertraits[['player_positions','grouped_position']].head(30))

#to ask: LW, CAM

final_withoutplayertraits['grouped_position'].value_counts()

final_withoutplayertraits.drop(['team_position'], axis = 1, inplace = True)

#checking values of body_type
df['body_type'].value_counts()

final_withoutplayertraits['body_type'] = final_withoutplayertraits['body_type'].apply(categorize_body_type)

print(final_withoutplayertraits['body_type'].value_counts())

final_withoutplayertraits.head(10)

final_withoutplayertraits.columns

#fig, ax = plt.subplots(figsize=(30, 25))
#sns.heatmap(final_withoutplayertraits.select_dtypes(include = ['int64','float64']).corr(), annot = True)
#plt.show()

"""# **EXPLORATORY VISUALIZATIONS**"""

ratingsByPositions = final_withoutplayertraits[['pace','shooting','passing','dribbling','defending','physic','overall']].groupby([final_withoutplayertraits['grouped_position']]).mean()
ratingsByPositions = ratingsByPositions[['pace','shooting','passing','dribbling','defending','physic','overall']]
ratingsByPositions.plot(kind='barh', figsize=(12,5))

plt.title('Ratings Average By Position',fontsize=20)
plt.xlabel('Rating',fontsize=10)
plt.ylabel('Position',fontsize=10);

overall = final_withoutplayertraits[['overall']].groupby(final_withoutplayertraits['grouped_position']).mean().overall
overall.plot.bar(figsize=(7,5))
plt.ylabel('Overall')
plt.title('Overall Average comparations')

plt.show()

by_pos = final_withoutplayertraits[['grouped_position']].groupby(final_withoutplayertraits['grouped_position']).count()

by_pos.plot(kind='pie',figsize=(7,6), colors=['green','red','blue','orange','pink'], labels=None, autopct='%1.1f%%', fontsize=16, subplots = True)

plt.legend(labels=final_withoutplayertraits['grouped_position'].unique())
plt.title('Positions', fontsize=14)
plt.ylabel('')
plt.show()

overall = final_withoutplayertraits[['overall']].groupby(final_withoutplayertraits['overall']).count()
overall.plot.bar(figsize=(8,5))
plt.ylabel('Count')
plt.title('Overall Distribution')
plt.rcParams["figure.figsize"] = (7,7)
plt.show()

"""# **PLAYER POSITION = 'GK'**
linear 0.9983
"""

df_gk = final_withoutplayertraits.loc[final_withoutplayertraits['grouped_position'] == 'GK',['preferred_foot','league_rank', 'overall', 'international_reputation', 'weak_foot',
        'work_rate', 'body_type','skill_moves','gk_diving', 'gk_handling', 'gk_kicking', 'gk_reflexes', 'gk_speed',
       'gk_positioning', 'attacking_crossing', 'attacking_finishing',
       'attacking_heading_accuracy', 'attacking_short_passing', 'attacking_volleys',
       'skill_dribbling', 'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
       'skill_ball_control', 'movement_acceleration', 'movement_sprint_speed', 'movement_agility',
       'movement_reactions', 'movement_balance', 'power_shot_power', 'power_jumping',
       'power_stamina', 'power_strength', 'power_long_shots', 'mentality_aggression',
       'mentality_interceptions', 'mentality_positioning', 'mentality_vision',
       'mentality_penalties', 'mentality_composure', 'defending_standing_tackle',
       'defending_sliding_tackle', 'goalkeeping_diving', 'goalkeeping_handling',
       'goalkeeping_kicking', 'goalkeeping_positioning', 'goalkeeping_reflexes']]
df_gk.head(10)

#cross checking correlation  for numerical data
corr_data =df_gk[['gk_diving', 'gk_handling', 'gk_kicking', 'gk_reflexes', 'gk_speed',
       'gk_positioning','movement_acceleration', 'movement_sprint_speed', 'movement_agility',
       'movement_reactions', 'movement_balance', 'power_shot_power', 'power_jumping',
       'power_stamina', 'power_strength', 'power_long_shots','mentality_interceptions', 'mentality_positioning', 'mentality_vision',
       'mentality_penalties', 'mentality_composure', 'goalkeeping_diving', 'goalkeeping_handling',
       'goalkeeping_kicking', 'goalkeeping_positioning', 'goalkeeping_reflexes', 'overall']]
fig, ax = plt.subplots(figsize=(20, 12))
sns.heatmap(corr_data.corr(), annot = True)
plt.show()

#cross checking ch2 test for discrete numerical data
for col in ['league_rank', 'international_reputation', 'weak_foot','skill_moves',
        'work_rate', 'body_type','preferred_foot']:
  print("\nCh2 on ", col)
  chi2_test(df_gk[col],df_gk['overall'])

final_gk = df_gk[['league_rank', 'international_reputation', 'weak_foot', 'body_type', 'movement_reactions','power_shot_power',
                 'goalkeeping_diving','goalkeeping_handling', 'goalkeeping_kicking', 'goalkeeping_positioning', 'goalkeeping_reflexes']]
final_gk_target = df_gk['overall']

final_gk_sum = final_gk.copy()

#obtaining a common feature for all gk attributes using mean
final_gk_sum['GK_attribute'] = final_gk_sum[['goalkeeping_diving','goalkeeping_handling', 'goalkeeping_kicking',
                                     'goalkeeping_positioning', 'goalkeeping_reflexes']].sum(axis = 1)

final_gk_sum.drop(['goalkeeping_diving','goalkeeping_handling', 'goalkeeping_kicking',
                                     'goalkeeping_positioning', 'goalkeeping_reflexes'], axis = 1, inplace = True)

final_gk_sum.head()

encoded_final_gk = final_gk_sum.copy()

#label encode object variables
import pickle
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
col_toencode = encoded_final_gk.select_dtypes(['object'])
for col in col_toencode.columns:
  encoded_final_gk[col] = le.fit_transform(encoded_final_gk[col])
  output = open(f'{col}gk.pkl', 'wb')
  pickle.dump(le, output)
  output.close()

encoded_final_gk.head(10)

"""**Scaling and outlier handling skipped as all columns are discrete numerical.**

Normalization
"""

#from sklearn.preprocessing import normalize
#x_norm = normalize(scaled_gk)
#norm_gk = pd.DataFrame(x_norm)
#norm_gk.describe()

"""Prediction models"""

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(encoded_final_gk, final_gk_target, test_size=0.2, random_state=42)

# Create a list to store information about different regression models
models = []

#linear regression model
lm = LinearRegression()
lm_model = lm.fit(X_train.values, y_train)
y_pred = lm_model.predict(X_test.values)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Linear Regression', 'mse': mse, 'r2': r2})

# Create the XGBRegressor model
xgb_model = XGBRegressor(objective='reg:squarederror', n_estimators=100)

# Train the model
xgb_model.fit(X_train, y_train)

# Make predictions on the testing set
y_pred = xgb_model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'XGBRegressor', 'mse': mse, 'r2': r2})

#random forest classifier
rf_cl = RandomForestClassifier(random_state = 1, n_estimators=20, max_depth = 20, criterion='entropy')
rf_cl.fit(X_train, y_train)
y_pred = rf_cl.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Random forest', 'mse': mse, 'r2': r2})

#decision tree model
dt_cl = DecisionTreeClassifier(random_state =2)
dt_cl.fit(X_train, y_train)
y_pred = dt_cl.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Decision tree', 'mse': mse, 'r2': r2})

"""Comparing models by weighted scores of R2 and MSE"""

compare_models(models)



"""# **   PICKLE GK**"""

import pickle
pickle.dump(lm_model, open('model_GK.pkl', 'wb'))

pickled_model_GK=pickle.load(open('model_GK.pkl','rb'))

pkl_file = open('body_typegk.pkl', 'rb')
le_body_typegk = pickle.load(pkl_file)
pkl_file.close()

s=[[1.0,3,3,'Other',88,59,437]]

s=pd.DataFrame(s)

s[3] = le_body_typegk.transform(s[3])

s[3]

pickled_model_GK.predict(s)

pickled_model_GK.predict([[3.0,1,2,2,42,32,235]])

"""# **PLAYER POSITION = 'DEF'**
xgb 0.9729
"""

df_DEF = final_withoutplayertraits.loc[final_withoutplayertraits['grouped_position'] == 'DEF',[ 'preferred_foot','league_rank', 'international_reputation',
        'weak_foot','work_rate', 'body_type','pace', 'shooting',
        'passing','dribbling', 'defending', 'physic','attacking_crossing', 'attacking_finishing',
       'attacking_heading_accuracy', 'attacking_short_passing', 'attacking_volleys',
       'skill_dribbling', 'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
       'skill_ball_control', 'movement_acceleration', 'movement_sprint_speed', 'movement_agility',
       'movement_reactions', 'movement_balance', 'power_shot_power', 'power_jumping',
       'power_stamina', 'power_strength', 'power_long_shots', 'mentality_aggression',
       'mentality_interceptions', 'mentality_positioning', 'mentality_vision',
       'mentality_penalties', 'mentality_composure', 'defending_standing_tackle',
       'defending_sliding_tackle','overall']]
df_DEF.head(5)

#cross checking correlation  for numerical data
corr_data =df_DEF[['attacking_crossing', 'attacking_finishing',
       'attacking_heading_accuracy', 'attacking_short_passing', 'attacking_volleys',
       'skill_dribbling', 'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
       'skill_ball_control', 'movement_acceleration', 'movement_sprint_speed', 'movement_agility',
       'movement_reactions', 'movement_balance', 'power_shot_power', 'power_jumping',
       'power_stamina', 'power_strength', 'power_long_shots', 'mentality_aggression',
       'mentality_interceptions', 'mentality_positioning', 'mentality_vision',
       'mentality_penalties', 'mentality_composure', 'defending_standing_tackle',
       'defending_sliding_tackle','pace', 'shooting','passing','dribbling', 'defending', 'physic', 'overall']]
fig, ax = plt.subplots(figsize=(20, 15))
sns.heatmap(corr_data.corr(), annot = True)
plt.show()

#cross checking ch2 test for discrete numerical data
for col in ['league_rank', 'international_reputation', 'weak_foot',
        'work_rate', 'body_type','preferred_foot']:
  print("\nCh2 on ", col)
  chi2_test(df_DEF[col],df_DEF['overall'])

final_DEF = df_DEF[['league_rank', 'international_reputation', 'weak_foot', 'work_rate','body_type','attacking_heading_accuracy',
                    'attacking_short_passing','skill_ball_control','movement_reactions','mentality_interceptions',
                    'mentality_composure','defending_sliding_tackle' ,'passing', 'defending','physic', 'dribbling']]
final_DEF_target = df_DEF['overall']
final_DEF.head()

final_DEF.shape



encoded_final_DEF = final_DEF.copy()

#label encode object variables
from sklearn.preprocessing import LabelEncoder
le_DEF = LabelEncoder()
col_toencode = encoded_final_DEF.select_dtypes(['object'])
for col in col_toencode.columns:
  encoded_final_DEF[col] = le_DEF.fit_transform(encoded_final_DEF[col])
  output = open(f'{col}_def.pkl', 'wb')
  pickle.dump(le, output)
  output.close()



pkl_file = open('body_type_def.pkl', 'rb')
le_body_type_def = pickle.load(pkl_file)
pkl_file.close()



pkl_file = open('work_rate_def.pkl', 'rb')
work_rate_type_def = pickle.load(pkl_file)
pkl_file.close()

import pickle
pickle.dump(le_DEF, open('le_DEF.pkl', 'wb'))

pickled_model_le_DEF=pickle.load(open('le_DEF.pkl','rb'))

encoded_final_DEF.head(10)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(encoded_final_DEF, final_DEF_target, test_size=0.2, random_state=42)

# Create a list to store information about different regression models
models = []

#linear regression model
lm = LinearRegression()
lm_model = lm.fit(X_train.values, y_train)
y_pred = lm_model.predict(X_test.values)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Linear Regression', 'mse': mse, 'r2': r2})

# Create the XGBRegressor model
xgb_model = XGBRegressor(objective='reg:squarederror', n_estimators=20)

# Train the model
xgb_model.fit(X_train, y_train)

# Make predictions on the testing set
y_pred = xgb_model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'XGBRegressor', 'mse': mse, 'r2': r2})

#lasso regression
lasso_model = Lasso(alpha=0.05)  # Adjust alpha (regularization parameter) as needed

# Train the model
lasso_model.fit(X_train, y_train)

# Predict the target variable for the new data
y_pred = lasso_model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Lasso Regression', 'mse': mse, 'r2': r2})

#random forest classifier
rf_cl = RandomForestClassifier(random_state = 1, n_estimators=20, max_depth = 20, criterion='entropy')
rf_cl.fit(X_train, y_train)
y_pred = rf_cl.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Random forest', 'mse': mse, 'r2': r2})

#decision tree model
dt_cl = DecisionTreeClassifier(random_state =2)
dt_cl.fit(X_train, y_train)
y_pred = dt_cl.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Decision tree', 'mse': mse, 'r2': r2})

compare_models(models)

#stratified kfold for the best model
stratified_cv = StratifiedKFold(n_splits = 50)
cv_score_str = cross_val_score(xgb_model, encoded_final_DEF,final_DEF_target, cv = stratified_cv)
print('Mean score: ',cv_score_str.mean())
print('Std deviation: ',cv_score_str.std())



"""# **   PICKLE DEF**"""

import pickle
pickle.dump(xgb_model, open('model_DEF.pkl', 'wb'))

pickled_model_DEF=pickle.load(open('model_DEF.pkl','rb'))



pickled_model_DEF.predict([[1.0,3,3,6,2,85,78,79,86,87,83,86,64.0,87.0,82.0,64.0]])

"""# **PLAYER POSITION = 'MID'**
xgb 0.9259
"""

df_MID = final_withoutplayertraits.loc[final_withoutplayertraits['grouped_position'] == 'MID',[ 'preferred_foot','league_rank', 'international_reputation',
       'weak_foot','work_rate', 'body_type','skill_moves','pace', 'shooting',
       'passing','dribbling', 'defending', 'physic','attacking_crossing', 'attacking_finishing',
       'attacking_heading_accuracy', 'attacking_short_passing', 'attacking_volleys',
       'skill_dribbling', 'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
       'skill_ball_control', 'movement_acceleration', 'movement_sprint_speed', 'movement_agility',
       'movement_reactions', 'movement_balance', 'power_shot_power', 'power_jumping',
       'power_stamina', 'power_strength', 'power_long_shots', 'mentality_aggression',
       'mentality_interceptions', 'mentality_positioning', 'mentality_vision',
       'mentality_penalties', 'mentality_composure', 'defending_standing_tackle',
       'defending_sliding_tackle','overall']]
df_MID.head(10)

#cross checking correlation  for numerical data
corr_data =df_MID[['attacking_crossing', 'attacking_finishing',
       'attacking_heading_accuracy', 'attacking_short_passing', 'attacking_volleys',
       'skill_dribbling', 'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
       'skill_ball_control', 'movement_acceleration', 'movement_sprint_speed', 'movement_agility',
       'movement_reactions', 'movement_balance', 'power_shot_power', 'power_jumping',
       'power_stamina', 'power_strength', 'power_long_shots', 'mentality_aggression',
       'mentality_interceptions', 'mentality_positioning', 'mentality_vision',
       'mentality_penalties', 'mentality_composure', 'defending_standing_tackle',
       'defending_sliding_tackle','pace', 'shooting','passing','dribbling', 'defending', 'physic', 'overall']]
fig, ax = plt.subplots(figsize=(20, 15))
sns.heatmap(corr_data.corr(), annot = True)
plt.show()

#cross checking ch2 test for discrete numerical data
for col in ['league_rank', 'international_reputation', 'weak_foot', 'skill_moves',
        'work_rate', 'body_type','preferred_foot']:
  print("\nCh2 on ", col)
  chi2_test(df_MID[col],df_MID['overall'])

final_MID = df_MID[['league_rank', 'international_reputation', 'weak_foot', 'skill_moves',
        'work_rate', 'body_type','preferred_foot','attacking_short_passing',
       'skill_dribbling', 'skill_long_passing','skill_ball_control','movement_reactions',
        'power_long_shots','mentality_composure','shooting','passing','dribbling']]

final_MID_target = df_MID['overall']
final_MID.head()

print(final_MID.shape)

encoded_final_MID = final_MID.copy()

#label encode object variables
from sklearn.preprocessing import LabelEncoder
le_MID = LabelEncoder()
col_toencode = encoded_final_MID.select_dtypes(['object'])
for col in col_toencode.columns:
  encoded_final_MID[col] = le_MID.fit_transform(encoded_final_MID[col])
  output = open(f'{col}_mid.pkl', 'wb')
  pickle.dump(le, output)
  output.close()



pkl_file = open('body_type_mid.pkl', 'rb')
le_body_type_mid = pickle.load(pkl_file)
pkl_file.close()



pkl_file = open('work_rate_mid.pkl', 'rb')
work_rate_type_mid = pickle.load(pkl_file)
pkl_file.close()



pkl_file = open('preferred_foot_mid.pkl', 'rb')
preferred_foot_type_mid = pickle.load(pkl_file)
pkl_file.close()

encoded_final_MID.head(10)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(encoded_final_MID, final_MID_target, test_size=0.2, random_state=42)

# Create a list to store information about different regression models
models = []

#linear regression model
lm = LinearRegression()
lm_model = lm.fit(X_train.values, y_train)
y_pred = lm_model.predict(X_test.values)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Linear Regression', 'mse': mse, 'r2': r2})

#lasso regression
lasso_model = Lasso(alpha=0.1)  # Adjust alpha (regularization parameter) as needed

# Train the model
lasso_model.fit(X_train, y_train)

# Predict the target variable for the new data
y_pred = lasso_model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Lasso Regression', 'mse': mse, 'r2': r2})

# Create the XGBRegressor model
xgb_model = XGBRegressor(objective='reg:linear', n_estimators=50)

# Train the model
xgb_model.fit(X_train, y_train)

# Make predictions on the testing set
y_pred = xgb_model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'XGBRegressor', 'mse': mse, 'r2': r2})

residuals = y_test - y_pred

fig, ax = plt.subplots(figsize=(5, 5))
plt.hist(residuals)
plt.show()

#random forest classifier
rf_cl = RandomForestClassifier(random_state = 1, n_estimators=20, max_depth = 20, criterion='entropy')
rf_cl.fit(X_train, y_train)
y_pred = rf_cl.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Random forest', 'mse': mse, 'r2': r2})

#decision tree model
dt_cl = DecisionTreeClassifier(random_state =2)
dt_cl.fit(X_train, y_train)
y_pred = dt_cl.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Decision tree', 'mse': mse, 'r2': r2})

compare_models(models)

#stratified kfold for the best model
stratified_cv = StratifiedKFold(n_splits = 50)
cv_score_str = cross_val_score(xgb_model, encoded_final_MID,final_MID_target, cv = stratified_cv)
print(cv_score_str[[0,1,2,3]])
print('Mean score: ',cv_score_str.mean())
print('Std deviation: ',cv_score_str.std())



"""# **   PICKLE MID**"""

import pickle
pickle.dump(xgb_model, open('model_MID.pkl', 'wb'))

pickled_model_MID=pickle.load(open('model_MID.pkl','rb'))



pickled_model_MID.predict([[1.0,3,3,2,0,2,1,84,69,84,79,87,81,84,73.0,76.0,72.0]])

"""# **PLAYER POSITION = 'FW'**
xgb 0.9695
"""

df_FW = final_withoutplayertraits.loc[final_withoutplayertraits['grouped_position'] == 'FW',[ 'preferred_foot','league_rank', 'international_reputation',
                                                                                               'weak_foot','work_rate', 'body_type','skill_moves','pace', 'shooting',
                                                                                                'passing','dribbling', 'defending', 'physic','attacking_crossing', 'attacking_finishing',
       'attacking_heading_accuracy', 'attacking_short_passing', 'attacking_volleys',
       'skill_dribbling', 'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
       'skill_ball_control', 'movement_acceleration', 'movement_sprint_speed', 'movement_agility',
       'movement_reactions', 'movement_balance', 'power_shot_power', 'power_jumping',
       'power_stamina', 'power_strength', 'power_long_shots', 'mentality_aggression',
       'mentality_interceptions', 'mentality_positioning', 'mentality_vision',
       'mentality_penalties', 'mentality_composure', 'defending_standing_tackle',
       'defending_sliding_tackle','overall']]
df_FW.head(5)

#cross checking correlation  for numerical data
corr_data =df_FW[['attacking_crossing', 'attacking_finishing',
       'attacking_heading_accuracy', 'attacking_short_passing', 'attacking_volleys',
       'skill_dribbling', 'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
       'skill_ball_control', 'movement_acceleration', 'movement_sprint_speed', 'movement_agility',
       'movement_reactions', 'movement_balance', 'power_shot_power', 'power_jumping',
       'power_stamina', 'power_strength', 'power_long_shots', 'mentality_aggression',
       'mentality_interceptions', 'mentality_positioning', 'mentality_vision',
       'mentality_penalties', 'mentality_composure', 'defending_standing_tackle',
       'defending_sliding_tackle','pace', 'shooting','passing','dribbling', 'defending', 'physic','overall']]
fig, ax = plt.subplots(figsize=(20, 15))
sns.heatmap(corr_data.corr(), annot = True)
plt.show()

#cross checking ch2 test for discrete numerical data
for col in ['league_rank', 'international_reputation', 'weak_foot', 'skill_moves',
        'work_rate', 'body_type','preferred_foot']:
  print("\nCh2 on ", col)
  chi2_test(df_FW[col],df_FW['overall'])

final_FW = df_FW[['league_rank', 'international_reputation', 'weak_foot', 'skill_moves',
        'work_rate', 'body_type','attacking_short_passing','attacking_volleys','skill_ball_control',
       'movement_reactions', 'power_shot_power','power_long_shots','mentality_positioning',
       'mentality_composure','shooting','passing','dribbling']]

final_FW_target = df_FW['overall']
final_FW.head()

final_FW.shape

final_FW.dtypes

encoded_final_FW = final_FW.copy()

#label encode object variables
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
col_toencode = encoded_final_FW.select_dtypes(['object'])
for col in col_toencode.columns:
  encoded_final_FW[col] = le.fit_transform(encoded_final_FW[col])
  output = open(f'{col}.pkl', 'wb')
  pickle.dump(le, output)
  output.close()



encoded_final_FW.head(10)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(encoded_final_FW, final_FW_target, test_size=0.2, random_state=42)

# Create a list to store information about different regression models
models = []

#linear regression model
lm = LinearRegression()
lm_model = lm.fit(X_train.values, y_train)
y_pred = lm_model.predict(X_test.values)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Linear Regression', 'mse': mse, 'r2': r2})

# Create the XGBRegressor model
xgb_model = XGBRegressor(objective='reg:squarederror', n_estimators=50)

# Train the model
xgb_model.fit(X_train, y_train)

# Make predictions on the testing set
y_pred = xgb_model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'XGBRegressor', 'mse': mse, 'r2': r2})

#random forest classifier
rf_cl = RandomForestClassifier(random_state = 1, n_estimators=20, max_depth = 20, criterion='entropy')
rf_cl.fit(X_train, y_train)
y_pred = rf_cl.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Random forest', 'mse': mse, 'r2': r2})

#decision tree model
dt_cl = DecisionTreeClassifier(random_state =2)
dt_cl.fit(X_train, y_train)
y_pred = dt_cl.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print("R-squared (R2) score:", r2)
print("Mean-squared error (MSE):", mse)

models.append({'Name': 'Decision tree', 'mse': mse, 'r2': r2})

compare_models(models)

#stratified kfold for the best model
stratified_cv = StratifiedKFold(n_splits = 10)
cv_score_str = cross_val_score(lm, encoded_final_FW,final_FW_target, cv = stratified_cv)
print('Mean score: ',cv_score_str.mean())
print('Std deviation: ',cv_score_str.std())



"""# **   PICKLE FW**"""

import pickle
pickle.dump(xgb_model, open('model_FW.pkl', 'wb'))

pickled_model_FW=pickle.load(open('model_FW.pkl','rb'))

pickled_model_FW.predict([[1.0,3,3,2,0,2,1,84,69,84,79,87,81,84,73.0,76.0,72.0]])

s=[[1.0,5,4,5,'High/Medium','Other',82,86,92,95,94,93,95,95,93.0,81.0,89.0]]
s=pd.DataFrame(s)

s.dtypes



work_rate_encoder=pickle.load(open('work_rate.pkl','rb'))

s[4]=work_rate_encoder.transform(s[4])

s[4]



body_type_encoder=pickle.load(open('body_type.pkl','rb'))

s[5]=body_type_encoder.transform(s[5])

s[5]

print(final_MID.shape)
print(final_DEF.shape)
print(final_FW.shape)
print(final_gk.shape)
