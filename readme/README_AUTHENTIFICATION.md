# Système d'Authentification - Documentation

## 📋 Vue d'ensemble

Le système d'authentification a été implémenté avec les fonctionnalités suivantes :

- ✅ **Connexion sécurisée** avec JWT tokens
- ✅ **Inscription utilisateur** avec validation
- ✅ **Mot de passe oublié** avec réinitialisation
- ✅ **Avatar utilisateur** avec première lettre du nom
- ✅ **Gestion des sessions** avec localStorage
- ✅ **Interface moderne** et responsive

## 🔐 Fonctionnalités

### 1. Connexion (`/login`)
- **Page** : Interface moderne avec validation en temps réel
- **Fonctionnalités** :
  - Validation des champs email/mot de passe
  - Option "Se souvenir de moi" (token 7 jours)
  - Lien vers "Mot de passe oublié"
  - Messages d'erreur/succès dynamiques
  - Stockage automatique du token JWT

### 2. Inscription (`/register`)
- **Page** : Formulaire d'inscription complet
- **Fonctionnalités** :
  - Validation des champs en temps réel
  - Indicateur de force du mot de passe
  - Vérification d'unicité email/username
  - Conditions d'utilisation obligatoires
  - Newsletter optionnelle

### 3. Mot de passe oublié (`/forgot-password`)
- **Page** : Interface simple pour récupération
- **Fonctionnalités** :
  - Saisie de l'adresse email
  - Génération de token de réinitialisation (1h)
  - Messages de sécurité (ne révèle pas si l'email existe)
  - Lien de réinitialisation automatique

### 4. Réinitialisation mot de passe (`/reset-password`)
- **Page** : Formulaire de nouveau mot de passe
- **Fonctionnalités** :
  - Validation du token de réinitialisation
  - Indicateur de force du mot de passe
  - Confirmation du mot de passe
  - Redirection automatique après succès

### 5. Avatar utilisateur
- **Affichage** : Première lettre du prénom (ou username)
- **Fonctionnalités** :
  - Cercle coloré avec initiale
  - Menu déroulant au survol
  - Informations utilisateur
  - Liens vers profil et déconnexion

## 🛠️ Endpoints API

### Authentification
```python
POST /login                    # Connexion
POST /register                 # Inscription
POST /logout                   # Déconnexion
GET  /profile                  # Profil utilisateur
PUT  /profile                  # Mise à jour profil
POST /change-password          # Changer mot de passe
```

### Mot de passe oublié
```python
GET  /forgot-password          # Page mot de passe oublié
POST /forgot-password          # Demander réinitialisation
GET  /reset-password           # Page réinitialisation
POST /reset-password           # Réinitialiser mot de passe
```

### Statut d'authentification
```python
GET  /api/auth/status          # Vérifier état connexion
```

## 👥 Utilisateurs de test

### Admin
- **Email** : admin@dengue.com
- **Mot de passe** : Admin123!
- **Rôle** : admin

### Utilisateurs standards
- **Jean Dupont** : jean.dupont@example.com / Password123!
- **Marie Martin** : marie.martin@example.com / Secure456!
- **Pierre Durand** : pierre.durand@example.com / Test789!

## 🔧 Installation et configuration

### 1. Installer les dépendances
```bash
pip install PyJWT passlib[bcrypt]
```

### 2. Créer les utilisateurs de test
```bash
python scripts/create_test_users.py
```

### 3. Démarrer l'application
```bash
uvicorn main:app --reload
```

## 🔒 Sécurité

### JWT Tokens
- **Algorithme** : HS256
- **Durée** : 30 minutes (standard) / 7 jours (se souvenir)
- **Clé secrète** : Configurée dans `main.py`

### Hachage des mots de passe
- **Algorithme** : bcrypt
- **Rounds** : 12 (recommandé)
- **Salt** : Automatique

### Validation
- **Email** : Format valide requis
- **Mot de passe** : Minimum 8 caractères
- **Username** : Unique dans la base
- **Token** : Vérification d'expiration

## 🎨 Interface utilisateur

### Design moderne
- **Gradients** : Couleurs modernes
- **Animations** : Transitions fluides
- **Responsive** : Mobile-first design
- **Accessibilité** : Contraste et focus

### Composants
- **Formulaires** : Validation en temps réel
- **Alertes** : Messages d'erreur/succès
- **Loading** : Indicateurs de chargement
- **Avatars** : Cercles avec initiales

## 🚀 Utilisation

### 1. Connexion
1. Aller sur `/login`
2. Saisir email et mot de passe
3. Optionnel : Cocher "Se souvenir de moi"
4. Cliquer sur "Se connecter"

### 2. Mot de passe oublié
1. Cliquer sur "Mot de passe oublié ?"
2. Saisir l'adresse email
3. Cliquer sur "Envoyer le lien"
4. Suivre le lien reçu

### 3. Avatar utilisateur
- **Connecté** : Affiche l'avatar avec menu
- **Non connecté** : Affiche bouton de connexion
- **Menu** : Profil et déconnexion

## 🔧 Configuration avancée

### Variables d'environnement
```python
SECRET_KEY = "votre_clé_secrète_très_longue_et_complexe_ici_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### Base de données
```python
# Modèle User dans schemas/models.py
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## 🐛 Dépannage

### Problèmes courants

#### 1. Import JWT
```python
# Correct
import jwt

# Incorrect
import PyJWT as jwt
```

#### 2. Token invalide
- Vérifier la clé secrète
- Vérifier l'expiration
- Vérifier l'algorithme

#### 3. Mot de passe incorrect
- Vérifier le hachage bcrypt
- Vérifier la fonction de vérification

#### 4. Avatar ne s'affiche pas
- Vérifier le localStorage
- Vérifier l'endpoint `/api/auth/status`
- Vérifier les permissions CORS

## 📝 Notes importantes

### Production
- ✅ Changer la clé secrète
- ✅ Utiliser HTTPS
- ✅ Configurer les emails
- ✅ Activer l'authentification 2FA
- ✅ Limiter les tentatives de connexion

### Développement
- ✅ Utiliser les utilisateurs de test
- ✅ Tester tous les scénarios
- ✅ Vérifier la validation
- ✅ Tester la responsivité

## 🔄 Mises à jour futures

### Fonctionnalités prévues
- [ ] Authentification à deux facteurs
- [ ] Gestion des rôles avancée
- [ ] Audit des connexions
- [ ] Expiration de session
- [ ] Blocage de compte

### Améliorations UI/UX
- [ ] Thème sombre
- [ ] Animations avancées
- [ ] Notifications push
- [ ] Mode hors ligne

---

**Version** : 1.0.0  
**Date** : 2024  
**Auteur** : Système de Surveillance Dengue 