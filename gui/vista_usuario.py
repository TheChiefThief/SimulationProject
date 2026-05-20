"""
gui/vista_usuario.py
---------------------
Tab "Vista de Usuario" de la aplicación.

Permite ingresar la cantidad de cámaras y DVRs, ejecutar la simulación
y ver un resumen rápido de resultados. El botón Ejecutar está bloqueado
si los parámetros operativos no fueron cargados por el Gerente.

Validaciones de entrada:
  - Campos no vacíos
  - Solo números enteros positivos
  - No se acepta texto ni negativos
"""

import customtkinter as ctk

from core.simulacion import simular_lote
from core.parametros import ParametrosSistema
from gui.ventana_resultados import VentanaResultados


class VistaUsuario(ctk.CTkFrame):
    """
    Frame que encapsula toda la Vista de Usuario.
    Se monta dentro del CTkTabview de la ventana principal.
    """

    def __init__(self, parent, params: ParametrosSistema):
        super().__init__(parent, fg_color="transparent")
        self.params = params
        self._ventana_resultado_activa = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_panel_izquierdo()
        self._construir_panel_derecho()

    # ------------------------------------------------------------------
    # Construcción de UI
    # ------------------------------------------------------------------

    def _construir_panel_izquierdo(self):
        """Panel de inputs: cantidad de cámaras y DVRs."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(frame, text="Ingresar", font=("Arial", 24, "bold")).pack(
            anchor="w", pady=(0, 20)
        )

        # Campo: Cantidad de cámaras
        ctk.CTkLabel(frame, text="Cantidad de Cámaras", font=("Arial", 14)).pack(anchor="w")
        self.in_camaras = ctk.CTkEntry(frame, width=250,
                                       placeholder_text="Ej: 50")
        self.in_camaras.pack(anchor="w", pady=(0, 20))
        self.in_camaras.insert(0, "50")

        # Campo: Cantidad de DVRs
        ctk.CTkLabel(frame, text="Cantidad de DVRs", font=("Arial", 14)).pack(anchor="w")
        self.in_dvrs = ctk.CTkEntry(frame, width=250,
                                    placeholder_text="Ej: 20")
        self.in_dvrs.pack(anchor="w", pady=(0, 40))
        self.in_dvrs.insert(0, "20")

        # Indicador de estado de parámetros
        self.lbl_estado = ctk.CTkLabel(
            frame, text="⚠ Parámetros no cargados",
            font=("Arial", 12), text_color="#FF7043"
        )
        self.lbl_estado.pack(anchor="w", pady=(0, 10))

        # Botón ejecutar
        self.btn_ejecutar = ctk.CTkButton(
            frame, text="▶  Ejecutar Simulación",
            width=200, font=("Arial", 14, "bold"),
            command=self._ejecutar
        )
        self.btn_ejecutar.pack(anchor="w")

        # Etiqueta de error
        self.lbl_error = ctk.CTkLabel(frame, text="", font=("Arial", 12),
                                      text_color="#EF5350", wraplength=280)
        self.lbl_error.pack(anchor="w", pady=(10, 0))

    def _construir_panel_derecho(self):
        """Panel de resumen rápido de resultados."""
        frame_outer = ctk.CTkFrame(self, fg_color="#1a2530", corner_radius=10)
        frame_outer.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        frame = ctk.CTkFrame(frame_outer, fg_color="transparent")
        frame.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Resumen", font=("Arial", 24, "bold")).pack(
            anchor="w", pady=(0, 20)
        )

        def _crear_fila(parent, etiqueta):
            ctk.CTkLabel(parent, text=etiqueta, font=("Arial", 13),
                         text_color="#AAAAAA").pack(anchor="w")
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(anchor="w", fill="x", pady=(0, 14))
            ctk.CTkLabel(row, text="$", font=("Arial", 17, "bold"),
                         text_color="#4FC3F7").pack(side="left", padx=(0, 8))
            entry = ctk.CTkEntry(row, width=220, state="readonly",
                                 font=("Arial", 14))
            entry.pack(side="left")
            return entry

        self.out_lentes = _crear_fila(frame, "Lentes recuperados")
        self.out_placas = _crear_fila(frame, "Placas recuperadas (total)")
        self.out_hdd = _crear_fila(frame, "Discos HDD recuperados")
        self.out_total = _crear_fila(frame, "Valor total recuperado")

        ctk.CTkLabel(frame, text="Ver informe completo →",
                     font=("Arial", 12), text_color="#4FC3F7",
                     cursor="hand2").pack(anchor="w", pady=(15, 0))

    # ------------------------------------------------------------------
    # Lógica de ejecución
    # ------------------------------------------------------------------

    def actualizar_estado_parametros(self):
        """Actualiza el indicador visual según si los parámetros están cargados."""
        if self.params.parametros_cargados:
            self.lbl_estado.configure(
                text="✔ Parámetros cargados",
                text_color="#66BB6A"
            )
        else:
            self.lbl_estado.configure(
                text="⚠ Parámetros no cargados",
                text_color="#FF7043"
            )

    def _ejecutar(self):
        """Valida las entradas y ejecuta la simulación."""
        self.lbl_error.configure(text="")

        # Verificar parámetros cargados
        if not self.params.parametros_cargados:
            self.lbl_error.configure(
                text="⛔ Debe cargar los parámetros operativos en la Vista del "
                     "Gerente antes de ejecutar la simulación."
            )
            return

        # Validar campo cámaras
        n_camaras, error = self._validar_entero_positivo(
            self.in_camaras.get(), "Cantidad de Cámaras"
        )
        if error:
            self.lbl_error.configure(text=error)
            return

        # Validar campo DVRs
        n_dvrs, error = self._validar_entero_positivo(
            self.in_dvrs.get(), "Cantidad de DVRs"
        )
        if error:
            self.lbl_error.configure(text=error)
            return

        if n_camaras + n_dvrs == 0:
            self.lbl_error.configure(
                text="⚠ Ingrese al menos 1 cámara o 1 DVR."
            )
            return

        # Ejecutar simulación
        try:
            resultado = simular_lote(self.params, n_camaras, n_dvrs)
        except RuntimeError as e:
            self.lbl_error.configure(text=f"⛔ {e}")
            return

        # Actualizar resumen rápido
        self._actualizar_entry(self.out_lentes,
                               f"{resultado.valor_lentes:,.2f}")
        self._actualizar_entry(self.out_placas,
                               f"{resultado.valor_total_placas:,.2f}")
        self._actualizar_entry(self.out_hdd,
                               f"{resultado.valor_hdd:,.2f}")
        self._actualizar_entry(self.out_total,
                               f"{resultado.valor_total:,.2f}")

        # Abrir ventana de resultados completa
        if self._ventana_resultado_activa is not None:
            try:
                self._ventana_resultado_activa.destroy()
            except Exception:
                pass
        self._ventana_resultado_activa = VentanaResultados(self, resultado)

    @staticmethod
    def _validar_entero_positivo(texto: str, nombre_campo: str):
        """
        Valida que un texto sea un entero no negativo.

        Returns:
            Tupla (valor_int, None) si es válido.
            Tupla (None, mensaje_error) si no lo es.
        """
        texto = texto.strip()
        if not texto:
            return None, f"⚠ El campo '{nombre_campo}' no puede estar vacío."
        try:
            valor = int(texto)
        except ValueError:
            return None, (
                f"⚠ '{nombre_campo}' debe ser un número entero "
                f"(se recibió: '{texto}')."
            )
        if valor < 0:
            return None, f"⚠ '{nombre_campo}' no puede ser negativo."
        return valor, None

    @staticmethod
    def _actualizar_entry(entry_widget, valor_str: str):
        """Actualiza un CTkEntry en modo readonly."""
        entry_widget.configure(state="normal")
        entry_widget.delete(0, "end")
        entry_widget.insert(0, valor_str)
        entry_widget.configure(state="readonly")
