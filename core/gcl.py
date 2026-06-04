"""
Fórmula:
    X_{n+1} = (a * X_n + c) mod m

Constantes de Numerical Recipes (período completo garantizado para m=2^32):
    a = 1664525
    c = 1013904223
    m = 2^32  (= 4294967296)

"""

import time
import math


class GeneradorCongruencialLineal:
    """
    Generador Congruencial Lineal (GCL)

    Parámetros del método:
        a = 1664525      (multiplicador)
        c = 1013904223   (incremento)
        m = 2^32         (módulo)
    """
    _A = 1664525
    _C = 1013904223
    _M = 4294967296  # 2^32

    def __init__(self, semilla: int = None):
        """ Inicializa el GCL """
        if semilla is None:
            self._x = time.time_ns() % self._M
        else:
            if not isinstance(semilla, int) or semilla < 0:
                raise ValueError("La semilla debe ser un entero no negativo")
            self._x = semilla % self._M

        # Guardamos la semilla original para referencia y reproducibilidad
        self._semilla_original = self._x
        self._iteraciones = 0

    # ------------------------------------------------------------------
    # Propiedades de solo lectura
    # ------------------------------------------------------------------

    @property
    def semilla(self) -> int:
        """Semilla con la que fue inicializado este generador"""
        return self._semilla_original

    @property
    def iteraciones(self) -> int:
        """Cantidad de números generados hasta el momento"""
        return self._iteraciones

    # ------------------------------------------------------------------
    # Métodos de generación
    # ------------------------------------------------------------------

    def siguiente_crudo(self) -> int:
        """
        Avanza el GCL y devuelve el próximo entero en [0, m)

        Returns:
            Entero pseudoaleatorio en el rango [0, 2^32)
        """
        self._x = (self._A * self._x + self._C) % self._M
        self._iteraciones += 1
        return self._x

    def siguiente_u(self) -> float:
        """
        Genera el próximo número pseudoaleatorio uniformemente distribuido
        en el intervalo semi-abierto [0.0, 1.0)

        Returns:
            Float en [0.0, 1.0)
        """
        return self.siguiente_crudo() / self._M


    def __repr__(self) -> str:
        return (
            f"GeneradorCongruencialLineal("
            f"semilla={self._semilla_original}, "
            f"iteraciones={self._iteraciones})"
        )
