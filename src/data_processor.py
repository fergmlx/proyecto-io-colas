"""
Data Processor Module
Procesa logs de servidor para análisis de teoría de colas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class DataProcessor:
    """Procesa logs de servidor para análisis de colas"""
    
    def __init__(self):
        self.data = None
        
    def load_data(self, filepath):
        """
        Carga CSV de logs de servidor
        
        Parameters:
        -----------
        filepath : str
            Ruta al archivo CSV
            
        Returns:
        --------
        pd.DataFrame
            DataFrame con los datos cargados
        """
        self.data = pd.read_csv(filepath)
        if 'timestamp' in self.data.columns:
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        return self.data
    
    def calculate_interarrival_times(self, df=None):
        """
        Calcula los intervalos entre llegadas consecutivas
        
        Parameters:
        -----------
        df : pd.DataFrame, optional
            DataFrame con columna 'arrival_time'. Si None, usa self.data
            
        Returns:
        --------
        np.ndarray
            Array con los tiempos entre llegadas (en segundos)
        """
        if df is None:
            df = self.data
            
        if 'arrival_time' in df.columns:
            interarrival = np.diff(df['arrival_time'].values)
        elif 'timestamp' in df.columns:
            timestamps = df['timestamp'].values
            interarrival = np.diff(timestamps.astype('datetime64[s]').astype(float))
        else:
            raise ValueError("DataFrame debe tener columna 'arrival_time' o 'timestamp'")
            
        return interarrival
    
    def get_statistics(self, df=None):
        """
        Calcula estadísticas descriptivas de los datos
        
        Parameters:
        -----------
        df : pd.DataFrame, optional
            DataFrame a analizar. Si None, usa self.data
            
        Returns:
        --------
        dict
            Diccionario con estadísticas clave
        """
        if df is None:
            df = self.data
            
        interarrival = self.calculate_interarrival_times(df)
        service_times = df['service_time'].values if 'service_time' in df.columns else None
        
        stats = {
            'total_requests': len(df),
            'interarrival': {
                'mean': np.mean(interarrival),
                'std': np.std(interarrival),
                'min': np.min(interarrival),
                'max': np.max(interarrival),
                'median': np.median(interarrival)
            }
        }
        
        if service_times is not None:
            stats['service_time'] = {
                'mean': np.mean(service_times),
                'std': np.std(service_times),
                'min': np.min(service_times),
                'max': np.max(service_times),
                'median': np.median(service_times)
            }
            
            # Calcular tasas (λ y μ)
            lambda_rate = 1 / np.mean(interarrival)
            mu_rate = 1 / np.mean(service_times)
            
            stats['rates'] = {
                'lambda_per_second': lambda_rate,
                'lambda_per_hour': lambda_rate * 3600,
                'mu_per_second': mu_rate,
                'mu_per_hour': mu_rate * 3600,
                'traffic_intensity': lambda_rate / mu_rate
            }
        
        return stats
    
    def detect_patterns(self, df=None):
        """
        Detecta patrones temporales en los datos (horas pico, tendencias)
        """
        if df is None:
            df = self.data
            
        if 'timestamp' not in df.columns:
            return {'error': 'Se requiere columna timestamp'}
        
        df = df.copy()
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        hourly_counts = df.groupby('hour').size()
        peak_hour = hourly_counts.idxmax()
        low_hour = hourly_counts.idxmin()
        
        patterns = {
            'peak_hour': int(peak_hour),
            'peak_hour_requests': int(hourly_counts.max()),
            'low_hour': int(low_hour),
            'low_hour_requests': int(hourly_counts.min()),
            'hourly_distribution': hourly_counts.to_dict(),
            'peak_to_average_ratio': hourly_counts.max() / hourly_counts.mean()
        }
        
        return patterns
    
    @staticmethod
    def generate_synthetic_data(n_requests=10000, lambda_rate=120, mu_rate=30, 
                                 start_date='2025-01-01', output_file='data/server_logs.csv'):
        """
        Genera datos sintéticos de servidor siguiendo proceso Poisson
        """
        np.random.seed(42)
        
        lambda_sec = lambda_rate / 3600
        mu_sec = mu_rate / 3600
        
        interarrival_times = np.random.exponential(1/lambda_sec, n_requests)
        arrival_times = np.cumsum(interarrival_times)
        
        service_times = np.random.exponential(1/mu_sec, n_requests)
        
        start = pd.to_datetime(start_date)
        timestamps = [start + timedelta(seconds=float(t)) for t in arrival_times]
        
        df = pd.DataFrame({
            'request_id': range(1, n_requests + 1),
            'arrival_time': arrival_times,
            'service_time': service_times,
            'timestamp': timestamps
        })
        
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False)
        
        print(f"Generated {n_requests} records")
        
        return df
