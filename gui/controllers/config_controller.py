"""
gui/controllers/config_controller.py
-------------------------------------
Controlador para la Vista de Configuración (VistaConfig).
Maneja la lógica de validación y guardado de los parámetros de configuración.
"""

from core.logger import registrar_error
from core.validador import Validador
from core.parametros import ParametrosSistema

class ConfigController:
    """
    Controlador encargado de mediar entre VistaConfig y ParametrosSistema.
    Extrae la lógica de negocio, validación y persistencia en memoria de la UI.
    """
    def __init__(self, params: ParametrosSistema, vista):
        self.params = params
        self.vista = vista

    _PRECIOS_KEYS = {
        "precio_oro", "precio_vidrio", "precio_lentes", "precio_cobre",
        "precio_aluminio", "precio_plastico",
        "precio_almacenamiento_min", "precio_almacenamiento_max",
    }
    _FRACCIONES_KEYS = {
        "tasa_placas_sanas", "tasa_opticas_sanas", "tasa_discos_sanos",
        "rendimiento_plastico", "rendimiento_metal",
        "camara_fraccion_plastico", "camara_fraccion_placas",
        "camara_fraccion_metal", "camara_fraccion_opticos",
        "dvr_fraccion_hdd", "dvr_fraccion_metal", "dvr_fraccion_placas",
    }

    def guardar(self):
        """Valida los datos de la vista y actualiza los parámetros del sistema."""
        nombres_amigables = {
            "precio_oro": "Precio Oro ($/kg)",
            "precio_vidrio": "Precio Vidrio ($/kg)",
            "precio_lentes": "Precio Lentes ($/unidad)",
            "precio_cobre": "Precio Cobre ($/kg)",
            "precio_aluminio": "Precio Aluminio ($/kg)",
            "precio_plastico": "Precio Plástico ($/kg)",
            "precio_almacenamiento_min": "Precio Almacenamiento Mínimo ($/GB)",
            "precio_almacenamiento_max": "Precio Almacenamiento Máximo ($/GB)",
            "tasa_placas_sanas": "Tasa Placas Sanas",
            "tasa_opticas_sanas": "Tasa Ópticas Sanas",
            "tasa_discos_sanos": "Tasa Discos Sanos",
            "rendimiento_plastico": "Rendimiento Plástico",
            "rendimiento_metal": "Rendimiento Metal",
            "camara_fraccion_plastico": "Fracción Plástico (Cámara)",
            "camara_fraccion_placas": "Fracción Placas (Cámara)",
            "camara_fraccion_metal": "Fracción Metal (Cámara)",
            "camara_fraccion_opticos": "Fracción Ópticos (Cámara)",
            "dvr_fraccion_hdd": "Fracción HDD (DVR)",
            "dvr_fraccion_metal": "Fracción Metal (DVR)",
            "dvr_fraccion_placas": "Fracción Placas (DVR)",
        }

        self.vista.limpiar_estado()
        valores = {}
        datos = self.vista.obtener_datos()

        try:
            for key, texto in datos.items():
                nombre_amigable = nombres_amigables.get(key, key)

                if key in self._PRECIOS_KEYS:
                    valores[key] = Validador.validar_precio(texto, nombre_amigable)
                elif key in self._FRACCIONES_KEYS:
                    valores[key] = Validador.validar_fraccion(texto, nombre_amigable)
                else:
                    valores[key] = Validador.validar_float(texto, nombre_amigable)

            # Validar precio min <= precio max de almacenamiento
            if valores["precio_almacenamiento_min"] > valores["precio_almacenamiento_max"]:
                raise ValueError("El precio mínimo de almacenamiento no puede superar al máximo.")

            # Validar sumas de fracciones de composición
            Validador.validar_suma_cercana_uno(
                [
                    valores["camara_fraccion_plastico"],
                    valores["camara_fraccion_placas"],
                    valores["camara_fraccion_metal"],
                    valores["camara_fraccion_opticos"],
                ],
                [
                    nombres_amigables["camara_fraccion_plastico"],
                    nombres_amigables["camara_fraccion_placas"],
                    nombres_amigables["camara_fraccion_metal"],
                    nombres_amigables["camara_fraccion_opticos"],
                ],
                "Cámara"
            )

            Validador.validar_suma_cercana_uno(
                [
                    valores["dvr_fraccion_hdd"],
                    valores["dvr_fraccion_metal"],
                    valores["dvr_fraccion_placas"],
                ],
                [
                    nombres_amigables["dvr_fraccion_hdd"],
                    nombres_amigables["dvr_fraccion_metal"],
                    nombres_amigables["dvr_fraccion_placas"],
                ],
                "DVR"
            )

        except ValueError as e:
            registrar_error("Error de validación de configuración en ConfigController", e)
            self.vista.mostrar_error(str(e))
            return

        # Aplicar todos los valores al objeto params
        for key, valor in valores.items():
            if key in self._PRECIOS_KEYS:
                setattr(self.params.precios, key, valor)
            elif key in {"tasa_placas_sanas", "tasa_opticas_sanas", "tasa_discos_sanos"}:
                setattr(self.params.tasas, key, valor)
            else:
                setattr(self.params.composicion, key, valor)

        self.vista.mostrar_exito("Configuración guardada correctamente.")
