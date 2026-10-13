from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import joblib
import sqlite3
import os
from datetime import datetime

app = FastAPI(
    title="Système de Détection de Fraude",
    description="API REST pour la détection de fraude bancaire",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect("fraude.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            transaction_type TEXT,
            amount REAL,
            old_balance_orig REAL,
            new_balance_orig REAL,
            old_balance_dest REAL,
            new_balance_dest REAL,
            is_fraud INTEGER,
            fraud_probability REAL,
            risk_score TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()s

MODEL_PATH = r"C:\Users\mahouachi\OneDrive\Desktop\fraud detection\Models\random_forest_model.pkl"
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

class Transaction(BaseModel):
    type: str
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    step: Optional[int] = 1

    class Config:
        json_schema_extra = {
            "example": {
                "type": "TRANSFER",
                "amount": 181.00,
                "oldbalanceOrg": 181.00,
                "newbalanceOrig": 0.00,
                "oldbalanceDest": 0.00,
                "newbalanceDest": 0.00
            }
        }

TYPE_MAPPING = {
    'CASH_IN': 0, 'CASH_OUT': 1,
    'DEBIT': 2, 'PAYMENT': 3, 'TRANSFER': 4
}

def engineer_features(tx: Transaction):
    type_encoded = TYPE_MAPPING.get(tx.type.upper(), 0)
    return {
        'type_encoded': type_encoded,
        'amount': tx.amount,
        'oldbalanceOrg': tx.oldbalanceOrg,
        'newbalanceOrig': tx.newbalanceOrig,
        'oldbalanceDest': tx.oldbalanceDest,
        'newbalanceDest': tx.newbalanceDest,
        'errorBalanceOrig': tx.newbalanceOrig + tx.amount - tx.oldbalanceOrg,
        'errorBalanceDest': tx.oldbalanceDest + tx.amount - tx.newbalanceDest,
        'isZeroOrig': 1 if tx.oldbalanceOrg == 0 else 0,
        'isZeroDest': 1 if tx.newbalanceDest == 0 else 0,
        'amountRatio': tx.amount / (tx.oldbalanceOrg + 1),
        'nb_tx_step': 100,
        'is_large_tx': 0,
    }

def get_risk_score(prob: float) -> str:
    if prob < 0.3:  return "FAIBLE"
    if prob < 0.6:  return "MODÉRÉ"
    if prob < 0.85: return "ÉLEVÉ"
    return "CRITIQUE"

def save_to_db(tx, result):
    conn = sqlite3.connect("fraude.db")
    conn.execute("""
        INSERT INTO predictions
        (timestamp, transaction_type, amount, old_balance_orig,
         new_balance_orig, old_balance_dest, new_balance_dest,
         is_fraud, fraud_probability, risk_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(), tx.type, tx.amount,
        tx.oldbalanceOrg, tx.newbalanceOrig,
        tx.oldbalanceDest, tx.newbalanceDest,
        int(result['is_fraud']), result['fraud_probability'],
        result['risk_score']
    ))
    conn.commit()
    conn.close()

@app.get("/", tags=["Général"])
def root():
    return {
        "message": "API Détection de Fraude",
        "docs": "http://127.0.0.1:8000/docs"
    }

@app.post("/predict", tags=["Prédiction"])
def predict(transaction: Transaction):
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    features = engineer_features(transaction)
    X = pd.DataFrame([features])
    prob = float(model.predict_proba(X)[0][1])
    is_fraud = bool(model.predict(X)[0])
    risk = get_risk_score(prob)
    decisions = {
        "FAIBLE":   "✅ Transaction approuvée",
        "MODÉRÉ":   "⚠️  Surveillance recommandée",
        "ÉLEVÉ":    "🔴 Vérification manuelle requise",
        "CRITIQUE": "🚨 ALERTE FRAUDE — Transaction bloquée"
    }
    result = {
        "is_fraud": is_fraud,
        "fraud_probability": round(prob, 4),
        "risk_score": risk,
        "decision": decisions[risk]
    }
    save_to_db(transaction, result)
    return result

@app.get("/stats", tags=["Statistiques"])
def get_stats():
    conn = sqlite3.connect("fraude.db")
    df = pd.read_sql("SELECT * FROM predictions", conn)
    conn.close()
    if df.empty:
        return {"message": "Aucune prédiction enregistrée"}
    return {
        "total_predictions": len(df),
        "total_frauds": int(df['is_fraud'].sum()),
        "fraud_rate_pct": round(df['is_fraud'].mean() * 100, 2),
        "risk_distribution": df['risk_score'].value_counts().to_dict(),
    }

@app.get("/history", tags=["Historique"])
def get_history(limit: int = 20, fraud_only: bool = False):
    conn = sqlite3.connect("fraude.db")
    query = "SELECT * FROM predictions"
    if fraud_only:
        query += " WHERE is_fraud = 1"
    query += f" ORDER BY id DESC LIMIT {limit}"
    df = pd.read_sql(query, conn)
    conn.close()
    return {"count": len(df), "transactions": df.to_dict(orient='records')}

@app.delete("/history", tags=["Historique"])
def clear_history():
    conn = sqlite3.connect("fraude.db")
    conn.execute("DELETE FROM predictions")
    conn.commit()
    conn.close()
    return {"message": "Historique supprimé"}