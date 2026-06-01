"""
core/simulacion_service.py
---------------------------
Servicio que orquesta la simulación completa de reciclaje RAEE.

Entrada: B (kg) — peso total del lote de basura electrónica.
El loop procesa dispositivos individuales (con peso P muestreado de
una distribución Uniforme según tipo) acumulando hasta alcanzar B.

Probabilidades reales (datos de investigación):
  - P(reventa)        = 0.25
  - P(es DVR)         = 0.113
  - P(HDD sano)       = 0.55
  - P(óptica sana)    = 0.70
  - P(placa sana cám) = 0.22
  - P(placa sana DVR) = 0.27

Tiempos reales por estación (distribución Exponencial, en minutos):
  - D1 Revisión general        : media = 3  min
  - D2 Desarme cámara/óptica   : media = 2  min
  - D3 Recuperación óptico     : media = 27 min
  - D4 Recuperación placas     : media = 90 min
  - D5 Desarme DVR             : media = 10 min
  - D6 Recuperación HDD        : media = 3  min

Composición de materiales al desguazar (por peso del dispositivo):
  - Cobre    : 20%
  - Aluminio :  3%
  - Oro      :  1%
  - Plástico : 60%
"""

from typing import Callable

from core.gcl import GeneradorCongruencialLineal
from core.distribuciones import Distribuciones
from core.parametros import ParametrosSistema
from core.resultados import ResultadoLote


# ── Tiempos reales por estación (media de distribución Exponencial, min) ──
_D1_REVISION = 3.0
_D2_OPTICA = 2.0
_D3_OPT_MATERIAL = 27.0
_D4_PLACAS = 90.0
_D5_DVR = 10.0
_D6_HDD = 3.0

# ── Probabilidades reales (datos de investigación) ────────────────────────
_P_REVENTA = 0.25
_P_ES_DVR = 0.113
_P_HDD_SANO = 0.55
_P_OPTICA_SANA = 0.70
_P_PLACA_SANA_CAM = 0.22
_P_PLACA_SANA_DVR = 0.27

# ── Umbral de cuello de botella ───────────────────────────────────────────
_UMBRAL_BOTELLA = 0.85


class SimulacionService:
    """
    Servicio de simulación que orquesta todos los componentes.
    Implementa el flujo del diagrama con entrada por peso B (kg).
    """

    def __init__(
        self,
        parametros: ParametrosSistema,
        gcl_factory: Callable[[], GeneradorCongruencialLineal] = None,
    ):
        self.parametros = parametros
        self.gcl_factory = gcl_factory or GeneradorCongruencialLineal

    # ------------------------------------------------------------------
    # Métodos internos de cálculo
    # ------------------------------------------------------------------

    def _procesar_material(self, resultado: ResultadoLote, p: float) -> None:
        """
        Aplica las fórmulas del subdiagrama de Recuperación de Material.
        Composición (datos reales): Cobre 20%, Aluminio 3%, Oro 1%, Plástico 60%.

        Args:
            resultado : ResultadoLote acumulador.
            p         : Peso del dispositivo (kg).
        """
        precios = self.parametros.precios

        cobre = p * 0.20
        aluminio = p * 0.03
        oro = p * 0.01
        plastico = p * 0.60

        resultado.peso_cobre += cobre
        resultado.peso_aluminio += aluminio
        resultado.peso_oro += oro
        resultado.peso_plastico += plastico
        resultado.peso_metal += (cobre + aluminio + oro)

        vc = cobre * precios.precio_cobre
        va = aluminio * precios.precio_aluminio
        vo = oro * precios.precio_oro
        vp = plastico * precios.precio_plastico

        resultado.valor_cobre += vc
        resultado.valor_aluminio += va
        resultado.valor_oro += vo
        resultado.valor_plastico += vp

        resultado.pmt += (vc + va + vo)
        resultado.pt += vp

    def _muestrear_peso_camara(self, dist: Distribuciones) -> float:
        """P ~ Uniforme(peso_camara_min, peso_camara_max)."""
        c = self.parametros.composicion
        return dist.siguiente_rango(c.peso_camara_min, c.peso_camara_max)

    def _muestrear_peso_dvr(self, dist: Distribuciones) -> float:
        """P ~ Uniforme(peso_dvr_min, peso_dvr_max)."""
        c = self.parametros.composicion
        return dist.siguiente_rango(c.peso_dvr_min, c.peso_dvr_max)

    # ------------------------------------------------------------------
    # Simulación principal
    # ------------------------------------------------------------------

    def simular_lote(self, b_kg: float) -> ResultadoLote:
        """
        Ejecuta la simulación de un lote de basura electrónica.

        Flujo (diagrama general):
          MIENTRAS peso_acumulado < B:
            D1 → Revisión: ¿Reventa?
              SÍ → CAMREC / DvrREC, acumular P, continuar
              NO → ¿Es DVR?
                SÍ → Procesar DVR (D5, HDD, Placas, Material)
                NO → Procesar Cámara (D2, Óptica, Placas, Material)

        Args:
            b_kg: B — peso total del lote en kg.

        Returns:
            ResultadoLote con todos los resultados agregados.

        Raises:
            RuntimeError: Si los parámetros no fueron cargados.
        """
        if not self.parametros.parametros_cargados:
            raise RuntimeError(
                "Los parámetros operativos no han sido cargados. "
                "Por favor, complete la Vista del Gerente antes de ejecutar."
            )

        gcl = self.gcl_factory()
        dist = Distribuciones(gcl)
        resultado = ResultadoLote()
        resultado.semilla_gcl = gcl.semilla
        resultado.b_kg_input = b_kg

        peso_acumulado = 0.0

        # ── Loop principal: procesar dispositivos hasta alcanzar B ─────
        while peso_acumulado < b_kg:

            # ── Estación 1: Revisión General (D1 ~ Exp(3 min)) ─────────
            d1 = dist.siguiente_exponencial(_D1_REVISION)
            resultado.c1 += 1
            resultado.tdr += d1

            # ── Decisión: ¿Reventa? (P=0.25) ───────────────────────────
            if gcl.siguiente_u() < _P_REVENTA:
                resultado.equipos_reventa += 1

                if gcl.siguiente_u() < _P_ES_DVR:
                    resultado.dvr_rec += 1
                    resultado.dvrs_reventa += 1
                    p = self._muestrear_peso_dvr(dist)
                else:
                    resultado.cam_rec += 1
                    resultado.camaras_reventa += 1
                    p = self._muestrear_peso_camara(dist)

                peso_acumulado += p
                continue

            # ── Decisión: ¿Es DVR? (P=0.113) ───────────────────────────
            if gcl.siguiente_u() < _P_ES_DVR:
                # ── Procesamiento DVR ───────────────────────────────────
                p = self._muestrear_peso_dvr(dist)
                peso_acumulado += p
                resultado.cant_dvr += 1
                resultado.camaras_desguazadas += 0  # alias no aplica
                resultado.dvrs_desguazados += 1
                resultado.mt += p

                # D5: Desarme DVR General (Exp(10 min))
                d5 = dist.siguiente_exponencial(_D5_DVR)
                resultado.c5 += 1
                resultado.tdd += d5

                # HDD: ¿Sano? (P=0.55)
                resultado.hdd_t += 1
                if gcl.siguiente_u() < _P_HDD_SANO:
                    resultado.hdd_f += 1
                    # Capacidad C ~ Uniforme(250, 2000) GB
                    _capacidad_gb = dist.siguiente_entero(250, 2000)
                else:
                    # D6: Recuperación material HDD (Exp(3 min))
                    d6 = dist.siguiente_exponencial(_D6_HDD)
                    resultado.c6 += 1
                    resultado.thd += d6

                # Placas DVR: ¿Sanas? (P=0.27)
                resultado.placas_t += 1
                if gcl.siguiente_u() < _P_PLACA_SANA_DVR:
                    resultado.placas_f += 1
                else:
                    # D4: Recuperación placas (Exp(90 min))
                    d4 = dist.siguiente_exponencial(_D4_PLACAS)
                    resultado.c4 += 1
                    resultado.tp += d4

                self._procesar_material(resultado, p)

            else:
                # ── Procesamiento Cámara ────────────────────────────────
                p = self._muestrear_peso_camara(dist)
                peso_acumulado += p
                resultado.cant_cam += 1
                resultado.camaras_desguazadas += 1
                resultado.mt += p

                # D2: Desarme Cámara / Óptica (Exp(2 min))
                d2 = dist.siguiente_exponencial(_D2_OPTICA)
                resultado.c2 += 1
                resultado.tdo += d2

                # Óptica: ¿Sana? (P=0.70)
                if gcl.siguiente_u() < _P_OPTICA_SANA:
                    resultado.peso_vidrio += (p * 0.30)
                else:
                    # D3: Recuperación componente óptico (Exp(27 min))
                    d3 = dist.siguiente_exponencial(_D3_OPT_MATERIAL)
                    resultado.c3 += 1
                    resultado.tco += d3

                # Placas Cámara: ¿Sanas? (P=0.22)
                resultado.placas_t += 1
                if gcl.siguiente_u() < _P_PLACA_SANA_CAM:
                    resultado.placas_f += 1
                else:
                    # D4: Recuperación placas (Exp(90 min))
                    d4 = dist.siguiente_exponencial(_D4_PLACAS)
                    resultado.c4 += 1
                    resultado.tp += d4

                self._procesar_material(resultado, p)

        # ── Fin del loop: registrar totales ───────────────────────────
        resultado.peso_acumulado = peso_acumulado
        resultado.n_total = (
            resultado.cant_cam + resultado.cant_dvr + resultado.equipos_reventa
        )

        # ── Cálculo de Ocupación y Productividad de Estaciones ──────────────
        jornada_minutos = self.parametros.operativo.horas_trabajo * 60.0

        # Ocupación: (TiempoAcumulado / JornadaEnMinutos) * 100
        resultado.ocupacion_1 = (resultado.tdr / jornada_minutos) * 100 if jornada_minutos > 0 else 0.0
        resultado.ocupacion_2 = (resultado.tdo / jornada_minutos) * 100 if jornada_minutos > 0 else 0.0
        resultado.ocupacion_3 = (resultado.tco / jornada_minutos) * 100 if jornada_minutos > 0 else 0.0
        resultado.ocupacion_4 = (resultado.tp / jornada_minutos) * 100 if jornada_minutos > 0 else 0.0
        resultado.ocupacion_5 = (resultado.tdd / jornada_minutos) * 100 if jornada_minutos > 0 else 0.0
        resultado.ocupacion_6 = (resultado.thd / jornada_minutos) * 100 if jornada_minutos > 0 else 0.0

        # Productividad: (Cantidad * DemoraExponencial) / TiempoAcumulado
        resultado.productividad_1 = (resultado.c1 * _D1_REVISION) / resultado.tdr if resultado.tdr > 0 else 0.0
        resultado.productividad_2 = (resultado.c2 * _D2_OPTICA) / resultado.tdo if resultado.tdo > 0 else 0.0
        resultado.productividad_3 = (resultado.c3 * _D3_OPT_MATERIAL) / resultado.tco if resultado.tco > 0 else 0.0
        resultado.productividad_4 = (resultado.c4 * _D4_PLACAS) / resultado.tp if resultado.tp > 0 else 0.0
        resultado.productividad_5 = (resultado.c5 * _D5_DVR) / resultado.tdd if resultado.tdd > 0 else 0.0
        resultado.productividad_6 = (resultado.c6 * _D6_HDD) / resultado.thd if resultado.thd > 0 else 0.0

        estaciones = [
            ("Estación 1 — Revisión General",      resultado.ocupacion_1),
            ("Estación 2 — Cámara/Óptica",         resultado.ocupacion_2),
            ("Estación 3 — Recuperación Óptica",   resultado.ocupacion_3),
            ("Estación 4 — Recuperación Placas",   resultado.ocupacion_4),
            ("Estación 5 — Desarme DVR",            resultado.ocupacion_5),
            ("Estación 6 — Recuperación HDD",      resultado.ocupacion_6),
        ]
        for nombre, ocup in estaciones:
            if ocup > (_UMBRAL_BOTELLA * 100):
                resultado.cuellos_botella.append(nombre)

        # ── Simulación de Demanda (Poisson λ=0.3 clientes/hora) ───────
        h = 0
        cp = 0
        limite_seg = resultado.n_total * 100 + 1000
        while cp < resultado.n_total and h < limite_seg:
            cp += dist.siguiente_poisson(0.3)
            h += 1
        resultado.horas_demanda = h
        resultado.clientes_totales = cp

        return resultado
