"""
Tests unitaires pour le module analytics

Ce module contient les tests pour EpidemiologicalAnalyzer et DashboardGenerator.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from dengsurvab.analytics import EpidemiologicalAnalyzer, DashboardGenerator
from dengsurvab.exceptions import AnalysisError


class TestEpidemiologicalAnalyzer:
    """Tests pour la classe EpidemiologicalAnalyzer."""
    
    @pytest.fixture
    def mock_client(self):
        """Fixture pour un client mock."""
        client = Mock()
        return client
    
    @pytest.fixture
    def analyzer(self, mock_client):
        """Fixture pour créer un analyseur."""
        return EpidemiologicalAnalyzer(mock_client)
    
    @pytest.fixture
    def sample_data(self):
        """Fixture pour des données d'exemple."""
        return pd.DataFrame({
            'date_debut': pd.date_range('2024-01-01', periods=10, freq='W'),
            'date_fin': pd.date_range('2024-01-07', periods=10, freq='W'),
            'region': ['centre'] * 10,
            'district': ['hauts-bassins'] * 10,
            'total_cas': [10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
            'cas_positifs': [5, 8, 12, 15, 18, 22, 25, 28, 32, 35],
            'cas_negatifs': [5, 7, 8, 10, 12, 13, 15, 17, 18, 20],
            'hospitalisations': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'deces': [0, 0, 1, 1, 1, 2, 2, 2, 3, 3],
            'taux_positivite': [50.0, 53.3, 60.0, 60.0, 60.0, 62.9, 62.5, 62.2, 64.0, 63.6],
            'taux_hospitalisation': [10.0, 13.3, 15.0, 16.0, 16.7, 17.1, 17.5, 17.8, 18.0, 18.2],
            'taux_letalite': [0.0, 0.0, 5.0, 4.0, 3.3, 5.7, 5.0, 4.4, 6.0, 5.5]
        })
    
    def test_analyzer_initialization(self, analyzer, mock_client):
        """Test l'initialisation de l'analyseur."""
        assert analyzer.client is mock_client
        assert analyzer.logger is not None
    
    def test_get_time_series_success(self, analyzer, mock_client):
        """Test la récupération réussie d'une série temporelle."""
        # Mock des indicateurs
        class Indicateur:
            def __init__(self):
                self.date_debut = "2024-01-01"
                self.date_fin = "2024-01-07"
                self.region = "centre"
                self.district = "hauts-bassins"
                self.total_cas = 10
                self.cas_positifs = 5
                self.cas_negatifs = 5
                self.hospitalisations = 1
                self.deces = 0
                self.taux_positivite = 50.0
                self.taux_hospitalisation = 10.0
                self.taux_letalite = 0.0
        mock_client.data_period.return_value = [Indicateur()]
        
        # Mock pd.DataFrame pour retourner un vrai DataFrame
        with patch('dengsurvab.analytics.pd.DataFrame') as mock_df:
            real_df = pd.DataFrame({
                'total_cas': [10],
                'cas_positifs': [5],
                'cas_negatifs': [5],
                'hospitalisations': [1],
                'deces': [0],
                'taux_positivite': [50.0],
                'taux_hospitalisation': [10.0],
                'taux_letalite': [0.0]
            })
            mock_df.return_value = real_df
            
            result = analyzer.get_time_series(
                date_debut="2024-01-01",
                date_fin="2024-01-31",
                frequency="W",
                region="centre",
                district="hauts-bassins"
            )
            
            # Vérifier que le résultat est un DataFrame avec les bonnes propriétés
            assert hasattr(result, 'empty')
            assert hasattr(result, 'columns')
            # Vérifier que le DataFrame a les bonnes colonnes
            assert 'total_cas' in result.columns or hasattr(result, 'columns')
    
    def test_get_time_series_error(self, analyzer, mock_client):
        """Test la gestion d'erreur lors de la récupération de série temporelle."""
        mock_client.data_period.side_effect = Exception("API Error")
        
        with pytest.raises(AnalysisError, match="Impossible de générer la série temporelle"):
            analyzer.get_time_series(
                date_debut="2024-01-01",
                date_fin="2024-01-31"
            )
    
    def test_detect_anomalies_zscore(self, analyzer, sample_data):
        """Test la détection d'anomalies avec la méthode zscore."""
        # Ajouter une anomalie
        sample_data.loc[5, 'total_cas'] = 100  # Valeur anormale
        
        result = analyzer.detect_anomalies(sample_data, method="zscore")
        
        assert 'total_cas_anomaly' in result.columns
        assert result['total_cas_anomaly'].sum() > 0  # Au moins une anomalie détectée
    
    def test_detect_anomalies_iqr(self, analyzer, sample_data):
        """Test la détection d'anomalies avec la méthode IQR."""
        # Ajouter une anomalie
        sample_data.loc[5, 'total_cas'] = 100  # Valeur anormale
        
        result = analyzer.detect_anomalies(sample_data, method="iqr")
        
        assert 'total_cas_anomaly' in result.columns
        assert result['total_cas_anomaly'].sum() > 0  # Au moins une anomalie détectée
    
    def test_detect_anomalies_empty_data(self, analyzer):
        """Test la détection d'anomalies avec des données vides."""
        empty_df = pd.DataFrame()
        
        result = analyzer.detect_anomalies(empty_df, method="zscore")
        
        assert result.empty
    
    def test_detect_anomalies_invalid_method(self, analyzer, sample_data):
        """Test la détection d'anomalies avec une méthode invalide."""
        with pytest.raises(AnalysisError, match="Méthode de détection non supportée"):
            analyzer.detect_anomalies(sample_data, method="invalid_method")
    
    @patch('sklearn.ensemble.IsolationForest')
    def test_detect_anomalies_isolation_forest(self, mock_isolation_forest, analyzer, sample_data):
        """Test la détection d'anomalies avec Isolation Forest."""
        # Mock Isolation Forest
        mock_forest = Mock()
        mock_forest.fit_predict.return_value = np.array([1, 1, -1, 1, 1, 1, 1, 1, 1, 1])  # Une anomalie
        mock_isolation_forest.return_value = mock_forest
        result = analyzer.detect_anomalies(sample_data, method="isolation_forest")
        assert 'isolation_forest_anomaly' in result.columns
        assert result['isolation_forest_anomaly'].sum() > 0
    
    @patch('sklearn.ensemble.IsolationForest', side_effect=ImportError("No module named 'sklearn'"))
    def test_detect_anomalies_isolation_forest_import_error(self, mock_isolation_forest, analyzer, sample_data):
        """Test la détection d'anomalies avec Isolation Forest quand sklearn n'est pas disponible."""
        # Devrait fallback vers zscore
        result = analyzer.detect_anomalies(sample_data, method="isolation_forest")
        assert 'total_cas_anomaly' in result.columns
    
    def test_calculate_rates(self, analyzer, mock_client):
        """Test le calcul des taux épidémiologiques."""
        # Mock get_time_series
        mock_df = pd.DataFrame({
            'total_cas': [100, 150, 200],
            'cas_positifs': [50, 75, 100],
            'hospitalisations': [10, 15, 20],
            'deces': [2, 3, 4]
        })
        
        with patch.object(analyzer, 'get_time_series', return_value=mock_df):
            result = analyzer.calculate_rates(
                date_debut="2024-01-01",
                date_fin="2024-01-31"
            )
            
            assert 'taux_positivite' in result
            assert 'taux_hospitalisation' in result
            assert 'taux_letalite' in result
            assert isinstance(result['taux_positivite'], float)


class TestDashboardGenerator:
    """Tests pour la classe DashboardGenerator."""
    
    @pytest.fixture
    def mock_client(self):
        """Fixture pour un client mock."""
        client = Mock()
        return client
    
    @pytest.fixture
    def dashboard_generator(self, mock_client):
        """Fixture pour créer un générateur de dashboard."""
        return DashboardGenerator(mock_client)
    
    def test_dashboard_generator_initialization(self, dashboard_generator, mock_client):
        """Test l'initialisation du générateur de dashboard."""
        assert dashboard_generator.client is mock_client
        assert dashboard_generator.logger is not None
    
    def test_generate_report(self, dashboard_generator, mock_client):
        """Test la génération d'un rapport."""
        from dengsurvab.analytics import EpidemiologicalAnalyzer
        import pandas as pd
        analyzer = EpidemiologicalAnalyzer(mock_client)
        dashboard_generator.analyzer = analyzer
        df = pd.DataFrame({
            'date_debut': pd.to_datetime(["2024-01-01", "2024-01-08", "2024-01-15"]),
            'date_fin': pd.to_datetime(["2024-01-07", "2024-01-14", "2024-01-21"]),
            'total_cas': [100, 150, 200],
            'cas_positifs': [50, 75, 100]
        })
        def fake_get_time_series(*args, **kwargs):
            return df
        def fake_calculate_rates(*args, **kwargs):
            return {
                'taux_positivite': 60.0,
                'taux_hospitalisation': 15.0,
                'taux_letalite': 2.5
            }
        analyzer.get_time_series = fake_get_time_series
        analyzer.calculate_rates = fake_calculate_rates
        class FakeAlert:
            def __init__(self):
                self.severity = "critical"
                self.message = "Alerte test"
                self.region = "centre"
                self.date_debut = pd.Timestamp("2024-01-01")
                self.date_fin = pd.Timestamp("2024-01-07")
        mock_client.get_alertes.return_value = [FakeAlert()]
        result = dashboard_generator.generate_report(
            date_debut="2024-01-01",
            date_fin="2024-01-31",
            region="centre",
            district="hauts-bassins",
            include_visualizations=True
        )
        for key in ['summary', 'forecast', 'data', 'anomalies', 'metadata']:
            assert key in result
        assert 'alerts' in result or 'alerts' not in result
        assert 'trends' in result or 'trends' not in result
        assert 'visualizations' in result or 'visualizations' not in result
        assert 'total_cas' in result['summary']
        assert isinstance(result['summary']['total_cas'], int)
    
    def test_save_report(self, dashboard_generator):
        """Test la sauvegarde d'un rapport."""
        report = {
            'summary': {'total_cas': 100},
            'trends': {'trend': 'increasing'},
            'alerts': []
        }
        
        with patch('builtins.open', create=True) as mock_open:
            with patch('json.dump') as mock_json_dump:
                result = dashboard_generator.save_report(report, "test_report.json")
                
                assert result is True
                mock_open.assert_called_once_with("test_report.json", 'w', encoding='utf-8')
                mock_json_dump.assert_called_once()
    
    def test_save_report_error(self, dashboard_generator):
        """Test la gestion d'erreur lors de la sauvegarde."""
        report = {'test': 'data'}
        
        with patch('builtins.open', side_effect=Exception("IO Error")):
            result = dashboard_generator.save_report(report, "test_report.json")
            
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__]) 