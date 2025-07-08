"""
Tests unitaires pour le client Appi Dengue

Ce module contient les tests pour la classe AppiClient et ses fonctionnalités.
"""

import pytest
import responses
from unittest.mock import Mock, patch
from datetime import datetime, date

from dengsurvab.client import AppiClient
from dengsurvab.models import CasDengue, AlertLog, User
from dengsurvab.exceptions import (
    AppiException, AuthenticationError, APIError, ValidationError
)


class TestAppiClient:
    """Tests pour la classe AppiClient."""
    
    @pytest.fixture
    def client(self):
        """Fixture pour créer un client de test."""
        return AppiClient(
            base_url="https://api.test.com",
            api_key="test-key",
            debug=False
        )
    
    @pytest.fixture
    def mock_response(self):
        """Fixture pour une réponse mock."""
        return {
            "idCas": 1,
            "date_consultation": "2024-01-15",
            "region": "Antananarivo",
            "district": "Analamanga",
            "sexe": "masculin",
            "age": 25,
            "resultat_test": "positif",
            "serotype": "denv2",
            "hospitalise": "non",
            "issue": "guéri",
            "id_source": 1
        }
    
    def test_client_initialization(self, client):
        """Test l'initialisation du client."""
        assert client.base_url == "https://api.test.com"
        assert client.api_key == "test-key"
        assert client.timeout == 30
        assert client.retry_attempts == 3
        assert "Authorization" in client.session.headers
    
    def test_client_from_env(self):
        """Test la création du client depuis les variables d'environnement."""
        with patch.dict('os.environ', {
            'APPI_API_URL': 'https://api.env.com',
            'APPI_API_KEY': 'env-key',
            'APPI_DEBUG': 'true'
        }):
            client = AppiClient.from_env()
            assert client.base_url == "https://api.env.com"
            assert client.api_key == "env-key"
            assert client.debug is True
    
    def test_client_from_env_missing_url(self):
        """Test la création du client avec URL manquante."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(AppiException, match="Variable d'environnement APPI_API_URL requise"):
                AppiClient.from_env()
    
    @responses.activate
    def test_make_request_success(self, client, mock_response):
        """Test une requête réussie."""
        responses.add(
            responses.GET,
            "https://api.test.com/test",
            json=mock_response,
            status=200
        )
        
        result = client._make_request("GET", "/test")
        assert result == mock_response
    
    @responses.activate
    def test_make_request_api_error(self, client):
        """Test une erreur API."""
        responses.add(
            responses.GET,
            "https://api.test.com/test",
            json={"detail": "Erreur API"},
            status=400
        )
        
        with pytest.raises(ValidationError):
            client._make_request("GET", "/test")
    
    @responses.activate
    def test_make_request_authentication_error(self, client):
        """Test une erreur d'authentification."""
        responses.add(
            responses.GET,
            "https://api.test.com/test",
            json={"detail": "Token invalide"},
            status=401
        )
        
        with pytest.raises(AuthenticationError):
            client._make_request("GET", "/test")
    
    @responses.activate
    def test_make_request_connection_error(self, client):
        """Test une erreur de connexion."""
        responses.add(
            responses.GET,
            "https://api.test.com/test",
            body=Exception("Connection failed")
        )
        
        with pytest.raises(Exception):
            client._make_request("GET", "/test")
    
    @responses.activate
    def test_get_cas_dengue(self, client):
        """Test la récupération des cas de dengue."""
        mock_data = {
            "data": [
                {
                    "idCas": 1,
                    "date_consultation": "2024-01-15",
                    "region": "Antananarivo",
                    "district": "Analamanga",
                    "sexe": "masculin",
                    "age": 25,
                    "resultat_test": "positif",
                    "serotype": "denv2",
                    "hospitalise": "non",
                    "issue": "guéri",
                    "id_source": 1
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://api.test.com/api/data/hebdomadaires",
            json=mock_data,
            status=200
        )
        
        cas = client.get_cas_dengue(
            date_debut="2024-01-01",
            date_fin="2024-01-31"
        )
        
        assert len(cas) == 1
        assert isinstance(cas[0], CasDengue)
        assert cas[0].idCas == 1
        assert cas[0].region == "Antananarivo"
    
    @responses.activate
    def test_get_stats(self, client):
        """Test la récupération des statistiques."""
        mock_stats = {
            "total_cas": 1000,
            "total_positifs": 500,
            "total_hospitalisations": 100,
            "total_deces": 10,
            "regions_actives": ["Antananarivo", "Fianarantsoa"],
            "districts_actifs": ["Analamanga", "Haute Matsiatra"],
            "derniere_mise_a_jour": "2024-01-15T10:30:00"
        }
        
        responses.add(
            responses.GET,
            "https://api.test.com/api/stats",
            json=mock_stats,
            status=200
        )
        
        stats = client.get_stats()
        assert stats.total_cas == 1000
        assert stats.total_positifs == 500
        assert len(stats.regions_actives) == 2
    
    @responses.activate
    def test_get_regions(self, client):
        """Test la récupération des régions."""
        mock_regions = {
            "regions": ["Antananarivo", "Fianarantsoa", "Toamasina"]
        }
        
        responses.add(
            responses.GET,
            "https://api.test.com/api/regions",
            json=mock_regions,
            status=200
        )
        
        regions = client.get_regions()
        assert regions == ["Antananarivo", "Fianarantsoa", "Toamasina"]
    
    @responses.activate
    def test_get_districts(self, client):
        """Test la récupération des districts."""
        mock_districts = {
            "districts": ["Analamanga", "Haute Matsiatra", "Atsinanana"]
        }
        
        responses.add(
            responses.GET,
            "https://api.test.com/api/districts",
            json=mock_districts,
            status=200
        )
        
        districts = client.get_districts(region="Antananarivo")
        assert districts == ["Analamanga", "Haute Matsiatra", "Atsinanana"]
    
    @responses.activate
    def test_data_period(self, client):
        """Test la récupération des indicateurs hebdomadaires."""
        mock_indicateurs = [
            {
                "date_debut": "2024-01-01",
                "date_fin": "2024-01-07",
                "region": "Toutes",
                "district": "Toutes",
                "total_cas": 100,
                "cas_positifs": 50,
                "cas_negatifs": 50,
                "hospitalisations": 10,
                "deces": 2,
                "taux_positivite": 50.0,
                "taux_hospitalisation": 10.0,
                "taux_letalite": 2.0
            }
        ]
        
        responses.add(
            responses.GET,
            "https://api.test.com/indicateurs/indicateurs_hebdo",
            json=mock_indicateurs,
            status=200
        )
        
        indicateurs = client.data_period(
            date_debut="2024-01-01",
            date_fin="2024-01-31"
        )
        
        assert len(indicateurs) == 1
        assert indicateurs[0].total_cas == 100
        assert indicateurs[0].taux_positivite == 50.0
    
    @responses.activate
    def test_get_alertes(self, client):
        """Test la récupération des alertes."""
        mock_alertes = [
            {
                "id": 1,
                "severity": "critical",
                "status": "active",
                "message": "Seuil dépassé",
                "region": "Antananarivo",
                "created_at": "2024-01-15T10:30:00"
            }
        ]
        
        responses.add(
            responses.GET,
            "https://api.test.com/api/alerts/logs",
            json=mock_alertes,
            status=200
        )
        
        alertes = client.get_alertes(limit=10)
        assert len(alertes) == 1
        assert isinstance(alertes[0], AlertLog)
        assert alertes[0].severity == "critical"
    
    @responses.activate
    def test_export_data(self, client):
        """Test l'export de données."""
        mock_csv_data = b"idCas,date_consultation,region\n1,2024-01-15,Antananarivo"
        
        responses.add(
            responses.GET,
            "https://api.test.com/export-data",
            body=mock_csv_data,
            status=200,
            content_type="text/csv"
        )
        
        data = client.export_data(
            format="csv",
            date_debut="2024-01-01",
            date_fin="2024-01-31"
        )
        
        assert data == mock_csv_data
    
    def test_clear_cache(self, client):
        """Test le vidage du cache."""
        client._cache["test"] = "value"
        assert len(client._cache) == 1
        
        client.clear_cache()
        assert len(client._cache) == 0
    
    def test_get_cache_info(self, client):
        """Test la récupération des informations du cache."""
        client._cache["test"] = "value"
        info = client.get_cache_info()
        
        assert info["size"] == 1
        assert "test" in info["keys"]
        assert info["ttl"] == 300
    
    def test_set_cache_ttl(self, client):
        """Test la modification de la durée de vie du cache."""
        original_ttl = client._cache_ttl
        client.set_cache_ttl(600)
        
        assert client._cache_ttl == 600
        assert client._cache_ttl != original_ttl
    
    def test_context_manager(self, client):
        """Test l'utilisation du client comme context manager."""
        with client as c:
            assert c is client
            assert c.session is not None
        
        # La session devrait être fermée après le context manager
        # assert client.session.closed is False  # requests.Session ne ferme pas automatiquement


class TestClientAuthentication:
    """Tests pour l'authentification."""
    
    @pytest.fixture
    def client(self):
        return AppiClient("https://api.test.com")
    
    @responses.activate
    def test_authenticate_success(self, client):
        """Test une authentification réussie."""
        mock_auth_response = {
            "access_token": "test-token",
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": 1,
                "email": "test@example.com",
                "username": "testuser"
            }
        }
        
        responses.add(
            responses.POST,
            "https://api.test.com/login",
            json=mock_auth_response,
            status=200
        )
        
        result = client.authenticate("test@example.com", "password")
        assert result == mock_auth_response
        assert "Bearer test-token" in client.session.headers["Authorization"]
    
    @responses.activate
    def test_authenticate_failure(self, client):
        """Test une authentification échouée."""
        responses.add(
            responses.POST,
            "https://api.test.com/login",
            json={"detail": "Identifiants invalides"},
            status=401
        )
        
        with pytest.raises(AuthenticationError):
            client.authenticate("test@example.com", "wrong-password")
    
    @responses.activate
    def test_logout(self, client):
        """Test la déconnexion."""
        # Simuler une session authentifiée
        client.session.headers["Authorization"] = "Bearer test-token"
        
        responses.add(
            responses.POST,
            "https://api.test.com/logout",
            json={"message": "Déconnexion réussie"},
            status=200
        )
        
        result = client.logout()
        assert result is True
        assert "Authorization" not in client.session.headers


class TestClientDataOperations:
    """Tests pour les opérations de données."""
    
    @pytest.fixture
    def client(self):
        return AppiClient("https://api.test.com", "test-key")
    
    @responses.activate
    def test_add_cas_dengue(self, client):
        """Test l'ajout de cas de dengue."""
        from dengsurvab.models import ValidationCasDengue
        
        cas = ValidationCasDengue(
            idCas=1,
            sexe="masculin",
            age=25,
            region="centre",
            id_source=1
        )
        
        mock_response = {"message": "Cas ajouté avec succès", "id": 1}
        
        responses.add(
            responses.POST,
            "https://api.test.com/add-listCasDengue-json/",
            json=mock_response,
            status=200
        )
        
        result = client.add_cas_dengue([cas])
        assert result == mock_response
    
    @responses.activate
    def test_get_taux_hospitalisation(self, client):
        """Test la récupération du taux d'hospitalisation."""
        mock_taux = {
            "taux_hospitalisation": 15.5,
            "total_cas": 1000,
            "total_hospitalisations": 155
        }
        
        responses.add(
            responses.GET,
            "https://api.test.com/indicateurs/taux-hospitalisation",
            json=mock_taux,
            status=200
        )
        
        result = client.get_taux_hospitalisation(
            date_debut="2024-01-01",
            date_fin="2024-01-31"
        )
        
        assert result == mock_taux
    
    @responses.activate
    def test_get_taux_letalite(self, client):
        """Test la récupération du taux de létalité."""
        mock_taux = {
            "taux_letalite": 2.5,
            "total_cas": 1000,
            "total_deces": 25
        }
        
        responses.add(
            responses.GET,
            "https://api.test.com/indicateurs/taux-deletalite",
            json=mock_taux,
            status=200
        )
        
        result = client.get_taux_letalite(
            date_debut="2024-01-01",
            date_fin="2024-01-31"
        )
        
        assert result == mock_taux


if __name__ == "__main__":
    pytest.main([__file__]) 