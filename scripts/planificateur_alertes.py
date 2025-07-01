#!/usr/bin/env python3
"""
Script de planification pour la vérification automatique des alertes épidémiologiques
Ce script s'exécute en arrière-plan et vérifie périodiquement les seuils d'alerte
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.database import get_db
from schemas import utils

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/alertes.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def verification_quotidienne():
    """Vérification automatique quotidienne des alertes"""
    logger.info("Début de la vérification quotidienne des alertes")
    
    try:
        db = next(get_db())
        
        # Vérifier pour toutes les régions
        regions = db.query(utils.models.ModelCasDengue.region).distinct().all()
        regions = [r[0] for r in regions if r[0]]
        
        total_alertes = 0
        
        for region in regions:
            try:
                resultat = utils.gestion_alertes_epidemiologiques(
                    db=db,
                    usermail="admin@gmail.com",
                    region=region
                )
                total_alertes += resultat['alertes_generes']
                logger.info(f"Région {region}: {resultat['alertes_generes']} alertes générées")
                
            except Exception as e:
                logger.error(f"Erreur lors de la vérification pour la région {region}: {e}")
        
        # Vérification globale (toutes régions confondues)
        try:
            resultat_global = utils.gestion_alertes_epidemiologiques(
                db=db,
                usermail="admin@gmail.com",
                region="Toutes"
            )
            total_alertes += resultat_global['alertes_generes']
            logger.info(f"Vérification globale: {resultat_global['alertes_generes']} alertes générées")
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification globale: {e}")
        
        logger.info(f"Vérification quotidienne terminée. Total: {total_alertes} alertes générées")
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification quotidienne: {e}")
    finally:
        try:
            db.close()
        except:
            pass

def verification_hebdomadaire():
    """Vérification hebdomadaire plus approfondie"""
    logger.info("Début de la vérification hebdomadaire approfondie")
    
    try:
        db = next(get_db())
        
        # Vérification automatique complète
        resultat = utils.verification_automatique_alertes(db)
        
        logger.info(f"Vérification hebdomadaire terminée. {resultat['total_alertes_generes']} alertes générées")
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification hebdomadaire: {e}")
    finally:
        try:
            db.close()
        except:
            pass

def verification_mensuelle():
    """Vérification mensuelle avec rapport détaillé"""
    logger.info("Début de la vérification mensuelle avec rapport")
    
    try:
        db = next(get_db())
        
        # Générer un rapport mensuel
        date_fin = datetime.now().date()
        date_debut = date_fin - timedelta(days=30)
        
        # Vérifier les alertes pour la période mensuelle
        resultat = utils.gestion_alertes_epidemiologiques(
            db=db,
            usermail="admin@gmail.com",
            date_debut=date_debut.strftime("%Y-%m-%d"),
            date_fin=date_fin.strftime("%Y-%m-%d"),
            region="Toutes"
        )
        
        logger.info(f"Rapport mensuel généré. {resultat['alertes_generes']} alertes pour la période")
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification mensuelle: {e}")
    finally:
        try:
            db.close()
        except:
            pass

def verification_mensuelle_condition():
    """Vérification mensuelle conditionnelle - s'exécute le 1er du mois"""
    now = datetime.now()
    if now.day == 1:  # Premier jour du mois
        verification_mensuelle()

def main():
    """Fonction principale du planificateur"""
    logger.info("Démarrage du planificateur d'alertes épidémiologiques")
    
    # Créer le dossier de logs s'il n'existe pas
    os.makedirs('logs', exist_ok=True)
    
    # Planifier les vérifications
    schedule.every().day.at("08:00").do(verification_quotidienne)
    schedule.every().monday.at("09:00").do(verification_hebdomadaire)
    schedule.every().day.at("10:00").do(verification_mensuelle_condition)  # Vérification conditionnelle mensuelle
    
    logger.info("Planification configurée:")
    logger.info("- Vérification quotidienne: 08:00")
    logger.info("- Vérification hebdomadaire: Lundi 09:00")
    logger.info("- Vérification mensuelle: 1er du mois 10:00")
    
    # Boucle principale
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
        except KeyboardInterrupt:
            logger.info("Arrêt du planificateur d'alertes")
            break
        except Exception as e:
            logger.error(f"Erreur dans la boucle principale: {e}")
            time.sleep(60)  # Attendre avant de réessayer

if __name__ == "__main__":
    main() 