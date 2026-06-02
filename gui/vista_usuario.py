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
from gui.componentes import CTKResultRow


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

        # Suscribirse al evento de parámetros cargados
        self.params.suscribir("parametros_cargados", self.actualizar_estado_parametros)

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
            text="El programa procesará dispositivos hasta alcanzar este peso (Máx 10000 kg).",
            font=("Azeri Sans", 14), text_color="#888888", wraplength=280
        ).pack(anchor="w", fill="x", pady=(2, 0))
        self.in_b_kg = ctk.CTkEntry(
            frame,
            placeholder_text="Ej: 100  (kg, de 0.1 a 10000)",
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

        self.out_peso = CTKResultRow(frame, "Peso procesado real (kg)", prefijo="⚖")
        self.out_peso.pack(fill="x", pady=(0, 5))

        self.out_dispositivos = CTKResultRow(frame, "Dispositivos procesados", icono_img=self.iconos.get("dispros"))
        self.out_dispositivos.pack(fill="x", pady=(0, 5))

        self.out_reventa = CTKResultRow(frame, "Equipos a reventa (CamRec + DvrRec)", icono_img=self.iconos.get("resell"))
        self.out_reventa.pack(fill="x", pady=(0, 5))

        self.out_cuellos = CTKResultRow(frame, "Cuellos de botella (Ocupación > 85%)", icono_img=self.iconos.get("cuello"))
        self.out_cuellos.pack(fill="x", pady=(0, 5))

        self.out_total = CTKResultRow(frame, "Valor total recuperado (ARS)", icono_img=self.iconos.get("money"))
        self.out_total.pack(fill="x", pady=(0, 5))

        self.lbl_ver_informe = ctk.CTkLabel(frame, text="Ver informe completo →",
                     font=("Arial", 12), text_color="#4FC3F7",
                     cursor="hand2")
        self.lbl_ver_informe.pack(anchor="w", pady=(10, 0))
        self.lbl_ver_informe.bind("<Button-1>", self._abrir_informe_completo)

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

    def _validar_peso_minimo_simulacion(self, texto_input: str) -> float:
        """Valida matemáticamente que el peso ingresado sea mayor o igual al peso del dispositivo más ligero configurado."""
        try:
            val_flotante = float(texto_input)
            peso_min_absoluto = min(self.params.composicion.peso_camara_min, self.params.composicion.peso_dvr_min)
            
            if val_flotante < peso_min_absoluto:
                msg = (f"El lote mínimo de simulación debe ser de {peso_min_absoluto} kg "
                       f"(el peso mínimo del dispositivo más ligero según la configuración).\n"
                       f"No se puede simular con un peso de {val_flotante} kg.")
                self.lbl_error.configure(text=f"⛔ Entrada inválida: debe ser >= {peso_min_absoluto} kg.")
                self.after(3000, lambda: self.lbl_error.configure(text=""))
                messagebox.showwarning("Atención: Peso inválido", msg)
                return None
            
            return Validador.validar_float(
                texto_input, "Peso total del lote (B)",
                min_valor=peso_min_absoluto,
                max_valor=100000.0
            )
        except ValueError as e:
            registrar_error("Error de validación del lote B (kg) en VistaUsuario", e)
            msg = str(e)
            self.lbl_error.configure(text=f"⚠ {msg}")
            self.after(3000, lambda: self.lbl_error.configure(text=""))
            messagebox.showwarning("Aviso de entrada", msg)
            return None

    def _ejecutar(self):
        """Valida la entrada B (kg) y ejecuta la simulación."""
        self.lbl_error.configure(text="")

        if not self.params.parametros_cargados:
            self.lbl_error.configure(
                text="⛔ Debe cargar los parámetros en la Vista del Gerente."
            )
            self.after(3000, lambda: self.lbl_error.configure(text=""))
            return

        texto_input = self.in_b_kg.get().strip()
        b_kg = self._validar_peso_minimo_simulacion(texto_input)
        if b_kg is None:
            return

        try:
            resultado = self.simulacion_service.simular_lote(b_kg)
        except RuntimeError as e:
            # registros de errores
            registrar_error("Error en la ejecución de la simulación en VistaUsuario", e)
            self.lbl_error.configure(text=f"⛔ {e}")
            self.after(3000, lambda: self.lbl_error.configure(text=""))
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
        self.out_peso.set(f"{resultado.peso_acumulado:.3f} kg")
        self.out_dispositivos.set(f"{resultado.n_total}  (Cám: {resultado.cant_cam} | DVR: {resultado.cant_dvr})")
        self.out_reventa.set(f"{resultado.equipos_reventa}  (Cám: {resultado.cam_rec} | DVR: {resultado.dvr_rec})")
        cuellos_str = ", ".join(resultado.cuellos_botella) if resultado.cuellos_botella else "Ninguno"
        self.out_cuellos.set(cuellos_str)
        self.out_total.set(f"{resultado.valor_total:,.2f}")

        self.ultimo_resultado = resultado

        # Abrir ventana de resultados completa
        if self._ventana_resultado_activa is not None:
            try:
                self._ventana_resultado_activa.destroy()
            except Exception as e:
                # registros de errores
                registrar_error("Error al intentar destruir la ventana de resultados activa en VistaUsuario", e)
                pass
        self._ventana_resultado_activa = VentanaResultados(self, resultado)

    def _abrir_informe_completo(self, event=None):
        if not hasattr(self, "ultimo_resultado") or self.ultimo_resultado is None:
            messagebox.showinfo("Info", "Debe ejecutar la simulación primero.")
            return

        if self._ventana_resultado_activa is not None:
            try:
                self._ventana_resultado_activa.destroy()
            except Exception:
                pass
        self._ventana_resultado_activa = VentanaResultados(self, self.ultimo_resultado)

    # (Fin de clase)
