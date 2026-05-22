"""tests/conftest.py - Fixtures compartidas para todos los tests."""

import pytest

from core.parametros import ParametrosSistema
from core.gcl import GeneradorCongruencialLineal


@pytest.fixture
def parametros_default():
    """Crea una instancia de ParametrosSistema con valores por defecto."""
    params = ParametrosSistema()
    params.parametros_cargados = True  # Ya cargados para tests
    return params


@pytest.fixture
def gcl_seeded():
    """Crea un GCL con semilla fija para reproducibilidad."""
    return GeneradorCongruencialLineal(semilla=12345)


@pytest.fixture
def gcl_factory():
    """Factory para crear GCLs con semilla fija."""
    def _factory(semilla=12345):
        return GeneradorCongruencialLineal(semilla=semilla)
    return _factory
