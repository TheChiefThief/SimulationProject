"""
core/resultados.py
------------------
Clases de datos para almacenar los resultados de la simulación
basados en el diagrama general de procesos.
"""

class ResultadoLote:
    """Resultado agregado de un lote completo de dispositivos, siguiendo el diagrama de flujo general."""

    def __init__(self):
        # Cantidad total
        self.n_total: int = 0
        
        # Conteo de reventa
        self.equipos_reventa: int = 0
        self.camaras_reventa: int = 0
        self.dvrs_reventa: int = 0
        
        # Conteo de desguace
        self.camaras_desguazadas: int = 0
        self.dvrs_desguazados: int = 0

        # Contadores por estación (C1 a C6)
        self.c1: int = 0
        self.c2: int = 0
        self.c3: int = 0
        self.c4: int = 0
        self.c5: int = 0
        self.c6: int = 0

        # Tiempos acumulados por estación (TDR, TDO, TCO, TP, TDD, THD)
        self.tdr: float = 0.0
        self.tdo: float = 0.0
        self.tco: float = 0.0
        self.tp: float = 0.0
        self.tdd: float = 0.0
        self.thd: float = 0.0

        # Porcentajes de Eficiencia/Ocupación (PE1 a PE6)
        self.pe1: float = 0.0
        self.pe2: float = 0.0
        self.pe3: float = 0.0
        self.pe4: float = 0.0
        self.pe5: float = 0.0
        self.pe6: float = 0.0
        
        self.cuellos_botella: list[str] = []

        # Masas de materiales (kg)
        self.peso_plastico: float = 0.0
        self.peso_metal: float = 0.0
        self.peso_cobre: float = 0.0
        self.peso_aluminio: float = 0.0
        self.peso_oro: float = 0.0

        # Valores monetarios (ARS)
        self.valor_cobre: float = 0.0
        self.valor_aluminio: float = 0.0
        self.valor_oro: float = 0.0
        self.valor_plastico: float = 0.0
        
        self.pmt: float = 0.0  # Plata Materiales Total
        self.pt: float = 0.0   # Plata Plástico Total

        # Resultados de la simulación de demanda (Poisson)
        self.horas_demanda: int = 0  # h
        self.clientes_totales: int = 0  # cp

        # Acumuladores para Coeficientes de Recuperación
        self.mt: float = 0.0
        self.placas_f: int = 0
        self.placas_t: int = 0
        self.hdd_f: int = 0
        self.hdd_t: int = 0
        self.peso_vidrio: float = 0.0

        # Semilla del GCL
        self.semilla_gcl: int = 0

    @property
    def valor_total(self) -> float:
        """Valor total generado (Materiales + Plástico)."""
        return self.pmt + self.pt

    @property
    def cr_plastico(self) -> float:
        return (self.peso_plastico / self.mt) * 100 if self.mt > 0 else 0.0

    @property
    def cr_metales(self) -> float:
        return (self.peso_metal / self.mt) * 100 if self.mt > 0 else 0.0

    @property
    def cr_placas(self) -> float:
        return (self.placas_f / self.placas_t) * 100 if self.placas_t > 0 else 0.0

    @property
    def cr_hdd(self) -> float:
        return (self.hdd_f / self.hdd_t) * 100 if self.hdd_t > 0 else 0.0

    @property
    def cr_opt(self) -> float:
        return (self.peso_vidrio / self.mt) * 100 if self.mt > 0 else 0.0
