import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def prepare_data(df, target_col='market_value_in_eur'):
    """
    Sépare les features de la cible et applique un découpage Train/Test.
    """
    # Sélection des features pertinentes pour le modèle
    features_numeric = ['age', 'age_squared', 'height_in_cm', 'goals_per_90', 
                        'assists_per_90', 'cards_per_90', 'international_caps', 'intl_efficiency']
    features_categorical = ['position', 'foot']
    
    X = df[features_numeric + features_categorical]
    # Transformation logarithmique de la cible pour stabiliser la variance (comme vu à l'EDA)
    y = np.log1p(df[target_col]) 
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test, features_numeric, features_categorical

def build_preprocessing_pipeline(numeric_cols, categorical_cols):
    """
    Crée un pipeline de prétraitement automatique avec ColumnTransformer.
    """
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_cols),
            ('cat', categorical_transformer, categorical_cols)
        ])
    
    return preprocessor

def evaluate_predictions(y_true_log, y_pred_log):
    """
    Calcule les métriques à la fois sur l'échelle Log et l'échelle réelle (Euros).
    """
    # Revenir à l'échelle réelle en Euros (Inversion du log1p via expm1)
    y_true = np.expm1(y_true_log)
    y_pred = np.expm1(y_pred_log)
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true_log, y_pred_log) # Le R² se calcule généralement sur l'espace de distribution du modèle
    
    return mae, rmse, r2