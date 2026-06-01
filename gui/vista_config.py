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
from core.logger import registrar_error
from core.parametros import ParametrosSistema
from core.validador import Validador
from gui.componentes import CTKLabeledEntry


class VistaConfig(ctk.CTkFrame):
    """
    Frame que encapsula la Vista de Configuración del sistema.
    Se monta dentro del CTkTabview de la ventana principal.
    """

    def __init__(self, parent, params: ParametrosSistema,
                 callback_config_guardada=None):
        """
        Args:
            parent:                  Widget padre.
            params:                  Objeto de parámetros compartido.
            callback_config_guardada: Función opcional a llamar al guardar.
        """
        super().__init__(parent, fg_color="transparent")
        self.params = params
        self.callback = callback_config_guardada

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
            command=self._guardar
        )
        self.btn_guardar.pack(side="left", padx=20)

        self.lbl_estado = ctk.CTkLabel(pie, text="", font=("Azeri Sans", 13))
        self.lbl_estado.pack(side="left", padx=10)

    # ------------------------------------------------------------------
    # Lógica de guardado y validación
    # ------------------------------------------------------------------

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

    def _guardar(self):
        """Valida todos los campos y guarda los valores en el objeto params."""
        self.lbl_estado.configure(text="")
        valores = {}

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

        try:
            for key, entry in self._campos.items():
                texto = entry.get()
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
            # registros de errores
            registrar_error("Error de validación de configuración en VistaConfig", e)
            mensaje_error = str(e)
            self.lbl_estado.configure(
                text=f"⚠ {mensaje_error}",
                text_color="#EF5350"
            )
            messagebox.showerror("Error de Configuración", mensaje_error)
            return

        # Aplicar todos los valores al objeto params
        for key, valor in valores.items():
            if key in self._PRECIOS_KEYS:
                setattr(self.params.precios, key, valor)
            elif key in {"tasa_placas_sanas", "tasa_opticas_sanas", "tasa_discos_sanos"}:
                setattr(self.params.tasas, key, valor)
            else:
                setattr(self.params.composicion, key, valor)

        self.lbl_estado.configure(
            text="✔  Configuración guardada correctamente.",
            text_color="#66BB6A"
        )

        if self.callback:
            self.callback()
