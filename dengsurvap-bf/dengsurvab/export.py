"""
Module d'export de données pour le client Appi Dengue

Ce module gère l'export des données dans différents formats.
"""

import io
import pandas as pd
from typing import Optional, Dict, Any, List
import logging

from .exceptions import DataExportError, APIError


class DataExporter:
    """
    Exportateur de données pour le client Appi.
    
    Cette classe gère l'export des données dans différents formats
    (CSV, JSON, Excel) avec validation et gestion d'erreurs.
    """
    
    def __init__(self, client):
        """
        Initialise l'exportateur de données.
        
        Args:
            client: Instance du client Appi
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
        
        # Formats supportés
        self.supported_formats = ["csv", "json", "xlsx", "pdf"]
    
    def export_data(self,
                   format: str = "csv",
                   date_debut: Optional[str] = None,
                   date_fin: Optional[str] = None,
                   region: Optional[str] = None,
                   district: Optional[str] = None,
                   limit: Optional[int] = None) -> bytes:
        """
        Exporte les données dans différents formats.
        
        Args:
            format: Format d'export (csv, json, xlsx)
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            limit: Nombre maximum d'enregistrements
            
        Returns:
            Données exportées en bytes
            
        Raises:
            DataExportError: En cas d'erreur d'export
        """
        if format not in self.supported_formats:
            raise DataExportError(
                f"Format non supporté: {format}. Formats supportés: {self.supported_formats}",
                format=format
            )
        
        try:
            params = {'format': format}
            
            if date_debut:
                params['date_debut'] = date_debut
            if date_fin:
                params['date_fin'] = date_fin
            if region:
                params['region'] = region
            if district:
                params['district'] = district
            if limit:
                params['limit'] = limit
            
            # Effectuer la requête d'export
            response = self.client.session.get(
                f"{self.client.base_url}/export-data",
                params=params,
                headers=self.client.session.headers
            )
            response.raise_for_status()
            
            self.logger.info(f"Export réussi au format {format}")
            return response.content
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export: {e}")
            raise DataExportError(
                f"Impossible d'exporter les données: {e}",
                format=format
            )
    
    def export_alertes(self,
                      format: str = "csv",
                      limit: int = 100,
                      severity: Optional[str] = None,
                      status: Optional[str] = None) -> bytes:
        """
        Exporte les alertes dans différents formats.
        
        Args:
            format: Format d'export (csv, json, xlsx)
            limit: Nombre maximum d'alertes
            severity: Sévérité
            status: Statut
            
        Returns:
            Alertes exportées en bytes
            
        Raises:
            DataExportError: En cas d'erreur d'export
        """
        if format not in self.supported_formats:
            raise DataExportError(
                f"Format non supporté: {format}. Formats supportés: {self.supported_formats}",
                format=format
            )
        
        try:
            params = {
                'format': format,
                'limit': limit
            }
            
            if severity:
                params['severity'] = severity
            if status:
                params['status'] = status
            
            # Effectuer la requête d'export
            response = self.client.session.get(
                f"{self.client.base_url}/api/alerts/logs/export",
                params=params,
                headers=self.client.session.headers
            )
            response.raise_for_status()
            
            self.logger.info(f"Export des alertes réussi au format {format}")
            return response.content
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export des alertes: {e}")
            raise DataExportError(
                f"Impossible d'exporter les alertes: {e}",
                format=format
            )
    
    def export_rapport(self,
                      format: str = "json",
                      date_debut: Optional[str] = None,
                      date_fin: Optional[str] = None) -> bytes:
        """
        Exporte un rapport d'analyse.
        
        Args:
            format: Format d'export (json, csv, pdf)
            date_debut: Date de début
            date_fin: Date de fin
            
        Returns:
            Rapport exporté en bytes
            
        Raises:
            DataExportError: En cas d'erreur d'export
        """
        if format not in self.supported_formats:
            raise DataExportError(
                f"Format non supporté: {format}. Formats supportés: {self.supported_formats}",
                format=format
            )
        
        try:
            params = {'format': format}
            
            if date_debut:
                params['date_debut'] = date_debut
            if date_fin:
                params['date_fin'] = date_fin
            
            # Effectuer la requête d'export
            response = self.client.session.get(
                f"{self.client.base_url}/export-rapport",
                params=params,
                headers=self.client.session.headers
            )
            response.raise_for_status()
            
            self.logger.info(f"Export du rapport réussi au format {format}")
            return response.content
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export du rapport: {e}")
            raise DataExportError(
                f"Impossible d'exporter le rapport: {e}",
                format=format
            )
    
    def export_donnees_corrigees(self,
                                format: str = "csv",
                                date_debut: Optional[str] = None,
                                date_fin: Optional[str] = None) -> bytes:
        """
        Exporte les données corrigées.
        
        Args:
            format: Format d'export (csv, json, xlsx)
            date_debut: Date de début
            date_fin: Date de fin
            
        Returns:
            Données corrigées exportées en bytes
            
        Raises:
            DataExportError: En cas d'erreur d'export
        """
        if format not in self.supported_formats:
            raise DataExportError(
                f"Format non supporté: {format}. Formats supportés: {self.supported_formats}",
                format=format
            )
        
        try:
            params = {'format': format}
            
            if date_debut:
                params['date_debut'] = date_debut
            if date_fin:
                params['date_fin'] = date_fin
            
            # Effectuer la requête d'export
            response = self.client.session.get(
                f"{self.client.base_url}/export-corrected",
                params=params,
                headers=self.client.session.headers
            )
            response.raise_for_status()
            
            self.logger.info(f"Export des données corrigées réussi au format {format}")
            return response.content
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export des données corrigées: {e}")
            raise DataExportError(
                f"Impossible d'exporter les données corrigées: {e}",
                format=format
            )
    
    def export_to_dataframe(self,
                           date_debut: Optional[str] = None,
                           date_fin: Optional[str] = None,
                           region: Optional[str] = None,
                           district: Optional[str] = None,
                           limit: Optional[int] = None) -> pd.DataFrame:
        """
        Exporte les données vers un DataFrame pandas.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            limit: Nombre maximum d'enregistrements
            
        Returns:
            DataFrame avec les données
            
        Raises:
            DataExportError: En cas d'erreur
        """
        try:
            # Récupérer les données au format JSON
            data_bytes = self.export_data(
                format="json",
                date_debut=date_debut,
                date_fin=date_fin,
                region=region,
                district=district,
                limit=limit
            )
            
            # Convertir en DataFrame
            import json
            data = json.loads(data_bytes.decode('utf-8'))
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
            else:
                df = pd.DataFrame([data])
            
            self.logger.info(f"Export vers DataFrame réussi: {len(df)} lignes")
            return df
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export vers DataFrame: {e}")
            raise DataExportError(f"Impossible d'exporter vers DataFrame: {e}")
    
    def save_to_file(self,
                    data_bytes: bytes,
                    file_path: str,
                    format: str) -> bool:
        """
        Sauvegarde les données exportées dans un fichier.
        
        Args:
            data_bytes: Données en bytes
            file_path: Chemin du fichier
            format: Format des données
            
        Returns:
            True si la sauvegarde a réussi
            
        Raises:
            DataExportError: En cas d'erreur
        """
        try:
            with open(file_path, 'wb') as f:
                f.write(data_bytes)
            
            self.logger.info(f"Données sauvegardées dans {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {e}")
            raise DataExportError(
                f"Impossible de sauvegarder le fichier: {e}",
                file_path=file_path,
                format=format
            )
    
    def export_and_save(self,
                       file_path: str,
                       format: str = "csv",
                       **kwargs) -> bool:
        """
        Exporte et sauvegarde les données en une seule opération.
        
        Args:
            file_path: Chemin du fichier
            format: Format d'export
            **kwargs: Paramètres d'export
            
        Returns:
            True si l'opération a réussi
        """
        try:
            data_bytes = self.export_data(format=format, **kwargs)
            return self.save_to_file(data_bytes, file_path, format)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export et sauvegarde: {e}")
            raise DataExportError(f"Impossible d'exporter et sauvegarder: {e}")
    
    def get_export_formats(self) -> List[str]:
        """
        Récupère la liste des formats d'export supportés.
        
        Returns:
            Liste des formats supportés
        """
        return self.supported_formats.copy()
    
    def validate_export_data(self, data_bytes: bytes, format: str) -> bool:
        """
        Valide les données exportées.
        
        Args:
            data_bytes: Données en bytes
            format: Format des données
            
        Returns:
            True si les données sont valides
        """
        try:
            if format == "json":
                import json
                json.loads(data_bytes.decode('utf-8'))
            elif format == "csv":
                # Vérifier que c'est du CSV valide
                pd.read_csv(io.BytesIO(data_bytes))
            elif format == "xlsx":
                # Vérifier que c'est du Excel valide
                pd.read_excel(io.BytesIO(data_bytes))
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Validation échouée pour le format {format}: {e}")
            return False 

# ==================== DONNÉES ET EXPORT ====================


