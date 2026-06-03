import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score
from sklearn.pipeline import Pipeline

# 1. Load Data
df = pd.read_csv('social_media_mental_health.csv')
drop_cols = ['User_ID', 'GAD_7_Severity', 'PHQ_9_Severity']
df_cleaned = df.drop(columns=drop_cols)

X = df_cleaned.drop(columns=['GAD_7_Score', 'PHQ_9_Score'])
y_gad = df_cleaned['GAD_7_Score']
y_phq = df_cleaned['PHQ_9_Score']

# 2. Preprocessor
categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numerical_cols),
        ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_cols)
    ])

# 3. Splits
X_train_gad, X_test_gad, y_train_gad, y_test_gad = train_test_split(X, y_gad, test_size=0.2, random_state=42)
X_train_phq, X_test_phq, y_train_phq, y_test_phq = train_test_split(X, y_phq, test_size=0.2, random_state=42)

# 4. Models
def get_models():
    return {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(),
        'Random Forest': RandomForestRegressor(random_state=42, n_estimators=100),
        'Gradient Boosting': GradientBoostingRegressor(random_state=42)
    }

# 5. Train and Find Best
def train_and_save(target_name, X_train, X_test, y_train, y_test, filename):
    best_score = -float('inf')
    best_pipeline = None
    best_name = ""
    
    models = get_models()
    for name, model in models.items():
        pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
        pipeline.fit(X_train, y_train)
        
        preds = pipeline.predict(X_test)
        score = r2_score(y_test, preds)
        
        print(f"{target_name} - {name}: R2 = {score:.4f}")
        if score > best_score:
            best_score = score
            best_pipeline = pipeline
            best_name = name
            
    print(f"Best model for {target_name} is {best_name} with R2 = {best_score:.4f}")
    
    # Save the pipeline
    with open(filename, 'wb') as f:
        pickle.dump(best_pipeline, f)
    print(f"Saved to {filename}\n")

print("Training GAD-7 models...")
train_and_save("GAD-7", X_train_gad, X_test_gad, y_train_gad, y_test_gad, 'model_gad7.pkl')

print("Training PHQ-9 models...")
train_and_save("PHQ-9", X_train_phq, X_test_phq, y_train_phq, y_test_phq, 'model_phq9.pkl')

print("All done!")
