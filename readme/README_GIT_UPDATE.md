# 🔄 Scripts de mise à jour automatique GitHub

Ce dossier contient des scripts pour automatiser la mise à jour de votre dépôt GitHub.

## 📁 Fichiers inclus

- `update_git.py` - Script Python principal
- `update_git.bat` - Script batch pour Windows
- `README_GIT_UPDATE.md` - Ce fichier d'aide

## 🚀 Utilisation

### Mode interactif (recommandé pour débuter)

**Windows:**
```bash
update_git.bat
```

**Linux/Mac:**
```bash
./update_git.sh
```

**Python directement:**
```bash
python update_git.py
```

### Mode automatique

**Windows:**
```bash
update_git.bat auto "Mon message de commit"
```

**Linux/Mac:**
```bash
./update_git.sh auto "Mon message de commit"
```

**Python directement:**
```bash
python update_git.py auto "Mon message de commit"
```

### Vérification du statut

**Windows:**
```bash
update_git.bat status
```

**Linux/Mac:**
```bash
./update_git.sh status
```

**Python directement:**
```bash
python update_git.py status
```

## 📋 Fonctionnalités

### ✅ Ce que fait le script

1. **Vérification des changements** - Détecte les fichiers modifiés
2. **Ajout automatique** - Ajoute tous les changements au staging
3. **Commit intelligent** - Utilise un message personnalisé ou la date/heure
4. **Push vers GitHub** - Pousse les changements vers le dépôt distant
5. **Gestion d'erreurs** - Affiche des messages clairs en cas de problème
6. **Historique** - Affiche les derniers commits

### 🎯 Commandes disponibles

| Commande | Description |
|----------|-------------|
| `auto [message]` | Mise à jour automatique avec message optionnel |
| `status` | Vérifie le statut et affiche l'historique |
| `remote` | Affiche les dépôts distants configurés |
| `help` | Affiche l'aide complète |

## ⚙️ Configuration requise

### Prérequis

1. **Git installé** sur votre système
2. **Python 3.6+** installé
3. **Dépôt Git initialisé** dans le dossier
4. **Dépôt distant configuré** (GitHub)

### Configuration Git

Assurez-vous que votre dépôt est correctement configuré :

```bash
# Vérifier la configuration
git remote -v

# Si pas de dépôt distant, l'ajouter
git remote add origin https://github.com/votre-username/votre-repo.git

# Configurer la branche principale
git branch -M main
```

## 🔧 Personnalisation

### Modifier la branche par défaut

Dans `update_git.py`, ligne 15, changez :
```python
self.branch = "main"  # Changez "main" par votre branche
```

### Ajouter des fichiers à ignorer

Créez ou modifiez `.gitignore` pour exclure certains fichiers :
```
# Exemple de .gitignore
__pycache__/
*.pyc
.env
venv/
```

## 🚨 Dépannage

### Erreur "fatal: not a git repository"
- Assurez-vous d'être dans le bon dossier
- Initialisez Git : `git init`

### Erreur "fatal: remote origin already exists"
- Vérifiez la configuration : `git remote -v`
- Si nécessaire, supprimez et rajoutez : `git remote remove origin`

### Erreur d'authentification
- Configurez vos credentials Git
- Utilisez un token GitHub si nécessaire

## 📝 Exemples d'utilisation

### Mise à jour quotidienne
```bash
# Windows
update_git.bat auto "Mise à jour quotidienne"

# Linux/Mac
./update_git.sh auto "Mise à jour quotidienne"
```

### Vérification rapide
```bash
# Windows
update_git.bat status

# Linux/Mac
./update_git.sh status
```

### Mode interactif pour les gros changements
```bash
# Windows
update_git.bat

# Linux/Mac
./update_git.sh
```

## 🎉 Avantages

- **Rapide** : Une seule commande pour tout faire
- **Sûr** : Vérifications et gestion d'erreurs
- **Flexible** : Mode automatique ou interactif
- **Multi-plateforme** : Windows, Linux, Mac
- **Informatif** : Messages clairs et historique

---

**💡 Conseil :** Commencez par le mode interactif pour comprendre le processus, puis passez au mode automatique pour les mises à jour régulières. 