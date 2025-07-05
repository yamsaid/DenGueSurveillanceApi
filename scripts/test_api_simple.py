#!/usr/bin/env python3
"""
Test simple de l'API d'analyse d'erreurs
"""

import requests
import json

# URL de base
BASE_URL = "http://localhost:8000"

def test_analyse_simple():
    """Test simple de l'analyse d'un fichier"""
    
    # Créer un fichier CSV de test
    csv_data = """date_consultation,region,district,sexe,age,resultat_test,serotype,hospitalise,issue
2024-01-01,Centre,Bobo,homme,25,positif,denv2,oui,guéri
invalid_date,Centre,Bobo,femme,150,invalid_test,invalid_serotype,oui,invalid_issue
2024-01-03,Centre,Bobo,homme,abc,positif,denv3,non,en traitement
2024-01-04,Centre,Bobo,femme,30,négatif,denv2,non,guéri
"""
    
    # Envoyer le fichier pour analyse
    files = {"file": ("test.csv", csv_data, "text/csv")}
    data = {"corriger": "true"}
    
    try:
        response = requests.post(f"{BASE_URL}/analyse", files=files, data=data)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Analyse réussie")
            return True
        else:
            print(f"❌ Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_endpoints():
    """Test des endpoints d'erreurs"""
    
    endpoints = [
        "/rapport/erreurs-analyse",
        "/rapport/nb-erreurs-col", 
        "/rapport/erreurs-par-types"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"\n📊 Test de {endpoint}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Réponse: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ Erreur: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception pour {endpoint}: {e}")

def main():
    """Fonction principale"""
    
    print("🧪 Test simple de l'API")
    print("=" * 30)
    
    # Test 1: Analyser un fichier
    print("\n1. Test d'analyse de fichier...")
    if test_analyse_simple():
        print("✅ Fichier analysé avec succès")
        
        # Test 2: Tester les endpoints
        print("\n2. Test des endpoints...")
        test_endpoints()
        
    else:
        print("❌ Échec de l'analyse")

if __name__ == "__main__":
    main() 