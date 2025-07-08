"""
Tests unitaires pour le module alerts

Ce module contient les tests pour les fonctionnalités d'alertes.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from dengsurvab.alerts import AlertManager
from dengsurvab.models import AlertLog, SeuilAlert
from dengsurvab.exceptions import AlertConfigurationError, APIError


class TestAlertManager:
    """Tests pour la classe AlertManager."""
    
    @pytest.fixture
    def mock_client(self):
        """Fixture pour un client mock."""
        client = Mock()
        return client
    
    @pytest.fixture
    def alert_manager(self, mock_client):
        """Fixture pour créer un gestionnaire d'alertes."""
        return AlertManager(mock_client)
    
    def test_alert_manager_initialization(self, alert_manager, mock_client):
        """Test l'initialisation du gestionnaire d'alertes."""
        assert alert_manager.client is mock_client
        assert alert_manager.logger is not None
    
    def test_get_alertes_success(self, alert_manager, mock_client):
        """Test la récupération réussie des alertes."""
        # Mock des données d'alerte
        mock_alert_data = [
            {
                "id": 1,
                "severity": "critical",
                "status": "active",
                "message": "Seuil dépassé",
                "region": "centre",
                "created_at": "2024-01-15T10:30:00"
            },
            {
                "id": 2,
                "severity": "warning",
                "status": "resolved",
                "message": "Tendance à la hausse",
                "region": "hauts-bassins",
                "created_at": "2024-01-14T15:45:00"
            }
        ]
        
        mock_client._make_request.return_value = mock_alert_data
        
        alertes = alert_manager.get_alertes(
            limit=10,
            severity="critical",
            status="active"
        )
        
        assert len(alertes) == 2
        assert isinstance(alertes[0], AlertLog)
        assert alertes[0].severity == "critical"
        assert alertes[1].severity == "warning"
        
        # Vérifier que la requête a été appelée avec les bons paramètres
        mock_client._make_request.assert_called_once_with(
            "GET", 
            "/api/alerts/logs", 
            params={'limit': 10, 'severity': 'critical', 'status': 'active'}
        )
    
    def test_get_alertes_error(self, alert_manager, mock_client):
        """Test la récupération des alertes avec erreur."""
        mock_client._make_request.side_effect = Exception("API Error")
        
        with pytest.raises(APIError, match="Impossible de récupérer les alertes"):
            alert_manager.get_alertes()
    
    def test_configurer_seuils_success(self, alert_manager, mock_client):
        """Test la configuration réussie des seuils."""
        mock_response = {"message": "Seuils configurés avec succès"}
        mock_client._make_request.return_value = mock_response
        
        result = alert_manager.configurer_seuils(
            seuil_positivite=50.0,
            seuil_hospitalisation=15.0,
            seuil_deces=2.0
        )
        
        assert result == mock_response
        # Vérifier que la méthode a été appelée avec les bons paramètres
        called_args, called_kwargs = mock_client._make_request.call_args
        assert called_kwargs['method'] == "POST"
        assert called_kwargs['endpoint'] == "/api/alerts/config/seuils"
        assert called_kwargs['data']['seuil_positivite'] == 50.0
        assert called_kwargs['data']['seuil_hospitalisation'] == 15.0
        assert called_kwargs['data']['seuil_deces'] == 2.0
    
    def test_configurer_seuils_invalid_threshold(self, alert_manager):
        """Test la configuration des seuils avec valeur invalide."""
        with pytest.raises(AlertConfigurationError, match="Seuil invalide"):
            alert_manager.configurer_seuils(seuil_positivite=150.0)
    
    def test_configurer_seuils_error(self, alert_manager, mock_client):
        """Test la configuration des seuils avec erreur."""
        mock_client._make_request.side_effect = Exception("API Error")
        
        with pytest.raises(AlertConfigurationError, match="Impossible de configurer les seuils"):
            alert_manager.configurer_seuils(seuil_positivite=50.0)
    
    def test_recuperer_seuils_success(self, alert_manager, mock_client):
        """Test la récupération réussie des seuils."""
        mock_seuil_data = {
            "id": 1,
            "seuil_positivite": 50.0,
            "seuil_hospitalisation": 15.0,
            "seuil_deces": 2.0,
            "usermail": "test@example.com"
        }
        mock_client._make_request.return_value = mock_seuil_data
        
        result = alert_manager.recuperer_seuils("test@example.com")
        
        assert isinstance(result, SeuilAlert)
        assert result.seuil_positivite == 50.0
        assert result.seuil_hospitalisation == 15.0
        assert result.seuil_deces == 2.0
        
        # Vérifier que la méthode a été appelée avec les bons paramètres
        called_args, called_kwargs = mock_client._make_request.call_args
        assert called_args[0] == "GET"
        assert called_args[1] == "/api/alerts/seuils/test@example.com"
    
    def test_recuperer_seuils_error(self, alert_manager, mock_client):
        """Test la récupération des seuils avec erreur."""
        mock_client._make_request.side_effect = Exception("API Error")
        
        with pytest.raises(APIError, match="Impossible de récupérer les seuils"):
            alert_manager.recuperer_seuils("test@example.com")
    
    def test_verifier_alertes_success(self, alert_manager, mock_client):
        """Test la vérification réussie des alertes."""
        mock_response = {
            "alertes_actives": 5,
            "alertes_critiques": 2,
            "seuils_depasses": ["positivite", "hospitalisation"]
        }
        mock_client._make_request.return_value = mock_response
        
        result = alert_manager.verifier_alertes(
            date_debut="2024-01-01",
            date_fin="2024-01-31",
            region="centre",
            district="hauts-bassins"
        )
        
        assert result == mock_response
        # Vérifier que la méthode a été appelée avec les bons paramètres
        called_args, called_kwargs = mock_client._make_request.call_args
        assert called_kwargs['method'] == "POST"
        assert called_kwargs['endpoint'] == "/api/alerts/verifier"
        assert called_kwargs['params']['region'] == 'centre'
        assert called_kwargs['params']['district'] == 'hauts-bassins'
        assert called_kwargs['params']['date_debut'] == '2024-01-01'
        assert called_kwargs['params']['date_fin'] == '2024-01-31'
    
    def test_verifier_alertes_error(self, alert_manager, mock_client):
        """Test la vérification des alertes avec erreur."""
        mock_client._make_request.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            alert_manager.verifier_alertes()
    
    def test_verification_automatique(self, alert_manager, mock_client):
        """Test la vérification automatique des alertes."""
        mock_response = {
            "verification_effectuee": True,
            "alertes_nouvelles": 3,
            "alertes_resolues": 1
        }
        mock_client._make_request.return_value = mock_response
        
        result = alert_manager.verification_automatique()
        
        assert result == mock_response
        # Vérifier que la méthode a été appelée avec les bons paramètres
        called_args, called_kwargs = mock_client._make_request.call_args
        assert called_kwargs['method'] == "POST"
        assert called_kwargs['endpoint'] == "/api/alerts/verification-automatique"
    
    def test_obtenir_indicateurs_actuels(self, alert_manager, mock_client):
        """Test l'obtention des indicateurs actuels."""
        mock_response = {
            "taux_positivite": 45.5,
            "taux_hospitalisation": 12.3,
            "taux_letalite": 1.8,
            "total_cas": 1250
        }
        mock_client._make_request.return_value = mock_response
        
        result = alert_manager.obtenir_indicateurs_actuels(
            date_debut="2024-01-01",
            date_fin="2024-01-31",
            region="centre"
        )
        
        assert result == mock_response
        # Vérifier que la méthode a été appelée avec les bons paramètres
        called_args, called_kwargs = mock_client._make_request.call_args
        assert called_args[0] == "GET"
        assert called_args[1] == "/api/alerts/indicateurs"
        assert called_kwargs['params']['region'] == 'centre'
        assert called_kwargs['params']['district'] == 'Toutes'
        assert called_kwargs['params']['date_debut'] == '2024-01-01'
        assert called_kwargs['params']['date_fin'] == '2024-01-31'
    
    def test_marquer_alerte_resolue(self, alert_manager, mock_client):
        """Test le marquage d'une alerte comme résolue."""
        mock_response = {"message": "Alerte résolue avec succès"}
        mock_client._make_request.return_value = mock_response
        
        result = alert_manager.marquer_alerte_resolue(1)
        
        assert result is True
        # Vérifier que la méthode a été appelée avec les bons paramètres
        called_args, called_kwargs = mock_client._make_request.call_args
        assert called_kwargs['method'] == "PUT"
        assert called_kwargs['endpoint'] == "/api/alerts/1/resolve"
    
    def test_marquer_alerte_resolue_error(self, alert_manager, mock_client):
        """Test le marquage d'une alerte avec erreur."""
        mock_client._make_request.side_effect = Exception("API Error")
        
        with pytest.raises(APIError, match="Impossible de résoudre l'alerte"):
            alert_manager.marquer_alerte_resolue(1)
    
    def test_exporter_alertes(self, alert_manager, mock_client):
        """Test l'export des alertes."""
        mock_data = b"id,severity,message\n1,critical,Test alert"
        # Simuler le comportement réel : le code appelle self.client.session.get().content
        mock_session = Mock()
        mock_session.get.return_value.content = mock_data
        mock_client.session = mock_session
        
        result = alert_manager.exporter_alertes(
            limit=50,
            severity="critical",
            format="csv"
        )
        
        assert result == mock_data
        mock_session.get.assert_called_once()
    
    def test_get_alertes_critiques(self, alert_manager, mock_client):
        """Test la récupération des alertes critiques."""
        mock_alert_data = [
            {
                "id": 1,
                "severity": "critical",
                "status": "active",
                "message": "Seuil critique dépassé"
            }
        ]
        mock_client._make_request.return_value = mock_alert_data
        
        alertes = alert_manager.get_alertes_critiques(limit=5)
        
        assert len(alertes) == 1
        assert alertes[0].severity == "critical"
        # Accepter des paramètres supplémentaires dans l'appel
        called_args, called_kwargs = mock_client._make_request.call_args
        assert called_args[0] == "GET"
        assert called_args[1] == "/api/alerts/logs"
        assert 'limit' in called_kwargs['params']
        assert 'severity' in called_kwargs['params']
        assert called_kwargs['params']['severity'] == 'critical'
    
    def test_get_alertes_actives(self, alert_manager, mock_client):
        """Test la récupération des alertes actives."""
        mock_alert_data = [
            {
                "id": 1,
                "severity": "warning",
                "status": "active",
                "message": "Alerte active"
            }
        ]
        mock_client._make_request.return_value = mock_alert_data
        
        alertes = alert_manager.get_alertes_actives(limit=5)
        
        assert len(alertes) == 1
        assert alertes[0].status == "active"
        mock_client._make_request.assert_called_once_with(
            "GET",
            "/api/alerts/logs",
            params={'limit': 5, 'status': 'active'}
        )
    
    def test_get_alertes_par_region(self, alert_manager, mock_client):
        """Test la récupération des alertes par région."""
        mock_alert_data = [
            {
                "id": 1,
                "severity": "warning",
                "region": "centre",
                "message": "Alerte région"
            }
        ]
        mock_client._make_request.return_value = mock_alert_data
        
        alertes = alert_manager.get_alertes_par_region("centre", limit=5)
        
        assert len(alertes) == 1
        assert alertes[0].region == "centre"
        mock_client._make_request.assert_called_once_with(
            "GET",
            "/api/alerts/logs",
            params={'limit': 5, 'region': 'centre'}
        )
    
    def test_get_alertes_par_periode(self, alert_manager, mock_client):
        """Test la récupération des alertes par période."""
        mock_alert_data = [
            {
                "id": 1,
                "severity": "info",
                "created_at": "2024-01-15T10:30:00",
                "message": "Alerte période"
            }
        ]
        mock_client._make_request.return_value = mock_alert_data
        
        alertes = alert_manager.get_alertes_par_periode(
            "2024-01-01",
            "2024-01-31",
            limit=5
        )
        
        assert len(alertes) == 1
        mock_client._make_request.assert_called_once_with(
            "GET",
            "/api/alerts/logs",
            params={
                'limit': 5,
                'date_debut': '2024-01-01',
                'date_fin': '2024-01-31'
            }
        )


if __name__ == "__main__":
    pytest.main([__file__]) 