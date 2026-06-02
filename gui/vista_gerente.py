"""
gui/vista_gerente.py
---------------------
Tab "Vista del Gerente" de la aplicación.

Permite al administrador cargar los parámetros operativos del proceso
(horas de trabajo, empleados, energía, coeficiente de pérdida, tipo
de maquinaria) con validaciones exhaustivas.

El sistema NO permite ejecutar simulaciones hasta que estos parámetros
sean cargados y validados correctamente.

Validaciones implementadas:
  - No vacío: todos los campos son obligatorios
  - Tipo de dato: rechaza letras donde van números
  - No negatividad: horas, empleados y energía deben ser > 0
  - Rango: coeficiente de pérdida entre 0.0 y 1.0 (inclusive)

Al guardar exitosamente, se activa params.parametros_cargados = True
y se notifica a todas las vistas dependientes.
"""

import customtkinter as ctk
from tkinter import messagebox
from core.parametros import ParametrosSistema
from gui.componentes import CTKLabeledEntry
from gui.controllers.gerente_controller import GerenteController


class VistaGerente(ctk.CTkFrame):
    """
    Frame que encapsula la Vista del Gerente/Administrador.
    Se monta dentro del CTkTabview de la ventana principal.
    """

    def __init__(self, parent, params: ParametrosSistema):
        """
        Args:
            parent:                       Widget padre (el tab del tabview).
            params:                       Objeto de parámetros compartido.
        """
        super().__init__(parent, fg_color="transparent")
        self.params = params
        self.controlador = GerenteController(self.params, self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_panel_izquierdo()
        self._construir_panel_derecho()

        # Precargar los parámetros automáticamente al inicio
        # usando los valores por defecto de params.operativo
        self.controlador.cargar_parametros()

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------

    def _construir_panel_izquierdo(self):
        """Panel de carga de parámetros operativos con validaciones."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(frame, text="Parámetros Operativos",
                     font=("Azeri Sans", 26, "bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            frame,
            text="Debe cargar estos parámetros antes de ejecutar la simulación.",
            font=("Azeri Sans", 12), text_color="#AAAAAA", wraplength=320
        ).pack(anchor="w", pady=(0, 20))

        # ── Campo: Horas de trabajo ────────────────────────────────────
        self.in_horas = CTKLabeledEntry(
            frame, label_text="Horas de trabajo por jornada *",
            placeholder_text="Ej: 8  (número > 0)",
            default_value=self.params.operativo.horas_trabajo
        )
        self.in_horas.pack(anchor="w", pady=(2, 5))

        # ── Campo: Cantidad de empleados ───────────────────────────────
        self.in_empleados = CTKLabeledEntry(
            frame, label_text="Cantidad de empleados *",
            placeholder_text="Ej: 5  (entero > 0)",
            default_value=self.params.operativo.cantidad_empleados
        )
        self.in_empleados.pack(anchor="w", pady=(2, 5))

        # ── Campo: Energía consumida ───────────────────────────────────
        self.in_energia = CTKLabeledEntry(
            frame, label_text="Energía consumida (kWh) *",
            placeholder_text="Ej: 100  (número ≥ 0)",
            default_value=self.params.operativo.energia_consumida
        )
        self.in_energia.pack(anchor="w", pady=(2, 5))

        # ── Campo: Coeficiente de pérdida ──────────────────────────────
        self.in_coef_perdida = CTKLabeledEntry(
            frame, label_text="Coeficiente de pérdida del proceso *",
            hint_text="Fracción entre 0.0 (sin pérdida) y 1.0 (pérdida total)",
            placeholder_text="Ej: 0.05",
            default_value=self.params.operativo.coeficiente_perdida
        )
        self.in_coef_perdida.pack(anchor="w", pady=(2, 5))

        # ── Campo: Tipo de maquinaria ──────────────────────────────────
        ctk.CTkLabel(frame, text="Tipo de maquinaria *",
                     font=("Azeri Sans", 13)).pack(anchor="w")
        self.opt_maquinaria = ctk.CTkOptionMenu(
            frame,
            values=["Proceso Manual", "Línea Automatizada", "Híbrido"],
            width=280,
            font=("Azeri Sans", 13)
        )
        self.opt_maquinaria.pack(anchor="w", pady=(2, 25))
        self.opt_maquinaria.set(self.params.operativo.tipo_maquinaria)

        # Nota de campos obligatorios
        ctk.CTkLabel(frame, text="* Campos obligatorios",
                     font=("Azeri Sans", 11), text_color="#888888").pack(anchor="w", pady=(0, 10))



    def _construir_panel_derecho(self):
        """Panel de estado y resultados de eficiencia operativa."""
        frame_outer = ctk.CTkFrame(self, fg_color="#1a2530", corner_radius=10)
        frame_outer.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        frame = ctk.CTkFrame(frame_outer, fg_color="transparent")
        frame.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Estado del Sistema",
                     font=("Azeri Sans", 22, "bold")).pack(anchor="w", pady=(0, 20))

        # Indicador de estado principal
        self.lbl_indicador = ctk.CTkLabel(
            frame,
            text="✔  Usando valores por defecto",
            font=("Azeri Sans", 16, "bold"),
            text_color="#66BB6A"
        )
        self.lbl_indicador.pack(anchor="w", pady=(0, 15))

        sep = ctk.CTkFrame(frame, height=1, fg_color="#2c3e50")
        sep.pack(fill="x", pady=(0, 20))

        # Resumen de parámetros cargados
        ctk.CTkLabel(frame, text="Parámetros Cargados:",
                     font=("Azeri Sans", 14, "bold"),
                     text_color="#AAAAAA").pack(anchor="w", pady=(0, 10))

        self.lbl_resumen = ctk.CTkLabel(
            frame,
            text="—",
            font=("Azeri Sans", 13),
            text_color="#888888",
            justify="left",
            wraplength=280
        )
        self.lbl_resumen.pack(anchor="w")

        sep2 = ctk.CTkFrame(frame, height=1, fg_color="#2c3e50")
        sep2.pack(fill="x", pady=(20, 15))

        # Acciones de Carga de Parámetros
        ctk.CTkLabel(frame, text="Acciones:",
                     font=("Azeri Sans", 14, "bold"),
                     text_color="#AAAAAA").pack(anchor="w", pady=(0, 10))

        acciones_frame = ctk.CTkFrame(frame, fg_color="transparent")
        acciones_frame.pack(anchor="w", pady=(5, 5))

        self.btn_guardar = ctk.CTkButton(
            acciones_frame, text="💾  Cargar Parámetros",
            width=150, font=("Azeri Sans", 13, "bold"),
            command=self.controlador.cargar_parametros
        )
        self.btn_guardar.pack(side="left", padx=(0, 10))

        self.btn_defaults = ctk.CTkButton(
            acciones_frame, text="🔄  Valores Base",
            width=130, font=("Azeri Sans", 13), fg_color="#F57C00", hover_color="#EF6C00",
            command=self.controlador.cargar_valores_base
        )
        self.btn_defaults.pack(side="left")

        # Configuración de Presets
        ctk.CTkLabel(frame, text="Presets del Sistema:",
                     font=("Azeri Sans", 14, "bold"),
                     text_color="#AAAAAA").pack(anchor="w", pady=(15, 10))

        presets_frame = ctk.CTkFrame(frame, fg_color="transparent")
        presets_frame.pack(anchor="w", pady=(5, 10))

        self.combo_presets = ctk.CTkOptionMenu(
            presets_frame, values=["Preset 1", "Preset 2", "Preset 3"], width=110,
            font=("Azeri Sans", 12)
        )
        self.combo_presets.pack(side="left", padx=(0, 10))

        self.btn_guardar_preset = ctk.CTkButton(
            presets_frame, text="Guardar Preset", width=100, font=("Azeri Sans", 12),
            fg_color="#4DB6AC", hover_color="#009688", text_color="#111111",
            command=self.controlador.guardar_preset
        )
        self.btn_guardar_preset.pack(side="left", padx=(0, 10))

        self.btn_cargar_preset = ctk.CTkButton(
            presets_frame, text="Cargar Preset", width=100, font=("Azeri Sans", 12),
            fg_color="#29B6F6", hover_color="#0288D1", text_color="#111111",
            command=self.controlador.cargar_preset
        )
        self.btn_cargar_preset.pack(side="left")

        # Etiqueta de error
        self.lbl_error = ctk.CTkLabel(
            frame, text="", font=("Azeri Sans", 12),
            text_color="#EF5350", wraplength=280
        )
        self.lbl_error.pack(anchor="w", pady=(10, 0))

    # ------------------------------------------------------------------
    # Métodos expuestos para el controlador (MVC)
    # ------------------------------------------------------------------

    def obtener_datos(self) -> dict:
        """Retorna un diccionario con los valores de texto de cada campo."""
        return {
            "horas": self.in_horas.get(),
            "empleados": self.in_empleados.get(),
            "energia": self.in_energia.get(),
            "coef_perdida": self.in_coef_perdida.get(),
            "tipo_maquinaria": self.opt_maquinaria.get()
        }

    def limpiar_error(self):
        """Limpia el mensaje de error."""
        self.lbl_error.configure(text="")

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error y un popup."""
        self.lbl_error.configure(text=f"⚠ {mensaje}")
        self.after(3000, self.limpiar_error)
        messagebox.showwarning("Aviso de Operación", mensaje)

    def mostrar_exito(self, mensaje: str, horas, empleados, energia, tipo_maquinaria, coef):
        """Actualiza el indicador visual y muestra el resumen de carga exitosa."""
        self.lbl_indicador.configure(
            text=f"✔  {mensaje}",
            text_color="#66BB6A"
        )
        resumen = (
            f"• Horas de trabajo: {horas:.1f} h\n"
            f"• Empleados: {empleados}\n"
            f"• Energía: {energia:.1f} kWh\n"
            f"• Coef. pérdida: {coef:.3f}\n"
            f"• Maquinaria: {tipo_maquinaria}"
        )
        self.lbl_resumen.configure(text=resumen, text_color="#E0E0E0")

    def cargar_datos(self, horas, empleados, energia, coef_perdida, tipo_maquinaria):
        """Carga valores en los campos de entrada de la UI."""
        self.in_horas.delete(0, "end")
        self.in_horas.insert(0, horas)
        
        self.in_empleados.delete(0, "end")
        self.in_empleados.insert(0, empleados)
        
        self.in_energia.delete(0, "end")
        self.in_energia.insert(0, energia)
        
        self.in_coef_perdida.delete(0, "end")
        self.in_coef_perdida.insert(0, coef_perdida)
        
        self.opt_maquinaria.set(tipo_maquinaria)

    def obtener_preset_seleccionado(self) -> str:
        """Devuelve el nombre del preset actualmente seleccionado."""
        return self.combo_presets.get()

    def mostrar_mensaje_valores_base(self):
        """Muestra popup de restauración de valores base."""
        messagebox.showinfo("Valores Base", "Se han restaurado los valores por defecto del sistema.")

    def mostrar_mensaje_preset_guardado(self, nombre: str):
        """Muestra popup de preset guardado."""
        messagebox.showinfo("Preset Guardado", f"Se guardaron los valores actuales en '{nombre}'.")

    def mostrar_mensaje_preset_cargado(self, nombre: str):
        """Muestra popup de preset cargado."""
        messagebox.showinfo("Preset Cargado", f"Se cargaron correctamente los valores de '{nombre}'.")

    def mostrar_error_preset_vacio(self, nombre: str):
        """Muestra popup indicando que el preset seleccionado está vacío."""
        messagebox.showwarning("Preset Vacío", f"El '{nombre}' no tiene valores guardados.\nGuarde uno primero.")
