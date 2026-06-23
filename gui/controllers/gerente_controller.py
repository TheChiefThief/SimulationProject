"""
Controlador para la Vista del Gerente (VistaGerente).
Maneja la lógica de validación de parámetros operativos, carga de presets y restauración de valores base.
"""

from core.logger import registrar_error
from core.validador import Validador
from core.parametros import ParametrosSistema

class GerenteController:
    """
    Controlador encargado de mediar entre VistaGerente y ParametrosSistema.
    Aísla la lógica de negocio, presets y validación fuera del código de interfaz.
    """
    def __init__(self, params: ParametrosSistema, vista):
        self.params = params
        self.vista = vista
        self.presets = {}  # Almacena los presets definidos en la sesión actual

    def cargar_parametros(self):
        """Valida y aplica los parámetros ingresados en la vista."""
        self.vista.limpiar_error()
        datos = self.vista.obtener_datos()

        try:
            # ── Validar: Horas de trabajo ──────────────────────────────────
            # Se limita de 0.1 a 8.0 según requerimiento del profesor ("como maximo 8 horas")
            horas = Validador.validar_float(
                datos["horas"], "Horas de trabajo por jornada", min_valor=0.1, max_valor=8.0
            )

            # ── Validar: Cantidad de empleados ─────────────────────────────
            empleados = Validador.validar_entero(
                datos["empleados"], "Cantidad de empleados", min_valor=1, max_valor=1000
            )

            # ── Validar: Energía consumida ─────────────────────────────────
            energia = Validador.validar_float(
                datos["energia"], "Energía consumida (kWh)", min_valor=0.0, max_valor=100000.0
            )

            # ── Validar: Coeficiente de pérdida ───────────────────────────
            coef = Validador.validar_fraccion(
                datos["coef_perdida"], "Coeficiente de pérdida"
            )

        except ValueError as e:
            registrar_error("Error de validación de parámetros operativos en GerenteController", e)
            self.vista.mostrar_error(str(e))
            return

        # ── Aplicar parámetros al objeto compartido ────────────────────
        self.params.operativo.horas_trabajo = horas
        self.params.operativo.cantidad_empleados = empleados
        self.params.operativo.energia_consumida = energia
        self.params.operativo.coeficiente_perdida = coef
        self.params.operativo.tipo_maquinaria = datos["tipo_maquinaria"]
        self.params.parametros_cargados = True

        # ── Actualizar UI en la vista ──────────────────────────────────
        self.vista.mostrar_exito(
            mensaje="Parámetros cargados correctamente",
            horas=horas,
            empleados=empleados,
            energia=energia,
            tipo_maquinaria=datos["tipo_maquinaria"],
            coef=coef
        )

    def cargar_valores_base(self):
        """Restaura los valores base definidos por defecto y notifica a la vista."""
        self.vista.cargar_datos(
            horas="8.0",
            empleados="5",
            energia="100.0",
            coef_perdida="0.05",
            tipo_maquinaria="Proceso Manual"
        )
        self.cargar_parametros()
        self.vista.mostrar_mensaje_valores_base()

    def guardar_preset(self):
        """Guarda los valores actuales de la vista bajo el preset seleccionado."""
        nombre = self.vista.obtener_preset_seleccionado()
        datos = self.vista.obtener_datos()

        self.presets[nombre] = (
            datos["horas"],
            datos["empleados"],
            datos["energia"],
            datos["coef_perdida"],
            datos["tipo_maquinaria"]
        )
        self.vista.mostrar_mensaje_preset_guardado(nombre)

    def cargar_preset(self):
        """Carga en los campos el preset seleccionado si existe."""
        nombre = self.vista.obtener_preset_seleccionado()
        if nombre not in self.presets:
            self.vista.mostrar_error_preset_vacio(nombre)
            return

        horas, emp, energia, coef, maq = self.presets[nombre]
        self.vista.cargar_datos(
            horas=horas,
            empleados=emp,
            energia=energia,
            coef_perdida=coef,
            tipo_maquinaria=maq
        )
        self.cargar_parametros()
        self.vista.mostrar_mensaje_preset_cargado(nombre)
