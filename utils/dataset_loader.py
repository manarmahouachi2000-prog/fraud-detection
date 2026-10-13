"""
Chargement et gestion du dataset PaySim
"""
import pandas as pd
import streamlit as st
import os

# Chemin du dataset
DATASET_PATH = r"C:\Users\mahouachi\OneDrive\Desktop\fraud detection\data\PS_20174392719_1491204439457_log.csv"


@st.cache_data(show_spinner=False)
def charger_dataset(nrows=100000):
    """
    Charge un échantillon du dataset PaySim (cache Streamlit).
    nrows=100000 par défaut pour la rapidité.
    """
    if not os.path.exists(DATASET_PATH):
        return None

    df = pd.read_csv(DATASET_PATH, nrows=nrows)
    return df


@st.cache_data(show_spinner=False)
def rechercher_par_client(name_orig, nrows=500000):
    """Recherche les transactions d'un client spécifique."""
    df = charger_dataset(nrows)
    if df is None:
        return None

    result = df[df['nameOrig'] == name_orig]
    return result


@st.cache_data(show_spinner=False)
def rechercher_par_dest(name_dest, nrows=100000):
    """Recherche les transactions vers un destinataire."""
    df = charger_dataset(nrows)
    if df is None:
        return None

    result = df[df['nameDest'] == name_dest]
    return result


def obtenir_stats_dataset():
    """Retourne les statistiques du dataset."""
    df = charger_dataset()
    if df is None:
        return None

    return {
        'total_lignes': len(df),
        'nb_clients_uniques': df['nameOrig'].nunique(),
        'nb_dest_uniques': df['nameDest'].nunique(),
        'nb_fraudes': int(df['isFraud'].sum()) if 'isFraud' in df.columns else 0,
        'taux_fraude': df['isFraud'].mean() * 100 if 'isFraud' in df.columns else 0,
    }

@st.cache_data(show_spinner=False)
def obtenir_exemples_clients(n=10):
    """Retourne des ID clients d'exemples (inclut des cas frauduleux)."""
    df = charger_dataset(nrows=500000)
    if df is None or len(df) == 0:
        return []

    exemples = []

    # ── 1. Chercher des clients FRAUDULEUX (isFraud == 1) ──
    if 'isFraud' in df.columns:
        fraudes = df[df['isFraud'] == 1]
        if len(fraudes) > 0:
            clients_fraude = fraudes['nameOrig'].unique().tolist()[:5]
            exemples.extend(clients_fraude)

    # ── 2. Compléter avec clients à haut risque (gros montants) ──
    if len(exemples) < n:
        risques = df[df['type'].isin(['TRANSFER', 'CASH_OUT'])]
        gros = risques.nlargest(100, 'amount')
        clients_risque = gros['nameOrig'].unique().tolist()
        for c in clients_risque:
            if c not in exemples:
                exemples.append(c)
            if len(exemples) >= n:
                break

    # ── 3. Compléter avec clients aléatoires si besoin ──
    if len(exemples) < n:
        clients_random = df['nameOrig'].dropna().unique().tolist()
        for c in clients_random:
            if c not in exemples:
                exemples.append(c)
            if len(exemples) >= n:
                break

    return exemples[:n]


@st.cache_data(show_spinner=False)
def obtenir_clients_frauduleux(n=10):
    """Retourne UNIQUEMENT des clients ayant commis une fraude."""
    df = charger_dataset(nrows=500000)
    if df is None or 'isFraud' not in df.columns:
        return []

    fraudes = df[df['isFraud'] == 1]
    return fraudes['nameOrig'].unique().tolist()[:n]


@st.cache_data(show_spinner=False)
def obtenir_clients_haut_risque(n=10):
    """Retourne des clients avec des TRANSFER/CASH_OUT de gros montants."""
    df = charger_dataset(nrows=500000)
    if df is None:
        return []

    risques = df[df['type'].isin(['TRANSFER', 'CASH_OUT'])]
    gros = risques.nlargest(200, 'amount')
    return gros['nameOrig'].unique().tolist()[:n]