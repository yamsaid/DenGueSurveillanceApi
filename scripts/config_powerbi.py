#!/usr/bin/env python3
"""
Script de configuration PowerBI
Permet de configurer PowerBI via des variables d'environnement
"""

import os
import json
from pathlib import Path

def create_env_template():
    """Crée un fichier .env.template pour PowerBI"""
    template = """# Configuration PowerBI
# Copiez ce fichier vers .env et remplissez vos valeurs

# ID du rapport PowerBI (obtenu depuis PowerBI Service)
POWERBI_REPORT_ID=your_report_id_here

# URL d'intégration (obtenue depuis PowerBI Service)
POWERBI_EMBED_URL=your_embed_url_here

# Token d'accès (généré via Azure AD ou PowerBI Embed Test Tool)
POWERBI_ACCESS_TOKEN=your_access_token_here

# ID de l'espace de travail (obtenu depuis PowerBI Service)
POWERBI_WORKSPACE_ID=your_workspace_id_here

# URL de base PowerBI (optionnel, par défaut: https://app.powerbi.com)
POWERBI_BASE_URL=https://app.powerbi.com
"""
    
    with open('.env.template', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("✅ Fichier .env.template créé")
    print("📝 Copiez-le vers .env et remplissez vos valeurs")

def update_js_config():
    """Met à jour la configuration JavaScript avec les variables d'environnement"""
    # Lire les variables d'environnement
    config = {
        'reportId': os.getenv('POWERBI_REPORT_ID', 'YOUR_REPORT_ID'),
        'embedUrl': os.getenv('POWERBI_EMBED_URL', 'YOUR_EMBED_URL'),
        'accessToken': os.getenv('POWERBI_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN'),
        'workspaceId': os.getenv('POWERBI_WORKSPACE_ID', 'YOUR_WORKSPACE_ID')
    }
    
    # Lire le fichier JavaScript
    js_file = Path('static/assets/js/page-indicateurs.js')
    if not js_file.exists():
        print("❌ Fichier page-indicateurs.js non trouvé")
        return
    
    content = js_file.read_text(encoding='utf-8')
    
    # Remplacer la configuration
    old_config = """    powerBI: {
        // Remplacez ces valeurs par vos informations PowerBI
        reportId: 'YOUR_REPORT_ID', // Exemple: '12345678-1234-1234-1234-123456789012'
        embedUrl: 'YOUR_EMBED_URL', // Exemple: 'https://app.powerbi.com/reportEmbed?reportId=...'
        accessToken: 'YOUR_ACCESS_TOKEN', // Token d'accès généré
        workspaceId: 'YOUR_WORKSPACE_ID' // Exemple: '12345678-1234-1234-1234-123456789012'
    },"""
    
    new_config = f"""    powerBI: {{
        reportId: '{config['reportId']}',
        embedUrl: '{config['embedUrl']}',
        accessToken: '{config['accessToken']}',
        workspaceId: '{config['workspaceId']}'
    }},"""
    
    content = content.replace(old_config, new_config)
    js_file.write_text(content, encoding='utf-8')
    
    print("✅ Configuration JavaScript mise à jour")

def validate_config():
    """Valide la configuration PowerBI"""
    required_vars = [
        'POWERBI_REPORT_ID',
        'POWERBI_EMBED_URL', 
        'POWERBI_ACCESS_TOKEN',
        'POWERBI_WORKSPACE_ID'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith('your_'):
            missing.append(var)
    
    if missing:
        print("❌ Variables manquantes ou non configurées:")
        for var in missing:
            print(f"   - {var}")
        return False
    
    print("✅ Configuration PowerBI valide")
    return True

def main():
    """Fonction principale"""
    print("🔧 Configuration PowerBI")
    print("=" * 40)
    
    # Créer le template si nécessaire
    if not Path('.env.template').exists():
        create_env_template()
    
    # Vérifier si .env existe
    if Path('.env').exists():
        print("📁 Fichier .env trouvé")
        # Charger les variables d'environnement
        from dotenv import load_dotenv
        load_dotenv()
        
        if validate_config():
            update_js_config()
        else:
            print("\n💡 Pour configurer:")
            print("1. Copiez .env.template vers .env")
            print("2. Remplissez vos valeurs PowerBI")
            print("3. Relancez ce script")
    else:
        print("📁 Fichier .env non trouvé")
        print("💡 Créez-le à partir de .env.template")

if __name__ == "__main__":
    main() 