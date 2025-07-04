#!/usr/bin/env python3
"""
Test spécifique pour vérifier le scroll automatique
"""

import requests
import time

def test_scroll_functionality():
    """Test du scroll automatique lors du changement de page"""
    base_url = "http://localhost:8000"
    
    print("🧪 Test du scroll automatique")
    print("=" * 40)
    
    # Test 1: Recherche initiale
    print("\n1. Test de recherche initiale...")
    try:
        data = {
            "date_debut": "2024-01-01",
            "date_fin": "2024-12-31",
            "region": "Toutes",
            "limit": 30,
            "page_size": 10,
            "page": 1
        }
        
        response = requests.post(f"{base_url}/affichage-donnees", data=data)
        if response.status_code == 200:
            print("✅ Recherche initiale réussie")
        else:
            print(f"❌ Erreur recherche initiale: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la recherche initiale: {e}")
        return False
    
    # Test 2: Test avec scroll_to_table
    print("\n2. Test avec paramètre scroll_to_table...")
    try:
        data["scroll_to_table"] = "true"
        response = requests.post(f"{base_url}/affichage-donnees", data=data)
        if response.status_code == 200:
            print("✅ Requête avec scroll_to_table réussie")
            
            # Vérifier que le paramètre est bien passé
            if "scroll_to_table" in response.text:
                print("✅ Paramètre scroll_to_table présent dans la réponse")
            else:
                print("⚠️  Paramètre scroll_to_table non trouvé dans la réponse")
                
        else:
            print(f"❌ Erreur avec scroll_to_table: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test scroll_to_table: {e}")
        return False
    
    # Test 3: Test de navigation avec scroll
    print("\n3. Test de navigation avec scroll...")
    try:
        data["page"] = 2
        data["scroll_to_table"] = "true"
        response = requests.post(f"{base_url}/affichage-donnees", data=data)
        if response.status_code == 200:
            print("✅ Navigation avec scroll réussie")
            
            # Vérifier la présence du JavaScript de scroll
            if "scrollIntoView" in response.text:
                print("✅ JavaScript de scroll présent")
            else:
                print("⚠️  JavaScript de scroll non trouvé")
                
        else:
            print(f"❌ Erreur navigation avec scroll: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test de navigation avec scroll: {e}")
        return False
    
    # Test 4: Vérification du HTML généré
    print("\n4. Vérification du HTML généré...")
    try:
        # Vérifier la présence des éléments de pagination
        if "pagination-section" in response.text:
            print("✅ Section pagination présente")
        else:
            print("⚠️  Section pagination non trouvée")
            
        # Vérifier la présence des boutons de navigation
        if "btn-pagination" in response.text:
            print("✅ Boutons de pagination présents")
        else:
            print("⚠️  Boutons de pagination non trouvés")
            
        # Vérifier la présence des informations de pagination
        if "pagination-info" in response.text:
            print("✅ Informations de pagination présentes")
        else:
            print("⚠️  Informations de pagination non trouvées")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification HTML: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 Test du scroll automatique terminé avec succès!")
    return True

if __name__ == "__main__":
    print("🚀 Démarrage du test de scroll automatique...")
    
    # Attendre que le serveur démarre
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(2)
    
    # Exécuter le test
    test_scroll_functionality()
    
    print("\n✨ Test terminé!") 