# Système de Surveillance et d'Alerte Dengue

Ce projet est une application web de surveillance épidémiologique dédiée à la détection, l'analyse et la gestion des alertes liées à la dengue. Il permet de configurer des seuils d'alerte, de visualiser des statistiques, d'explorer les données, et de suivre l'évolution des indicateurs clés en temps réel.

## Fonctionnalités principales

- **Configuration des seuils d'alerte** :
  - Définissez des seuils globaux et régionaux pour les taux de positivité, d'hospitalisation et de mortalité.
  - Personnalisez les alertes selon vos besoins de surveillance.
- **Dashboard interactif** :
  - Visualisez les statistiques actuelles (taux de positivité, hospitalisation, mortalité, alertes actives).
  - Accédez à des graphiques et indicateurs dynamiques.
- **Exploration et mise à jour des données** :
  - Importez et mettez à jour les données de surveillance.
  - Explorez les données historiques et les tendances.
- **Gestion des alertes** :
  - Vérifiez les alertes en temps réel selon les seuils configurés.
  - Consultez l'historique des alertes et les logs du système.
- **Export/Import de configuration** :
  - Exportez ou importez facilement la configuration des seuils d'alerte.
- **Documentation intégrée** :
  - Accédez à la documentation et au guide d'utilisation depuis l'interface.

## Technologies utilisées

- **Backend** : FastAPI, SQLAlchemy, Pydantic
- **Frontend** : HTML5, CSS3 (Bootstrap), JavaScript
- **Données** : Pandas, Numpy, Faker (pour la simulation)
- **Planification** : Schedule
- **Templates** : Jinja2

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/VOTRE-UTILISATEUR/NOM-DU-DEPOT.git
   cd NOM-DU-DEPOT
   ```
2. Créez un environnement virtuel et activez-le :
   ```bash
   python -m venv venv
   # Sur Windows
   venv\Scripts\activate
   # Sur Mac/Linux
   source venv/bin/activate
   ```
3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Lancez l'application :
   ```bash
   uvicorn main:app --reload
   ```

## Structure du projet

- `main.py` : Point d'entrée de l'application FastAPI
- `schemas/` : Schémas Pydantic, modèles SQLAlchemy, utilitaires
- `scripts/` : Scripts de planification, de simulation et de test des alertes
- `templates/` : Templates HTML pour l'interface utilisateur
- `static/` : Fichiers statiques (CSS, JS, images)
- `logs/` : Logs des alertes et du système
- `data_nettoyee/` : Données nettoyées

## Contribution

Les contributions sont les bienvenues ! Merci de soumettre vos issues et pull requests pour améliorer le projet.

## Licence

Ce projet est sous licence MIT.








