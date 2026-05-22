"""tests/test_parametros_dominio/test_precios.py - Tests para PreciosParametros."""

import pytest

from core.parametros_dominio import PreciosParametros


class TestPreciosParametros:
    """Suite de tests para validación de precios."""

    def test_init_default_valores(self):
        """Verifica que los precios por defecto sean coherentes."""
        precios = PreciosParametros()
        assert precios.precio_oro == 210_000.0
        assert precios.precio_cobre == 8_500.0
        assert precios.precio_plastico == 60.0
        assert precios.precio_almacenamiento_min < precios.precio_almacenamiento_max

    def test_validar_todos_positivos(self):
        """Verifica que todos los precios por defecto sean no negativos."""
        precios = PreciosParametros()
        errores = precios.validar()
        assert len(errores) == 0

    def test_validar_precio_negativo(self):
        """Verifica que se detecte precio negativo."""
        precios = PreciosParametros()
        precios.precio_oro = -1000
        errores = precios.validar()
        assert len(errores) > 0
        assert "Precio Oro" in errores[0]

    def test_validar_almacenamiento_rango(self):
        """Verifica que se detecte cuando mín > máx."""
        precios = PreciosParametros()
        precios.precio_almacenamiento_min = 200.0
        precios.precio_almacenamiento_max = 50.0
        errores = precios.validar()
        assert len(errores) > 0
        assert "mínimo" in errores[0].lower() and "máximo" in errores[0].lower()

    def test_validar_cero_es_valido(self):
        """Verifica que precio 0 sea válido (puede haber remates)."""
        precios = PreciosParametros()
        precios.precio_plastico = 0.0
        errores = precios.validar()
        assert len(errores) == 0

    def test_repr(self):
        """Verifica que __repr__ retorne string válido."""
        precios = PreciosParametros()
        repr_str = repr(precios)
        assert "PreciosParametros" in repr_str
        assert "oro=" in repr_str.lower()
