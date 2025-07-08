"""
Exemple de génération de tableau de bord épidémiologique

Ce script montre comment générer un tableau de bord complet
avec des analyses épidémiologiques avancées.
"""

import os
from datetime import datetime, timedelta
from dengsurvab import AppiClient, DashboardGenerator


def generate_epidemiological_dashboard():
    """Génère un tableau de bord épidémiologique complet."""
    
    print("=== Tableau de Bord Épidémiologique - Appi Dengue ===\n")
    
    # Configuration du client
    base_url = os.getenv('APPI_API_URL', 'https://votre-api-appi.com')
    api_key = os.getenv('APPI_API_KEY', 'votre-clé-api')
    
    client = AppiClient(base_url=base_url, api_key=api_key)
    dashboard = DashboardGenerator(client)
    
    # Période d'analyse (derniers 3 mois)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    print(f"📅 Période d'analyse: {start_date} à {end_date}")
    print(f"📊 Génération du tableau de bord...\n")
    
    try:
        # Générer le rapport complet
        report = dashboard.generate_report(
            date_debut=start_date.strftime("%Y-%m-%d"),
            date_fin=end_date.strftime("%Y-%m-%d"),
            region="Toutes",
            district="Toutes",
            include_visualizations=True
        )
        
        # Afficher le résumé
        print("📋 RÉSUMÉ EXÉCUTIF")
        print("=" * 50)
        summary = report['summary']
        print(f"Total cas: {summary['total_cas']:,}")
        print(f"Cas positifs: {summary['total_positifs']:,}")
        print(f"Hospitalisations: {summary['total_hospitalisations']:,}")
        print(f"Décès: {summary['total_deces']:,}")
        
        # Afficher les taux
        print("\n📈 INDICATEURS ÉPIDÉMIOLOGIQUES")
        print("=" * 50)
        rates = report['rates']
        print(f"Taux de positivité: {rates.get('taux_positivite', 0):.1f}%")
        print(f"Taux d'hospitalisation: {rates.get('taux_hospitalisation', 0):.1f}%")
        print(f"Taux de létalité: {rates.get('taux_letalite', 0):.1f}%")
        
        # Afficher l'analyse des tendances
        print("\n📊 ANALYSE DES TENDANCES")
        print("=" * 50)
        trend = report['trend_analysis']
        if trend:
            print(f"Direction de la tendance: {trend.get('trend_direction', 'N/A')}")
            print(f"Pente: {trend.get('slope', 0):.2f}")
            print(f"Pente (%): {trend.get('slope_percentage', 0):.1f}%")
            print(f"Coefficient de corrélation: {trend.get('correlation', 0):.3f}")
        
        # Afficher l'analyse saisonnière
        print("\n🌡️ ANALYSE SAISONNIÈRE")
        print("=" * 50)
        seasonal = report['seasonal_analysis']
        if seasonal:
            print(f"Mois de pic: {seasonal.get('peak_month', 'N/A')}")
            print(f"Mois de creux: {seasonal.get('trough_month', 'N/A')}")
            print(f"Amplitude saisonnière: {seasonal.get('seasonal_amplitude', 0):.1f}")
        
        # Afficher les prédictions
        print("\n🔮 PRÉDICTIONS")
        print("=" * 50)
        forecast = report['forecast']
        if forecast:
            print(f"Prédiction semaine suivante: {forecast.get('prediction', 0):.0f} cas")
            print(f"Intervalle de confiance: [{forecast.get('confidence_interval_lower', 0):.0f}, {forecast.get('confidence_interval_upper', 0):.0f}]")
            print(f"Méthode utilisée: {forecast.get('method', 'N/A')}")
        
        # Afficher les anomalies
        print("\n🚨 ANOMALIES DÉTECTÉES")
        print("=" * 50)
        anomalies = report['anomalies']
        print(f"Nombre d'anomalies: {anomalies['count']}")
        
        if anomalies['periods']:
            print("Périodes avec anomalies:")
            for period in anomalies['periods'][:3]:  # Afficher les 3 premières
                print(f"  - {period['date_debut']} à {period['date_fin']}: {period['total_cas']} cas")
        
        # Sauvegarder le rapport
        print("\n💾 SAUVEGARDE DU RAPPORT")
        print("=" * 50)
        report_file = f"rapport_epidemiologique_{end_date.strftime('%Y%m%d')}.json"
        if dashboard.save_report(report, report_file):
            print(f"✅ Rapport sauvegardé dans '{report_file}'")
        else:
            print("❌ Erreur lors de la sauvegarde")
        
        # Générer des visualisations (si matplotlib est disponible)
        try:
            import matplotlib.pyplot as plt
            generate_visualizations(report, end_date)
        except ImportError:
            print("📊 Matplotlib non disponible - visualisations ignorées")
        
        print("\n✅ Tableau de bord généré avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du tableau de bord: {e}")


def generate_visualizations(report, end_date):
    """Génère des visualisations pour le tableau de bord."""
    
    print("\n📊 GÉNÉRATION DES VISUALISATIONS")
    print("=" * 50)
    
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        
        # Créer un DataFrame à partir des données
        data = pd.DataFrame(report['data'])
        if data.empty:
            print("Aucune donnée disponible pour les visualisations")
            return
        
        # Convertir les dates
        data['date_debut'] = pd.to_datetime(data['date_debut'])
        
        # Créer une figure avec plusieurs sous-graphiques
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Tableau de Bord Épidémiologique - {end_date}', fontsize=16)
        
        # 1. Évolution temporelle des cas
        axes[0, 0].plot(data['date_debut'], data['total_cas'], 'b-', linewidth=2)
        axes[0, 0].set_title('Évolution des cas de dengue')
        axes[0, 0].set_ylabel('Nombre de cas')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Taux de positivité
        axes[0, 1].plot(data['date_debut'], data['taux_positivite'], 'r-', linewidth=2)
        axes[0, 1].set_title('Taux de positivité')
        axes[0, 1].set_ylabel('Taux (%)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Hospitalisations vs décès
        axes[1, 0].bar(data['date_debut'], data['hospitalisations'], alpha=0.7, label='Hospitalisations')
        axes[1, 0].bar(data['date_debut'], data['deces'], alpha=0.7, label='Décès')
        axes[1, 0].set_title('Hospitalisations et décès')
        axes[1, 0].set_ylabel('Nombre')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Taux d'hospitalisation
        axes[1, 1].plot(data['date_debut'], data['taux_hospitalisation'], 'g-', linewidth=2)
        axes[1, 1].set_title('Taux d\'hospitalisation')
        axes[1, 1].set_ylabel('Taux (%)')
        axes[1, 1].grid(True, alpha=0.3)
        
        # Ajuster la mise en page
        plt.tight_layout()
        
        # Sauvegarder la figure
        plot_file = f"dashboard_visualization_{end_date.strftime('%Y%m%d')}.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"✅ Visualisations sauvegardées dans '{plot_file}'")
        
        # Afficher la figure
        plt.show()
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des visualisations: {e}")


def generate_alert_report():
    """Génère un rapport d'alertes."""
    
    print("\n🚨 RAPPORT D'ALERTES")
    print("=" * 50)
    
    base_url = os.getenv('APPI_API_URL', 'https://votre-api-appi.com')
    api_key = os.getenv('APPI_API_KEY', 'votre-clé-api')
    
    client = AppiClient(base_url=base_url, api_key=api_key)
    
    try:
        # Récupérer les alertes critiques
        alertes_critiques = client.get_alertes_critiques(limit=10)
        print(f"Alertes critiques: {len(alertes_critiques)}")
        
        for alerte in alertes_critiques[:5]:
            print(f"  - {alerte.created_at}: {alerte.message}")
        
        # Récupérer les alertes actives
        alertes_actives = client.get_alertes_actives(limit=10)
        print(f"\nAlertes actives: {len(alertes_actives)}")
        
        for alerte in alertes_actives[:5]:
            print(f"  - {alerte.severity}: {alerte.message}")
        
        # Vérifier les alertes
        print("\n🔍 Vérification des alertes...")
        verification = client.verifier_alertes(
            date_debut=(datetime.now().date() - timedelta(days=7)).strftime("%Y-%m-%d"),
            date_fin=datetime.now().date().strftime("%Y-%m-%d")
        )
        
        print(f"Vérification terminée: {verification.get('status', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du rapport d'alertes: {e}")


if __name__ == "__main__":
    # Générer le tableau de bord principal
    generate_epidemiological_dashboard()
    
    # Générer le rapport d'alertes
    generate_alert_report()
    
    print("\n🎉 Génération des rapports terminée!")
    print("📊 Consultez les fichiers générés pour plus de détails.") 