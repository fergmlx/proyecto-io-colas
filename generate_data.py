"""
Script para generar dataset sintético de logs de servidor
"""

import sys
sys.path.append('.')
from src.data_processor import DataProcessor

if __name__ == "__main__":
    print("Generando dataset sintético...")
    DataProcessor.generate_synthetic_data(
        n_requests=10000,
        lambda_rate=120,
        mu_rate=30,
        start_date='2025-01-01',
        output_file='data/server_logs.csv'
    )
    print("Dataset generado exitosamente!")
