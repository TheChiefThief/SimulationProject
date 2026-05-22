"""core/simulacion_service.py - Servicio que orquesta la simulación completa."""

from typing import Callable

from core.gcl import GeneradorCongruencialLineal
from core.parametros import ParametrosSistema
from core.resultados import ResultadoLote
from core.simuladores import SimuladorCamara, SimuladorDVR
from core.indicadores import CalculadorIndicadores


class SimulacionService:
    """
    Servicio de simulación que orquesta todos los componentes.

    Actúa como facade hacia la GUI, permitiendo:
    - Inyección de dependencias (especialmente GCL)
    - Separación clara de responsabilidades
    - Testabilidad mediante mocks
    - Punto único de entrada para simulación

    Patrón: Service Locator + Facade
    """

    def __init__(
        self,
        parametros: ParametrosSistema,
        gcl_factory: Callable[[], GeneradorCongruencialLineal] = None,
    ):
        """
        Inicializa el servicio de simulación.

        Args:
            parametros: ParametrosSistema compartido con la aplicación.
            gcl_factory: Factory para crear GeneradorCongruencialLineal.
                        Si no se provee, usa el constructor por defecto.
        """
        self.parametros = parametros
        self.gcl_factory = gcl_factory or GeneradorCongruencialLineal
        self.simulador_camara = SimuladorCamara(parametros)
        self.simulador_dvr = SimuladorDVR(parametros)
        self.calculador = CalculadorIndicadores()

    def simular_lote(self, n_camaras: int, n_dvrs: int) -> ResultadoLote:
        """
        Ejecuta la simulación completa de un lote de dispositivos.

        Flujo:
          1. Valida que parámetros estén cargados
          2. Instancia GCL (inyectable)
          3. Procesa cada cámara con SimuladorCamara
          4. Procesa cada DVR con SimuladorDVR
          5. Calcula indicadores con CalculadorIndicadores
          6. Retorna resultado agregado

        Args:
            n_camaras: Cantidad de cámaras a procesar.
            n_dvrs: Cantidad de DVRs a procesar.

        Returns:
            ResultadoLote con agregados y métricas de eficiencia.

        Raises:
            RuntimeError: Si los parámetros operativos no están cargados.
        """
        if not self.parametros.parametros_cargados:
            raise RuntimeError(
                "Los parámetros operativos no han sido cargados. "
                "Por favor, complete la Vista del Gerente antes de ejecutar."
            )

        gcl = self.gcl_factory()
        resultado = ResultadoLote()
        resultado.semilla_gcl = gcl.semilla
        resultado.n_camaras = n_camaras
        resultado.n_dvrs = n_dvrs

        # Procesar cámaras
        for _ in range(n_camaras):
            rc = self.simulador_camara.simular(gcl)
            if rc.recuperable:
                resultado.camaras_recuperables += 1
            else:
                resultado.camaras_desguazadas += 1

            resultado.valor_lentes += rc.valor_lentes
            resultado.valor_placas_camara += rc.valor_placas
            resultado.valor_plastico += rc.valor_plastico
            resultado.valor_metal += rc.valor_metal
            resultado.kg_plastico += rc.kg_plastico
            resultado.kg_metal += rc.kg_metal

        # Procesar DVRs
        for _ in range(n_dvrs):
            rd = self.simulador_dvr.simular(gcl)
            if rd.recuperable:
                resultado.dvrs_recuperables += 1
            else:
                resultado.dvrs_desguazados += 1

            resultado.valor_hdd += rd.valor_hdd
            resultado.valor_placas_dvr += rd.valor_placas
            resultado.valor_metal += rd.valor_metal
            resultado.kg_metal += rd.kg_metal

        # Calcular indicadores de eficiencia
        resultado.coef_productividad, resultado.eficacia, \
            resultado.eficiencia, resultado.rango_mejora = \
            self.calculador.calcular(
                self.parametros.operativo,
                resultado,
                precios=self.parametros.precios,
                composicion=self.parametros.composicion,
            )

        return resultado
