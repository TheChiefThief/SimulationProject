"""
gui/ventana_resultados.py
--------------------------
Ventana Toplevel que muestra el informe de resultados de la simulación.
Incluye gráficos estáticos (matplotlib) y botones de exportación a PDF y Excel.
"""

from tkinter import filedialog, messagebox
from datetime import datetime

import customtkinter as ctk
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

from core.logger import registrar_error
from core.resultados import ResultadoLote

matplotlib.use("TkAgg")

# ── Paleta visual (tema oscuro vivo pero serio) ────────────────────────────
COLORES_TORTA = ["#FF9800", "#90A4AE", "#FFD54F", "#4DB6AC"]
COLOR_FONDO = "#151b23"
COLOR_TEXTO = "#E0E0E0"
COLOR_GRID = "#2c3e50"
COLOR_PRIMARIO = "#29B6F6"
COLOR_SECUNDARIO = "#FFCA28"


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
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        panel_izq = ctk.CTkFrame(self, fg_color="#12192a", corner_radius=0)
        panel_izq.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        panel_der = ctk.CTkFrame(self, fg_color="#12192a", corner_radius=0)
        panel_der.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

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
        self._fila(scroll, "Peso ingresado (B)",     f"{r.b_kg_input:.2f} kg")
        self._fila(scroll, "Peso procesado real",    f"{r.peso_acumulado:.3f} kg")
        self._fila(scroll, "Total dispositivos (N)", f"{r.n_total}")
        self._fila(scroll, "Cámaras desguazadas (CantCam)", f"{r.cant_cam}")
        self._fila(scroll, "DVRs desguazados (CantDvr)",    f"{r.cant_dvr}")
        self._fila(scroll, "Cámaras reventa (CAMREC)",      f"{r.cam_rec}")
        self._fila(scroll, "DVRs reventa (DvrREC)",          f"{r.dvr_rec}")
        self._fila(scroll, "Total reventa",                  f"{r.equipos_reventa}")

        # ── Monetización ───────────────────────────────────────────────
        self._seccion(scroll, "Monetización de Materiales (ARS)")
        self._fila(scroll, "Cobre",    f"$ {r.valor_cobre:>15,.2f}")
        self._fila(scroll, "Aluminio", f"$ {r.valor_aluminio:>15,.2f}")
        self._fila(scroll, "Oro",      f"$ {r.valor_oro:>15,.2f}")
        self._fila(scroll, "Plástico", f"$ {r.valor_plastico:>15,.2f}")
        self._fila(scroll, "PMT (metales)", f"$ {r.pmt:>15,.2f}")

        self._separador(scroll)
        total_frame = ctk.CTkFrame(scroll, fg_color="#1e3a5f", corner_radius=8)
        total_frame.pack(fill="x", pady=(5, 15), padx=(5, 20))
        ctk.CTkLabel(total_frame, text="VALOR TOTAL (PMT + PT)",
                     font=("Azeri Sans", 13, "bold"), text_color="#4FC3F7"
                     ).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(total_frame, text=f"$ {r.valor_total:,.2f} ARS",
                     font=("Azeri Sans", 14, "bold"), text_color="#81C784"
                     ).pack(side="right", padx=15, pady=10)

        # ── Masa Recuperada ────────────────────────────────────────────
        self._seccion(scroll, "Masa Recuperada (kg)")
        self._fila(scroll, "MT — Material Total",    f"{r.mt:.3f} kg")
        self._fila(scroll, "PesoPlástico",           f"{r.peso_plastico:.3f} kg")
        self._fila(scroll, "PesoMetal (total)",      f"{r.peso_metal:.3f} kg")
        self._fila(scroll, "  Cobre",                f"{r.peso_cobre:.3f} kg")
        self._fila(scroll, "  Aluminio",             f"{r.peso_aluminio:.3f} kg")
        self._fila(scroll, "  Oro",                  f"{r.peso_oro:.4f} kg")
        self._fila(scroll, "PesoVidrio",             f"{r.peso_vidrio:.3f} kg")

        # ── Coeficientes de Recuperación ──────────────────────────────
        self._seccion(scroll, "Coeficientes de Recuperación")
        self._fila(scroll, "CrPlástico",  f"{r.cr_plastico:.2f} %")
        self._fila(scroll, "CrMetales",   f"{r.cr_metales:.2f} %")
        self._fila(scroll, "CrPlacas",    f"{r.cr_placas:.2f} %  (PlacasF={r.placas_f} / PlacasT={r.placas_t})")
        self._fila(scroll, "CrHDD",       f"{r.cr_hdd:.2f} %  (HDDF={r.hdd_f} / HDDT={r.hdd_t})")
        self._fila(scroll, "CrÓptica",    f"{r.cr_opt:.2f} %")

        # ── Indicadores de Ocupación y Productividad ───────────────────
        self._seccion(scroll, "Ocupación y Productividad por Estación")
        self._fila(scroll, "E1 — Revisión (D1=3m)",  f"Ocup: {r.ocupacion_1:.1f}%  |  Prod: {r.productividad_1:.2f}  |  C1={r.c1}")
        self._fila(scroll, "E2 — Cámara/Ópt (D2=2m)",f"Ocup: {r.ocupacion_2:.1f}%  |  Prod: {r.productividad_2:.2f}  |  C2={r.c2}")
        self._fila(scroll, "E3 — Ópt. Mat. (D3=27m)",f"Ocup: {r.ocupacion_3:.1f}%  |  Prod: {r.productividad_3:.2f}  |  C3={r.c3}")
        self._fila(scroll, "E4 — Placas (D4=90m)",   f"Ocup: {r.ocupacion_4:.1f}%  |  Prod: {r.productividad_4:.2f}  |  C4={r.c4}")
        self._fila(scroll, "E5 — Desarme DVR(D5=10m)",f"Ocup: {r.ocupacion_5:.1f}%  |  Prod: {r.productividad_5:.2f}  |  C5={r.c5}")
        self._fila(scroll, "E6 — HDD (D6=3m)",       f"Ocup: {r.ocupacion_6:.1f}%  |  Prod: {r.productividad_6:.2f}  |  C6={r.c6}")

        cuellos_str = ", ".join(r.cuellos_botella) if r.cuellos_botella else "Ninguno"
        self._fila(scroll, "Cuellos de Bot. (Oc>85%)", cuellos_str,
                   destacar=bool(r.cuellos_botella))

        # ── Demanda Simulada ───────────────────────────────────────────
        self._seccion(scroll, "Demanda Simulada — Poisson (λ=0.3)")
        self._fila(scroll, "Horas simuladas (h)", f"{r.horas_demanda}")
        self._fila(scroll, "Total clientes",       f"{r.clientes_totales}")

        # ── Botones de exportación ─────────────────────────────────────
        self._separador(scroll)
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 10), padx=(5, 20))

        ctk.CTkButton(
            btn_frame, text="📥  Exportar a Excel",
            font=("Azeri Sans", 14, "bold"), fg_color="#1E88E5", hover_color="#1565C0",
            width=200, command=self._exportar_excel
        ).pack(side="left", padx=(0, 10), fill="x", expand=True)

        ctk.CTkButton(
            btn_frame, text="📄  Exportar a PDF",
            font=("Azeri Sans", 14, "bold"), fg_color="#E53935", hover_color="#C62828",
            width=200, command=self._exportar_pdf
        ).pack(side="left", padx=(10, 0), fill="x", expand=True)
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

    def _fila(self, parent, etiqueta: str, valor: str, destacar: bool = False):
        fila = ctk.CTkFrame(parent, fg_color="transparent")
        fila.pack(fill="x", pady=2, padx=(5, 20))
        color_val = "#F06292" if destacar else "#E0E0E0"
        ctk.CTkLabel(fila, text=etiqueta, font=("Azeri Sans", 12),
                     text_color="#AAAAAA").pack(side="left")
        ctk.CTkLabel(fila, text=valor, font=("Azeri Sans", 12, "bold"),
                     text_color=color_val).pack(side="right")

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
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")],
                title="Exportar a Excel"
            )
            if not filepath:
                return

            r = self.resultado
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

            filas = [
                # Encabezado
                {"Categoría": "INFORME", "Métrica": "Fecha",         "Valor": fecha},
                {"Categoría": "INFORME", "Métrica": "Semilla GCL",   "Valor": r.semilla_gcl},
                {"Categoría": "", "Métrica": "", "Valor": ""},
                # Lote
                {"Categoría": "LOTE", "Métrica": "Peso ingresado B (kg)",  "Valor": r.b_kg_input},
                {"Categoría": "LOTE", "Métrica": "Peso procesado real (kg)","Valor": round(r.peso_acumulado, 3)},
                {"Categoría": "LOTE", "Métrica": "Total dispositivos (N)",  "Valor": r.n_total},
                {"Categoría": "LOTE", "Métrica": "CantCam (desguazadas)",   "Valor": r.cant_cam},
                {"Categoría": "LOTE", "Métrica": "CantDvr (desguazados)",   "Valor": r.cant_dvr},
                {"Categoría": "LOTE", "Métrica": "CAMREC (reventa)",        "Valor": r.cam_rec},
                {"Categoría": "LOTE", "Métrica": "DvrREC (reventa)",        "Valor": r.dvr_rec},
                {"Categoría": "LOTE", "Métrica": "Total reventa",           "Valor": r.equipos_reventa},
                {"Categoría": "", "Métrica": "", "Valor": ""},
                # Valores
                {"Categoría": "VALORES (ARS)", "Métrica": "Cobre",     "Valor": round(r.valor_cobre, 2)},
                {"Categoría": "VALORES (ARS)", "Métrica": "Aluminio",  "Valor": round(r.valor_aluminio, 2)},
                {"Categoría": "VALORES (ARS)", "Métrica": "Oro",       "Valor": round(r.valor_oro, 2)},
                {"Categoría": "VALORES (ARS)", "Métrica": "Plástico",  "Valor": round(r.valor_plastico, 2)},
                {"Categoría": "VALORES (ARS)", "Métrica": "PMT",       "Valor": round(r.pmt, 2)},
                {"Categoría": "VALORES (ARS)", "Métrica": "PT",        "Valor": round(r.pt, 2)},
                {"Categoría": "VALORES (ARS)", "Métrica": "TOTAL",     "Valor": round(r.valor_total, 2)},
                {"Categoría": "", "Métrica": "", "Valor": ""},
                # Masa
                {"Categoría": "MASA (kg)", "Métrica": "MT (total)",   "Valor": round(r.mt, 3)},
                {"Categoría": "MASA (kg)", "Métrica": "PesoPlastico", "Valor": round(r.peso_plastico, 3)},
                {"Categoría": "MASA (kg)", "Métrica": "PesoMetal",    "Valor": round(r.peso_metal, 3)},
                {"Categoría": "MASA (kg)", "Métrica": "PesoVidrio",   "Valor": round(r.peso_vidrio, 3)},
                {"Categoría": "", "Métrica": "", "Valor": ""},
                # Coeficientes
                {"Categoría": "COEFICIENTES", "Métrica": "CrPlastico (%)", "Valor": round(r.cr_plastico, 2)},
                {"Categoría": "COEFICIENTES", "Métrica": "CrMetales (%)",  "Valor": round(r.cr_metales, 2)},
                {"Categoría": "COEFICIENTES", "Métrica": "CrPlacas (%)",   "Valor": round(r.cr_placas, 2)},
                {"Categoría": "COEFICIENTES", "Métrica": "CrHDD (%)",      "Valor": round(r.cr_hdd, 2)},
                {"Categoría": "COEFICIENTES", "Métrica": "CrOptica (%)",   "Valor": round(r.cr_opt, 2)},
                {"Categoría": "", "Métrica": "", "Valor": ""},
                # Estaciones (Ocupación)
                {"Categoría": "OCUPACIÓN (%)", "Métrica": "E1 — Revisión",      "Valor": round(r.ocupacion_1, 1)},
                {"Categoría": "OCUPACIÓN (%)", "Métrica": "E2 — Cámara/Ópt",   "Valor": round(r.ocupacion_2, 1)},
                {"Categoría": "OCUPACIÓN (%)", "Métrica": "E3 — Ópt. Mat",      "Valor": round(r.ocupacion_3, 1)},
                {"Categoría": "OCUPACIÓN (%)", "Métrica": "E4 — Placas",        "Valor": round(r.ocupacion_4, 1)},
                {"Categoría": "OCUPACIÓN (%)", "Métrica": "E5 — Desarme DVR",   "Valor": round(r.ocupacion_5, 1)},
                {"Categoría": "OCUPACIÓN (%)", "Métrica": "E6 — HDD",           "Valor": round(r.ocupacion_6, 1)},
                {"Categoría": "OCUPACIÓN (%)", "Métrica": "Cuellos de botella", "Valor": ", ".join(r.cuellos_botella) or "Ninguno"},
                {"Categoría": "", "Métrica": "", "Valor": ""},
                # Estaciones (Productividad)
                {"Categoría": "PRODUCTIVIDAD", "Métrica": "E1 — Revisión",      "Valor": round(r.productividad_1, 2)},
                {"Categoría": "PRODUCTIVIDAD", "Métrica": "E2 — Cámara/Ópt",   "Valor": round(r.productividad_2, 2)},
                {"Categoría": "PRODUCTIVIDAD", "Métrica": "E3 — Ópt. Mat",      "Valor": round(r.productividad_3, 2)},
                {"Categoría": "PRODUCTIVIDAD", "Métrica": "E4 — Placas",        "Valor": round(r.productividad_4, 2)},
                {"Categoría": "PRODUCTIVIDAD", "Métrica": "E5 — Desarme DVR",   "Valor": round(r.productividad_5, 2)},
                {"Categoría": "PRODUCTIVIDAD", "Métrica": "E6 — HDD",           "Valor": round(r.productividad_6, 2)},
                {"Categoría": "", "Métrica": "", "Valor": ""},
                # Demanda
                {"Categoría": "DEMANDA", "Métrica": "Horas simuladas", "Valor": r.horas_demanda},
                {"Categoría": "DEMANDA", "Métrica": "Clientes totales","Valor": r.clientes_totales},
            ]

            df = pd.DataFrame(filas)
            with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Reporte", index=False)

            messagebox.showinfo("Exportación Exitosa", f"Archivo Excel guardado en:\n{filepath}")

        except Exception as e:
            # registros de errores
            registrar_error("Error al exportar los resultados a Excel en VentanaResultados", e)
            messagebox.showwarning("Aviso", f"No se pudo exportar a Excel:\n{e}")

    # ------------------------------------------------------------------
    # Exportación a PDF
    # ------------------------------------------------------------------

    def _exportar_pdf(self):
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("Error", "La librería fpdf no está instalada. Ejecute: pip install fpdf")
            return

        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
                title="Exportar a PDF"
            )
            if not filepath:
                return

            r = self.resultado
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

            def safe_str(text):
                # fpdf uses latin-1 by default. Replaces em-dash and en-dash with standard hyphen.
                return str(text).replace("\u2014", "-").replace("\u2013", "-").encode('latin-1', 'replace').decode('latin-1')

            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, safe_str("Informe de Simulacion - Resultados Generales"), ln=True, align='C')
            
            # Subtítulo
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 10, safe_str(f"Fecha: {fecha} | Semilla GCL: {r.semilla_gcl}"), ln=True, align='C')
            
            def add_section(title):
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 12)
                pdf.set_text_color(0, 51, 102) # Azul oscuro
                pdf.cell(0, 8, safe_str(title), ln=True, align='L')
                pdf.set_font("Arial", '', 11)
                pdf.set_text_color(0, 0, 0)
                
            def add_row(label, value):
                pdf.cell(100, 6, safe_str(label), ln=False)
                pdf.set_font("Arial", 'B', 11)
                pdf.cell(90, 6, safe_str(value), ln=True, align='R')
                pdf.set_font("Arial", '', 11)

            # Lote Procesado
            add_section("Lote Procesado")
            add_row("Peso ingresado (B)", f"{r.b_kg_input:.2f} kg")
            add_row("Peso procesado real", f"{r.peso_acumulado:.3f} kg")
            add_row("Total dispositivos (N)", f"{r.n_total}")
            add_row("Camaras desguazadas (CantCam)", f"{r.cant_cam}")
            add_row("DVRs desguazados (CantDvr)", f"{r.cant_dvr}")
            add_row("Camaras reventa (CAMREC)", f"{r.cam_rec}")
            add_row("DVRs reventa (DvrREC)", f"{r.dvr_rec}")
            add_row("Total reventa", f"{r.equipos_reventa}")

            # Monetización
            add_section("Monetizacion de Materiales (ARS)")
            add_row("Cobre", f"$ {r.valor_cobre:,.2f}")
            add_row("Aluminio", f"$ {r.valor_aluminio:,.2f}")
            add_row("Oro", f"$ {r.valor_oro:,.2f}")
            add_row("Plastico", f"$ {r.valor_plastico:,.2f}")
            add_row("PMT (metales)", f"$ {r.pmt:,.2f}")
            
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 11)
            pdf.set_text_color(0, 102, 51)
            pdf.cell(100, 8, safe_str("VALOR TOTAL (PMT + PT)"), ln=False)
            pdf.cell(90, 8, safe_str(f"$ {r.valor_total:,.2f}"), ln=True, align='R')
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 11)

            # Masa
            add_section("Masa Recuperada (kg)")
            add_row("MT - Material Total", f"{r.mt:.3f} kg")
            add_row("PesoPlastico", f"{r.peso_plastico:.3f} kg")
            add_row("PesoMetal (total)", f"{r.peso_metal:.3f} kg")
            add_row("  Cobre", f"{r.peso_cobre:.3f} kg")
            add_row("  Aluminio", f"{r.peso_aluminio:.3f} kg")
            add_row("  Oro", f"{r.peso_oro:.4f} kg")
            add_row("PesoVidrio", f"{r.peso_vidrio:.3f} kg")

            # Coeficientes
            add_section("Coeficientes de Recuperacion")
            add_row("CrPlastico", f"{r.cr_plastico:.2f} %")
            add_row("CrMetales", f"{r.cr_metales:.2f} %")
            add_row("CrPlacas", f"{r.cr_placas:.2f} % (PlacasF={r.placas_f} / PlacasT={r.placas_t})")
            add_row("CrHDD", f"{r.cr_hdd:.2f} % (HDDF={r.hdd_f} / HDDT={r.hdd_t})")
            add_row("CrOptica", f"{r.cr_opt:.2f} %")

            # Ocupacion y Productividad
            add_section("Ocupacion y Productividad")
            add_row("E1 - Revision", f"Ocup: {r.ocupacion_1:.1f}% | Prod: {r.productividad_1:.2f} | C1={r.c1}")
            add_row("E2 - Camara/Opt", f"Ocup: {r.ocupacion_2:.1f}% | Prod: {r.productividad_2:.2f} | C2={r.c2}")
            add_row("E3 - Opt. Mat.", f"Ocup: {r.ocupacion_3:.1f}% | Prod: {r.productividad_3:.2f} | C3={r.c3}")
            add_row("E4 - Placas", f"Ocup: {r.ocupacion_4:.1f}% | Prod: {r.productividad_4:.2f} | C4={r.c4}")
            add_row("E5 - Desarme DVR", f"Ocup: {r.ocupacion_5:.1f}% | Prod: {r.productividad_5:.2f} | C5={r.c5}")
            add_row("E6 - HDD", f"Ocup: {r.ocupacion_6:.1f}% | Prod: {r.productividad_6:.2f} | C6={r.c6}")
            
            cuellos_str = ", ".join(r.cuellos_botella) if r.cuellos_botella else "Ninguno"
            add_row("Cuellos de Botella", cuellos_str)

            # Demanda
            add_section("Demanda Simulada")
            add_row("Horas simuladas", str(r.horas_demanda))
            add_row("Total clientes", str(r.clientes_totales))

            pdf.output(filepath)

            messagebox.showinfo("Exportacion Exitosa", f"Archivo PDF guardado en:\n{filepath}")

        except Exception as e:
            registrar_error("Error al exportar los resultados a PDF en VentanaResultados", e)
            messagebox.showwarning("Aviso", f"No se pudo exportar a PDF:\n{e}")
