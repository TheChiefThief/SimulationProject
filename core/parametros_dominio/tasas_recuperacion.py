""" Tasas de recuperación de componentes """


class TasasRecuperacionParametros:
    """Contenedor independiente para tasas de recuperación de componentes """

    def __init__(self):
        # Tasas de recuperación (fracción 0–1)
        self.tasa_placas_sanas: float = 0.75
        self.tasa_opticas_sanas: float = 0.70
        self.tasa_discos_sanos: float = 0.65

    def validar(self) -> list[str]:
        """Valida que todas las tasas estén en [0, 1]"""
        errores = []

        tasas = {
            "Tasa Placas Sanas": self.tasa_placas_sanas,
            "Tasa Ópticas Sanas": self.tasa_opticas_sanas,
            "Tasa Discos Sanos": self.tasa_discos_sanos,
        }

        for nombre, valor in tasas.items():
            if not (0.0 <= valor <= 1.0):
                errores.append(f"{nombre} debe estar entre 0 y 1.")

        return errores

    def __repr__(self) -> str:
        return (
            f"TasasRecuperacionParametros("
            f"placas={self.tasa_placas_sanas}, "
            f"opticas={self.tasa_opticas_sanas}, "
            f"discos={self.tasa_discos_sanos})"
        )
