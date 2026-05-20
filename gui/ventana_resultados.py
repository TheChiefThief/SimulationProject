"""
gui/ventana_resultados.py
--------------------------
Ventana Toplevel que muestra el informe de resultados de la simulación.

Contiene:
  - Panel izquierdo: informe textual (tabla de valores por componente,
    indicadores de eficiencia, semilla GCL usada)
  - Panel derecho: gráficos estáticos (matplotlib) embebidos en tkinter:
      * Gráfico de torta: distribución del valor por tipo de componente
      * Gráfico de barras: masa recuperada por material (kg)
"""

import tkinter as tk
import customtkinter as ctk
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.simulacion import ResultadoLote

matplotlib.use("TkAgg")

# Paleta de colores para los gráficos (consistente con el tema oscuro)
COLORES_TORTA = ["#4FC3F7", "#81C784", "#FFB74D", "#F06292", "#CE93D8", "#80CBC4"]
COLOR_BARRAS = "#4FC3F7"
COLOR_FONDO = "#1a2530"
COLOR_TEXTO = "#E0E0E0"
COLOR_GRID = "#2c3e50"


class VentanaResultados(ctk.CTkToplevel):
    """
    Ventana emergente con informe completo de resultados y gráficos.
    Se abre tras ejecutar una simulación exitosa.
    """

    def __init__(self, parent, resultado: ResultadoLote):
        super().__init__(parent)
        self.resultado = resultado

        self.title("Informe de Simulación — Resultados")
        self.geometry("1200x680")
        self.resizable(True, True)
        self.grab_set()  # Modal: bloquea la ventana principal mientras está abierta

        self._construir_layout()

    # ------------------------------------------------------------------
    # Construcción del layout principal
    # ------------------------------------------------------------------

    def _construir_layout(self):
        """Divide la ventana en panel de informe (izq) y gráficos (der)."""
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        panel_informe = ctk.CTkFrame(self, fg_color="#12192a", corner_radius=0)
        panel_informe.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        panel_graficos = ctk.CTkFrame(self, fg_color="#12192a", corner_radius=0)
        panel_graficos.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        self._construir_informe(panel_informe)
        self._construir_graficos(panel_graficos)

    # ------------------------------------------------------------------
    # Panel de informe textual
    # ------------------------------------------------------------------

    def _construir_informe(self, parent):
        """Construye el panel izquierdo con el informe textual de resultados."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        r = self.resultado

        # Título
        ctk.CTkLabel(
            scroll, text="📋 Informe de Resultados",
            font=("Arial", 20, "bold"), text_color="#4FC3F7"
        ).pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(
            scroll, text=f"Semilla GCL: {r.semilla_gcl}",
            font=("Arial", 11), text_color="#888888"
        ).pack(anchor="w", pady=(0, 20))

        # ── Sección: Lote procesado ──────────────────────────────────
        self._seccion(scroll, "Lote Procesado")
        datos_lote = [
            ("Cámaras ingresadas",  f"{r.n_camaras}"),
            ("DVRs ingresados",     f"{r.n_dvrs}"),
            ("Cámaras recuperables", f"{r.camaras_recuperables}"),
            ("Cámaras desguazadas", f"{r.camaras_desguazadas}"),
            ("DVRs recuperables",   f"{r.dvrs_recuperables}"),
            ("DVRs desguazados",    f"{r.dvrs_desguazados}"),
        ]
        for etiqueta, valor in datos_lote:
            self._fila(scroll, etiqueta, valor)

        # ── Sección: Valor por componente ────────────────────────────
        self._seccion(scroll, "Monetización por Componente")
        datos_valor = [
            ("Lentes recuperados",      f"$ {r.valor_lentes:>15,.2f}"),
            ("Placas (cámaras)",        f"$ {r.valor_placas_camara:>15,.2f}"),
            ("Placas (DVRs)",           f"$ {r.valor_placas_dvr:>15,.2f}"),
            ("Discos HDD",              f"$ {r.valor_hdd:>15,.2f}"),
            ("Plástico",                f"$ {r.valor_plastico:>15,.2f}"),
            ("Metal",                   f"$ {r.valor_metal:>15,.2f}"),
        ]
        for etiqueta, valor in datos_valor:
            self._fila(scroll, etiqueta, valor)

        # Total destacado
        self._separador(scroll)
        total_frame = ctk.CTkFrame(scroll, fg_color="#1e3a5f", corner_radius=8)
        total_frame.pack(fill="x", pady=(5, 15), padx=5)
        ctk.CTkLabel(
            total_frame, text="VALOR TOTAL RECUPERADO",
            font=("Arial", 13, "bold"), text_color="#4FC3F7"
        ).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(
            total_frame, text=f"$ {r.valor_total:,.2f} ARS",
            font=("Arial", 14, "bold"), text_color="#81C784"
        ).pack(side="right", padx=15, pady=10)

        # ── Sección: Masa recuperada ─────────────────────────────────
        self._seccion(scroll, "Masa Recuperada")
        datos_masa = [
            ("Plástico recuperado", f"{r.kg_plastico:.3f} kg"),
            ("Metal recuperado",    f"{r.kg_metal:.3f} kg"),
        ]
        for etiqueta, valor in datos_masa:
            self._fila(scroll, etiqueta, valor)

        # ── Sección: Indicadores operativos ─────────────────────────
        self._seccion(scroll, "Indicadores de Eficiencia Operativa")
        datos_ind = [
            ("Coef. de Productividad",  f"{r.coef_productividad:.4f} u/h/emp"),
            ("Eficacia",               f"{r.eficacia:.2f} %"),
            ("Eficiencia",             f"{r.eficiencia:.2f} %"),
            ("Rango de Mejora",        f"{r.rango_mejora:.2f} %"),
        ]
        for etiqueta, valor in datos_ind:
            self._fila(scroll, etiqueta, valor, destacar=(etiqueta == "Rango de Mejora"))

    def _seccion(self, parent, titulo: str):
        """Agrega un encabezado de sección al informe."""
        ctk.CTkLabel(
            parent, text=titulo,
            font=("Arial", 14, "bold"), text_color="#FFB74D"
        ).pack(anchor="w", pady=(15, 4))
        self._separador(parent)

    def _separador(self, parent):
        """Línea separadora horizontal."""
        sep = ctk.CTkFrame(parent, height=1, fg_color="#2c3e50")
        sep.pack(fill="x", pady=(0, 6))

    def _fila(self, parent, etiqueta: str, valor: str, destacar: bool = False):
        """Fila de dato: etiqueta a la izquierda, valor a la derecha."""
        fila = ctk.CTkFrame(parent, fg_color="transparent")
        fila.pack(fill="x", pady=2)
        color_val = "#F06292" if destacar else "#E0E0E0"
        ctk.CTkLabel(fila, text=etiqueta, font=("Arial", 12),
                     text_color="#AAAAAA").pack(side="left")
        ctk.CTkLabel(fila, text=valor, font=("Arial", 12, "bold"),
                     text_color=color_val).pack(side="right")

    # ------------------------------------------------------------------
    # Panel de gráficos
    # ------------------------------------------------------------------

    def _construir_graficos(self, parent):
        """Construye el panel derecho con los gráficos matplotlib estáticos."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        r = self.resultado

        # Crear figura con dos subplots
        fig, (ax_torta, ax_barras) = plt.subplots(
            1, 2, figsize=(8, 5),
            facecolor=COLOR_FONDO
        )
        fig.subplots_adjust(wspace=0.4, left=0.08, right=0.95, top=0.88, bottom=0.18)

        # ── Gráfico 1: Torta — distribución del valor por componente ──
        etiquetas = ["Lentes", "Placas Cám.", "Placas DVR", "HDD", "Plástico", "Metal"]
        valores = [
            r.valor_lentes,
            r.valor_placas_camara,
            r.valor_placas_dvr,
            r.valor_hdd,
            r.valor_plastico,
            r.valor_metal,
        ]

        # Filtrar componentes con valor > 0 para evitar secciones vacías
        pares = [(e, v, c) for e, v, c in zip(etiquetas, valores, COLORES_TORTA) if v > 0]
        if pares:
            etq_f, val_f, col_f = zip(*pares)
        else:
            etq_f, val_f, col_f = ["Sin datos"], [1], ["#555555"]

        wedges, texts, autotexts = ax_torta.pie(
            val_f,
            labels=None,
            autopct="%1.1f%%",
            colors=col_f,
            startangle=140,
            pctdistance=0.75,
            wedgeprops={"edgecolor": COLOR_FONDO, "linewidth": 1.5},
        )
        for at in autotexts:
            at.set_color(COLOR_FONDO)
            at.set_fontsize(9)
            at.set_fontweight("bold")

        ax_torta.set_facecolor(COLOR_FONDO)
        ax_torta.set_title("Distribución del Valor\nRecuperado", color=COLOR_TEXTO,
                            fontsize=11, fontweight="bold", pad=12)

        # Leyenda para la torta
        ax_torta.legend(
            wedges, etq_f,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.28),
            ncol=2,
            fontsize=8,
            frameon=False,
            labelcolor=COLOR_TEXTO,
        )

        # ── Gráfico 2: Barras — masa recuperada por material ──────────
        materiales = ["Plástico", "Metal"]
        masas = [r.kg_plastico, r.kg_metal]
        colores_barras = ["#81C784", "#4FC3F7"]
        x_pos = range(len(materiales))

        bars = ax_barras.bar(x_pos, masas, color=colores_barras,
                             edgecolor=COLOR_FONDO, linewidth=1.2, width=0.5)

        # Etiquetas de valor sobre cada barra
        for bar, masa in zip(bars, masas):
            ax_barras.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(masas) * 0.02,
                f"{masa:.2f} kg",
                ha="center", va="bottom",
                color=COLOR_TEXTO, fontsize=10, fontweight="bold"
            )

        ax_barras.set_facecolor(COLOR_FONDO)
        ax_barras.set_xticks(list(x_pos))
        ax_barras.set_xticklabels(materiales, color=COLOR_TEXTO, fontsize=11)
        ax_barras.set_ylabel("Masa (kg)", color=COLOR_TEXTO, fontsize=10)
        ax_barras.set_title("Masa Recuperada\npor Material", color=COLOR_TEXTO,
                            fontsize=11, fontweight="bold", pad=12)
        ax_barras.tick_params(colors=COLOR_TEXTO)
        ax_barras.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax_barras.spines["top"].set_visible(False)
        ax_barras.spines["right"].set_visible(False)
        for spine in ["left", "bottom"]:
            ax_barras.spines[spine].set_color(COLOR_GRID)
        ax_barras.yaxis.label.set_color(COLOR_TEXTO)
        ax_barras.tick_params(axis="y", colors=COLOR_TEXTO)
        ax_barras.set_ylim(0, max(masas) * 1.25 if max(masas) > 0 else 1)
        ax_barras.yaxis.grid(True, color=COLOR_GRID, linestyle="--", alpha=0.5)
        ax_barras.set_axisbelow(True)

        # Embeber figura en tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        plt.close(fig)  # Liberar memoria de la figura de matplotlib
