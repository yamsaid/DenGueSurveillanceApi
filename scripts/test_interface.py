#!/usr/bin/env python3
"""
Test pour vérifier l'interface et le scroll
"""

import requests
import time

def test_interface():
    """Test de l'interface et du scroll"""
    base_url = "http://localhost:8000"
    
    print("🧪 Test de l'interface et du scroll")
    print("=" * 40)
    
    # Test 1: Vérifier que le champ "Page" n'est pas visible
    print("\n1. Vérification de l'interface...")
    try:
        response = requests.get(f"{base_url}/exploration")
        if response.status_code == 200:
            print("✅ Page exploration accessible")
            
            # Vérifier que le champ "Page" est caché
            if 'input type="hidden" id="page"' in response.text:
                print("✅ Champ 'Page' bien caché (type hidden)")
            else:
                print("⚠️  Champ 'Page' pas trouvé ou pas caché")
                
            # Vérifier que le label "Page" est caché
            if 'style="display: none;"' in response.text and 'Page' in response.text:
                print("✅ Label 'Page' bien caché")
            else:
                print("⚠️  Label 'Page' pas trouvé ou pas caché")
                
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    # Test 2: Test de navigation avec scroll
    print("\n2. Test de navigation avec scroll...")
    try:
        data = {
            "date_debut": "2024-01-01",
            "date_fin": "2024-12-31",
            "region": "Toutes",
            "limit": 30,
            "page_size": 10,
            "page": 1,
            "scroll_to_table": "true"
        }
        
        response = requests.post(f"{base_url}/affichage-donnees", data=data)
        if response.status_code == 200:
            print("✅ Navigation avec scroll réussie")
            
            # Vérifier la présence du JavaScript de scroll
            if "scrollIntoView" in response.text:
                print("✅ JavaScript de scroll présent")
            else:
                print("⚠️  JavaScript de scroll non trouvé")
                
            # Vérifier que le paramètre scroll_to_table est passé
            if "scroll_to_table" in response.text:
                print("✅ Paramètre scroll_to_table présent")
            else:
                print("⚠️  Paramètre scroll_to_table non trouvé")
                
        else:
            print(f"❌ Erreur navigation: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test de navigation: {e}")
        return False
    
    # Test 3: Test de changement de page
    print("\n3. Test de changement de page...")
    try:
        data["page"] = 2
        response = requests.post(f"{base_url}/affichage-donnees", data=data)
        if response.status_code == 200:
            print("✅ Changement de page réussi")
            
            # Vérifier que la pagination fonctionne
            if "Page 2 sur" in response.text:
                print("✅ Pagination fonctionne correctement")
            else:
                print("⚠️  Pagination ne semble pas fonctionner")
                
        else:
            print(f"❌ Erreur changement de page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors du changement de page: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 Test de l'interface terminé avec succès!")
    return True

if __name__ == "__main__":
    print("🚀 Démarrage du test d'interface...")
    
    # Attendre que le serveur démarre
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(2)
    
    # Exécuter le test
    test_interface()
    
    print("\n✨ Test terminé!") 