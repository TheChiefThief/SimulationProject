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

    def __init__(self):
        super().__init__()

        # Configuración de apariencia
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Simulador de Reciclaje RAEE — Cámaras y DVRs")
        self.geometry("1100x640")
        self.minsize(900, 560)

        # Estado compartido entre todas las vistas
        self.params = ParametrosSistema()

        self._construir_tabs()

    # ------------------------------------------------------------------
    # Construcción del layout principal
    # ------------------------------------------------------------------

    def _construir_tabs(self):
        """Crea el CTkTabview y monta cada vista en su tab correspondiente."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=15, pady=15, fill="both", expand=True)

        self.tabview.add(self.T_USUARIO)
        self.tabview.add(self.T_GERENTE)
        self.tabview.add(self.T_CONFIG)

        # ── Vista de Usuario ───────────────────────────────────────────
        self.vista_usuario = VistaUsuario(
            self.tabview.tab(self.T_USUARIO),
            params=self.params
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
