"""
gui/app.py
-----------
Ventana principal de la aplicación: AppSimulador.

Orquesta los tres tabs (VistaUsuario, VistaGerente, VistaConfig)
y el objeto ParametrosSistema compartido entre todas las vistas.

El objeto `params` se instancia aquí y se pasa a cada vista;
actúa como fuente única de verdad del estado del sistema.
"""

import customtkinter as ctk

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

        self.title("Simulador de Reciclaje RAEE — Cámaras y DVRs")
        
        # Definir dimensiones y centrar en la pantalla
        ancho = 1200
        alto = 810
        self.minsize(950, 650)
        
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()
        
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

        # Estado compartido entre todas las vistas
        self.params = ParametrosSistema()

        # Servicio de simulación (inyectable para testing)
        self.simulacion_service = SimulacionService(self.params)

        self._construir_tabs()

    # ------------------------------------------------------------------
    # Construcción del layout principal
    # ------------------------------------------------------------------

    def _construir_tabs(self):
        """Crea el CTkTabview y monta cada vista en su tab correspondiente."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=0, pady=0, fill="both", expand=True)

        self.tabview.add(self.T_USUARIO)
        self.tabview.add(self.T_GERENTE)
        self.tabview.add(self.T_CONFIG)
        self.tabview.add(self.T_HISTORIAL)

        # ── Vista de Usuario ───────────────────────────────────────────
        self.vista_usuario = VistaUsuario(
            self.tabview.tab(self.T_USUARIO),
            params=self.params,
            simulacion_service=self.simulacion_service,
            callback_simulacion_ejecutada=self._on_simulacion_ejecutada,
            callback_ver_historial=self._on_ver_historial
        )
        self.vista_usuario.pack(fill="both", expand=True)

        # ── Vista del Gerente ──────────────────────────────────────────
        self.vista_gerente = VistaGerente(
            self.tabview.tab(self.T_GERENTE),
            params=self.params,
            callback_parametros_cargados=self._on_parametros_cargados
        )
        self.vista_gerente.pack(fill="both", expand=True)

        # ── Vista de Configuración ─────────────────────────────────────
        self.vista_config = VistaConfig(
            self.tabview.tab(self.T_CONFIG),
            params=self.params,
            callback_config_guardada=self._on_config_guardada
        )
        self.vista_config.pack(fill="both", expand=True)

        # ── Vista de Historial ─────────────────────────────────────────
        from gui.vista_historial import VistaHistorial
        self.vista_historial = VistaHistorial(
            self.tabview.tab(self.T_HISTORIAL)
        )
        self.vista_historial.pack(fill="both", expand=True)

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
        """Redirige al usuario al tab del historial."""
        self.tabview.set(self.T_HISTORIAL)
