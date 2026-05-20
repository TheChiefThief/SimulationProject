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

from core.parametros import ParametrosSistema


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

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_panel_izquierdo()
        self._construir_panel_derecho()

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------

    def _construir_panel_izquierdo(self):
        """Panel de carga de parámetros operativos con validaciones."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(frame, text="Parámetros Operativos",
                     font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            frame,
            text="Debe cargar estos parámetros antes de ejecutar la simulación.",
            font=("Arial", 12), text_color="#AAAAAA", wraplength=320
        ).pack(anchor="w", pady=(0, 20))

        # ── Campo: Horas de trabajo ────────────────────────────────────
        ctk.CTkLabel(frame, text="Horas de trabajo por jornada *",
                     font=("Arial", 13)).pack(anchor="w")
        self.in_horas = ctk.CTkEntry(frame, width=280,
                                     placeholder_text="Ej: 8  (número > 0)")
        self.in_horas.pack(anchor="w", pady=(2, 14))
        self.in_horas.insert(0, str(self.params.horas_trabajo))

        # ── Campo: Cantidad de empleados ───────────────────────────────
        ctk.CTkLabel(frame, text="Cantidad de empleados *",
                     font=("Arial", 13)).pack(anchor="w")
        self.in_empleados = ctk.CTkEntry(frame, width=280,
                                         placeholder_text="Ej: 5  (entero > 0)")
        self.in_empleados.pack(anchor="w", pady=(2, 14))
        self.in_empleados.insert(0, str(self.params.cantidad_empleados))

        # ── Campo: Energía consumida ───────────────────────────────────
        ctk.CTkLabel(frame, text="Energía consumida (kWh) *",
                     font=("Arial", 13)).pack(anchor="w")
        self.in_energia = ctk.CTkEntry(frame, width=280,
                                       placeholder_text="Ej: 100  (número ≥ 0)")
        self.in_energia.pack(anchor="w", pady=(2, 14))
        self.in_energia.insert(0, str(self.params.energia_consumida))

        # ── Campo: Coeficiente de pérdida ──────────────────────────────
        ctk.CTkLabel(frame, text="Coeficiente de pérdida del proceso *",
                     font=("Arial", 13)).pack(anchor="w")
        ctk.CTkLabel(frame, text="Fracción entre 0.0 (sin pérdida) y 1.0 (pérdida total)",
                     font=("Arial", 11), text_color="#888888").pack(anchor="w")
        self.in_coef_perdida = ctk.CTkEntry(frame, width=280,
                                            placeholder_text="Ej: 0.05")
        self.in_coef_perdida.pack(anchor="w", pady=(2, 14))
        self.in_coef_perdida.insert(0, str(self.params.coeficiente_perdida))

        # ── Campo: Tipo de maquinaria ──────────────────────────────────
        ctk.CTkLabel(frame, text="Tipo de maquinaria *",
                     font=("Arial", 13)).pack(anchor="w")
        self.opt_maquinaria = ctk.CTkOptionMenu(
            frame,
            values=["Proceso Manual", "Línea Automatizada", "Híbrido"],
            width=280,
            font=("Arial", 13)
        )
        self.opt_maquinaria.pack(anchor="w", pady=(2, 25))
        self.opt_maquinaria.set(self.params.tipo_maquinaria)

        # Nota de campos obligatorios
        ctk.CTkLabel(frame, text="* Campos obligatorios",
                     font=("Arial", 11), text_color="#888888").pack(anchor="w", pady=(0, 10))

        # Botón guardar
        self.btn_guardar = ctk.CTkButton(
            frame, text="💾  Cargar Parámetros",
            width=200, font=("Arial", 14, "bold"),
            command=self._cargar_parametros
        )
        self.btn_guardar.pack(anchor="w")

        # Etiqueta de error
        self.lbl_error = ctk.CTkLabel(
            frame, text="", font=("Arial", 12),
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
                     font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 20))

        # Indicador de estado principal
        self.lbl_indicador = ctk.CTkLabel(
            frame,
            text="⛔  Sin parámetros cargados",
            font=("Arial", 16, "bold"),
            text_color="#EF5350"
        )
        self.lbl_indicador.pack(anchor="w", pady=(0, 15))

        sep = ctk.CTkFrame(frame, height=1, fg_color="#2c3e50")
        sep.pack(fill="x", pady=(0, 20))

        # Resumen de parámetros cargados
        ctk.CTkLabel(frame, text="Parámetros Cargados:",
                     font=("Arial", 14, "bold"),
                     text_color="#AAAAAA").pack(anchor="w", pady=(0, 10))

        self.lbl_resumen = ctk.CTkLabel(
            frame,
            text="—",
            font=("Arial", 13),
            text_color="#888888",
            justify="left",
            wraplength=280
        )
        self.lbl_resumen.pack(anchor="w")

        sep2 = ctk.CTkFrame(frame, height=1, fg_color="#2c3e50")
        sep2.pack(fill="x", pady=(20, 15))

        # Resultados de indicadores (se llenan tras ejecutar)
        ctk.CTkLabel(frame, text="Indicadores de Productividad:",
                     font=("Arial", 14, "bold"),
                     text_color="#AAAAAA").pack(anchor="w", pady=(0, 10))

        indicadores = [
            ("Coef. Productividad", "coef_prod"),
            ("Eficacia",            "eficacia"),
            ("Eficiencia",          "eficiencia"),
            ("Rango de Mejora",     "rango_mejora"),
        ]
        self._entries_indicadores = {}
        for etiqueta, key in indicadores:
            ctk.CTkLabel(frame, text=etiqueta, font=("Arial", 13),
                         text_color="#AAAAAA").pack(anchor="w")
            entry = ctk.CTkEntry(frame, width=240, state="readonly",
                                 font=("Arial", 13))
            entry.pack(anchor="w", pady=(2, 10))
            self._entries_indicadores[key] = entry

    # ------------------------------------------------------------------
    # Lógica de carga y validación
    # ------------------------------------------------------------------

    def _cargar_parametros(self):
        """Valida todos los campos y carga los parámetros en el sistema."""
        self.lbl_error.configure(text="")

        # ── Validar: Horas de trabajo ──────────────────────────────────
        horas, err = self._validar_float_positivo(
            self.in_horas.get(), "Horas de trabajo", estrictamente_positivo=True
        )
        if err:
            self.lbl_error.configure(text=err)
            return

        # ── Validar: Cantidad de empleados ─────────────────────────────
        empleados_f, err = self._validar_float_positivo(
            self.in_empleados.get(), "Cantidad de empleados",
            estrictamente_positivo=True
        )
        if err:
            self.lbl_error.configure(text=err)
            return
        empleados = int(empleados_f)
        if empleados <= 0:
            self.lbl_error.configure(
                text="⚠ La cantidad de empleados debe ser un entero mayor a 0."
            )
            return

        # ── Validar: Energía consumida ─────────────────────────────────
        energia, err = self._validar_float_positivo(
            self.in_energia.get(), "Energía consumida",
            estrictamente_positivo=False  # puede ser 0
        )
        if err:
            self.lbl_error.configure(text=err)
            return

        # ── Validar: Coeficiente de pérdida ───────────────────────────
        coef, err = self._validar_float_positivo(
            self.in_coef_perdida.get(), "Coeficiente de pérdida",
            estrictamente_positivo=False
        )
        if err:
            self.lbl_error.configure(text=err)
            return
        if not (0.0 <= coef <= 1.0):
            self.lbl_error.configure(
                text="⚠ El coeficiente de pérdida debe estar entre 0.0 y 1.0."
            )
            return

        # ── Aplicar parámetros al objeto compartido ────────────────────
        self.params.horas_trabajo = horas
        self.params.cantidad_empleados = empleados
        self.params.energia_consumida = energia
        self.params.coeficiente_perdida = coef
        self.params.tipo_maquinaria = self.opt_maquinaria.get()
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
            f"• Maquinaria: {self.params.tipo_maquinaria}"
        )
        self.lbl_resumen.configure(text=resumen, text_color="#E0E0E0")

        # Notificar a otras vistas (ej: VistaUsuario actualiza su indicador)
        if self.callback:
            self.callback()

    def actualizar_indicadores(self, coef_prod: float, eficacia: float,
                               eficiencia: float, rango_mejora: float):
        """
        Actualiza los entries de indicadores tras ejecutar una simulación.
        Puede ser llamado externamente por la vista de usuario.
        """
        datos = {
            "coef_prod":   f"{coef_prod:.4f} u/h/emp",
            "eficacia":    f"{eficacia:.2f} %",
            "eficiencia":  f"{eficiencia:.2f} %",
            "rango_mejora": f"{rango_mejora:.2f} %",
        }
        for key, valor in datos.items():
            entry = self._entries_indicadores[key]
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, valor)
            entry.configure(state="readonly")

    # ------------------------------------------------------------------
    # Validadores estáticos
    # ------------------------------------------------------------------

    @staticmethod
    def _validar_float_positivo(texto: str, nombre: str,
                                estrictamente_positivo: bool = True):
        """
        Valida que un texto sea un número float válido.

        Args:
            texto:                 Texto del campo de entrada.
            nombre:                Nombre del campo (para el mensaje de error).
            estrictamente_positivo: Si True, rechaza el valor 0.

        Returns:
            Tupla (float, None) si válido.
            Tupla (None, str_error) si inválido.
        """
        texto = texto.strip()
        if not texto:
            return None, f"⚠ El campo '{nombre}' no puede estar vacío."
        try:
            valor = float(texto)
        except ValueError:
            return None, (
                f"⚠ '{nombre}' debe ser un número "
                f"(se recibió: '{texto}')."
            )
        if valor < 0:
            return None, f"⚠ '{nombre}' no puede ser negativo."
        if estrictamente_positivo and valor == 0:
            return None, f"⚠ '{nombre}' debe ser mayor a 0."
        return valor, None
