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
from core.parametros import ParametrosSistema


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

        self._campos = {}  # dict[nombre_param] -> CTkEntry
        self._construir_columnas()
        self._construir_pie()

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------

    def _construir_columnas(self):
        """Construye las tres columnas de parámetros configurables."""
        # ── Columna 1: Precios ─────────────────────────────────────────
        col1 = ctk.CTkFrame(self, fg_color="transparent")
        col1.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        ctk.CTkLabel(col1, text="Precios de Referencia",
                     font=("Arial", 16, "bold")).pack(pady=(0, 5))
        ctk.CTkLabel(col1, text="(ARS por kg o unidad)",
                     font=("Arial", 11), text_color="#888888").pack(pady=(0, 15))

        precios = [
            ("Oro ($/kg)",              "precio_oro",              self.params.precio_oro),
            ("Vidrio ($/kg)",           "precio_vidrio",           self.params.precio_vidrio),
            ("Lentes ($/unidad)",       "precio_lentes",           self.params.precio_lentes),
            ("Cobre ($/kg)",            "precio_cobre",            self.params.precio_cobre),
            ("Aluminio ($/kg)",         "precio_aluminio",         self.params.precio_aluminio),
            ("Plástico ($/kg)",         "precio_plastico",         self.params.precio_plastico),
            ("Almacenamiento mín $/GB", "precio_almacenamiento_min", self.params.precio_almacenamiento_min),
            ("Almacenamiento máx $/GB", "precio_almacenamiento_max", self.params.precio_almacenamiento_max),
        ]
        for etiqueta, key, valor in precios:
            self._campo(col1, etiqueta, key, valor)

        # ── Columna 2: Tasas y rendimientos ───────────────────────────
        col2 = ctk.CTkFrame(self, fg_color="transparent")
        col2.grid(row=0, column=1, padx=20, pady=20, sticky="n")

        ctk.CTkLabel(col2, text="Tasas de Recuperación",
                     font=("Arial", 16, "bold")).pack(pady=(0, 5))
        ctk.CTkLabel(col2, text="(Fracción entre 0.0 y 1.0)",
                     font=("Arial", 11), text_color="#888888").pack(pady=(0, 15))

        tasas = [
            ("Placas sanas",   "tasa_placas_sanas",  self.params.tasa_placas_sanas),
            ("Ópticas sanas",  "tasa_opticas_sanas", self.params.tasa_opticas_sanas),
            ("Discos sanos",   "tasa_discos_sanos",  self.params.tasa_discos_sanos),
        ]
        for etiqueta, key, valor in tasas:
            self._campo(col2, etiqueta, key, valor)

        ctk.CTkLabel(col2, text="Rendimientos de Materiales",
                     font=("Arial", 16, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(col2, text="(Fracción entre 0.0 y 1.0)",
                     font=("Arial", 11), text_color="#888888").pack(pady=(0, 15))

        rendimientos = [
            ("Rendimiento Plástico", "rendimiento_plastico", self.params.rendimiento_plastico),
            ("Rendimiento Metal",    "rendimiento_metal",    self.params.rendimiento_metal),
        ]
        for etiqueta, key, valor in rendimientos:
            self._campo(col2, etiqueta, key, valor)

        # ── Columna 3: Composición de materiales ──────────────────────
        col3 = ctk.CTkFrame(self, fg_color="transparent")
        col3.grid(row=0, column=2, padx=20, pady=20, sticky="n")

        ctk.CTkLabel(col3, text="Composición de Dispositivos",
                     font=("Arial", 16, "bold")).pack(pady=(0, 5))
        ctk.CTkLabel(col3, text="(Fracción del peso total, suma ≈ 1)",
                     font=("Arial", 11), text_color="#888888").pack(pady=(0, 15))

        composicion = [
            ("Cámara — Plástico",  "camara_fraccion_plastico", self.params.camara_fraccion_plastico),
            ("Cámara — Placas",    "camara_fraccion_placas",   self.params.camara_fraccion_placas),
            ("Cámara — Metal",     "camara_fraccion_metal",    self.params.camara_fraccion_metal),
            ("Cámara — Ópticos",   "camara_fraccion_opticos",  self.params.camara_fraccion_opticos),
            ("DVR — HDD",          "dvr_fraccion_hdd",         self.params.dvr_fraccion_hdd),
            ("DVR — Metal",        "dvr_fraccion_metal",       self.params.dvr_fraccion_metal),
            ("DVR — Placas",       "dvr_fraccion_placas",      self.params.dvr_fraccion_placas),
        ]
        for etiqueta, key, valor in composicion:
            self._campo(col3, etiqueta, key, valor)

    def _campo(self, parent, etiqueta: str, key: str, valor_inicial: float):
        """Crea un label + entry y lo registra en self._campos."""
        ctk.CTkLabel(parent, text=etiqueta, font=("Arial", 13)).pack(anchor="w")
        entry = ctk.CTkEntry(parent, width=200, font=("Arial", 13))
        entry.pack(anchor="w", pady=(2, 12))
        entry.insert(0, str(valor_inicial))
        self._campos[key] = entry

    def _construir_pie(self):
        """Fila inferior con botón guardar y mensaje de estado."""
        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.grid(row=1, column=0, columnspan=3, pady=(0, 20))

        self.btn_guardar = ctk.CTkButton(
            pie, text="💾  Guardar Configuración",
            width=220, font=("Arial", 14, "bold"),
            command=self._guardar
        )
        self.btn_guardar.pack(side="left", padx=20)

        self.lbl_estado = ctk.CTkLabel(pie, text="", font=("Arial", 13))
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

        for key, entry in self._campos.items():
            texto = entry.get().strip()

            # No vacío
            if not texto:
                self.lbl_estado.configure(
                    text=f"⚠ El campo '{key}' no puede estar vacío.",
                    text_color="#EF5350"
                )
                return

            # Tipo numérico
            try:
                valor = float(texto)
            except ValueError:
                self.lbl_estado.configure(
                    text=f"⚠ '{key}' debe ser un número (recibido: '{texto}').",
                    text_color="#EF5350"
                )
                return

            # No negativo
            if valor < 0:
                self.lbl_estado.configure(
                    text=f"⚠ '{key}' no puede ser negativo.",
                    text_color="#EF5350"
                )
                return

            # Rango [0, 1] para fracciones
            if key in self._FRACCIONES_KEYS and not (0.0 <= valor <= 1.0):
                self.lbl_estado.configure(
                    text=f"⚠ '{key}' debe estar entre 0.0 y 1.0.",
                    text_color="#EF5350"
                )
                return

            # Precios > 0
            if key in self._PRECIOS_KEYS and valor == 0:
                self.lbl_estado.configure(
                    text=f"⚠ El precio '{key}' debe ser mayor a 0.",
                    text_color="#EF5350"
                )
                return

            valores[key] = valor

        # Validar precio min ≤ precio max de almacenamiento
        if valores.get("precio_almacenamiento_min", 0) > valores.get("precio_almacenamiento_max", 0):
            self.lbl_estado.configure(
                text="⚠ El precio mínimo de almacenamiento no puede superar al máximo.",
                text_color="#EF5350"
            )
            return

        # Aplicar todos los valores al objeto params
        for key, valor in valores.items():
            setattr(self.params, key, valor)

        self.lbl_estado.configure(
            text="✔  Configuración guardada correctamente.",
            text_color="#66BB6A"
        )

        if self.callback:
            self.callback()
