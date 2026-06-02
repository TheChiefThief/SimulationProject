"""core/parametros_dominio/composicion.py - Parámetros de composición de materiales."""


class ComposicionParametros:
    """Contenedor independiente para composición de materiales por dispositivo."""

    def __init__(self):
        # Cámaras: fracciones del peso total
        self.camara_fraccion_plastico: float = 0.60
        self.camara_fraccion_placas: float = 0.20
        self.camara_fraccion_metal: float = 0.10
        self.camara_fraccion_opticos: float = 0.10

        # DVRs: fracciones del peso total
        self.dvr_fraccion_hdd: float = 0.45
        self.dvr_fraccion_metal: float = 0.30
        self.dvr_fraccion_placas: float = 0.25

        # Peso promedio por dispositivo (kg) — referencia del documento
        self.peso_camara: float = 1.14
        self.peso_dvr: float = 1.12

        # Rangos de peso para muestreo por distribución Uniforme
        # Cámara: centrado en ~1.14 kg según datos de diseño
        self.peso_camara_min: float = 0.2
        self.peso_camara_max: float = 1.5
        # DVR: centrado en ~1.12 kg según datos de diseño
        self.peso_dvr_min: float = 0.5
        self.peso_dvr_max: float = 1.5

        # Rendimientos de procesamiento
        self.rendimiento_plastico: float = 0.80
        self.rendimiento_metal: float = 0.85

    def validar(self) -> list[str]:
        """Valida que todas las fracciones estén en [0, 1] y pesos sean positivos."""
        errores = []

        # Validar fracciones de cámaras
        fracciones_camara = {
            "Fracción Plástico (Cámara)": self.camara_fraccion_plastico,
            "Fracción Placas (Cámara)": self.camara_fraccion_placas,
            "Fracción Metal (Cámara)": self.camara_fraccion_metal,
            "Fracción Ópticos (Cámara)": self.camara_fraccion_opticos,
        }

        # Validar fracciones de DVRs
        fracciones_dvr = {
            "Fracción HDD (DVR)": self.dvr_fraccion_hdd,
            "Fracción Metal (DVR)": self.dvr_fraccion_metal,
            "Fracción Placas (DVR)": self.dvr_fraccion_placas,
        }

        for nombre, valor in {**fracciones_camara, **fracciones_dvr}.items():
            if not (0.0 <= valor <= 1.0):
                errores.append(f"{nombre} debe estar entre 0 y 1.")

        # Suma de fracciones por dispositivo
        suma_camara = (
            self.camara_fraccion_plastico
            + self.camara_fraccion_placas
            + self.camara_fraccion_metal
            + self.camara_fraccion_opticos
        )
        if not (0.99 <= suma_camara <= 1.01):  # Tolerancia numérica
            errores.append(
                f"La suma de fracciones de cámara debe ser 1, obtuvo {suma_camara}."
            )

        suma_dvr = (
            self.dvr_fraccion_hdd + self.dvr_fraccion_metal + self.dvr_fraccion_placas
        )
        if not (0.99 <= suma_dvr <= 1.01):
            errores.append(f"La suma de fracciones de DVR debe ser 1, obtuvo {suma_dvr}.")

        # Pesos positivos
        if self.peso_camara <= 0:
            errores.append("Peso de cámara debe ser positivo.")
        if self.peso_dvr <= 0:
            errores.append("Peso de DVR debe ser positivo.")

        # Rendimientos en [0, 1]
        if not (0.0 <= self.rendimiento_plastico <= 1.0):
            errores.append("Rendimiento de plástico debe estar entre 0 y 1.")
        if not (0.0 <= self.rendimiento_metal <= 1.0):
            errores.append("Rendimiento de metal debe estar entre 0 y 1.")

        # Validar consistencia de rangos (min vs max)
        if self.peso_camara_min >= self.peso_camara_max:
            errores.append("El peso máximo de la cámara debe ser estrictamente mayor a su peso mínimo.")
        if self.peso_dvr_min >= self.peso_dvr_max:
            errores.append("El peso máximo del DVR debe ser estrictamente mayor a su peso mínimo.")

        return errores

    def __repr__(self) -> str:
        return (
            f"ComposicionParametros("
            f"camara_plastico={self.camara_fraccion_plastico}, "
            f"dvr_hdd={self.dvr_fraccion_hdd})"
        )
