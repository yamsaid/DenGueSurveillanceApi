#!/usr/bin/env python3
"""
Script de test pour le système de gestion des alertes épidémiologiques
Ce script permet de tester toutes les fonctionnalités du système d'alertes
"""

import sys
import os
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.database import get_db
from schemas import utils, models

def test_recuperation_seuils():
    """Test de la récupération des seuils utilisateur"""
    print("🔍 Test de récupération des seuils...")
    
    try:
        db = next(get_db())
        
        # Test avec un utilisateur existant
        seuils = utils.recuperer_seuils_utilisateur(db, "admin@gmail.com")
        print(f"✅ Seuils récupérés pour admin@gmail.com: {len(seuils)} paramètres")
        
        # Test avec un utilisateur inexistant (doit utiliser les seuils par défaut)
        seuils_defaut = utils.recuperer_seuils_utilisateur(db, "test@example.com")
        print(f"✅ Seuils par défaut récupérés: {len(seuils_defaut)} paramètres")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des seuils: {e}")
        return False
    finally:
        try:
            db.close()
        except:
            pass

def test_calcul_indicateurs():
    """Test du calcul des indicateurs épidémiologiques"""
    print("\n📊 Test du calcul des indicateurs...")
    
    try:
        db = next(get_db())
        
        # Test avec une période récente
        date_fin = datetime.now().date()
        date_debut = date_fin - timedelta(days=30)
        
        indicateurs = utils.calculer_indicateurs_epidemiologiques(
            db, 
            date_debut.strftime("%Y-%m-%d"),
            date_fin.strftime("%Y-%m-%d"),
            "Toutes"
        )
        
        print(f"✅ Indicateurs calculés:")
        print(f"   - Total cas: {indicateurs['total_cas']}")
        print(f"   - Taux positivité: {indicateurs['taux_positivite']}%")
        print(f"   - Taux hospitalisation: {indicateurs['taux_hospitalisation']}%")
        print(f"   - Taux décès: {indicateurs['taux_deces']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul des indicateurs: {e}")
        return False
    finally:
        try:
            db.close()
        except:
            pass

def test_verification_seuils():
    """Test de la vérification des seuils"""
    print("\n⚠️ Test de la vérification des seuils...")
    
    try:
        db = next(get_db())
        
        # Récupérer les seuils
        seuils = utils.recuperer_seuils_utilisateur(db, "admin@gmail.com")
        
        # Créer des indicateurs de test
        indicateurs_test = {
            "taux_positivite": 25.0,  # Au-dessus du seuil
            "taux_hospitalisation": 8.0,  # En dessous du seuil
            "taux_deces": 12.0  # Au-dessus du seuil
        }
        
        alertes = utils.verifier_seuils_alertes(
            indicateurs_test, 
            seuils, 
            "Centre", 
            "Toutes"
        )
        
        print(f"✅ Alertes générées: {len(alertes)}")
        for alerte in alertes:
            print(f"   - {alerte['type']}: {alerte['message']} (niveau: {alerte['niveau']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des seuils: {e}")
        return False
    finally:
        try:
            db.close()
        except:
            pass

def test_gestion_alertes_complete():
    """Test complet de la gestion des alertes"""
    print("\n🚀 Test complet de la gestion des alertes...")
    
    try:
        db = next(get_db())
        
        # Test avec une période récente
        date_fin = datetime.now().date()
        date_debut = date_fin - timedelta(days=7)
        
        resultat = utils.gestion_alertes_epidemiologiques(
            db=db,
            usermail="admin@gmail.com",
            date_debut=date_debut.strftime("%Y-%m-%d"),
            date_fin=date_fin.strftime("%Y-%m-%d"),
            region="Toutes"
        )
        
        print(f"✅ Gestion des alertes terminée:")
        print(f"   - Période: {resultat['periode_analyse']}")
        print(f"   - Alertes générées: {resultat['alertes_generes']}")
        print(f"   - Alertes sauvegardées: {resultat['alertes_sauvegardees']}")
        
        if resultat['details_alertes']:
            print("   - Détails des alertes:")
            for alerte in resultat['details_alertes']:
                print(f"     * {alerte['type']}: {alerte['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la gestion complète des alertes: {e}")
        return False
    finally:
        try:
            db.close()
        except:
            pass

def test_verification_automatique():
    """Test de la vérification automatique"""
    print("\n🤖 Test de la vérification automatique...")
    
    try:
        db = next(get_db())
        
        resultat = utils.verification_automatique_alertes(db)
        
        print(f"✅ Vérification automatique terminée:")
        print(f"   - Régions vérifiées: {resultat['total_regions_verifiees']}")
        print(f"   - Total alertes générées: {resultat['total_alertes_generes']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification automatique: {e}")
        return False
    finally:
        try:
            db.close()
        except:
            pass

def test_consultation_alertes():
    """Test de la consultation des alertes"""
    print("\n📋 Test de la consultation des alertes...")
    
    try:
        db = next(get_db())
        
        # Compter les alertes existantes
        total_alertes = db.query(models.AlertLog).count()
        alertes_critiques = db.query(models.AlertLog).filter(
            models.AlertLog.notification_type == "critical"
        ).count()
        
        # Récupérer les dernières alertes
        dernieres_alertes = db.query(models.AlertLog).order_by(
            models.AlertLog.created_at.desc()
        ).limit(5).all()
        
        print(f"✅ Consultation des alertes:")
        print(f"   - Total alertes en base: {total_alertes}")
        print(f"   - Alertes critiques: {alertes_critiques}")
        print(f"   - 5 dernières alertes:")
        
        for alerte in dernieres_alertes:
            print(f"     * {alerte.created_at}: {alerte.message} ({alerte.notification_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la consultation des alertes: {e}")
        return False
    finally:
        try:
            db.close()
        except:
            pass

def main():
    """Fonction principale de test"""
    print("🧪 Tests du Système de Gestion des Alertes Épidémiologiques")
    print("=" * 60)
    
    tests = [
        ("Récupération des seuils", test_recuperation_seuils),
        ("Calcul des indicateurs", test_calcul_indicateurs),
        ("Vérification des seuils", test_verification_seuils),
        ("Gestion complète des alertes", test_gestion_alertes_complete),
        ("Vérification automatique", test_verification_automatique),
        ("Consultation des alertes", test_consultation_alertes)
    ]
    
    resultats = []
    
    for nom_test, fonction_test in tests:
        try:
            resultat = fonction_test()
            resultats.append((nom_test, resultat))
        except Exception as e:
            print(f"❌ Erreur inattendue dans {nom_test}: {e}")
            resultats.append((nom_test, False))
    
    # Résumé des tests
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    tests_reussis = sum(1 for _, resultat in resultats if resultat)
    total_tests = len(resultats)
    
    for nom_test, resultat in resultats:
        statut = "✅ RÉUSSI" if resultat else "❌ ÉCHOUÉ"
        print(f"{statut} - {nom_test}")
    
    print(f"\n🎯 Résultat global: {tests_reussis}/{total_tests} tests réussis")
    
    if tests_reussis == total_tests:
        print("🎉 Tous les tests sont passés avec succès !")
        return 0
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
        return 1

if __name__ == "__main__":
    exit(main()) 