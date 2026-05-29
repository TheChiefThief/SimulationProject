"""tests/test_validador.py
-------------------------
Pruebas unitarias para validar de forma estricta las funciones de parseo
y control de errores en core/validador.py.
"""

import pytest
from core.validador import Validador


class TestValidador:
    """Suite de pruebas para el validador estricto."""

    # ── Pruebas de validar_entero ───────────────────────────────────────────

    def test_validar_entero_correcto(self):
        assert Validador.validar_entero("10", "campo_test") == 10
        assert Validador.validar_entero(" 0 ", "campo_test") == 0
        assert Validador.validar_entero("-5", "campo_test") == -5

    def test_validar_entero_vacio(self):
        with pytest.raises(ValueError) as exc:
            Validador.validar_entero("  ", "campo_test")
        assert "no puede estar vacío" in str(exc.value)

    def test_validar_entero_invalido(self):
        invalidos = ["10a", "abc", "10.5", "1 0", "1.0", "@12"]
        for val in invalidos:
            with pytest.raises(ValueError) as exc:
                Validador.validar_entero(val, "campo_test")
            assert "entero válido" in str(exc.value)

    def test_validar_entero_limite_minimo(self):
        with pytest.raises(ValueError) as exc:
            Validador.validar_entero("5", "campo_test", min_valor=10)
        assert "no puede ser menor a" in str(exc.value)

    def test_validar_entero_limite_maximo(self):
        with pytest.raises(ValueError) as exc:
            Validador.validar_entero("15", "campo_test", max_valor=10)
        assert "no puede ser mayor a" in str(exc.value)

    # ── Pruebas de validar_float ────────────────────────────────────────────

    def test_validar_float_correcto(self):
        assert Validador.validar_float("10.5", "campo_test") == 10.5
        assert Validador.validar_float(" 0.001 ", "campo_test") == 0.001
        assert Validador.validar_float("-1.23", "campo_test") == -1.23

    def test_validar_float_vacio(self):
        with pytest.raises(ValueError) as exc:
            Validador.validar_float("   ", "campo_test")
        assert "no puede estar vacío" in str(exc.value)

    def test_validar_float_invalido(self):
        invalidos = ["10.5.5", "abc", "1.0a", "1 0.5", "@1.2"]
        for val in invalidos:
            with pytest.raises(ValueError) as exc:
                Validador.validar_float(val, "campo_test")
            assert "decimal válido" in str(exc.value)

    def test_validar_float_nan_inf(self):
        invalidos = ["nan", "inf", "-inf", "infinity", "-infinity", "NaN", "INF"]
        for val in invalidos:
            with pytest.raises(ValueError) as exc:
                Validador.validar_float(val, "campo_test")
            assert "valor no permitido" in str(exc.value) or "decimal válido" in str(exc.value)

    def test_validar_float_limite_minimo(self):
        with pytest.raises(ValueError) as exc:
            Validador.validar_float("4.99", "campo_test", min_valor=5.0)
        assert "no puede ser menor a" in str(exc.value)

    def test_validar_float_limite_maximo(self):
        with pytest.raises(ValueError) as exc:
            Validador.validar_float("5.01", "campo_test", max_valor=5.0)
        assert "no puede ser mayor a" in str(exc.value)

    # ── Pruebas de validar_fraccion ─────────────────────────────────────────

    def test_validar_fraccion_correcta(self):
        assert Validador.validar_fraccion("0.0", "fraccion") == 0.0
        assert Validador.validar_fraccion("0.5", "fraccion") == 0.5
        assert Validador.validar_fraccion("1.0", "fraccion") == 1.0

    def test_validar_fraccion_fuera_rango(self):
        with pytest.raises(ValueError):
            Validador.validar_fraccion("-0.01", "fraccion")
        with pytest.raises(ValueError):
            Validador.validar_fraccion("1.01", "fraccion")

    # ── Pruebas de validar_precio ───────────────────────────────────────────

    def test_validar_precio_correcto(self):
        assert Validador.validar_precio("0.01", "precio") == 0.01
        assert Validador.validar_precio("1500.0", "precio") == 1500.0

    def test_validar_precio_invalido(self):
        with pytest.raises(ValueError):
            Validador.validar_precio("0.0", "precio")
        with pytest.raises(ValueError):
            Validador.validar_precio("-10.0", "precio")

    # ── Pruebas de validar_suma_cercana_uno ─────────────────────────────────

    def test_validar_suma_cercana_uno_correcta(self):
        # La suma es exactamente 1.0
        Validador.validar_suma_cercana_uno([0.5, 0.3, 0.2], ["p1", "p2", "p3"], "dispositivo")
        # La suma es 0.99
        Validador.validar_suma_cercana_uno([0.5, 0.29, 0.2], ["p1", "p2", "p3"], "dispositivo")
        # La suma es 1.01
        Validador.validar_suma_cercana_uno([0.51, 0.3, 0.2], ["p1", "p2", "p3"], "dispositivo")

    def test_validar_suma_cercana_uno_incorrecta(self):
        # Suma 0.98
        with pytest.raises(ValueError) as exc:
            Validador.validar_suma_cercana_uno([0.5, 0.28, 0.2], ["p1", "p2", "p3"], "dispositivo")
        assert "debe ser aproximadamente 100%" in str(exc.value)

        # Suma 1.02
        with pytest.raises(ValueError) as exc:
            Validador.validar_suma_cercana_uno([0.52, 0.3, 0.2], ["p1", "p2", "p3"], "dispositivo")
        assert "debe ser aproximadamente 100%" in str(exc.value)
