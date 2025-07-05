# Pagination - Page Exploration des Données

## Vue d'ensemble

La fonctionnalité de pagination a été ajoutée à la page d'exploration des données pour améliorer l'expérience utilisateur lors de la consultation de grands volumes de données épidémiologiques. Cette fonctionnalité permet une navigation fluide et efficace à travers les résultats de recherche.

## Fonctionnalités de Pagination

### 🔢 Contrôles de Pagination

#### **Paramètres de Pagination**
- **Page Size** : Nombre d'éléments par page (10, 25, 50, 100)
- **Page** : Numéro de page actuelle
- **Limit** : Limite totale de données à récupérer
- **Navigation** : Boutons Précédent/Suivant

#### **Interface Utilisateur**
- **Boutons de navigation** : Précédent/Suivant avec états désactivés
- **Numéros de pages** : Affichage des pages avec pagination intelligente
- **Indicateurs visuels** : Page active mise en évidence
- **Saut de page** : Champ de saisie pour aller directement à une page
- **Informations contextuelles** : Affichage du nombre d'éléments et de la page courante

### 🎨 Design et UX

#### **Style Moderne**
- Boutons avec effets de survol et transitions fluides
- États visuels clairs (actif, désactivé, survol)
- Couleurs cohérentes avec le thème de l'application
- Responsive design pour mobile et desktop

#### **Navigation Intelligente**
- Affichage des pages autour de la page courante (±2 pages)
- Boutons "Première page" et "Dernière page" quand nécessaire
- Indicateurs "..." pour les longues séquences de pages
- Gestion automatique des états désactivés

## Architecture Technique

### Backend (FastAPI)

#### **Route `/affichage-donnees`**
```python
@app.post("/affichage-donnees")
async def affichage_donnees(
    date_debut: str = Form(...),
    date_fin: str = Form(...),
    region: str = Form("Toutes"),
    limit: int = Form(100),
    page_size: int = Form(25),
    page: int = Form(1),
    db: Session = Depends(get_db)
):
```

#### **Logique de Pagination**
```python
# Calcul de l'offset
offset = (page - 1) * page_size

# Récupération des données paginées
donnees = query.offset(offset).limit(page_size).all()

# Calcul des informations de pagination
total_pages = min((total_count + page_size - 1) // page_size, 
                  (limit + page_size - 1) // page_size)
```

#### **Structure de Données de Pagination**
```python
pagination = {
    "current_page": page,
    "total_pages": total_pages,
    "total_count": total_count,
    "start_record": offset + 1,
    "end_record": min(offset + page_size, total_count, limit),
    "page_size": page_size,
    "links": pagination_links,
    "prev_page": prev_page,
    "next_page": next_page,
    "has_prev": page > 1,
    "has_next": page < total_pages
}
```

### Frontend (HTML/JavaScript)

#### **Template Jinja2**
```html
<!-- Pagination Controls -->
<div class="pagination-controls">
    <button class="btn-pagination" onclick="changePage({{ pagination.prev_page }})" 
            {% if not pagination.has_prev %}disabled{% endif %}>
        <i class="fas fa-chevron-left"></i> Précédent
    </button>
    
    <!-- Pages around current -->
    {% for link in pagination.links %}
    <button class="btn-pagination {% if link.active %}active{% endif %}" 
            onclick="changePage({{ link.page }})">
        {{ link.page }}
    </button>
    {% endfor %}
    
    <button class="btn-pagination" onclick="changePage({{ pagination.next_page }})" 
            {% if not pagination.has_next %}disabled{% endif %}>
        Suivant <i class="fas fa-chevron-right"></i>
    </button>
</div>
```

#### **JavaScript Functions**
```javascript
// Navigation entre pages
function changePage(page) {
    if (page < 1) return;
    document.getElementById('page').value = page;
    document.getElementById('searchForm').submit();
}

// Saut direct vers une page
function jumpToPage() {
    const pageInput = document.getElementById('jump-to-page');
    const page = parseInt(pageInput.value);
    if (page && page > 0) {
        changePage(page);
    }
}
```

## Utilisation

### 1. Configuration des Paramètres
1. **Sélectionnez la taille de page** : 10, 25, 50 ou 100 éléments
2. **Définissez la limite totale** : Nombre maximum de données à récupérer
3. **Choisissez la page** : Numéro de page de départ

### 2. Navigation
- **Boutons Précédent/Suivant** : Navigation séquentielle
- **Numéros de pages** : Clic direct sur une page
- **Champ de saut** : Saisie directe du numéro de page
- **Touches clavier** : Entrée pour valider le saut de page

### 3. Informations Affichées
- **Plage d'éléments** : "Affichage de X à Y sur Z résultats"
- **Page courante** : "Page X sur Y"
- **Nombre de colonnes** : Informations sur la structure des données
- **Période** : Dates de début et fin de la recherche

## Fonctionnalités Avancées

### 🔄 Synchronisation Automatique
- **Changement de page_size** : Retour automatique à la page 1
- **Nouvelle recherche** : Réinitialisation de la pagination
- **Validation des paramètres** : Contrôles de cohérence

### 📊 Intégration avec les Exports
- **Exports paginés** : Possibilité d'exporter une page spécifique
- **Paramètres préservés** : Les filtres de pagination sont inclus dans les exports
- **Formats supportés** : JSON, CSV, Excel avec pagination

### 🎯 Optimisations de Performance
- **Requêtes optimisées** : Utilisation d'OFFSET et LIMIT en SQL
- **Chargement progressif** : Affichage des données par pages
- **Cache intelligent** : Réutilisation des données quand possible

## Tests et Validation

### Script de Test
Le fichier `test_pagination.py` permet de valider :
- ✅ Accès à la page exploration
- ✅ Recherche avec pagination
- ✅ Navigation entre pages
- ✅ Paramètres de pagination
- ✅ Exports avec pagination

### Exécution des Tests
```bash
python test_pagination.py
```

## Maintenance et Évolutions

### 🔧 Améliorations Futures
- **Pagination AJAX** : Navigation sans rechargement de page
- **Pagination infinie** : Chargement automatique au scroll
- **Filtres persistants** : Sauvegarde des paramètres de pagination
- **Export de pages multiples** : Sélection de plages de pages

### 🐛 Dépannage
- **Page vide** : Vérifier les paramètres de recherche
- **Navigation bloquée** : Contrôler les valeurs de page et page_size
- **Performance lente** : Optimiser les requêtes avec des index

## Intégration avec le Système

### 🔗 Compatibilité
- **Backend existant** : Utilise les routes et modèles existants
- **Frontend cohérent** : Style et comportement uniformes
- **API REST** : Endpoints compatibles avec les clients existants

### 📈 Métriques
- **Temps de réponse** : Mesure des performances de pagination
- **Utilisation** : Statistiques d'utilisation des fonctionnalités
- **Erreurs** : Monitoring des problèmes de pagination

---

**Version** : 1.0  
**Date** : 2024  
**Auteur** : Système de Surveillance Épidémiologique 