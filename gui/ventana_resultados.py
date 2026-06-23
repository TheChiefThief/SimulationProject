from tkinter import filedialog, messagebox
from datetime import datetime

import customtkinter as ctk
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.logger import registrar_error
from core.resultados import ResultadoLote
from core.exportadores import exportar_a_excel
from core.estimador_tiempo import estimar_tiempo_procesamiento, formatear_tiempo
from gui.componentes import CTKKeyValueRow

matplotlib.use("TkAgg")

# ── Paleta visual (tema oscuro vivo pero serio) ────────────────────────────
COLORES_TORTA = ["#FF9800", "#90A4AE", "#FFD54F", "#4DB6AC"]
COLOR_FONDO = "#151b23"
COLOR_TEXTO = "#E0E0E0"
COLOR_GRID = "#2c3e50"
COLOR_PRIMARIO = "#29B6F6"
COLOR_SECUNDARIO = "#FFCA28"


import tkinter as tk

class VentanaResultados(ctk.CTkToplevel):
    """
    Ventana emergente modal con informe completo, gráficos y exportación.
    Se abre tras ejecutar una simulación exitosa.
    """

    def __init__(self, parent, resultado: ResultadoLote):
        super().__init__(parent)
        self.resultado = resultado

        self.title("Informe de Simulación — Resultados Generales")
        self.geometry("1250x740")
        self.resizable(True, True)
        self.grab_set()

        self._construir_layout()

    # ------------------------------------------------------------------
    # Layout principal
    # ------------------------------------------------------------------

    def _construir_layout(self):
        
        pw = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#151b23", bd=0, sashwidth=6, sashrelief=tk.FLAT)
        pw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        try:
            pw.configure(sashcursor="sb_h_double_arrow")
        except Exception:
            try:
                pw.configure(sashcursor="size_we")
            except Exception:
                pass

        panel_izq = ctk.CTkFrame(pw, fg_color="#12192a", corner_radius=8)
        panel_der = ctk.CTkFrame(pw, fg_color="#12192a", corner_radius=8)

        pw.add(panel_izq, minsize=450, stretch="always")
        pw.add(panel_der, minsize=500, stretch="always")

        self._construir_informe(panel_izq)
        self._construir_graficos(panel_der)

    # ------------------------------------------------------------------
    # Panel de informe textual (izquierdo)
    # ------------------------------------------------------------------

    def _construir_informe(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        r = self.resultado

        ctk.CTkLabel(scroll, text="📋 Informe de Resultados",
                     font=("Azeri Sans", 20, "bold"), text_color="#4FC3F7"
                     ).pack(anchor="w", pady=(0, 3), padx=(5, 20))
        ctk.CTkLabel(scroll, text=f"Semilla GCL: {r.semilla_gcl}",
                     font=("Azeri Sans", 11), text_color="#888888"
                     ).pack(anchor="w", pady=(0, 16), padx=(5, 20))

        # ── Lote Procesado ─────────────────────────────────────────────
        self._seccion(scroll, "Lote Procesado")
        CTKKeyValueRow(scroll, "Peso ingresado (B)",     f"{r.b_kg_input:.2f} kg")
        CTKKeyValueRow(scroll, "Peso procesado real",    f"{r.peso_acumulado:.3f} kg")
        CTKKeyValueRow(scroll, "Total dispositivos (N)", f"{r.n_total}")
        CTKKeyValueRow(scroll, "Cámaras desguazadas (CantCam)", f"{r.cant_cam}")
        CTKKeyValueRow(scroll, "DVRs desguazados (CantDvr)",    f"{r.cant_dvr}")
        CTKKeyValueRow(scroll, "Cámaras reventa (CAMREC)",      f"{r.cam_rec}")
        CTKKeyValueRow(scroll, "DVRs reventa (DvrREC)",          f"{r.dvr_rec}")
        CTKKeyValueRow(scroll, "Total equipos a reventa", r.equipos_reventa)

        # ── Estimación de Tiempo ───────────────────────────────────────
        self._separador(scroll)
        tiempo_minutos = estimar_tiempo_procesamiento(r)
        tiempo_texto = formatear_tiempo(tiempo_minutos, r.horas_jornada)
        CTKKeyValueRow(scroll, "⏳ Tiempo est. de proceso", tiempo_texto, destacar=True)

        # ── Monetización ───────────────────────────────────────────────
        self._seccion(scroll, "Monetización de Materiales (ARS)")
        CTKKeyValueRow(scroll, "Cobre",    f"$ {r.valor_cobre:>15,.2f}")
        CTKKeyValueRow(scroll, "Aluminio", f"$ {r.valor_aluminio:>15,.2f}")
        CTKKeyValueRow(scroll, "Oro",      f"$ {r.valor_oro:>15,.2f}")
        CTKKeyValueRow(scroll, "Plástico", f"$ {r.valor_plastico:>15,.2f}")
        CTKKeyValueRow(scroll, "HDD",      f"$ {r.valor_hdd:>15,.2f}")
        CTKKeyValueRow(scroll, "Placas",   f"$ {r.valor_placas:>15,.2f}")
        CTKKeyValueRow(scroll, "Óptica",   f"$ {r.valor_optica:>15,.2f}")
        CTKKeyValueRow(scroll, "PMT (metales)", f"$ {r.pmt:>15,.2f}")

        self._separador(scroll)
        total_frame = ctk.CTkFrame(scroll, fg_color="#1e3a5f", corner_radius=8)
        total_frame.pack(fill="x", pady=(5, 15), padx=(5, 20))
        ctk.CTkLabel(total_frame, text="Valor Total:",
                     font=("Azeri Sans", 13, "bold"), text_color="#4FC3F7"
                     ).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(total_frame, text=f"$ {r.valor_total:,.2f} ARS",
                     font=("Azeri Sans", 14, "bold"), text_color="#81C784"
                     ).pack(side="right", padx=15, pady=10)

        # ── Masa Recuperada ────────────────────────────────────────────
        self._seccion(scroll, "Masa Recuperada (kg)")
        CTKKeyValueRow(scroll, "MT — Material Total",    f"{r.mt:.3f} kg")
        CTKKeyValueRow(scroll, "PesoPlástico",           f"{r.peso_plastico:.3f} kg")
        CTKKeyValueRow(scroll, "PesoMetal (total)",      f"{r.peso_metal:.3f} kg")
        CTKKeyValueRow(scroll, "  Cobre",                f"{r.peso_cobre:.3f} kg")
        CTKKeyValueRow(scroll, "  Aluminio",             f"{r.peso_aluminio:.3f} kg")
        CTKKeyValueRow(scroll, "  Oro",                  f"{r.peso_oro:.4f} kg")
        CTKKeyValueRow(scroll, "PesoVidrio",             f"{r.peso_vidrio:.3f} kg")

        # ── Coeficientes de Recuperación ──────────────────────────────
        self._seccion(scroll, "Coeficientes de Recuperación")
        CTKKeyValueRow(scroll, "CrPlástico",  f"{r.cr_plastico:.2f} %")
        CTKKeyValueRow(scroll, "CrMetales",   f"{r.cr_metales:.2f} %")
        CTKKeyValueRow(scroll, "CrPlacas",    f"{r.cr_placas:.2f} %  (PlacasF={r.placas_f} / PlacasT={r.placas_t})")
        CTKKeyValueRow(scroll, "CrHDD",       f"{r.cr_hdd:.2f} %  (HDDF={r.hdd_f} / HDDT={r.hdd_t})")
        CTKKeyValueRow(scroll, "CrÓptica",    f"{r.cr_opt:.2f} %")

        # ── Indicadores de Ocupación y Productividad ───────────────────
        self._seccion(scroll, "Ocupación y Productividad por Estación")
        CTKKeyValueRow(scroll, "E1 — Revisión (D1=3m)",  f"Ocup: {r.ocupacion_1:.1f}%  |  Prod: {r.productividad_1:.2f}  |  C1={r.c1}")
        CTKKeyValueRow(scroll, "E2 — Cámara/Ópt (D2=2m)",f"Ocup: {r.ocupacion_2:.1f}%  |  Prod: {r.productividad_2:.2f}  |  C2={r.c2}")
        CTKKeyValueRow(scroll, "E3 — Ópt. Mat. (D3=27m)",f"Ocup: {r.ocupacion_3:.1f}%  |  Prod: {r.productividad_3:.2f}  |  C3={r.c3}")
        CTKKeyValueRow(scroll, "E4 — Placas (D4=90m)",   f"Ocup: {r.ocupacion_4:.1f}%  |  Prod: {r.productividad_4:.2f}  |  C4={r.c4}")
        CTKKeyValueRow(scroll, "E5 — Desarme DVR(D5=10m)",f"Ocup: {r.ocupacion_5:.1f}%  |  Prod: {r.productividad_5:.2f}  |  C5={r.c5}")
        CTKKeyValueRow(scroll, "E6 — HDD (D6=3m)",       f"Ocup: {r.ocupacion_6:.1f}%  |  Prod: {r.productividad_6:.2f}  |  C6={r.c6}")

        cuellos_str = ", ".join(r.cuellos_botella) if r.cuellos_botella else "Ninguno"
        CTKKeyValueRow(scroll, "Cuellos de Bot. (Oc>85%)", cuellos_str,
                   destacar=bool(r.cuellos_botella))

        # ── Botones de exportación ─────────────────────────────────────
        self._separador(scroll)
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 10), padx=(5, 20))

        ctk.CTkButton(
            btn_frame, text="📥  Exportar a Excel",
            font=("Azeri Sans", 14, "bold"), fg_color="#1E88E5", hover_color="#1565C0",
            width=200, command=self._exportar_excel
        ).pack(side="left", padx=(0, 10), fill="x", expand=True)

    # ------------------------------------------------------------------
    # Helpers de UI del informe
    # ------------------------------------------------------------------

    def _seccion(self, parent, titulo: str):
        ctk.CTkLabel(parent, text=titulo, font=("Azeri Sans", 14, "bold"),
                     text_color="#FFB74D"
                     ).pack(anchor="w", pady=(15, 4), padx=(5, 20))
        self._separador(parent)

    def _separador(self, parent):
        sep = ctk.CTkFrame(parent, height=1, fg_color="#2c3e50")
        sep.pack(fill="x", pady=(0, 6), padx=(5, 20))

    # ------------------------------------------------------------------
    # Gráficos estáticos (panel derecho)
    # ------------------------------------------------------------------

    def _construir_graficos(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        r = self.resultado
        fig, (ax_torta, ax_barras) = plt.subplots(
            1, 2, figsize=(8, 5), facecolor=COLOR_FONDO
        )
        fig.subplots_adjust(wspace=0.45, left=0.08, right=0.95, top=0.88, bottom=0.20)

        # ── Torta: distribución del valor por material ─────────────────
        etiquetas = ["Cobre", "Aluminio", "Oro", "Plástico"]
        valores = [r.valor_cobre, r.valor_aluminio, r.valor_oro, r.valor_plastico]
        pares = [(e, v, c) for e, v, c in zip(etiquetas, valores, COLORES_TORTA) if v > 0]
        if pares:
            etq_f, val_f, col_f = zip(*pares)
        else:
            etq_f, val_f, col_f = ["Sin datos"], [1], ["#555555"]

        wedges, _, autotexts = ax_torta.pie(
            val_f, labels=None, autopct="%1.1f%%", colors=col_f,
            startangle=140, pctdistance=0.75,
            wedgeprops={"edgecolor": COLOR_FONDO, "linewidth": 1.5}
        )
        for at in autotexts:
            at.set_color(COLOR_FONDO)
            at.set_fontsize(9)
            at.set_fontweight("bold")
        ax_torta.set_facecolor(COLOR_FONDO)
        ax_torta.set_title("Distribución del Valor\nRecuperado",
                            color=COLOR_TEXTO, fontsize=11, fontweight="bold", pad=12)
        ax_torta.legend(wedges, etq_f, loc="lower center",
                        bbox_to_anchor=(0.5, -0.30), ncol=2,
                        fontsize=8, frameon=False, labelcolor=COLOR_TEXTO)

        # ── Barras: masa recuperada por material ───────────────────────
        materiales = ["Cobre", "Aluminio", "Oro", "Plástico"]
        masas = [r.peso_cobre, r.peso_aluminio, r.peso_oro, r.peso_plastico]
        x_pos = range(len(materiales))

        bars = ax_barras.bar(x_pos, masas, color=COLORES_TORTA,
                              edgecolor=COLOR_FONDO, linewidth=1.2, width=0.55)
        max_masa = max(masas) if max(masas) > 0 else 1
        for bar, masa in zip(bars, masas):
            ax_barras.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max_masa * 0.02,
                f"{masa:.3f}",
                ha="center", va="bottom",
                color=COLOR_TEXTO, fontsize=9, fontweight="bold"
            )
        ax_barras.set_facecolor(COLOR_FONDO)
        ax_barras.set_xticks(list(x_pos))
        ax_barras.set_xticklabels(["Cu", "Al", "Au", "Plast."],
                                   color=COLOR_TEXTO, fontsize=10)
        ax_barras.set_ylabel("Masa (kg)", color=COLOR_TEXTO, fontsize=10)
        ax_barras.set_title("Masa Recuperada\npor Material",
                             color=COLOR_TEXTO, fontsize=11, fontweight="bold", pad=12)
        ax_barras.tick_params(colors=COLOR_TEXTO)
        ax_barras.spines["top"].set_visible(False)
        ax_barras.spines["right"].set_visible(False)
        for spine in ["left", "bottom"]:
            ax_barras.spines[spine].set_color(COLOR_GRID)
        ax_barras.set_ylim(0, max_masa * 1.28)
        ax_barras.yaxis.grid(True, color=COLOR_GRID, linestyle="--", alpha=0.5)
        ax_barras.set_axisbelow(True)
        ax_barras.tick_params(axis="y", colors=COLOR_TEXTO)

        ax_barras.text(
            0.5, -0.35, "Distribución porcentual de los\ningresos generados por la venta\nde materiales recuperados.",
            ha="center", va="top", color="#888888", fontsize=9, transform=ax_torta.transAxes
        )

        ax_barras.text(
            0.5, -0.22, "Cantidad neta en kilogramos de cada material\nobtenido tras el desguace.",
            ha="center", va="top", color="#888888", fontsize=9, transform=ax_barras.transAxes
        )

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        plt.close(fig)

    # ------------------------------------------------------------------
    # Exportación a Excel
    # ------------------------------------------------------------------

    def _exportar_excel(self):
        exportar_a_excel(self.resultado, parent=self)
