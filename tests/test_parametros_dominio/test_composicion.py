"""tests/test_parametros_dominio/test_composicion.py - Tests para ComposicionParametros."""

import pytest

from core.parametros_dominio import ComposicionParametros


class TestComposicionParametros:
    """Suite de tests para validación de composición."""

    def test_init_fracciones_validas(self):
        """Verifica que las fracciones por defecto sumen ~1."""
        composicion = ComposicionParametros()
        suma_camara = (
            composicion.camara_fraccion_plastico
            + composicion.camara_fraccion_placas
            + composicion.camara_fraccion_metal
            + composicion.camara_fraccion_opticos
        )
        assert 0.99 <= suma_camara <= 1.01

        suma_dvr = (
            composicion.dvr_fraccion_hdd
            + composicion.dvr_fraccion_metal
            + composicion.dvr_fraccion_placas
        )
        assert 0.99 <= suma_dvr <= 1.01

    def test_validar_default(self):
        """Verifica que los valores por defecto pasen validación."""
        composicion = ComposicionParametros()
        errores = composicion.validar()
        assert len(errores) == 0

    def test_validar_fraccion_fuera_rango(self):
        """Verifica que se detecte fracción > 1."""
        composicion = ComposicionParametros()
        composicion.camara_fraccion_plastico = 1.5
        errores = composicion.validar()
        assert len(errores) > 0
        assert "Plástico" in errores[0] or "entre 0 y 1" in errores[0]

    def test_validar_fraccion_negativa(self):
        """Verifica que se detecte fracción < 0."""
        composicion = ComposicionParametros()
        composicion.dvr_fraccion_hdd = -0.1
        errores = composicion.validar()
        assert len(errores) > 0

    def test_validar_suma_fracciones_invalida(self):
        """Verifica que se detecte cuando suma no es ~1."""
        composicion = ComposicionParametros()
        composicion.camara_fraccion_plastico = 0.8  # suma será > 1
        errores = composicion.validar()
        assert any("suma" in e.lower() for e in errores)

    def test_validar_peso_positivo(self):
        """Verifica que pesos deben ser positivos."""
        composicion = ComposicionParametros()
        composicion.peso_camara = 0.0
        errores = composicion.validar()
        assert any("peso" in e.lower() for e in errores)

    def test_validar_rendimiento_rango(self):
        """Verifica que rendimientos estén en [0, 1]."""
        composicion = ComposicionParametros()
        composicion.rendimiento_plastico = 1.5
        errores = composicion.validar()
        assert any("rendimiento" in e.lower() for e in errores)

    def test_repr(self):
        """Verifica que __repr__ retorne string válido."""
        composicion = ComposicionParametros()
        repr_str = repr(composicion)
        assert "ComposicionParametros" in repr_str
