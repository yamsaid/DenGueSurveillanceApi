# Guide d'Utilisation - Page Indicateurs

## 🚀 Accès Rapide

### URLs d'accès
- **Page principale** : `http://localhost:8000/page-indicateurs`
- **Page PowerBI** : `http://localhost:8000/dashboard/indicateurs-powerbi`

### Navigation depuis le dashboard
- Cliquez sur "Indicateurs" dans le menu de navigation
- Ou utilisez le bouton "Indicateurs détaillés" dans la section actions

## 📊 Fonctionnalités Disponibles

### 1. Métriques Rapides
La page affiche automatiquement :
- **Cas totaux** : Nombre total de cas enregistrés
- **Cas positifs** : Nombre de cas confirmés positifs
- **Hospitalisations** : Nombre de cas hospitalisés
- **Décès** : Nombre de décès liés à la dengue

Chaque métrique inclut :
- Valeur actuelle
- Tendance (hausse/baisse en pourcentage)
- Icône visuelle

### 2. Filtres Avancés
- **Période** : 7j, 30j, 90j, 1an, personnalisée
- **Région** : Toutes ou région spécifique
- **District** : Tous ou district spécifique
- **Sérotype** : Tous ou sérotype spécifique (DENV1, DENV2, DENV3, DENV4)

### 3. Intégration PowerBI
- **Rapport intégré** : Affichage du rapport PowerBI
- **Contrôles** : Plein écran, actualisation
- **Responsive** : Adaptation automatique à la taille d'écran

### 4. Actions Disponibles
- **Actualiser** : Recharger les données
- **Export PDF** : Télécharger en PDF
- **Export Excel** : Télécharger en Excel
- **Partager** : Générer un lien de partage
- **Mode sombre** : Basculer le thème
- **Imprimer** : Mode impression optimisé

## 🎯 Utilisation Pas à Pas

### Étape 1 : Accéder à la page
1. Ouvrez votre navigateur
2. Allez sur `http://localhost:8000/page-indicateurs`
3. Attendez le chargement complet

### Étape 2 : Consulter les métriques
1. Regardez les cartes de métriques en haut
2. Notez les tendances (flèches vertes/rouges)
3. Identifiez les alertes potentielles

### Étape 3 : Appliquer des filtres
1. Sélectionnez une période dans le menu déroulant
2. Choisissez une région si nécessaire
3. Sélectionnez un district si applicable
4. Cliquez sur "Appliquer les filtres"

### Étape 4 : Analyser le rapport PowerBI
1. Faites défiler vers la section PowerBI
2. Interagissez avec les graphiques
3. Utilisez les contrôles PowerBI intégrés
4. Passez en plein écran si nécessaire

### Étape 5 : Exporter ou partager
1. Cliquez sur "Export PDF" ou "Export Excel"
2. Ou utilisez "Partager" pour générer un lien
3. Ou cliquez sur "Imprimer" pour l'impression

## ⌨️ Raccourcis Clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl/Cmd + R` | Actualiser les données |
| `Ctrl/Cmd + E` | Export PDF |
| `Ctrl/Cmd + S` | Sauvegarder les filtres |
| `F11` | Plein écran |
| `Echap` | Quitter le plein écran |

## 🔧 Configuration PowerBI

### Pour configurer PowerBI :
1. Modifiez le fichier `static/assets/js/page-indicateurs.js`
2. Remplacez les valeurs dans `CONFIG.powerBI` :
```javascript
const CONFIG = {
    powerBI: {
        reportId: 'VOTRE_REPORT_ID',
        embedUrl: 'VOTRE_EMBED_URL',
        accessToken: 'VOTRE_ACCESS_TOKEN',
        workspaceId: 'VOTRE_WORKSPACE_ID'
    }
};
```

### Obtenir les informations PowerBI :
1. Connectez-vous à [PowerBI.com](https://powerbi.com)
2. Ouvrez votre rapport
3. Cliquez sur "Partager" > "Intégrer"
4. Copiez l'ID du rapport et l'URL d'embed

## 🐛 Dépannage

### Problème : Page ne se charge pas
**Solution** :
- Vérifiez que le serveur FastAPI est démarré
- Vérifiez l'URL dans le navigateur
- Consultez la console du navigateur (F12)

### Problème : PowerBI ne s'affiche pas
**Solution** :
- Vérifiez la configuration PowerBI
- Assurez-vous que le token d'accès est valide
- Vérifiez les permissions du rapport

### Problème : Filtres ne fonctionnent pas
**Solution** :
- Vérifiez que les endpoints API fonctionnent
- Consultez les logs du serveur
- Vérifiez la console du navigateur

### Problème : Export ne fonctionne pas
**Solution** :
- Vérifiez que le rapport PowerBI est chargé
- Assurez-vous d'avoir les permissions d'export
- Vérifiez la configuration PowerBI

## 📱 Utilisation Mobile

La page est entièrement responsive :
- **Navigation** : Menu hamburger sur mobile
- **Filtres** : Empilés verticalement
- **Métriques** : Une colonne sur mobile
- **PowerBI** : Adaptation automatique

## 🔒 Sécurité

### Bonnes pratiques :
- Utilisez HTTPS en production
- Configurez l'authentification si nécessaire
- Limitez l'accès aux utilisateurs autorisés
- Surveillez les logs d'accès

### Configuration sécurisée :
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

## 📞 Support

En cas de problème :
1. Consultez ce guide
2. Vérifiez les logs d'erreur
3. Testez avec le script `test_page_indicateurs.py`
4. Contactez l'équipe de développement

## 📈 Évolutions Futures

Fonctionnalités prévues :
- [ ] Notifications en temps réel
- [ ] Alertes automatiques
- [ ] Comparaisons inter-régionales
- [ ] Prédictions épidémiologiques
- [ ] Intégration de données externes
- [ ] API REST complète
- [ ] Authentification utilisateur
- [ ] Gestion des rôles et permissions 