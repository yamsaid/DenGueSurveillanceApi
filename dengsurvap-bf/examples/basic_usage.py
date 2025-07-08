"""
Exemple d'utilisation de base du client Appi Dengue

Ce script montre comment utiliser les fonctionnalités principales
du client pour accéder aux données de surveillance de la dengue.
"""
# dengsurvap-bf # Dengue Surveillance API for Burkina Faso
# pip install dengsurvap-bf
# Importation des bibliothèques nécessaires
import os
from datetime import datetime, timedelta
from dengsurvab import AppiClient

# Fonction principale
def main():
    """Exemple principal d'utilisation du client."""
    
    # Configuration du client
    # Vous pouvez utiliser des variables d'environnement ou configurer directement
    base_url = os.getenv('APPI_API_URL', 'https://votre-api-appi.com')
    api_key = os.getenv('APPI_API_KEY', 'votre-clé-api')
    
    print("=== Client Appi Dengue - Exemple d'utilisation ===\n")
    
    # Initialisation du client
    print("1. Initialisation du client...")
    client = AppiClient(
        base_url=base_url,
        api_key=api_key,
        debug=True  # Activer les logs détaillés
    )
    
    # Authentification (optionnelle si vous avez une clé API)
    print("\n2. Authentification...")
    try:
        # Remplacez par vos identifiants
        auth_result = client.authenticate("votre-email@example.com", "votre-mot-de-passe")
        print(f"✅ Authentification réussie pour {auth_result.get('user', {}).get('email', 'N/A')}")
    except Exception as e:
        print(f"⚠️  Authentification échouée: {e}")
        print("Continuing without authentication...")
    
    # Récupération des statistiques générales
    print("\n3. Récupération des statistiques...")
    try:
        stats = client.get_stats()
        print(f"📊 Statistiques générales:")
        print(f"   - Total cas: {stats.total_cas}")
        print(f"   - Cas positifs: {stats.total_positifs}")
        print(f"   - Hospitalisations: {stats.total_hospitalisations}")
        print(f"   - Décès: {stats.total_deces}")
        print(f"   - Régions actives: {len(stats.regions_actives)}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des statistiques: {e}")
    
    # Récupération des régions et districts
    print("\n4. Récupération des régions et districts...")
    try:
        regions = client.get_regions()
        print(f"🏛️  Régions disponibles: {regions}")
        
        if regions:
            districts = client.get_districts(region=regions[0])
            print(f"📍 Districts de {regions[0]}: {districts[:5]}...")  # Afficher les 5 premiers
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des régions: {e}")
    
    # Récupération des cas de dengue
    print("\n5. Récupération des cas de dengue...")
    try:
        # Date de la dernière semaine
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        cas = client.get_cas_dengue(
            date_debut=start_date.strftime("%Y-%m-%d"),
            date_fin=end_date.strftime("%Y-%m-%d"),
            limit=10
        )
        
        print(f"🦟 Cas de dengue récupérés: {len(cas)}")
        if cas:
            print(f"   Premier cas: {cas[0].date_consultation} - {cas[0].region}")
            print(f"   Dernier cas: {cas[-1].date_consultation} - {cas[-1].region}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des cas: {e}")
    
    # Récupération des indicateurs hebdomadaires
    print("\n6. Récupération des indicateurs hebdomadaires...")
    try:
        indicateurs = client.data_period(
            date_debut=start_date.strftime("%Y-%m-%d"),
            date_fin=end_date.strftime("%Y-%m-%d"),
            region="Toutes"
        )
        
        print(f"📈 Indicateurs hebdomadaires récupérés: {len(indicateurs)}")
        if indicateurs:
            latest = indicateurs[-1]
            print(f"   Dernière semaine: {latest.date_debut} - {latest.date_fin}")
            print(f"   Total cas: {latest.total_cas}")
            print(f"   Taux positivité: {latest.taux_positivite:.1f}%")
            print(f"   Taux hospitalisation: {latest.taux_hospitalisation:.1f}%")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des indicateurs: {e}")
    
    # Récupération des alertes
    print("\n7. Récupération des alertes...")
    try:
        alertes = client.get_alertes(limit=5)
        print(f"🚨 Alertes récupérées: {len(alertes)}")
        
        for alerte in alertes[:3]:  # Afficher les 3 premières
            print(f"   - {alerte.severity}: {alerte.message}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des alertes: {e}")
    
    # Export de données
    print("\n8. Export de données...")
    try:
        # Export au format CSV
        csv_data = client.export_data(
            format="csv",
            date_debut=start_date.strftime("%Y-%m-%d"),
            date_fin=end_date.strftime("%Y-%m-%d"),
            limit=100
        )
        
        # Sauvegarder le fichier
        with open("donnees_dengue.csv", "wb") as f:
            f.write(csv_data)
        
        print(f"💾 Données exportées dans 'donnees_dengue.csv' ({len(csv_data)} bytes)")
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
    
    # Analyse épidémiologique
    print("\n9. Analyse épidémiologique...")
    try:
        # Récupérer une série temporelle
        series = client.get_time_series(
            date_debut=(end_date - timedelta(days=30)).strftime("%Y-%m-%d"),
            date_fin=end_date.strftime("%Y-%m-%d"),
            region="Toutes"
        )
        
        print(f"📊 Série temporelle générée: {len(series)} points")
        
        # Calculer les taux
        rates = client.calculate_rates(
            date_debut=(end_date - timedelta(days=30)).strftime("%Y-%m-%d"),
            date_fin=end_date.strftime("%Y-%m-%d")
        )
        
        print(f"📈 Taux calculés:")
        print(f"   - Positivité: {rates.get('taux_positivite', 0):.1f}%")
        print(f"   - Hospitalisation: {rates.get('taux_hospitalisation', 0):.1f}%")
        print(f"   - Létalité: {rates.get('taux_letalite', 0):.1f}%")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
    
    # Configuration des alertes
    print("\n10. Configuration des alertes...")
    try:
        # Configurer les seuils d'alerte
        config_result = client.configurer_seuils(
            seuil_positivite=15,
            seuil_hospitalisation=10,
            seuil_deces=5
        )
        
        print("✅ Seuils d'alerte configurés")
        print(f"   - Seuil positivité: 15%")
        print(f"   - Seuil hospitalisation: 10%")
        print(f"   - Seuil décès: 5%")
    except Exception as e:
        print(f"❌ Erreur lors de la configuration des alertes: {e}")
    
    print("\n=== Exemple terminé ===")
    print("📚 Consultez la documentation pour plus d'exemples et de fonctionnalités.")


if __name__ == "__main__":
    main() 