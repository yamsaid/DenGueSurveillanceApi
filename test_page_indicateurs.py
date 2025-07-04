#!/usr/bin/env python3
"""
Script de test pour la page d'indicateurs
Vérifie que tous les endpoints nécessaires fonctionnent
"""

import requests
import json
from datetime import datetime, date

# Configuration
BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(endpoint, description):
    """Teste un endpoint et affiche le résultat"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            print(f"✅ {description}: OK")
            return True
        else:
            print(f"❌ {description}: Erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description}: Exception - {str(e)}")
        return False

def test_api_endpoint(endpoint, params=None, description=None):
    """Teste un endpoint API avec paramètres"""
    try:
        if params is None:
            params = {}
        
        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description or endpoint}: OK")
            print(f"   Données reçues: {len(data) if isinstance(data, list) else 'dict'}")
            return True
        else:
            print(f"❌ {description or endpoint}: Erreur {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
    except Exception as e:
        print(f"❌ {description or endpoint}: Exception - {str(e)}")
        return False

def main():
    print("🧪 Test de la page d'indicateurs")
    print("=" * 50)
    
    # Test des pages HTML
    print("\n📄 Test des pages HTML:")
    test_endpoint("/page-indicateurs", "Page indicateurs principale")
    test_endpoint("/dashboard/indicateurs-powerbi", "Page indicateurs PowerBI")
    
    # Test des endpoints API
    print("\n🔌 Test des endpoints API:")
    test_api_endpoint("/api/stats", description="Statistiques générales")
    test_api_endpoint("/api/regions", description="Liste des régions")
    test_api_endpoint("/api/districts", description="Liste des districts")
    
    # Test des endpoints de données avec paramètres
    print("\n📊 Test des endpoints de données:")
    current_year = date.today().year
    test_api_endpoint(
        "/api/data/hebdomadaires", 
        {"annee": current_year, "mois": 6, "region": "Toutes", "district": "Toutes"},
        "Données hebdomadaires"
    )
    test_api_endpoint(
        "/api/data/mensuels", 
        {"annee": current_year, "region": "Toutes", "district": "Toutes"},
        "Données mensuelles"
    )
    
    # Test des fichiers statiques
    print("\n📁 Test des fichiers statiques:")
    test_endpoint("/static/assets/css/page-indicateurs.css", "CSS de la page indicateurs")
    test_endpoint("/static/assets/js/page-indicateurs.js", "JavaScript de la page indicateurs")
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés!")

if __name__ == "__main__":
    main() 