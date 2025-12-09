"""
Queue Models Module
Implementa modelos de teoría de colas M/M/c y simulación
"""

import numpy as np
from scipy.special import factorial
from scipy.stats import expon
import simpy


class MMcQueue:
    """Modelo de cola M/M/c (Poisson/Exponencial/c servidores)"""
    
    def __init__(self, lambda_rate, mu_rate, c_servers):
        """
        Inicializa modelo M/M/c
        
        Parameters:
        -----------
        lambda_rate : float
            Tasa de llegada (clientes por unidad de tiempo)
        mu_rate : float
            Tasa de servicio por servidor (clientes por unidad de tiempo)
        c_servers : int
            Número de servidores
        """
        self.lambda_rate = lambda_rate
        self.mu_rate = mu_rate
        self.c = c_servers
        self.rho = lambda_rate / (c_servers * mu_rate)
        
    def is_stable(self):
        """Verifica si el sistema es estable (rho < 1)"""
        return self.rho < 1
    
    def _calculate_p0(self):
        """Calcula probabilidad de 0 clientes en el sistema"""
        c = self.c
        lam = self.lambda_rate
        mu = self.mu_rate
        rho = self.rho
        
        sum_term = sum([(lam/mu)**n / factorial(n) for n in range(c)])
        last_term = (lam/mu)**c / factorial(c) * (1 / (1 - rho))
        
        p0 = 1 / (sum_term + last_term)
        return p0
    
    def calculate_metrics(self):
        """
        Calcula todas las métricas del sistema M/M/c
        
        Returns:
        --------
        dict
            Diccionario con L, Lq, W, Wq, rho, P0, Pw (Erlang-C)
        """
        if not self.is_stable():
            return {
                'stable': False,
                'rho': self.rho,
                'message': 'Sistema inestable: rho >= 1'
            }
        
        c = self.c
        lam = self.lambda_rate
        mu = self.mu_rate
        rho = self.rho
        
        # P0: Probabilidad de sistema vacío
        p0 = self._calculate_p0()
        
        # Pw (Erlang-C): Probabilidad de esperar en cola
        pw = ((lam/mu)**c / factorial(c)) * (1 / (1 - rho)) * p0
        
        # Lq: Número promedio en cola
        lq = pw * rho / (1 - rho)
        
        # Wq: Tiempo promedio en cola
        wq = lq / lam
        
        # L: Número promedio en sistema
        l = lq + lam / mu
        
        # W: Tiempo promedio en sistema
        w = wq + 1 / mu
        
        return {
            'stable': True,
            'rho': rho,
            'utilization_percent': rho * 100,
            'P0': p0,
            'Pw_erlang_c': pw,
            'Lq': lq,
            'L': l,
            'Wq': wq,
            'W': w,
            'lambda': lam,
            'mu': mu,
            'c': c
        }


class QueueSimulator:
    """Simulación de cola usando SimPy (Monte Carlo)"""
    
    def __init__(self, lambda_rate, mu_rate, c_servers, sim_time=10000):
        """
        Configura simulación de cola
        
        Parameters:
        -----------
        lambda_rate : float
            Tasa de llegada
        mu_rate : float
            Tasa de servicio por servidor
        c_servers : int
            Número de servidores
        sim_time : float
            Tiempo de simulación
        """
        self.lambda_rate = lambda_rate
        self.mu_rate = mu_rate
        self.c_servers = c_servers
        self.sim_time = sim_time
        
        self.wait_times = []
        self.system_times = []
        self.queue_lengths = []
        
    def customer(self, env, name, server, arrival_time):
        """Proceso de un cliente en el sistema"""
        arrive = env.now
        
        with server.request() as req:
            yield req
            
            wait = env.now - arrive
            self.wait_times.append(wait)
            
            service_time = expon.rvs(scale=1/self.mu_rate)
            yield env.timeout(service_time)
            
            system_time = env.now - arrive
            self.system_times.append(system_time)
    
    def customer_generator(self, env, server):
        """Genera llegadas de clientes siguiendo proceso Poisson"""
        customer_count = 0
        while True:
            interarrival = expon.rvs(scale=1/self.lambda_rate)
            yield env.timeout(interarrival)
            
            customer_count += 1
            env.process(self.customer(env, f'Customer{customer_count}', 
                                      server, env.now))
            
            # Registrar longitud de cola
            self.queue_lengths.append(len(server.queue))
    
    def run_simulation(self, seed=42):
        """
        Ejecuta la simulación
        
        Parameters:
        -----------
        seed : int
            Semilla para reproducibilidad
            
        Returns:
        --------
        dict
            Métricas empíricas de la simulación
        """
        np.random.seed(seed)
        
        env = simpy.Environment()
        server = simpy.Resource(env, capacity=self.c_servers)
        
        env.process(self.customer_generator(env, server))
        env.run(until=self.sim_time)
        
        # Calcular métricas empíricas
        wq_sim = np.mean(self.wait_times)
        w_sim = np.mean(self.system_times)
        lq_sim = np.mean(self.queue_lengths)
        l_sim = lq_sim + self.lambda_rate / self.mu_rate
        
        return {
            'Wq_simulated': wq_sim,
            'W_simulated': w_sim,
            'Lq_simulated': lq_sim,
            'L_simulated': l_sim,
            'total_customers': len(self.wait_times),
            'sim_time': self.sim_time,
            'wait_times': self.wait_times,
            'system_times': self.system_times,
            'queue_lengths': self.queue_lengths
        }
