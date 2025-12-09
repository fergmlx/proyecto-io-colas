"""
Cost Optimizer Module
Optimiza número de servidores minimizando costos totales
"""

import numpy as np
from scipy.optimize import minimize_scalar, differential_evolution
from .queue_models import MMcQueue


class CostOptimizer:
    """Optimiza número de servidores minimizando función de costos"""
    
    def __init__(self, lambda_rate, mu_rate, cost_server, cost_waiting):
        """
        Inicializa optimizador de costos
        
        Parameters:
        -----------
        lambda_rate : float
            Tasa de llegada (clientes por hora)
        mu_rate : float
            Tasa de servicio por servidor (clientes por hora)
        cost_server : float
            Costo operativo por servidor ($/hora)
        cost_waiting : float
            Costo de espera por cliente ($/cliente)
        """
        self.lambda_rate = lambda_rate
        self.mu_rate = mu_rate
        self.cost_server = cost_server
        self.cost_waiting = cost_waiting
        
    def objective_function(self, c):
        """
        Función objetivo: Z = c·Cs + Lq·Cw
        
        Parameters:
        -----------
        c : int or float
            Número de servidores
            
        Returns:
        --------
        float
            Costo total por hora
        """
        c = int(np.ceil(c))
        
        # Verificar estabilidad
        if c <= 0:
            return 1e10
        
        queue = MMcQueue(self.lambda_rate, self.mu_rate, c)
        
        if not queue.is_stable():
            return 1e10
        
        metrics = queue.calculate_metrics()
        
        if not metrics['stable']:
            return 1e10
        
        lq = metrics['Lq']
        
        # Costo total = Costo de servidores + Costo de espera
        total_cost = c * self.cost_server + lq * self.cost_waiting
        
        return total_cost
    
    def optimize(self, c_min=1, c_max=50, sla_wq=None):
        """
        Encuentra el número óptimo de servidores
        
        Parameters:
        -----------
        c_min : int
            Número mínimo de servidores a considerar
        c_max : int
            Número máximo de servidores a considerar
        sla_wq : float, optional
            SLA: Tiempo máximo de espera en cola (restricción)
            
        Returns:
        --------
        dict
            Resultados de la optimización
        """
        # Calcular c_min necesario para estabilidad
        c_stability = int(np.ceil(self.lambda_rate / self.mu_rate)) + 1
        c_min = max(c_min, c_stability)
        
        best_c = None
        best_cost = np.inf
        best_metrics = None
        
        # Evaluar todos los valores enteros de c
        results = []
        
        for c in range(c_min, c_max + 1):
            queue = MMcQueue(self.lambda_rate, self.mu_rate, c)
            
            if not queue.is_stable():
                continue
            
            metrics = queue.calculate_metrics()
            
            # Verificar restricción SLA si existe
            if sla_wq is not None and metrics['Wq'] > sla_wq:
                continue
            
            cost = self.objective_function(c)
            
            results.append({
                'c': c,
                'cost': cost,
                'Lq': metrics['Lq'],
                'Wq': metrics['Wq'],
                'rho': metrics['rho'],
                'meets_sla': metrics['Wq'] <= sla_wq if sla_wq else True
            })
            
            if cost < best_cost:
                best_cost = cost
                best_c = c
                best_metrics = metrics
        
        if best_c is None:
            return {
                'success': False,
                'message': 'No se encontró solución factible'
            }
        
        return {
            'success': True,
            'optimal_c': best_c,
            'total_cost': best_cost,
            'server_cost': best_c * self.cost_server,
            'waiting_cost': best_metrics['Lq'] * self.cost_waiting,
            'metrics': best_metrics,
            'all_results': results,
            'sla_wq': sla_wq
        }
    
    def sensitivity_analysis(self, c_range=None):
        """
        Analiza sensibilidad de costos para diferentes valores de c
        
        Parameters:
        -----------
        c_range : tuple, optional
            (c_min, c_max). Si None, usa rango automático
            
        Returns:
        --------
        dict
            Análisis de sensibilidad con costos para cada c
        """
        if c_range is None:
            c_stability = int(np.ceil(self.lambda_rate / self.mu_rate)) + 1
            c_range = (c_stability, c_stability + 20)
        
        c_min, c_max = c_range
        
        results = {
            'c_values': [],
            'total_costs': [],
            'server_costs': [],
            'waiting_costs': [],
            'utilizations': [],
            'wq_values': [],
            'lq_values': []
        }
        
        for c in range(c_min, c_max + 1):
            queue = MMcQueue(self.lambda_rate, self.mu_rate, c)
            
            if not queue.is_stable():
                continue
            
            metrics = queue.calculate_metrics()
            
            server_cost = c * self.cost_server
            waiting_cost = metrics['Lq'] * self.cost_waiting
            total_cost = server_cost + waiting_cost
            
            results['c_values'].append(c)
            results['total_costs'].append(total_cost)
            results['server_costs'].append(server_cost)
            results['waiting_costs'].append(waiting_cost)
            results['utilizations'].append(metrics['rho'])
            results['wq_values'].append(metrics['Wq'])
            results['lq_values'].append(metrics['Lq'])
        
        # Encontrar óptimo
        if results['total_costs']:
            min_idx = np.argmin(results['total_costs'])
            results['optimal_c'] = results['c_values'][min_idx]
            results['optimal_cost'] = results['total_costs'][min_idx]
        
        return results
    
    def compare_scenarios(self, scenarios):
        """
        Compara múltiples escenarios de costos
        
        Parameters:
        -----------
        scenarios : list of dict
            Lista de escenarios con 'name', 'cost_server', 'cost_waiting'
            
        Returns:
        --------
        list
            Resultados de optimización para cada escenario
        """
        results = []
        
        for scenario in scenarios:
            temp_optimizer = CostOptimizer(
                self.lambda_rate,
                self.mu_rate,
                scenario['cost_server'],
                scenario['cost_waiting']
            )
            
            opt_result = temp_optimizer.optimize()
            opt_result['scenario_name'] = scenario['name']
            results.append(opt_result)
        
        return results
