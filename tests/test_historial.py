"""
tests/test_historial.py
------------------------
Pruebas unitarias para el módulo de historial de simulaciones.
"""

import os
import pytest

from core.parametros import ParametrosSistema
from core.resultados import ResultadoLote
from core.historial_simulador import HistorialSimulador
from core.simulacion_service import SimulacionService


def test_serializacion_deserializacion_parametros(parametros_default):
    # Modificar algunos parámetros para diferenciarlos de los valores por defecto
    parametros_default.precios.precio_oro = 500000.0
    parametros_default.composicion.camara_fraccion_plastico = 0.50
    parametros_default.composicion.camara_fraccion_placas = 0.30  # Ajustar para mantener suma = 1
    parametros_default.operativo.cantidad_empleados = 12

    # Serializar
    serialized = HistorialSimulador.serializar_parametros(parametros_default)

    # Deserializar
    deserialized = HistorialSimulador.deserializar_parametros(serialized)

    # Verificar precios
    assert deserialized.precios.precio_oro == 500000.0
    assert deserialized.precios.precio_vidrio == parametros_default.precios.precio_vidrio
    
    # Verificar composición
    assert deserialized.composicion.camara_fraccion_plastico == 0.50
    assert deserialized.composicion.camara_fraccion_placas == 0.30
    
    # Verificar operativo
    assert deserialized.operativo.cantidad_empleados == 12


def test_serializacion_deserializacion_resultados():
    # Instanciar y rellenar un objeto ResultadoLote
    res = ResultadoLote()
    res.b_kg_input = 150.0
    res.peso_acumulado = 151.2
    res.n_total = 120
    res.cant_cam = 100
    res.cant_dvr = 20
    res.valor_cobre = 85000.0
    res.cuellos_botella = ["Estación 1 — Revisión General", "Estación 4 — Recuperación Placas"]
    res.semilla_gcl = 998877

    # Serializar
    serialized = HistorialSimulador.serializar_resultados(res)

    # Deserializar
    deserialized = HistorialSimulador.deserializar_resultados(serialized)

    # Verificar
    assert deserialized.b_kg_input == 150.0
    assert deserialized.peso_acumulado == 151.2
    assert deserialized.n_total == 120
    assert deserialized.cant_cam == 100
    assert deserialized.cant_dvr == 20
    assert deserialized.valor_cobre == 85000.0
    assert deserialized.cuellos_botella == ["Estación 1 — Revisión General", "Estación 4 — Recuperación Placas"]
    assert deserialized.semilla_gcl == 998877
    assert deserialized.valor_total == res.valor_total  # Propiedad calculada


def test_guardar_recuperar_limpiar_historial(parametros_default, gcl_factory, tmp_path):
    # Definir ruta de archivo temporal
    archivo_temp = str(tmp_path / "historial_test.json")

    # Ejecutar una simulación real
    service = SimulacionService(parametros_default, gcl_factory)
    resultado = service.simular_lote(b_kg=50.0)

    # Guardar en el historial temporal
    reg_id_1 = HistorialSimulador.guardar_simulacion(parametros_default, resultado, archivo=archivo_temp)
    assert reg_id_1 is not None
    assert len(reg_id_1) > 0

    # Guardar una segunda simulación
    resultado_2 = service.simular_lote(b_kg=80.0)
    reg_id_2 = HistorialSimulador.guardar_simulacion(parametros_default, resultado_2, archivo=archivo_temp)

    # Recuperar historial
    historial = HistorialSimulador.obtener_historial(archivo=archivo_temp)
    assert len(historial) == 2
    
    # Comprobar orden cronológico inverso (el más nuevo primero)
    assert historial[0]["id"] == reg_id_2
    assert historial[1]["id"] == reg_id_1
    
    # Comprobar datos recuperados
    res_recuperado_2 = HistorialSimulador.deserializar_resultados(historial[0]["resultados"])
    assert res_recuperado_2.b_kg_input == 80.0

    # Eliminar un registro
    eliminado = HistorialSimulador.eliminar_registro(reg_id_1, archivo=archivo_temp)
    assert eliminado is True
    
    historial_after_del = HistorialSimulador.obtener_historial(archivo=archivo_temp)
    assert len(historial_after_del) == 1
    assert historial_after_del[0]["id"] == reg_id_2

    # Limpiar todo el historial
    HistorialSimulador.limpiar_historial(archivo=archivo_temp)
    historial_vacio = HistorialSimulador.obtener_historial(archivo=archivo_temp)
    assert len(historial_vacio) == 0
