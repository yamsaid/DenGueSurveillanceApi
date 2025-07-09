#!/usr/bin/env python3
"""
Script pour supprimer des données de la base de données Railway
Permet de supprimer des observations selon différents critères
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, date
import sys

def get_database_connection():
    """Établit la connexion à la base de données Railway"""
    try:
        # Récupération de l'URL depuis les variables d'environnement
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            print("❌ Erreur: DATABASE_URL non définie")
            print("Assurez-vous que la variable d'environnement DATABASE_URL est configurée")
            return None
        
        # Correction de l'URL si nécessaire (postgres:// -> postgresql://)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        engine = create_engine(database_url)
        return engine
    
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def show_current_data(engine):
    """Affiche les données actuelles dans la base"""
    try:
        with engine.connect() as conn:
            # Compter les cas de dengue
            result = conn.execute(text("SELECT COUNT(*) FROM tdengue2"))
            total_cas = result.scalar()
            
            # Compter les soumissions
            result = conn.execute(text("SELECT COUNT(*) FROM tsoumissions2"))
            total_soumissions = result.scalar()
            
            print(f"\n📊 Données actuelles dans la base :")
            print(f"   • Cas de dengue : {total_cas}")
            print(f"   • Soumissions : {total_soumissions}")
            
            # Aperçu des dernières données
            if total_cas > 0:
                result = conn.execute(text("""
                    SELECT idCas, date_consultation, region, district, sexe, age, resultat_test 
                    FROM tdengue2 
                    ORDER BY idCas DESC 
                    LIMIT 5
                """))
                print(f"\n📋 Derniers cas ajoutés :")
                for row in result:
                    print(f"   • ID: {row[0]}, Date: {row[1]}, Région: {row[2]}, District: {row[3]}")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage des données: {e}")

def delete_by_date_range(engine, start_date, end_date):
    """Supprime les données dans une plage de dates"""
    try:
        with engine.connect() as conn:
            # Compter avant suppression
            result = conn.execute(text(f"""
                SELECT COUNT(*) FROM tdengue2 
                WHERE date_consultation BETWEEN '{start_date}' AND '{end_date}'
            """))
            count_before = result.scalar()
            
            if count_before == 0:
                print(f"❌ Aucune donnée trouvée entre {start_date} et {end_date}")
                return
            
            # Suppression
            result = conn.execute(text(f"""
                DELETE FROM tdengue2 
                WHERE date_consultation BETWEEN '{start_date}' AND '{end_date}'
            """))
            conn.commit()
            
            print(f"✅ {count_before} cas supprimés entre {start_date} et {end_date}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")

def delete_by_region(engine, region):
    """Supprime les données d'une région spécifique"""
    try:
        with engine.connect() as conn:
            # Compter avant suppression
            result = conn.execute(text(f"""
                SELECT COUNT(*) FROM tdengue2 
                WHERE region = '{region}'
            """))
            count_before = result.scalar()
            
            if count_before == 0:
                print(f"❌ Aucune donnée trouvée pour la région {region}")
                return
            
            # Suppression
            result = conn.execute(text(f"""
                DELETE FROM tdengue2 
                WHERE region = '{region}'
            """))
            conn.commit()
            
            print(f"✅ {count_before} cas supprimés pour la région {region}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")

def delete_by_id_range(engine, start_id, end_id):
    """Supprime les données dans une plage d'ID"""
    try:
        with engine.connect() as conn:
            # Compter avant suppression
            result = conn.execute(text(f"""
                SELECT COUNT(*) FROM tdengue2 
                WHERE idCas BETWEEN {start_id} AND {end_id}
            """))
            count_before = result.scalar()
            
            if count_before == 0:
                print(f"❌ Aucune donnée trouvée entre les ID {start_id} et {end_id}")
                return
            
            # Suppression
            result = conn.execute(text(f"""
                DELETE FROM tdengue2 
                WHERE idCas BETWEEN {start_id} AND {end_id}
            """))
            conn.commit()
            
            print(f"✅ {count_before} cas supprimés entre les ID {start_id} et {end_id}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")

def delete_all_data(engine):
    """Supprime toutes les données (⚠️ ATTENTION)"""
    try:
        with engine.connect() as conn:
            # Compter avant suppression
            result = conn.execute(text("SELECT COUNT(*) FROM tdengue2"))
            count_before = result.scalar()
            
            if count_before == 0:
                print("❌ Aucune donnée à supprimer")
                return
            
            # Demander confirmation
            confirm = input(f"⚠️  ATTENTION: Vous allez supprimer {count_before} cas. Continuer ? (oui/non): ")
            if confirm.lower() != 'oui':
                print("❌ Suppression annulée")
                return
            
            # Suppression
            result = conn.execute(text("DELETE FROM tdengue2"))
            conn.commit()
            
            print(f"✅ {count_before} cas supprimés")
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")

def main():
    """Fonction principale"""
    print("🗑️  Script de suppression de données - Base Railway")
    
    # Connexion à la base
    engine = get_database_connection()
    if not engine:
        return
    
    # Affichage des données actuelles
    show_current_data(engine)
    
    print(f"\n🔧 Options de suppression :")
    print(f"   1. Supprimer par plage de dates")
    print(f"   2. Supprimer par région")
    print(f"   3. Supprimer par plage d'ID")
    print(f"   4. Supprimer toutes les données (⚠️ ATTENTION)")
    print(f"   5. Quitter")
    
    choice = input("\nChoisissez une option (1-5): ")
    
    if choice == "1":
        start_date = input("Date de début (YYYY-MM-DD): ")
        end_date = input("Date de fin (YYYY-MM-DD): ")
        delete_by_date_range(engine, start_date, end_date)
        
    elif choice == "2":
        region = input("Région à supprimer (ex: Centre, Hauts Bassins): ")
        delete_by_region(engine, region)
        
    elif choice == "3":
        start_id = input("ID de début: ")
        end_id = input("ID de fin: ")
        delete_by_id_range(engine, int(start_id), int(end_id))
        
    elif choice == "4":
        delete_all_data(engine)
        
    elif choice == "5":
        print("👋 Au revoir !")
        
    else:
        print("❌ Option invalide")

if __name__ == "__main__":
    main() 