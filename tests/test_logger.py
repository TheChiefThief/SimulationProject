"""
tests/test_logger.py
--------------------
Pruebas unitarias para el módulo centralizado de logging.
"""

import os
import logging
import pytest
from core.logger import registrar_error, logger


def test_logger_integration(tmp_path):
    # Definir archivo de log de prueba
    log_test_file = str(tmp_path / "test_errores.log")

    # Guardar handlers originales
    old_handlers = list(logger.handlers)
    for h in old_handlers:
        logger.removeHandler(h)

    # Configurar handler de prueba temporal
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(log_test_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    try:
        # 1. Registrar error sin excepción
        registrar_error("Mensaje de prueba sin excepcion")

        # 2. Registrar error con excepción
        try:
            raise ValueError("Excepcion de prueba de valor")
        except ValueError as e:
            registrar_error("Ocurrio un ValueError de prueba", e)

    finally:
        # Limpiar y cerrar handler de prueba
        file_handler.close()
        logger.removeHandler(file_handler)

        # Restaurar handlers originales
        for h in old_handlers:
            logger.addHandler(h)

    # 3. Validar contenido escrito en el log de prueba
    assert os.path.exists(log_test_file)
    with open(log_test_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Mensaje de prueba sin excepcion" in content
    assert "Ocurrio un ValueError de prueba" in content
    assert "Excepcion de prueba de valor" in content
    # Asegurar que se guarde el traceback (nombre de la función test en el stack trace)
    assert "test_logger_integration" in content
