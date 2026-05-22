"""core/simuladores/simulador_camara.py - Simulador para dispositivos de tipo cámara."""

from core.gcl import GeneradorCongruencialLineal
from core.parametros import ParametrosSistema
from core.resultados import ResultadoCamara


class SimuladorCamara:
    """
    Simulador independiente para procesamiento de cámaras de seguridad.

    Encapsula la lógica de árbol de decisiones para cada cámara:
    - Estado general (recuperable/desguace)
    - Componentes ópticos (sano/dañado)
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

    def simular(self, gcl: GeneradorCongruencialLineal) -> ResultadoCamara:
        """
        Simula el procesamiento de una cámara individual.

        Árbol de decisiones:
          1. Estado general (Bernoulli 0.72 aprox.)
          2. Componentes ópticos (Bernoulli)
          3. Placas (Bernoulli)
          4. Materiales base siempre se recuperan

        Args:
            gcl: Generador congruencial lineal para aleatorización.

        Returns:
            ResultadoCamara con valores calculados.
        """
        r = ResultadoCamara()
        params = self.parametros
        coef = 1.0 - params.operativo.coeficiente_perdida

        kg_total = params.composicion.peso_camara
        kg_plastico = kg_total * params.composicion.camara_fraccion_plastico
        kg_placas_peso = kg_total * params.composicion.camara_fraccion_placas
        kg_metal = kg_total * params.composicion.camara_fraccion_metal
        kg_opticos = kg_total * params.composicion.camara_fraccion_opticos

        # Decisión 1: Estado general del dispositivo
        r.recuperable = gcl.siguiente_bernoulli(0.72)

        if not r.recuperable:
            kg_plas_real = kg_plastico * params.composicion.rendimiento_plastico * coef
            r.valor_plastico = kg_plas_real * params.precios.precio_plastico
            r.kg_plastico = kg_plas_real

            kg_metal_real = kg_metal * params.composicion.rendimiento_metal * coef
            r.valor_metal = kg_metal_real * params.precios.precio_aluminio
            r.kg_metal = kg_metal_real
            return r

        # Decisión 2: Componentes ópticos
        r.optica_sana = gcl.siguiente_bernoulli(params.tasas.tasa_opticas_sanas)

        if r.optica_sana:
            r.valor_lentes = params.precios.precio_lentes * coef
        else:
            fraccion_vidrio = gcl.siguiente_triangular(0.2, 0.5, 0.9)
            kg_vidrio = kg_opticos * fraccion_vidrio * coef
            r.valor_lentes = kg_vidrio * params.precios.precio_vidrio

        # Decisión 3: Placas electrónicas
        r.placa_sana = gcl.siguiente_bernoulli(params.tasas.tasa_placas_sanas)

        if r.placa_sana:
            precio_placa = gcl.siguiente_rango(
                kg_placas_peso * params.precios.precio_cobre * 0.8,
                kg_placas_peso * params.precios.precio_cobre * 1.5,
            )
            r.valor_placas = precio_placa * coef
        else:
            fraccion_cobre = gcl.siguiente_triangular(0.1, 0.35, 0.6)
            kg_cobre = kg_placas_peso * fraccion_cobre * coef
            r.valor_placas = kg_cobre * params.precios.precio_cobre

        kg_plas_real = kg_plastico * params.composicion.rendimiento_plastico * coef
        r.valor_plastico = kg_plas_real * params.precios.precio_plastico
        r.kg_plastico = kg_plas_real

        kg_metal_real = kg_metal * params.composicion.rendimiento_metal * coef
        r.valor_metal = kg_metal_real * params.precios.precio_aluminio
        r.kg_metal = kg_metal_real

        return r
