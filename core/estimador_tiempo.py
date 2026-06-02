"""
core/estimador_tiempo.py
-------------------------
Módulo separado para calcular el tiempo real (estimado) que tomará procesar el lote,
teniendo en cuenta la arquitectura en serie y paralelo de las estaciones de la planta.
"""

from core.resultados import ResultadoLote

def estimar_tiempo_procesamiento(resultado: ResultadoLote) -> float:
    """
    Calcula el tiempo real aproximado (en minutos) de procesamiento del lote basándose 
    en las dependencias en serie y paralelo de las estaciones de trabajo.
    
    Reglas de negocio:
    1. Revisión general (E1) es en SERIE.
    2. Desarmar cámara (E2), Desarmar DVR (E5) y Recuperar ópticas (E3) son PARALELAS.
    3. Recuperar placas (E4) y Recuperar discos (E6) son en SERIE.
    
    Args:
        resultado (ResultadoLote): El resultado de la simulación.
        
    Returns:
        float: Tiempo total estimado en minutos.
    """
    # 1. Fase en serie inicial
    tiempo_revision = resultado.tdr
    
    # 2. Fase paralela (el tiempo que domina es el del cuello de botella más lento de esta fase)
    tiempo_desarme_y_opticas = max(resultado.tdo, resultado.tdd, resultado.tco)
    
    # 3. Fase en serie final
    tiempo_placas_y_discos = resultado.tp + resultado.thd
    
    # Suma total
    tiempo_total = tiempo_revision + tiempo_desarme_y_opticas + tiempo_placas_y_discos
    
    return tiempo_total

def calcular_jornadas(minutos_totales: float, horas_por_jornada: float) -> float:
    """Calcula cuántas jornadas de trabajo representan los minutos totales."""
    if horas_por_jornada <= 0:
        return 0.0
    minutos_por_jornada = horas_por_jornada * 60
    return minutos_totales / minutos_por_jornada

def formatear_tiempo(minutos_totales: float, horas_por_jornada: float) -> str:
    """Convierte los minutos a un formato de texto legible (Horas, Minutos y Jornadas)."""
    minutos_enteros = int(minutos_totales)
    horas = minutos_enteros // 60
    minutos = minutos_enteros % 60
    
    jornadas = calcular_jornadas(minutos_totales, horas_por_jornada)
    str_jornadas = f" (~{jornadas:.1f} jornadas)"
    
    if horas > 0:
        return f"{horas} hs {minutos} min{str_jornadas}"
    else:
        return f"{minutos} min{str_jornadas}"
