"""tests/test_parametros_dominio/test_tasas.py - Tests para TasasRecuperacionParametros."""

import pytest

from core.parametros_dominio import TasasRecuperacionParametros


class TestTasasRecuperacionParametros:
    """Suite de tests para validación de tasas de recuperación."""

    def test_init_default_valores(self):
        """Verifica que las tasas por defecto estén en [0, 1]."""
        tasas = TasasRecuperacionParametros()
        assert 0.0 <= tasas.tasa_placas_sanas <= 1.0
        assert 0.0 <= tasas.tasa_opticas_sanas <= 1.0
        assert 0.0 <= tasas.tasa_discos_sanos <= 1.0

    def test_validar_default(self):
        """Verifica que los valores por defecto pasen validación."""
        tasas = TasasRecuperacionParametros()
        errores = tasas.validar()
        assert len(errores) == 0

    def test_validar_tasa_fuera_rango(self):
        """Verifica que se detecte tasa > 1."""
        tasas = TasasRecuperacionParametros()
        tasas.tasa_placas_sanas = 1.5
        errores = tasas.validar()
        assert len(errores) > 0

    def test_validar_tasa_negativa(self):
        """Verifica que se detecte tasa < 0."""
        tasas = TasasRecuperacionParametros()
        tasas.tasa_opticas_sanas = -0.1
        errores = tasas.validar()
        assert len(errores) > 0

    def test_validar_extremos(self):
        """Verifica que 0.0 y 1.0 sean válidos."""
        tasas = TasasRecuperacionParametros()
        tasas.tasa_placas_sanas = 0.0
        tasas.tasa_opticas_sanas = 1.0
        tasas.tasa_discos_sanos = 0.5
        errores = tasas.validar()
        assert len(errores) == 0

    def test_repr(self):
        """Verifica que __repr__ retorne string válido."""
        tasas = TasasRecuperacionParametros()
        repr_str = repr(tasas)
        assert "TasasRecuperacionParametros" in repr_str
