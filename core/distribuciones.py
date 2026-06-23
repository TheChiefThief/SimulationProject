import math
from core.gcl import GeneradorCongruencialLineal


class Distribuciones:

    def __init__(self, gcl: GeneradorCongruencialLineal):
        self.gcl = gcl

    def siguiente_rango(self, a: float, b: float) -> float:
        if a >= b:
            raise ValueError(f"Se requiere a < b, pero se recibió a={a}, b={b}.")
        return a + (b - a) * self.gcl.siguiente_u()

    def siguiente_normal(self, media: float, desviacion_estandar: float) -> float:

        if desviacion_estandar < 0:
            raise ValueError("La desviación estándar debe ser no negativa.")

        u1 = self.gcl.siguiente_u()
        while u1 == 0.0:
            u1 = self.gcl.siguiente_u()
        u2 = self.gcl.siguiente_u()

        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return media + z0 * desviacion_estandar

    def siguiente_exponencial(self, media: float) -> float:

        if media <= 0:
            raise ValueError("La media debe ser mayor a cero.")
        u = self.gcl.siguiente_u()
        return -media * math.log(1.0 - u)
