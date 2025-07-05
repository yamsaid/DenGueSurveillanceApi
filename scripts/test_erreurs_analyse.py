#!/usr/bin/env python3
"""
Test des endpoints d'analyse d'erreurs
"""

import requests
import json
import pandas as pd
from io import StringIO

# URL de base de l'API
BASE_URL = "http://localhost:8000"

def test_analyse_fichier():
    """Test d'analyse d'un fichier CSV avec des erreurs"""
    
    # Créer un fichier CSV de test avec des erreurs
    csv_data = """date_consultation,region,district,sexe,age,resultat_test,serotype,hospitalise,issue
2024-01-01,Centre,Bobo,homme,25,positif,denv2,oui,guéri
invalid_date,Centre,Bobo,femme,150,invalid_test,invalid_serotype,oui,invalid_issue
2024-01-03,Centre,Bobo,homme,abc,positif,denv3,non,en traitement
2024-01-04,Centre,Bobo,femme,30,négatif,denv2,non,guéri
"""
    
    # Créer un fichier temporaire
    with open("test_data.csv", "w") as f:
        f.write(csv_data)
    
    # Envoyer le fichier pour analyse
    with open("test_data.csv", "rb") as f:
        files = {"file": ("test_data.csv", f, "text/csv")}
        data = {"corriger": "true"}
        
        response = requests.post(f"{BASE_URL}/analyse", files=files, data=data)
        
        if response.status_code == 200:
            print("✅ Analyse du fichier réussie")
            return True
        else:
            print(f"❌ Erreur lors de l'analyse: {response.status_code}")
            return False

def test_endpoint_erreurs_analyse():
    """Test de l'endpoint /rapport/erreurs-analyse"""
    
    response = requests.get(f"{BASE_URL}/rapport/erreurs-analyse")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Endpoint erreurs-analyse accessible")
        print(f"📊 Résumé: {data.get('resume', {})}")
        return data
    else:
        print(f"❌ Erreur endpoint erreurs-analyse: {response.status_code}")
        return None

def test_endpoint_nb_erreurs_col():
    """Test de l'endpoint /rapport/nb-erreurs-col"""
    
    response = requests.get(f"{BASE_URL}/rapport/nb-erreurs-col")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Endpoint nb-erreurs-col accessible")
        print(f"📈 Colonnes avec erreurs: {data.get('labels', [])}")
        print(f"📊 Nombre d'erreurs: {data.get('data', [])}")
        return data
    else:
        print(f"❌ Erreur endpoint nb-erreurs-col: {response.status_code}")
        return None

def test_endpoint_erreurs_par_types():
    """Test de l'endpoint /rapport/erreurs-par-types"""
    
    response = requests.get(f"{BASE_URL}/rapport/erreurs-par-types")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Endpoint erreurs-par-types accessible")
        print(f"📊 Types d'erreurs: {data.get('labels', [])}")
        print(f"📈 Nombre par type: {data.get('data', [])}")
        return data
    else:
        print(f"❌ Erreur endpoint erreurs-par-types: {response.status_code}")
        return None

def test_rapport_complet():
    """Test du rapport complet d'analyse"""
    
    response = requests.get(f"{BASE_URL}/le-rapport")
    
    if response.status_code == 200:
        print("✅ Page de rapport accessible")
        return True
    else:
        print(f"❌ Erreur page rapport: {response.status_code}")
        return False

def main():
    """Fonction principale de test"""
    
    print("🧪 Tests des endpoints d'analyse d'erreurs")
    print("=" * 50)
    
    # Test 1: Analyser un fichier
    print("\n1. Test d'analyse de fichier...")
    if test_analyse_fichier():
        print("✅ Fichier analysé avec succès")
    else:
        print("❌ Échec de l'analyse du fichier")
        return
    
    # Test 2: Endpoint erreurs-analyse
    print("\n2. Test endpoint erreurs-analyse...")
    data_erreurs = test_endpoint_erreurs_analyse()
    
    # Test 3: Endpoint nb-erreurs-col
    print("\n3. Test endpoint nb-erreurs-col...")
    data_colonnes = test_endpoint_nb_erreurs_col()
    
    # Test 4: Endpoint erreurs-par-types
    print("\n4. Test endpoint erreurs-par-types...")
    data_types = test_endpoint_erreurs_par_types()
    
    # Test 5: Page de rapport
    print("\n5. Test page de rapport...")
    test_rapport_complet()
    
    # Affichage des résultats
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    if data_erreurs:
        print(f"✅ Endpoint erreurs-analyse: {data_erreurs.get('resume', {}).get('total_erreurs', 0)} erreurs détectées")
    
    if data_colonnes:
        print(f"✅ Endpoint nb-erreurs-col: {len(data_colonnes.get('labels', []))} colonnes avec erreurs")
    
    if data_types:
        print(f"✅ Endpoint erreurs-par-types: {len(data_types.get('labels', []))} types d'erreurs différents")
    
    print("\n🎉 Tests terminés!")

if __name__ == "__main__":
    main() 