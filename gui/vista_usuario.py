"""
gui/vista_usuario.py
---------------------
Tab "Vista de Usuario" de la aplicación.

Permite ingresar el peso total del lote (B en kg). El motor de simulación
procesa dispositivos individuales acumulando peso hasta alcanzar B.

El botón Ejecutar funciona desde el inicio con valores por defecto.
"""

import os

import customtkinter as ctk
from PIL import Image
from tkinter import messagebox

from core.logger import registrar_error
from core.parametros import ParametrosSistema
from core.simulacion_service import SimulacionService
from core.validador import Validador
from gui.ventana_resultados import VentanaResultados


class VistaUsuario(ctk.CTkFrame):
    """Frame de la Vista de Usuario — entrada por peso B (kg)."""

    def __init__(self, parent, params: ParametrosSistema,
                 simulacion_service: SimulacionService,
                 callback_simulacion_ejecutada=None,
                 callback_ver_historial=None):
        super().__init__(parent, fg_color="transparent")
        self.params = params
        self.simulacion_service = simulacion_service
        self.callback_simulacion_ejecutada = callback_simulacion_ejecutada
        self.callback_ver_historial = callback_ver_historial
        self._ventana_resultado_activa = None
        self.iconos = {
            "dispros": self._cargar_icono("dispros.png"),
            "resell": self._cargar_icono("resell.png"),
            "cuello": self._cargar_icono("cuello.png"),
            "money": self._cargar_icono("money.png")
        }

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_panel_izquierdo()
        self._construir_panel_derecho()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _construir_panel_izquierdo(self):
        """Panel de input: peso total del lote B (kg)."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Ingresar", font=("Azeri Sans", 38, "bold")).pack(
            anchor="w", pady=(0, 20)
        )

        # Campo: Peso total del lote (B)
        ctk.CTkLabel(
            frame,
            text="Peso total del lote — B (kg)",
            font=("Azeri Sans", 22)
        ).pack(anchor="w", fill="x")
        ctk.CTkLabel(
            frame,
            text="El programa procesará dispositivos hasta alcanzar este peso.",
            font=("Azeri Sans", 14), text_color="#888888", wraplength=280
        ).pack(anchor="w", fill="x", pady=(2, 0))
        self.in_b_kg = ctk.CTkEntry(
            frame,
            placeholder_text="Ej: 100  (kg, número > 0)",
            corner_radius=12,
            height=50
        )
        self.in_b_kg.pack(anchor="w", fill="x", pady=(5, 20))
        self.in_b_kg.insert(0, "100")

        # Indicador de estado de parámetros
        self.lbl_estado = ctk.CTkLabel(
            frame,
            text="✔ Parámetros por defecto activos",
            font=("Azeri Sans", 12), text_color="#66BB6A"
        )
        self.lbl_estado.pack(anchor="w", fill="x", pady=(0, 10))

        # Espaciador flexible para que la columna izquierda ocupe todo el alto
        spacer = ctk.CTkFrame(frame, fg_color="transparent")
        spacer.pack(expand=True, fill="both")

        # Etiqueta de error (aparece justo encima de los botones en la parte inferior)
        self.lbl_error = ctk.CTkLabel(
            frame, text="", font=("Azeri Sans", 14),
            text_color="#EF5350", wraplength=280
        )
        self.lbl_error.pack(anchor="w", fill="x", pady=(10, 6))

        # Botones en la parte inferior
        self.btn_ver_historial = ctk.CTkButton(
            frame, text="📋 Ver Historial",
            font=("Azeri Sans", 24, "bold"),
            fg_color="#37474F", hover_color="#455A64",
            corner_radius=15,
            height=52,
            command=self._ir_a_historial
        )
        self.btn_ver_historial.pack(side="bottom", fill="x", pady=(6, 0))

        self.btn_ejecutar = ctk.CTkButton(
            frame, text="▶  Ejecutar Simulación",
            font=("Azeri Sans", 24, "bold"),
            fg_color="#327fc3", hover_color="#2865a3",
            corner_radius=15,
            height=52,
            command=self._ejecutar
        )
        self.btn_ejecutar.pack(side="bottom", fill="x")

    def _cargar_icono(self, nombre_archivo):
        ruta_icono = os.path.join(os.path.dirname(__file__), "iconos", nombre_archivo)
        try:
            imagen = Image.open(ruta_icono).convert("RGBA")
            imagen = imagen.resize((24, 24), Image.LANCZOS)
            return ctk.CTkImage(light_image=imagen, dark_image=imagen, size=(24, 24))
        except Exception:
            return None

    def _construir_panel_derecho(self):
        """Panel de resumen rápido de resultados."""
        frame_outer = ctk.CTkFrame(self, fg_color="#1a2530", corner_radius=10)
        frame_outer.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        frame = ctk.CTkFrame(frame_outer, fg_color="transparent")
        frame.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Resumen", font=("Azeri Sans", 24, "bold")).pack(
            anchor="w", pady=(0, 20)
        )

        def _fila_resultado(parent, etiqueta, prefijo="", icono=None):
            # Truncar etiquetas largas o usar wraplength
            ctk.CTkLabel(parent, text=etiqueta, font=("Azeri Sans", 13),
                         text_color="#AAAAAA", wraplength=280).pack(anchor="w")
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(anchor="w", fill="x", pady=(0, 14), expand=True)
            if icono and self.iconos.get(icono):
                ctk.CTkLabel(row, image=self.iconos[icono], text="").pack(side="left", padx=(0, 10), pady=4)
            if prefijo:
                ctk.CTkLabel(row, text=prefijo, font=("Azeri Sans", 15, "bold"),
                             text_color="#4FC3F7").pack(side="left", padx=(0, 8))
            entry = ctk.CTkEntry(row, state="readonly", font=("Azeri Sans", 13))
            entry.pack(side="left", fill="x", expand=True)
            return entry

        self.out_peso = _fila_resultado(frame, "Peso procesado real (kg)", "⚖")
        self.out_dispositivos = _fila_resultado(frame, "Dispositivos procesados", icono="dispros")
        self.out_reventa = _fila_resultado(frame, "Equipos a reventa (CamRec + DvrRec)", icono="resell")
        self.out_cuellos = _fila_resultado(frame, "Cuellos de botella (Ocupación > 85%)", icono="cuello")
        self.out_total = _fila_resultado(frame, "Valor total recuperado (ARS)", icono="money")

        ctk.CTkLabel(frame, text="Ver informe completo →",
                     font=("Arial", 12), text_color="#4FC3F7",
                     cursor="hand2").pack(anchor="w", pady=(10, 0))

    # ------------------------------------------------------------------
    # Lógica de ejecución
    # ------------------------------------------------------------------

    def actualizar_estado_parametros(self):
        """Actualiza el indicador visual según si los parámetros están cargados."""
        if self.params.parametros_cargados:
            self.lbl_estado.configure(
                text="✔ Parámetros cargados correctamente",
                text_color="#66BB6A"
            )
        else:
            self.lbl_estado.configure(
                text="⚠ Parámetros no cargados",
                text_color="#FF7043"
            )

    def _ir_a_historial(self):
        """Redirige al tab del historial si está configurado."""
        if self.callback_ver_historial:
            self.callback_ver_historial()

    def _ejecutar(self):
        """Valida la entrada B (kg) y ejecuta la simulación."""
        self.lbl_error.configure(text="")

        if not self.params.parametros_cargados:
            self.lbl_error.configure(
                text="⛔ Debe cargar los parámetros en la Vista del Gerente."
            )
            return

        try:
            b_kg = Validador.validar_float(
                self.in_b_kg.get(), "Peso total del lote (B)",
                min_valor=0.1
            )
        except ValueError as e:
            # registros de errores
            registrar_error("Error de validación del lote B (kg) en VistaUsuario", e)
            msg = str(e)
            self.lbl_error.configure(text=f"⚠ {msg}")
            messagebox.showwarning("Aviso de entrada", msg)
            return

        try:
            resultado = self.simulacion_service.simular_lote(b_kg)
        except RuntimeError as e:
            # registros de errores
            registrar_error("Error en la ejecución de la simulación en VistaUsuario", e)
            self.lbl_error.configure(text=f"⛔ {e}")
            return

        # Guardar en el historial
        try:
            from core.historial_simulador import HistorialSimulador
            HistorialSimulador.guardar_simulacion(self.params, resultado)
            if self.callback_simulacion_ejecutada:
                self.callback_simulacion_ejecutada()
        except Exception as e:
            # registros de errores
            registrar_error("Error al guardar la simulación en el historial desde VistaUsuario", e)
            print(f"Error al guardar en el historial: {e}")

        # Actualizar resumen
        self._set_entry(self.out_peso,
                        f"{resultado.peso_acumulado:.3f} kg")
        self._set_entry(self.out_dispositivos,
                        f"{resultado.n_total}  (Cám: {resultado.cant_cam} | DVR: {resultado.cant_dvr})")
        self._set_entry(self.out_reventa,
                        f"{resultado.equipos_reventa}  (Cám: {resultado.cam_rec} | DVR: {resultado.dvr_rec})")
        cuellos_str = ", ".join(resultado.cuellos_botella) if resultado.cuellos_botella else "Ninguno"
        self._set_entry(self.out_cuellos, cuellos_str)
        self._set_entry(self.out_total, f"{resultado.valor_total:,.2f}")

        # Abrir ventana de resultados completa
        if self._ventana_resultado_activa is not None:
            try:
                self._ventana_resultado_activa.destroy()
            except Exception as e:
                # registros de errores
                registrar_error("Error al intentar destruir la ventana de resultados activa en VistaUsuario", e)
                pass
        self._ventana_resultado_activa = VentanaResultados(self, resultado)

    @staticmethod
    def _set_entry(entry_widget, valor_str: str):
        """Actualiza un CTkEntry en modo readonly."""
        entry_widget.configure(state="normal")
        entry_widget.delete(0, "end")
        entry_widget.insert(0, valor_str)
        entry_widget.configure(state="readonly")
