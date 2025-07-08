"""
Modèles de données Pydantic pour le client Appi Dengue

Ce module définit tous les modèles de données utilisés dans le package
pour la validation, la sérialisation et la désérialisation des données.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class Sexe(str, Enum):
    """Enumération pour le sexe du patient."""
    MASCULIN = "masculin"
    FEMININ = "feminin"
    M = "m"
    F = "f"
    HOMME = "homme"
    FEMME = "femme"


class ResultatTest(str, Enum):
    """Enumération pour le résultat du test de dengue."""
    POSITIF = "positif"
    NEGATIF = "négatif"


class Serotype(str, Enum):
    """Enumération pour les sérotypes de dengue."""
    DENV2 = "denv2"
    DENV3 = "denv3"


class Hospitalisation(str, Enum):
    """Enumération pour le statut d'hospitalisation."""
    OUI = "oui"
    NON = "non"


class Issue(str, Enum):
    """Enumération pour l'issue du cas."""
    GUERI = "guéri"
    EN_TRAITEMENT = "en traitement"
    DECEDE = "décédé"
    INCONNUE = "inconnue"


class Severity(str, Enum):
    """Enumération pour la sévérité des alertes."""
    WARNING = "warning"
    CRITICAL = "critical"
    INFO = "info"


class Status(str, Enum):
    """Enumération pour le statut des alertes."""
    ACTIVE = "active"
    RESOLVED = "resolved"


class Role(str, Enum):
    """Enumération pour les rôles utilisateur."""
    USER = "user"
    ANALYST = "analyst"
    ADMIN = "admin"
    AUTHORITY = "authority"


class CasDengue(BaseModel):
    """
    Modèle pour un cas de dengue.
    
    Ce modèle représente un cas individuel de dengue avec toutes
    les informations épidémiologiques associées.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    idCas: int = Field(description="Identifiant unique du cas")
    date_consultation: Optional[date] = Field(None, description="Date de consultation")
    region: Optional[str] = Field(None, description="Région du cas")
    district: Optional[str] = Field(None, description="District du cas")
    sexe: Sexe = Field(description="Sexe du patient")
    age: int = Field(gt=0, le=120, description="Âge du patient en années")
    resultat_test: Optional[ResultatTest] = Field(None, description="Résultat du test de dengue")
    serotype: Optional[Serotype] = Field(None, description="Sérotype de dengue")
    hospitalise: Optional[Hospitalisation] = Field(None, description="Statut d'hospitalisation")
    issue: Optional[Issue] = Field(None, description="Issue du cas")
    id_source: int = Field(description="Identifiant de la source de données")
    
    @field_validator("region")
    @classmethod
    def validate_region(cls, v):
        """Valide la région."""
        if v is not None:
            valid_regions = ["centre", "hauts-bassins", "antananarivo", "toutes"]
            if v.lower() not in valid_regions:
                raise ValueError(f"Région invalide: {v}. Régions valides: {valid_regions}")
        return v
    
    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        """Valide l'âge."""
        if v < 0 or v > 120:
            raise ValueError("L'âge doit être entre 0 et 120 ans")
        return v


class SoumissionDonnee(BaseModel):
    """
    Modèle pour une soumission de données.
    
    Ce modèle représente une soumission de données de cas de dengue
    avec les métadonnées associées.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description="Identifiant unique de la soumission")
    date_soumission: Optional[date] = Field(None, description="Date de soumission")
    username: Optional[str] = Field(None, description="Nom d'utilisateur")
    centre: Optional[str] = Field(None, description="Centre de santé")
    poste: Optional[str] = Field(None, description="Poste de l'utilisateur")
    apikey: Optional[str] = Field(None, description="Clé API utilisée")
    periode_debut: Optional[date] = Field(None, description="Début de la période")
    periode_fin: Optional[date] = Field(None, description="Fin de la période")
    sources: Optional[str] = Field(None, description="Sources des données")
    description: Optional[str] = Field(None, description="Description de la soumission")


class AlertLog(BaseModel):
    """
    Modèle pour un log d'alerte.
    
    Ce modèle représente une alerte générée par le système
    de surveillance épidémiologique.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description="Identifiant unique de l'alerte")
    id_seuil: Optional[int] = Field(None, description="Identifiant du seuil déclencheur")
    usermail: Optional[str] = Field(None, description="Email de l'utilisateur")
    severity: Optional[Severity] = Field(None, description="Sévérité de l'alerte")
    status: Optional[Status] = Field(None, description="Statut de l'alerte")
    message: Optional[str] = Field(None, description="Message de l'alerte")
    region: Optional[str] = Field(None, description="Région concernée")
    district: Optional[str] = Field(None, description="District concerné")
    notification_type: Optional[str] = Field(None, description="Type de notification")
    recipient: Optional[str] = Field(None, description="Destinataire de l'alerte")
    created_at: Optional[datetime] = Field(None, description="Date de création de l'alerte")


class SeuilAlert(BaseModel):
    """
    Modèle pour la configuration des seuils d'alerte.
    
    Ce modèle représente la configuration des seuils pour
    le déclenchement des alertes épidémiologiques.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description="Identifiant unique du seuil")
    usermail: str = Field(description="Email de l'utilisateur")
    intervalle: str = Field(default="1", description="Intervalle de vérification")
    seuil_positivite: int = Field(default=10, ge=0, le=100, description="Seuil de positivité (%)")
    seuil_hospitalisation: int = Field(default=10, ge=0, le=100, description="Seuil d'hospitalisation (%)")
    seuil_deces: int = Field(default=10, ge=0, le=100, description="Seuil de décès (%)")
    seuil_positivite_region: int = Field(default=10, ge=0, le=100, description="Seuil de positivité par région (%)")
    seuil_hospitalisation_region: int = Field(default=10, ge=0, le=100, description="Seuil d'hospitalisation par région (%)")
    seuil_deces_region: int = Field(default=10, ge=0, le=100, description="Seuil de décès par région (%)")
    seuil_positivite_district: int = Field(default=10, ge=0, le=100, description="Seuil de positivité par district (%)")
    seuil_hospitalisation_district: int = Field(default=10, ge=0, le=100, description="Seuil d'hospitalisation par district (%)")
    seuil_deces_district: int = Field(default=10, ge=0, le=100, description="Seuil de décès par district (%)")
    created_at: Optional[datetime] = Field(None, description="Date de création du seuil")
    
    @field_validator("intervalle")
    @classmethod
    def validate_intervalle(cls, v):
        """Valide l'intervalle."""
        valid_intervalles = ["1", "2", "3"]  # 1: hebdomadaire, 2: mensuel, 3: annuel
        if v not in valid_intervalles:
            raise ValueError(f"Intervalle invalide: {v}. Intervalles valides: {valid_intervalles}")
        return v


class User(BaseModel):
    """
    Modèle pour un utilisateur.
    
    Ce modèle représente un utilisateur du système avec
    ses informations de profil et permissions.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description="Identifiant unique de l'utilisateur")
    username: str = Field(description="Nom d'utilisateur")
    email: str = Field(description="Adresse email")
    hashed_password: Optional[str] = Field(None, description="Mot de passe hashé (optionnel pour les réponses API)")
    first_name: Optional[str] = Field(None, description="Prénom")
    last_name: Optional[str] = Field(None, description="Nom de famille")
    role: Role = Field(default=Role.USER, description="Rôle de l'utilisateur")
    is_active: bool = Field(default=True, description="Statut actif de l'utilisateur")
    created_at: Optional[datetime] = Field(None, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")


class ValidationCasDengue(BaseModel):
    """
    Modèle pour la validation des cas de dengue.
    
    Ce modèle est utilisé pour valider les données de cas
    avant leur insertion dans la base de données.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    idCas: int = Field(description="Identifiant unique du cas")
    sexe: Sexe = Field(description="Sexe du patient")
    age: int = Field(gt=0, le=120, description="Âge du patient en années")
    region: Optional[str] = Field(default="Centre", min_length=2, max_length=50, description="Région")
    date_consultation: Optional[str] = Field(None, description="Date de consultation")
    district: Optional[str] = Field(None, description="District")
    resultat_test: Optional[ResultatTest] = Field(None, description="Résultat du test")
    serotype: Optional[Serotype] = Field(None, description="Sérotype")
    hospitalisation: Optional[Hospitalisation] = Field(None, description="Statut d'hospitalisation")
    issue: Optional[Issue] = Field(default=Issue.GUERI, min_length=2, max_length=50, description="Issue")
    id_source: int = Field(description="Identifiant de la source")
    
    @field_validator("region")
    @classmethod
    def validate_region(cls, v):
        """Valide la région."""
        if v is not None:
            valid_regions = ["centre", "hauts-bassins"]
            if v.lower() not in valid_regions:
                raise ValueError(f"Région invalide: {v}. Régions valides: {valid_regions}")
        return v
    
    @field_validator("issue")
    @classmethod
    def validate_issue(cls, v):
        """Valide l'issue."""
        if v is not None:
            valid_issues = ["guéri", "en traitement", "décédé", "inconnue"]
            if v.lower() not in valid_issues:
                raise ValueError(f"Issue invalide: {v}. Issues valides: {valid_issues}")
        return v


class ValidationSoumissionBase(BaseModel):
    """
    Modèle de base pour la validation des soumissions.
    
    Ce modèle définit les champs requis pour toute soumission
    de données de cas de dengue.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    username: str = Field(description="Nom d'utilisateur")
    date_soumission: date = Field(description="Date de soumission")
    centre: str = Field(description="Centre de santé")
    poste: str = Field(description="Poste de l'utilisateur")
    apikey: str = Field(description="Clé API")
    periode_debut: date = Field(description="Début de la période")
    periode_fin: date = Field(description="Fin de la période")
    description: str = Field(description="Description de la soumission")
    sources: str = Field(description="Sources des données")


class IndicateurHebdo(BaseModel):
    """
    Modèle pour les indicateurs hebdomadaires.
    
    Ce modèle représente les indicateurs épidémiologiques
    calculés sur une base hebdomadaire.
    """
    
    date_debut: date = Field(description="Date de début de la semaine")
    date_fin: date = Field(description="Date de fin de la semaine")
    region: str = Field(description="Région")
    district: str = Field(description="District")
    total_cas: int = Field(ge=0, description="Nombre total de cas")
    cas_positifs: int = Field(ge=0, description="Nombre de cas positifs")
    cas_negatifs: int = Field(ge=0, description="Nombre de cas négatifs")
    hospitalisations: int = Field(ge=0, description="Nombre d'hospitalisations")
    deces: int = Field(ge=0, description="Nombre de décès")
    taux_positivite: float = Field(ge=0, le=100, description="Taux de positivité (%)")
    taux_hospitalisation: float = Field(ge=0, le=100, description="Taux d'hospitalisation (%)")
    taux_letalite: float = Field(ge=0, le=100, description="Taux de létalité (%)")


class Statistiques(BaseModel):
    """
    Modèle pour les statistiques générales.
    
    Ce modèle représente les statistiques globales
    du système de surveillance.
    """
    
    total_cas: int = Field(ge=0, description="Nombre total de cas")
    total_positifs: int = Field(ge=0, description="Nombre total de cas positifs")
    total_hospitalisations: int = Field(ge=0, description="Nombre total d'hospitalisations")
    total_deces: int = Field(ge=0, description="Nombre total de décès")
    regions_actives: List[str] = Field(description="Liste des régions actives")
    districts_actifs: List[str] = Field(description="Liste des districts actifs")
    derniere_mise_a_jour: datetime = Field(description="Date de dernière mise à jour")


# Modèles pour les requêtes API
class LoginRequest(BaseModel):
    """Modèle pour la requête de connexion."""
    email: str = Field(description="Adresse email")
    password: str = Field(description="Mot de passe")


class RegisterRequest(BaseModel):
    """Modèle pour la requête d'inscription."""
    firstName: str = Field(description="Prénom")
    lastName: str = Field(description="Nom de famille")
    email: str = Field(description="Adresse email")
    username: str = Field(description="Nom d'utilisateur")
    password: str = Field(description="Mot de passe")
    terms: bool = Field(description="Acceptation des termes")
    newsletter: bool = Field(default=False, description="Inscription à la newsletter")


class AlertConfigRequest(BaseModel):
    """Modèle pour la configuration des alertes."""
    seuil_positivite: int = Field(ge=0, le=100, description="Seuil de positivité (%)")
    seuil_hospitalisation: int = Field(ge=0, le=100, description="Seuil d'hospitalisation (%)")
    seuil_deces: int = Field(ge=0, le=100, description="Seuil de décès (%)")
    intervalle: str = Field(default="1", description="Intervalle de vérification")


# Modèles pour les réponses API
class LoginResponse(BaseModel):
    """Modèle pour la réponse de connexion."""
    access_token: str = Field(description="Token d'accès JWT")
    token_type: str = Field(default="bearer", description="Type de token")
    expires_in: int = Field(description="Durée de validité en secondes")
    user: User = Field(description="Informations de l'utilisateur")


class APIResponse(BaseModel):
    """Modèle générique pour les réponses API."""
    success: bool = Field(description="Statut de la requête")
    message: str = Field(description="Message de réponse")
    data: Optional[Dict[str, Any]] = Field(None, description="Données de la réponse")
    errors: Optional[List[str]] = Field(None, description="Liste des erreurs") 