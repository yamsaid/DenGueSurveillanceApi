# Système Intelligent de Surveillance, Prédiction et Alerte Dengue ( SIS-PAD )

Ce projet est une application web de surveillance épidémiologique intelligente dédiée à la dengue.
Elle combine des méthodes classiques de surveillance sanitaire avec des techniques de machine learning
afin de détecter précocement les flambées épidémiques, anticiper les risques et soutenir la prise de décision
en santé publique, notamment dans les contextes à ressources limitées comme le Burkina Faso.

## Objectifs

- Surveiller en temps réel les indicateurs clés de la dengue
- Détecter automatiquement des anomalies épidémiologiques
- Prédire l’évolution future des cas et des indicateurs
- Générer des alertes intelligentes basées sur des seuils dynamiques
- Aider à la priorisation des interventions sanitaires

## Fonctionnalités principales

### Surveillance épidémiologique classique
- Configuration de seuils d’alerte globaux et régionaux
- Suivi des taux de positivité, hospitalisation et mortalité
- Tableaux de bord interactifs et historiques

### Intelligence artificielle et Machine Learning
- **Prédiction des cas de dengue** à court et moyen terme
- **Détection d’anomalies** et de signaux faibles dans les données
- **Seuils d’alerte adaptatifs** par district sanitaire
- **Score de risque dengue** par zone géographique
- Simulation de scénarios épidémiologiques

### Gestion et exploitation des données
- Importation et nettoyage des données
- Exploration des tendances temporelles
- Export des résultats pour analyses externes

## Technologies utilisées

- Backend : FastAPI, SQLAlchemy, Pydantic
- Data & ML : Pandas, NumPy, Scikit-learn, Statsmodels
- Frontend : HTML5, CSS3 (Bootstrap), JavaScript
- Visualisation : Chart.js
- Planification : Schedule
- Templates : Jinja2

## Cas d’usage

- Systèmes nationaux de surveillance épidémiologique
- Directions régionales de la santé
- ONG et partenaires techniques
- Projets de recherche en santé publique
