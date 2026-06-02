import math
from core.gcl import GeneradorCongruencialLineal


class Distribuciones:
    """
    Clase que agrupa los métodos para generar números con distintas
    distribuciones estadísticas a partir de un Generador Congruencial Lineal.
    """

    def __init__(self, gcl: GeneradorCongruencialLineal):
        """
        Inicializa la clase con un generador base.

        Args:
            gcl: Instancia de GeneradorCongruencialLineal que proveerá
                 la aleatoriedad uniforme subyacente.
        """
        self.gcl = gcl

    def siguiente_rango(self, a: float, b: float) -> float:
        """
        Genera un número pseudoaleatorio uniformemente distribuido en [a, b).

        Args:
            a: Límite inferior (inclusive).
            b: Límite superior (exclusive).

        Returns:
            Float en [a, b).
        """
        if a >= b:
            raise ValueError(f"Se requiere a < b, pero se recibió a={a}, b={b}.")
        return a + (b - a) * self.gcl.siguiente_u()

    def siguiente_entero(self, a: int, b: int) -> int:
        """
        Genera un entero pseudoaleatorio en el rango cerrado [a, b].

        Args:
            a: Límite inferior (inclusive).
            b: Límite superior (inclusive).

        Returns:
            Entero en [a, b].
        """
        if a > b:
            raise ValueError(f"Se requiere a <= b, pero se recibió a={a}, b={b}.")
        rango = b - a + 1
        return a + (self.gcl.siguiente_crudo() % rango)

    def siguiente_bernoulli(self, p: float) -> bool:
        """
        Genera una variable de Bernoulli: True con probabilidad p.

        Args:
            p: Probabilidad de éxito, en [0, 1].

        Returns:
            True con probabilidad p, False con probabilidad (1 - p).
        """
        return self.gcl.siguiente_u() < p

    # Alias por compatibilidad
    def siguiente_binomial(self, p: float) -> bool:
        return self.siguiente_bernoulli(p)

    def siguiente_normal(self, media: float, desviacion_estandar: float) -> float:
        """
        Genera un número con distribución normal usando el método de Box-Muller.

        Args:
            media: Media de la distribución (mu).
            desviacion_estandar: Desviación estándar (sigma).

        Returns:
            Float con distribución normal.
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
        Genera un número con distribución exponencial.

        Args:
            media: Valor medio (E[x] = 1/lambda).

        Returns:
            Float con distribución exponencial.
        """
        if media <= 0:
            raise ValueError("La media debe ser mayor a cero.")
        u = self.gcl.siguiente_u()
        return -media * math.log(1.0 - u)
