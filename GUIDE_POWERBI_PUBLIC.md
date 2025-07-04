# 🔧 Guide Configuration PowerBI - Mode Public (Essai Gratuit)

## 📋 Prérequis

- Un compte PowerBI gratuit
- Un rapport PowerBI publié
- Le lien public du rapport

## 🚀 Configuration Rapide

### Étape 1 : Obtenir le lien public

1. **Connectez-vous à PowerBI.com**
   - Allez sur [powerbi.com](https://powerbi.com)
   - Connectez-vous avec votre compte Microsoft

2. **Ouvrez votre rapport**
   - Trouvez votre rapport dans "Espace de travail"
   - Cliquez dessus pour l'ouvrir

3. **Générez le lien public**
   - Cliquez sur **"Partager"** (en haut à droite)
   - Sélectionnez **"Publier sur le web"**
   - Cliquez sur **"Créer un lien public"**
   - Copiez le lien généré

### Étape 2 : Configurer l'application

1. **Ouvrez le fichier** `static/assets/js/page-indicateurs.js`

2. **Remplacez l'URL** dans la configuration :
```javascript
powerBI: {
    // Remplacez cette URL par votre lien PowerBI
    publicUrl: 'VOTRE_LIEN_POWERBI_ICI',
    height: 600,
    width: '100%'
},
```

3. **Exemple avec votre lien** :
```javascript
powerBI: {
    publicUrl: 'https://app.powerbi.com/view?r=eyJrIjoiN2QyMzZmYWYtNTllOS00MTNlLWI0NzYtYzNhZTRiNDRmYjIyIiwidCI6IjdmYzlhNjBkLTViMDAtNDdmOS04NDRhLTg2YWI1YzNhNTVmMyJ9&embedImagePlaceholder=true',
    height: 600,
    width: '100%'
},
```

### Étape 3 : Tester

1. **Redémarrez votre serveur FastAPI**
2. **Accédez à** `http://localhost:8000/page-indicateurs`
3. **Vérifiez** que le rapport PowerBI s'affiche

## ✅ Avantages du Mode Public

- ✅ **Configuration simple** : juste une URL
- ✅ **Pas de token** nécessaire
- ✅ **Pas de configuration Azure AD**
- ✅ **Fonctionne immédiatement**
- ✅ **Gratuit**

## ⚠️ Limitations du Mode Public

- ❌ **Pas de sécurité** : tout le monde peut voir le rapport
- ❌ **Pas de filtres dynamiques** via API
- ❌ **Pas d'export programmatique**
- ❌ **Pas d'authentification**

## 🔄 Migration vers PowerBI Pro (Optionnel)

Si vous souhaitez plus de fonctionnalités :

1. **Passez à PowerBI Pro** (abonnement payant)
2. **Configurez Azure AD**
3. **Générez des tokens d'accès**
4. **Utilisez l'intégration avancée**

## 🐛 Dépannage

### Problème : Le rapport ne s'affiche pas
**Solutions :**
- Vérifiez que l'URL est correcte
- Assurez-vous que le rapport est publié
- Vérifiez les permissions du rapport

### Problème : Erreur de chargement
**Solutions :**
- Vérifiez la console du navigateur (F12)
- Assurez-vous que l'URL est accessible
- Vérifiez la connexion internet

### Problème : Rapport vide
**Solutions :**
- Vérifiez que le rapport contient des données
- Assurez-vous que les données sont à jour
- Vérifiez les filtres dans PowerBI

## 📞 Support

En cas de problème :
1. Vérifiez ce guide
2. Consultez la console du navigateur
3. Testez l'URL directement dans un nouvel onglet
4. Contactez l'équipe de développement

---

## 🎉 Configuration Terminée !

Votre page d'indicateurs est maintenant configurée pour afficher votre rapport PowerBI en mode public. 

**URLs d'accès :**
- Page principale : `http://localhost:8000/page-indicateurs`
- Page PowerBI : `http://localhost:8000/dashboard/indicateurs-powerbi`

**Fonctionnalités disponibles :**
- ✅ Affichage du rapport PowerBI
- ✅ Filtres de données
- ✅ Métriques en temps réel
- ✅ Mode sombre
- ✅ Responsive design
- ✅ Partage de liens
- ✅ Ouverture en plein écran 