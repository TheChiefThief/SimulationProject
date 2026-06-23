import pytest
from core.gcl import GeneradorCongruencialLineal
from core.distribuciones import Distribuciones

class TestDistribucionesBinomial:

    def setup_method(self):
        # Usamos una semilla fija para asegurar reproducibilidad
        self.gcl = GeneradorCongruencialLineal(semilla=54321)
        self.dist = Distribuciones(self.gcl)

    def test_siguiente_binomial_valores_limite(self):
        # Si n = 0, siempre debe retornar 0 sin importar p
        assert self.dist.siguiente_binomial(0, 0.5) == 0

        # Si p = 0.0, siempre debe retornar 0
        assert self.dist.siguiente_binomial(10, 0.0) == 0

        # Si p = 1.0, siempre debe retornar n
        assert self.dist.siguiente_binomial(10, 1.0) == 10

    def test_siguiente_binomial_excepciones(self):
        # n negativo
        with pytest.raises(ValueError, match="El número de ensayos n debe ser no negativo."):
            self.dist.siguiente_binomial(-5, 0.5)

        # p menor a 0
        with pytest.raises(ValueError, match="La probabilidad p debe estar en el rango"):
            self.dist.siguiente_binomial(10, -0.1)

        # p mayor a 1
        with pytest.raises(ValueError, match="La probabilidad p debe estar en el rango"):
            self.dist.siguiente_binomial(10, 1.1)

    def test_siguiente_binomial_distribucion_estadistica(self):
        # Hacemos una simulación de 1000 iteraciones con n = 10, p = 0.5
        # La media teórica es n * p = 5.0
        n = 10
        p = 0.5
        muestras = [self.dist.siguiente_binomial(n, p) for _ in range(1000)]

        # Validamos que todos los valores generados están en el rango correcto [0, n]
        for m in muestras:
            assert 0 <= m <= n
            assert isinstance(m, int)

        media_observada = sum(muestras) / len(muestras)
        # Con 1000 muestras, la media observada debería estar bastante cerca de 5.0
        assert abs(media_observada - 5.0) < 0.25


class TestDistribucionesUniforme:

    def setup_method(self):
        self.gcl = GeneradorCongruencialLineal(semilla=54321)
        self.dist = Distribuciones(self.gcl)

    def test_siguiente_uniforme_valores_limite(self):
        # a >= b debería lanzar ValueError
        with pytest.raises(ValueError, match="Se requiere a < b"):
            self.dist.siguiente_uniforme(5.0, 5.0)
        with pytest.raises(ValueError, match="Se requiere a < b"):
            self.dist.siguiente_uniforme(5.0, 4.9)

    def test_siguiente_uniforme_rango_correcto(self):
        a = 2.5
        b = 7.5
        muestras = [self.dist.siguiente_uniforme(a, b) for _ in range(1000)]
        for m in muestras:
            assert a <= m < b

    def test_siguiente_uniforme_distribucion_estadistica(self):
        # Muestras uniformes en [0, 10). Media teórica es (0 + 10) / 2 = 5.0
        a = 0.0
        b = 10.0
        muestras = [self.dist.siguiente_uniforme(a, b) for _ in range(5000)]
        media_observada = sum(muestras) / len(muestras)
        assert abs(media_observada - 5.0) < 0.1
