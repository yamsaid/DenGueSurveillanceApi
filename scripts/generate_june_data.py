#!/usr/bin/env python3
"""
Script de génération de données aléatoires pour juillet 2025
Génère des données épidémiologiques de dengue pour la période du 1er au 6 juillet 2025
"""

import pandas as pd
import random
from faker import Faker
from datetime import datetime, date, timedelta
import os

# Initialisation
fake = Faker('fr_FR')
Faker.seed(42)  # Pour la reproductibilité
random.seed(42)

# Paramètres épidémiologiques réalistes
POSITIF_RATIO = 0.65  # 65% de tests positifs en période épidémique
FEMME_RATIO = 0.52    # 52% de femmes
HOSPITALISE_RATIO = 0.35  # 35% d'hospitalisations
DECES_RATIO = 0.02    # 2% de décès
SEROTYPES = ['DENV2', 'DENV3']

# Données par district avec cas pour juin 2024
DISTRICTS_DATA = [
    # Centre
    ("Centre", "DS Baskuy", 45, 1),
    ("Centre", "DS Bogodogo", 78, 2),
    ("Centre", "DS Boulmiougou", 62, 1),
    ("Centre", "DS Nongr-Massom", 38, 0),
    ("Centre", "DS Sig-Noghin", 55, 1),
    
    # Hauts Bassins
    ("Hauts Bassins", "DS Dafra", 42, 1),
    ("Hauts Bassins", "DS Dande", 28, 0),
    ("Hauts Bassins", "DS Do", 35, 1),
    ("Hauts Bassins", "DS Hounde", 31, 0),
    ("Hauts Bassins", "DS Karangasso Vigue", 15, 0),
    ("Hauts Bassins", "DS Léna", 12, 0),
    ("Hauts Bassins", "DS N'Dorola", 18, 0),
    ("Hauts Bassins", "DS Orodara", 22, 0),
]

def generate_july_data():
    """Génère des données pour juillet 2025 (1-6 juillet)"""
    all_data = []
    id_counter = 1
    
    # Période du 1er au 6 juillet 2025
    start_date = date(2025, 7, 1)
    end_date = date(2025, 7, 6)
    
    for region, district, n_cases, n_deaths in DISTRICTS_DATA:
        # Sélection aléatoire des cas qui décèdent
        deaths_set = set(random.sample(range(n_cases), n_deaths)) if n_deaths < n_cases else set()
        
        for i in range(n_cases):
            # Date aléatoire entre le 1er et 6 juillet 2025
            days_offset = random.randint(0, 5)  # 0-5 pour couvrir 6 jours (1-6 juillet)
            consultation_date = start_date + timedelta(days=days_offset)
            
            # Génération des données épidémiologiques
            sexe = "Femme" if random.random() < FEMME_RATIO else "Homme"
            hospitalise = "Oui" if random.random() < HOSPITALISE_RATIO else "Non"
            resultat_test = "Positif" if random.random() < POSITIF_RATIO else "Négatif"
            
            # Issue du cas
            if i in deaths_set:
                evolution = "Décédé"
            else:
                evolution = random.choice(["Guéri", "En traitement", "Inconnue"])
            
            # Âge réaliste (distribution normale centrée sur 25 ans)
            age = max(0, min(120, int(abs(random.gauss(25, 15)))))
            
            # Sérotype
            serotype = random.choice(SEROTYPES) if resultat_test == "Positif" else None
            
            # Création de l'enregistrement
            record = {
                
                "date_consultation": consultation_date,
                "region": region,
                "district": district,
                "sexe": sexe,
                "age": age,
                "resultat_test": resultat_test,
                "serotype": serotype,
                "hospitalise": hospitalise,
                "issue": evolution,
                "id_source": 1  # ID de soumission par défaut
            }
            
            all_data.append(record)
            id_counter += 1
    
    return pd.DataFrame(all_data)

def main():
    """Fonction principale"""
    print("🔄 Génération des données épidémiologiques pour juillet 2025 (1-6 juillet)...")
    
    # Génération des données
    df_cas = generate_july_data()
  
    
    # Répartition par région
   
    # Sauvegarde des données
    output_dir = "data_Juillet-2025-1-6"
    os.makedirs(output_dir, exist_ok=True)
    
    # Fichier principal des cas
    cas_file = f"{output_dir}/data_july_2025.csv"
    df_cas.to_csv(cas_file, index=False)
    
    

if __name__ == "__main__":
    df_cas, submission = main() 