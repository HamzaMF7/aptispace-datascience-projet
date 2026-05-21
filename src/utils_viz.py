import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_target_distribution(df, target_col='market_value_in_eur'):
    """
    Trace la distribution de la valeur marchande (Brute vs Logarithmique).
    Utile pour l'audit et montre pourquoi une transformation log est souvent requise en ML.
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. Distribution brute
    sns.histplot(df[target_col], bins=50, kde=True, ax=axes[0], color='#0284c7')
    axes[0].set_title("Distribution brute de la Valeur Marchande", fontsize=12)
    axes[0].set_xlabel("Valeur en EUR")
    axes[0].set_ylabel("Nombre de Joueurs")
    
    # 2. Distribution Logarithmique (pour gérer l'asymétrie)
    sns.histplot(np.log1p(df[target_col]), bins=50, kde=True, ax=axes[1], color='#16a34a')
    axes[1].set_title("Distribution Logarithmique: $\log(1 + x)$", fontsize=12)
    axes[1].set_xlabel("Log de la Valeur")
    axes[1].set_ylabel("Nombre de Joueurs")
    
    plt.tight_layout()
    return fig

def plot_correlation_matrix(df, numeric_cols):
    """
    Génère une matrice de corrélation de Pearson pour les variables numériques clés.

    """
    # Calcul de la matrice
    corr = df[numeric_cols].corr(method='pearson')
    
    # Masque pour le triangle supérieur (plus esthétique)
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(
        corr, 
        mask=mask, 
        cmap='coolwarm', 
        vmax=1, 
        vmin=-1, 
        center=0,
        square=True, 
        linewidths=.5, 
        cbar_kws={"shrink": .7},
        annot=True, 
        fmt=".2f", 
        ax=ax
    )
    
    ax.set_title("Matrice de Corrélation des Caractéristiques", fontsize=14, pad=20)
    plt.tight_layout()
    return fig