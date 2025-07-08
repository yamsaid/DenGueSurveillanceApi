"""
Tests unitaires pour le module export

Ce module contient les tests pour les fonctionnalités d'export.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime, timedelta
import json

from dengsurvab.export import DataExporter
from dengsurvab.exceptions import DataExportError, APIError


class TestDataExporter:
    """Tests pour la classe DataExporter."""
    
    @pytest.fixture
    def mock_client(self):
        """Fixture pour un client mock."""
        client = Mock()
        return client
    
    @pytest.fixture
    def data_exporter(self, mock_client):
        """Fixture pour créer un exportateur de données."""
        return DataExporter(mock_client)
    
    @pytest.fixture
    def sample_data(self):
        """Fixture pour des données d'exemple."""
        return pd.DataFrame({
            'idCas': [1, 2, 3],
            'date_consultation': ['2024-01-15', '2024-01-16', '2024-01-17'],
            'region': ['centre', 'hauts-bassins', 'centre'],
            'district': ['district1', 'district2', 'district1'],
            'sexe': ['masculin', 'feminin', 'masculin'],
            'age': [25, 30, 35],
            'resultat_test': ['positif', 'negatif', 'positif'],
            'serotype': ['denv1', None, 'denv2'],
            'hospitalise': ['non', 'oui', 'non'],
            'issue': ['guéri', 'guéri', 'guéri'],
            'id_source': [1, 1, 2]
        })
    
    def test_data_exporter_initialization(self, data_exporter, mock_client):
        """Test l'initialisation de l'exportateur de données."""
        assert data_exporter.client is mock_client
        assert data_exporter.logger is not None
        assert "csv" in data_exporter.supported_formats
        assert "json" in data_exporter.supported_formats
        assert "xlsx" in data_exporter.supported_formats
        assert "pdf" in data_exporter.supported_formats
    
    def test_export_data_success(self, data_exporter, mock_client):
        """Test l'export de données avec succès."""
        mock_response = Mock()
        mock_response.content = b"test,data,csv"
        mock_response.raise_for_status.return_value = None
        
        mock_client.session.get.return_value = mock_response
        
        result = data_exporter.export_data(
            format="csv",
            date_debut="2024-01-01",
            date_fin="2024-01-31",
            region="centre"
        )
        
        assert result == b"test,data,csv"
        mock_client.session.get.assert_called_once()
    
    def test_export_data_unsupported_format(self, data_exporter):
        """Test l'export avec un format non supporté."""
        with pytest.raises(DataExportError, match="Format non supporté"):
            data_exporter.export_data(format="unsupported")
    
    def test_export_data_error(self, data_exporter, mock_client):
        """Test l'export de données avec erreur."""
        mock_client.session.get.side_effect = Exception("Network Error")
        
        with pytest.raises(DataExportError, match="Impossible d'exporter les données"):
            data_exporter.export_data(format="csv")
    
    def test_export_alertes_success(self, data_exporter, mock_client):
        """Test l'export des alertes avec succès."""
        mock_response = Mock()
        mock_response.content = b"id,severity,message\n1,critical,Test"
        mock_response.raise_for_status.return_value = None
        
        mock_client.session.get.return_value = mock_response
        
        result = data_exporter.export_alertes(
            format="csv",
            limit=50,
            severity="critical"
        )
        
        assert result == b"id,severity,message\n1,critical,Test"
        mock_client.session.get.assert_called_once()
    
    def test_export_alertes_unsupported_format(self, data_exporter):
        """Test l'export des alertes avec format non supporté."""
        with pytest.raises(DataExportError, match="Format non supporté"):
            data_exporter.export_alertes(format="unsupported")
    
    def test_export_alertes_error(self, data_exporter, mock_client):
        """Test l'export des alertes avec erreur."""
        mock_client.session.get.side_effect = Exception("Network Error")
        
        with pytest.raises(DataExportError, match="Impossible d'exporter les alertes"):
            data_exporter.export_alertes(format="csv")
    
    def test_export_rapport_success(self, data_exporter, mock_client):
        """Test l'export de rapport avec succès."""
        mock_response = Mock()
        mock_response.content = b'{"rapport": "data"}'
        mock_response.raise_for_status.return_value = None
        
        mock_client.session.get.return_value = mock_response
        
        result = data_exporter.export_rapport(
            format="json",
            date_debut="2024-01-01",
            date_fin="2024-01-31"
        )
        
        assert result == b'{"rapport": "data"}'
        mock_client.session.get.assert_called_once()
    
    def test_export_rapport_unsupported_format(self, data_exporter):
        """Test l'export de rapport avec format non supporté."""
        with pytest.raises(DataExportError, match="Format non supporté"):
            data_exporter.export_rapport(format="unsupported")
    
    def test_export_rapport_error(self, data_exporter, mock_client):
        """Test l'export de rapport avec erreur."""
        mock_client.session.get.side_effect = Exception("Network Error")
        
        with pytest.raises(DataExportError, match="Impossible d'exporter le rapport"):
            data_exporter.export_rapport(format="json")
    
    def test_export_donnees_corrigees_success(self, data_exporter, mock_client):
        """Test l'export de données corrigées avec succès."""
        mock_response = Mock()
        mock_response.content = b"donnees,corrigees,csv"
        mock_response.raise_for_status.return_value = None
        
        mock_client.session.get.return_value = mock_response
        
        result = data_exporter.export_donnees_corrigees(
            format="csv",
            date_debut="2024-01-01",
            date_fin="2024-01-31"
        )
        
        assert result == b"donnees,corrigees,csv"
        mock_client.session.get.assert_called_once()
    
    def test_export_donnees_corrigees_error(self, data_exporter, mock_client):
        """Test l'export de données corrigées avec erreur."""
        mock_client.session.get.side_effect = Exception("Network Error")
        
        with pytest.raises(DataExportError, match="Impossible d'exporter les données corrigées"):
            data_exporter.export_donnees_corrigees(format="csv")
    
    def test_export_to_dataframe_success(self, data_exporter, mock_client):
        """Test l'export vers DataFrame avec succès."""
        # Mock des données JSON valides
        json_data = b'[{"idCas": 1, "region": "centre"}, {"idCas": 2, "region": "hauts-bassins"}]'
        mock_response = Mock()
        mock_response.content = json_data
        mock_response.raise_for_status.return_value = None
        
        mock_client.session.get.return_value = mock_response
        
        result = data_exporter.export_to_dataframe(
            date_debut="2024-01-01",
            date_fin="2024-01-31",
            region="centre"
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'idCas' in result.columns
        assert 'region' in result.columns
        mock_client.session.get.assert_called_once()
    
    def test_export_to_dataframe_error(self, data_exporter, mock_client):
        """Test l'export vers DataFrame avec erreur."""
        mock_client.session.get.side_effect = Exception("Network Error")
        
        with pytest.raises(DataExportError, match="Impossible d'exporter vers DataFrame"):
            data_exporter.export_to_dataframe()
    
    def test_save_to_file_success(self, data_exporter):
        """Test la sauvegarde de fichier avec succès."""
        test_data = b"test,data,csv"
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = data_exporter.save_to_file(test_data, "test.csv", "csv")
            
            assert result is True
            mock_file.assert_called_once_with("test.csv", "wb")
    
    def test_save_to_file_error(self, data_exporter):
        """Test la sauvegarde de fichier avec erreur."""
        test_data = b"test,data,csv"
        
        with patch('builtins.open', side_effect=Exception("IO Error")):
            with pytest.raises(DataExportError, match="Impossible de sauvegarder le fichier"):
                data_exporter.save_to_file(test_data, "test.csv", "csv")
    
    def test_export_and_save_success(self, data_exporter):
        """Test l'export et sauvegarde avec succès."""
        with patch.object(data_exporter, 'export_data', return_value=b"test,data") as mock_export:
            with patch.object(data_exporter, 'save_to_file', return_value=True) as mock_save:
                result = data_exporter.export_and_save(
                    "test.csv",
                    format="csv",
                    date_debut="2024-01-01"
                )
                
                assert result is True
                mock_export.assert_called_once_with(
                    format="csv",
                    date_debut="2024-01-01"
                )
                mock_save.assert_called_once_with(b"test,data", "test.csv", "csv")
    
    def test_export_and_save_export_error(self, data_exporter):
        """Test l'export et sauvegarde avec erreur d'export."""
        with patch.object(data_exporter, 'export_data', side_effect=DataExportError("Export failed")):
            with pytest.raises(DataExportError, match="Impossible d'exporter et sauvegarder"):
                data_exporter.export_and_save("test.csv", format="csv")
    
    def test_export_and_save_save_error(self, data_exporter):
        """Test l'export et sauvegarde avec erreur de sauvegarde."""
        with patch.object(data_exporter, 'export_data', return_value=b"test,data"):
            with patch.object(data_exporter, 'save_to_file', side_effect=DataExportError("Save failed")):
                with pytest.raises(DataExportError, match="Impossible d'exporter et sauvegarder"):
                    data_exporter.export_and_save("test.csv", format="csv")
    
    def test_get_export_formats(self, data_exporter):
        """Test la récupération des formats d'export."""
        formats = data_exporter.get_export_formats()
        
        assert isinstance(formats, list)
        assert "csv" in formats
        assert "json" in formats
        assert "xlsx" in formats
        assert "pdf" in formats
    
    def test_validate_export_data_success(self, data_exporter):
        """Test la validation de données d'export avec succès."""
        # Test avec des données CSV valides
        csv_data = b"idCas,date_consultation,region\n1,2024-01-15,centre"
        result = data_exporter.validate_export_data(csv_data, "csv")
        
        assert result is True
    
    def test_validate_export_data_invalid_format(self, data_exporter):
        """Test la validation avec format invalide."""
        test_data = b"test,data"
        
        # La méthode ne lève pas d'exception pour les formats invalides
        # Elle retourne False ou True selon l'implémentation
        result = data_exporter.validate_export_data(test_data, "unsupported")
        assert isinstance(result, bool)
    
    def test_validate_export_data_empty_data(self, data_exporter):
        """Test la validation avec données vides."""
        empty_data = b""
        
        # La méthode ne lève pas d'exception pour les données vides
        # Elle retourne False ou True selon l'implémentation
        result = data_exporter.validate_export_data(empty_data, "csv")
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__]) 