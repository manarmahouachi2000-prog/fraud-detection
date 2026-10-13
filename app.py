"""
Système Intelligent de Détection de Fraude
Application Streamlit — PaySim 6.3M — ATB
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import sqlite3
import matplotlib.pyplot as plt
import base64
import os
from datetime import datetime

# Chemin base de données : /tmp sur Streamlit Cloud, dossier local sinon
DB_PATH = "/tmp/fraude.db" if os.path.exists("/tmp") else "fraude.db"

# ==============================================================
# CONFIGURATION
# ==============================================================
st.set_page_config(
    page_title="Détection de Fraude | ATB",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================
# CHARGEMENT DU MODÈLE
# ==============================================================
@st.cache_resource
def load_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "Models", "random_forest_model.pkl")
    return joblib.load(path)

model = load_model()

# ==============================================================
# BASE DE DONNÉES
# ==============================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            transaction_type TEXT,
            amount REAL,
            is_fraud INTEGER,
            fraud_probability REAL,
            risk_score TEXT
        )
    """)
    conn.commit()
    conn.close()

def init_users_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            nom TEXT,
            timestamp TEXT,
            action TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_connexion(email, nom, action="connexion"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO sessions (email, nom, timestamp, action)
        VALUES (?, ?, ?, ?)
    """, (email, nom, datetime.now().isoformat(), action))
    conn.commit()
    conn.close()

def save_prediction(tx_type, amount, is_fraud, prob, risk):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO predictions
        (timestamp, transaction_type, amount, is_fraud, fraud_probability, risk_score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), tx_type, amount, int(is_fraud), prob, risk))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM predictions ORDER BY id DESC LIMIT 50", conn)
    conn.close()
    return df

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM predictions", conn)
    conn.close()
    return df

# ==============================================================
# AUTHENTIFICATION
# ==============================================================
BANQUIERS_AUTORISES = {
    "manarmahouachi2000@gmail.com": "Manar Mahouachi",
}

def verifier_banquier(email):
    email = email.strip().lower()
    if email in BANQUIERS_AUTORISES:
        return True, BANQUIERS_AUTORISES[email]
    return False, None

def page_connexion():
    """Page de connexion — design moderne ATB."""
    try:
        with open("atb_background.jpg", "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
    except Exception:
        logo_b64 = ""

    st.markdown("""
    <style>
        .stApp {
            background: 
                radial-gradient(circle at 20% 30%, #8B0000 0%, transparent 45%),
                radial-gradient(circle at 80% 20%, #1D9E75 0%, transparent 45%),
                radial-gradient(circle at 75% 80%, #6B0000 0%, transparent 45%),
                radial-gradient(circle at 25% 75%, #0a5a3a 0%, transparent 45%),
                linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            background-attachment: fixed;
        }
        header[data-testid="stHeader"] { background: transparent; }
        .login-wrapper {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 2.5rem 3rem;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.25);
            max-width: 480px;
            margin: 2rem auto 1rem auto;
            border: 1px solid rgba(255, 255, 255, 0.6);
        }
        .card-logo {
            display: block;
            margin: 0 auto 1.5rem auto;
            width: 130px;
            height: auto;
        }
        .card-title {
            text-align: center;
            color: #8B0000;
            font-size: 1.7rem;
            font-weight: 700;
            margin: 0 0 0.5rem 0;
        }
        .card-subtitle {
            text-align: center;
            color: #666;
            font-size: 0.95rem;
            margin: 0 0 1rem 0;
            font-weight: 500;
        }
        .card-divider {
            height: 3px;
            background: linear-gradient(90deg, #8B0000 0%, #1D9E75 100%);
            border: none;
            border-radius: 2px;
            margin: 1.5rem 0;
            opacity: 0.7;
        }
        .stButton > button {
            width: 100%;
            background: linear-gradient(90deg, #8B0000 0%, #6B0000 100%);
            color: white !important;
            font-weight: 600;
            padding: 0.9rem;
            border: none;
            border-radius: 12px;
            font-size: 1.05rem;
            transition: all 0.3s ease;
            box-shadow: 0 6px 20px rgba(139, 0, 0, 0.35);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            background: linear-gradient(90deg, #6B0000 0%, #8B0000 100%);
            box-shadow: 0 10px 30px rgba(139, 0, 0, 0.5);
        }
        .stTextInput > div > div > input {
            border-radius: 12px !important;
            border: 2px solid #e0e0e0 !important;
            padding: 0.85rem 1rem !important;
            font-size: 1rem !important;
            background: white !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #8B0000 !important;
            box-shadow: 0 0 0 4px rgba(139, 0, 0, 0.12) !important;
        }
        .security-note {
            text-align: center;
            color: #888;
            font-size: 0.82rem;
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px dashed #ddd;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown(f"""
        <div class="login-wrapper">
            <img src="data:image/jpeg;base64,{logo_b64}" class="card-logo" alt="ATB">
            <h1 class="card-title">Système de Détection de Fraude</h1>
            <p class="card-subtitle">Arab Tunisian Bank — Espace Sécurisé</p>
            <hr class="card-divider">
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Saisissez votre adresse email professionnelle.**")

        email = st.text_input("📧 Adresse email",
                              placeholder="prenom.nom@atb.com.tn",
                              key="login_email")

        if st.button("🚀 Se connecter", use_container_width=True):
            if not email or "@" not in email:
                st.error("❌ Veuillez saisir une adresse email valide.")
            else:
                ok, nom = verifier_banquier(email)
                if ok:
                    st.session_state['logged_in'] = True
                    st.session_state['banquier_email'] = email
                    st.session_state['banquier_nom'] = nom
                    log_connexion(email, nom, "connexion")
                    st.success(f"✅ Bienvenue {nom} !")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Accès refusé — Email non autorisé.")
                    st.caption("Contactez votre administrateur.")

        st.markdown(
            '<p class="security-note">🔒 Connexion sécurisée · Toutes les tentatives sont enregistrées</p>',
            unsafe_allow_html=True
        )

# ==============================================================
# FEATURE ENGINEERING
# ==============================================================
TYPE_MAPPING = {'CASH_IN': 0, 'CASH_OUT': 1, 'DEBIT': 2, 'PAYMENT': 3, 'TRANSFER': 4}
AVG_AMOUNT   = {'CASH_IN': 168866, 'CASH_OUT': 191537, 'DEBIT': 5793,
                'PAYMENT': 9839, 'TRANSFER': 487839}

def engineer_features(tx_type, amount, old_orig, new_orig, old_dest, new_dest):
    type_enc = TYPE_MAPPING.get(tx_type, 0)
    return pd.DataFrame([{
        'type_encoded'     : type_enc,
        'amount'           : amount,
        'oldbalanceOrg'    : old_orig,
        'newbalanceOrig'   : new_orig,
        'oldbalanceDest'   : old_dest,
        'newbalanceDest'   : new_dest,
        'errorBalanceOrig' : new_orig + amount - old_orig,
        'errorBalanceDest' : old_dest + amount - new_dest,
        'isZeroOrig'       : 1 if old_orig == 0 else 0,
        'isZeroDest'       : 1 if new_dest == 0 else 0,
        'amountRatio'      : amount / (old_orig + 1),
        'nb_tx_step'       : 100,
        'is_large_tx'      : 1 if amount > AVG_AMOUNT.get(tx_type, 100000) * 2 else 0,
    }])

def get_risk(prob):
    if prob < 0.3:  return "🟢 FAIBLE",   "green"
    if prob < 0.6:  return "🟡 MODÉRÉ",   "orange"
    if prob < 0.85: return "🔴 ÉLEVÉ",    "red"
    return "🚨 CRITIQUE", "darkred"

# ==============================================================
# INITIALISATION
# ==============================================================
init_users_db()
init_db()

# ==============================================================
# VÉRIFICATION AUTHENTIFICATION
# ==============================================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    page_connexion()
    st.stop()

# ==============================================================
# SIDEBAR
# ==============================================================
try:
    st.sidebar.image("atb_background.jpg", width=120)
except Exception:
    st.sidebar.markdown("# 🏦")

st.sidebar.title("🛡️ Détection de Fraude")
st.sidebar.markdown("---")

st.sidebar.success(f"👤 **{st.session_state.get('banquier_nom', 'Utilisateur')}**")
st.sidebar.caption(f"📧 {st.session_state.get('banquier_email', '')}")

if st.sidebar.button("🚪 Se déconnecter", use_container_width=True):
    log_connexion(
        st.session_state.get('banquier_email', ''),
        st.session_state.get('banquier_nom', ''),
        "deconnexion"
    )
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("---")

options = [
    "🏠 Accueil",
    "🔍 Analyser une transaction",
    "📁 Analyse batch CSV",
    "📊 Dashboard",
    "🤖 Comparaison modèles",
    "📬 Notifications"
]

default_index = 0
if 'rediriger' in st.session_state:
    cible = st.session_state['rediriger']
    if cible in options:
        default_index = options.index(cible)
        st.session_state.pop('rediriger')

page = st.sidebar.radio("Navigation", options, index=default_index)

st.sidebar.markdown("---")
st.sidebar.markdown("**Modèle :** Random Forest")
st.sidebar.markdown("**Dataset :** PaySim 6.3M")
st.sidebar.markdown("**F1-Score :** 0.94")
st.sidebar.markdown("**AUC-ROC :** 0.9998")

# ==============================================================
# PAGE 1 — ACCUEIL
# ==============================================================
if page == "🏠 Accueil":
    import plotly.graph_objects as go

    nom_banquier = st.session_state.get('banquier_nom', 'Utilisateur')
    date_now = datetime.now().strftime("%A %d %B %Y · %H:%M")

    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #8B0000 0%, #1D9E75 100%);
                color: white; padding: 1.5rem 2rem; border-radius: 12px;
                margin-bottom: 2rem;">
        <h1 style="margin: 0; color: white;">🛡️ Système de Détection de Fraude</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.95;">
            👤 Bienvenue <b>{nom_banquier}</b> · 📅 {date_now}
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #E8F5F0 0%, #D1EDE1 100%);
                    padding: 1.5rem; border-radius: 12px; border-left: 5px solid #1D9E75;">
            <p style="margin: 0; color: #666; font-size: 0.9rem;">📊 DATASET</p>
            <h2 style="margin: 0.3rem 0; color: #1D9E75; font-size: 2rem;">6.3M</h2>
            <p style="margin: 0; color: #888; font-size: 0.85rem;">transactions</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FFF4E5 0%, #FFE4C4 100%);
                    padding: 1.5rem; border-radius: 12px; border-left: 5px solid #EF9F27;">
            <p style="margin: 0; color: #666; font-size: 0.9rem;">🎯 F1-SCORE</p>
            <h2 style="margin: 0.3rem 0; color: #EF9F27; font-size: 2rem;">0.94</h2>
            <p style="margin: 0; color: #888; font-size: 0.85rem;">vs baseline 0.07</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #E8F0FA 0%, #D1E0F5 100%);
                    padding: 1.5rem; border-radius: 12px; border-left: 5px solid #378ADD;">
            <p style="margin: 0; color: #666; font-size: 0.9rem;">📈 AUC-ROC</p>
            <h2 style="margin: 0.3rem 0; color: #378ADD; font-size: 2rem;">0.9998</h2>
            <p style="margin: 0; color: #888; font-size: 0.85rem;">quasi-parfait</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FCE8E8 0%, #F5D1D1 100%);
                    padding: 1.5rem; border-radius: 12px; border-left: 5px solid #8B0000;">
            <p style="margin: 0; color: #666; font-size: 0.9rem;">🚨 DÉTECTION</p>
            <h2 style="margin: 0.3rem 0; color: #8B0000; font-size: 2rem;">99.8%</h2>
            <p style="margin: 0; color: #888; font-size: 0.85rem;">des fraudes</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🏆 Modèle Champion")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #8B0000 0%, #6B0000 100%);
                    color: white; padding: 2rem; border-radius: 12px;">
            <h2 style="color: white; margin: 0;">🌲 Random Forest</h2>
            <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 1.5rem 0;">
                Meilleur parmi 5 modèles testés
            </p>
            <table style="width: 100%; color: white;">
                <tr><td>F1-Score</td><td style="text-align:right;"><b>0.94</b></td></tr>
                <tr><td>AUC-ROC</td><td style="text-align:right;"><b>0.9998</b></td></tr>
                <tr><td>Recall</td><td style="text-align:right;"><b>100%</b></td></tr>
                <tr><td>Precision</td><td style="text-align:right;"><b>90%</b></td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("###  Répartition du Dataset")

        fig = go.Figure(data=[go.Pie(
            labels=['✅ Légitimes', '🚨 Fraudes'],
            values=[6354407, 8213],
            hole=0.65,
            marker=dict(colors=['#1D9E75', '#8B0000']),
            textinfo='label+percent',
            textfont=dict(size=13),
            hovertemplate='<b>%{label}</b><br>%{value:,} transactions<br>%{percent}<extra></extra>'
        )])

        fig.update_layout(
            height=320,
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1,
                        xanchor="center", x=0.5),
            annotations=[dict(
                text='<b>0.13%</b><br><span style="font-size:10px">fraudes</span>',
                x=0.5, y=0.5, font_size=18, showarrow=False
            )]
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown("### 📊 Top 5 Features Importantes")
    st.caption("Ces features contribuent le plus à la détection des fraudes")

    features = ['errorBalanceOrig', 'amountRatio', 'newbalanceOrig',
                'nb_tx_step', 'amount']
    importances = [0.349, 0.253, 0.134, 0.075, 0.050]
    colors = ['#8B0000', '#A50000', '#C20000', '#D94545', '#E88B8B']

    fig = go.Figure(go.Bar(
        x=importances,
        y=features,
        orientation='h',
        marker=dict(color=colors),
        text=[f'{v*100:.1f}%' for v in importances],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Importance: %{x:.3f}<br>(%{text})<extra></extra>'
    ))

    fig.update_layout(
        height=350,
        margin=dict(t=20, b=20, l=20, r=60),
        xaxis=dict(title='Importance', showgrid=True, gridcolor='#eee'),
        yaxis=dict(autorange='reversed'),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown("### 📈 Activité Récente")
    st.caption("Les 5 dernières transactions analysées")

    df_hist = get_history()

    if df_hist.empty:
        st.info("📭 Aucune transaction analysée pour le moment. "
                "Commencez par la page 🔍 Analyser une transaction.")
    else:
        df_recent = df_hist.head(5).copy()
        for _, row in df_recent.iterrows():
            is_fraud = row['is_fraud'] == 1
            color = '#8B0000' if is_fraud else '#1D9E75'
            bg = '#FCE8E8' if is_fraud else '#E8F5F0'
            icon = '🚨' if is_fraud else '✅'
            statut = 'FRAUDE' if is_fraud else 'LÉGITIME'

            st.markdown(f"""
            <div style="background: {bg}; padding: 1rem 1.5rem; border-radius: 10px;
                        margin-bottom: 0.8rem; border-left: 4px solid {color};
                        display: flex; justify-content: space-between;
                        align-items: center;">
                <div><b>{icon} {statut}</b> · {row['transaction_type']}</div>
                <div style="text-align: right;">
                    <b>{row['amount']:,.2f} €</b><br>
                    <small style="color: #888;">{row['timestamp'][:16].replace('T', ' ')}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================
# PAGE 2 — ANALYSER UNE TRANSACTION
# ==============================================================
elif page == "🔍 Analyser une transaction":
    st.title("🔍 Analyser une transaction")
    st.markdown("Recherchez un client dans le dataset PaySim et analysez ses transactions.")
    st.markdown("---")

    from utils.dataset_loader import (
        charger_dataset, rechercher_par_client,
        obtenir_stats_dataset, obtenir_exemples_clients,
        obtenir_clients_frauduleux, obtenir_clients_haut_risque
    )

    with st.spinner("📂 Chargement du dataset PaySim..."):
        df = charger_dataset(nrows=500000)

    if df is None:
        st.error("❌ Dataset introuvable.")
        st.stop()

    stats = obtenir_stats_dataset()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Transactions", f"{stats['total_lignes']:,}")
    with col2:
        st.metric("👥 Clients uniques", f"{stats['nb_clients_uniques']:,}")
    with col3:
        st.metric("🚨 Fraudes", f"{stats['nb_fraudes']:,}")
    with col4:
        st.metric("📈 Taux fraude", f"{stats['taux_fraude']:.3f}%")

    st.markdown("---")
    st.markdown("### 🔍 Rechercher un client")

    col_input, col_btn = st.columns([3, 1])
    with col_input:
        exemples = obtenir_exemples_clients(10)
        exemple_defaut = exemples[0] if exemples else ""

        name_orig = st.text_input(
            "ID Client (nameOrig)",
            value="",
            placeholder=f"Ex: {exemple_defaut}",
            help="Format : C suivi de 9 chiffres (ex: C1231006815)"
        )

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        rechercher = st.button("🔍 Rechercher", use_container_width=True, type="primary")

    st.markdown("### 💡 Exemples de clients à tester")
    tab1, tab2, tab3 = st.tabs(["🚨 Fraudes réelles", "⚠️ Haut risque", "✅ Aléatoires"])

    with tab1:
        clients_fraude = obtenir_clients_frauduleux(5)
        if clients_fraude:
            st.caption("Ces clients ont des transactions marquées comme fraude :")
            cols = st.columns(len(clients_fraude))
            for i, client in enumerate(clients_fraude):
                with cols[i]:
                    if st.button(f"🚨 {client}", key=f"fraude_{i}",
                                 use_container_width=True):
                        st.session_state['client_selectionne'] = client
                        st.rerun()
        else:
            st.info("Aucune fraude dans l'échantillon chargé.")

    with tab2:
        clients_risque = obtenir_clients_haut_risque(5)
        if clients_risque:
            st.caption("Ces clients ont de gros TRANSFER/CASH_OUT :")
            cols = st.columns(len(clients_risque))
            for i, client in enumerate(clients_risque):
                with cols[i]:
                    if st.button(f"⚠️ {client}", key=f"risque_{i}",
                                 use_container_width=True):
                        st.session_state['client_selectionne'] = client
                        st.rerun()

    with tab3:
        exemples = obtenir_exemples_clients(10)
        if exemples:
            st.caption("Clients aléatoires du dataset :")
            cols = st.columns(5)
            for i, client in enumerate(exemples[:5]):
                with cols[i]:
                    if st.button(f"👤 {client}", key=f"rand_{i}",
                                 use_container_width=True):
                        st.session_state['client_selectionne'] = client
                        st.rerun()

    if 'client_selectionne' in st.session_state:
        name_orig = st.session_state['client_selectionne']

    st.markdown("---")

    if rechercher or name_orig:
        if not name_orig:
            st.info("👆 Saisissez un ID client pour commencer")
        else:
            with st.spinner(f"Recherche des transactions de {name_orig}..."):
                transactions = rechercher_par_client(name_orig.strip().upper())

            if transactions is None or len(transactions) == 0:
                st.warning(f"⚠️ Aucune transaction trouvée pour **{name_orig}**.")
            else:
                st.success(f"✅ **{len(transactions)}** transaction(s) pour **{name_orig}**")

                df_affichage = transactions.reset_index(drop=True).copy()

                st.markdown("### 📋 Transactions du client")
                st.dataframe(
                    df_affichage[['step', 'type', 'amount',
                                  'oldbalanceOrg', 'newbalanceOrig',
                                  'oldbalanceDest', 'newbalanceDest']],
                    use_container_width=True,
                    height=300
                )

                st.markdown("### 🎯 Choisir une transaction")

                options_tx = [
                    f"#{i} - {row['type']} {row['amount']:,.2f}€ (step {row['step']})"
                    for i, row in df_affichage.iterrows()
                ]

                choix = st.selectbox("Sélectionnez une transaction :", options_tx)
                index_choisi = int(choix.split(" - ")[0].replace("#", ""))
                tx = df_affichage.iloc[index_choisi]

                col_det1, col_det2 = st.columns(2)
                with col_det1:
                    st.markdown("**📊 Détails**")
                    st.markdown(f"- **Step :** {tx['step']}")
                    st.markdown(f"- **Type :** {tx['type']}")
                    st.markdown(f"- **Montant :** {tx['amount']:,.2f} €")
                    st.markdown(f"- **Émetteur :** `{tx['nameOrig']}`")
                    st.markdown(f"- **Destinataire :** `{tx['nameDest']}`")

                with col_det2:
                    st.markdown("**💰 Soldes**")
                    st.markdown(f"- **Avant émetteur :** {tx['oldbalanceOrg']:,.2f} €")
                    st.markdown(f"- **Après émetteur :** {tx['newbalanceOrig']:,.2f} €")
                    st.markdown(f"- **Avant destinataire :** {tx['oldbalanceDest']:,.2f} €")
                    st.markdown(f"- **Après destinataire :** {tx['newbalanceDest']:,.2f} €")

                if 'isFraud' in tx.index:
                    verite = "🚨 FRAUDE réelle" if tx['isFraud'] == 1 else "✅ Légitime"
                    st.info(f"**Vérité terrain :** {verite}")

                st.markdown("---")
                if st.button("🎯 Analyser cette transaction",
                             use_container_width=True, type="primary"):
                    X = engineer_features(
                        tx['type'], tx['amount'],
                        tx['oldbalanceOrg'], tx['newbalanceOrig'],
                        tx['oldbalanceDest'], tx['newbalanceDest']
                    )

                    prob     = float(model.predict_proba(X)[0][1])
                    is_fraud = bool(model.predict(X)[0])
                    risk, _  = get_risk(prob)

                    save_prediction(tx['type'], tx['amount'], is_fraud, prob, risk)

                    st.markdown("---")
                    st.markdown("### 🎯 Résultat de l'analyse")

                    if is_fraud:
                        st.markdown(f"""
                        <div style="background:linear-gradient(90deg,#8B0000,#E24B4A);
                                    color:white; padding:2rem; border-radius:12px;">
                            <h2 style="color:white; margin:0;">🚨 FRAUDE DÉTECTÉE</h2>
                            <p style="font-size:1.2rem; margin-top:1rem;">
                                Probabilité : <b>{prob*100:.2f}%</b>
                            </p>
                            <p style="font-size:1.1rem;">
                                Risque : <b>{risk}</b>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success("## ✅ Transaction légitime")
                        st.markdown(f"**Probabilité de fraude :** {prob*100:.2f}%")
                        st.progress(prob)

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Risque", risk)
                    with c2:
                        st.metric("Probabilité", f"{prob*100:.2f}%")
                    with c3:
                        if 'isFraud' in tx.index:
                            verite = "🚨 OUI" if tx['isFraud'] == 1 else "✅ NON"
                            st.metric("Fraude réelle", verite)

                    if is_fraud:
                        st.markdown("---")
                        st.markdown("### 📬 Notification automatique")

                        cle = f"fraude_{int(datetime.now().timestamp())}_{int(tx['amount'])}"

                        if cle not in st.session_state:
                            st.session_state[cle] = True

                            with st.spinner("📤 Envoi automatique de l'alerte..."):
                                from utils.notifications import notifier_fraude

                                tx_info = {
                                    'id': int(datetime.now().timestamp()),
                                    'type': tx['type'],
                                    'amount': tx['amount'],
                                    'prob': prob,
                                    'risk': risk,
                                }
                                resultats = notifier_fraude(tx_info)

                            st.success("✅ Alerte envoyée AUTOMATIQUEMENT !")
                            st.caption("📧 Email envoyé au banquier")

                            with st.expander("📄 Voir le contenu de l'email"):
                                st.markdown("**📧 Email banquier :**")
                                st.code(resultats['email_banquier']['contenu'])

# ==============================================================
# PAGE 3 — ANALYSE BATCH CSV
# ==============================================================
elif page == "📁 Analyse batch CSV":
    st.title("📁 Analyse batch CSV")
    st.markdown("Uploadez un fichier CSV de transactions pour les analyser en masse.")
    st.markdown("---")

    st.markdown("**Format attendu :**")
    st.code("type,amount,oldbalanceOrg,newbalanceOrig,oldbalanceDest,newbalanceDest")

    uploaded_file = st.file_uploader("Choisir un fichier CSV", type=['csv'])

    if uploaded_file:
        df_upload = pd.read_csv(uploaded_file, nrows=5000)
        st.success(f"✅ {len(df_upload):,} transactions chargées (max 5000)")
        st.dataframe(df_upload.head())

        if st.button("🔍 Analyser toutes les transactions", use_container_width=True):
            with st.spinner("Analyse en cours..."):
                results = []
                for _, row in df_upload.iterrows():
                    X = engineer_features(
                        row.get('type', 'PAYMENT'),
                        row.get('amount', 0),
                        row.get('oldbalanceOrg', 0),
                        row.get('newbalanceOrig', 0),
                        row.get('oldbalanceDest', 0),
                        row.get('newbalanceDest', 0)
                    )
                    prob     = float(model.predict_proba(X)[0][1])
                    is_fraud = bool(model.predict(X)[0])
                    risk, _  = get_risk(prob)
                    results.append({
                        'type': row.get('type', ''),
                        'amount': row.get('amount', 0),
                        'is_fraud': '🚨 FRAUDE' if is_fraud else '✅ OK',
                        'probability': f"{prob*100:.2f}%",
                        'risk': risk
                    })

                df_results = pd.DataFrame(results)
                nb_frauds  = sum(1 for r in results if '🚨' in r['is_fraud'])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total analysé", len(results))
                with col2:
                    st.metric("Fraudes détectées", nb_frauds)
                with col3:
                    st.metric("Taux fraude", f"{nb_frauds/len(results)*100:.2f}%")

                st.dataframe(df_results, use_container_width=True)

                csv = df_results.to_csv(index=False)
                st.download_button(
                    "📥 Télécharger les résultats",
                    csv, "resultats_fraude.csv", "text/csv",
                    use_container_width=True
                )

# ==============================================================
# PAGE 4 — DASHBOARD
# ==============================================================
elif page == "📊 Dashboard":
    st.title("📊 Dashboard — Fraudes détectées")
    st.markdown("---")

    df_stats = get_stats()

    if df_stats.empty:
        st.warning("⚠️ Aucune transaction analysée — utilisez la page 'Analyser une transaction'")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total prédictions", len(df_stats))
        with col2:
            st.metric("Fraudes détectées", int(df_stats['is_fraud'].sum()))
        with col3:
            st.metric("Taux de fraude", f"{df_stats['is_fraud'].mean()*100:.2f}%")
        with col4:
            st.metric("Transactions sûres", int((df_stats['is_fraud']==0).sum()))

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Fraudes par type")
            fig, ax = plt.subplots(figsize=(6, 4))
            df_stats.groupby('transaction_type')['is_fraud'].sum().plot(
                kind='bar', ax=ax, color='#8B0000', alpha=0.85)
            ax.set_xlabel('')
            ax.tick_params(axis='x', rotation=30)
            st.pyplot(fig)

        with col2:
            st.markdown("### Distribution des risques")
            fig, ax = plt.subplots(figsize=(6, 4))
            df_stats['risk_score'].value_counts().plot(
                kind='pie', ax=ax, autopct='%1.1f%%',
                colors=['#1D9E75', '#EF9F27', '#E24B4A', '#8B0000'])
            ax.set_ylabel('')
            st.pyplot(fig)

        st.markdown("### Historique des transactions")
        df_hist = get_history()
        df_hist['Statut'] = df_hist['is_fraud'].apply(
            lambda x: '🚨 FRAUDE' if x == 1 else '✅ OK')
        st.dataframe(df_hist[['timestamp', 'transaction_type',
                              'amount', 'fraud_probability',
                              'risk_score', 'Statut']],
                     use_container_width=True)

# ==============================================================
# PAGE 5 — COMPARAISON MODÈLES
# ==============================================================
elif page == "🤖 Comparaison modèles":
    st.title("🤖 Comparaison des modèles")
    st.markdown("---")

    data = {
        'Modèle': ['Logistic Regression', 'Random Forest',
                   'Isolation Forest', 'ANN', 'Autoencoder'],
        'Type': ['ML supervisé', 'ML supervisé', 'ML non supervisé',
                 'Deep Learning', 'Deep Learning'],
        'Precision': [0.04, 0.90, 0.00, 0.70, 0.09],
        'Recall':    [0.93, 1.00, 0.00, 0.46, 0.72],
        'F1-Score':  [0.07, 0.94, 0.00, 0.55, 0.16],
        'AUC-ROC':   [0.983, 0.9998, 0.499, 0.937, 0.925],
    }
    df_comp = pd.DataFrame(data)

    st.dataframe(df_comp.style.highlight_max(
        subset=['Precision', 'Recall', 'F1-Score', 'AUC-ROC'],
        color='lightgreen'), use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### F1-Score par modèle")
        fig, ax = plt.subplots(figsize=(7, 4))
        colors = ['#378ADD', '#1D9E75', '#E24B4A', '#EF9F27', '#9333EA']
        ax.bar(df_comp['Modèle'], df_comp['F1-Score'], color=colors, alpha=0.85)
        ax.set_ylim(0, 1.1)
        ax.set_title('F1-Score')
        ax.tick_params(axis='x', rotation=20)
        for i, v in enumerate(df_comp['F1-Score']):
            ax.text(i, v + 0.01, f'{v:.2f}', ha='center', fontsize=10)
        st.pyplot(fig)

    with col2:
        st.markdown("### AUC-ROC par modèle")
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(df_comp['Modèle'], df_comp['AUC-ROC'], color=colors, alpha=0.85)
        ax.set_ylim(0, 1.1)
        ax.set_title('AUC-ROC')
        ax.tick_params(axis='x', rotation=20)
        for i, v in enumerate(df_comp['AUC-ROC']):
            ax.text(i, v + 0.01, f'{v:.3f}', ha='center', fontsize=10)
        st.pyplot(fig)

    st.markdown("---")
    st.success("🏆 **Meilleur modèle : Random Forest** — F1=0.94 · AUC=0.9998 · Recall=100%")

# ==============================================================
# PAGE 6 — NOTIFICATIONS
# ==============================================================
elif page == "📬 Notifications":
    st.title("📬 Historique des notifications")
    st.markdown("Alertes envoyées au banquier.")
    st.markdown("---")

    from utils.notifications import get_notifications, init_notifications_db

    init_notifications_db()
    df = get_notifications(limit=100)

    if df.empty:
        st.info("📭 Aucune notification envoyée pour le moment.")
        st.markdown("**Pour créer une notification :**")
        st.markdown("1. Allez dans **🔍 Analyser une transaction**")
        st.markdown("2. Saisissez une transaction suspecte")
        st.markdown("3. L'email sera envoyé automatiquement en cas de fraude")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📨 Total", len(df))
        with col2:
            st.metric("📧 Emails banquier",
                      int((df['destinataire_type'] == 'banquier').sum()))
        with col3:
            st.metric("✅ Traités",
                      int((df['statut'] != 'échec').sum()))

        st.markdown("---")
        st.dataframe(
            df[['timestamp', 'destinataire_type',
                'destinataire', 'canal', 'sujet', 'statut']],
            use_container_width=True
        )

        st.markdown("### 🔍 Détail")
        notif_id = st.selectbox("Choisir une notification", df['id'].tolist())
        notif = df[df['id'] == notif_id].iloc[0]
        st.markdown(f"**Destinataire :** {notif['destinataire']}")
        st.markdown(f"**Canal :** {notif['canal']}")
        st.markdown(f"**Date :** {notif['timestamp']}")
        st.markdown("**Message :**")
        st.code(notif['message'])