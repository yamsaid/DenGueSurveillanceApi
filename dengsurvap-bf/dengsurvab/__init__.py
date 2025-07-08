"""
Appi Dengue Client - Client Python pour l'API de surveillance de la dengue

Ce package fournit une interface Python complète pour accéder aux données
épidémiologiques de la dengue, gérer les alertes et effectuer des analyses avancées.

Exemple d'utilisation:
    >>> from dengsurvab import AppiClient
    >>> client = AppiClient("https://api.example.com", "your-api-key")
    >>> cas = client.get_cas_dengue(date_debut="2024-01-01", date_fin="2024-12-31")
"""

from .client import AppiClient
from .models import (
    CasDengue,
    SoumissionDonnee,
    AlertLog,
    SeuilAlert,
    User,
    ValidationCasDengue,
    ValidationSoumissionBase
)
from .exceptions import (
    AppiException,
    AuthenticationError,
    APIError,
    ValidationError,
    RateLimitError
)
from .analytics import EpidemiologicalAnalyzer, DashboardGenerator
from .alerts import AlertManager
from .auth import AuthManager
from .export import DataExporter

__version__ = "0.1.0"
__author__ = "Saïdou YAMEOGO - Data Analyst @ Appi"
__email__ = "saidouyameogo3@gmail.com"

__all__ = [
    # Client principal
    "AppiClient",
    
    # Modèles de données
    "CasDengue",
    "SoumissionDonnee", 
    "AlertLog",
    "SeuilAlert",
    "User",
    "ValidationCasDengue",
    "ValidationSoumissionBase",
    
    # Exceptions
    "AppiException",
    "AuthenticationError",
    "APIError", 
    "ValidationError",
    "RateLimitError",
    
    # Modules spécialisés
    "EpidemiologicalAnalyzer",
    "DashboardGenerator",
    "AlertManager",
    "AuthManager",
    "DataExporter",
]

# Configuration par défaut
DEFAULT_TIMEOUT = 30
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 1

# Versions supportées de l'API
SUPPORTED_API_VERSIONS = ["v1"]

# Formats d'export supportés
SUPPORTED_EXPORT_FORMATS = ["csv", "json", "xlsx", "pdf"]

# Types d'alerte supportés
SUPPORTED_ALERT_TYPES = ["warning", "critical", "info"]

# Statuts d'alerte supportés
SUPPORTED_ALERT_STATUSES = ["active", "resolved"]

# Rôles utilisateur supportés
SUPPORTED_USER_ROLES = ["user", "analyst", "admin", "authority"] 