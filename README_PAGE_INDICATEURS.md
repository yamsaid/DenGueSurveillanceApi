# Page Indicateurs avec PowerBI - Documentation

## Vue d'ensemble

La page d'indicateurs est une interface moderne et professionnelle pour afficher les rapports PowerBI intégrés dans le système de surveillance de la dengue. Elle offre une expérience utilisateur exceptionnelle avec des filtres avancés, des métriques rapides et des fonctionnalités d'export.

## Fonctionnalités

### 🎯 Fonctionnalités Principales
- **Intégration PowerBI** : Affichage fluide des rapports PowerBI
- **Filtres Avancés** : Période, région, district, sérotype
- **Métriques Rapides** : KPIs principaux avec tendances
- **Export Multiple** : PDF, Excel, impression
- **Partage** : Partage de vues spécifiques
- **Mode Sombre** : Thème sombre optionnel
- **Responsive** : Adaptation mobile-first

### 🔧 Fonctionnalités Techniques
- **Gestion d'État** : Système robuste de gestion des filtres
- **Persistance** : Sauvegarde des préférences utilisateur
- **Raccourcis Clavier** : Navigation au clavier
- **Gestion d'Erreurs** : Gestion robuste des erreurs
- **Performance** : Optimisation du rendu

## Configuration

### 1. Configuration PowerBI

Avant d'utiliser la page, vous devez configurer l'intégration PowerBI :

#### Étape 1 : Créer un rapport PowerBI
1. Connectez-vous à [PowerBI.com](https://powerbi.com)
2. Créez ou uploadez votre rapport de surveillance dengue
3. Notez l'ID du rapport et l'URL d'embed

#### Étape 2 : Configurer l'authentification
```javascript
// Dans static/assets/js/page-indicateurs.js
const CONFIG = {
    powerBI: {
        reportId: 'VOTRE_REPORT_ID',
        embedUrl: 'VOTRE_EMBED_URL',
        accessToken: 'VOTRE_ACCESS_TOKEN',
        workspaceId: 'VOTRE_WORKSPACE_ID'
    }
};
```

#### Étape 3 : Obtenir un token d'accès
```python
# Exemple de génération de token (à adapter selon votre setup)
import msal

def get_powerbi_token():
    app = msal.ConfidentialClientApplication(
        client_id="VOTRE_CLIENT_ID",
        client_credential="VOTRE_CLIENT_SECRET",
        authority="https://login.microsoftonline.com/VOTRE_TENANT_ID"
    )
    
    result = app.acquire_token_for_client(scopes=["https://analysis.windows.net/powerbi/api/.default"])
    return result['access_token']
```

### 2. Configuration des Endpoints API

La page utilise plusieurs endpoints API qui doivent être configurés :

#### Endpoints Requis
- `GET /api/stats` - Statistiques générales
- `GET /api/regions` - Liste des régions
- `GET /api/districts` - Liste des districts
- `GET /api/data/hebdomadaires` - Données hebdomadaires
- `GET /api/data/mensuels` - Données mensuelles

#### Exemple de Configuration
```python
# Dans main.py
@app.get("/api/stats")
async def get_stats_api(db: Session = Depends(get_db)):
    return utils.get_stats(db)

@app.get("/api/regions")
def get_regions(db: Session = Depends(get_db)):
    regions = utils.recuperer_regions_distinctes(db)
    return regions

@app.get("/api/districts")
def get_districts(region: str = Query(None), db: Session = Depends(get_db)):
    # Logique pour récupérer les districts
    pass
```

## Utilisation

### 1. Accès à la Page
```
URL: http://votre-domaine/page-indicateurs
```

### 2. Navigation
- **Breadcrumb** : Navigation contextuelle
- **Filtres** : Sélection de période et géographie
- **Actions** : Export, partage, actualisation

### 3. Filtres Disponibles
- **Période** : 7j, 30j, 90j, 1an, personnalisée
- **Région** : Toutes ou région spécifique
- **District** : Tous ou district spécifique
- **Sérotype** : Tous ou sérotype spécifique

### 4. Actions Disponibles
- **Actualiser** : Recharger les données
- **Export PDF** : Télécharger en PDF
- **Export Excel** : Télécharger en Excel
- **Partager** : Générer un lien de partage
- **Mode Sombre** : Basculer le thème

## Raccourcis Clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl/Cmd + R` | Actualiser les données |
| `Ctrl/Cmd + E` | Export PDF |
| `Ctrl/Cmd + S` | Sauvegarder les filtres |
| `F11` | Plein écran |
| `Echap` | Quitter le plein écran |

## Structure des Fichiers

```
templates/
├── page-indicateurs.html          # Template principal
static/
├── assets/
│   ├── css/
│   │   └── page-indicateurs.css   # Styles CSS
│   └── js/
│       └── page-indicateurs.js    # Logique JavaScript
main.py                            # Routes et endpoints
```

## Personnalisation

### 1. Couleurs et Thème
Modifiez les variables CSS dans `page-indicateurs.css` :

```css
:root {
    --primary-color: #2563eb;      /* Couleur principale */
    --secondary-color: #64748b;    /* Couleur secondaire */
    --accent-color: #10b981;       /* Couleur d'accent */
    --warning-color: #f59e0b;      /* Couleur d'alerte */
    --danger-color: #ef4444;       /* Couleur de danger */
}
```

### 2. Métriques Personnalisées
Ajoutez de nouvelles métriques dans le HTML et JavaScript :

```html
<!-- Dans page-indicateurs.html -->
<div class="stat-card">
    <div class="stat-card-body">
        <div class="stat-icon bg-info">
            <i class="fas fa-chart-line"></i>
        </div>
        <div class="stat-content">
            <h3 class="stat-value" id="new-metric">-</h3>
            <p class="stat-label">Nouvelle Métrique</p>
        </div>
    </div>
</div>
```

```javascript
// Dans page-indicateurs.js
function updateNewMetric(value) {
    updateMetric('new-metric', value);
}
```

### 3. Filtres Personnalisés
Ajoutez de nouveaux filtres :

```html
<!-- Nouveau filtre -->
<div class="col-lg-3 col-md-6">
    <label for="new-filter" class="form-label">
        <i class="fas fa-filter"></i> Nouveau Filtre
    </label>
    <select class="form-select" id="new-filter">
        <option value="all">Toutes les options</option>
        <option value="option1">Option 1</option>
        <option value="option2">Option 2</option>
    </select>
</div>
```

## Dépannage

### Problèmes Courants

#### 1. PowerBI ne se charge pas
- Vérifiez la configuration PowerBI dans `page-indicateurs.js`
- Assurez-vous que le token d'accès est valide
- Vérifiez les permissions du rapport

#### 2. Les filtres ne fonctionnent pas
- Vérifiez que les endpoints API sont correctement configurés
- Assurez-vous que la base de données contient des données
- Vérifiez les logs d'erreur dans la console

#### 3. Problèmes de performance
- Optimisez les requêtes de base de données
- Utilisez la pagination pour les grandes quantités de données
- Mettez en cache les données statiques

### Logs et Debugging

Activez le mode debug dans le navigateur :
```javascript
// Dans la console du navigateur
localStorage.setItem('debug', 'true');
```

Vérifiez les logs dans :
- Console du navigateur (F12)
- Logs du serveur FastAPI
- Logs de la base de données

## Sécurité

### Bonnes Pratiques
1. **Authentification** : Utilisez des tokens d'accès sécurisés
2. **Autorisation** : Vérifiez les permissions utilisateur
3. **Validation** : Validez toutes les entrées utilisateur
4. **HTTPS** : Utilisez HTTPS en production
5. **CORS** : Configurez CORS correctement

### Configuration Sécurisée
```python
# Dans main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://votre-domaine.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Performance

### Optimisations Recommandées
1. **Mise en cache** : Cachez les données statiques
2. **Lazy Loading** : Chargez les données à la demande
3. **Compression** : Activez la compression gzip
4. **CDN** : Utilisez un CDN pour les assets statiques
5. **Base de données** : Optimisez les requêtes SQL

### Monitoring
- Surveillez les temps de réponse
- Surveillez l'utilisation mémoire
- Surveillez les erreurs utilisateur
- Surveillez les performances PowerBI

## Support

Pour obtenir de l'aide :
1. Consultez cette documentation
2. Vérifiez les logs d'erreur
3. Testez avec des données minimales
4. Contactez l'équipe de développement

## Changelog

### Version 1.0.0
- ✅ Page d'indicateurs initiale
- ✅ Intégration PowerBI
- ✅ Filtres avancés
- ✅ Export PDF/Excel
- ✅ Mode sombre
- ✅ Responsive design 