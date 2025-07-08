#!/usr/bin/env python3
"""
Exemple d'utilisation de la fonction resume_display avec graphiques

Ce script montre comment utiliser la fonction resume_display pour générer
un résumé statistique complet avec des graphiques descriptifs.
"""

import sys
import os

# Ajouter le chemin du package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dengsurvab import AppiClient

def main():
    """Exemple principal d'utilisation de resume_display avec graphiques"""
    
    # Configuration du client
    client = AppiClient("https://api-bf-dengue-survey-production.up.railway.app/")
    
    print("📊 EXEMPLE D'UTILISATION - RÉSUMÉ AVEC GRAPHIQUES")
    print("=" * 60)
    
    # Authentification
    print("1. Authentification...")
    auth_result = client.authenticate("admin@gmail.com", "admin123")
    
    if not auth_result.get('success'):
        print("❌ Échec de l'authentification")
        return
    
    print("✅ Authentification réussie")
    
    # Exemple 1: Résumé complet avec graphiques
    print("\n2. Résumé complet avec graphiques...")
    print("   Paramètres: verbose=True, show_details=True, graph=True")
    
    try:
        client.resume_display(
            verbose=True,      # Afficher tous les détails
            show_details=True, # Statistiques détaillées
            graph=True        # Afficher les graphiques
        )
        print("✅ Résumé avec graphiques généré avec succès")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Exemple 2: Résumé simplifié sans graphiques
    print("\n3. Résumé simplifié sans graphiques...")
    print("   Paramètres: verbose=False, show_details=False, graph=False")
    
    try:
        client.resume_display(
            verbose=False,     # Affichage simplifié
            show_details=False, # Pas de détails
            graph=False       # Pas de graphiques
        )
        print("✅ Résumé simplifié généré avec succès")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Exemple 3: Résumé avec graphiques mais sans détails
    print("\n4. Résumé avec graphiques mais sans détails...")
    print("   Paramètres: verbose=False, show_details=False, graph=True")
    
    try:
        client.resume_display(
            verbose=False,     # Affichage simplifié
            show_details=False, # Pas de détails
            graph=True        # Afficher les graphiques
        )
        print("✅ Résumé avec graphiques (simplifié) généré avec succès")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Déconnexion
    print("\n5. Déconnexion...")
    client.logout()
    print("✅ Déconnexion réussie")

def example_api_usage():
    """Exemple d'utilisation via l'API"""
    
    import requests
    
    print("\n🌐 EXEMPLE D'UTILISATION VIA L'API")
    print("=" * 40)
    
    # URL de l'API
    base_url = "https://api-bf-dengue-survey-production.up.railway.app"
    
    # Endpoint pour le résumé avec graphiques
    url = f"{base_url}/api/resume/display"
    
    # Paramètres
    params = {
        "verbose": True,
        "show_details": True,
        "graph": True
    }
    
    print(f"URL: {url}")
    print(f"Paramètres: {params}")
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Requête API réussie")
            print(f"Succès: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            
            # Afficher le contenu formaté
            if data.get('display'):
                print("\n📋 CONTENU FORMATÉ:")
                print("-" * 40)
                print(data['display'])
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    # Exemple principal
    main()
    
    # Exemple API
    example_api_usage()
    
    print("\n🎉 Exemples terminés !") 