"""
Tests unitaires pour le module CLI

Ce module contient les tests pour l'interface en ligne de commande.
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from dengsurvab.cli import main, handle_stats, handle_cas, handle_alertes, handle_export, handle_auth, handle_regions, handle_districts


class TestCLI:
    """Tests pour les fonctions CLI."""
    
    @pytest.fixture
    def mock_client(self):
        """Fixture pour un client mock."""
        client = Mock()
        return client
    
    @patch('sys.argv', ['test_cli.py', 'stats'])
    @patch('dengsurvab.cli.AppiClient')
    @patch('dengsurvab.cli.handle_stats')
    @patch('os.getenv', return_value='https://api.test.com')
    def test_main_stats_command(self, mock_getenv, mock_handle_stats, mock_client_class, mock_client):
        """Test la commande stats."""
        mock_client_class.return_value = mock_client
        
        with patch('sys.exit') as mock_exit:
            main()
            
            mock_client_class.assert_called_once()
            mock_handle_stats.assert_called_once_with(mock_client)
            mock_exit.assert_not_called()
    
    @patch('sys.argv', ['test_cli.py', 'cas', '--date-debut', '2024-01-01', '--date-fin', '2024-01-31'])
    @patch('dengsurvab.cli.AppiClient')
    @patch('dengsurvab.cli.handle_cas')
    @patch('os.getenv', return_value='https://api.test.com')
    def test_main_cas_command(self, mock_getenv, mock_handle_cas, mock_client_class, mock_client):
        """Test la commande cas."""
        mock_client_class.return_value = mock_client
        
        with patch('sys.exit') as mock_exit:
            main()
            
            mock_handle_cas.assert_called_once()
            mock_exit.assert_not_called()
    
    @patch('sys.argv', ['test_cli.py', 'alertes', '--severity', 'critical'])
    @patch('dengsurvab.cli.AppiClient')
    @patch('dengsurvab.cli.handle_alertes')
    @patch('os.getenv', return_value='https://api.test.com')
    def test_main_alertes_command(self, mock_getenv, mock_handle_alertes, mock_client_class, mock_client):
        """Test la commande alertes."""
        mock_client_class.return_value = mock_client
        
        with patch('sys.exit') as mock_exit:
            main()
            
            mock_handle_alertes.assert_called_once()
            mock_exit.assert_not_called()
    
    @patch('sys.argv', ['test_cli.py', 'export', '--format', 'csv', '--output', 'test.csv'])
    @patch('dengsurvab.cli.AppiClient')
    @patch('dengsurvab.cli.handle_export')
    @patch('os.getenv', return_value='https://api.test.com')
    def test_main_export_command(self, mock_getenv, mock_handle_export, mock_client_class, mock_client):
        """Test la commande export."""
        mock_client_class.return_value = mock_client
        
        with patch('sys.exit') as mock_exit:
            main()
            
            mock_handle_export.assert_called_once()
            mock_exit.assert_not_called()
    
    @patch('sys.argv', ['test_cli.py', 'auth', '--email', 'test@example.com', '--password', 'password'])
    @patch('dengsurvab.cli.AppiClient')
    @patch('dengsurvab.cli.handle_auth')
    @patch('os.getenv', return_value='https://api.test.com')
    def test_main_auth_command(self, mock_getenv, mock_handle_auth, mock_client_class, mock_client):
        """Test la commande auth."""
        mock_client_class.return_value = mock_client
        
        with patch('sys.exit') as mock_exit:
            main()
            
            mock_handle_auth.assert_called_once()
            mock_exit.assert_not_called()
    
    @patch('sys.argv', ['test_cli.py', 'regions'])
    @patch('dengsurvab.cli.AppiClient')
    @patch('dengsurvab.cli.handle_regions')
    @patch('os.getenv', return_value='https://api.test.com')
    def test_main_regions_command(self, mock_getenv, mock_handle_regions, mock_client_class, mock_client):
        """Test la commande regions."""
        mock_client_class.return_value = mock_client
        
        with patch('sys.exit') as mock_exit:
            main()
            
            mock_handle_regions.assert_called_once_with(mock_client)
            mock_exit.assert_not_called()
    
    @patch('sys.argv', ['test_cli.py', 'districts', '--region', 'centre'])
    @patch('dengsurvab.cli.AppiClient')
    @patch('dengsurvab.cli.handle_districts')
    @patch('os.getenv', return_value='https://api.test.com')
    def test_main_districts_command(self, mock_getenv, mock_handle_districts, mock_client_class, mock_client):
        """Test la commande districts."""
        mock_client_class.return_value = mock_client
        
        with patch('sys.exit') as mock_exit:
            main()
            
            mock_handle_districts.assert_called_once()
            mock_exit.assert_not_called()
    
    @patch('sys.argv', ['test_cli.py'])
    @patch('dengsurvab.cli.AppiClient')
    @patch('os.getenv', return_value='https://api.test.com')
    def test_main_no_command(self, mock_getenv, mock_client_class):
        """Test l'exécution sans commande."""
        with patch('sys.exit') as mock_exit:
            main()
            assert mock_exit.called
    
    @patch('sys.argv', ['test_cli.py', 'stats'])
    @patch('dengsurvab.cli.AppiClient')
    def test_main_missing_api_url(self, mock_client_class):
        """Test l'exécution sans URL API."""
        with patch('sys.exit') as mock_exit:
            with patch('os.getenv', return_value=None):
                main()
                
                mock_exit.assert_called_once_with(1)
    
    @patch('sys.argv', ['test_cli.py', 'stats'])
    @patch('dengsurvab.cli.AppiClient')
    @patch('os.getenv', return_value='https://api.test.com')
    def test_main_client_error(self, mock_getenv, mock_client_class):
        """Test la gestion d'erreur du client."""
        mock_client_class.side_effect = Exception("Client Error")
        with patch('sys.exit') as mock_exit:
            main()
            assert mock_exit.called
    
    @patch('sys.argv', ['test_cli.py', 'unknown'])
    @patch('dengsurvab.cli.AppiClient')
    @patch('os.getenv', return_value='https://api.test.com')
    def test_main_unknown_command(self, mock_getenv, mock_client_class, mock_client):
        """Test une commande inconnue."""
        mock_client_class.return_value = mock_client
        with patch('sys.exit') as mock_exit:
            main()
            assert mock_exit.called


class TestCLIHandlers:
    """Tests pour les handlers CLI."""
    
    @pytest.fixture
    def mock_client(self):
        """Fixture pour un client mock."""
        client = Mock()
        return client
    
    def test_handle_stats_success(self, mock_client):
        """Test le handler stats avec succès."""
        # Mock des statistiques
        mock_stats = Mock()
        mock_stats.total_cas = 1000
        mock_stats.total_positifs = 500
        mock_stats.total_hospitalisations = 100
        mock_stats.total_deces = 10
        mock_stats.regions_actives = ['centre', 'hauts-bassins']
        mock_stats.districts_actifs = ['district1', 'district2']
        mock_stats.derniere_mise_a_jour = "2024-01-15T10:30:00"
        
        mock_client.get_stats.return_value = mock_stats
        
        with patch('builtins.print') as mock_print:
            handle_stats(mock_client)
            
            mock_print.assert_called()
            mock_client.get_stats.assert_called_once()
    
    def test_handle_stats_error(self, mock_client):
        """Test le handler stats avec erreur."""
        mock_client.get_stats.side_effect = Exception("API Error")
        
        with patch('builtins.print') as mock_print:
            handle_stats(mock_client)
            
            # Vérifier qu'un message d'erreur a été affiché
            mock_print.assert_called()
    
    def test_handle_cas_success(self, mock_client):
        """Test le handler cas avec succès."""
        # Mock des cas
        mock_cas = [
            Mock(
                date_consultation="2024-01-15",
                region="centre",
                sexe="masculin",
                age=25,
                resultat_test="positif",
                hospitalise="non"
            ),
            Mock(
                date_consultation="2024-01-16",
                region="hauts-bassins",
                sexe="feminin",
                age=30,
                resultat_test="negatif",
                hospitalise="oui"
            )
        ]
        
        mock_client.get_cas_dengue.return_value = mock_cas
        
        # Mock des arguments
        mock_args = Mock()
        mock_args.date_debut = "2024-01-01"
        mock_args.date_fin = "2024-01-31"
        mock_args.region = "centre"
        mock_args.district = "hauts-bassins"
        mock_args.limit = 10
        
        with patch('builtins.print') as mock_print:
            handle_cas(mock_client, mock_args)
            
            mock_print.assert_called()
            mock_client.get_cas_dengue.assert_called_once_with(
                date_debut="2024-01-01",
                date_fin="2024-01-31",
                region="centre",
                district="hauts-bassins",
                limit=10
            )
    
    def test_handle_cas_error(self, mock_client):
        """Test le handler cas avec erreur."""
        mock_client.get_cas_dengue.side_effect = Exception("API Error")
        
        mock_args = Mock()
        mock_args.date_debut = "2024-01-01"
        mock_args.date_fin = "2024-01-31"
        mock_args.region = None
        mock_args.district = None
        mock_args.limit = 10
        
        with patch('builtins.print') as mock_print:
            handle_cas(mock_client, mock_args)
            
            mock_print.assert_called()
    
    def test_handle_alertes_success(self, mock_client):
        """Test le handler alertes avec succès."""
        # Mock des alertes
        mock_alertes = [
            Mock(
                severity="critical",
                message="Seuil dépassé",
                region="centre",
                status="active",
                created_at="2024-01-15T10:30:00"
            ),
            Mock(
                severity="warning",
                message="Tendance à la hausse",
                region="hauts-bassins",
                status="resolved",
                created_at="2024-01-14T15:45:00"
            )
        ]
        
        mock_client.get_alertes.return_value = mock_alertes
        
        # Mock des arguments
        mock_args = Mock()
        mock_args.limit = 10
        mock_args.severity = "critical"
        mock_args.status = "active"
        
        with patch('builtins.print') as mock_print:
            handle_alertes(mock_client, mock_args)
            
            mock_print.assert_called()
            mock_client.get_alertes.assert_called_once_with(
                limit=10,
                severity="critical",
                status="active"
            )
    
    def test_handle_alertes_error(self, mock_client):
        """Test le handler alertes avec erreur."""
        mock_client.get_alertes.side_effect = Exception("API Error")
        
        mock_args = Mock()
        mock_args.limit = 10
        mock_args.severity = None
        mock_args.status = None
        
        with patch('builtins.print') as mock_print:
            handle_alertes(mock_client, mock_args)
            
            mock_print.assert_called()
    
    def test_handle_export_success(self, mock_client):
        """Test le handler export avec succès."""
        mock_data = b"idCas,date_consultation,region\n1,2024-01-15,centre"
        mock_client.export_data.return_value = mock_data
        
        # Mock des arguments
        mock_args = Mock()
        mock_args.format = "csv"
        mock_args.output = "test.csv"
        mock_args.date_debut = "2024-01-01"
        mock_args.date_fin = "2024-01-31"
        mock_args.region = "centre"
        mock_args.district = "hauts-bassins"
        
        with patch('builtins.print') as mock_print:
            with patch('builtins.open', create=True) as mock_open:
                handle_export(mock_client, mock_args)
                
                mock_print.assert_called()
                mock_client.export_data.assert_called_once_with(
                    format="csv",
                    date_debut="2024-01-01",
                    date_fin="2024-01-31",
                    region="centre",
                    district="hauts-bassins"
                )
                mock_open.assert_called_once_with("test.csv", "wb")
    
    def test_handle_export_error(self, mock_client):
        """Test le handler export avec erreur."""
        mock_client.export_data.side_effect = Exception("API Error")
        
        mock_args = Mock()
        mock_args.format = "csv"
        mock_args.output = "test.csv"
        mock_args.date_debut = "2024-01-01"
        mock_args.date_fin = "2024-01-31"
        mock_args.region = None
        mock_args.district = None
        
        with patch('builtins.print') as mock_print:
            handle_export(mock_client, mock_args)
            
            mock_print.assert_called()
    
    def test_handle_auth_success(self, mock_client):
        """Test le handler auth avec succès."""
        mock_auth_response = {
            "access_token": "test-token",
            "user": {"email": "test@example.com"}
        }
        mock_client.authenticate.return_value = mock_auth_response
        
        # Mock des arguments
        mock_args = Mock()
        mock_args.email = "test@example.com"
        mock_args.password = "password"
        
        with patch('builtins.print') as mock_print:
            handle_auth(mock_client, mock_args)
            
            mock_print.assert_called()
            mock_client.authenticate.assert_called_once_with("test@example.com", "password")
    
    def test_handle_auth_error(self, mock_client):
        """Test le handler auth avec erreur."""
        mock_client.authenticate.side_effect = Exception("Auth Error")
        
        mock_args = Mock()
        mock_args.email = "test@example.com"
        mock_args.password = "password"
        
        with patch('builtins.print') as mock_print:
            handle_auth(mock_client, mock_args)
            
            mock_print.assert_called()
    
    def test_handle_regions_success(self, mock_client):
        """Test le handler regions avec succès."""
        mock_regions = ["centre", "hauts-bassins", "plateau-central"]
        mock_client.get_regions.return_value = mock_regions
        
        with patch('builtins.print') as mock_print:
            handle_regions(mock_client)
            
            mock_print.assert_called()
            mock_client.get_regions.assert_called_once()
    
    def test_handle_regions_error(self, mock_client):
        """Test le handler regions avec erreur."""
        mock_client.get_regions.side_effect = Exception("API Error")
        
        with patch('builtins.print') as mock_print:
            handle_regions(mock_client)
            
            mock_print.assert_called()
    
    def test_handle_districts_success(self, mock_client):
        """Test le handler districts avec succès."""
        mock_districts = ["district1", "district2", "district3"]
        mock_client.get_districts.return_value = mock_districts
        
        # Mock des arguments
        mock_args = Mock()
        mock_args.region = "centre"
        
        with patch('builtins.print') as mock_print:
            handle_districts(mock_client, mock_args)
            
            mock_print.assert_called()
            mock_client.get_districts.assert_called_once_with(region="centre")
    
    def test_handle_districts_error(self, mock_client):
        """Test le handler districts avec erreur."""
        mock_client.get_districts.side_effect = Exception("API Error")
        
        mock_args = Mock()
        mock_args.region = "centre"
        
        with patch('builtins.print') as mock_print:
            handle_districts(mock_client, mock_args)
            
            mock_print.assert_called()


if __name__ == "__main__":
    pytest.main([__file__]) 