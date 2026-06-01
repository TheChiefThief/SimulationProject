import pytest
import math

from core.gcl import GeneradorCongruencialLineal
from core.prueba_estadistica import PruebaKolmogorovSmirnov

class TestPruebaKolmogorovSmirnov:

    def setup_method(self):
        # Usamos una semilla fija para asegurar reproducibilidad en los tests
        self.gcl = GeneradorCongruencialLineal(semilla=12345)
        self.prueba = PruebaKolmogorovSmirnov(self.gcl)

    def test_calcular_estadistico_basico(self):
        # Muestra conocida
        muestra = [0.1, 0.2, 0.3, 0.4, 0.5]
        # Para i=1: x_i=0.1. d+ = 1/5 - 0.1 = 0.1, d- = 0.1 - 0/5 = 0.1
        # Para i=2: x_i=0.2. d+ = 2/5 - 0.2 = 0.2, d- = 0.2 - 1/5 = 0.0
        # Para i=3: x_i=0.3. d+ = 3/5 - 0.3 = 0.3, d- = 0.3 - 2/5 = -0.1
        # Para i=4: x_i=0.4. d+ = 4/5 - 0.4 = 0.4, d- = 0.4 - 3/5 = -0.2
        # Para i=5: x_i=0.5. d+ = 5/5 - 0.5 = 0.5, d- = 0.5 - 4/5 = -0.3
        # D_mas_max = 0.5, D_menos_max = 0.1, D = 0.5
        d, d_mas, d_menos = self.prueba.calcular_estadistico(muestra)
        
        assert math.isclose(d_mas, 0.5, rel_tol=1e-5)
        assert math.isclose(d_menos, 0.1, rel_tol=1e-5)
        assert math.isclose(d, 0.5, rel_tol=1e-5)

    def test_calcular_estadistico_muestra_vacia(self):
        with pytest.raises(ValueError, match="La muestra no puede estar vacía."):
            self.prueba.calcular_estadistico([])

    def test_obtener_valor_critico_valido(self):
        # alpha = 0.05, n = 100 -> 1.36 / 10 = 0.136
        critico = self.prueba.obtener_valor_critico(0.05, 100)
        assert math.isclose(critico, 0.136, rel_tol=1e-5)

    def test_obtener_valor_critico_invalido(self):
        with pytest.raises(ValueError, match="Alpha 0.99 no soportado"):
            self.prueba.obtener_valor_critico(0.99, 100)

    def test_ejecutar_prueba(self):
        # Ejecutamos la prueba con n=1000 y alpha=0.05
        # El GCL implementado es bueno y debería pasar la prueba
        resultado = self.prueba.ejecutar_prueba(n=1000, alpha=0.05)
        
        assert "aprobado" in resultado
        assert "d_calculado" in resultado
        assert "d_critico" in resultado
        assert resultado["n"] == 1000
        assert resultado["alpha"] == 0.05
        assert resultado["d_calculado"] >= 0
        assert resultado["d_critico"] > 0
        
        assert resultado["aprobado"] is True

    def test_ejecutar_prueba_parametros_invalidos(self):
        with pytest.raises(ValueError, match="El tamaño de la muestra debe ser mayor a cero."):
            self.prueba.ejecutar_prueba(n=0)
