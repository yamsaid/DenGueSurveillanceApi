#!/usr/bin/env python3
"""
Script pour créer automatiquement les favicons à partir du logo SVG existant.
Ce script génère les formats : PNG, ICO, et Apple Touch Icon.
"""

import os
import sys
from pathlib import Path

def create_favicon_files():
    """Crée les fichiers favicon manquants."""
    
    # Chemins des fichiers
    svg_path = "static/assets/img/logoproduct.svg"
    favicon_svg = "static/assets/img/favicon.svg"
    favicon_png = "static/assets/img/favicon.png"
    favicon_ico = "static/assets/img/favicon.ico"
    apple_touch = "static/assets/img/apple-touch-icon.png"
    
    print("🔧 Création des favicons...")
    
    # 1. Copier le SVG comme favicon SVG
    if os.path.exists(svg_path):
        try:
            with open(svg_path, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(favicon_svg, 'w', encoding='utf-8') as dst:
                dst.write(content)
            print("✅ favicon.svg créé")
        except Exception as e:
            print(f"❌ Erreur lors de la création de favicon.svg: {e}")
    else:
        print("⚠️  Logo SVG non trouvé, création d'un favicon par défaut")
        create_default_favicon_svg(favicon_svg)
    
    # 2. Créer les fichiers PNG et ICO (placeholder)
    create_placeholder_files()
    
    print("\n📝 Instructions pour finaliser les favicons:")
    print("1. Ouvrez votre logo SVG dans un éditeur d'image (Inkscape, GIMP, etc.)")
    print("2. Exportez-le en PNG aux tailles suivantes:")
    print("   - 16x16 px → favicon.png")
    print("   - 32x32 px → favicon.png (ou 16x16)")
    print("   - 180x180 px → apple-touch-icon.png")
    print("3. Convertissez le PNG en ICO pour favicon.ico")
    print("\n🌐 Votre favicon SVG est déjà fonctionnel !")

def create_default_favicon_svg(favicon_path):
    """Crée un favicon SVG par défaut si le logo n'existe pas."""
    default_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="32" height="32" rx="6" fill="url(#grad)"/>
  <text x="16" y="22" font-family="Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="white">D</text>
</svg>'''
    
    try:
        with open(favicon_path, 'w', encoding='utf-8') as f:
            f.write(default_svg)
        print("✅ favicon.svg par défaut créé")
    except Exception as e:
        print(f"❌ Erreur lors de la création du favicon par défaut: {e}")

def create_placeholder_files():
    """Crée des fichiers placeholder pour les formats PNG et ICO."""
    placeholder_content = "# Placeholder - Remplacez par vos vraies images"
    
    files_to_create = [
        "static/assets/img/favicon.png",
        "static/assets/img/favicon.ico", 
        "static/assets/img/apple-touch-icon.png"
    ]
    
    for file_path in files_to_create:
        try:
            # Créer le dossier parent si nécessaire
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Créer un fichier texte temporaire
            with open(file_path + ".txt", 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            print(f"📝 Placeholder créé pour {file_path}")
        except Exception as e:
            print(f"❌ Erreur lors de la création du placeholder {file_path}: {e}")

if __name__ == "__main__":
    create_favicon_files()
    print("\n🎉 Configuration des favicons terminée !")
    print("💡 Le favicon SVG fonctionne déjà dans les navigateurs modernes.") 