"""
core/gcl.py
-----------
Generador Congruencial Lineal (GCL) implementado 100% en código propio,
sin uso de librerías externas de aleatorización.

Fórmula:
    X_{n+1} = (a * X_n + c) mod m

Constantes de Numerical Recipes (período completo garantizado para m=2^32):
    a = 1664525
    c = 1013904223
    m = 2^32  (= 4294967296)

La semilla inicial se obtiene de time.time_ns() que provee nanosegundos
del reloj del sistema, garantizando variabilidad entre ejecuciones.
"""

import time
import math


class GeneradorCongruencialLineal:

    _A = 1664525
    _C = 1013904223
    _M = 4294967296  # 2^32

    def __init__(self, semilla: int = None):
        if semilla is None:
            self._x = time.time_ns() % self._M
        else:
            if not isinstance(semilla, int) or semilla < 0:
                raise ValueError("La semilla debe ser un entero no negativo.")
            self._x = semilla % self._M

        self._semilla_original = self._x
        self._iteraciones = 0

    @property
    def semilla(self) -> int:
        """Semilla con la que fue inicializado este generador."""
        return self._semilla_original

    @property
    def iteraciones(self) -> int:
        """Cantidad de números generados hasta el momento."""
        return self._iteraciones

    def siguiente_crudo(self) -> int:

        self._x = (self._A * self._x + self._C) % self._M
        self._iteraciones += 1
        return self._x

    def siguiente_u(self) -> float:
        return self.siguiente_crudo() / self._M


    def __repr__(self) -> str:
        return (
            f"GeneradorCongruencialLineal("
            f"semilla={self._semilla_original}, "
            f"iteraciones={self._iteraciones})"
        )
