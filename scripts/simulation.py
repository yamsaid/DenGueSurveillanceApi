"""
import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('fr_FR')

# Paramètres actualisés
districts_data = {
    'DS Baskuy': {'cas': 6663, 'deces': 111},
    'DS Bogodogo': {'cas': 29436, 'deces': 59},
    'DS Boulmiougou': {'cas': 21183, 'deces': 110},
    'DS Nongr-Massom': {'cas': 13228, 'deces': 23},
}

# Nouveaux paramètres
proportion_positifs = 0.5172
proportion_femmes = 0.5076
variants = ['DENV2', 'DENV3']

# Simulation des données
def simuler_donnees_district(district, infos, id_start=1):
    nb_cas = infos['cas']
    nb_deces = infos['deces']
    data = []
    base_date = datetime(2024, 1, 1)

    for i in range(nb_cas):
        evolution = 'Décédé' if i < nb_deces else random.choice(['Guéri', 'En traitement'])
        resultat_test = 'Positif' if random.random() < proportion_positifs else 'Négatif'
        sexe = 'Femme' if random.random() < proportion_femmes else 'Homme'

        data.append({
            'id_cas': id_start + i,
            'date_notification': base_date + timedelta(days=random.randint(0, 180)),
            'region': 'Centre',
            'district': district,
            'sexe': sexe,
            'age': max(0, int(random.gauss(25, 15))),
            'statut': random.choice(['Suspecté', 'Probable']),
            'serotype': random.choice(variants),
            'resultat_test': resultat_test,
            'evolution': evolution,
        })
    return pd.DataFrame(data)

# Génération des données pour chaque district
all_dfs = []
id_counter = 1
for district, infos in districts_data.items():
    df_district = simuler_donnees_district(district, infos, id_counter)
    all_dfs.append(df_district)
    id_counter += infos['cas']

df_final = pd.concat(all_dfs, ignore_index=True)

# Sauvegarde
df_final.to_csv("csv/donnees_dengue.csv", index=False)
print("✅ Données enrichies enregistrées dans 'donnees_dengue_centre_completes.csv'")




CREATE TABLE cas_dengue_centre (
    id_cas SERIAL PRIMARY KEY,
    date_notification DATE NOT NULL,
    region VARCHAR(50) DEFAULT 'Centre',
    district VARCHAR(100) NOT NULL,
    sexe VARCHAR(10) CHECK (sexe IN ('Homme', 'Femme')),
    age INTEGER CHECK (age >= 0),
    statut VARCHAR(20) CHECK (statut IN ('Suspecté', 'Probable')),
    serotype VARCHAR(10) CHECK (serotype IN ('DENV2', 'DENV3')),
    resultat_test VARCHAR(10) CHECK (resultat_test IN ('Positif', 'Négatif')),
    evolution VARCHAR(20) CHECK (evolution IN ('Guéri', 'En traitement', 'Décédé'))
);
"""



"================================================================="

import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('fr_FR')
Faker.seed(42)
random.seed(42)

# Paramètres globaux
positif_ratio = 0.5172
femme_ratio = 0.5076
hospitalise_ratio = 0.2816
serotypes = ['DENV2', 'DENV3']
mois_peak = [9, 10]  # Septembre et Octobre

# Données par district
districts_data = [
    ("Centre", "DS Baskuy", 6663, 111),
    ("Centre", "DS Bogodogo", 29436, 59),
    ("Centre", "DS Boulmiougou", 21183, 110),
    ("Centre", "DS Nongr-Massom", 13228, 23),
    ("Centre", "DS Sig-Noghin", 20571, 8),
    ("Hauts Bassins", "DS Dafra", 14565, 14),
    ("Hauts Bassins", "DS Dande", 294, 2),
    ("Hauts Bassins", "DS Do", 20998, 219),
    ("Hauts Bassins", "DS Hounde", 3927, 6),
    ("Hauts Bassins", "DS Karangasso Vigue", 140, 0),
    ("Hauts Bassins", "DS Léna", 65, 0),
    ("Hauts Bassins", "DS N'Dorola", 64, 0),
    ("Hauts Bassins", "DS Orodara", 360, 0),
]

# Simulation des données
all_data = []
id_counter = 1
base_year = 2023

for region, district, n_cases, n_deaths in districts_data:
    deaths_set = set(random.sample(range(n_cases), n_deaths)) if n_deaths < n_cases else set()
    for i in range(n_cases):
        mois = random.choices(range(1, 13), weights=[3 if m in mois_peak else 1 for m in range(1, 13)])[0]
        jour = random.randint(1, 28)  # Pour éviter les erreurs de date
        date_notification = datetime(base_year, mois, jour)

        sexe = "Femme" if random.random() < femme_ratio else "Homme"
        hospitalise = "Oui" if random.random() < hospitalise_ratio else "Non"
        resultat_test = "Positif" if random.random() < positif_ratio else "Négatif"
        evolution = "Décédé" if i in deaths_set else random.choice(["Guéri", "En traitement","Inconnue"])

        all_data.append({
            "idCas": id_counter,
            "date_consultation": date_notification.date(),
            "region": region,
            "district": district,
            "sexe": sexe,
            "age": int(abs(random.gauss(25, 15))),
            "resultat_test": resultat_test,
            "serotype": random.choice(serotypes),
            "hospitalise": hospitalise,
            "issue": evolution
        })
        id_counter += 1

df_simule = pd.DataFrame(all_data)
csv_path = "csv/data_simulate.csv"
df_simule.to_csv(csv_path, index=False)

print(f"✅ Données simulées enregistrées dans '{csv_path}'")
print("Données simulées :")