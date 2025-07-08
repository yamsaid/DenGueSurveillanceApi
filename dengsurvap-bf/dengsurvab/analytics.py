"""
Module d'analyse épidémiologique pour le client Appi Dengue

Ce module fournit des outils d'analyse avancés pour les données
de surveillance de la dengue.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from .exceptions import AnalysisError, APIError


class EpidemiologicalAnalyzer:
    """
    Analyseur épidémiologique pour les données de dengue.
    
    Cette classe fournit des méthodes d'analyse avancées pour
    les données de surveillance épidémiologique.
    """
    
    def __init__(self, client):
        """
        Initialise l'analyseur épidémiologique.
        
        Args:
            client: Instance du client Appi
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    def get_time_series(self,
                       date_debut: str,
                       date_fin: str,
                       frequency: str = "W",
                       region: str = "Toutes",
                       district: str = "Tous") -> pd.DataFrame:
        """
        Récupère une série temporelle des données.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            frequency: Fréquence (W: hebdomadaire, M: mensuel)
            region: Région
            district: District
            
        Returns:
            DataFrame avec la série temporelle
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            # Récupérer les indicateurs hebdomadaires
            indicateurs = self.client.data_period(
                date_debut=date_debut,
                date_fin=date_fin,
                region=region,
                district=district,
                frequence=frequency
            )
            
            # Convertir en DataFrame
            data = []
            for ind in indicateurs:
                data.append({
                    'date_debut': ind.date_debut,
                    'date_fin': ind.date_fin,
                    'region': ind.region,
                    'district': ind.district,
                    'total_cas': ind.total_cas,
                    'cas_positifs': ind.cas_positifs,
                    'cas_negatifs': ind.cas_negatifs,
                    'hospitalisations': ind.hospitalisations,
                    'deces': ind.deces,
                    'taux_positivite': ind.taux_positivite,
                    'taux_hospitalisation': ind.taux_hospitalisation,
                    'taux_letalite': ind.taux_letalite
                })
            
            df = pd.DataFrame(data)
            
            if not df.empty:
                # Convertir les dates
                df['date_debut'] = pd.to_datetime(df['date_debut'])
                df['date_fin'] = pd.to_datetime(df['date_fin'])
                
                # Trier par date
                df = df.sort_values('date_debut')
            
            self.logger.info(f"Série temporelle générée: {len(df)} points")
            return df
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de la série temporelle: {e}")
            raise AnalysisError(
                f"Impossible de générer la série temporelle: {e}",
                analysis_type="time_series"
            )
    
    def detect_anomalies(self, data: pd.DataFrame, method: str = "zscore") -> pd.DataFrame:
        """
        Détecte les anomalies dans les données.
        
        Args:
            data: DataFrame avec les données
            method: Méthode de détection (zscore, iqr, isolation_forest)
            
        Returns:
            DataFrame avec les anomalies détectées
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            if data.empty:
                return pd.DataFrame()
            
            anomalies = data.copy()
            
            if method == "zscore":
                # Détection par score Z
                for col in ['total_cas', 'cas_positifs', 'hospitalisations', 'deces']:
                    if col in anomalies.columns:
                        z_scores = np.abs((anomalies[col] - anomalies[col].mean()) / anomalies[col].std())
                        anomalies[f'{col}_anomaly'] = z_scores > 2
            
            elif method == "iqr":
                # Détection par IQR (Interquartile Range)
                for col in ['total_cas', 'cas_positifs', 'hospitalisations', 'deces']:
                    if col in anomalies.columns:
                        Q1 = anomalies[col].quantile(0.25)
                        Q3 = anomalies[col].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        anomalies[f'{col}_anomaly'] = (anomalies[col] < lower_bound) | (anomalies[col] > upper_bound)
            
            elif method == "isolation_forest":
                # Détection par Isolation Forest (nécessite scikit-learn)
                try:
                    from sklearn.ensemble import IsolationForest
                    
                    # Sélectionner les colonnes numériques
                    numeric_cols = ['total_cas', 'cas_positifs', 'hospitalisations', 'deces']
                    available_cols = [col for col in numeric_cols if col in anomalies.columns]
                    
                    if available_cols:
                        # Préparer les données
                        X = anomalies[available_cols].fillna(0)
                        
                        # Entraîner le modèle
                        iso_forest = IsolationForest(contamination=0.1, random_state=42)
                        anomalies['isolation_forest_anomaly'] = iso_forest.fit_predict(X) == -1
                
                except ImportError:
                    self.logger.warning("scikit-learn non disponible, utilisation de la méthode zscore")
                    return self.detect_anomalies(data, method="zscore")
            
            else:
                raise AnalysisError(f"Méthode de détection non supportée: {method}")
            
            self.logger.info(f"Anomalies détectées avec la méthode {method}")
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la détection d'anomalies: {e}")
            raise AnalysisError(
                f"Impossible de détecter les anomalies: {e}",
                analysis_type="anomaly_detection"
            )
    
    def calculate_rates(self,
                       date_debut: str,
                       date_fin: str,
                       region: Optional[str] = None,
                       district: Optional[str] = None) -> Dict[str, float]:
        """
        Calcule les taux épidémiologiques.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            
        Returns:
            Dictionnaire avec les taux calculés
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            # Récupérer les données
            df = self.get_time_series(
                date_debut=date_debut,
                date_fin=date_fin,
                region=region or "Toutes",
                district=district or "Toutes"
            )
            
            if df.empty:
                return {}
            
            # Calculer les taux
            total_cas = df['total_cas'].sum()
            total_positifs = df['cas_positifs'].sum()
            total_hospitalisations = df['hospitalisations'].sum()
            total_deces = df['deces'].sum()
            
            rates = {
                'taux_positivite': (total_positifs / total_cas * 100) if total_cas > 0 else 0,
                'taux_hospitalisation': (total_hospitalisations / total_cas * 100) if total_cas > 0 else 0,
                'taux_letalite': (total_deces / total_cas * 100) if total_cas > 0 else 0,
                'total_cas': total_cas,
                'total_positifs': total_positifs,
                'total_hospitalisations': total_hospitalisations,
                'total_deces': total_deces
            }
            
            self.logger.info("Taux épidémiologiques calculés")
            return rates
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul des taux: {e}")
            raise AnalysisError(
                f"Impossible de calculer les taux: {e}",
                analysis_type="rate_calculation"
            )
    
    def trend_analysis(self, data: pd.DataFrame, column: str = "total_cas") -> Dict[str, Any]:
        """
        Analyse les tendances dans les données.
        
        Args:
            data: DataFrame avec les données
            column: Colonne à analyser
            
        Returns:
            Dictionnaire avec l'analyse des tendances
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            if data.empty or column not in data.columns:
                return {}
            
            # Calculer les statistiques de tendance
            values = data[column].dropna()
            
            if len(values) < 2:
                return {}
            
            # Régression linéaire simple
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            
            # Calculer le coefficient de corrélation
            correlation = np.corrcoef(x, values)[0, 1]
            
            # Déterminer la direction de la tendance
            if slope > 0:
                trend_direction = "croissante"
            elif slope < 0:
                trend_direction = "décroissante"
            else:
                trend_direction = "stable"
            
            # Calculer la pente en pourcentage
            if values.mean() > 0:
                slope_percentage = (slope / values.mean()) * 100
            else:
                slope_percentage = 0
            
            analysis = {
                'slope': slope,
                'intercept': intercept,
                'correlation': correlation,
                'trend_direction': trend_direction,
                'slope_percentage': slope_percentage,
                'mean': values.mean(),
                'std': values.std(),
                'min': values.min(),
                'max': values.max()
            }
            
            self.logger.info(f"Analyse de tendance effectuée pour {column}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de tendance: {e}")
            raise AnalysisError(
                f"Impossible d'analyser les tendances: {e}",
                analysis_type="trend_analysis"
            )
    
    def seasonal_analysis(self, data: pd.DataFrame, column: str = "total_cas") -> Dict[str, Any]:
        """
        Analyse la saisonnalité des données.
        
        Args:
            data: DataFrame avec les données
            column: Colonne à analyser
            
        Returns:
            Dictionnaire avec l'analyse de saisonnalité
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            if data.empty or column not in data.columns:
                return {}
            
            # Extraire le mois de chaque date
            data_copy = data.copy()
            data_copy['month'] = data_copy['date_debut'].dt.month
            
            # Calculer les moyennes par mois
            monthly_means = data_copy.groupby('month')[column].mean()
            
            # Identifier les mois de pic et de creux
            peak_month = monthly_means.idxmax()
            trough_month = monthly_means.idxmin()
            
            # Calculer l'amplitude saisonnière
            seasonal_amplitude = monthly_means.max() - monthly_means.min()
            
            # Calculer l'indice de saisonnalité
            overall_mean = data_copy[column].mean()
            seasonal_index = (monthly_means / overall_mean) * 100 if overall_mean > 0 else 0
            
            analysis = {
                'peak_month': int(peak_month),
                'trough_month': int(trough_month),
                'seasonal_amplitude': float(seasonal_amplitude),
                'seasonal_index': seasonal_index.to_dict(),
                'monthly_means': monthly_means.to_dict()
            }
            
            self.logger.info(f"Analyse de saisonnalité effectuée pour {column}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de saisonnalité: {e}")
            raise AnalysisError(
                f"Impossible d'analyser la saisonnalité: {e}",
                analysis_type="seasonal_analysis"
            )
    
    def forecast_next_week(self, data: pd.DataFrame, column: str = "total_cas") -> Dict[str, Any]:
        """
        Prédit les valeurs pour la semaine suivante.
        
        Args:
            data: DataFrame avec les données historiques
            column: Colonne à prédire
            
        Returns:
            Dictionnaire avec les prédictions
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            if data.empty or column not in data.columns:
                return {}
            
            # Utiliser une moyenne mobile simple pour la prédiction
            recent_values = data[column].tail(4).values  # 4 dernières semaines
            
            if len(recent_values) == 0:
                return {}
            
            # Prédiction basée sur la moyenne mobile
            prediction = np.mean(recent_values)
            
            # Calculer l'intervalle de confiance simple
            std_error = np.std(recent_values) / np.sqrt(len(recent_values))
            confidence_interval = (prediction - 1.96 * std_error, prediction + 1.96 * std_error)
            
            forecast = {
                'prediction': float(prediction),
                'confidence_interval_lower': float(confidence_interval[0]),
                'confidence_interval_upper': float(confidence_interval[1]),
                'method': 'moving_average',
                'last_values_used': len(recent_values)
            }
            
            self.logger.info(f"Prédiction générée pour {column}")
            return forecast
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la prédiction: {e}")
            raise AnalysisError(
                f"Impossible de générer la prédiction: {e}",
                analysis_type="forecasting"
            )


class DashboardGenerator:
    """
    Générateur de tableaux de bord épidémiologiques.
    
    Cette classe génère des rapports et tableaux de bord
    complets à partir des données de surveillance.
    """
    
    def __init__(self, client):
        """
        Initialise le générateur de tableaux de bord.
        
        Args:
            client: Instance du client Appi
        """
        self.client = client
        self.analyzer = EpidemiologicalAnalyzer(client)
        self.logger = logging.getLogger(__name__)
    
    def generate_report(self,
                       date_debut: str,
                       date_fin: str,
                       region: str = "Toutes",
                       district: str = "Toutes",
                       include_visualizations: bool = True) -> Dict[str, Any]:
        """
        Génère un rapport épidémiologique complet.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            include_visualizations: Inclure les visualisations
            
        Returns:
            Rapport complet
            
        Raises:
            AnalysisError: En cas d'erreur
        """
        try:
            # Récupérer les données de base
            data = self.analyzer.get_time_series(
                date_debut=date_debut,
                date_fin=date_fin,
                region=region,
                district=district
            )
            
            # Calculer les taux
            rates = self.analyzer.calculate_rates(
                date_debut=date_debut,
                date_fin=date_fin,
                region=region,
                district=district
            )
            
            # Analyser les tendances
            trend_analysis = self.analyzer.trend_analysis(data, "total_cas")
            
            # Analyser la saisonnalité
            seasonal_analysis = self.analyzer.seasonal_analysis(data, "total_cas")
            
            # Prédiction pour la semaine suivante
            forecast = self.analyzer.forecast_next_week(data, "total_cas")
            
            # Détecter les anomalies
            anomalies = self.analyzer.detect_anomalies(data)
            
            # Compiler le rapport
            report = {
                'metadata': {
                    'date_debut': date_debut,
                    'date_fin': date_fin,
                    'region': region,
                    'district': district,
                    'generated_at': datetime.now().isoformat(),
                    'data_points': len(data)
                },
                'summary': {
                    'total_cas': rates.get('total_cas', 0),
                    'total_positifs': rates.get('total_positifs', 0),
                    'total_hospitalisations': rates.get('total_hospitalisations', 0),
                    'total_deces': rates.get('total_deces', 0)
                },
                'rates': rates,
                'trend_analysis': trend_analysis,
                'seasonal_analysis': seasonal_analysis,
                'forecast': forecast,
                'anomalies': {
                    'count': len(anomalies[anomalies.get('total_cas_anomaly', False)]),
                    'periods': anomalies[anomalies.get('total_cas_anomaly', False)][['date_debut', 'date_fin', 'total_cas']].to_dict('records')
                },
                'data': data.to_dict('records') if not data.empty else []
            }
            
            self.logger.info("Rapport épidémiologique généré")
            return report
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {e}")
            raise AnalysisError(
                f"Impossible de générer le rapport: {e}",
                analysis_type="report_generation"
            )
    
    def save_report(self, report: Dict[str, Any], file_path: str) -> bool:
        """
        Sauvegarde un rapport dans un fichier.
        
        Args:
            report: Rapport à sauvegarder
            file_path: Chemin du fichier
            
        Returns:
            True si la sauvegarde a réussi
        """
        try:
            import json
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Rapport sauvegardé dans {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du rapport: {e}")
            return False 