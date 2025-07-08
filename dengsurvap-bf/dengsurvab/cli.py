"""
Interface en ligne de commande pour le client Appi Dengue

Ce module fournit une interface CLI simple pour utiliser le client.
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
from typing import Optional

from . import AppiClient


def main():
    """Point d'entrée principal du CLI."""
    parser = argparse.ArgumentParser(
        description="Client CLI pour l'API de surveillance de la dengue Appi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s stats
  %(prog)s cas --date-debut 2024-01-01 --date-fin 2024-01-31
  %(prog)s alertes --severity critical
  %(prog)s export --format csv --output donnees.csv
        """
    )
    
    # Arguments globaux
    parser.add_argument(
        "--api-url",
        default=os.getenv("APPI_API_URL"),
        help="URL de l'API Appi"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("APPI_API_KEY"),
        help="Clé API"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Mode debug"
    )
    
    # Sous-commandes
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    # Commande stats
    stats_parser = subparsers.add_parser("stats", help="Afficher les statistiques")
    
    # Commande cas
    cas_parser = subparsers.add_parser("cas", help="Récupérer les cas de dengue")
    cas_parser.add_argument("--date-debut", help="Date de début (YYYY-MM-DD)")
    cas_parser.add_argument("--date-fin", help="Date de fin (YYYY-MM-DD)")
    cas_parser.add_argument("--region", help="Région")
    cas_parser.add_argument("--district", help="District")
    cas_parser.add_argument("--limit", type=int, default=10, help="Nombre maximum de cas")
    
    # Commande alertes
    alertes_parser = subparsers.add_parser("alertes", help="Gérer les alertes")
    alertes_parser.add_argument("--severity", choices=["warning", "critical", "info"], help="Sévérité")
    alertes_parser.add_argument("--status", choices=["active", "resolved"], help="Statut")
    alertes_parser.add_argument("--limit", type=int, default=10, help="Nombre maximum d'alertes")
    
    # Commande export
    export_parser = subparsers.add_parser("export", help="Exporter les données")
    export_parser.add_argument("--format", choices=["csv", "json", "excel"], default="csv", help="Format d'export")
    export_parser.add_argument("--output", help="Fichier de sortie")
    export_parser.add_argument("--date-debut", help="Date de début (YYYY-MM-DD)")
    export_parser.add_argument("--date-fin", help="Date de fin (YYYY-MM-DD)")
    export_parser.add_argument("--region", help="Région")
    export_parser.add_argument("--district", help="District")
    
    # Commande auth
    auth_parser = subparsers.add_parser("auth", help="Authentification")
    auth_parser.add_argument("--email", required=True, help="Email")
    auth_parser.add_argument("--password", required=True, help="Mot de passe")
    
    # Commande regions
    regions_parser = subparsers.add_parser("regions", help="Lister les régions")
    
    # Commande districts
    districts_parser = subparsers.add_parser("districts", help="Lister les districts")
    districts_parser.add_argument("--region", help="Région")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialiser le client
    if not args.api_url:
        print("❌ Erreur: URL de l'API requise (--api-url ou APPI_API_URL)")
        sys.exit(1)
    
    try:
        client = AppiClient(
            base_url=args.api_url,
            api_key=args.api_key,
            debug=args.debug
        )
        
        # Exécuter la commande
        if args.command == "stats":
            handle_stats(client)
        elif args.command == "cas":
            handle_cas(client, args)
        elif args.command == "alertes":
            handle_alertes(client, args)
        elif args.command == "export":
            handle_export(client, args)
        elif args.command == "auth":
            handle_auth(client, args)
        elif args.command == "regions":
            handle_regions(client)
        elif args.command == "districts":
            handle_districts(client, args)
        else:
            print(f"❌ Commande inconnue: {args.command}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def handle_stats(client):
    """Gérer la commande stats."""
    print("📊 Récupération des statistiques...")
    
    try:
        stats = client.get_stats()
        print(f"\n📈 Statistiques générales:")
        print(f"   Total cas: {stats.total_cas:,}")
        print(f"   Cas positifs: {stats.total_positifs:,}")
        print(f"   Hospitalisations: {stats.total_hospitalisations:,}")
        print(f"   Décès: {stats.total_deces:,}")
        print(f"   Régions actives: {len(stats.regions_actives)}")
        print(f"   Districts actifs: {len(stats.districts_actifs)}")
        print(f"   Dernière mise à jour: {stats.derniere_mise_a_jour}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des statistiques: {e}")


def handle_cas(client, args):
    """Gérer la commande cas."""
    print("🦟 Récupération des cas de dengue...")
    
    try:
        cas = client.get_cas_dengue(
            date_debut=args.date_debut,
            date_fin=args.date_fin,
            region=args.region,
            district=args.district,
            limit=args.limit
        )
        
        print(f"\n📋 Cas récupérés: {len(cas)}")
        
        for i, c in enumerate(cas[:5], 1):  # Afficher les 5 premiers
            print(f"   {i}. {c.date_consultation} - {c.region} - {c.sexe} ({c.age} ans)")
            if c.resultat_test:
                print(f"      Test: {c.resultat_test}")
            if c.hospitalise:
                print(f"      Hospitalisé: {c.hospitalise}")
        
        if len(cas) > 5:
            print(f"   ... et {len(cas) - 5} autres cas")
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des cas: {e}")


def handle_alertes(client, args):
    """Gérer la commande alertes."""
    print("🚨 Récupération des alertes...")
    
    try:
        alertes = client.get_alertes(
            limit=args.limit,
            severity=args.severity,
            status=args.status
        )
        
        print(f"\n📢 Alertes récupérées: {len(alertes)}")
        
        for i, a in enumerate(alertes, 1):
            print(f"   {i}. [{a.severity}] {a.message}")
            print(f"      Région: {a.region or 'N/A'}")
            print(f"      Statut: {a.status or 'N/A'}")
            print(f"      Date: {a.created_at or 'N/A'}")
            print()
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des alertes: {e}")


def handle_export(client, args):
    """Gérer la commande export."""
    print(f"💾 Export des données au format {args.format}...")
    
    try:
        data = client.export_data(
            format=args.format,
            date_debut=args.date_debut,
            date_fin=args.date_fin,
            region=args.region,
            district=args.district
        )
        
        if args.output:
            with open(args.output, "wb") as f:
                f.write(data)
            print(f"✅ Données exportées dans '{args.output}' ({len(data)} bytes)")
        else:
            # Afficher les données
            if args.format == "json":
                import json
                print(json.dumps(json.loads(data.decode()), indent=2))
            else:
                print(data.decode())
                
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")


def handle_auth(client, args):
    """Gérer la commande auth."""
    print("🔐 Authentification...")
    
    try:
        result = client.authenticate(args.email, args.password)
        print(f"✅ Authentification réussie pour {args.email}")
        print(f"   Token: {result.get('access_token', 'N/A')[:20]}...")
        
    except Exception as e:
        print(f"❌ Erreur d'authentification: {e}")


def handle_regions(client):
    """Gérer la commande regions."""
    print("🏛️ Récupération des régions...")
    
    try:
        regions = client.get_regions()
        print(f"\n📋 Régions disponibles ({len(regions)}):")
        
        for i, region in enumerate(regions, 1):
            print(f"   {i}. {region}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des régions: {e}")


def handle_districts(client, args):
    """Gérer la commande districts."""
    print("📍 Récupération des districts...")
    
    try:
        districts = client.get_districts(region=args.region)
        region_info = f" de {args.region}" if args.region else ""
        print(f"\n📋 Districts{region_info} ({len(districts)}):")
        
        for i, district in enumerate(districts, 1):
            print(f"   {i}. {district}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des districts: {e}")


if __name__ == "__main__":
    main() 