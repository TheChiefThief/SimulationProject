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
            logo_image = logo_image.resize((150, 70), Image.LANCZOS)
            self.logo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(150, 70))
            logo_label = ctk.CTkLabel(header_frame, image=self.logo, text="")
            logo_label.grid(row=0, column=0, padx=(0, 50), pady=0)
        except Exception:
            pass
        
        # Botones de navegación
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="w", padx=40, pady=20)
        
        self.nav_buttons = {}
        for idx, tab_name in enumerate([self.T_USUARIO, self.T_GERENTE, self.T_CONFIG, self.T_HISTORIAL]):
            btn = ctk.CTkButton(
                buttons_frame,
                text=tab_name,
                font=("Azeri Sans", 20),
                fg_color="#0E3848" if idx != 0 else "#327fc3",
                hover_color="#60808F",
                command=lambda tn=tab_name: self._cambiar_vista(tn)
            )
            btn.pack(side="left", padx=8)
            self.nav_buttons[tab_name] = btn
        
        self.vista_actual = self.T_USUARIO

    def _construir_vistas(self):
        """Crea el contenedor principal y prepara la estructura de lazy loading."""
        # Contenedor para las vistas
        self.contenedor_vistas = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_vistas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        self.vistas_cacheadas = {}
        
        # Cargar por defecto la primera vista
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
        """Muestra la vista especificada (usando lazy loading) y oculta las demás."""
        if nombre_vista not in self.vistas_cacheadas:
            frame = ctk.CTkFrame(self.contenedor_vistas, fg_color="transparent")
            
            if nombre_vista == self.T_USUARIO:
                from gui.vista_usuario import VistaUsuario
                vista = VistaUsuario(
                    frame,
                    params=self.params,
                    simulacion_service=self.simulacion_service,
                    callback_simulacion_ejecutada=self._on_simulacion_ejecutada,
                    callback_ver_historial=lambda: self._cambiar_vista(self.T_HISTORIAL)
                )
                vista.pack(fill="both", expand=True)
                self.vista_usuario = vista
                
            elif nombre_vista == self.T_GERENTE:
                from gui.vista_gerente import VistaGerente
                vista = VistaGerente(
                    frame,
                    params=self.params
                )
                vista.pack(fill="both", expand=True)
                self.vista_gerente = vista
                
            elif nombre_vista == self.T_CONFIG:
                from gui.vista_config import VistaConfig
                vista = VistaConfig(
                    frame,
                    params=self.params
                )
                vista.pack(fill="both", expand=True)
                self.vista_config = vista
                
            elif nombre_vista == self.T_HISTORIAL:
                from gui.vista_historial import VistaHistorial
                vista = VistaHistorial(
                    frame
                )
                vista.pack(fill="both", expand=True)
                self.vista_historial = vista
                
            self.vistas_cacheadas[nombre_vista] = frame

        # Ocultar todas las demás vistas que ya estén cargadas en la UI
        for vista_name, frame in self.vistas_cacheadas.items():
            if vista_name != nombre_vista:
                frame.pack_forget()

        # Mostrar la nueva vista
        self.vistas_cacheadas[nombre_vista].pack(fill="both", expand=True)
        self.vista_actual = nombre_vista

    def _construir_tabs(self):
        """Método deprecado, reemplazado por _construir_vistas()."""
        pass

    # ------------------------------------------------------------------
    # Callbacks de comunicación entre vistas
    # ------------------------------------------------------------------



    def _on_simulacion_ejecutada(self):
        """Llamado cuando se ejecuta una simulación para recargar el historial."""
        if hasattr(self, "vista_historial"):
            self.vista_historial.recargar_historial()

    def _on_ver_historial(self):
        """Redirige al usuario a la vista del historial."""
        self._cambiar_vista(self.T_HISTORIAL)
