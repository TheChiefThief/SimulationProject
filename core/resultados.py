"""
core/resultados.py
------------------
Clases de datos para almacenar los resultados de la simulación.
"""

class ResultadoCamara:
    """Resultado del procesamiento de una cámara individual."""

    def __init__(self):
        self.recuperable: bool = False
        self.optica_sana: bool = False
        self.placa_sana: bool = False

        # Valores recuperados (ARS)
        self.valor_lentes: float = 0.0
        self.valor_placas: float = 0.0
        self.valor_plastico: float = 0.0
        self.valor_metal: float = 0.0

        # Masa de materiales recuperados (kg)
        self.kg_plastico: float = 0.0
        self.kg_metal: float = 0.0

    @property
    def valor_total(self) -> float:
        return (
            self.valor_lentes
            + self.valor_placas
            + self.valor_plastico
            + self.valor_metal
        )


class ResultadoDVR:
    """Resultado del procesamiento de un DVR individual."""

    def __init__(self):
        self.recuperable: bool = False
        self.hdd_operativo: bool = False
        self.placa_sana: bool = False

        # Valores recuperados (ARS)
        self.valor_hdd: float = 0.0
        self.valor_placas: float = 0.0
        self.valor_metal: float = 0.0

        # Masa de materiales recuperados (kg)
        self.kg_metal: float = 0.0

    @property
    def valor_total(self) -> float:
        return self.valor_hdd + self.valor_placas + self.valor_metal


class ResultadoLote:
    """Resultado agregado de un lote completo de dispositivos."""

    def __init__(self):
        # Cantidades procesadas
        self.n_camaras: int = 0
        self.n_dvrs: int = 0

        # Conteos de estados
        self.camaras_recuperables: int = 0
        self.camaras_desguazadas: int = 0
        self.dvrs_recuperables: int = 0
        self.dvrs_desguazados: int = 0

        # Valores por componente (ARS)
        self.valor_lentes: float = 0.0
        self.valor_placas_camara: float = 0.0
        self.valor_placas_dvr: float = 0.0
        self.valor_hdd: float = 0.0
        self.valor_plastico: float = 0.0
        self.valor_metal: float = 0.0

        # Masa recuperada (kg)
        self.kg_plastico: float = 0.0
        self.kg_metal: float = 0.0

        # Indicadores de eficiencia
        self.coef_productividad: float = 0.0
        self.eficacia: float = 0.0
        self.eficiencia: float = 0.0
        self.rango_mejora: float = 0.0

        # Semilla del GCL utilizada (para referencia y reproducibilidad)
        self.semilla_gcl: int = 0

    @property
    def valor_total_placas(self) -> float:
        return self.valor_placas_camara + self.valor_placas_dvr

    @property
    def valor_total(self) -> float:
        return (
            self.valor_lentes
            + self.valor_placas_camara
            + self.valor_placas_dvr
            + self.valor_hdd
            + self.valor_plastico
            + self.valor_metal
        )

    @property
    def n_total(self) -> int:
        return self.n_camaras + self.n_dvrs
