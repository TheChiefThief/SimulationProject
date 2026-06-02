"""core/simuladores/simulador_dvr.py - Simulador para dispositivos tipo DVR."""

from core.gcl import GeneradorCongruencialLineal
from core.parametros import ParametrosSistema
from core.resultados import ResultadoDVR
from core.distribuciones import Distribuciones


class SimuladorDVR:
    """
    Simulador independiente para procesamiento de DVRs.

    Encapsula la lógica de árbol de decisiones para cada DVR:
    - Estado general (recuperable/desguace)
    - HDD (operativo/inoperativo)
    - Placas (funcionales/parcial)

    Cada instancia es independiente y puede ser testeada en aislamiento.
    """

    def __init__(self, parametros: ParametrosSistema):
        """
        Inicializa el simulador con parámetros del sistema.

        Args:
            parametros: ParametrosSistema con todas las configuraciones.
        """
        self.parametros = parametros

    def simular(self, gcl: GeneradorCongruencialLineal) -> ResultadoDVR:
        """
        Simula el procesamiento de un DVR individual.

        Árbol de decisiones:
          1. Estado general (Bernoulli 0.68 aprox.)
          2. HDD (Bernoulli)
          3. Placas (Bernoulli)
          4. Materiales base siempre se recuperan

        Args:
            gcl: Generador congruencial lineal para aleatorización.

        Returns:
            ResultadoDVR con valores calculados.
        """
        r = ResultadoDVR()
        params = self.parametros
        coef = 1.0 - params.operativo.coeficiente_perdida
        dist = Distribuciones(gcl)

        kg_total = params.composicion.peso_dvr
        kg_hdd = kg_total * params.composicion.dvr_fraccion_hdd
        kg_metal = kg_total * params.composicion.dvr_fraccion_metal
        kg_placas_peso = kg_total * params.composicion.dvr_fraccion_placas

        # Decisión 1: Estado general
        r.recuperable = dist.siguiente_bernoulli(0.68)

        if not r.recuperable:
            kg_metal_real = kg_metal * params.composicion.rendimiento_metal * coef
            r.valor_metal = kg_metal_real * params.precios.precio_aluminio
            r.kg_metal = kg_metal_real
            return r

        # Decisión 2: HDD
        r.hdd_operativo = dist.siguiente_bernoulli(params.tasas.tasa_discos_sanos)

        if r.hdd_operativo:
            capacidad_gb = dist.siguiente_entero(250, 2000)
            precio_gb = dist.siguiente_rango(
                params.precios.precio_almacenamiento_min,
                params.precios.precio_almacenamiento_max,
            )
            r.valor_hdd = capacidad_gb * precio_gb * coef
        else:
            fraccion_mat = dist.siguiente_normal(0.53, 0.08)
            kg_mat_hdd = kg_hdd * fraccion_mat * coef
            r.valor_hdd = kg_mat_hdd * params.precios.precio_aluminio

        # Decisión 3: Placas del DVR
        r.placa_sana = dist.siguiente_bernoulli(params.tasas.tasa_placas_sanas)

        if r.placa_sana:
            precio_placa = dist.siguiente_rango(
                kg_placas_peso * params.precios.precio_cobre * 0.8,
                kg_placas_peso * params.precios.precio_cobre * 1.5,
            )
            r.valor_placas = precio_placa * coef
        else:
            fraccion_cobre = dist.siguiente_normal(0.35, 0.08)
            kg_cobre = kg_placas_peso * fraccion_cobre * coef
            r.valor_placas = kg_cobre * params.precios.precio_cobre

        kg_metal_real = kg_metal * params.composicion.rendimiento_metal * coef
        r.valor_metal = kg_metal_real * params.precios.precio_aluminio
        r.kg_metal = kg_metal_real

        return r
