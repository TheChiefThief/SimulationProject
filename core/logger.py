"""
core/logger.py
--------------
Módulo para registrar de manera centralizada y estructurada todos los errores y excepciones
que ocurran durante la ejecución del simulador.
"""

import logging
import traceback

LOG_FILE = "errores_simulador.log"

# Obtener o crear el logger
logger = logging.getLogger("SimuladorRAEE")
logger.setLevel(logging.ERROR)

# Configurar el manejador de archivo de forma segura
if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def registrar_error(mensaje: str, excepcion: Exception = None):
    """
    Registra un mensaje de error y opcionalmente incluye el traceback
    detallado de la excepción para facilitar la depuración.
    """
    if excepcion:
        tb_str = "".join(
            traceback.format_exception(
                type(excepcion), excepcion, excepcion.__traceback__
            )
        )
        logger.error(f"{mensaje} | Excepción: {type(excepcion).__name__}: {excepcion}\n{tb_str}")
    else:
        logger.error(mensaje)
