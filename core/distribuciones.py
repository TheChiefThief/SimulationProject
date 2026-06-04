import math
from core.gcl import GeneradorCongruencialLineal


class Distribuciones:
    """
    Clase que agrupa los métodos para generar números con distintas
    distribuciones estadísticas a partir de un Generador Congruencial Lineal
    """

    def __init__(self, gcl: GeneradorCongruencialLineal):
        """ Inicializa la clase con un generador base """
        self.gcl = gcl

    def siguiente_uniforme(self, a: float, b: float) -> float:
        """
        Genera un número pseudoaleatorio uniformemente distribuido en [a, b)

        Returns:
            Float en [a, b)
        """
        if a >= b:
            raise ValueError(f"Se requiere a < b, pero se recibió a={a}, b={b}.")
        return a + (b - a) * self.gcl.siguiente_u()

    def siguiente_entero(self, a: int, b: int) -> int:
        """
        Genera un entero pseudoaleatorio en el rango cerrado [a, b]
        
        Returns:
            Entero en [a, b]
        """
        if a > b:
            raise ValueError(f"Se requiere a <= b, pero se recibió a={a}, b={b}.")
        rango = b - a + 1
        return a + (self.gcl.siguiente_crudo() % rango)

    def siguiente_binomial(self, n: int, p: float) -> int:
        """
        Genera un número pseudoaleatorio con distribución binomial
        (cantidad de éxitos en n ensayos independientes de Bernoulli de probabilidad p)

        Returns:
            Entero en el rango [0, n]
        """
        if n < 0:
            raise ValueError("El número de ensayos n debe ser no negativo.")
        if not (0.0 <= p <= 1.0):
            raise ValueError("La probabilidad p debe estar en el rango [0, 1].")

        exitos = 0
        for _ in range(n):
            if self.gcl.siguiente_u() < p:
                exitos += 1
        return exitos

    def siguiente_normal(self, media: float, desviacion_estandar: float) -> float:
        """
        Genera un número con distribución normal usando el método de Box-Muller

        Returns:
            Float con distribución normal
        """
        if desviacion_estandar < 0:
            raise ValueError("La desviación estándar debe ser no negativa.")

        u1 = self.gcl.siguiente_u()
        while u1 == 0.0:
            u1 = self.gcl.siguiente_u()
        u2 = self.gcl.siguiente_u()

        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return media + z0 * desviacion_estandar

    def siguiente_exponencial(self, media: float) -> float:
        """
        Genera un número con distribución exponencial

        Returns:
            Float con distribución exponencial
        """
        if media <= 0:
            raise ValueError("La media debe ser mayor a cero.")
        u = self.gcl.siguiente_u()
        return -media * math.log(1.0 - u)
