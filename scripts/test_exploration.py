#!/usr/bin/env python3
"""
Script de test pour vérifier l'endpoint d'exploration
"""

import requests
import sys

def test_exploration_page():
    """Test de la page d'exploration"""
    try:
        # Test de la page GET
        response = requests.get("http://localhost:8000/exploration")
        print(f"Status GET /exploration: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Page d'exploration accessible")
            return True
        else:
            print(f"❌ Erreur: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur. Assurez-vous que l'application est démarrée.")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_search_form():
    """Test du formulaire de recherche"""
    try:
        # Test POST avec des données de test
        data = {
            "date_debut": "2024-01-01",
            "date_fin": "2024-12-31", 
            "region": "Toutes",
            "limit": 100,
            "page_size": 25,
            "page": 1
        }
        
        response = requests.post("http://localhost:8000/affichage-donnees", data=data)
        print(f"Status POST /affichage-donnees: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Formulaire de recherche fonctionne")
            return True
        else:
            print(f"❌ Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test du formulaire: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test de la page d'exploration...")
    
    # Test de la page
    if test_exploration_page():
        # Test du formulaire
        test_search_form()
    else:
        print("❌ Impossible de tester le formulaire car la page n'est pas accessible")
        sys.exit(1) 