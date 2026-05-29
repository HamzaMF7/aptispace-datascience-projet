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
    Sépare les données en ensembles d'entraînement/test (valeurs connues) et de scouting (valeurs manquantes).
    Conserve les DataFrames de métadonnées pour le storytelling opérationnel (noms de joueurs, clubs).
    """
    # Sélection des features pertinentes pour le modèle
    features_numeric = ['age', 'age_squared', 'height_in_cm', 'goals_per_90', 
                        'assists_per_90', 'cards_per_90', 'international_caps', 'intl_efficiency']
    features_categorical = ['position', 'foot']
    
    # 1. Séparation des joueurs labélisés (valeur connue) et scouting (NaN)
    df_labeled = df[df[target_col].notna()].copy()
    df_scouting = df[df[target_col].isna()].copy()
    
    # 2. Découpage Train/Test sur les données labélisées
    df_train, df_test = train_test_split(df_labeled, test_size=0.2, random_state=42)
    
    # 3. Extraction des matrices explicatives (X) et cibles (y, log-transform)
    X_train = df_train[features_numeric + features_categorical]
    y_train = np.log1p(df_train[target_col])
    
    X_test = df_test[features_numeric + features_categorical]
    y_test = np.log1p(df_test[target_col])
    
    # Pour le scouting, on prépare uniquement la matrice explicative X
    X_scouting = df_scouting[features_numeric + features_categorical]
    
    return df_train, df_test, df_scouting, X_train, X_test, X_scouting, y_train, y_test, features_numeric, features_categorical

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