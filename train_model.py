import pandas as pd
import pickle
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

print("Sedang melatih model... Harap tunggu.")

# 1. Muat dataset
df = pd.read_csv('social_media_mental_health.csv')

# 2. Tentukan fitur (X) dan target (y)
X = df[['Age', 'Gender', 'User_Archetype', 'Primary_Platform', 'Daily_Screen_Time_Hours', 
        'Dominant_Content_Type', 'Activity_Type', 'Late_Night_Usage', 'Social_Comparison_Trigger', 'Sleep_Duration_Hours']]
y_gad = df['GAD_7_Score']
y_phq = df['PHQ_9_Score']

# 3. Pisahkan kolom kategorikal dan numerikal
categorical_cols = ['Gender', 'User_Archetype', 'Primary_Platform', 'Dominant_Content_Type', 'Activity_Type']
numerical_cols = ['Age', 'Daily_Screen_Time_Hours', 'Late_Night_Usage', 'Social_Comparison_Trigger', 'Sleep_Duration_Hours']

# 4. Buat Preprocessor untuk menyelaraskan data teks ke angka
preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numerical_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ])

# 5. Bangun Pipeline Model untuk GAD-7 dan PHQ-9
model_gad = Pipeline(steps=[('preprocessor', preprocessor),
                           ('regressor', RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1))])

model_phq = Pipeline(steps=[('preprocessor', preprocessor),
                           ('regressor', RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1))])

# 6. Fit Model
model_gad.fit(X, y_gad)
model_phq.fit(X, y_phq)

# 7. Simpan model menjadi file .pkl
with open('model_gad7.pkl', 'wb') as f:
    pickle.dump(model_gad, f)

with open('model_phq9.pkl', 'wb') as f:
    pickle.dump(model_phq, f)

print("Berhasil! File 'model_gad7.pkl' dan 'model_phq9.pkl' siap digunakan.")