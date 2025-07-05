#!/usr/bin/env python3
"""
Script de test pour le système d'authentification
Usage: python test_auth.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test de l'inscription d'un utilisateur"""
    print("🔧 Test d'inscription...")
    
    data = {
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!",
        "role": "user",
        "terms": True,
        "newsletter": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", data=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Inscription réussie!")
            return True
        else:
            print(f"❌ Erreur d'inscription: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_login():
    """Test de connexion"""
    print("\n🔐 Test de connexion...")
    
    data = {
        "email": "admin@dengue-surveillance.com",
        "password": "admin123",
        "remember": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", data=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Connexion réussie!")
            print(f"Token: {result['access_token'][:50]}...")
            print(f"Utilisateur: {result['user']['username']}")
            return result['access_token']
        else:
            print(f"❌ Erreur de connexion: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_profile(token):
    """Test de récupération du profil"""
    print("\n👤 Test de récupération du profil...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/profile", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.json()
            print("✅ Profil récupéré avec succès!")
            print(f"Nom: {profile['first_name']} {profile['last_name']}")
            print(f"Email: {profile['email']}")
            print(f"Rôle: {profile['role']}")
            return True
        else:
            print(f"❌ Erreur de récupération du profil: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_logout(token):
    """Test de déconnexion"""
    print("\n🚪 Test de déconnexion...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/logout", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Déconnexion réussie!")
            return True
        else:
            print(f"❌ Erreur de déconnexion: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_pages():
    """Test des pages web"""
    print("\n🌐 Test des pages web...")
    
    pages = [
        ("/login", "Page de connexion"),
        ("/register", "Page d'inscription"),
        ("/", "Page d'accueil")
    ]
    
    for page, description in pages:
        try:
            response = requests.get(f"{BASE_URL}{page}")
            print(f"{description}: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur pour {description}: {e}")

def main():
    """Fonction principale de test"""
    print("🧪 Tests du système d'authentification")
    print("=" * 50)
    
    # Test des pages web
    test_pages()
    
    # Test de connexion
    token = test_login()
    
    if token:
        # Test du profil
        test_profile(token)
        
        # Test de déconnexion
        test_logout(token)
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    main() 