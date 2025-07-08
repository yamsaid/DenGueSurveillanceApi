# Documentation Complète - Package dengsurvap-bf

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du package](#architecture-du-package)
3. [Installation et configuration](#installation-et-configuration)
4. [Guide d'utilisation](#guide-dutilisation)
5. [API de référence](#api-de-référence)
6. [Modules spécialisés](#modules-spécialisés)
7. [Gestion des erreurs](#gestion-des-erreurs)
8. [Exemples d'utilisation](#exemples-dutilisation)
9. [Tests et qualité](#tests-et-qualité)
10. [Déploiement](#déploiement)

---

## 🎯 Vue d'ensemble

Le package `dengsurvap-bf` est un client Python officiel pour l'API de surveillance de la dengue Appi ( La plateforme de surveillance de dengue au Burkina Faso ). Il fournit une interface complète pour :

- **Accéder aux données épidémiologiques** de la dengue
- **Gérer les alertes** et leur configuration
- **Effectuer des analyses avancées** (séries temporelles, détection d'anomalies)
- **Exporter les données** dans différents formats
- **Authentifier les utilisateurs** avec gestion des rôles

### Caractéristiques principales

- ✅ **Interface intuitive** avec validation automatique des données
- ✅ **Gestion d'erreurs robuste** avec exceptions spécialisées
- ✅ **Cache intelligent** pour optimiser les performances
- ✅ **Support multi-formats** (CSV, JSON, xlsx, PDF)
- ✅ **Analyses épidémiologiques avancées**
- ✅ **Système d'alertes configurable**
- ✅ **CLI intégré** pour utilisation en ligne de commande
- ✅ **Tests complets** avec couverture élevée

---

## 🏗️ Architecture du package

### Structure des modules

```
dengsurvap-bf/
├── dengsurvab/
│   ├── __init__.py          # Point d'entrée principal
│   ├── client.py            # Client principal AppiClient
│   ├── models.py            # Modèles Pydantic
│   ├── exceptions.py        # Exceptions personnalisées
│   ├── analytics.py         # Outils d'analyse
│   ├── alerts.py            # Gestion des alertes
│   ├── auth.py              # Authentification
│   ├── export.py            # Export de données
│   └── cli.py               # Interface CLI
├── tests/                   # Tests unitaires
├── examples/                # Exemples d'utilisation
├── pyproject.toml          # Configuration du projet
└── README.md               # Documentation de base
```

### Flux de données

```
Utilisateur → AppiClient → API Appi → Données épidémiologiques
                ↓
        Modules spécialisés:
        - Analytics (analyses)
        - Alerts (alertes)
        - Export (export)
        - Auth (authentification)
```

---

## 🔧 Installation et configuration

### Installation

```bash
# Installation de base
pip install dengsurvap-bf

# Installation avec fonctionnalités d'analyse
pip install dengsurvap-bf[analysis]

# Installation en mode développement
pip install -e .
```

### Configuration

#### Variables d'environnement

```bash
# URL de l'API
export APPI_API_URL="https://api-bf-dengue-survey-production.up.railway.app"

# Clé API (optionnelle)
export APPI_API_KEY="votre-clé-api"

# Mode debug
export APPI_DEBUG="true"
```

#### Configuration programmatique

```python
from dengsurvab import AppiClient

# Configuration manuelle
client = AppiClient(
    base_url="https://api.appi.com",
    api_key="your-api-key",
    timeout=30,
    retry_attempts=3,
    debug=True
)

# Configuration depuis l'environnement
client = AppiClient.from_env()
```

---

## 📖 Guide d'utilisation

### 1. Connexion et authentification

```python
from dengsurvab import AppiClient

# Initialisation
client = AppiClient("https://api.appi.com")

# Authentification
auth_result = client.authenticate("user@example.com", "password")
print(f"Token: {auth_result['access_token']}")

# Vérification du profil
profile = client.get_profile()
print(f"Utilisateur: {profile.username} ({profile.role})")
```

### 2. Récupération des données

```python
# Cas de dengue
cas = client.get_cas_dengue(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    region="Antananarivo",
    limit=100
)

# Statistiques générales
stats = client.get_stats()
print(f"Total cas: {stats.total_cas}")

# Indicateurs hebdomadaires
indicateurs = client.data_period(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    region="Toutes"
)
```

### 3. Gestion des alertes

```python
# Configuration des seuils
client.configurer_seuils(
    seuil_positivite=10,
    seuil_hospitalisation=5,
    seuil_deces=2
)

# Récupération des alertes
alertes = client.get_alertes(
    severity="critical",
    status="active",
    limit=10
)

# Vérification automatique
resultat = client.verifier_alertes(
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)
```

### 4. Export de données

```python
# Export CSV
csv_data = client.export_data(
    format="csv",
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)

# Sauvegarde
with open("donnees.csv", "wb") as f:
    f.write(csv_data)

# Export des alertes
alertes_csv = client.export_alertes(
    format="csv",
    severity="critical"
)
```

---

## 🔌 API de référence

### Classe AppiClient

#### Méthodes d'authentification

```python
def authenticate(self, email: str, password: str) -> Dict[str, Any]
```
Authentifie l'utilisateur et récupère un token JWT.

```python
def logout(self) -> bool
```
Déconnecte l'utilisateur et invalide le token.

```python
def get_profile(self) -> User
```
Récupère le profil de l'utilisateur connecté.

#### Méthodes de données

```python
def get_cas_dengue(self, 
                   date_debut: Optional[str] = None,
                   date_fin: Optional[str] = None,
                   region: Optional[str] = None,
                   district: Optional[str] = None,
                   limit: Optional[int] = None,
                   page: int = 1,
                   page_size: int = 100) -> List[CasDengue]
```
Récupère les cas de dengue selon les critères.

```python
def get_stats(self) -> Statistiques
```
Récupère les statistiques générales.

```python
def data_period(self,
                         date_debut: str,
                         date_fin: str,
                         region: str = "Toutes",
                         district: str = "Toutes",
                         frequence: str = "W") -> List[IndicateurHebdo]
```
Récupère les indicateurs hebdomadaires.

#### Méthodes d'alertes

```python
def get_alertes(self,
                limit: int = 10,
                severity: Optional[str] = None,
                status: Optional[str] = None,
                region: Optional[str] = None,
                district: Optional[str] = None,
                date_debut: Optional[str] = None,
                date_fin: Optional[str] = None) -> List[AlertLog]
```
Récupère les alertes selon les critères.

```python
def configurer_seuils(self, **kwargs) -> Dict[str, Any]
```
Configure les seuils d'alerte.

```python
def verifier_alertes(self,
                    date_debut: Optional[str] = None,
                    date_fin: Optional[str] = None,
                    region: str = "Toutes",
                    district: str = "Toutes") -> Dict[str, Any]
```
Vérifie les alertes selon les critères.

#### Méthodes d'export

```python
def export_data(self,
               format: str = "csv",
               date_debut: Optional[str] = None,
               date_fin: Optional[str] = None,
               region: Optional[str] = None,
               district: Optional[str] = None,
               limit: Optional[int] = None) -> bytes
```
Exporte les données dans le format spécifié.

```python
def export_alertes(self,
                  format: str = "csv",
                  limit: int = 100,
                  severity: Optional[str] = None,
                  status: Optional[str] = None) -> bytes
```
Exporte les alertes dans le format spécifié.

---

## 🔬 Modules spécialisés

### 1. Module Analytics

#### EpidemiologicalAnalyzer

```python
from dengsurvab import EpidemiologicalAnalyzer

analyzer = EpidemiologicalAnalyzer(client)

# Série temporelle
series = analyzer.get_time_series(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    frequency="W"
)

# Détection d'anomalies
anomalies = analyzer.detect_anomalies(series, method="zscore")

# Calcul de taux
taux = analyzer.calculate_rates(
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)

# Analyse de tendance
tendance = analyzer.trend_analysis(series, column="total_cas")

# Analyse saisonnière
saisonnalite = analyzer.seasonal_analysis(series, column="total_cas")

# Prévision
prevision = analyzer.forecast_next_week(series, column="total_cas")
```

#### DashboardGenerator

```python
from dengsurvab import DashboardGenerator

generator = DashboardGenerator(client)

# Génération de rapport
rapport = generator.generate_report(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    region="Toutes",
    include_visualizations=True
)

# Sauvegarde
generator.save_report(rapport, "rapport_epidemio.json")
```

### 2. Module Alerts

```python
from dengsurvab import AlertManager

alert_manager = AlertManager(client)

# Récupération d'alertes
alertes = alert_manager.get_alertes(
    severity="critical",
    status="active",
    limit=10
)

# Configuration des seuils
config = alert_manager.configurer_seuils(
    seuil_positivite=10,
    seuil_hospitalisation=5,
    seuil_deces=2
)

# Vérification automatique
verification = alert_manager.verifier_alertes(
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)

# Export des alertes
alertes_export = alert_manager.exporter_alertes(
    format="csv",
    severity="critical"
)
```

### 3. Module Export

```python
from dengsurvab import DataExporter

exporter = DataExporter(client)

# Export de données
data_csv = exporter.export_data(
    format="csv",
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)

# Export d'alertes
alertes_csv = exporter.export_alertes(
    format="csv",
    severity="critical"
)

# Export de rapport
rapport_json = exporter.export_rapport(
    format="json",
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)

# Sauvegarde
exporter.save_to_file(data_csv, "donnees.csv", "csv")
```

---

## 🚨 Gestion des erreurs

### Exceptions disponibles

```python
from dengsurvab import (
    AppiException,
    AuthenticationError,
    APIError,
    ValidationError,
    RateLimitError,
    ConnectionError,
    AnalysisError,
    AlertConfigurationError,
    DataExportError
)
```

### Gestion typique

```python
from dengsurvab import AppiClient, AuthenticationError, APIError

try:
    client = AppiClient("https://api.appi.com")
    cas = client.get_cas_dengue(date_debut="2024-01-01")
    
except AuthenticationError as e:
    print(f"Erreur d'authentification: {e}")
    
except APIError as e:
    print(f"Erreur API: {e}")
    
except Exception as e:
    print(f"Erreur inattendue: {e}")
```

### Codes d'erreur

| Code | Exception | Description |
|------|------------|-------------|
| 401 | AuthenticationError | Token invalide ou expiré |
| 403 | AuthenticationError | Permissions insuffisantes |
| 400 | ValidationError | Données invalides |
| 404 | APIError | Ressource non trouvée |
| 429 | RateLimitError | Limite de requêtes dépassée |
| 500 | APIError | Erreur serveur |
| -1 | ConnectionError | Erreur de connexion |

---

## 💡 Exemples d'utilisation

### Exemple 1: Surveillance épidémiologique

```python
from dengsurvab import AppiClient, EpidemiologicalAnalyzer

# Connexion
client = AppiClient("https://api.appi.com")
client.authenticate("epidemiologist@health.gov", "password")

# Récupération des données
cas = client.get_cas_dengue(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    region="Antananarivo"
)

# Analyse épidémiologique
analyzer = EpidemiologicalAnalyzer(client)
series = analyzer.get_time_series(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    frequency="W"
)

# Détection d'anomalies
anomalies = analyzer.detect_anomalies(series, method="isolation_forest")

# Export du rapport
rapport = analyzer.generate_report(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    region="Antananarivo"
)

print(f"Cas analysés: {len(cas)}")
print(f"Anomalies détectées: {len(anomalies[anomalies['total_cas_anomaly']])}")
```

### Exemple 2: Système d'alertes

```python
from dengsurvab import AppiClient, AlertManager

# Connexion
client = AppiClient("https://api.appi.com")
client.authenticate("alert-manager@health.gov", "password")

# Configuration des seuils
alert_manager = AlertManager(client)
alert_manager.configurer_seuils(
    seuil_positivite=15,      # 15% de positivité
    seuil_hospitalisation=10,  # 10% d'hospitalisation
    seuil_deces=5             # 5% de décès
)

# Vérification des alertes
alertes = alert_manager.verifier_alertes(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    region="Toutes"
)

# Récupération des alertes critiques
alertes_critiques = alert_manager.get_alertes_critiques(limit=10)

# Export des alertes
alertes_export = alert_manager.exporter_alertes(
    format="csv",
    severity="critical"
)

print(f"Alertes actives: {len(alertes_critiques)}")
```

### Exemple 3: Export et reporting

```python
from dengsurvab import AppiClient, DataExporter

# Connexion
client = AppiClient("https://api.appi.com")
client.authenticate("data-analyst@health.gov", "password")

# Export de données
exporter = DataExporter(client)

# Export CSV des cas
cas_csv = exporter.export_data(
    format="csv",
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    region="Toutes"
)

# Export JSON des alertes
alertes_json = exporter.export_alertes(
    format="json",
    severity="critical"
)

# Export Excel du rapport
rapport_excel = exporter.export_rapport(
    format="xlsx",
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)

# Sauvegarde
exporter.save_to_file(cas_csv, "cas_dengue_janvier.csv", "csv")
exporter.save_to_file(alertes_json, "alertes_critiques.json", "json")
exporter.save_to_file(rapport_excel, "rapport_epidemio.xlsx", "xlsx")

print("Exports terminés avec succès")
```

### Exemple 4: Utilisation CLI

```bash
# Authentification
python -m dengsurvab auth --email user@example.com --password password

# Statistiques
python -m dengsurvab stats

# Récupération de cas
python -m dengsurvab cas --date-debut 2024-01-01 --date-fin 2024-01-31 --region Antananarivo

# Alertes critiques
python -m dengsurvab alertes --severity critical --limit 10

# Export de données
python -m dengsurvab export --format csv --output donnees.csv --date-debut 2024-01-01 --date-fin 2024-01-31

# Liste des régions
python -m dengsurvab regions

# Districts d'une région
python -m dengsurvab districts --region Antananarivo
```

---

## 🧪 Tests et qualité

### Exécution des tests

```bash
# Installation des dépendances de test
pip install dengsurvap-bf[dev]

# Exécution des tests
pytest tests/

# Avec couverture
pytest tests/ --cov=dengsurvab --cov-report=html

# Tests spécifiques
pytest tests/test_client.py
pytest tests/test_analytics.py
pytest tests/test_alerts.py
```

### Couverture de tests

- **test_client.py**: Tests du client principal (100%)
- **test_analytics.py**: Tests des analyses (85%)
- **test_alerts.py**: Tests des alertes (90%)
- **test_export.py**: Tests d'export (80%)
- **test_auth.py**: Tests d'authentification (95%)

### Qualité du code

```bash
# Linting
flake8 dengsurvab/

# Type checking
mypy dengsurvab/

# Formatage
black dengsurvab/
```

---

## 🚀 Déploiement

### Configuration de production

```python
# Configuration recommandée
client = AppiClient(
    base_url="https://api.appi.com",
    api_key="production-api-key",
    timeout=60,           # Timeout plus long en production
    retry_attempts=5,     # Plus de tentatives
    retry_delay=2.0,      # Délai plus long
    debug=False           # Pas de debug en production
)
```

### Variables d'environnement de production

```bash
# Production
export APPI_API_URL="https://api-bf-dengue-survey-production.up.railway.app"
export APPI_API_KEY="votre-clé-api"
export APPI_DEBUG="false"
export APPI_TIMEOUT="30"
export APPI_RETRY_ATTEMPTS="3"
```

### Monitoring et logging

```python
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('appi_client.log'),
        logging.StreamHandler()
    ]
)

# Utilisation avec logging
client = AppiClient("https://api.appi.com", debug=True)
client.logger.info("Client initialisé")
```

---

## 📚 Ressources supplémentaires

### Documentation API

- [Documentation API Appi](https://api.appi.com/docs)
- [Guide d'authentification](https://api.appi.com/auth)
- [Référence des endpoints](https://api.appi.com/endpoints)

### Support

- **Email**: saidouyameogo3@gmail.com
- **Issues**: GitHub Issues
- **Documentation**: README.md et ce document

### Contribution

1. Fork le repository
2. Créer une branche feature
3. Ajouter les tests
4. Soumettre une pull request

---

## 📝 Notes de version

### Version 0.1.0

- ✅ Client principal AppiClient
- ✅ Authentification JWT
- ✅ Gestion des alertes
- ✅ Export multi-formats
- ✅ Analyses épidémiologiques
- ✅ Interface CLI
- ✅ Tests complets
- ✅ Documentation complète

### Roadmap

- 🔄 Support WebSocket pour les alertes temps réel
- 🔄 Cache Redis pour les performances
- 🔄 Intégration avec PowerBI
- 🔄 API GraphQL
- 🔄 Support multi-langues
- 🔄 Dashboard web intégré

---

*Documentation générée le $(date) - Version 0.1.0* 