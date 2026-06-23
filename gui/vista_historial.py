"""
Tab "Historial de Simulaciones" de la aplicación.
Permite visualizar de manera persistente las simulaciones anteriores,
abrir sus reportes detallados y volver a exportarlas a Excel.
"""

from tkinter import messagebox
import customtkinter as ctk

from core.logger import registrar_error
from core.historial_simulador import HistorialSimulador
from gui.ventana_resultados import VentanaResultados
from core.exportadores import exportar_a_excel


class VistaHistorial(ctk.CTkFrame):
    """
    Frame que muestra el listado histórico de simulaciones con opciones para
    abrir detalles, exportar a Excel y eliminar registros.
    """

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._ventana_resultado_activa = None

        # Configurar Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._construir_cabecera()
        self._construir_cuerpo()
        self.recargar_historial()

    def _construir_cabecera(self):
        """Panel superior con el título y botón de borrar historial."""
        self.cabecera = ctk.CTkFrame(self, fg_color="transparent")
        self.cabecera.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        self.cabecera.grid_columnconfigure(0, weight=1)

        # Título e información
        info_frame = ctk.CTkFrame(self.cabecera, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w")

        self.lbl_titulo = ctk.CTkLabel(
            info_frame, text="📋 Historial de Simulaciones", font=("Azeri Sans", 22, "bold")
        )
        self.lbl_titulo.pack(anchor="w")

        self.lbl_info = ctk.CTkLabel(
            info_frame, text="Listado de corridas guardadas localmente.",
            font=("Azeri Sans", 12), text_color="#888888"
        )
        self.lbl_info.pack(anchor="w", pady=(2, 0))

        # Botón para borrar todo
        self.btn_borrar_todo = ctk.CTkButton(
            self.cabecera, text="🗑 Borrar Historial",
            font=("Azeri Sans", 12, "bold"), fg_color="#D32F2F", hover_color="#C62828",
            width=160, command=self._borrar_todo
        )
        self.btn_borrar_todo.grid(row=0, column=1, sticky="e")

    def _construir_cuerpo(self):
        """Crea el contenedor principal que alojará las tarjetas o el placeholder vacío."""
        self.cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        self.cuerpo.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.cuerpo.grid_columnconfigure(0, weight=1)
        self.cuerpo.grid_rowconfigure(0, weight=1)

        # Scrollable frame para el listado de tarjetas
        self.scroll_historial = ctk.CTkScrollableFrame(self.cuerpo, fg_color="#12192a")
        self.scroll_historial.grid(row=0, column=0, sticky="nsew")
        self.scroll_historial.grid_columnconfigure(0, weight=1)

    def recargar_historial(self):
        """Recarga el historial leyendo del archivo JSON y refrescando la UI."""
        # Limpiar elementos previos en el scroll
        for widget in self.scroll_historial.winfo_children():
            widget.destroy()

        registros = HistorialSimulador.obtener_historial()

        # Actualizar cantidad en cabecera
        cant = len(registros)
        if cant == 1:
            self.lbl_info.configure(text="Se encontró 1 simulación guardada localmente.")
        else:
            self.lbl_info.configure(text=f"Se encontraron {cant} simulaciones guardadas localmente.")

        if not registros:
            self._mostrar_placeholder_vacio()
            self.btn_borrar_todo.configure(state="disabled")
            return

        self.btn_borrar_todo.configure(state="normal")

        # Dibujar tarjetas de simulación
        for i, reg in enumerate(registros):
            self._crear_tarjeta_simulacion(reg, i)

    def _mostrar_placeholder_vacio(self):
        """Muestra una vista limpia cuando no hay registros guardados."""
        frame_vacio = ctk.CTkFrame(self.scroll_historial, fg_color="transparent")
        frame_vacio.pack(expand=True, pady=150)

        lbl_icono = ctk.CTkLabel(
            frame_vacio, text="📂", font=("Azeri Sans", 64)
        )
        lbl_icono.pack()

        lbl_texto = ctk.CTkLabel(
            frame_vacio, text="No hay simulaciones registradas en el historial.",
            font=("Azeri Sans", 16, "bold"), text_color="#AAAAAA"
        )
        lbl_texto.pack(pady=10)

        lbl_subtexto = ctk.CTkLabel(
            frame_vacio, text="Las simulaciones que realices en el panel de usuario se guardarán de forma automática aquí.",
            font=("Azeri Sans", 12), text_color="#777777", wraplength=450
        )
        lbl_subtexto.pack()

    def _crear_tarjeta_simulacion(self, registro: dict, index: int):
        """Crea una tarjeta gráfica representativa de una corrida de simulación."""
        reg_id = registro.get("id")
        fecha = registro.get("fecha", "Fecha desconocida")
        
        # Deserializar resultados para acceder a sus properties
        r = HistorialSimulador.deserializar_resultados(registro.get("resultados", {}))
        r.fecha = fecha

        # Tarjeta contenedor
        card = ctk.CTkFrame(self.scroll_historial, fg_color="#182232", border_width=1, border_color="#233248")
        card.pack(fill="x", pady=6, padx=10)
        
        # Configurar columnas de la tarjeta
        card.grid_columnconfigure(0, weight=2)  # Info lote y fecha
        card.grid_columnconfigure(1, weight=3)  # Métricas
        card.grid_columnconfigure(2, weight=2)  # Acciones

        # ── Columna 0: Encabezado, fecha e ID ──
        col0 = ctk.CTkFrame(card, fg_color="transparent")
        col0.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        lbl_fecha = ctk.CTkLabel(
            col0, text=f"📅 {fecha}", font=("Azeri Sans", 13, "bold"), text_color="#4FC3F7"
        )
        lbl_fecha.pack(anchor="w")
        
        lbl_id = ctk.CTkLabel(
            col0, text=f"ID: {reg_id[:8]}... (Semilla: {r.semilla_gcl})", font=("Azeri Sans", 10), text_color="#666666"
        )
        lbl_id.pack(anchor="w", pady=(3, 0))

        # ── Columna 1: Resumen rápido de métricas ──
        col1 = ctk.CTkFrame(card, fg_color="transparent")
        col1.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Grid interno para métricas alineadas
        col1.grid_columnconfigure(0, weight=1)
        col1.grid_columnconfigure(1, weight=1)
        
        # Fila 1: Peso lote y cantidad dispositivos
        lbl_lote = ctk.CTkLabel(
            col1, text=f"Lote: {r.b_kg_input:.2f} kg ({r.n_total} disp.)",
            font=("Azeri Sans", 12, "bold"), text_color="#E0E0E0"
        )
        lbl_lote.grid(row=0, column=0, sticky="w", pady=2)
        
        lbl_reventa = ctk.CTkLabel(
            col1, text=f"Reventa: {r.equipos_reventa} equipos",
            font=("Azeri Sans", 12), text_color="#AAAAAA"
        )
        lbl_reventa.grid(row=0, column=1, sticky="w", pady=2)
        
        # Fila 2: Valor recuperado
        lbl_valor = ctk.CTkLabel(
            col1, text=f"Valor Total: $ {r.valor_total:,.2f} ARS",
            font=("Azeri Sans", 12, "bold"), text_color="#81C784"
        )
        lbl_valor.grid(row=1, column=0, columnspan=2, sticky="w", pady=2)

        # ── Columna 2: Acciones ──
        col2 = ctk.CTkFrame(card, fg_color="transparent")
        col2.grid(row=0, column=2, padx=15, pady=15, sticky="e")

        # Botón Detalles
        btn_detalles = ctk.CTkButton(
            col2, text="🔍 Ver Informe",
            font=("Azeri Sans", 11, "bold"), width=110,
            command=lambda r_obj=r: self._ver_detalles(r_obj)
        )
        btn_detalles.pack(side="left", padx=5)

        # Botón Exportar Excel
        btn_exportar = ctk.CTkButton(
            col2, text="📥 Excel",
            font=("Azeri Sans", 11, "bold"), fg_color="#1E88E5", hover_color="#1565C0",
            width=80, command=lambda r_obj=r: self._exportar_individual(r_obj)
        )
        btn_exportar.pack(side="left", padx=5)

        # Botón Eliminar
        btn_eliminar = ctk.CTkButton(
            col2, text="❌",
            font=("Azeri Sans", 11, "bold"), fg_color="#D32F2F", hover_color="#C62828",
            width=30, command=lambda r_id=reg_id: self._eliminar_registro(r_id)
        )
        btn_eliminar.pack(side="left", padx=5)

    def _ver_detalles(self, resultado_obj):
        """Abre la ventana VentanaResultados con la simulación seleccionada."""
        if self._ventana_resultado_activa is not None:
            try:
                self._ventana_resultado_activa.destroy()
            except Exception as e:
                # registros de errores
                registrar_error("Error al destruir la ventana de resultados en VistaHistorial", e)
                pass

        self._ventana_resultado_activa = VentanaResultados(self, resultado_obj)

    def _exportar_individual(self, resultado_obj):
        """Invoca la exportación a Excel directamente para este objeto de resultados."""
        exportar_a_excel(resultado_obj, parent=self)

    def _eliminar_registro(self, registro_id: str):
        """Elimina un único registro del historial."""
        if messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar esta simulación del historial?"
        ):
            eliminado = HistorialSimulador.eliminar_registro(registro_id)
            if eliminado:
                self.recargar_historial()
            else:
                messagebox.showerror("Error", "No se pudo encontrar o eliminar la simulación.")

    def _borrar_todo(self):
        """Borra todo el historial tras confirmación."""
        if messagebox.askyesno(
            "Confirmar borrado completo",
            "⚠ ADVERTENCIA: ¿Está seguro de que desea borrar TODO el historial de simulaciones?\nEsta acción no se puede deshacer."
        ):
            HistorialSimulador.limpiar_historial()
            self.recargar_historial()
