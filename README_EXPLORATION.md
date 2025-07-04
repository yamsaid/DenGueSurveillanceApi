# Page d'Exploration des Données Épidémiologiques

## Vue d'ensemble

La page d'exploration des données épidémiologiques est une interface moderne et interactive permettant aux utilisateurs d'explorer, filtrer et analyser les données de surveillance de la dengue. Cette page offre une expérience utilisateur fluide avec des fonctionnalités avancées de filtrage, d'export et de visualisation.

## Fonctionnalités principales

### 🔍 Interface de filtrage avancée
- **Sélecteur de période** : Date de début et fin avec validation automatique
- **Filtre par région** : Dropdown dynamique avec toutes les régions disponibles
- **Filtre par district** : Dropdown dynamique selon la région sélectionnée
- **Limite de données** : Contrôle du nombre maximum d'enregistrements à récupérer
- **Limite d'affichage** : Pagination personnalisable (10, 25, 50, 100 éléments par page)

### 📊 Tableau de données interactif
- **Colonnes affichées** : ID, Date consultation, Région, District, Sexe, Âge, Résultat test, Sérotype, Hospitalisé, Issue
- **Tri intelligent** : Tri par colonnes (ascendant/descendant)
- **Recherche globale** : Recherche dans toutes les colonnes
- **Pagination** : Navigation fluide avec sélection du nombre d'éléments
- **Indicateurs visuels** : Badges colorés pour les statuts et résultats

### 📈 Statistiques en temps réel
- **Total des cas** : Nombre total d'enregistrements
- **Cas positifs** : Nombre de cas confirmés positifs
- **Hospitalisés** : Nombre de cas hospitalisés
- **Décès** : Nombre de cas décédés
- **Calculs automatiques** : Taux de positivité, d'hospitalisation et de mortalité

### 📤 Options d'export
- **Format JSON** : Export en format JSON structuré
- **Format CSV** : Export en format CSV compatible Excel
- **Format Excel** : Export direct en format XLSX
- **Nommage intelligent** : Fichiers nommés avec date et filtres appliqués

## Architecture technique

### Frontend
- **HTML5** : Structure sémantique et accessible
- **CSS3** : Styles modernes avec Flexbox/Grid
- **JavaScript ES6+** : Fonctionnalités interactives
- **Bootstrap 5** : Framework CSS responsive
- **DataTables** : Tableau interactif avec pagination
- **Flatpickr** : Sélecteur de dates moderne

### Backend
- **FastAPI** : API REST performante
- **SQLAlchemy** : ORM pour la base de données
- **Pandas** : Manipulation des données
- **Jinja2** : Moteur de templates

### Fichiers principaux
```
templates/
├── exploration.html          # Template principal
static/
├── assets/
│   ├── css/
│   │   └── exploration.css   # Styles personnalisés
│   └── js/
│       └── exploration.js    # Logique JavaScript
main.py                       # Routes et API
```

## Utilisation

### 1. Accès à la page
- Naviguez vers `/exploration` dans l'application
- La page se charge avec les filtres par défaut (30 derniers jours)

### 2. Configuration des filtres
1. **Période** : Sélectionnez les dates de début et fin
2. **Région** : Choisissez une région spécifique ou "Toutes"
3. **District** : Sélectionnez un district (se charge selon la région)
4. **Limites** : Définissez le nombre max de données et d'éléments par page
5. **Appliquer** : Cliquez sur "Appliquer les filtres"

### 3. Exploration des données
- **Recherche** : Utilisez la barre de recherche pour filtrer
- **Tri** : Cliquez sur les en-têtes de colonnes pour trier
- **Pagination** : Naviguez entre les pages
- **Statistiques** : Consultez les métriques en temps réel

### 4. Export des données
- **Sélection du format** : Choisissez JSON, CSV ou Excel
- **Téléchargement** : Le fichier se télécharge automatiquement
- **Nommage** : Le fichier inclut la date et les filtres appliqués

## Fonctionnalités avancées

### 🎨 Design moderne
- **Gradients colorés** : Interface visuellement attrayante
- **Animations fluides** : Transitions et effets visuels
- **Responsive design** : Adaptation mobile, tablette et desktop
- **Mode sombre/clair** : Thème adaptable

### ⚡ Performance optimisée
- **Lazy loading** : Chargement progressif des données
- **Pagination côté serveur** : Gestion efficace de grandes quantités
- **Cache intelligent** : Mise en cache des requêtes fréquentes
- **Validation côté client** : Réduction des requêtes serveur

### 🔧 Personnalisation
- **Filtres sauvegardés** : Mémorisation des derniers filtres utilisés
- **Préférences utilisateur** : Configuration des éléments par page
- **Raccourcis clavier** : Ctrl+R (rafraîchir), Ctrl+E (exporter)
- **Notifications** : Messages d'état et d'erreur élégants

## API Endpoints

### GET `/exploration`
Affiche la page d'exploration avec les filtres par défaut.

### POST `/affichage-donnees`
Récupère les données filtrées selon les critères fournis.

**Paramètres :**
- `date_debut` : Date de début (YYYY-MM-DD)
- `date_fin` : Date de fin (YYYY-MM-DD)
- `region` : Région à filtrer
- `districts` : Districts à filtrer (optionnel)
- `limit` : Limite de données
- `page_size` : Éléments par page

### GET `/export-data`
Exporte les données dans le format demandé.

**Paramètres :**
- `format` : json, csv, ou excel
- `date_debut` : Date de début
- `date_fin` : Date de fin
- `region` : Région à filtrer
- `districts` : Districts à filtrer
- `limit` : Limite de données

### GET `/api/regions`
Récupère la liste des régions disponibles.

### GET `/api/districts`
Récupère la liste des districts pour une région donnée.

## Sécurité et validation

### Validation des données
- **Dates** : Validation du format et de la cohérence
- **Limites** : Contrôle des valeurs numériques
- **Régions/Districts** : Validation de l'existence
- **Injection SQL** : Protection via SQLAlchemy

### Gestion des erreurs
- **Messages d'erreur** : Notifications claires et informatives
- **Fallbacks** : Valeurs par défaut en cas d'erreur
- **Logging** : Traçabilité des erreurs
- **Recovery** : Récupération automatique des sessions

## Maintenance et évolutions

### Ajouts futurs possibles
- **Graphiques interactifs** : Visualisations Chart.js ou D3.js
- **Filtres avancés** : Par âge, sexe, serotype
- **Sauvegarde des requêtes** : Historique des recherches
- **Export programmé** : Export automatique périodique
- **Notifications push** : Alertes en temps réel
- **Mode hors ligne** : Cache local pour consultation offline

### Optimisations
- **Indexation base de données** : Amélioration des performances
- **Compression des données** : Réduction de la bande passante
- **CDN** : Distribution des assets statiques
- **Cache Redis** : Mise en cache des requêtes fréquentes

## Support et documentation

### Développement
- **Code source** : Commenté et documenté
- **Tests unitaires** : Couverture de test complète
- **Documentation API** : Swagger/OpenAPI
- **Versioning** : Gestion des versions

### Utilisation
- **Guide utilisateur** : Documentation complète
- **Vidéos tutorielles** : Démonstrations interactives
- **FAQ** : Questions fréquentes
- **Support technique** : Assistance utilisateur

---

*Cette page d'exploration représente une solution complète et moderne pour l'analyse des données épidémiologiques, offrant une expérience utilisateur exceptionnelle tout en maintenant des performances optimales.* 