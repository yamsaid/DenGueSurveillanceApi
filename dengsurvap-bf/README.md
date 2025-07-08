# Appi Dengue Client

Client Python officiel pour l'API de surveillance de la dengue Appi. Ce package permet d'accéder facilement aux données épidémiologiques, de gérer les alertes et d'effectuer des analyses avancées.

## 🚀 Installation

```bash
pip install dengsurvap-bf
```

Pour les fonctionnalités d'analyse avancées :
```bash
pip install dengsurvap-bf[analysis]
```

## 📖 Guide rapide

### Connexion à l'API

```python
from dengsurvab import AppiClient

# Initialisation du client
client = AppiClient(
    base_url="https://votre-api-appi.com",
    api_key="votre-clé-api"
)

# Authentification
client.authenticate("votre-email", "votre-mot-de-passe")
```

### Récupération des données

```python
# Récupérer les cas de dengue
cas = client.get_cas_dengue(
    date_debut="2024-01-01",
    date_fin="2024-12-31",
    region="Antananarivo",
    limit=100
)

# Récupérer les indicateurs hebdomadaires
indicateurs = client.data_period(
    date_debut="2024-01-01",
    date_fin="2024-12-31",
    region="Toutes"
)

# Exporter les données
data_bytes = client.export_data(
    format="csv",
    date_debut="2024-01-01",
    date_fin="2024-12-31"
)
```

### Gestion des alertes

```python
# Récupérer les alertes actives
alertes = client.get_alertes(severity="critical", status="active")

# Configurer les seuils d'alerte
client.configurer_seuils(
    seuil_positivite=10,
    seuil_hospitalisation=5,
    seuil_deces=2
)

# Vérifier les alertes
alertes_verifiees = client.verifier_alertes(
    date_debut="2024-01-01",
    date_fin="2024-12-31"
)
```

## 🔧 Fonctionnalités principales

### 📊 Données épidémiologiques
- Récupération des cas de dengue
- Indicateurs hebdomadaires et mensuels
- Analyses géographiques et démographiques
- Calculs de taux (hospitalisation, létalité, positivité)

### 🚨 Système d'alertes
- Configuration des seuils d'alerte
- Vérification automatique des alertes
- Historique des alertes
- Notifications personnalisées

### 📈 Outils d'analyse
- Séries temporelles
- Détection d'anomalies
- Analyses statistiques
- Visualisations

### 🔐 Authentification sécurisée
- Support JWT
- Gestion des rôles (user, analyst, admin, authority)
- Tokens automatiques
- Sécurité renforcée

### 📤 Export/Import
- Formats multiples (CSV, JSON, Excel)
- Filtrage avancé
- Validation des données
- Compression automatique

## 📚 Documentation complète

### Modèles de données

#### Cas de dengue
```python
from dengsurvab.models import CasDengue

cas = CasDengue(
    idCas=1,
    date_consultation="2024-01-15",
    region="Antananarivo",
    district="Analamanga",
    sexe="M",
    age=25,
    resultat_test="Positif",
    serotype="DENV2",
    hospitalise="Non",
    issue="Guéri",
    id_source=1
)
```

#### Alertes
```python
from dengsurvab.models import AlertLog

alerte = AlertLog(
    id=1,
    severity="critical",
    status="active",
    message="Seuil dépassé pour la région Antananarivo",
    region="Antananarivo",
    created_at="2024-01-15T10:30:00"
)
```

### Méthodes principales

#### Client API
```python
# Authentification
client.authenticate(email, password)
client.logout()

# Données
client.get_cas_dengue(**params)
client.data_period(**params)
client.get_stats()

# Résumé statistique
client.resume()                    # Résumé JSON structuré
client.resume_display(verbose=True, show_details=True, graph=True)  # Affichage console avec graphiques

# Alertes
client.get_alertes(**params)
client.configurer_seuils(**params)
client.verifier_alertes(**params)

# Export
client.export_data(format="csv", **params)
client.export_alertes(format="json", **params)
```

#### Outils d'analyse
```python
from dengsurvab.analytics import EpidemiologicalAnalyzer

analyzer = EpidemiologicalAnalyzer(client)

# Analyses temporelles
series = analyzer.get_time_series(
    date_debut="2024-01-01",
    date_fin="2024-12-31",
    frequency="W"
)

# Détection d'anomalies
anomalies = analyzer.detect_anomalies(series)

# Calculs de taux
taux = analyzer.calculate_rates(
    date_debut="2024-01-01",
    date_fin="2024-12-31"
)
```

## 🧪 Tests

```bash
# Installer les dépendances de développement
pip install dengsurvap-bf[dev]

# Lancer les tests
pytest

# Avec couverture
pytest --cov=dengsurvab

# Tests spécifiques
pytest tests/test_client.py
pytest tests/test_analytics.py
```

## 🔧 Configuration

### Variables d'environnement
```bash
export APPI_API_URL="https://api-bf-dengue-survey-production.up.railway.app/"

export APPI_API_KEY="votre-clé-api"
export APPI_DEBUG="true"
```

### Configuration programmatique
```python
import os
from dengsurvab import AppiClient

# Configuration via variables d'environnement
client = AppiClient.from_env()

# Configuration manuelle
client = AppiClient(
    base_url=os.getenv("APPI_API_URL"),
    api_key=os.getenv("APPI_API_KEY"),
    debug=os.getenv("APPI_DEBUG", "false").lower() == "true"
)
```

## 📊 Exemples avancés

### Résumé statistique avec graphiques
```python
from dengsurvab import AppiClient

client = AppiClient("https://api.example.com", "your-key")

# Résumé complet avec graphiques
client.resume_display(
    verbose=True,      # Afficher tous les détails
    show_details=True, # Statistiques détaillées
    graph=True        # Afficher les graphiques
)

# Résumé simplifié sans graphiques
client.resume_display(
    verbose=False,     # Affichage simplifié
    show_details=False, # Pas de détails
    graph=False       # Pas de graphiques
)

# Résumé avec graphiques mais sans détails
client.resume_display(
    verbose=False,     # Affichage simplifié
    show_details=False, # Pas de détails
    graph=True        # Afficher les graphiques
)
```

### Dashboard épidémiologique
```python
from dengsurvab import AppiClient
from dengsurvab.analytics import DashboardGenerator

client = AppiClient("https://api.example.com", "your-key")
dashboard = DashboardGenerator(client)

# Générer un rapport complet
rapport = dashboard.generate_report(
    date_debut="2024-01-01",
    date_fin="2024-12-31",
    region="Toutes",
    include_visualizations=True
)

# Sauvegarder le rapport
dashboard.save_report(rapport, "rapport_dengue_2024.pdf")
```

### Surveillance en temps réel
```python
from dengsurvab import AppiClient
import time

client = AppiClient("https://api.example.com", "your-key")

def surveillance_continue():
    while True:
        # Vérifier les nouvelles alertes
        alertes = client.get_alertes(status="active")
        
        for alerte in alertes:
            print(f"Nouvelle alerte: {alerte.message}")
            
        # Attendre 5 minutes
        time.sleep(300)

# Démarrer la surveillance
surveillance_continue()
```

## 🐛 Dépannage

### Erreurs courantes

#### Erreur d'authentification
```python
# Vérifier vos identifiants
client.authenticate("email@example.com", "mot-de-passe")
```

#### Erreur de connexion
```python
# Vérifier l'URL de l'API
client = AppiClient("https://api-correcte.com", "your-key")
```

#### Erreur de validation
```python
# Vérifier le format des dates
cas = client.get_cas_dengue(
    date_debut="2024-01-01",  # Format YYYY-MM-DD
    date_fin="2024-12-31"
)
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

- 📧 Email: yamsaid74@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/yamsaid/dengsurvap-bf/issues)
- 📖 Documentation: [ReadTheDocs](https://dengsurvap-bf.readthedocs.io/)
 
## 🔄 Changelog

### Version 0.1.0
- ✅ Client API de base
- ✅ Authentification JWT
- ✅ Gestion des alertes
- ✅ Export de données
- ✅ Outils d'analyse épidémiologique
- ✅ Documentation complète
- ✅ Tests unitaires

---

**Appi Dengue Client** - Simplifiez l'accès aux données de surveillance de la dengue avec Python. 