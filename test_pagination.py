#!/usr/bin/env python3
"""
Script de test pour la pagination de la page exploration
"""

import requests
import time

def test_pagination():
    """Test de la pagination sur la page exploration"""
    base_url = "http://localhost:8000"
    
    print("🧪 Test de la pagination - Page Exploration")
    print("=" * 50)
    
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
            "limit": 100,
            "page_size": 25,
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
    
    # Test 3: Test de navigation entre pages
    print("\n3. Test de navigation entre pages...")
    try:
        # Page 2
        data["page"] = 2
        response = requests.post(f"{base_url}/affichage-donnees", data=data)
        if response.status_code == 200:
            print("✅ Navigation vers la page 2 réussie")
        else:
            print(f"❌ Erreur navigation page 2: {response.status_code}")
            
        # Page 3 avec page_size différent
        data["page"] = 3
        data["page_size"] = 10
        response = requests.post(f"{base_url}/affichage-donnees", data=data)
        if response.status_code == 200:
            print("✅ Navigation vers la page 3 avec page_size=10 réussie")
        else:
            print(f"❌ Erreur navigation page 3: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test de navigation: {e}")
        return False
    
    # Test 4: Test des paramètres de pagination
    print("\n4. Test des paramètres de pagination...")
    try:
        # Test avec différentes tailles de page
        page_sizes = [10, 25, 50, 100]
        for size in page_sizes:
            data["page_size"] = size
            data["page"] = 1
            response = requests.post(f"{base_url}/affichage-donnees", data=data)
            if response.status_code == 200:
                print(f"✅ Page size {size} fonctionne")
            else:
                print(f"❌ Erreur avec page_size {size}")
                
    except Exception as e:
        print(f"❌ Erreur lors du test des paramètres: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Tests de pagination terminés avec succès!")
    return True

def test_export_with_pagination():
    """Test des exports avec pagination"""
    print("\n🧪 Test des exports avec pagination")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test export JSON avec pagination
        params = {
            "format": "json",
            "date_debut": "2024-01-01",
            "date_fin": "2024-12-31",
            "region": "Toutes",
            "limit": 100,
            "page_size": 25,
            "page": 1
        }
        
        response = requests.get(f"{base_url}/export-data", params=params)
        if response.status_code == 200:
            print("✅ Export JSON avec pagination fonctionne")
        else:
            print(f"❌ Erreur export JSON: {response.status_code}")
            
        # Test export CSV avec pagination
        params["format"] = "csv"
        response = requests.get(f"{base_url}/export-data", params=params)
        if response.status_code == 200:
            print("✅ Export CSV avec pagination fonctionne")
        else:
            print(f"❌ Erreur export CSV: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test des exports: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Démarrage des tests de pagination...")
    
    # Attendre que le serveur démarre
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(3)
    
    # Exécuter les tests
    success = test_pagination()
    if success:
        test_export_with_pagination()
    
    print("\n✨ Tests terminés!") 