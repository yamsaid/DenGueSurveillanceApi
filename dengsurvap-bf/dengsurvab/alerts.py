"""
Module de gestion des alertes pour le client Appi Dengue

Ce module gère les alertes épidémiologiques et leur configuration.
"""

from typing import List, Optional, Dict, Any
import logging

from .models import AlertLog, SeuilAlert, AlertConfigRequest
from .exceptions import AlertConfigurationError, APIError


class AlertManager:
    """
    Gestionnaire d'alertes pour le client Appi.
    
    Cette classe gère la configuration des seuils d'alerte,
    la récupération des alertes et leur vérification.
    """
    
    def __init__(self, client):
        """
        Initialise le gestionnaire d'alertes.
        
        Args:
            client: Instance du client Appi
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    def get_alertes(self,
                    limit: int = 10,
                    severity: Optional[str] = None,
                    status: Optional[str] = None,
                    region: Optional[str] = None,
                    district: Optional[str] = None,
                    date_debut: Optional[str] = None,
                    date_fin: Optional[str] = None) -> List[AlertLog]:
        """
        Récupère les alertes selon les critères.
        
        Args:
            limit: Nombre maximum d'alertes
            severity: Sévérité (warning, critical, info)
            status: Statut (active, resolved)
            region: Région
            district: District
            date_debut: Date de début
            date_fin: Date de fin
            
        Returns:
            Liste des alertes
        """
        params = {'limit': limit}
        
        if severity:
            params['severity'] = severity
        if status:
            params['status'] = status
        if region:
            params['region'] = region
        if district:
            params['district'] = district
        if date_debut:
            params['date_debut'] = date_debut
        if date_fin:
            params['date_fin'] = date_fin
        
        try:
            data = self.client._make_request("GET", "/api/alerts/logs", params=params)
            
            alertes = []
            for alerte_data in data.get('data', []):
                try:
                    alerte = AlertLog(**alerte_data)
                    alertes.append(alerte)
                except Exception as e:
                    self.logger.warning(f"Erreur de validation de l'alerte: {e}")
            
            return alertes
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des alertes: {e}")
            raise APIError(f"Impossible de récupérer les alertes: {e}")
    
    def configurer_seuils(self, **kwargs) -> Dict[str, Any]:
        """
        Configure les seuils d'alerte.
        
        Args:
            **kwargs: Paramètres de configuration
            
        Returns:
            Résultat de la configuration
            
        Raises:
            AlertConfigurationError: En cas d'erreur de configuration
        """
        try:
            # Validation des paramètres
            valid_params = [
                'seuil_positivite', 'seuil_hospitalisation', 'seuil_deces',
                'seuil_positivite_region', 'seuil_hospitalisation_region', 'seuil_deces_region',
                'seuil_positivite_district', 'seuil_hospitalisation_district', 'seuil_deces_district',
                'intervalle'
            ]
            
            config_data = {}
            for key, value in kwargs.items():
                if key in valid_params:
                    config_data[key] = value
                else:
                    self.logger.warning(f"Paramètre ignoré: {key}")
            
            # Validation des seuils
            for key, value in config_data.items():
                if 'seuil' in key and isinstance(value, (int, float)):
                    if value < 0 or value > 100:
                        raise AlertConfigurationError(
                            f"Seuil invalide pour {key}: {value}. Doit être entre 0 et 100.",
                            alert_type=key,
                            threshold=value
                        )
            
            response = self.client._make_request(
                method="POST",
                endpoint="/api/alerts/config/seuils",
                data=config_data
            )
            
            self.logger.info("Configuration des seuils réussie")
            return response
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la configuration des seuils: {e}")
            raise AlertConfigurationError(f"Impossible de configurer les seuils: {e}")
    
    def recuperer_seuils(self, usermail: str) -> SeuilAlert:
        """
        Récupère les seuils d'alerte pour un utilisateur.
        
        Args:
            usermail: Email de l'utilisateur
            
        Returns:
            Configuration des seuils
            
        Raises:
            APIError: En cas d'erreur
        """
        try:
            data = self.client._make_request(
                "GET", 
                f"/api/alerts/seuils/{usermail}"
            )
            
            return SeuilAlert(**data)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des seuils: {e}")
            raise APIError(f"Impossible de récupérer les seuils: {e}")
    
    def verifier_alertes(self,
                        date_debut: Optional[str] = None,
                        date_fin: Optional[str] = None,
                        region: str = "Toutes",
                        district: str = "Toutes") -> Dict[str, Any]:
        """
        Vérifie les alertes selon les critères.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            
        Returns:
            Résultat de la vérification
        """
        params = {
            'region': region,
            'district': district
        }
        
        if date_debut:
            params['date_debut'] = date_debut
        if date_fin:
            params['date_fin'] = date_fin
        
        try:
            response = self.client._make_request(
                method="POST",
                endpoint="/api/alerts/verifier",
                params=params
            )
            
            self.logger.info("Vérification des alertes réussie")
            return response
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification des alertes: {e}")
            raise APIError(f"Impossible de vérifier les alertes: {e}")
    
    def verification_automatique(self) -> Dict[str, Any]:
        """
        Lance une vérification automatique des alertes.
        
        Returns:
            Résultat de la vérification automatique
        """
        try:
            response = self.client._make_request(
                method="POST",
                endpoint="/api/alerts/verification-automatique"
            )
            
            self.logger.info("Vérification automatique lancée")
            return response
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification automatique: {e}")
            raise APIError(f"Impossible de lancer la vérification automatique: {e}")
    
    def obtenir_indicateurs_actuels(self,
                                  date_debut: Optional[str] = None,
                                  date_fin: Optional[str] = None,
                                  region: str = "Toutes",
                                  district: str = "Toutes") -> Dict[str, Any]:
        """
        Obtient les indicateurs actuels pour les alertes.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            
        Returns:
            Indicateurs actuels
        """
        params = {
            'region': region,
            'district': district
        }
        
        if date_debut:
            params['date_debut'] = date_debut
        if date_fin:
            params['date_fin'] = date_fin
        
        try:
            response = self.client._make_request(
                "GET",
                "/api/alerts/indicateurs",
                params=params
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des indicateurs: {e}")
            raise APIError(f"Impossible de récupérer les indicateurs: {e}")
    
    def marquer_alerte_resolue(self, alerte_id: int) -> bool:
        """
        Marque une alerte comme résolue.
        
        Args:
            alerte_id: Identifiant de l'alerte
            
        Returns:
            True si l'opération a réussi
        """
        try:
            self.client._make_request(
                method="PUT",
                endpoint=f"/api/alerts/{alerte_id}/resolve"
            )
            
            self.logger.info(f"Alerte {alerte_id} marquée comme résolue")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la résolution de l'alerte: {e}")
            raise APIError(f"Impossible de résoudre l'alerte: {e}")
    
    def exporter_alertes(self,
                        limit: int = 100,
                        usermail: Optional[str] = None,
                        region: Optional[str] = None,
                        severity: Optional[str] = None,
                        status: Optional[str] = None,
                        date_debut: Optional[str] = None,
                        date_fin: Optional[str] = None,
                        format: str = "csv") -> bytes:
        """
        Exporte les alertes dans différents formats.
        
        Args:
            limit: Nombre maximum d'alertes
            usermail: Email de l'utilisateur
            region: Région
            severity: Sévérité
            status: Statut
            date_debut: Date de début
            date_fin: Date de fin
            format: Format d'export (csv, json, excel)
            
        Returns:
            Données exportées en bytes
        """
        params = {
            'limit': limit,
            'format': format
        }
        
        if usermail:
            params['usermail'] = usermail
        if region:
            params['region'] = region
        if severity:
            params['severity'] = severity
        if status:
            params['status'] = status
        if date_debut:
            params['date_debut'] = date_debut
        if date_fin:
            params['date_fin'] = date_fin
        
        try:
            response = self.client.session.get(
                f"{self.client.base_url}/api/alerts/logs/export",
                params=params,
                headers=self.client.session.headers
            )
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export des alertes: {e}")
            raise APIError(f"Impossible d'exporter les alertes: {e}")
    
    def get_alertes_critiques(self, limit: int = 10) -> List[AlertLog]:
        """
        Récupère les alertes critiques.
        
        Args:
            limit: Nombre maximum d'alertes
            
        Returns:
            Liste des alertes critiques
        """
        return self.get_alertes(
            limit=limit,
            severity="critical",
            status="active"
        )
    
    def get_alertes_actives(self, limit: int = 10) -> List[AlertLog]:
        """
        Récupère les alertes actives.
        
        Args:
            limit: Nombre maximum d'alertes
            
        Returns:
            Liste des alertes actives
        """
        return self.get_alertes(
            limit=limit,
            status="active"
        )
    
    def get_alertes_par_region(self, region: str, limit: int = 10) -> List[AlertLog]:
        """
        Récupère les alertes pour une région spécifique.
        
        Args:
            region: Région
            limit: Nombre maximum d'alertes
            
        Returns:
            Liste des alertes pour la région
        """
        return self.get_alertes(
            limit=limit,
            region=region
        )
    
    def get_alertes_par_periode(self,
                               date_debut: str,
                               date_fin: str,
                               limit: int = 10) -> List[AlertLog]:
        """
        Récupère les alertes pour une période spécifique.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            limit: Nombre maximum d'alertes
            
        Returns:
            Liste des alertes pour la période
        """
        return self.get_alertes(
            limit=limit,
            date_debut=date_debut,
            date_fin=date_fin
        ) 