"""
gui/vista_config.py
--------------------
Tab "Vista de Configuración" de la aplicación.

Permite al administrador editar todos los parámetros del sistema:
  - Precios de referencia (ARS/kg o ARS/unidad)
  - Tasas de recuperación por componente
  - Rendimientos de materiales base
  - Coeficiente de pérdida general

Al guardar, los valores se escriben en el objeto ParametrosSistema
compartido. Todos los campos tienen validación:
  - No vacíos
  - Números positivos o no negativos según el campo
  - Rangos lógicos (fracciones entre 0 y 1, precios > 0)
"""

import customtkinter as ctk
from tkinter import messagebox
from core.parametros import ParametrosSistema
from gui.componentes import CTKLabeledEntry
from gui.controllers.config_controller import ConfigController


class VistaConfig(ctk.CTkFrame):
    """
    Frame que encapsula la Vista de Configuración del sistema.
    Se monta dentro del CTkTabview de la ventana principal.
    """

    def __init__(self, parent, params: ParametrosSistema):
        """
        Args:
            parent:                  Widget padre.
            params:                  Objeto de parámetros compartido.
        """
        super().__init__(parent, fg_color="transparent")
        self.params = params
        self.controlador = ConfigController(self.params, self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Contenedor scrollable para las columnas de configuración
        self.scroll_contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_contenedor.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.scroll_contenedor.grid_columnconfigure(0, weight=1)
        self.scroll_contenedor.grid_columnconfigure(1, weight=1)
        self.scroll_contenedor.grid_columnconfigure(2, weight=1)

        self._campos = {}  # dict[nombre_param] -> CTkEntry
        self._construir_columnas()
        self._construir_pie()

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------

    def _construir_columnas(self):
        """Construye las tres columnas de parámetros configurables."""
        # ── Columna 1: Precios ─────────────────────────────────────────
        col1 = ctk.CTkFrame(self.scroll_contenedor, fg_color="transparent")
        col1.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        ctk.CTkLabel(col1, text="Precios de Referencia",
                     font=("Azeri Sans", 20, "bold")).pack(pady=(0, 5))
        ctk.CTkLabel(col1, text="(ARS por kg o unidad)",
                     font=("Azeri Sans", 11), text_color="#888888").pack(pady=(0, 15))

        precios = [
            ("Oro ($/kg)",              "precio_oro",              self.params.precios.precio_oro),
            ("Vidrio ($/kg)",           "precio_vidrio",           self.params.precios.precio_vidrio),
            ("Lentes ($/unidad)",       "precio_lentes",           self.params.precios.precio_lentes),
            ("Cobre ($/kg)",            "precio_cobre",            self.params.precios.precio_cobre),
            ("Aluminio ($/kg)",         "precio_aluminio",         self.params.precios.precio_aluminio),
            ("Plástico ($/kg)",         "precio_plastico",         self.params.precios.precio_plastico),
            ("Almacenamiento mín $/GB", "precio_almacenamiento_min", self.params.precios.precio_almacenamiento_min),
            ("Almacenamiento máx $/GB", "precio_almacenamiento_max", self.params.precios.precio_almacenamiento_max),
        ]
        for etiqueta, key, valor in precios:
            self._campo(col1, etiqueta, key, valor)

        # ── Columna 2: Tasas y rendimientos ───────────────────────────
        col2 = ctk.CTkFrame(self.scroll_contenedor, fg_color="transparent")
        col2.grid(row=0, column=1, padx=20, pady=20, sticky="n")

        ctk.CTkLabel(col2, text="Tasas de Recuperación",
                     font=("Azeri Sans", 20, "bold")).pack(pady=(0, 5))
        ctk.CTkLabel(col2, text="(Fracción entre 0.0 y 1.0)",
                     font=("Azeri Sans", 11), text_color="#888888").pack(pady=(0, 15))

        tasas = [
            ("Placas sanas",   "tasa_placas_sanas",  self.params.tasas.tasa_placas_sanas),
            ("Ópticas sanas",  "tasa_opticas_sanas", self.params.tasas.tasa_opticas_sanas),
            ("Discos sanos",   "tasa_discos_sanos",  self.params.tasas.tasa_discos_sanos),
        ]
        for etiqueta, key, valor in tasas:
            self._campo(col2, etiqueta, key, valor)

        ctk.CTkLabel(col2, text="Rendimientos de Materiales",
                     font=("Azeri Sans", 20, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(col2, text="(Fracción entre 0.0 y 1.0)",
                     font=("Azeri Sans", 11), text_color="#888888").pack(pady=(0, 15))

        rendimientos = [
            ("Rendimiento Plástico", "rendimiento_plastico", self.params.composicion.rendimiento_plastico),
            ("Rendimiento Metal",    "rendimiento_metal",    self.params.composicion.rendimiento_metal),
        ]
        for etiqueta, key, valor in rendimientos:
            self._campo(col2, etiqueta, key, valor)

        # ── Columna 3: Composición de materiales ──────────────────────
        col3 = ctk.CTkFrame(self.scroll_contenedor, fg_color="transparent")
        col3.grid(row=0, column=2, padx=20, pady=20, sticky="n")

        ctk.CTkLabel(col3, text="Composición de Dispositivos",
                     font=("Azeri Sans", 20, "bold")).pack(pady=(0, 5))
        ctk.CTkLabel(col3, text="(Fracción del peso total, suma ≈ 1)",
                     font=("Azeri Sans", 11), text_color="#888888").pack(pady=(0, 15))

        composicion = [
            ("Cámara — Plástico",  "camara_fraccion_plastico", self.params.composicion.camara_fraccion_plastico),
            ("Cámara — Placas",    "camara_fraccion_placas",   self.params.composicion.camara_fraccion_placas),
            ("Cámara — Metal",     "camara_fraccion_metal",    self.params.composicion.camara_fraccion_metal),
            ("Cámara — Ópticos",   "camara_fraccion_opticos",  self.params.composicion.camara_fraccion_opticos),
            ("DVR — HDD",          "dvr_fraccion_hdd",         self.params.composicion.dvr_fraccion_hdd),
            ("DVR — Metal",        "dvr_fraccion_metal",       self.params.composicion.dvr_fraccion_metal),
            ("DVR — Placas",       "dvr_fraccion_placas",      self.params.composicion.dvr_fraccion_placas),
        ]
        for etiqueta, key, valor in composicion:
            self._campo(col3, etiqueta, key, valor)

    def _campo(self, parent, etiqueta: str, key: str, valor_inicial: float):
        """Crea un label + entry y lo registra en self._campos."""
        labeled_entry = CTKLabeledEntry(
            parent, label_text=etiqueta, width=200, default_value=valor_inicial
        )
        labeled_entry.pack(anchor="w", pady=(2, 5))
        self._campos[key] = labeled_entry

    def _construir_pie(self):
        """Fila inferior con botón guardar y mensaje de estado."""
        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.grid(row=1, column=0, columnspan=3, pady=(0, 20))

        self.btn_guardar = ctk.CTkButton(
            pie, text="💾  Guardar Configuración",
            width=220, font=("Azeri Sans", 14, "bold"),
            command=self.controlador.guardar
        )
        self.btn_guardar.pack(side="left", padx=20)

        self.lbl_estado = ctk.CTkLabel(pie, text="", font=("Azeri Sans", 13))
        self.lbl_estado.pack(side="left", padx=10)

    # ------------------------------------------------------------------
    # Métodos expuestos para el controlador (MVC)
    # ------------------------------------------------------------------

    def obtener_datos(self) -> dict:
        """Retorna un diccionario con los valores de texto de cada campo."""
        return {key: entry.get() for key, entry in self._campos.items()}

    def limpiar_estado(self):
        """Limpia el mensaje de estado inferior."""
        self.lbl_estado.configure(text="")

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error en el label de estado y un popup."""
        self.lbl_estado.configure(
            text=f"⚠ {mensaje}",
            text_color="#EF5350"
        )
        self.after(3000, self.limpiar_estado)
        messagebox.showwarning("Aviso de Configuración", mensaje)

    def mostrar_exito(self, mensaje: str):
        """Muestra un mensaje de éxito en el label de estado."""
        self.lbl_estado.configure(
            text=f"✔  {mensaje}",
            text_color="#66BB6A"
        )


