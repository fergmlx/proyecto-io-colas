"""
Distribution Fitter Module
Ajusta distribuciones estadísticas a datos de teoría de colas
"""

import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class DistributionFitter:
    """Ajusta distribuciones estadísticas a los datos"""
    
    def __init__(self):
        self.fitted_distributions = {}
        
    def fit_distributions(self, data, distributions=['expon', 'gamma', 'lognorm', 'weibull_min']):
        """
        Ajusta múltiples distribuciones a los datos
        
        Parameters:
        -----------
        data : array-like
            Datos a ajustar
        distributions : list
            Lista de nombres de distribuciones de scipy.stats
            
        Returns:
        --------
        dict
            Diccionario con parámetros ajustados para cada distribución
        """
        results = {}
        
        for dist_name in distributions:
            try:
                dist = getattr(stats, dist_name)
                params = dist.fit(data)
                
                # Calcular log-likelihood para AIC/BIC
                log_likelihood = np.sum(dist.logpdf(data, *params))
                k = len(params)
                n = len(data)
                
                aic = 2 * k - 2 * log_likelihood
                bic = k * np.log(n) - 2 * log_likelihood
                
                results[dist_name] = {
                    'params': params,
                    'dist_object': dist,
                    'log_likelihood': log_likelihood,
                    'aic': aic,
                    'bic': bic
                }
            except Exception as e:
                print(f"Error fitting {dist_name}: {e}")
                
        self.fitted_distributions = results
        return results
    
    def goodness_of_fit_tests(self, data, distribution, params):
        """
        Ejecuta tests de bondad de ajuste
        
        Parameters:
        -----------
        data : array-like
            Datos observados
        distribution : str or scipy.stats distribution
            Distribución a probar
        params : tuple
            Parámetros de la distribución
            
        Returns:
        --------
        dict
            Resultados de los tests K-S y Chi-cuadrado
        """
        if isinstance(distribution, str):
            dist = getattr(stats, distribution)
        else:
            dist = distribution
            
        # Test Kolmogorov-Smirnov
        ks_stat, ks_pvalue = stats.kstest(data, lambda x: dist.cdf(x, *params))
        
        # Test Chi-cuadrado
        observed, bin_edges = np.histogram(data, bins=20)
        expected = []
        for i in range(len(bin_edges) - 1):
            expected.append(
                (dist.cdf(bin_edges[i+1], *params) - dist.cdf(bin_edges[i], *params)) * len(data)
            )
        expected = np.array(expected)
        
        # Filtrar bins vacíos
        mask = expected > 5
        chi2_stat, chi2_pvalue = stats.chisquare(observed[mask], expected[mask])
        
        return {
            'ks_statistic': ks_stat,
            'ks_pvalue': ks_pvalue,
            'chi2_statistic': chi2_stat,
            'chi2_pvalue': chi2_pvalue
        }
    
    def get_best_distribution(self, data, criterion='aic'):
        """
        Retorna la mejor distribución según AIC o BIC
        
        Parameters:
        -----------
        data : array-like
            Datos a analizar
        criterion : str
            'aic' o 'bic'
            
        Returns:
        --------
        tuple
            (nombre_distribución, parámetros, valor_criterio)
        """
        if not self.fitted_distributions:
            self.fit_distributions(data)
            
        best_name = None
        best_value = np.inf
        best_params = None
        
        for name, info in self.fitted_distributions.items():
            value = info[criterion]
            if value < best_value:
                best_value = value
                best_name = name
                best_params = info['params']
                
        return best_name, best_params, best_value
    
    def plot_fit(self, data, distribution=None, params=None):
        """
        Genera datos para Q-Q plot y comparación PDF
        
        Parameters:
        -----------
        data : array-like
            Datos observados
        distribution : str, optional
            Nombre de la distribución. Si None, usa la mejor
        params : tuple, optional
            Parámetros de la distribución
            
        Returns:
        --------
        dict
            Diccionario con datos para graficar
        """
        if distribution is None:
            distribution, params, _ = self.get_best_distribution(data)
            
        dist = getattr(stats, distribution)
        
        # Q-Q plot data
        theoretical_quantiles = dist.ppf(np.linspace(0.01, 0.99, 100), *params)
        sample_quantiles = np.percentile(data, np.linspace(1, 99, 100))
        
        # PDF comparison
        x = np.linspace(data.min(), data.max(), 1000)
        pdf_fitted = dist.pdf(x, *params)
        
        return {
            'distribution': distribution,
            'params': params,
            'qq_theoretical': theoretical_quantiles,
            'qq_sample': sample_quantiles,
            'pdf_x': x,
            'pdf_y': pdf_fitted,
            'data_hist': data
        }
