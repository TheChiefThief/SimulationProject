"""core/indicadores/calculador.py - Calcula indicadores de eficiencia operativa."""

from core.parametros_dominio import ParametrosOperativo
from core.resultados import ResultadoLote


class CalculadorIndicadores:
    """
    Calcula indicadores de eficiencia industrial de forma independiente.

    Métodos estáticos para no requerir estado, permitiendo reutilización.
    """

    @staticmethod
    def calcular(
        parametros_operativo: ParametrosOperativo,
        lote: ResultadoLote,
        precios=None,
        composicion=None,
    ) -> tuple[float, float, float, float]:
        """
        Calcula los indicadores de eficiencia del lote.

        Args:
            parametros_operativo: Parámetros operativos (horas, empleados, etc.).
            lote: ResultadoLote con datos agregados de la simulación.
            precios: PreciosParametros (opcional, para cálculo de máximo teórico).
            composicion: ComposicionParametros (opcional, para cálculo de máximo teórico).

        Returns:
            Tupla (coef_productividad, eficacia, eficiencia, rango_mejora):
            - coef_productividad: unidades procesadas por hora por empleado
            - eficacia: % de dispositivos recuperables vs total
            - eficiencia: % valor recuperado vs valor teórico máximo
            - rango_mejora: puntos porcentuales de diferencia con ideal
        """
        n_total = lote.n_total
        if n_total == 0 or parametros_operativo.horas_trabajo == 0 or parametros_operativo.cantidad_empleados == 0:
            return 0.0, 0.0, 0.0, 0.0

        # Coeficiente de productividad (unidades / hora / empleado)
        coef_prod = n_total / (
            parametros_operativo.horas_trabajo * parametros_operativo.cantidad_empleados
        )

        # Eficacia: % de dispositivos recuperables del total procesado
        n_recuperables = lote.camaras_recuperables + lote.dvrs_recuperables
        eficacia = (n_recuperables / n_total) * 100.0

        # Valor teórico máximo (todos recuperables, sin pérdida)
        if precios and composicion:
            val_max_camara = (
                precios.precio_lentes
                + composicion.peso_camara
                * composicion.camara_fraccion_placas
                * precios.precio_cobre
                + composicion.peso_camara
                * composicion.camara_fraccion_plastico
                * precios.precio_plastico
                + composicion.peso_camara
                * composicion.camara_fraccion_metal
                * precios.precio_aluminio
            ) * lote.n_camaras

            val_max_dvr = (
                2000 * precios.precio_almacenamiento_max
                + composicion.peso_dvr * composicion.dvr_fraccion_placas * precios.precio_cobre
                + composicion.peso_dvr * composicion.dvr_fraccion_metal * precios.precio_aluminio
            ) * lote.n_dvrs

            val_max = val_max_camara + val_max_dvr
        else:
            val_max = 0.0

        eficiencia = (lote.valor_total / val_max * 100.0) if val_max > 0 else 0.0
        rango_mejora = 100.0 - eficiencia

        return coef_prod, eficacia, eficiencia, rango_mejora
