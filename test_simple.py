#!/usr/bin/env python3
"""
Test simple pour vérifier la pagination
"""

import requests
import time

def test_simple():
    """Test simple de la pagination"""
    base_url = "http://localhost:8000"
    
    print("🧪 Test simple de la pagination")
    print("=" * 40)
    
    # Test 1: Accès à la page exploration
    print("\n1. Test d'accès à la page exploration...")
    try:
        response = requests.get(f"{base_url}/exploration")
        if response.status_code == 200:
            print("✅ Page exploration accessible")
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    # Test 2: Recherche avec pagination
    print("\n2. Test de recherche avec pagination...")
    try:
        data = {
            "date_debut": "2024-01-01",
            "date_fin": "2024-12-31",
            "region": "Toutes",
            "limit": 50,
            "page_size": 10,
            "page": 1
        }
        
        response = requests.post(f"{base_url}/affichage-donnees", data=data)
        if response.status_code == 200:
            print("✅ Recherche avec pagination réussie")
            
            # Vérifier la présence des éléments de pagination
            if "pagination" in response.text:
                print("✅ Éléments de pagination présents")
            else:
                print("⚠️  Éléments de pagination non trouvés")
                
        else:
            print(f"❌ Erreur lors de la recherche: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de recherche: {e}")
        return False
    
    # Test 3: Test de navigation vers la page 2
    print("\n3. Test de navigation vers la page 2...")
    try:
        data["page"] = 2
        response = requests.post(f"{base_url}/affichage-donnees", data=data)
        if response.status_code == 200:
            print("✅ Navigation vers la page 2 réussie")
        else:
            print(f"❌ Erreur navigation page 2: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test de navigation: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 Test simple terminé avec succès!")
    return True

if __name__ == "__main__":
    print("🚀 Démarrage du test simple...")
    
    # Attendre que le serveur démarre
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(2)
    
    # Exécuter le test
    test_simple()
    
    print("\n✨ Test terminé!") 