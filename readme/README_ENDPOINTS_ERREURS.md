# Endpoints d'Analyse d'Erreurs

Ce document décrit les nouveaux endpoints créés pour afficher les erreurs par colonnes et par types lors de l'analyse d'un fichier CSV.

## 📋 Vue d'ensemble

Les endpoints permettent de :
- Analyser les erreurs détectées lors de l'analyse d'un fichier CSV
- Afficher les erreurs par colonnes
- Afficher les erreurs par types
- Fournir des données pour les graphiques de visualisation

## 🔗 Endpoints disponibles

### 1. `/rapport/erreurs-analyse`

**Méthode :** GET  
**Description :** Endpoint principal pour obtenir l'analyse complète des erreurs

**Réponse :**
```json
{
  "message": "Analyse des erreurs par colonnes et par types",
  "rapport_complet": {...},
  "erreurs_par_colonnes": {
    "date_consultation": {
      "total_erreurs": 5,
      "types_erreurs": {
        "valeurs_invalides": 5
      },
      "details": {
        "valeurs_invalides": 5
      }
    },
    "age": {
      "total_erreurs": 3,
      "types_erreurs": {
        "valeurs_hors_plage": 2,
        "valeurs_non_numeriques": 1
      },
      "details": {
        "valeurs_hors_plage": 2,
        "valeurs_non_numeriques": 1
      }
    }
  },
  "erreurs_par_types": {
    "valeurs_invalides": 8,
    "valeurs_manquantes": 2,
    "valeurs_hors_plage": 3,
    "valeurs_non_numeriques": 1,
    "total_erreurs": 14
  },
  "resume": {
    "nombre_colonnes_avec_erreurs": 2,
    "total_erreurs": 14,
    "colonne_plus_erreurs": "date_consultation",
    "type_erreur_plus_frequent": "valeurs_invalides"
  }
}
```

### 2. `/rapport/nb-erreurs-col`

**Méthode :** GET  
**Description :** Endpoint pour obtenir le nombre d'erreurs par colonne (utilisé pour les graphiques)

**Réponse :**
```json
{
  "labels": ["date_consultation", "age", "resultat_test"],
  "data": [5, 3, 2],
  "total_erreurs": 10,
  "resume": {
    "nombre_colonnes_avec_erreurs": 3,
    "total_erreurs": 10,
    "colonne_plus_erreurs": "date_consultation",
    "type_erreur_plus_frequent": "valeurs_invalides"
  }
}
```

### 3. `/rapport/erreurs-par-types`

**Méthode :** GET  
**Description :** Endpoint pour obtenir les erreurs par types (utilisé pour les graphiques)

**Réponse :**
```json
{
  "labels": ["Valeurs Invalides", "Valeurs Manquantes", "Valeurs Hors Plage"],
  "data": [8, 2, 3],
  "total_erreurs": 13,
  "resume": {
    "nombre_colonnes_avec_erreurs": 3,
    "total_erreurs": 13,
    "colonne_plus_erreurs": "date_consultation",
    "type_erreur_plus_frequent": "valeurs_invalides"
  }
}
```

## 🔧 Utilisation

### 1. Analyser un fichier

```bash
# Envoyer un fichier CSV pour analyse
curl -X POST "http://localhost:8000/analyse" \
  -F "file=@mon_fichier.csv" \
  -F "corriger=true"
```

### 2. Obtenir l'analyse des erreurs

```bash
# Obtenir l'analyse complète
curl "http://localhost:8000/rapport/erreurs-analyse"

# Obtenir les erreurs par colonnes
curl "http://localhost:8000/rapport/nb-erreurs-col"

# Obtenir les erreurs par types
curl "http://localhost:8000/rapport/erreurs-par-types"
```

### 3. Utilisation en JavaScript

```javascript
// Charger les données d'erreurs
async function loadErrorData() {
    try {
        // Récupérer les erreurs par colonnes
        const responseColonnes = await fetch('/rapport/nb-erreurs-col');
        const dataColonnes = await responseColonnes.json();
        
        // Récupérer les erreurs par types
        const responseTypes = await fetch('/rapport/erreurs-par-types');
        const dataTypes = await responseTypes.json();
        
        // Mettre à jour les graphiques
        updateErrorCharts(dataColonnes, dataTypes);
        
    } catch (error) {
        console.error('Erreur lors du chargement des données:', error);
    }
}
```

## 📊 Types d'erreurs détectées

### Erreurs de format
- **valeurs_invalides** : Valeurs qui ne respectent pas le format attendu
- **valeurs_manquantes** : Valeurs manquantes (null, NaN, etc.)
- **valeurs_hors_plage** : Valeurs numériques hors de la plage valide
- **valeurs_non_numeriques** : Valeurs non numériques dans des colonnes numériques

### Colonnes analysées
- **date_consultation** : Format de date
- **age** : Valeur numérique entre 0 et 120
- **sexe** : Valeurs valides (Homme, Femme)
- **resultat_test** : Valeurs valides (Positif, Négatif)
- **serotype** : Valeurs valides (DENV2, DENV3)
- **hospitalise** : Valeurs valides (Oui, Non)
- **issue** : Valeurs valides (Guéri, En traitement, Décédé, Inconnue)

## 🧪 Tests

Pour tester les endpoints, utilisez le fichier `test_erreurs_analyse.py` :

```bash
python test_erreurs_analyse.py
```

Ce script va :
1. Créer un fichier CSV de test avec des erreurs
2. L'envoyer pour analyse
3. Tester tous les endpoints
4. Afficher les résultats

## 🔄 Intégration avec l'interface

Les endpoints sont automatiquement utilisés par l'interface web dans `templates/rapport-Form.html`. Les graphiques se mettent à jour automatiquement avec les vraies données d'erreurs au lieu des données statiques.

## 📝 Notes techniques

- Les endpoints utilisent la variable globale `rapport` qui contient les résultats de la dernière analyse
- Si aucun rapport n'est disponible, les endpoints retournent un message d'erreur approprié
- Les données sont formatées pour être directement utilisables par Chart.js
- La fonction `analyser_erreurs_par_colonnes_et_types()` dans `utils.py` fait l'analyse principale

## 🚀 Déploiement

Les endpoints sont automatiquement disponibles une fois le serveur FastAPI démarré :

```bash
uvicorn main:app --reload
```

Accédez ensuite aux endpoints via :
- http://localhost:8000/rapport/erreurs-analyse
- http://localhost:8000/rapport/nb-erreurs-col
- http://localhost:8000/rapport/erreurs-par-types 