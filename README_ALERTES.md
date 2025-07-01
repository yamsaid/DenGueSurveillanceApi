# Système de Gestion des Alertes Épidémiologiques

## Vue d'ensemble

Le système de gestion des alertes épidémiologiques permet de surveiller automatiquement les indicateurs de la dengue et de déclencher des alertes lorsque les seuils définis sont dépassés.

## Architecture

### Tables de Base de Données

#### 1. `alert_logs`
Stocke les alertes déclenchées avec les informations suivantes :
- `id`: Identifiant unique de l'alerte
- `id_seuil`: Référence au seuil utilisé
- `message`: Message descriptif de l'alerte
- `region`: Région concernée (optionnel)
- `district`: District concerné (optionnel)
- `notification_type`: Type de notification (warning, critical)
- `recipient`: Email du destinataire
- `created_at`: Date et heure de création

#### 2. `seuil_alert`
Contient les seuils personnalisés par utilisateur :
- `id`: Identifiant unique
- `usermail`: Email de l'utilisateur
- `intervalle`: Fréquence de vérification (1=hebdomadaire, 2=mensuel, 3=annuel)
- `seuil_positivite`: Seuil global pour le taux de positivité
- `seuil_hospitalisation`: Seuil global pour le taux d'hospitalisation
- `seuil_deces`: Seuil global pour le taux de décès
- `seuil_positivite_region`: Seuil régional pour le taux de positivité
- `seuil_hospitalisation_region`: Seuil régional pour le taux d'hospitalisation
- `seuil_deces_region`: Seuil régional pour le taux de décès
- `seuil_positivite_district`: Seuil district pour le taux de positivité
- `seuil_hospitalisation_district`: Seuil district pour le taux d'hospitalisation
- `seuil_deces_district`: Seuil district pour le taux de décès

## Fonctionnalités

### 1. Gestion des Seuils

#### Récupération des Seuils
```python
def recuperer_seuils_utilisateur(db: Session, usermail: str) -> dict:
    """
    Récupère les seuils personnalisés d'un utilisateur ou retourne les seuils par défaut
    """
```

**Comportement :**
- Cherche d'abord les seuils personnalisés de l'utilisateur
- Si aucun seuil personnalisé n'existe, utilise les seuils par défaut (admin@gmail.com)
- Si aucun seuil par défaut n'existe, crée automatiquement des seuils par défaut

#### Configuration des Seuils
- Interface web : `/configuration-alertes`
- API : `POST /api/alerts/seuils`
- Récupération : `GET /api/alerts/seuils/{usermail}`

### 2. Calcul des Indicateurs

#### Indicateurs Calculés
- **Taux de positivité** : (cas positifs / total cas) × 100
- **Taux d'hospitalisation** : (cas hospitalisés / total cas) × 100
- **Taux de décès** : (cas décédés / total cas) × 100

#### Fonction de Calcul
```python
def calculer_indicateurs_epidemiologiques(
    db: Session,
    date_debut: str,
    date_fin: str,
    region: str = "Toutes",
    district: str = "Toutes"
) -> dict:
```

### 3. Vérification des Seuils

#### Logique de Vérification
1. **Détermination du niveau géographique** :
   - District : si district spécifié
   - Région : si région spécifiée
   - Global : sinon

2. **Application des seuils appropriés** :
   - Seuils district > Seuils régionaux > Seuils globaux

3. **Génération des alertes** :
   - **Warning** : dépassement modéré (valeur < seuil × 1.5)
   - **Critical** : dépassement important (valeur ≥ seuil × 1.5)
   - **Critical** : toujours pour les décès

### 4. Sauvegarde des Alertes

#### Prévention des Doublons
- Vérification des alertes similaires dans les dernières 24h
- Évite la génération d'alertes répétitives

#### Informations Sauvegardées
- Référence au seuil utilisé
- Message descriptif
- Niveau de criticité
- Destinataire
- Horodatage

## API Endpoints

### 1. Vérification des Alertes
```
POST /api/alerts/verifier
```
**Paramètres :**
- `usermail`: Email de l'utilisateur (défaut: admin@gmail.com)
- `date_debut`: Date de début (optionnel)
- `date_fin`: Date de fin (optionnel)
- `region`: Région à analyser (défaut: "Toutes")
- `district`: District à analyser (défaut: "Toutes")

### 2. Configuration des Seuils
```
POST /api/alerts/seuils
```
**Paramètres (Form):**
- `usermail`: Email de l'utilisateur
- `seuil_positivite`: Seuil global positivité
- `seuil_hospitalisation`: Seuil global hospitalisation
- `seuil_deces`: Seuil global décès
- `seuil_positivite_region`: Seuil régional positivité
- `seuil_hospitalisation_region`: Seuil régional hospitalisation
- `seuil_deces_region`: Seuil régional décès
- `seuil_positivite_district`: Seuil district positivité
- `seuil_hospitalisation_district`: Seuil district hospitalisation
- `seuil_deces_district`: Seuil district décès
- `intervalle`: Fréquence de vérification

### 3. Récupération des Seuils
```
GET /api/alerts/seuils/{usermail}
```

### 4. Vérification Automatique
```
POST /api/alerts/verification-automatique
```

### 5. Indicateurs Actuels
```
GET /api/alerts/indicateurs
```

### 6. Logs d'Alertes
```
GET /api/alerts/logs
```

## Interface Utilisateur

### Page de Configuration
**URL :** `/configuration-alertes`

**Fonctionnalités :**
- Configuration des seuils par niveau géographique
- Affichage des statistiques actuelles
- Actions de vérification manuelle
- Chargement/sauvegarde des configurations

### Intégration dans les Pages Existantes
- **Accueil** : Affichage des alertes récentes
- **Évolution** : Notifications d'alertes actives

## Automatisation

### Script de Planification
**Fichier :** `scripts/planificateur_alertes.py`

**Fonctionnalités :**
- Vérification quotidienne à 08:00
- Vérification hebdomadaire le lundi à 09:00
- Vérification mensuelle le 1er du mois à 10:00
- Logging détaillé des opérations

### Démarrage du Planificateur
```bash
python scripts/planificateur_alertes.py
```

## Utilisation

### 1. Configuration Initiale
1. Accéder à `/configuration-alertes`
2. Configurer les seuils selon vos besoins
3. Sauvegarder la configuration

### 2. Vérification Manuelle
1. Utiliser l'interface web ou l'API
2. Vérifier les résultats dans les logs d'alertes

### 3. Surveillance Automatique
1. Démarrer le script de planification
2. Surveiller les logs dans `logs/alertes.log`

### 4. Consultation des Alertes
1. Page d'accueil : alertes récentes
2. API `/api/alerts/logs` : historique complet
3. Filtrage par région, district, type, etc.

## Exemples d'Utilisation

### Configuration via API
```bash
curl -X POST "http://localhost:8000/api/alerts/seuils" \
  -F "usermail=medecin@hopital.com" \
  -F "seuil_positivite=15" \
  -F "seuil_hospitalisation=12" \
  -F "seuil_deces=3"
```

### Vérification Manuelle
```bash
curl -X POST "http://localhost:8000/api/alerts/verifier?region=Centre"
```

### Consultation des Alertes
```bash
curl "http://localhost:8000/api/alerts/logs?limit=10&notification_type=critical"
```

## Maintenance

### Logs
- **Fichier :** `logs/alertes.log`
- **Niveau :** INFO, ERROR
- **Rotation :** Manuelle

### Base de Données
- Nettoyage périodique des anciennes alertes
- Sauvegarde régulière des seuils utilisateur

### Performance
- Indexation recommandée sur `alert_logs.created_at`
- Indexation recommandée sur `seuil_alert.usermail`

## Sécurité

### Authentification
- Validation des emails utilisateur
- Protection contre les injections SQL (via SQLAlchemy)

### Validation
- Vérification des valeurs de seuils (0-100%)
- Validation des dates
- Sanitisation des messages d'alerte

## Support

Pour toute question ou problème :
1. Consulter les logs dans `logs/alertes.log`
2. Vérifier la configuration des seuils
3. Tester les endpoints API individuellement
4. Contacter l'équipe de développement 