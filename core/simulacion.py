"""
core/simulacion.py
------------------
Motor de simulación de reciclaje de RAEE (cámaras y DVRs).

Toda la aleatorización se realiza EXCLUSIVAMENTE mediante el GCL
definido en core/gcl.py. No se utiliza ninguna librería de números
aleatorios externa.

Flujo lógico por dispositivo:
  1. Estado general: Bernoulli(p) → recuperable o desguace completo
  2. Componentes ópticos: Bernoulli → sano o dañado
  3. Placas: Bernoulli → funcional o recuperación parcial
  4. HDD (solo DVR): Bernoulli → operativo o desguace estructural
  5. Valores se calculan con distribuciones aplicadas via GCL
"""

from core.gcl import GeneradorCongruencialLineal
from core.parametros import ParametrosSistema


# ---------------------------------------------------------------------------
# Resultados de simulación
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Funciones de simulación individuales
# ---------------------------------------------------------------------------

def simular_camara(params: ParametrosSistema, gcl: GeneradorCongruencialLineal) -> ResultadoCamara:
    """
    Simula el procesamiento de una cámara de seguridad.

    Árbol de decisiones:
      - Estado general (Bernoulli con p=tasa_opticas_sanas aprox.):
          * Recuperable → se procesan componentes individualmente
          * No recuperable → desguace completo, solo se recupera plástico base
      - Componentes ópticos (Bernoulli):
          * Sanos → valor unitario de lente
          * Dañados → recuperación parcial de vidrio
      - Placas (Bernoulli):
          * Sanas → recuperación funcional completa
          * Dañadas → recuperación parcial de cobre/componentes

    Args:
        params: Parámetros del sistema con precios y tasas.
        gcl:    Generador congruencial lineal para obtener U ~ Uniforme[0,1).

    Returns:
        ResultadoCamara con todos los valores calculados.
    """
    r = ResultadoCamara()
    coef = 1.0 - params.coeficiente_perdida

    # Peso de los componentes de esta cámara
    kg_total = params.peso_camara
    kg_plastico = kg_total * params.camara_fraccion_plastico
    kg_placas_peso = kg_total * params.camara_fraccion_placas
    kg_metal = kg_total * params.camara_fraccion_metal
    kg_opticos = kg_total * params.camara_fraccion_opticos

    # --- Decisión 1: Estado general del dispositivo ---
    r.recuperable = gcl.siguiente_bernoulli(0.72)

    if not r.recuperable:
        # Desguace completo: solo recuperamos plástico a precio base
        kg_plas_real = kg_plastico * params.rendimiento_plastico * coef
        r.valor_plastico = kg_plas_real * params.precio_plastico
        r.kg_plastico = kg_plas_real

        kg_metal_real = kg_metal * params.rendimiento_metal * coef
        r.valor_metal = kg_metal_real * params.precio_aluminio
        r.kg_metal = kg_metal_real
        return r

    # --- Decisión 2: Componentes ópticos ---
    r.optica_sana = gcl.siguiente_bernoulli(params.tasa_opticas_sanas)

    if r.optica_sana:
        # Lente funcional: valor unitario completo
        r.valor_lentes = params.precio_lentes * coef
    else:
        # Lente dañado: recuperación parcial de vidrio
        # Distribución triangular para variabilidad en la fracción recuperada
        fraccion_vidrio = gcl.siguiente_triangular(0.2, 0.5, 0.9)
        kg_vidrio = kg_opticos * fraccion_vidrio * coef
        r.valor_lentes = kg_vidrio * params.precio_vidrio

    # --- Decisión 3: Placas electrónicas ---
    r.placa_sana = gcl.siguiente_bernoulli(params.tasa_placas_sanas)

    if r.placa_sana:
        # Placa sana: recuperación funcional — valor proporcional al peso
        # Se modela con distribución uniforme en un rango razonable de precio
        precio_placa = gcl.siguiente_rango(
            kg_placas_peso * params.precio_cobre * 0.8,
            kg_placas_peso * params.precio_cobre * 1.5
        )
        r.valor_placas = precio_placa * coef
    else:
        # Placa dañada: recuperación parcial de cobre
        fraccion_cobre = gcl.siguiente_triangular(0.1, 0.35, 0.6)
        kg_cobre = kg_placas_peso * fraccion_cobre * coef
        r.valor_placas = kg_cobre * params.precio_cobre

    # Plástico y metal siempre se recuperan (aunque sea parcialmente)
    kg_plas_real = kg_plastico * params.rendimiento_plastico * coef
    r.valor_plastico = kg_plas_real * params.precio_plastico
    r.kg_plastico = kg_plas_real

    kg_metal_real = kg_metal * params.rendimiento_metal * coef
    r.valor_metal = kg_metal_real * params.precio_aluminio
    r.kg_metal = kg_metal_real

    return r


def simular_dvr(params: ParametrosSistema, gcl: GeneradorCongruencialLineal) -> ResultadoDVR:
    """
    Simula el procesamiento de un DVR.

    Árbol de decisiones:
      - Estado general (Bernoulli):
          * Recuperable → se procesan componentes individualmente
          * No recuperable → desguace completo
      - HDD (Bernoulli):
          * Operativo → se recupera capacidad de almacenamiento (GB)
          * Inoperativo → recuperación de materiales estructurales (aluminio/imanes)
      - Placas (Bernoulli):
          * Sanas → recuperación funcional
          * Dañadas → recuperación parcial de cobre

    Args:
        params: Parámetros del sistema.
        gcl:    Generador congruencial lineal.

    Returns:
        ResultadoDVR con todos los valores calculados.
    """
    r = ResultadoDVR()
    coef = 1.0 - params.coeficiente_perdida

    kg_total = params.peso_dvr
    kg_hdd = kg_total * params.dvr_fraccion_hdd
    kg_metal = kg_total * params.dvr_fraccion_metal
    kg_placas_peso = kg_total * params.dvr_fraccion_placas

    # --- Decisión 1: Estado general ---
    r.recuperable = gcl.siguiente_bernoulli(0.68)

    if not r.recuperable:
        # Desguace total: recuperamos metal estructural
        kg_metal_real = kg_metal * params.rendimiento_metal * coef
        r.valor_metal = kg_metal_real * params.precio_aluminio
        r.kg_metal = kg_metal_real
        return r

    # --- Decisión 2: HDD ---
    r.hdd_operativo = gcl.siguiente_bernoulli(params.tasa_discos_sanos)

    if r.hdd_operativo:
        # HDD operativo: recuperar capacidad de almacenamiento
        # Distribución uniforme para la capacidad en GB (rangos típicos de cámaras CCTV)
        capacidad_gb = gcl.siguiente_entero(250, 2000)
        precio_gb = gcl.siguiente_rango(
            params.precio_almacenamiento_min,
            params.precio_almacenamiento_max
        )
        r.valor_hdd = capacidad_gb * precio_gb * coef
    else:
        # HDD inoperativo: recuperar materiales (aluminio, imanes de tierras raras)
        # Se modela con fracción triangular del peso total del HDD
        fraccion_mat = gcl.siguiente_triangular(0.3, 0.5, 0.8)
        kg_mat_hdd = kg_hdd * fraccion_mat * coef
        r.valor_hdd = kg_mat_hdd * params.precio_aluminio

    # --- Decisión 3: Placas del DVR ---
    r.placa_sana = gcl.siguiente_bernoulli(params.tasa_placas_sanas)

    if r.placa_sana:
        precio_placa = gcl.siguiente_rango(
            kg_placas_peso * params.precio_cobre * 0.8,
            kg_placas_peso * params.precio_cobre * 1.5
        )
        r.valor_placas = precio_placa * coef
    else:
        fraccion_cobre = gcl.siguiente_triangular(0.1, 0.35, 0.6)
        kg_cobre = kg_placas_peso * fraccion_cobre * coef
        r.valor_placas = kg_cobre * params.precio_cobre

    kg_metal_real = kg_metal * params.rendimiento_metal * coef
    r.valor_metal = kg_metal_real * params.precio_aluminio
    r.kg_metal = kg_metal_real

    return r


# ---------------------------------------------------------------------------
# Función principal de simulación de lote
# ---------------------------------------------------------------------------

def simular_lote(
    params: ParametrosSistema,
    n_camaras: int,
    n_dvrs: int
) -> ResultadoLote:
    """
    Ejecuta la simulación completa de un lote de dispositivos.

    Instancia un GCL con semilla aleatoria (basada en tiempo de sistema)
    y procesa cada dispositivo individualmente aplicando el árbol de
    decisiones definido en simular_camara y simular_dvr.

    Args:
        params:    Parámetros del sistema (deben estar cargados).
        n_camaras: Cantidad de cámaras a procesar.
        n_dvrs:    Cantidad de DVRs a procesar.

    Returns:
        ResultadoLote con todos los agregados y métricas de eficiencia.

    Raises:
        RuntimeError: Si los parámetros no fueron cargados previamente.
    """
    if not params.parametros_cargados:
        raise RuntimeError(
            "Los parámetros operativos no han sido cargados. "
            "Por favor, complete la Vista del Gerente antes de ejecutar."
        )

    # Instanciar GCL — semilla automática desde nanosegundos del sistema
    gcl = GeneradorCongruencialLineal()
    resultado = ResultadoLote()
    resultado.semilla_gcl = gcl.semilla
    resultado.n_camaras = n_camaras
    resultado.n_dvrs = n_dvrs

    # ---- Procesar cámaras ----
    for _ in range(n_camaras):
        rc = simular_camara(params, gcl)
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

    # ---- Procesar DVRs ----
    for _ in range(n_dvrs):
        rd = simular_dvr(params, gcl)
        if rd.recuperable:
            resultado.dvrs_recuperables += 1
        else:
            resultado.dvrs_desguazados += 1

        resultado.valor_hdd += rd.valor_hdd
        resultado.valor_placas_dvr += rd.valor_placas
        resultado.valor_metal += rd.valor_metal
        resultado.kg_metal += rd.kg_metal

    # ---- Calcular indicadores de eficiencia operativa ----
    resultado.coef_productividad, resultado.eficacia, \
        resultado.eficiencia, resultado.rango_mejora = \
        _calcular_indicadores(params, resultado)

    return resultado


def _calcular_indicadores(params: ParametrosSistema, lote: ResultadoLote):
    """
    Calcula los indicadores de eficiencia industrial.

    - Coeficiente de productividad: unidades procesadas por hora por empleado
    - Eficacia: fracción del lote que fue recuperable vs total ingresado
    - Eficiencia: relación valor recuperado / valor teórico máximo posible
    - Rango de mejora: diferencia porcentual con escenario ideal (100% recuperable)

    Returns:
        Tupla (coef_productividad, eficacia, eficiencia, rango_mejora)
    """
    n_total = lote.n_total
    if n_total == 0 or params.horas_trabajo == 0 or params.cantidad_empleados == 0:
        return 0.0, 0.0, 0.0, 0.0

    # Coeficiente de productividad (unidades / hora / empleado)
    coef_prod = n_total / (params.horas_trabajo * params.cantidad_empleados)

    # Eficacia: % de dispositivos recuperables del total procesado
    n_recuperables = lote.camaras_recuperables + lote.dvrs_recuperables
    eficacia = (n_recuperables / n_total) * 100.0

    # Valor teórico máximo (todos recuperables, sin pérdida)
    val_max_camara = (
        params.precio_lentes
        + params.peso_camara * params.camara_fraccion_placas * params.precio_cobre
        + params.peso_camara * params.camara_fraccion_plastico * params.precio_plastico
        + params.peso_camara * params.camara_fraccion_metal * params.precio_aluminio
    ) * lote.n_camaras

    val_max_dvr = (
        2000 * params.precio_almacenamiento_max  # HDD de 2TB a precio máximo
        + params.peso_dvr * params.dvr_fraccion_placas * params.precio_cobre
        + params.peso_dvr * params.dvr_fraccion_metal * params.precio_aluminio
    ) * lote.n_dvrs

    val_max = val_max_camara + val_max_dvr
    eficiencia = (lote.valor_total / val_max * 100.0) if val_max > 0 else 0.0

    # Rango de mejora (puntos porcentuales de diferencia con el ideal)
    rango_mejora = 100.0 - eficiencia

    return coef_prod, eficacia, eficiencia, rango_mejora
