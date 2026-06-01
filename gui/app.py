"""
gui/app.py
-----------
Ventana principal de la aplicación: AppSimulador.

Orquesta los tres tabs (VistaUsuario, VistaGerente, VistaConfig)
y el objeto ParametrosSistema compartido entre todas las vistas.

El objeto `params` se instancia aquí y se pasa a cada vista;
actúa como fuente única de verdad del estado del sistema.
"""

import os
import tkinter as tk

import customtkinter as ctk
from PIL import Image

from core.parametros import ParametrosSistema
from core.simulacion_service import SimulacionService
from gui.vista_usuario import VistaUsuario
from gui.vista_gerente import VistaGerente
from gui.vista_config import VistaConfig


class AppSimulador(ctk.CTk):
    """
    Ventana raíz de la aplicación de simulación de reciclaje RAEE.

    Gestiona el ciclo de vida de la GUI y coordina la comunicación
    entre las vistas mediante el objeto ParametrosSistema compartido.
    """

    T_USUARIO = "Vista de Usuario"
    T_GERENTE = "Vista del Gerente"
    T_CONFIG = "Configuración"
    T_HISTORIAL = "Historial"

    def __init__(self):
        super().__init__()

        # Configuración de apariencia
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Establecer el color de fondo principal
        self.configure(fg_color="#082334")

        self.title("Simulador de Reciclaje RAEE — Cámaras y DVRs")
        
        # Definir dimensiones y centrar en la pantalla
        ancho = 1200
        alto = 840
        self.minsize(950, 650)
        
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()
        
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

        # Configurar grid para el layout principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Estado compartido entre todas las vistas
        self.params = ParametrosSistema()

        # Servicio de simulación (inyectable para testing)
        self.simulacion_service = SimulacionService(self.params)

        self._construir_header()
        self._construir_vistas()

    # ------------------------------------------------------------------
    # Construcción del layout principal
    # ------------------------------------------------------------------

    def _construir_header(self):
        """Dibuja el encabezado con el logo y botones de navegación."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo de la empresa
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        try:
            logo_image = Image.open(logo_path).convert("RGBA")
            logo_image = logo_image.resize((110, 40), Image.LANCZOS)
            self.logo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(110, 40))
            logo_label = ctk.CTkLabel(header_frame, image=self.logo, text="")
            logo_label.grid(row=0, column=0, padx=(0, 20), pady=20)
        except Exception:
            pass
        
        # Botones de navegación
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="w", padx=0, pady=20)
        
        self.nav_buttons = {}
        for idx, tab_name in enumerate([self.T_USUARIO, self.T_GERENTE, self.T_CONFIG, self.T_HISTORIAL]):
            btn = ctk.CTkButton(
                buttons_frame,
                text=tab_name,
                font=("Azeri Sans", 16),
                fg_color="#0E3848" if idx != 0 else "#327fc3",
                hover_color="#60808F",
                command=lambda tn=tab_name: self._cambiar_vista(tn)
            )
            btn.pack(side="left", padx=8)
            self.nav_buttons[tab_name] = btn
        
        self.vista_actual = self.T_USUARIO

    def _construir_vistas(self):
        """Crea el contenedor principal y monta las vistas."""
        # Contenedor para las vistas
        self.contenedor_vistas = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_vistas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        # ── Vista de Usuario ───────────────────────────────────────────
        self.frame_usuario = ctk.CTkFrame(self.contenedor_vistas, fg_color="transparent")
        self.frame_usuario.pack(fill="both", expand=True)
        
        self.vista_usuario = VistaUsuario(
            self.frame_usuario,
            params=self.params,
            simulacion_service=self.simulacion_service,
            callback_simulacion_ejecutada=self._on_simulacion_ejecutada,
            callback_ver_historial=lambda: self._cambiar_vista(self.T_HISTORIAL)
        )
        self.vista_usuario.pack(fill="both", expand=True)

        # ── Vista del Gerente ──────────────────────────────────────────
        self.frame_gerente = ctk.CTkFrame(self.contenedor_vistas, fg_color="transparent")
        
        self.vista_gerente = VistaGerente(
            self.frame_gerente,
            params=self.params,
            callback_parametros_cargados=self._on_parametros_cargados
        )
        self.vista_gerente.pack(fill="both", expand=True)

        # ── Vista de Configuración ─────────────────────────────────────
        self.frame_config = ctk.CTkFrame(self.contenedor_vistas, fg_color="transparent")
        
        self.vista_config = VistaConfig(
            self.frame_config,
            params=self.params,
            callback_config_guardada=self._on_config_guardada
        )
        self.vista_config.pack(fill="both", expand=True)

        # ── Vista de Historial ─────────────────────────────────────────
        from gui.vista_historial import VistaHistorial
        self.frame_historial = ctk.CTkFrame(self.contenedor_vistas, fg_color="transparent")
        
        self.vista_historial = VistaHistorial(
            self.frame_historial
        )
        self.vista_historial.pack(fill="both", expand=True)
        
        # Mostrar solo la vista actual
        self._mostrar_vista(self.T_USUARIO)

    def _cambiar_vista(self, nombre_vista):
        """Cambia la vista activa y actualiza los estilos de los botones."""
        self.vista_actual = nombre_vista
        self._mostrar_vista(nombre_vista)
        
        # Actualizar estilos de botones
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == nombre_vista:
                btn.configure(fg_color="#327fc3")
            else:
                btn.configure(fg_color="#0E3848")

    def _mostrar_vista(self, nombre_vista):
        """Muestra la vista especificada y oculta las demás."""
        frames = {
            self.T_USUARIO: self.frame_usuario,
            self.T_GERENTE: self.frame_gerente,
            self.T_CONFIG: self.frame_config,
            self.T_HISTORIAL: self.frame_historial
        }
        
        for vista_name, frame in frames.items():
            if vista_name == nombre_vista:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    def _construir_tabs(self):
        """Método deprecado, reemplazado por _construir_vistas()."""
        pass

    # ------------------------------------------------------------------
    # Callbacks de comunicación entre vistas
    # ------------------------------------------------------------------

    def _on_parametros_cargados(self):
        """
        Llamado por VistaGerente cuando los parámetros operativos
        son cargados exitosamente. Notifica a VistaUsuario.
        """
        self.vista_usuario.actualizar_estado_parametros()

    def _on_config_guardada(self):
        """
        Llamado por VistaConfig cuando la configuración es guardada.
        Puede usarse para propagar cambios si fuera necesario.
        """
        pass  # Extensible para futuras necesidades

    def _on_simulacion_ejecutada(self):
        """Llamado cuando se ejecuta una simulación para recargar el historial."""
        if hasattr(self, "vista_historial"):
            self.vista_historial.recargar_historial()

    def _on_ver_historial(self):
        """Redirige al usuario a la vista del historial."""
        self._cambiar_vista(self.T_HISTORIAL)
