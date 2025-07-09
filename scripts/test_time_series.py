#!/usr/bin/env python3
"""
Script de test pour diagnostiquer le problème avec get_time_series_data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.database import get_db
from schemas import models
from datetime import datetime, date
from sqlalchemy import and_, func
import pandas as pd

def test_database_connection():
    """Test de la connexion à la base de données"""
    print("🔍 Test de connexion à la base de données...")
    try:
        db = next(get_db())
        # Test simple de requête
        count = db.query(func.count(models.ModelCasDengue.idCas)).scalar()
        print(f"✅ Connexion réussie. Nombre total de cas: {count}")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_data_exists():
    """Vérifie si des données existent dans la base"""
    print("\n🔍 Vérification des données existantes...")
    try:
        db = next(get_db())
        
        # Compter les cas par date
        result = db.query(
            models.ModelCasDengue.date_consultation,
            func.count(models.ModelCasDengue.idCas)
        ).group_by(models.ModelCasDengue.date_consultation).order_by(models.ModelCasDengue.date_consultation).limit(10).all()
        
        print(f"✅ Données trouvées. Aperçu des dates:")
        for date_consultation, count in result:
            print(f"   • {date_consultation}: {count} cas")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def test_date_range():
    """Test avec une plage de dates spécifique"""
    print("\n🔍 Test avec plage de dates (2025-07-01 à 2025-07-06)...")
    try:
        db = next(get_db())
        
        date_debut = "2025-07-01"
        date_fin = "2025-07-06"
        
        # Requête simple
        query = db.query(models.ModelCasDengue).filter(
            and_(
                models.ModelCasDengue.date_consultation >= date_debut,
                models.ModelCasDengue.date_consultation <= date_fin
            )
        )
        
        cas_data = query.all()
        print(f"✅ Cas trouvés pour la période: {len(cas_data)}")
        
        if cas_data:
            print("   Aperçu des premiers cas:")
            for i, cas in enumerate(cas_data[:5]):
                print(f"   • Cas {i+1}: {cas.date_consultation}, {cas.region}, {cas.district}")
        
        return len(cas_data) > 0
    except Exception as e:
        print(f"❌ Erreur lors du test de plage de dates: {e}")
        return False

def test_get_time_series_data():
    """Test de la fonction get_time_series_data"""
    print("\n🔍 Test de la fonction get_time_series_data...")
    try:
        from schemas.utils import get_time_series_data
        
        # Test avec les paramètres
        result = get_time_series_data(
            date_debut="2025-07-01",
            date_fin="2025-07-06",
            frequence="W",
            region="Toutes",
            district="Tous",
            db=next(get_db())
        )
        
        print(f"✅ Fonction exécutée avec succès")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message')}")
        print(f"   Nombre de périodes: {len(result.get('data', []))}")
        
        if result.get('data'):
            print("   Aperçu des données:")
            for i, periode in enumerate(result['data'][:3]):
                print(f"   • Période {i+1}: {periode.get('periode')} - {periode.get('total_cas')} cas")
        
        return result.get('success', False)
    except Exception as e:
        print(f"❌ Erreur lors du test de get_time_series_data: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dataframe_creation():
    """Test de la création du DataFrame"""
    print("\n🔍 Test de création du DataFrame...")
    try:
        db = next(get_db())
        
        # Récupérer des données
        cas_data = db.query(models.ModelCasDengue).filter(
            and_(
                models.ModelCasDengue.date_consultation >= "2025-07-01",
                models.ModelCasDengue.date_consultation <= "2025-07-06"
            )
        ).limit(10).all()
        
        if not cas_data:
            print("❌ Aucune donnée trouvée pour créer le DataFrame")
            return False
        
        # Créer le DataFrame
        df = pd.DataFrame([
            {
                'date_consultation': cas.date_consultation,
                'region': cas.region,
                'district': cas.district,
                'sexe': cas.sexe,
                'age': cas.age,
                'resultat_test': cas.resultat_test,
                'serotype': cas.serotype,
                'hospitalise': cas.hospitalise,
                'issue': cas.issue
            }
            for cas in cas_data
        ])
        
        print(f"✅ DataFrame créé avec succès")
        print(f"   Shape: {df.shape}")
        print(f"   Colonnes: {list(df.columns)}")
        print(f"   Types: {df.dtypes.to_dict()}")
        
        # Test de conversion en datetime
        df['date_consultation'] = pd.to_datetime(df['date_consultation'])
        print(f"   Conversion datetime réussie")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du DataFrame: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests de diagnostic...")
    
    tests = [
        ("Connexion à la base", test_database_connection),
        ("Existence des données", test_data_exists),
        ("Plage de dates", test_date_range),
        ("Création DataFrame", test_dataframe_creation),
        ("Fonction get_time_series_data", test_get_time_series_data),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Test: {test_name}")
        print('='*50)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            results.append((test_name, False))
    
    # Résumé
    print(f"\n{'='*50}")
    print("📊 RÉSUMÉ DES TESTS")
    print('='*50)
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    print(f"\nTotal: {success_count}/{len(results)} tests réussis")

if __name__ == "__main__":
    main() 