"""
core/resultados.py
------------------
Clases de datos para almacenar los resultados de la simulación.
Alineado al diagrama de flujo general con entrada por peso B (kg).
"""


class ResultadoLote:
    """
    Resultado agregado de un lote completo, siguiendo el diccionario de datos
    y el diagrama de flujo general.

    Entrada:
        b_kg_input      : B — peso total ingresado (kg)
        peso_acumulado  : peso real procesado (puede ser ≥ B por el último dispositivo)

    Conteos de dispositivos:
        n_total         : total de dispositivos procesados (desguace + reventa)
        cant_cam        : CantCam — cámaras desguazadas
        cant_dvr        : CantDvr — DVRs desguazados
        cam_rec         : CAMREC — cámaras derivadas a reventa
        dvr_rec         : DvrREC — DVRs derivados a reventa
        equipos_reventa : total de equipos a reventa

    Contadores por estación (C1–C6):
        c1 … c6

    Tiempos acumulados por estación:
        tdr (D1), tdo (D2), tco (D3), tp (D4), tdd (D5), thd (D6)

    Ocupación y Productividad por estación:
        ocupacion_1 … ocupacion_6
        productividad_1 … productividad_6
        cuellos_botella : lista de estaciones con ocupación > 85%

    Masas de materiales recuperados (kg):
        mt, peso_plastico, peso_metal, peso_cobre, peso_aluminio, peso_oro, peso_vidrio

    Valores monetarios (ARS):
        valor_cobre, valor_aluminio, valor_oro, valor_plastico
        pmt : PMT — precio material total (cobre + aluminio + oro)
        pt  : PT  — precio plástico total

    Coeficientes de recuperación (calculados como property):
        cr_plastico, cr_metales, cr_placas, cr_hdd, cr_opt

    Placas y HDDs:
        placas_f, placas_t, hdd_f, hdd_t

    Demanda simulada (Poisson):
        horas_demanda, clientes_totales

    Reproducibilidad:
        semilla_gcl
    """

    def __init__(self):
        # ── Entrada ────────────────────────────────────────────────────
        self.b_kg_input: float = 0.0          # B ingresado por el usuario
        self.peso_acumulado: float = 0.0       # Peso real procesado

        # ── Conteos ────────────────────────────────────────────────────
        self.n_total: int = 0                  # Total dispositivos (desguace + reventa)
        self.cant_cam: int = 0                 # CantCam — cámaras desguazadas
        self.cant_dvr: int = 0                 # CantDvr — DVRs desguazados
        self.cam_rec: int = 0                  # CAMREC — cámaras a reventa
        self.dvr_rec: int = 0                  # DvrREC — DVRs a reventa
        self.equipos_reventa: int = 0          # Total reventa

        # Alias de compatibilidad con código existente (gui/ventana_resultados)
        self.camaras_desguazadas: int = 0
        self.dvrs_desguazados: int = 0
        self.camaras_reventa: int = 0
        self.dvrs_reventa: int = 0

        # ── Contadores de estación ─────────────────────────────────────
        self.c1: int = 0   # Revisión general
        self.c2: int = 0   # Desarme cámara / óptica
        self.c3: int = 0   # Recuperación componente óptico
        self.c4: int = 0   # Recuperación placas
        self.c5: int = 0   # Desarme DVR
        self.c6: int = 0   # Recuperación material HDD

        # ── Tiempos acumulados por estación (minutos) ──────────────────
        self.tdr: float = 0.0   # D1
        self.tdo: float = 0.0   # D2
        self.tco: float = 0.0   # D3
        self.tp: float = 0.0    # D4
        self.tdd: float = 0.0   # D5
        self.thd: float = 0.0   # D6

        # ── Ocupación y Productividad por estación ─────────────────────
        self.ocupacion_1: float = 0.0
        self.ocupacion_2: float = 0.0
        self.ocupacion_3: float = 0.0
        self.ocupacion_4: float = 0.0
        self.ocupacion_5: float = 0.0
        self.ocupacion_6: float = 0.0

        self.productividad_1: float = 0.0
        self.productividad_2: float = 0.0
        self.productividad_3: float = 0.0
        self.productividad_4: float = 0.0
        self.productividad_5: float = 0.0
        self.productividad_6: float = 0.0
        self.cuellos_botella: list[str] = []

        # ── Masas de materiales (kg) ───────────────────────────────────
        self.mt: float = 0.0            # Material Total ingresado
        self.peso_plastico: float = 0.0
        self.peso_metal: float = 0.0
        self.peso_cobre: float = 0.0
        self.peso_aluminio: float = 0.0
        self.peso_oro: float = 0.0
        self.peso_vidrio: float = 0.0

        # ── Valores monetarios (ARS) ───────────────────────────────────
        self.valor_cobre: float = 0.0
        self.valor_aluminio: float = 0.0
        self.valor_oro: float = 0.0
        self.valor_plastico: float = 0.0
        self.pmt: float = 0.0    # PMT: plata materiales total (metales)
        self.pt: float = 0.0     # PT: plata plástico total

        # ── Placas y HDDs ─────────────────────────────────────────────
        self.placas_f: int = 0   # PlacasF
        self.placas_t: int = 0   # PlacasT
        self.hdd_f: int = 0      # HDDF
        self.hdd_t: int = 0      # HDDT

        # ── Demanda simulada ───────────────────────────────────────────
        self.horas_demanda: int = 0
        self.clientes_totales: int = 0

        # ── Reproducibilidad ──────────────────────────────────────────
        self.semilla_gcl: int = 0

    # ── Propiedades calculadas ─────────────────────────────────────────

    @property
    def valor_total(self) -> float:
        """Valor total generado (PMT + PT)."""
        return self.pmt + self.pt

    @property
    def cr_plastico(self) -> float:
        """CrPlástico — coeficiente de recuperación de plástico (%)."""
        return (self.peso_plastico / self.mt) * 100 if self.mt > 0 else 0.0

    @property
    def cr_metales(self) -> float:
        """CrMetales — coeficiente de recuperación de metales (%)."""
        return (self.peso_metal / self.mt) * 100 if self.mt > 0 else 0.0

    @property
    def cr_placas(self) -> float:
        """CrPlacas — coeficiente de recuperación de placas funcionales (%)."""
        return (self.placas_f / self.placas_t) * 100 if self.placas_t > 0 else 0.0

    @property
    def cr_hdd(self) -> float:
        """CrHDD — coeficiente de recuperación de HDDs funcionales (%)."""
        return (self.hdd_f / self.hdd_t) * 100 if self.hdd_t > 0 else 0.0

    @property
    def cr_opt(self) -> float:
        """CrÓptica — coeficiente de recuperación óptica (%)."""
        return (self.peso_vidrio / self.mt) * 100 if self.mt > 0 else 0.0
