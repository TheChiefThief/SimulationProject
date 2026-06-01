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
from core.logger import registrar_error
from core.parametros import ParametrosSistema
from core.validador import Validador
from gui.componentes import CTKLabeledEntry


class VistaGerente(ctk.CTkFrame):
    """
    Frame que encapsula la Vista del Gerente/Administrador.
    Se monta dentro del CTkTabview de la ventana principal.
    """

    def __init__(self, parent, params: ParametrosSistema,
                 callback_parametros_cargados=None):
        """
        Args:
            parent:                       Widget padre (el tab del tabview).
            params:                       Objeto de parámetros compartido.
            callback_parametros_cargados: Función a llamar cuando los
                                          parámetros se cargan exitosamente,
                                          para notificar a otras vistas.
        """
        super().__init__(parent, fg_color="transparent")
        self.params = params
        self.callback = callback_parametros_cargados
        self.presets = {}  # Almacena los presets de la sesión actual

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_panel_izquierdo()
        self._construir_panel_derecho()

        # Precargar los parámetros automáticamente al inicio
        # usando los valores por defecto de params.operativo
        self._cargar_parametros()

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

        # ── Acciones (Guardar, Defaults) ───────────────────────────────
        acciones_frame = ctk.CTkFrame(frame, fg_color="transparent")
        acciones_frame.pack(anchor="w", pady=(15, 5))

        self.btn_guardar = ctk.CTkButton(
            acciones_frame, text="💾  Cargar Parámetros",
            width=150, font=("Azeri Sans", 13, "bold"),
            command=self._cargar_parametros
        )
        self.btn_guardar.pack(side="left", padx=(0, 10))

        self.btn_defaults = ctk.CTkButton(
            acciones_frame, text="🔄  Valores Base",
            width=130, font=("Azeri Sans", 13), fg_color="#F57C00", hover_color="#EF6C00",
            command=self._cargar_valores_por_defecto
        )
        self.btn_defaults.pack(side="left")

        # ── Presets ───────────────────────────────────────────────────
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
            command=self._guardar_preset
        )
        self.btn_guardar_preset.pack(side="left", padx=(0, 10))

        self.btn_cargar_preset = ctk.CTkButton(
            presets_frame, text="Cargar Preset", width=100, font=("Azeri Sans", 12),
            fg_color="#29B6F6", hover_color="#0288D1", text_color="#111111",
            command=self._cargar_preset
        )
        self.btn_cargar_preset.pack(side="left")

        # Etiqueta de error
        self.lbl_error = ctk.CTkLabel(
            frame, text="", font=("Azeri Sans", 12),
            text_color="#EF5350", wraplength=300
        )
        self.lbl_error.pack(anchor="w", pady=(10, 0))

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

        # Resultados de indicadores (se llenan tras ejecutar)
        ctk.CTkLabel(frame, text="Indicadores de Productividad:",
                     font=("Azeri Sans", 14, "bold"),
                     text_color="#AAAAAA").pack(anchor="w", pady=(0, 10))

        indicadores = [
            ("Coef. Productividad", "coef_prod"),
            ("Eficacia",            "eficacia"),
            ("Eficiencia",          "eficiencia"),
            ("Rango de Mejora",     "rango_mejora"),
        ]
        self._entries_indicadores = {}
        for etiqueta, key in indicadores:
            labeled_entry = CTKLabeledEntry(
                frame, label_text=etiqueta, width=240
            )
            labeled_entry.configure_entry(state="readonly")
            labeled_entry.pack(anchor="w", pady=(2, 5))
            self._entries_indicadores[key] = labeled_entry

    def _cargar_parametros(self):
        """Valida todos los campos y carga los parámetros en el sistema."""
        self.lbl_error.configure(text="")

        try:
            # ── Validar: Horas de trabajo ──────────────────────────────────
            # Se limita de 0.1 a 8.0 según requerimiento del profesor ("como maximo 8 horas")
            horas = Validador.validar_float(
                self.in_horas.get(), "Horas de trabajo por jornada", min_valor=0.1, max_valor=8.0
            )

            # ── Validar: Cantidad de empleados ─────────────────────────────
            empleados = Validador.validar_entero(
                self.in_empleados.get(), "Cantidad de empleados", min_valor=1, max_valor=1000
            )

            # ── Validar: Energía consumida ─────────────────────────────────
            energia = Validador.validar_float(
                self.in_energia.get(), "Energía consumida (kWh)", min_valor=0.0, max_valor=100000.0
            )

            # ── Validar: Coeficiente de pérdida ───────────────────────────
            coef = Validador.validar_fraccion(
                self.in_coef_perdida.get(), "Coeficiente de pérdida"
            )

        except ValueError as e:
            # registros de errores
            registrar_error("Error de validación de parámetros operativos en VistaGerente", e)
            mensaje_error = str(e)
            self.lbl_error.configure(text=f"⚠ {mensaje_error}")
            messagebox.showerror("Error de Operación", mensaje_error)
            return

        # ── Aplicar parámetros al objeto compartido ────────────────────
        self.params.operativo.horas_trabajo = horas
        self.params.operativo.cantidad_empleados = empleados
        self.params.operativo.energia_consumida = energia
        self.params.operativo.coeficiente_perdida = coef
        self.params.operativo.tipo_maquinaria = self.opt_maquinaria.get()
        self.params.parametros_cargados = True

        # ── Actualizar indicador visual ────────────────────────────────
        self.lbl_indicador.configure(
            text="✔  Parámetros cargados correctamente",
            text_color="#66BB6A"
        )

        # Resumen textual de lo cargado
        resumen = (
            f"• Horas de trabajo: {horas:.1f} h\n"
            f"• Empleados: {empleados}\n"
            f"• Energía: {energia:.1f} kWh\n"
            f"• Coef. pérdida: {coef:.3f}\n"
            f"• Maquinaria: {self.params.operativo.tipo_maquinaria}"
        )
        self.lbl_resumen.configure(text=resumen, text_color="#E0E0E0")

        # Notificar a otras vistas (ej: VistaUsuario actualiza su indicador)
        if self.callback:
            self.callback()

    # ------------------------------------------------------------------
    # Presets y Valores por Defecto
    # ------------------------------------------------------------------

    def _cargar_valores_por_defecto(self):
        """Restaura los valores iniciales predeterminados (hardcodeados o desde params defaults)."""
        self.in_horas.delete(0, "end")
        self.in_horas.insert(0, "8.0")
        
        self.in_empleados.delete(0, "end")
        self.in_empleados.insert(0, "5")
        
        self.in_energia.delete(0, "end")
        self.in_energia.insert(0, "100.0")
        
        self.in_coef_perdida.delete(0, "end")
        self.in_coef_perdida.insert(0, "0.05")
        
        self.opt_maquinaria.set("Proceso Manual")
        self._cargar_parametros()
        messagebox.showinfo("Valores Base", "Se han restaurado los valores por defecto del sistema.")

    def _guardar_preset(self):
        """Guarda la configuración actual de entradas en el slot seleccionado."""
        nombre = self.combo_presets.get()
        self.presets[nombre] = (
            self.in_horas.get(),
            self.in_empleados.get(),
            self.in_energia.get(),
            self.in_coef_perdida.get(),
            self.opt_maquinaria.get()
        )
        messagebox.showinfo("Preset Guardado", f"Se guardaron los valores actuales en '{nombre}'.")

    def _cargar_preset(self):
        """Carga en los campos la configuración guardada en el slot seleccionado."""
        nombre = self.combo_presets.get()
        if nombre not in self.presets:
            messagebox.showwarning("Preset Vacío", f"El '{nombre}' no tiene valores guardados.\nGuarde uno primero.")
            return
            
        horas, emp, energia, coef, maq = self.presets[nombre]
        
        self.in_horas.delete(0, "end")
        self.in_horas.insert(0, horas)
        
        self.in_empleados.delete(0, "end")
        self.in_empleados.insert(0, emp)
        
        self.in_energia.delete(0, "end")
        self.in_energia.insert(0, energia)
        
        self.in_coef_perdida.delete(0, "end")
        self.in_coef_perdida.insert(0, coef)
        
        self.opt_maquinaria.set(maq)
        self._cargar_parametros()
        messagebox.showinfo("Preset Cargado", f"Se cargaron correctamente los valores de '{nombre}'.")
