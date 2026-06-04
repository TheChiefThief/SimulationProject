""" Parámetros de precios de materiales """


class PreciosParametros:
    """Contenedor independiente para todos los precios del sistema (ARS) """

    def __init__(self):
        self.precio_oro: float = 210_000.0        # ARS/kg
        self.precio_vidrio: float = 15_000.0      # ARS/kg
        self.precio_lentes: float = 60_000.0      # ARS/unidad
        self.precio_cobre: float = 8_500.0        # ARS/kg
        self.precio_aluminio: float = 1_500.0     # ARS/kg
        self.precio_plastico: float = 60.0        # ARS/kg
        self.precio_almacenamiento_min: float = 50.0   # ARS/GB
        self.precio_almacenamiento_max: float = 100.0  # ARS/GB

    def validar(self) -> list[str]:
        """Valida que todos los precios sean no negativos y coherentes """
        errores = []

        precios = {
            "Precio Oro": self.precio_oro,
            "Precio Vidrio": self.precio_vidrio,
            "Precio Lentes": self.precio_lentes,
            "Precio Cobre": self.precio_cobre,
            "Precio Aluminio": self.precio_aluminio,
            "Precio Plástico": self.precio_plastico,
            "Precio Almacenamiento Mín": self.precio_almacenamiento_min,
            "Precio Almacenamiento Máx": self.precio_almacenamiento_max,
        }

        for nombre, valor in precios.items():
            if valor < 0:
                errores.append(f"{nombre} no puede ser negativo ")

        if self.precio_almacenamiento_min > self.precio_almacenamiento_max:
            errores.append(
                "El precio mínimo de almacenamiento no puede superar al máximo "
            )

        return errores

    def __repr__(self) -> str:
        return (
            f"PreciosParametros("
            f"oro={self.precio_oro}, "
            f"vidrio={self.precio_vidrio}, "
            f"cobre={self.precio_cobre})"
        )
