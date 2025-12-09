# 🚀 Sistema Inteligente de Auto-scaling para Servidores Cloud

## Basado en Teoría de Colas e Investigación de Operaciones

### 📋 Descripción del Proyecto

Este proyecto implementa un sistema completo de optimización de costos para servidores cloud (AWS/Azure) utilizando **Teoría de Colas** e **Investigación de Operaciones**. 

**El Problema**: Una empresa tiene servidores en la nube. Si tiene pocos servidores, los clientes esperan mucho (alta latencia = pérdida de clientes). Si tiene muchos servidores, gasta dinero innecesariamente.

**La Solución**: Usar modelos matemáticos M/M/c para determinar el número óptimo de servidores que minimiza costos totales manteniendo un SLA aceptable.

---

## 🎯 Objetivos

1. **Análisis Estadístico**: Ajustar distribuciones a datos reales de tráfico
2. **Modelado Matemático**: Implementar modelo M/M/c de teoría de colas
3. **Optimización**: Minimizar función objetivo `Z = c·Cs + Lq·Cw`
4. **Simulación**: Validar resultados teóricos con Monte Carlo
5. **Visualización**: Dashboard interactivo con Streamlit

---

## 📦 Estructura del Proyecto

```
proyecto-io-colas/
├── README.md
├── requirements.txt
├── data/
│   └── server_logs.csv          # Dataset sintético de 10,000 registros
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb    # Análisis exploratorio
│   ├── 02_distribution_fitting.ipynb     # Ajuste de distribuciones
│   ├── 03_queue_modeling.ipynb          # Modelado de colas M/M/c
│   └── 04_optimization.ipynb            # Optimización de costos
├── src/
│   ├── __init__.py
│   ├── data_processor.py         # Procesamiento de datos
│   ├── distribution_fitter.py    # Ajuste estadístico
│   ├── queue_models.py           # Modelos M/M/c y simulación
│   └── optimizer.py              # Optimización de costos
└── app/
    └── dashboard.py              # Dashboard interactivo (Streamlit)
```

---

## 🔧 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/fergmlx/proyecto-io-colas.git
cd proyecto-io-colas

# Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 🚀 Uso

### Opción 1: Notebooks Jupyter (Análisis Completo)

```bash
jupyter notebook
```

Ejecutar los notebooks en orden:
1. `01_exploratory_analysis.ipynb` - Exploración de datos
2. `02_distribution_fitting.ipynb` - Ajuste de distribuciones
3. `03_queue_modeling.ipynb` - Modelado y simulación
4. `04_optimization.ipynb` - Optimización final

### Opción 2: Dashboard Interactivo

```bash
streamlit run app/dashboard.py
```

Abre tu navegador en `http://localhost:8501`

---

## 📊 Metodología

### 1. **Recolección de Datos**
- Logs de servidor con timestamps de llegada y tiempos de servicio
- 10,000 registros sintéticos generados con:
  - Llegadas: Proceso Poisson (λ = 120 req/hora)
  - Servicio: Distribución Exponencial (μ = 30 req/hora)

### 2. **Análisis Estadístico**
- Ajuste de distribuciones (Exponencial, Gamma, Log-normal, Weibull)
- Tests de bondad de ajuste (Kolmogorov-Smirnov, Chi-cuadrado)
- Identificación de parámetros λ (tasa de llegada) y μ (tasa de servicio)

### 3. **Modelado de Colas**
- Modelo **M/M/c** (Poisson/Exponencial/c servidores)
- Cálculo de métricas:
  - **L**: Número promedio de clientes en el sistema
  - **Lq**: Número promedio en cola
  - **W**: Tiempo promedio en el sistema
  - **Wq**: Tiempo promedio en cola
  - **ρ**: Factor de utilización

### 4. **Optimización de Costos**

**Variables de Decisión**:
- `c`: Número de servidores

**Parámetros**:
- `λ`: Tasa de llegada (req/segundo)
- `μ`: Tasa de servicio por servidor
- `Cs`: Costo operativo por servidor ($/hora)
- `Cw`: Costo de espera ($/cliente)

**Función Objetivo**:
```
Min Z = c·Cs + Lq·Cw
```

**Restricciones**:
- `ρ = λ/(c·μ) < 1` (estabilidad)
- `Wq ≤ Wq_max` (SLA opcional)

### 5. **Validación**
- Simulación de Monte Carlo con SimPy
- Comparación resultados teóricos vs empíricos

---

## 📈 Resultados Esperados

Para el dataset de ejemplo (λ=120 req/hora, μ=30 req/hora):
- **Configuración óptima**: ~5 servidores
- **Tiempo en cola**: <2 segundos
- **Utilización**: ~80%
- **Ahorro mensual**: Comparado con sobre-provisionar

---

## 🛠️ Tecnologías Utilizadas

| Categoría | Librerías |
|-----------|-----------|
| **Análisis de datos** | pandas, numpy |
| **Estadística** | scipy.stats |
| **Teoría de colas** | Implementación propia + scipy |
| **Simulación** | simpy |
| **Optimización** | scipy.optimize |
| **Visualización** | matplotlib, seaborn, plotly |
| **Dashboard** | streamlit |
| **Notebooks** | jupyter |

---

## 📚 Referencias Teóricas

- **Erlang-C Formula**: Para calcular probabilidad de espera en M/M/c
- **Ley de Little**: `L = λ·W` y `Lq = λ·Wq`
- **Factor de utilización**: `ρ = λ/(c·μ)`

---

## 👨‍💻 Autor

**Proyecto de Investigación de Operaciones**  
Ingeniería en Sistemas Computacionales  
GitHub: [@fergmlx](https://github.com/fergmlx)

---

## 📝 Licencia

MIT License - Libre uso académico y comercial

---

## 🎓 Aplicaciones Prácticas

- Auto-scaling en AWS/Azure/GCP
- Dimensionamiento de call centers
- Optimización de líneas de producción
- Planificación de capacidad en sistemas distribuidos
- Gestión de recursos en microservicios

---

**¡Listo para optimizar tu infraestructura cloud! 🚀**