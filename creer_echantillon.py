"""
Script a lancer UNE SEULE FOIS sur votre PC.
Extrait 10 000 lignes du dataset PaySim (en gardant toutes les fraudes).
"""
import pandas as pd
import os

CSV_SOURCE = "data/PS_20174392719_1491204439457_log.csv"
CSV_CIBLE = "data/paysim_sample.csv"

print(f"Lecture de {CSV_SOURCE}...")
df = pd.read_csv(CSV_SOURCE)
print(f"OK : {len(df):,} lignes chargees")

fraudes = df[df['isFraud'] == 1]
print(f"{len(fraudes):,} fraudes trouvees dans le dataset complet")

n_normales = 10000 - len(fraudes)
normales = df[df['isFraud'] == 0].sample(n=n_normales, random_state=42)

echantillon = pd.concat([fraudes, normales]).sample(frac=1, random_state=42)
echantillon.to_csv(CSV_CIBLE, index=False)

taille_mo = os.path.getsize(CSV_CIBLE) / 1024 / 1024
print(f"\nEchantillon cree : {CSV_CIBLE}")
print(f"   Lignes  : {len(echantillon):,}")
print(f"   Fraudes : {len(fraudes):,} ({len(fraudes)/len(echantillon)*100:.2f}%)")
print(f"   Taille  : {taille_mo:.2f} Mo")