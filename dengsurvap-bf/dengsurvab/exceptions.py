"""
Exceptions personnalisées pour le client Appi Dengue

Ce module définit toutes les exceptions spécifiques au package
pour une gestion d'erreur claire et informative.
"""

from typing import Optional, Dict, Any


class AppiException(Exception):
    """
    Exception de base pour toutes les exceptions du package Appi Dengue Client.
    
    Cette classe sert de point d'entrée pour toutes les exceptions spécifiques
    au package et permet une gestion centralisée des erreurs.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialise l'exception avec un message et des détails optionnels.
        
        Args:
            message: Message d'erreur principal
            details: Détails supplémentaires de l'erreur
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """Retourne une représentation string de l'exception."""
        if self.details:
            return f"{self.message} - Détails: {self.details}"
        return self.message


class AuthenticationError(AppiException):
    """
    Exception levée en cas d'erreur d'authentification.
    
    Cette exception est levée quand:
    - Les identifiants sont incorrects
    - Le token JWT est invalide ou expiré
    - L'utilisateur n'a pas les permissions nécessaires
    """
    
    def __init__(self, message: str = "Erreur d'authentification", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class APIError(AppiException):
    """
    Exception levée en cas d'erreur de l'API.
    
    Cette exception est levée quand:
    - L'API retourne une erreur HTTP
    - Le format de réponse est invalide
    - L'endpoint n'existe pas
    """
    
    def __init__(self, message: str = "Erreur de l'API", 
                 status_code: Optional[int] = None,
                 endpoint: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self.endpoint = endpoint
        super().__init__(message, details)


class ValidationError(AppiException):
    """
    Exception levée en cas d'erreur de validation des données.
    
    Cette exception est levée quand:
    - Les données ne respectent pas le schéma attendu
    - Les valeurs sont hors limites
    - Les types de données sont incorrects
    """
    
    def __init__(self, message: str = "Erreur de validation", 
                 field: Optional[str] = None,
                 value: Optional[Any] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.field = field
        self.value = value
        super().__init__(message, details)


class RateLimitError(AppiException):
    """
    Exception levée quand la limite de requêtes est dépassée.
    
    Cette exception est levée quand:
    - Trop de requêtes sont envoyées dans un court laps de temps
    - Le quota API est dépassé
    """
    
    def __init__(self, message: str = "Limite de requêtes dépassée",
                 retry_after: Optional[int] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.retry_after = retry_after
        super().__init__(message, details)


class ConnectionError(AppiException):
    """
    Exception levée en cas d'erreur de connexion.
    
    Cette exception est levée quand:
    - Le serveur est inaccessible
    - Le timeout est dépassé
    - La connexion réseau échoue
    """
    
    def __init__(self, message: str = "Erreur de connexion",
                 url: Optional[str] = None,
                 timeout: Optional[float] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.url = url
        self.timeout = timeout
        super().__init__(message, details)


class DataExportError(AppiException):
    """
    Exception levée en cas d'erreur lors de l'export de données.
    
    Cette exception est levée quand:
    - Le format d'export n'est pas supporté
    - L'écriture du fichier échoue
    - Les données sont corrompues
    """
    
    def __init__(self, message: str = "Erreur d'export de données",
                 format: Optional[str] = None,
                 file_path: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.format = format
        self.file_path = file_path
        super().__init__(message, details)


class AlertConfigurationError(AppiException):
    """
    Exception levée en cas d'erreur de configuration des alertes.
    
    Cette exception est levée quand:
    - Les seuils sont invalides
    - La configuration est incomplète
    - Les paramètres sont contradictoires
    """
    
    def __init__(self, message: str = "Erreur de configuration des alertes",
                 alert_type: Optional[str] = None,
                 threshold: Optional[float] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.alert_type = alert_type
        self.threshold = threshold
        super().__init__(message, details)


class AnalysisError(AppiException):
    """
    Exception levée en cas d'erreur lors des analyses.
    
    Cette exception est levée quand:
    - Les données sont insuffisantes pour l'analyse
    - Les calculs échouent
    - Les paramètres d'analyse sont invalides
    """
    
    def __init__(self, message: str = "Erreur d'analyse",
                 analysis_type: Optional[str] = None,
                 parameters: Optional[Dict[str, Any]] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.analysis_type = analysis_type
        self.parameters = parameters
        super().__init__(message, details)


class ConfigurationError(AppiException):
    """
    Exception levée en cas d'erreur de configuration.
    
    Cette exception est levée quand:
    - Les variables d'environnement sont manquantes
    - La configuration est invalide
    - Les paramètres sont mal formatés
    """
    
    def __init__(self, message: str = "Erreur de configuration",
                 config_key: Optional[str] = None,
                 config_value: Optional[Any] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.config_key = config_key
        self.config_value = config_value
        super().__init__(message, details)


# Mapping des codes d'erreur HTTP vers nos exceptions
HTTP_ERROR_MAPPING = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthenticationError,
    404: APIError,
    429: RateLimitError,
    500: APIError,
    502: ConnectionError,
    503: ConnectionError,
    504: ConnectionError,
}


def create_exception_from_response(status_code: int, response_data: Dict[str, Any]) -> AppiException:
    """
    Crée une exception appropriée basée sur le code de statut HTTP.
    
    Args:
        status_code: Code de statut HTTP
        response_data: Données de la réponse d'erreur
        
    Returns:
        Exception appropriée pour le code de statut
    """
    exception_class = HTTP_ERROR_MAPPING.get(status_code, APIError)
    
    message = response_data.get("detail", f"Erreur HTTP {status_code}")
    details = {
        "status_code": status_code,
        "response_data": response_data
    }
    
    if exception_class == RateLimitError:
        retry_after = response_data.get("retry_after")
        return exception_class(message, retry_after=retry_after, details=details)
    elif exception_class == APIError:
        return exception_class(message, status_code=status_code, details=details)
    else:
        return exception_class(message, details=details) 