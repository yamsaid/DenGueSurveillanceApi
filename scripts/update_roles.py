#!/usr/bin/env python3
"""
Script pour mettre à jour les rôles des utilisateurs existants
Usage: python scripts/update_roles.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.database import SessionLocal, engine
from schemas import models
from datetime import datetime

def update_user_roles():
    """Met à jour les rôles des utilisateurs existants"""
    db = SessionLocal()
    
    try:
        # Créer les tables si elles n'existent pas
        models.Base.metadata.create_all(bind=engine)
        
        print("🔧 Mise à jour des rôles utilisateurs...")
        print("=" * 50)
        
        # Mettre à jour les utilisateurs existants
        users_to_update = [
            {
                "email": "admin@dengue-surveillance.com",
                "role": "admin",
                "description": "Administrateur principal"
            },
            {
                "email": "jean.dupont@example.com",
                "role": "analyst",
                "description": "Analyste de données"
            },
            {
                "email": "marie.martin@example.com",
                "role": "authority",
                "description": "Autorité sanitaire"
            },
            {
                "email": "pierre.durand@example.com",
                "role": "user",
                "description": "Utilisateur standard"
            }
        ]
        
        updated_count = 0
        for user_data in users_to_update:
            user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
            
            if user:
                old_role = user.role
                user.role = user_data["role"]
                user.updated_at = datetime.utcnow()
                
                print(f"✅ {user_data['description']}: {old_role} → {user_data['role']}")
                updated_count += 1
            else:
                print(f"⚠️  Utilisateur {user_data['email']} non trouvé")
        
        # Commiter les changements
        db.commit()
        
        print(f"\n✅ {updated_count} utilisateurs mis à jour avec succès!")
        
        # Afficher le résumé des rôles
        print("\n" + "=" * 50)
        print("RÉSUMÉ DES RÔLES")
        print("=" * 50)
        
        all_users = db.query(models.User).all()
        for user in all_users:
            print(f"👤 {user.first_name} {user.last_name} ({user.email})")
            print(f"   Rôle: {user.role}")
            print(f"   Statut: {'Actif' if user.is_active else 'Inactif'}")
            print()
        
        print("=" * 50)
        print("HIÉRARCHIE DES RÔLES")
        print("=" * 50)
        print("🔴 Admin: Contrôle total de l'API")
        print("🟡 Analyst: Tous les droits sauf ajouter des utilisateurs")
        print("🟢 Authority: Pas d'ajout d'utilisateurs, pas d'accès mise à jour")
        print("🔵 User: Pas d'accès mise à jour, pas d'ajout d'utilisateurs")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour des rôles: {e}")
        db.rollback()
    finally:
        db.close()

def create_test_users_with_roles():
    """Crée des utilisateurs de test avec les nouveaux rôles"""
    db = SessionLocal()
    
    try:
        # Utilisateurs de test avec nouveaux rôles
        test_users = [
            {
                "first_name": "Alice",
                "last_name": "Analyste",
                "email": "alice.analyste@test.com",
                "username": "alice.analyste",
                "password": "Analyst123!",
                "role": "analyst"
            },
            {
                "first_name": "Bob",
                "last_name": "Authority",
                "email": "bob.authority@test.com",
                "username": "bob.authority",
                "password": "Authority123!",
                "role": "authority"
            },
            {
                "first_name": "Charlie",
                "last_name": "User",
                "email": "charlie.user@test.com",
                "username": "charlie.user",
                "password": "User123!",
                "role": "user"
            }
        ]
        
        created_count = 0
        for user_data in test_users:
            # Vérifier si l'utilisateur existe déjà
            existing_user = db.query(models.User).filter(
                (models.User.email == user_data["email"]) | 
                (models.User.username == user_data["username"])
            ).first()
            
            if existing_user:
                print(f"⚠️  Utilisateur {user_data['username']} existe déjà")
                continue
            
            # Créer le nouvel utilisateur
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            hashed_password = pwd_context.hash(user_data["password"])
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
            created_count += 1
            print(f"✅ Utilisateur {user_data['username']} créé avec le rôle {user_data['role']}")
        
        db.commit()
        print(f"\n✅ {created_count} nouveaux utilisateurs créés!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des utilisateurs: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Mise à jour du système de rôles...")
    print("=" * 50)
    
    # Mettre à jour les rôles existants
    update_user_roles()
    
    # Demander si on veut créer des utilisateurs de test
    response = input("\nVoulez-vous créer des utilisateurs de test avec les nouveaux rôles? (y/n): ")
    if response.lower() in ['y', 'yes', 'o', 'oui']:
        create_test_users_with_roles()
    
    print("\n✅ Configuration des rôles terminée!")
    print("Vous pouvez maintenant tester les différents niveaux d'accès.") 