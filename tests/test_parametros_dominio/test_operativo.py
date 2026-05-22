"""tests/test_parametros_dominio/test_operativo.py - Tests para ParametrosOperativo."""

import pytest

from core.parametros_dominio import ParametrosOperativo


class TestParametrosOperativo:
    """Suite de tests para validación de parámetros operativos."""

    def test_init_default_valores(self):
        """Verifica que los valores por defecto sean coherentes."""
        operativo = ParametrosOperativo()
        assert operativo.horas_trabajo == 8.0
        assert operativo.cantidad_empleados == 5
        assert operativo.energia_consumida == 100.0
        assert operativo.coeficiente_perdida == 0.05

    def test_validar_default(self):
        """Verifica que los valores por defecto pasen validación."""
        operativo = ParametrosOperativo()
        errores = operativo.validar()
        assert len(errores) == 0

    def test_validar_horas_negativas(self):
        """Verifica que se detecte horas_trabajo <= 0."""
        operativo = ParametrosOperativo()
        operativo.horas_trabajo = 0.0
        errores = operativo.validar()
        assert any("horas" in e.lower() for e in errores)

    def test_validar_empleados_negativos(self):
        """Verifica que se detecte cantidad_empleados <= 0."""
        operativo = ParametrosOperativo()
        operativo.cantidad_empleados = -1
        errores = operativo.validar()
        assert any("empleados" in e.lower() for e in errores)

    def test_validar_energia_negativa(self):
        """Verifica que se detecte energia_consumida < 0."""
        operativo = ParametrosOperativo()
        operativo.energia_consumida = -10.0
        errores = operativo.validar()
        assert any("energía" in e.lower() for e in errores)

    def test_validar_coeficiente_perdida_rango(self):
        """Verifica que coeficiente_perdida esté en [0, 1]."""
        operativo = ParametrosOperativo()
        operativo.coeficiente_perdida = 1.5
        errores = operativo.validar()
        assert any("pérdida" in e.lower() for e in errores)

    def test_validar_energia_cero_valido(self):
        """Verifica que energía = 0 sea válido (sin energía consumida)."""
        operativo = ParametrosOperativo()
        operativo.energia_consumida = 0.0
        errores = operativo.validar()
        assert len(errores) == 0

    def test_repr(self):
        """Verifica que __repr__ retorne string válido."""
        operativo = ParametrosOperativo()
        repr_str = repr(operativo)
        assert "ParametrosOperativo" in repr_str
