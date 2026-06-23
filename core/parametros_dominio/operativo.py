""" Parámetros operativos del sistema """


class ParametrosOperativo:
    """Contenedor independiente para parámetros operativos cargados por el gerente """

    def __init__(self):
        self.horas_trabajo: float = 8.0
        self.cantidad_empleados: int = 5
        self.energia_consumida: float = 100.0     # kWh
        self.coeficiente_perdida: float = 0.05    # 5% de pérdida (fracción 0–1)
        self.tipo_maquinaria: str = "Proceso Manual"

    def validar(self) -> list[str]:
        """Valida que los parámetros operativos sean válidos """
        errores = []

        if self.horas_trabajo <= 0:
            errores.append("Las horas de trabajo deben ser mayores a 0 ")
        if self.cantidad_empleados <= 0:
            errores.append("La cantidad de empleados debe ser mayor a 0 ")
        if self.energia_consumida < 0:
            errores.append("La energía consumida no puede ser negativa ")
        if not (0.0 <= self.coeficiente_perdida <= 1.0):
            errores.append("El coeficiente de pérdida debe estar entre 0 y 1 ")

        return errores

    def __repr__(self) -> str:
        return (
            f"ParametrosOperativo("
            f"horas={self.horas_trabajo}, "
            f"empleados={self.cantidad_empleados}, "
            f"maquinaria={self.tipo_maquinaria})"
        )
