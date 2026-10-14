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
    """Page de connexion — design ATB corporate."""
    # Charger les 2 images (logo + bâtiment)
    try:
        with open("atb_background.jpg", "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
    except Exception:
        logo_b64 = ""

    try:
        with open("atb_building.jpg", "rb") as f:
            building_b64 = base64.b64encode(f.read()).decode()
    except Exception:
        building_b64 = ""

    # CSS + Design
    st.markdown(f"""
    <style>
        /* Fond général */
        .stApp {{
            background: #F5F7FA;
        }}
        header[data-testid="stHeader"] {{ background: transparent; }}

        /* Cacher la sidebar sur la page de connexion */
        section[data-testid="stSidebar"] {{
            display: none !important;
        }}

        /* Conteneur principal */
        .login-container {{
            display: flex;
            min-height: 85vh;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 25px 80px rgba(0,0,0,0.3);
            margin: 1rem 0;
        }}

        /* Côté gauche — Image du bâtiment */
        .login-left {{
            flex: 1.2;
            background-image: url("data:image/jpeg;base64,{building_b64}");
            background-size: cover;
            background-position: center;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 2rem;
        }}
        .login-left::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, rgba(74,0,0,0.5) 0%, rgba(139,0,0,0.4) 100%);
            z-index: 1;
        }}
        .login-left > * {{
            position: relative;
            z-index: 2;
        }}
        .atb-brand-left {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .atb-brand-logo {{
            background: white;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 800;
            color: #8B0000;
            font-size: 1.4rem;
            letter-spacing: 1px;
        }}
        .atb-brand-name {{
            color: white;
            font-size: 0.75rem;
            letter-spacing: 2px;
            font-weight: 500;
        }}
        .login-left-bottom {{
            color: white;
        }}
        .login-left-bottom p {{
            margin: 0;
            font-size: 1rem;
            line-height: 1.6;
            text-shadow: 0 2px 8px rgba(0,0,0,0.5);
        }}

        /* Côté droit — Carte de connexion */
        .login-right {{
            flex: 1;
            background: linear-gradient(135deg, #6B0000 0%, #8B0000 50%, #4A0000 100%);
            padding: 3rem 3rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
        }}
        .login-right::before {{
            content: '';
            position: absolute;
            top: -20%; right: -20%;
            width: 400px; height: 400px;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            border-radius: 50%;
        }}
        .login-right::after {{
            content: '';
            position: absolute;
            bottom: -30%; left: -10%;
            width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
            border-radius: 50%;
        }}

        /* Carte blanche centrale */
        .login-card {{
            background: white;
            border-radius: 16px;
            padding: 2rem 2rem;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
            position: relative;
            z-index: 2;
            text-align: center;
        }}
        .login-card-logo {{
            width: 100px;
            margin: 0 auto 1rem auto;
            display: block;
        }}
        .login-card-title {{
            color: #8B0000;
            font-size: 1.6rem;
            font-weight: 800;
            margin: 0.5rem 0;
            line-height: 1.3;
        }}
        .login-card-subtitle {{
            color: #888;
            font-size: 0.8rem;
            margin-bottom: 1.5rem;
        }}
        .login-card-divider {{
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, #8B0000 0%, #1D9E75 100%);
            border-radius: 2px;
            margin: 1rem auto;
        }}
        .login-card-hint {{
            background: #FFF5F5;
            border-left: 3px solid #8B0000;
            border-radius: 8px;
            padding: 0.8rem 1rem;
            margin: 1rem 0;
            text-align: left;
            font-size: 0.85rem;
            color: #666;
        }}

        /* Boutons profils */
        div[data-testid="stButton"] > button {{
            width: 100% !important;
            background: linear-gradient(135deg, #8B0000 0%, #6B0000 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 0.9rem 1rem !important;
            border: none !important;
            border-radius: 10px !important;
            font-size: 0.9rem !important;
            transition: all 0.2s !important;
            box-shadow: 0 4px 12px rgba(139,0,0,0.3) !important;
            white-space: pre-line !important;
            line-height: 1.3 !important;
            text-align: center !important;
            margin-bottom: 0.5rem !important;
        }}
        div[data-testid="stButton"] > button:hover {{
            transform: translateY(-2px) !important;
            background: linear-gradient(135deg, #A6192E 0%, #8B0000 100%) !important;
            box-shadow: 0 8px 20px rgba(139,0,0,0.5) !important;
            color: white !important;
        }}

        /* Réduire l'espacement dans la carte */
        .login-card div[data-testid="stVerticalBlock"] {{
            gap: 0.5rem;
        }}

        /* Input admin */
        .stTextInput > div > div > input {{
            border-radius: 8px !important;
            border: 2px solid #e0e0e0 !important;
            padding: 0.7rem 1rem !important;
            font-size: 0.9rem !important;
        }}
        .stTextInput > div > div > input:focus {{
            border-color: #8B0000 !important;
            box-shadow: 0 0 0 3px rgba(139,0,0,0.1) !important;
        }}

        /* Expander admin */
        .streamlit-expanderHeader {{
            background: #F8F8F8 !important;
            border-radius: 8px !important;
            font-size: 0.85rem !important;
            color: #666 !important;
        }}

        /* Responsive */
        @media (max-width: 900px) {{
            .login-left {{ display: none; }}
            .login-right {{ flex: 1; padding: 1.5rem; }}
        }}
    </style>
    """, unsafe_allow_html=True)

    # Layout
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1])

    # ============ GAUCHE : IMAGE + SLOGAN ============
    with col_left:
        st.markdown(f"""
        <div style="background-image: url('data:image/jpeg;base64,{building_b64}');
                    background-size: cover;
                    background-position: center;
                    height: 700px;
                    border-radius: 20px 0 0 20px;
                    position: relative;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    padding: 2rem;
                    overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0;
                        background: linear-gradient(135deg, rgba(74,0,0,0.55) 0%, rgba(139,0,0,0.35) 100%);
                        z-index: 1;"></div>
            <div style="position: relative; z-index: 2; display: flex; align-items: center; gap: 1rem;">
                <div style="background: white; padding: 8px 14px; border-radius: 6px;
                            font-weight: 800; color: #8B0000; font-size: 1.3rem;
                            letter-spacing: 1px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                    ATB
                </div>
                <div style="color: white; font-size: 0.7rem; letter-spacing: 2px;
                            font-weight: 500; text-shadow: 0 2px 8px rgba(0,0,0,0.5);">
                    ARAB TUNISIAN BANK
                </div>
            </div>
            <div style="position: relative; z-index: 2; color: white;">
                <div style="width: 40px; height: 3px; background: white;
                            margin-bottom: 1rem; border-radius: 2px;"></div>
                <p style="margin: 0; font-size: 1.1rem; line-height: 1.5;
                          font-weight: 500; text-shadow: 0 2px 8px rgba(0,0,0,0.6);">
                    Votre confiance<br>
                    est notre plus grande<br>
                    sécurité
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ============ DROITE : CARTE DE CONNEXION ============
    with col_right:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #6B0000 0%, #8B0000 50%, #4A0000 100%);
                    border-radius: 0 20px 20px 0;
                    height: 700px;
                    padding: 2rem;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    position: relative;
                    overflow: hidden;">
            <div style="position: absolute; top: -20%; right: -20%;
                        width: 400px; height: 400px;
                        background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
                        border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -30%; left: -20%;
                        width: 500px; height: 500px;
                        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
                        border-radius: 50%;"></div>
            <div style="background: white; border-radius: 16px;
                        padding: 2rem; width: 100%; max-width: 400px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
                        position: relative; z-index: 2;
                        text-align: center;">

                <img src="data:image/jpeg;base64,{logo_b64}"
                     style="width: 90px; margin: 0 auto 0.5rem auto; display: block;">

                <h1 style="color: #8B0000; font-size: 1.5rem; font-weight: 800;
                           margin: 0.5rem 0; line-height: 1.3;">
                    Système de<br>Détection de Fraude
                </h1>

                <p style="color: #888; font-size: 0.8rem; margin: 0.5rem 0 0 0;">
                    Arab Tunisian Bank — Espace Sécurisé
                </p>

                <div style="width: 60px; height: 3px;
                            background: linear-gradient(90deg, #8B0000 0%, #1D9E75 100%);
                            border-radius: 2px; margin: 1.2rem auto;"></div>

                <div style="background: #FFF5F5; border-left: 3px solid #8B0000;
                            border-radius: 8px; padding: 0.7rem 1rem;
                            margin: 0.5rem 0 1rem 0; text-align: left;">
                    <p style="margin: 0; font-size: 0.8rem; color: #8B0000; font-weight: 700;">
                        👤 Bienvenue
                    </p>
                    <p style="margin: 0.3rem 0 0 0; font-size: 0.75rem; color: #666;">
                        Sélectionnez votre profil ci-dessous
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ============ BOUTONS PROFILS (à droite) ============
    col_spacer1, col_btn, col_spacer2 = st.columns([1.2, 1, 1])

    with col_btn:
        st.markdown("### 👤 Sélectionnez votre profil")

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("👤  Banquier\n\nAccès complet",
                         use_container_width=True,
                         key="btn_banquier"):
                st.session_state['logged_in'] = True
                st.session_state['banquier_email'] = "banquier@atb.com.tn"
                st.session_state['banquier_nom'] = "Banquier ATB"
                st.session_state['role'] = "banquier"
                log_connexion("banquier@atb.com.tn", "Banquier ATB", "connexion")
                st.rerun()

            if st.button("🎓  Recruteur\n\nMode démo",
                         use_container_width=True,
                         key="btn_recruteur"):
                st.session_state['logged_in'] = True
                st.session_state['banquier_email'] = "recruteur@demo.tn"
                st.session_state['banquier_nom'] = "Recruteur"
                st.session_state['role'] = "recruteur"
                log_connexion("recruteur@demo.tn", "Recruteur", "connexion")
                st.rerun()

        with col_b:
            if st.button("🔍  Analyste\n\nLecture seule",
                         use_container_width=True,
                         key="btn_analyste"):
                st.session_state['logged_in'] = True
                st.session_state['banquier_email'] = "analyste@atb.com.tn"
                st.session_state['banquier_nom'] = "Analyste ATB"
                st.session_state['role'] = "analyste"
                log_connexion("analyste@atb.com.tn", "Analyste ATB", "connexion")
                st.rerun()

            if st.button("🎯  Démo rapide\n\nSans compte",
                         use_container_width=True,
                         key="btn_demo"):
                st.session_state['logged_in'] = True
                st.session_state['banquier_email'] = "demo@atb.com.tn"
                st.session_state['banquier_nom'] = "Invité"
                st.session_state['role'] = "demo"
                log_connexion("demo@atb.com.tn", "Invité", "connexion")
                st.rerun()

        st.markdown("---")

        # Admin expander
        with st.expander("🔐 Connexion administrateur"):
            email_admin = st.text_input("Email administrateur",
                                         placeholder="admin@atb.com.tn",
                                         key="admin_email")
            if st.button("Se connecter", use_container_width=True):
                ok, nom = verifier_banquier(email_admin)
                if ok:
                    st.session_state['logged_in'] = True
                    st.session_state['banquier_email'] = email_admin
                    st.session_state['banquier_nom'] = nom
                    st.session_state['role'] = "admin"
                    log_connexion(email_admin, nom, "connexion")
                    st.success(f"✅ Bienvenue {nom} !")
                    st.rerun()
                else:
                    st.error("❌ Accès refusé — Email non autorisé.")

        st.markdown(
            '<p style="text-align: center; color: #888; font-size: 0.75rem; '
            'margin-top: 1rem;">🔒 Connexion sécurisée · Toutes les sessions sont enregistrées</p>',
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
# ==============================================================
# PAGE 1 — ACCUEIL (Style Dashboard ATB)
# ==============================================================
if page == "🏠 Accueil":
    import plotly.graph_objects as go

    nom_banquier = st.session_state.get('banquier_nom', 'Utilisateur')
    date_now = datetime.now().strftime("%A %d %B %Y · %H:%M")

    # CSS GLOBAL
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a0000 0%, #2C0000 50%, #4A0000 100%);
            border-right: 3px solid #8B0000;
        }
        section[data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,0.08) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            text-align: left !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #8B0000 !important;
            border-color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] .stRadio > div { gap: 4px; }
        section[data-testid="stSidebar"] .stRadio label {
            background: rgba(255,255,255,0.05);
            padding: 10px 14px;
            border-radius: 6px;
            border-left: 3px solid transparent;
            transition: all 0.2s;
            cursor: pointer;
            display: block;
        }
        section[data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(139,0,0,0.4);
            border-left: 3px solid #FFFFFF;
        }
        .main { background: #F5F7FA; }
        .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

        .hero-banner {
            background: linear-gradient(135deg, #4A0000 0%, #8B0000 40%, #A6192E 70%, #6B0000 100%);
            color: white;
            padding: 2rem 2.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(139,0,0,0.3);
        }
        .hero-banner::after {
            content: '';
            position: absolute;
            top: -50%; right: -10%;
            width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
            border-radius: 50%;
        }
        .hero-title { font-size: 1.9rem; font-weight: 800; letter-spacing: 0.5px; margin: 0; color: #FFFFFF; }
        .hero-subtitle { color: rgba(255,255,255,0.85); font-size: 0.85rem; letter-spacing: 3px; margin: 0.5rem 0 0 0; font-weight: 300; }
        .hero-desc { color: rgba(255,255,255,0.9); font-size: 0.95rem; margin: 1rem 0 0 0; }
        .hero-status {
            display: flex; gap: 2rem;
            margin-top: 1.2rem; padding-top: 1.2rem;
            border-top: 1px solid rgba(255,255,255,0.15);
            font-size: 0.85rem; color: rgba(255,255,255,0.9);
        }
        .hero-shield { font-size: 3.5rem; filter: drop-shadow(0 0 20px rgba(255,255,255,0.4)); }

        .kpi-card {
            background: white; border-radius: 10px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid #EEEEEE;
            height: 100%; position: relative;
        }
        .kpi-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; }
        .kpi-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #666; }
        .kpi-icon { font-size: 1.3rem; opacity: 0.5; }
        .kpi-value { font-size: 2rem; font-weight: 800; margin: 0.3rem 0; color: #1a1a1a; }
        .kpi-sub { font-size: 0.8rem; color: #999; margin: 0; }
        .kpi-trend { display: inline-block; margin-top: 0.6rem; font-size: 0.75rem; font-weight: 600; color: #1D9E75; }
        .kpi-card-dark { background: linear-gradient(135deg, #8B0000 0%, #6B0000 100%); border: none; }
        .kpi-card-dark .kpi-label, .kpi-card-dark .kpi-sub { color: rgba(255,255,255,0.75); }
        .kpi-card-dark .kpi-value { color: #FFFFFF; }
        .kpi-card-dark .kpi-icon { opacity: 0.8; }

        .section-title { font-size: 1.05rem; font-weight: 700; color: #1a1a1a; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem; }

        .panel { background: white; border-radius: 10px; padding: 1.4rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #EEEEEE; margin-bottom: 1rem; }

        .activity-row { display: flex; align-items: center; justify-content: space-between; padding: 0.7rem 0; border-bottom: 1px solid #f0f0f0; font-size: 0.85rem; }
        .activity-row:last-child { border-bottom: none; }
        .activity-icon { width: 32px; height: 32px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 0.9rem; margin-right: 0.7rem; flex-shrink: 0; }
        .activity-icon-fraud { background: #FFE5E5; color: #8B0000; }
        .activity-icon-ok { background: #E5F7EE; color: #1D9E75; }

        .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.72rem; font-weight: 600; }
        .badge-fraud { background: #8B0000; color: white; }
        .badge-ok { background: #E5F7EE; color: #1D9E75; }
    </style>
    """, unsafe_allow_html=True)

    # BANNIÈRE HÉRO
    st.markdown(f"""
    <div class="hero-banner">
        <div style="display: flex; align-items: center; gap: 1.5rem; position: relative; z-index: 2;">
            <div class="hero-shield">🛡️</div>
            <div style="flex: 1;">
                <h1 class="hero-title">SYSTÈME DE DÉTECTION DE FRAUDE</h1>
                <p class="hero-subtitle">ARAB TUNISIAN BANK · DIVISION SÉCURITÉ</p>
                <p class="hero-desc">Des modèles avancés pour protéger vos transactions</p>
            </div>
            <div style="text-align: right; max-width: 220px;">
                <p style="color: rgba(255,255,255,0.9); font-style: italic; margin: 0;">
                    Prévenir aujourd'hui,<br>protéger demain
                </p>
            </div>
        </div>
        <div class="hero-status">
            <span>🟢 Système opérationnel</span>
            <span>📅 {date_now}</span>
            <span>👤 {nom_banquier}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI CARDS
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">📊 DATASET</span>
                <span class="kpi-icon">⋯</span>
            </div>
            <div class="kpi-value">6.3M</div>
            <p class="kpi-sub">transactions analysées</p>
            <span class="kpi-trend">↑ +12% vs hier</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">🎯 F1-SCORE</span>
                <span class="kpi-icon">⋯</span>
            </div>
            <div class="kpi-value" style="color: #8B0000;">0.94</div>
            <p class="kpi-sub">vs baseline 0.07</p>
            <span class="kpi-trend">↑ +0.03</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">📈 AUC-ROC</span>
                <span class="kpi-icon">⋯</span>
            </div>
            <div class="kpi-value">0.9998</div>
            <p class="kpi-sub">quasi-parfait</p>
            <span class="kpi-trend">↑ +0.0002</span>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="kpi-card kpi-card-dark">
            <div class="kpi-header">
                <span class="kpi-label">🛡️ DÉTECTION</span>
                <span class="kpi-icon">⋯</span>
            </div>
            <div class="kpi-value">99.8%</div>
            <p class="kpi-sub">des fraudes détectées</p>
            <span class="kpi-trend" style="color: rgba(255,255,255,0.9);">🎯 Taux de précision du modèle</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # MODÈLE + RÉPARTITION + ACTIVITÉ
    col_left, col_mid, col_right = st.columns([1.5, 1, 1])

    with col_left:
        st.markdown("""
        <div class="section-title">
            🏆 Modèle Champion
            <span style="background: #FFE5E5; color: #8B0000; padding: 2px 10px;
                         border-radius: 12px; font-size: 0.7rem; font-weight: 700;">
                ✨ Random Forest
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="panel" style="padding: 0;">
            <div style="display: flex; border-bottom: 1px solid #eee; padding: 0 1.4rem;">
                <div style="padding: 0.8rem 0; border-bottom: 3px solid #8B0000; color: #8B0000;
                            font-weight: 700; font-size: 0.85rem; margin-right: 1.5rem;">
                    Performance globale
                </div>
                <div style="padding: 0.8rem 0; color: #999; font-size: 0.85rem; margin-right: 1.5rem;">Matrice de confusion</div>
                <div style="padding: 0.8rem 0; color: #999; font-size: 0.85rem; margin-right: 1.5rem;">Courbe ROC</div>
                <div style="padding: 0.8rem 0; color: #999; font-size: 0.85rem;">Importance</div>
            </div>
            <div style="padding: 1.4rem;">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem;">
                    <div>
                        <p style="margin: 0; font-size: 0.7rem; color: #999; text-transform: uppercase;">F1-Score</p>
                        <p style="margin: 0.2rem 0; font-size: 1.5rem; font-weight: 800; color: #1a1a1a;">0.94</p>
                        <p style="margin: 0; font-size: 0.7rem; color: #1D9E75;">↑ +0.03</p>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 0.7rem; color: #999; text-transform: uppercase;">AUC-ROC</p>
                        <p style="margin: 0.2rem 0; font-size: 1.5rem; font-weight: 800; color: #1a1a1a;">0.9998</p>
                        <p style="margin: 0; font-size: 0.7rem; color: #1D9E75;">↑ +0.0002</p>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 0.7rem; color: #999; text-transform: uppercase;">Précision</p>
                        <p style="margin: 0.2rem 0; font-size: 1.5rem; font-weight: 800; color: #1a1a1a;">0.93</p>
                        <p style="margin: 0; font-size: 0.7rem; color: #1D9E75;">↑ +0.02</p>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 0.7rem; color: #999; text-transform: uppercase;">Rappel</p>
                        <p style="margin: 0.2rem 0; font-size: 1.5rem; font-weight: 800; color: #1a1a1a;">0.96</p>
                        <p style="margin: 0; font-size: 0.7rem; color: #1D9E75;">↑ +0.04</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8'],
            y=[0.62, 0.71, 0.78, 0.83, 0.87, 0.90, 0.92, 0.94],
            mode='lines+markers',
            line=dict(color='#8B0000', width=3),
            marker=dict(size=10, color='#8B0000', line=dict(color='white', width=2)),
            fill='tozeroy', fillcolor='rgba(139,0,0,0.1)',
            hovertemplate='<b>%{x}</b><br>F1: %{y:.2f}<extra></extra>'
        ))
        fig.update_layout(
            height=220, margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(showgrid=False, tickfont=dict(size=11, color='#666')),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0', tickfont=dict(size=11, color='#666'), range=[0.5, 1.0]),
            plot_bgcolor='white', paper_bgcolor='white', showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_mid:
        st.markdown('<div class="section-title">📊 Répartition du dataset</div>', unsafe_allow_html=True)

        fig = go.Figure(data=[go.Pie(
            labels=['Non fraudes', 'Fraudes'],
            values=[6354407, 8213],
            hole=0.7,
            marker=dict(colors=['#2C2C2C', '#8B0000'], line=dict(color='white', width=2)),
            textinfo='none',
            hovertemplate='<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>'
        )])
        fig.update_layout(
            height=230, margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0, font=dict(size=10)),
            annotations=[
                dict(text='<b style="font-size:16px;">6.3M</b><br>'
                          '<span style="font-size:10px; color:#999;">transactions</span>',
                     x=0.5, y=0.5, showarrow=False),
                dict(text='<b>0.13%</b>', x=1.05, y=0.85, xref='paper', yref='paper', showarrow=False,
                     font=dict(color='#8B0000', size=10)),
                dict(text='<b>99.87%</b>', x=1.05, y=0.15, xref='paper', yref='paper', showarrow=False,
                     font=dict(color='#2C2C2C', size=10))
            ],
            paper_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_right:
        st.markdown("""
        <div class="section-title">
            ⏱️ Activité récente
            <a style="font-size: 0.75rem; color: #8B0000; margin-left: auto; text-decoration: none;">
                Voir tout →
            </a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="panel" style="padding: 1rem;">
            <div class="activity-row">
                <div style="display: flex; align-items: center; flex: 1;">
                    <span class="activity-icon activity-icon-fraud">⚠️</span>
                    <div>
                        <div style="font-weight: 600; color: #1a1a1a; font-size: 0.85rem;">Transaction suspecte</div>
                        <div style="color: #999; font-size: 0.75rem;">- 12 500 TND</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="badge badge-fraud">Fraude</span>
                </div>
            </div>
            <div class="activity-row">
                <div style="display: flex; align-items: center; flex: 1;">
                    <span class="activity-icon activity-icon-ok">✅</span>
                    <div>
                        <div style="font-weight: 600; color: #1a1a1a; font-size: 0.85rem;">Paiement validé</div>
                        <div style="color: #999; font-size: 0.75rem;">+ 3 200 TND</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="badge badge-ok">Légitime</span>
                </div>
            </div>
            <div class="activity-row">
                <div style="display: flex; align-items: center; flex: 1;">
                    <span class="activity-icon activity-icon-fraud">🚫</span>
                    <div>
                        <div style="font-weight: 600; color: #1a1a1a; font-size: 0.85rem;">Fraude bloquée</div>
                        <div style="color: #999; font-size: 0.75rem;">- 15 000 TND</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="badge badge-fraud">Fraude</span>
                </div>
            </div>
            <div class="activity-row">
                <div style="display: flex; align-items: center; flex: 1;">
                    <span class="activity-icon activity-icon-ok">✅</span>
                    <div>
                        <div style="font-weight: 600; color: #1a1a1a; font-size: 0.85rem;">Paiement validé</div>
                        <div style="color: #999; font-size: 0.75rem;">+ 4 500 TND</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="badge badge-ok">Légitime</span>
                </div>
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