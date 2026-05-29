"""
core/parametros.py
------------------
Define la clase ParametrosSistema, que agrupa parámetros del sistema
en dominios especializados para mejor modularidad.

El flag `parametros_cargados` controla si el sistema está habilitado
para ejecutar una simulación.
"""

from core.parametros_dominio import (
    PreciosParametros,
    ComposicionParametros,
    TasasRecuperacionParametros,
    ParametrosOperativo,
)


class ParametrosSistema:
    """
    Agregador de parámetros del simulador usando composición de dominios.

    Componentes:
        precios      : PreciosParametros - todos los precios en ARS
        composicion  : ComposicionParametros - fracciones de materiales
        tasas        : TasasRecuperacionParametros - tasas de recuperación
        operativo    : ParametrosOperativo - parámetros operativos
        parametros_cargados : Bool - indica si los parámetros están listos

    Cada dominio es independiente y testeable por separado.
    """

    def __init__(self):
        self.precios = PreciosParametros()
        self.composicion = ComposicionParametros()
        self.tasas = TasasRecuperacionParametros()
        self.operativo = ParametrosOperativo()
        self.parametros_cargados: bool = True  # Por defecto habilitado con valores base

    def validar(self) -> list[str]:
        """
        Valida todos los dominios de parámetros.

        Returns:
            Lista de mensajes de error. Lista vacía si todo es válido.
        """
        errores = []
        errores.extend(self.precios.validar())
        errores.extend(self.composicion.validar())
        errores.extend(self.tasas.validar())
        errores.extend(self.operativo.validar())
        return errores

    def __repr__(self) -> str:
        estado = "CARGADOS" if self.parametros_cargados else "NO CARGADOS"
        return f"ParametrosSistema(estado={estado})"
