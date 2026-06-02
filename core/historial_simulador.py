"""
core/historial_simulador.py
----------------------------
Módulo para persistir y recuperar el historial de simulaciones realizadas.
Permite guardar las configuraciones de parámetros y resultados de cada corrida en un archivo JSON.
"""

import json
import os
import uuid
from datetime import datetime

from core.logger import registrar_error
from core.parametros import ParametrosSistema
from core.resultados import ResultadoLote


class HistorialSimulador:
    """
    Clase utilitaria con métodos estáticos para guardar, recuperar
    y administrar el historial de simulaciones.
    """

    DEFAULT_FILE = "historial_simulaciones.json"

    @staticmethod
    def serializar_parametros(params: ParametrosSistema) -> dict:
        """Convierte los parámetros del sistema en un diccionario serializable."""
        return {
            "precios": {
                "precio_oro": params.precios.precio_oro,
                "precio_vidrio": params.precios.precio_vidrio,
                "precio_lentes": params.precios.precio_lentes,
                "precio_cobre": params.precios.precio_cobre,
                "precio_aluminio": params.precios.precio_aluminio,
                "precio_plastico": params.precios.precio_plastico,
                "precio_almacenamiento_min": params.precios.precio_almacenamiento_min,
                "precio_almacenamiento_max": params.precios.precio_almacenamiento_max,
            },
            "composicion": {
                "camara_fraccion_plastico": params.composicion.camara_fraccion_plastico,
                "camara_fraccion_placas": params.composicion.camara_fraccion_placas,
                "camara_fraccion_metal": params.composicion.camara_fraccion_metal,
                "camara_fraccion_opticos": params.composicion.camara_fraccion_opticos,
                "dvr_fraccion_hdd": params.composicion.dvr_fraccion_hdd,
                "dvr_fraccion_metal": params.composicion.dvr_fraccion_metal,
                "dvr_fraccion_placas": params.composicion.dvr_fraccion_placas,
                "peso_camara": params.composicion.peso_camara,
                "peso_dvr": params.composicion.peso_dvr,
                "peso_camara_min": params.composicion.peso_camara_min,
                "peso_camara_max": params.composicion.peso_camara_max,
                "peso_dvr_min": params.composicion.peso_dvr_min,
                "peso_dvr_max": params.composicion.peso_dvr_max,
                "rendimiento_plastico": params.composicion.rendimiento_plastico,
                "rendimiento_metal": params.composicion.rendimiento_metal,
            },
            "tasas": {
                "tasa_placas_sanas": params.tasas.tasa_placas_sanas,
                "tasa_opticas_sanas": params.tasas.tasa_opticas_sanas,
                "tasa_discos_sanos": params.tasas.tasa_discos_sanos,
            },
            "operativo": {
                "horas_trabajo": params.operativo.horas_trabajo,
                "cantidad_empleados": params.operativo.cantidad_empleados,
                "energia_consumida": params.operativo.energia_consumida,
                "coeficiente_perdida": params.operativo.coeficiente_perdida,
                "tipo_maquinaria": params.operativo.tipo_maquinaria,
            },
        }

    @staticmethod
    def deserializar_parametros(data: dict) -> ParametrosSistema:
        """Reconstruye un objeto ParametrosSistema a partir de un diccionario."""
        params = ParametrosSistema()

        # Precios
        p_data = data.get("precios", {})
        params.precios.precio_oro = p_data.get("precio_oro", params.precios.precio_oro)
        params.precios.precio_vidrio = p_data.get("precio_vidrio", params.precios.precio_vidrio)
        params.precios.precio_lentes = p_data.get("precio_lentes", params.precios.precio_lentes)
        params.precios.precio_cobre = p_data.get("precio_cobre", params.precios.precio_cobre)
        params.precios.precio_aluminio = p_data.get("precio_aluminio", params.precios.precio_aluminio)
        params.precios.precio_plastico = p_data.get("precio_plastico", params.precios.precio_plastico)
        params.precios.precio_almacenamiento_min = p_data.get("precio_almacenamiento_min", params.precios.precio_almacenamiento_min)
        params.precios.precio_almacenamiento_max = p_data.get("precio_almacenamiento_max", params.precios.precio_almacenamiento_max)

        # Composición
        c_data = data.get("composicion", {})
        params.composicion.camara_fraccion_plastico = c_data.get("camara_fraccion_plastico", params.composicion.camara_fraccion_plastico)
        params.composicion.camara_fraccion_placas = c_data.get("camara_fraccion_placas", params.composicion.camara_fraccion_placas)
        params.composicion.camara_fraccion_metal = c_data.get("camara_fraccion_metal", params.composicion.camara_fraccion_metal)
        params.composicion.camara_fraccion_opticos = c_data.get("camara_fraccion_opticos", params.composicion.camara_fraccion_opticos)
        params.composicion.dvr_fraccion_hdd = c_data.get("dvr_fraccion_hdd", params.composicion.dvr_fraccion_hdd)
        params.composicion.dvr_fraccion_metal = c_data.get("dvr_fraccion_metal", params.composicion.dvr_fraccion_metal)
        params.composicion.dvr_fraccion_placas = c_data.get("dvr_fraccion_placas", params.composicion.dvr_fraccion_placas)
        params.composicion.peso_camara = c_data.get("peso_camara", params.composicion.peso_camara)
        params.composicion.peso_dvr = c_data.get("peso_dvr", params.composicion.peso_dvr)
        params.composicion.peso_camara_min = c_data.get("peso_camara_min", params.composicion.peso_camara_min)
        params.composicion.peso_camara_max = c_data.get("peso_camara_max", params.composicion.peso_camara_max)
        params.composicion.peso_dvr_min = c_data.get("peso_dvr_min", params.composicion.peso_dvr_min)
        params.composicion.peso_dvr_max = c_data.get("peso_dvr_max", params.composicion.peso_dvr_max)
        params.composicion.rendimiento_plastico = c_data.get("rendimiento_plastico", params.composicion.rendimiento_plastico)
        params.composicion.rendimiento_metal = c_data.get("rendimiento_metal", params.composicion.rendimiento_metal)

        # Tasas
        t_data = data.get("tasas", {})
        params.tasas.tasa_placas_sanas = t_data.get("tasa_placas_sanas", params.tasas.tasa_placas_sanas)
        params.tasas.tasa_opticas_sanas = t_data.get("tasa_opticas_sanas", params.tasas.tasa_opticas_sanas)
        params.tasas.tasa_discos_sanos = t_data.get("tasa_discos_sanos", params.tasas.tasa_discos_sanos)

        # Operativo
        o_data = data.get("operativo", {})
        params.operativo.horas_trabajo = o_data.get("horas_trabajo", params.operativo.horas_trabajo)
        params.operativo.cantidad_empleados = o_data.get("cantidad_empleados", params.operativo.cantidad_empleados)
        params.operativo.energia_consumida = o_data.get("energia_consumida", params.operativo.energia_consumida)
        params.operativo.coeficiente_perdida = o_data.get("coeficiente_perdida", params.operativo.coeficiente_perdida)
        params.operativo.tipo_maquinaria = o_data.get("tipo_maquinaria", params.operativo.tipo_maquinaria)

        params.parametros_cargados = True
        return params

    @staticmethod
    def serializar_resultados(res: ResultadoLote) -> dict:
        """Convierte un ResultadoLote en un diccionario serializable."""
        return {
            "b_kg_input": res.b_kg_input,
            "peso_acumulado": res.peso_acumulado,
            "n_total": res.n_total,
            "cant_cam": res.cant_cam,
            "cant_dvr": res.cant_dvr,
            "cam_rec": res.cam_rec,
            "dvr_rec": res.dvr_rec,
            "equipos_reventa": res.equipos_reventa,
            "camaras_desguazadas": res.camaras_desguazadas,
            "dvrs_desguazados": res.dvrs_desguazados,
            "camaras_reventa": res.camaras_reventa,
            "dvrs_reventa": res.dvrs_reventa,
            "c1": res.c1,
            "c2": res.c2,
            "c3": res.c3,
            "c4": res.c4,
            "c5": res.c5,
            "c6": res.c6,
            "tdr": res.tdr,
            "tdo": res.tdo,
            "tco": res.tco,
            "tp": res.tp,
            "tdd": res.tdd,
            "thd": res.thd,
            "ocupacion_1": res.ocupacion_1,
            "ocupacion_2": res.ocupacion_2,
            "ocupacion_3": res.ocupacion_3,
            "ocupacion_4": res.ocupacion_4,
            "ocupacion_5": res.ocupacion_5,
            "ocupacion_6": res.ocupacion_6,
            "productividad_1": res.productividad_1,
            "productividad_2": res.productividad_2,
            "productividad_3": res.productividad_3,
            "productividad_4": res.productividad_4,
            "productividad_5": res.productividad_5,
            "productividad_6": res.productividad_6,
            "cuellos_botella": res.cuellos_botella,
            "mt": res.mt,
            "peso_plastico": res.peso_plastico,
            "peso_metal": res.peso_metal,
            "peso_cobre": res.peso_cobre,
            "peso_aluminio": res.peso_aluminio,
            "peso_oro": res.peso_oro,
            "peso_vidrio": res.peso_vidrio,
            "valor_cobre": res.valor_cobre,
            "valor_aluminio": res.valor_aluminio,
            "valor_oro": res.valor_oro,
            "valor_plastico": res.valor_plastico,
            "pmt": res.pmt,
            "pt": res.pt,
            "placas_f": res.placas_f,
            "placas_t": res.placas_t,
            "hdd_f": res.hdd_f,
            "hdd_t": res.hdd_t,
            "horas_demanda": res.horas_demanda,
            "basura_acumulada_poisson": res.basura_acumulada_poisson,
            "semilla_gcl": res.semilla_gcl,
        }

    @staticmethod
    def deserializar_resultados(data: dict) -> ResultadoLote:
        """Reconstruye un objeto ResultadoLote a partir de un diccionario."""
        res = ResultadoLote()
        res.b_kg_input = data.get("b_kg_input", 0.0)
        res.peso_acumulado = data.get("peso_acumulado", 0.0)
        res.n_total = data.get("n_total", 0)
        res.cant_cam = data.get("cant_cam", 0)
        res.cant_dvr = data.get("cant_dvr", 0)
        res.cam_rec = data.get("cam_rec", 0)
        res.dvr_rec = data.get("dvr_rec", 0)
        res.equipos_reventa = data.get("equipos_reventa", 0)
        res.camaras_desguazadas = data.get("camaras_desguazadas", 0)
        res.dvrs_desguazados = data.get("dvrs_desguazados", 0)
        res.camaras_reventa = data.get("camaras_reventa", 0)
        res.dvrs_reventa = data.get("dvrs_reventa", 0)
        res.c1 = data.get("c1", 0)
        res.c2 = data.get("c2", 0)
        res.c3 = data.get("c3", 0)
        res.c4 = data.get("c4", 0)
        res.c5 = data.get("c5", 0)
        res.c6 = data.get("c6", 0)
        res.tdr = data.get("tdr", 0.0)
        res.tdo = data.get("tdo", 0.0)
        res.tco = data.get("tco", 0.0)
        res.tp = data.get("tp", 0.0)
        res.tdd = data.get("tdd", 0.0)
        res.thd = data.get("thd", 0.0)
        res.ocupacion_1 = data.get("ocupacion_1", 0.0)
        res.ocupacion_2 = data.get("ocupacion_2", 0.0)
        res.ocupacion_3 = data.get("ocupacion_3", 0.0)
        res.ocupacion_4 = data.get("ocupacion_4", 0.0)
        res.ocupacion_5 = data.get("ocupacion_5", 0.0)
        res.ocupacion_6 = data.get("ocupacion_6", 0.0)
        res.productividad_1 = data.get("productividad_1", 0.0)
        res.productividad_2 = data.get("productividad_2", 0.0)
        res.productividad_3 = data.get("productividad_3", 0.0)
        res.productividad_4 = data.get("productividad_4", 0.0)
        res.productividad_5 = data.get("productividad_5", 0.0)
        res.productividad_6 = data.get("productividad_6", 0.0)
        res.cuellos_botella = data.get("cuellos_botella", [])
        res.mt = data.get("mt", 0.0)
        res.peso_plastico = data.get("peso_plastico", 0.0)
        res.peso_metal = data.get("peso_metal", 0.0)
        res.peso_cobre = data.get("peso_cobre", 0.0)
        res.peso_aluminio = data.get("peso_aluminio", 0.0)
        res.peso_oro = data.get("peso_oro", 0.0)
        res.peso_vidrio = data.get("peso_vidrio", 0.0)
        res.valor_cobre = data.get("valor_cobre", 0.0)
        res.valor_aluminio = data.get("valor_aluminio", 0.0)
        res.valor_oro = data.get("valor_oro", 0.0)
        res.valor_plastico = data.get("valor_plastico", 0.0)
        res.pmt = data.get("pmt", 0.0)
        res.pt = data.get("pt", 0.0)
        res.placas_f = data.get("placas_f", 0)
        res.placas_t = data.get("placas_t", 0)
        res.hdd_f = data.get("hdd_f", 0)
        res.hdd_t = data.get("hdd_t", 0)
        res.horas_demanda = data.get("horas_demanda", 0)
        res.basura_acumulada_poisson = data.get("basura_acumulada_poisson", data.get("clientes_totales", 0))
        res.semilla_gcl = data.get("semilla_gcl", 0)
        return res

    @classmethod
    def guardar_simulacion(
        cls, params: ParametrosSistema, resultado: ResultadoLote, archivo=None
    ) -> str:
        """
        Guarda una simulación en el archivo JSON.
        Retorna el ID único asignado a la simulación.
        """
        if archivo is None:
            archivo = cls.DEFAULT_FILE

        registro_id = str(uuid.uuid4())
        registro = {
            "id": registro_id,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": datetime.now().timestamp(),
            "parametros": cls.serializar_parametros(params),
            "resultados": cls.serializar_resultados(resultado),
        }

        historial = []
        if os.path.exists(archivo):
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    historial = json.load(f)
                    if not isinstance(historial, list):
                        historial = []
            except Exception as e:
                # registros de errores
                registrar_error("Error al cargar el archivo de historial JSON en guardar_simulacion", e)
                historial = []

        historial.append(registro)

        try:
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(historial, f, indent=4, ensure_ascii=False)
        except Exception as e:
            # registros de errores
            registrar_error("Error al escribir el archivo de historial JSON en guardar_simulacion", e)

        return registro_id

    @classmethod
    def obtener_historial(cls, archivo=None) -> list[dict]:
        """
        Retorna la lista de todas las simulaciones guardadas,
        ordenadas de la más reciente a la más antigua.
        """
        if archivo is None:
            archivo = cls.DEFAULT_FILE

        if not os.path.exists(archivo):
            return []

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                historial = json.load(f)
                if not isinstance(historial, list):
                    return []
                # Ordenar por timestamp del más reciente al más antiguo
                historial.sort(key=lambda x: x.get("timestamp", 0.0), reverse=True)
                return historial
        except Exception as e:
            # registros de errores
            registrar_error("Error al leer el archivo de historial JSON en obtener_historial", e)
            return []

    @classmethod
    def limpiar_historial(cls, archivo=None) -> None:
        """Vacía todo el registro histórico de simulaciones."""
        if archivo is None:
            archivo = cls.DEFAULT_FILE

        try:
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)
        except Exception as e:
            # registros de errores
            registrar_error("Error al limpiar el archivo de historial JSON", e)

    @classmethod
    def eliminar_registro(cls, registro_id: str, archivo=None) -> bool:
        """
        Elimina un registro individual por su ID.
        Retorna True si fue encontrado y eliminado, False de lo contrario.
        """
        if archivo is None:
            archivo = cls.DEFAULT_FILE

        if not os.path.exists(archivo):
            return False

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                historial = json.load(f)
                if not isinstance(historial, list):
                    return False
        except Exception as e:
            # registros de errores
            registrar_error("Error al leer el archivo de historial JSON en eliminar_registro", e)
            return False

        original_len = len(historial)
        historial = [r for r in historial if r.get("id") != registro_id]

        if len(historial) == original_len:
            return False

        try:
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(historial, f, indent=4, ensure_ascii=False)
        except Exception as e:
            # registros de errores
            registrar_error("Error al escribir el archivo de historial JSON en eliminar_registro", e)
            return False

        return True
