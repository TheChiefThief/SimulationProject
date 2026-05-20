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


class GeneradorCongruencialLineal:
    """
    Generador Congruencial Lineal (GCL) puro.
    Genera números pseudoaleatorios sin usar ninguna librería de aleatorización.

    Parámetros del método:
        a = 1664525      (multiplicador)
        c = 1013904223   (incremento)
        m = 2^32         (módulo)
    """

    # Constantes con período completo (Numerical Recipes)
    _A = 1664525
    _C = 1013904223
    _M = 4294967296  # 2^32

    def __init__(self, semilla: int = None):
        """
        Inicializa el GCL.

        Args:
            semilla: Valor inicial X_0. Si no se provee, se genera
                     automáticamente a partir de los nanosegundos del
                     reloj del sistema (time.time_ns).
        """
        if semilla is None:
            # La semilla puede ser generada por cualquier método.
            # Usamos nanosegundos del sistema y los reducimos al rango [0, m)
            self._x = time.time_ns() % self._M
        else:
            if not isinstance(semilla, int) or semilla < 0:
                raise ValueError("La semilla debe ser un entero no negativo.")
            self._x = semilla % self._M

        # Guardamos la semilla original para referencia y reproducibilidad
        self._semilla_original = self._x
        self._iteraciones = 0

    # ------------------------------------------------------------------
    # Propiedades de solo lectura
    # ------------------------------------------------------------------

    @property
    def semilla(self) -> int:
        """Semilla con la que fue inicializado este generador."""
        return self._semilla_original

    @property
    def iteraciones(self) -> int:
        """Cantidad de números generados hasta el momento."""
        return self._iteraciones

    # ------------------------------------------------------------------
    # Métodos de generación
    # ------------------------------------------------------------------

    def siguiente_crudo(self) -> int:
        """
        Avanza el GCL y devuelve el próximo entero en [0, m).

        Returns:
            Entero pseudoaleatorio en el rango [0, 2^32).
        """
        self._x = (self._A * self._x + self._C) % self._M
        self._iteraciones += 1
        return self._x

    def siguiente_u(self) -> float:
        """
        Genera el próximo número pseudoaleatorio uniformemente distribuido
        en el intervalo semi-abierto [0.0, 1.0).

        Returns:
            Float en [0.0, 1.0).
        """
        return self.siguiente_crudo() / self._M

    def siguiente_rango(self, a: float, b: float) -> float:
        """
        Genera un número pseudoaleatorio uniformemente distribuido en [a, b).

        Args:
            a: Límite inferior (inclusive).
            b: Límite superior (exclusive).

        Returns:
            Float en [a, b).

        Raises:
            ValueError: Si a >= b.
        """
        if a >= b:
            raise ValueError(f"Se requiere a < b, pero se recibió a={a}, b={b}.")
        return a + (b - a) * self.siguiente_u()

    def siguiente_entero(self, a: int, b: int) -> int:
        """
        Genera un entero pseudoaleatorio en el rango cerrado [a, b].

        Args:
            a: Límite inferior (inclusive).
            b: Límite superior (inclusive).

        Returns:
            Entero en [a, b].

        Raises:
            ValueError: Si a > b.
        """
        if a > b:
            raise ValueError(f"Se requiere a <= b, pero se recibió a={a}, b={b}.")
        # Rango de (b - a + 1) valores enteros
        rango = b - a + 1
        return a + (self.siguiente_crudo() % rango)

    def siguiente_bernoulli(self, p: float) -> bool:
        """
        Genera una variable de Bernoulli: True con probabilidad p.

        Args:
            p: Probabilidad de éxito, en [0, 1].

        Returns:
            True con probabilidad p, False con probabilidad (1 - p).
        """
        return self.siguiente_u() < p

    def siguiente_triangular(self, minimo: float, moda: float, maximo: float) -> float:
        """
        Genera un número con distribución triangular usando el método
        de la transformada inversa (implementación manual).

        Args:
            minimo: Valor mínimo.
            moda:   Valor más probable (moda).
            maximo: Valor máximo.

        Returns:
            Float con distribución triangular en [minimo, maximo].
        """
        if not (minimo <= moda <= maximo):
            raise ValueError("Se requiere minimo <= moda <= maximo.")

        u = self.siguiente_u()
        rango = maximo - minimo
        punto_corte = (moda - minimo) / rango  # F(moda)

        if u <= punto_corte:
            return minimo + (u * rango * (moda - minimo)) ** 0.5
        else:
            return maximo - ((1 - u) * rango * (maximo - moda)) ** 0.5

    def __repr__(self) -> str:
        return (
            f"GeneradorCongruencialLineal("
            f"semilla={self._semilla_original}, "
            f"iteraciones={self._iteraciones})"
        )
