import pandas as pd
import numpy as np

def clean_dates(df, date_columns):
    """
    Uniformise et convertit les colonnes spécifiées au format datetime.
    """
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def impute_missing_data(df_players):
    """
    Gère les valeurs manquantes critiques.
    - market_value_in_eur : Imputation par la médiane selon le poste (position)
    - foot : Pied fort par défaut à 'right' si manquant (le plus fréquent)
    """
    df = df_players.copy()
    
    # NOTE : La variable cible 'market_value_in_eur' n'est plus imputée ici pour éviter de biaiser l'entraînement.
    # Les valeurs manquantes (NaN) seront séparées dans le jeu de scouting lors de la préparation des données.
        
    # Imputation du pied fort
    if 'foot' in df.columns:
        df['foot'] = df['foot'].fillna('right')
        
    # Imputation de la taille (height_in_cm) par la moyenne globale
    if 'height_in_cm' in df.columns:
        df['height_in_cm'] = df['height_in_cm'].fillna(df['height_in_cm'].mean())
        
    return df

def aggregate_performances(df_appearances):
    """
    Agrège les statistiques de matchs (appearances) par joueur pour obtenir 
    une ligne unique par joueur avec ses statistiques cumulées historiques.
    """
    # Agrégation par joueur
    df_agg = df_appearances.groupby('player_id').agg({
        'goals': 'sum',
        'assists': 'sum',
        'minutes_played': 'sum',
        'yellow_cards': 'sum',
        'red_cards': 'sum'
    }).reset_index()
    
    # Feature Engineering précoce : Normalisation par tranche de 90 minutes
    # On ajoute +1 pour éviter la division par zéro si un joueur a 0 minute jouée
    df_agg['goals_per_90'] = (df_agg['goals'] / (df_agg['minutes_played'] + 1)) * 90
    df_agg['assists_per_90'] = (df_agg['assists'] / (df_agg['minutes_played'] + 1)) * 90
    
    return df_agg

def build_final_dataset(df_players, df_perf_agg):
    """
    Fusionne la table des profils joueurs nettoyée avec leurs statistiques cumulées.
    """
    # Jointure de type inner pour ne garder que les joueurs qui ont des correspondances
    df_final = pd.merge(df_players, df_perf_agg, on='player_id', how='inner')
    
    # Nettoyage final des colonnes inutiles pour l'apprentissage automatique (ML)
    columns_to_drop = ['image_url', 'url', 'player_code']
    df_final = df_final.drop(columns=[col for col in columns_to_drop if col in df_final.columns])
    
    return df_final