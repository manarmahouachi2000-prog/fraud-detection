"""
Système de notifications automatiques
- Email au banquier
- SMS au client
- Log dans la base SQLite
"""

import sqlite3
from datetime import datetime
import yagmail
import streamlit as st
import os     
# ══════════════════════════════════════════════════════════════
# CONFIGURATION EMAIL — REMPLACEZ CES 2 VALEURS !
# ══════════════════════════════════════════════════════════════
EMAIL_EXPEDITEUR   = "manarmahouachi2000@gmail.com"
EMAIL_MOT_DE_PASSE = "xefx ytir mzqo ahhy"

MODE_SIMULATION = False   # ← False = envoi RÉEL
import os
DB_PATH = "/tmp/fraude.db" if os.path.exists("/tmp") else "fraude.db"

# ══════════════════════════════════════════════════════════════
# BASE DE DONNÉES
# ══════════════════════════════════════════════════════════════
def init_notifications_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            destinataire_type TEXT,
            destinataire TEXT,
            canal TEXT,
            sujet TEXT,
            message TEXT,
            statut TEXT,
            transaction_id INTEGER
        )
    """)
    conn.commit()
    conn.close()


def log_notification(dest_type, dest, canal, sujet, message,
                     statut, transaction_id=None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO notifications
        (timestamp, destinataire_type, destinataire, canal,
         sujet, message, statut, transaction_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), dest_type, dest, canal,
          sujet, message, statut, transaction_id))
    conn.commit()
    conn.close()


def get_notifications(limit=100):
    import pandas as pd
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        f"SELECT * FROM notifications ORDER BY id DESC LIMIT {limit}",
        conn
    )
    conn.close()
    return df


# ══════════════════════════════════════════════════════════════
# TEMPLATES DES MESSAGES
# ══════════════════════════════════════════════════════════════
def template_email_banquier(tx):
    sujet = f"🚨 ALERTE FRAUDE - Transaction #{tx.get('id', 'N/A')}"
    corps = f"""
🚨 ALERTE FRAUDE DÉTECTÉE

Bonjour,

Le système de détection a identifié une transaction suspecte :

  ID Transaction    : {tx.get('id', 'N/A')}
  Date / Heure      : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
  Type              : {tx.get('type', 'N/A')}
  Montant           : {tx.get('amount', 0):,.2f} €
  Probabilité       : {tx.get('prob', 0)*100:.2f}%
  Niveau de risque  : {tx.get('risk', 'N/A')}

⚠️ ACTION REQUISE :
Veuillez vérifier cette transaction et contacter le client
dans les plus brefs délais.

---
Système automatique de détection de fraude
Random Forest · F1-Score : 0.94
    """
    return sujet, corps


def template_sms_client(tx):
    return (
        f"🚨 ALERTE BANQUE\n"
        f"Une transaction suspecte a été détectée sur votre compte.\n"
        f"Montant: {tx.get('amount', 0):,.2f} €\n"
        f"Type: {tx.get('type', 'N/A')}\n\n"
        f"⚠️ Contactez votre agence IMMÉDIATEMENT.\n"
        f"Si vous n'êtes pas à l'origine de cette transaction, "
        f"faites opposition sans délai."
    )


# ══════════════════════════════════════════════════════════════
# ENVOI (SIMULÉ)
# ══════════════════════════════════════════════════════════════
def envoyer_email(destinataire, sujet, corps):
    """Envoie un VRAI email via Gmail SMTP."""
    if MODE_SIMULATION:
        print(f"[SIMULATION] Email → {destinataire}")
        return True, "simulé"

    try:
        yag = yagmail.SMTP(EMAIL_EXPEDITEUR, EMAIL_MOT_DE_PASSE)
        yag.send(
            to=destinataire,
            subject=sujet,
            contents=corps.replace("\n", "<br>")
        )
        print(f"[EMAIL ENVOYÉ] → {destinataire}")
        return True, "envoyé"
    except Exception as e:
        print(f"❌ Erreur email : {e}")
        return False, f"échec: {str(e)[:50]}"

def envoyer_sms(numero, message):
    print(f"[SMS] → {numero}")
    return True, "simulé"


# ══════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ══════════════════════════════════════════════════════════════
def notifier_fraude(tx, email_banquier=None,
                    tel_client="+21600000000"):
    init_notifications_db()

    # Utilise automatiquement l'email configuré si aucun fourni
    if email_banquier is None:
        email_banquier = EMAIL_EXPEDITEUR

    resultats = {}

    # 1. Email banquier
    sujet, corps = template_email_banquier(tx)
    ok_email, statut_email = envoyer_email(email_banquier, sujet, corps)
    log_notification('banquier', email_banquier, 'email',
                     sujet, corps, statut_email, tx.get('id'))
    resultats['email_banquier'] = {
        'ok': ok_email, 'statut': statut_email,
        'destinataire': email_banquier, 'contenu': corps
    }

    # 2. SMS client
    msg_sms = template_sms_client(tx)
    ok_sms, statut_sms = envoyer_sms(tel_client, msg_sms)
    log_notification('client', tel_client, 'sms',
                     'Alerte fraude', msg_sms, statut_sms, tx.get('id'))
    resultats['sms_client'] = {
        'ok': ok_sms, 'statut': statut_sms,
        'destinataire': tel_client, 'contenu': msg_sms
    }

    return resultats