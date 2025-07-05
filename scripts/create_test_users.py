#!/usr/bin/env python3
"""
Script pour créer des utilisateurs de test pour le système d'authentification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.database import get_db, engine
from schemas import models
from passlib.context import CryptContext
from datetime import datetime

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    """Génère un hash du mot de passe"""
    return pwd_context.hash(password)

def create_test_users():
    """Crée des utilisateurs de test"""
    
    # Créer les tables si elles n'existent pas
    models.Base.metadata.create_all(bind=engine)
    
    # Obtenir une session de base de données
    db = next(get_db())
    
    # Liste des utilisateurs de test
    test_users = [
        {
            "first_name": "Admin",
            "last_name": "Système",
            "email": "admin@dengue.com",
            "username": "admin",
            "password": "Admin123!",
            "role": "admin"
        },
        {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "username": "jean.dupont",
            "password": "Password123!",
            "role": "user"
        },
        {
            "first_name": "Marie",
            "last_name": "Martin",
            "email": "marie.martin@example.com",
            "username": "marie.martin",
            "password": "Secure456!",
            "role": "user"
        },
        {
            "first_name": "Pierre",
            "last_name": "Durand",
            "email": "pierre.durand@example.com",
            "username": "pierre.durand",
            "password": "Test789!",
            "role": "user"
        }
    ]
    
    created_users = []
    existing_users = []
    
    for user_data in test_users:
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(models.User).filter(
            (models.User.email == user_data["email"]) | 
            (models.User.username == user_data["username"])
        ).first()
        
        if existing_user:
            existing_users.append(user_data["username"])
            print(f"⚠️  Utilisateur {user_data['username']} existe déjà")
            continue
        
        # Créer le nouvel utilisateur
        hashed_password = get_password_hash(user_data["password"])
        db_user = models.User(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=hashed_password,
            role=user_data["role"],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        created_users.append(user_data["username"])
        print(f"✅ Utilisateur {user_data['username']} créé avec succès")
    
    # Commiter les changements
    db.commit()
    db.close()
    
    # Afficher le résumé
    print("\n" + "="*50)
    print("RÉSUMÉ DE LA CRÉATION DES UTILISATEURS")
    print("="*50)
    
    if created_users:
        print(f"\n✅ Utilisateurs créés ({len(created_users)}):")
        for username in created_users:
            print(f"   - {username}")
    
    if existing_users:
        print(f"\n⚠️  Utilisateurs existants ({len(existing_users)}):")
        for username in existing_users:
            print(f"   - {username}")
    
    print("\n" + "="*50)
    print("INFORMATIONS DE CONNEXION")
    print("="*50)
    
    for user_data in test_users:
        if user_data["username"] in created_users:
            print(f"\n👤 {user_data['first_name']} {user_data['last_name']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Mot de passe: {user_data['password']}")
            print(f"   Rôle: {user_data['role']}")
    
    print("\n" + "="*50)
    print("NOTES IMPORTANTES")
    print("="*50)
    print("• Changez les mots de passe en production")
    print("• Supprimez ce script après utilisation")
    print("• Utilisez des mots de passe forts en production")
    print("• Activez l'authentification à deux facteurs si nécessaire")

if __name__ == "__main__":
    print("🔧 Création des utilisateurs de test...")
    print("="*50)
    
    try:
        create_test_users()
        print("\n✅ Script terminé avec succès!")
    except Exception as e:
        print(f"\n❌ Erreur lors de la création des utilisateurs: {str(e)}")
        sys.exit(1) 