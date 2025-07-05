#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur par défaut
Usage: python scripts/create_admin.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.database import SessionLocal, engine
from schemas import models
from passlib.context import CryptContext
from datetime import datetime

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    """Génère un hash du mot de passe"""
    return pwd_context.hash(password)

def create_admin_user():
    """Crée un utilisateur administrateur par défaut"""
    db = SessionLocal()
    
    try:
        # Vérifier si l'utilisateur admin existe déjà
        existing_admin = db.query(models.User).filter(
            models.User.username == "admin"
        ).first()
        
        if existing_admin:
            print("L'utilisateur administrateur existe déjà.")
            return
        
        # Créer l'utilisateur administrateur
        admin_user = models.User(
            username="admin",
            email="admin@dengue-surveillance.com",
            hashed_password=get_password_hash("admin123"),
            first_name="Administrateur",
            last_name="Système",
            role="admin",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Utilisateur administrateur créé avec succès!")
        print(f"   Username: admin")
        print(f"   Email: admin@dengue-surveillance.com")
        print(f"   Mot de passe: admin123")
        print("\n⚠️  IMPORTANT: Changez le mot de passe après la première connexion!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur administrateur: {e}")
        db.rollback()
    finally:
        db.close()

def create_test_users():
    """Crée quelques utilisateurs de test"""
    db = SessionLocal()
    
    try:
        # Utilisateur analyste
        analyst_user = models.User(
            username="analyste",
            email="analyste@dengue-surveillance.com",
            hashed_password=get_password_hash("analyste123"),
            first_name="Jean",
            last_name="Dupont",
            role="analyst",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Utilisateur standard
        user_standard = models.User(
            username="utilisateur",
            email="user@dengue-surveillance.com",
            hashed_password=get_password_hash("user123"),
            first_name="Marie",
            last_name="Martin",
            role="user",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add_all([analyst_user, user_standard])
        db.commit()
        
        print("✅ Utilisateurs de test créés avec succès!")
        print("   Analyste: analyste / analyste123")
        print("   Utilisateur: utilisateur / user123")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des utilisateurs de test: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Création des utilisateurs par défaut...")
    print("=" * 50)
    
    # Créer les tables si elles n'existent pas
    models.Base.metadata.create_all(bind=engine)
    
    # Créer l'administrateur
    create_admin_user()
    
    # Demander si on veut créer des utilisateurs de test
    response = input("\nVoulez-vous créer des utilisateurs de test? (y/n): ")
    if response.lower() in ['y', 'yes', 'o', 'oui']:
        create_test_users()
    
    print("\n✅ Configuration terminée!")
    print("Vous pouvez maintenant démarrer l'application avec: uvicorn main:app --reload") 