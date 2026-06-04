import math
from typing import Tuple, List, Dict

from core.gcl import GeneradorCongruencialLineal


class PruebaKolmogorovSmirnov:
    """
    Implementación de la prueba estadística de Kolmogorov-Smirnov (K-S)
    para evaluar la bondad de ajuste de un Generador de Números 
    Pseudoaleatorios a la distribución Uniforme(0, 1).
    """

    # Tabla de valores críticos aproximados para K-S cuando N > 35
    # Clave: nivel de significancia (alpha), Valor: Coeficiente
    COEFICIENTES_CRITICOS = {
        0.20: 1.07,
        0.10: 1.22,
        0.05: 1.36,
        0.01: 1.63,
        0.005: 1.73,
        0.001: 1.95
    }

    def __init__(self, generador: GeneradorCongruencialLineal):
        """Inicializa la prueba con una instancia del GCL"""
        self.generador = generador

    def calcular_estadistico(self, muestra: List[float]) -> Tuple[float, float, float]:
        """
        Calcula el estadístico de prueba D para una muestra dada

        Returns:
            Tupla (D, D_mas, D_menos)
        """
        n = len(muestra)
        if n == 0:
            raise ValueError("La muestra no puede estar vacía.")

        # La prueba K-S requiere que los datos estén ordenados de menor a mayor
        muestra_ordenada = sorted(muestra)

        d_mas_max = 0.0
        d_menos_max = 0.0

        for i, x_i in enumerate(muestra_ordenada):
            # i en matemáticas es de 1 a N, en python el índice es de 0 a N-1
            # Por lo tanto, el i matemático es (i_py + 1)
            i_mat = i + 1
            
            d_mas = (i_mat / n) - x_i
            d_menos = x_i - ((i_mat - 1) / n)

            if d_mas > d_mas_max:
                d_mas_max = d_mas
            if d_menos > d_menos_max:
                d_menos_max = d_menos

        d = max(d_mas_max, d_menos_max)
        return d, d_mas_max, d_menos_max

    def obtener_valor_critico(self, alpha: float, n: int) -> float:
        """
        Calcula el valor crítico aproximado D_alpha
        Válido principalmente para n > 35
        """
        if n <= 35:
            pass
            
        if alpha not in self.COEFICIENTES_CRITICOS:
            raise ValueError(f"Alpha {alpha} no soportado. Valores permitidos: {list(self.COEFICIENTES_CRITICOS.keys())}")
            
        coeficiente = self.COEFICIENTES_CRITICOS[alpha]
        return coeficiente / math.sqrt(n)

    def ejecutar_prueba(self, n: int = 1000, alpha: float = 0.05) -> Dict:
        """
        Ejecuta la prueba K-S generando N números del GCL y calculando la uniformidad
        
        Args:
            n: Tamaño de la muestra a generar y evaluar
            alpha: Nivel de significancia
            
        Returns:
            Diccionario con los resultados detallados de la prueba
        """
        if n <= 0:
            raise ValueError("El tamaño de la muestra debe ser mayor a cero ")

        # 1. Generar la muestra de números aleatorios en [0, 1)
        muestra = [self.generador.siguiente_u() for _ in range(n)]

        # 2. Calcular los estadísticos D+, D- y D
        d, d_mas, d_menos = self.calcular_estadistico(muestra)

        # 3. Calcular el valor crítico
        d_critico = self.obtener_valor_critico(alpha, n)

        # 4. Decisión: Si D < D_critico, no se rechaza la hipótesis de uniformidad
        aprobado = d < d_critico

        return {
            "aprobado": aprobado,
            "d_calculado": d,
            "d_critico": d_critico,
            "d_mas": d_mas,
            "d_menos": d_menos,
            "n": n,
            "alpha": alpha,
            "muestra_min": min(muestra),
            "muestra_max": max(muestra)
        }
