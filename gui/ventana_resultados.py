"""
gui/ventana_resultados.py
--------------------------
Ventana Toplevel que muestra el informe de resultados de la simulación.
Alineado al nuevo flujo general de diagrama.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

from core.resultados import ResultadoLote

matplotlib.use("TkAgg")

COLORES_TORTA = ["#FFB74D", "#90A4AE", "#FDD835", "#81C784"]
COLOR_BARRAS = "#4FC3F7"
COLOR_FONDO = "#1a2530"
COLOR_TEXTO = "#E0E0E0"
COLOR_GRID = "#2c3e50"


class VentanaResultados(ctk.CTkToplevel):
    def __init__(self, parent, resultado: ResultadoLote):
        super().__init__(parent)
        self.resultado = resultado

        self.title("Informe de Simulación — Resultados Generales")
        self.geometry("1200x720")
        self.resizable(True, True)
        self.grab_set()

        self._construir_layout()

    def _construir_layout(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        panel_informe = ctk.CTkFrame(self, fg_color="#12192a", corner_radius=0)
        panel_informe.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        panel_graficos = ctk.CTkFrame(self, fg_color="#12192a", corner_radius=0)
        panel_graficos.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

        self._construir_informe(panel_informe)
        self._construir_graficos(panel_graficos)

    def _construir_informe(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        r = self.resultado

        ctk.CTkLabel(
            scroll, text="📋 Informe de Resultados",
            font=("Arial", 20, "bold"), text_color="#4FC3F7"
        ).pack(anchor="w", pady=(0, 5), padx=(5, 20))

        ctk.CTkLabel(
            scroll, text=f"Semilla GCL: {r.semilla_gcl}",
            font=("Arial", 11), text_color="#888888"
        ).pack(anchor="w", pady=(0, 20), padx=(5, 20))

        # ── Sección: Lote procesado ──
        self._seccion(scroll, "Lote Procesado")
        datos_lote = [
            ("Total Ingresados (N)",  f"{r.n_total}"),
            ("Equipos para Reventa", f"{r.equipos_reventa}"),
            ("  - Cámaras Reventa", f"{r.camaras_reventa}"),
            ("  - DVRs Reventa", f"{r.dvrs_reventa}"),
            ("Cámaras Desguazadas", f"{r.camaras_desguazadas}"),
            ("DVRs Desguazados",    f"{r.dvrs_desguazados}"),
        ]
        for etiqueta, valor in datos_lote:
            self._fila(scroll, etiqueta, valor)

        # ── Sección: Valor por componente ──
        self._seccion(scroll, "Monetización de Materiales")
        datos_valor = [
            ("Cobre",      f"$ {r.valor_cobre:>15,.2f}"),
            ("Aluminio",   f"$ {r.valor_aluminio:>15,.2f}"),
            ("Oro",        f"$ {r.valor_oro:>15,.2f}"),
            ("Plástico",   f"$ {r.valor_plastico:>15,.2f}"),
            ("Subtotal Materiales (PMT)", f"$ {r.pmt:>15,.2f}"),
        ]
        for etiqueta, valor in datos_valor:
            self._fila(scroll, etiqueta, valor)

        # Total destacado
        self._separador(scroll)
        total_frame = ctk.CTkFrame(scroll, fg_color="#1e3a5f", corner_radius=8)
        total_frame.pack(fill="x", pady=(5, 15), padx=(5, 20))
        ctk.CTkLabel(
            total_frame, text="VALOR TOTAL (PMT + PT)",
            font=("Arial", 13, "bold"), text_color="#4FC3F7"
        ).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(
            total_frame, text=f"$ {r.valor_total:,.2f} ARS",
            font=("Arial", 14, "bold"), text_color="#81C784"
        ).pack(side="right", padx=15, pady=10)

        # ── Sección: Masa recuperada ──
        self._seccion(scroll, "Masa Recuperada")
        datos_masa = [
            ("Masa Total Procesada", f"{r.mt:.3f} kg"),
            ("Cobre",      f"{r.peso_cobre:.3f} kg"),
            ("Aluminio",   f"{r.peso_aluminio:.3f} kg"),
            ("Oro",        f"{r.peso_oro:.3f} kg"),
            ("Plástico",   f"{r.peso_plastico:.3f} kg"),
            ("Total Metal",f"{r.peso_metal:.3f} kg"),
            ("Vidrio (Óptica)", f"{r.peso_vidrio:.3f} kg"),
        ]
        for etiqueta, valor in datos_masa:
            self._fila(scroll, etiqueta, valor)

        # ── Sección: Coeficientes de Recuperación ──
        self._seccion(scroll, "Coeficientes de Recuperación")
        datos_coef = [
            ("CrPlástico", f"{r.cr_plastico:.2f} %"),
            ("CrMetales",  f"{r.cr_metales:.2f} %"),
            ("CrPlacas",   f"{r.cr_placas:.2f} %"),
            ("CrHDD",      f"{r.cr_hdd:.2f} %"),
            ("CrÓptica",   f"{r.cr_opt:.2f} %"),
        ]
        for etiqueta, valor in datos_coef:
            self._fila(scroll, etiqueta, valor)

        # ── Sección: Indicadores operativos ──
        self._seccion(scroll, "Indicadores de Ocupación y Tiempos")
        datos_ind = [
            ("Est. 1 Revisión (PE1)", f"{r.pe1*100:.1f} % (T: {r.tdr:.1f} m)"),
            ("Est. 2 Óptica (PE2)", f"{r.pe2*100:.1f} % (T: {r.tdo:.1f} m)"),
            ("Est. 3 Ópt. Mat. (PE3)", f"{r.pe3*100:.1f} % (T: {r.tco:.1f} m)"),
            ("Est. 4 Placas (PE4)", f"{r.pe4*100:.1f} % (T: {r.tp:.1f} m)"),
            ("Est. 5 DVR (PE5)", f"{r.pe5*100:.1f} % (T: {r.tdd:.1f} m)"),
            ("Est. 6 HDD (PE6)", f"{r.pe6*100:.1f} % (T: {r.thd:.1f} m)"),
        ]
        for etiqueta, valor in datos_ind:
            self._fila(scroll, etiqueta, valor)
            
        cuellos_str = ", ".join(r.cuellos_botella) if r.cuellos_botella else "Ninguno"
        self._fila(scroll, "Cuellos de Botella", cuellos_str, destacar=bool(r.cuellos_botella))
        
        self._seccion(scroll, "Demanda Simulada (Poisson)")
        self._fila(scroll, "Horas Simuladas (h)", f"{r.horas_demanda}")
        self._fila(scroll, "Total Clientes", f"{r.clientes_totales}")

        # Botón Exportar
        self._separador(scroll)
        btn_exportar = ctk.CTkButton(
            scroll, text="📥  Exportar a Excel",
            font=("Arial", 14, "bold"), fg_color="#388E3C", hover_color="#2E7D32",
            command=self._exportar_excel
        )
        btn_exportar.pack(pady=(15, 10))

    def _exportar_excel(self):
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                title="Exportar Resultados a Excel"
            )
            if not filepath:
                return
            
            r = self.resultado
            datos_completos = [
                {"Categoría": "LOTE", "Métrica": "Total Ingresados", "Valor": r.n_total},
                {"Categoría": "LOTE", "Métrica": "Cámaras Desguazadas", "Valor": r.camaras_desguazadas},
                {"Categoría": "LOTE", "Métrica": "DVRs Desguazados", "Valor": r.dvrs_desguazados},
                {"Categoría": "LOTE", "Métrica": "Total Reventa", "Valor": r.equipos_reventa},
                {"Categoría": "", "Métrica": "", "Valor": ""},
                {"Categoría": "VALORES (ARS)", "Métrica": "Cobre", "Valor": r.valor_cobre},
                {"Categoría": "VALORES (ARS)", "Métrica": "Aluminio", "Valor": r.valor_aluminio},
                {"Categoría": "VALORES (ARS)", "Métrica": "Oro", "Valor": r.valor_oro},
                {"Categoría": "VALORES (ARS)", "Métrica": "Plástico", "Valor": r.valor_plastico},
                {"Categoría": "VALORES (ARS)", "Métrica": "Total", "Valor": r.valor_total},
                {"Categoría": "", "Métrica": "", "Valor": ""},
                {"Categoría": "COEFICIENTES", "Métrica": "CrPlástico (%)", "Valor": r.cr_plastico},
                {"Categoría": "COEFICIENTES", "Métrica": "CrMetales (%)", "Valor": r.cr_metales},
                {"Categoría": "COEFICIENTES", "Métrica": "CrPlacas (%)", "Valor": r.cr_placas},
                {"Categoría": "COEFICIENTES", "Métrica": "CrHDD (%)", "Valor": r.cr_hdd},
                {"Categoría": "COEFICIENTES", "Métrica": "CrÓptica (%)", "Valor": r.cr_opt},
            ]
            df = pd.DataFrame(datos_completos)
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Reporte', index=False)
            messagebox.showinfo("Exportación Exitosa", f"Exportado a:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

    def _seccion(self, parent, titulo: str):
        ctk.CTkLabel(
            parent, text=titulo,
            font=("Arial", 14, "bold"), text_color="#FFB74D"
        ).pack(anchor="w", pady=(15, 4), padx=(5, 20))
        self._separador(parent)

    def _separador(self, parent):
        sep = ctk.CTkFrame(parent, height=1, fg_color="#2c3e50")
        sep.pack(fill="x", pady=(0, 6), padx=(5, 20))

    def _fila(self, parent, etiqueta: str, valor: str, destacar: bool = False):
        fila = ctk.CTkFrame(parent, fg_color="transparent")
        fila.pack(fill="x", pady=2, padx=(5, 20))
        color_val = "#F06292" if destacar else "#E0E0E0"
        ctk.CTkLabel(fila, text=etiqueta, font=("Arial", 12), text_color="#AAAAAA").pack(side="left")
        ctk.CTkLabel(fila, text=valor, font=("Arial", 12, "bold"), text_color=color_val).pack(side="right")

    def _construir_graficos(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        r = self.resultado

        fig, (ax_torta, ax_barras) = plt.subplots(
            1, 2, figsize=(8, 5), facecolor=COLOR_FONDO
        )
        fig.subplots_adjust(wspace=0.4, left=0.08, right=0.95, top=0.88, bottom=0.18)

        # ── Gráfico 1: Torta (Valores) ──
        etiquetas = ["Cobre", "Aluminio", "Oro", "Plástico"]
        valores = [r.valor_cobre, r.valor_aluminio, r.valor_oro, r.valor_plastico]

        pares = [(e, v, c) for e, v, c in zip(etiquetas, valores, COLORES_TORTA) if v > 0]
        if pares:
            etq_f, val_f, col_f = zip(*pares)
        else:
            etq_f, val_f, col_f = ["Sin datos"], [1], ["#555555"]

        wedges, texts, autotexts = ax_torta.pie(
            val_f, labels=None, autopct="%1.1f%%", colors=col_f,
            startangle=140, pctdistance=0.75,
            wedgeprops={"edgecolor": COLOR_FONDO, "linewidth": 1.5}
        )
        for at in autotexts:
            at.set_color(COLOR_FONDO)
            at.set_fontsize(9)
            at.set_fontweight("bold")

        ax_torta.set_facecolor(COLOR_FONDO)
        ax_torta.set_title("Distribución del Valor\nRecuperado", color=COLOR_TEXTO,
                            fontsize=11, fontweight="bold", pad=12)

        ax_torta.legend(
            wedges, etq_f, loc="lower center", bbox_to_anchor=(0.5, -0.28),
            ncol=2, fontsize=8, frameon=False, labelcolor=COLOR_TEXTO
        )

        # ── Gráfico 2: Barras (Masa) ──
        materiales = ["Cobre", "Aluminio", "Oro", "Plástico"]
        masas = [r.peso_cobre, r.peso_aluminio, r.peso_oro, r.peso_plastico]
        colores_barras = COLORES_TORTA
        x_pos = range(len(materiales))

        bars = ax_barras.bar(x_pos, masas, color=colores_barras,
                             edgecolor=COLOR_FONDO, linewidth=1.2, width=0.5)

        for bar, masa in zip(bars, masas):
            ax_barras.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + (max(masas) if max(masas) > 0 else 1) * 0.02,
                f"{masa:.2f} kg",
                ha="center", va="bottom",
                color=COLOR_TEXTO, fontsize=9, fontweight="bold"
            )

        ax_barras.set_facecolor(COLOR_FONDO)
        ax_barras.set_xticks(list(x_pos))
        ax_barras.set_xticklabels(["Cu", "Al", "Au", "Plast."], color=COLOR_TEXTO, fontsize=10)
        ax_barras.set_ylabel("Masa (kg)", color=COLOR_TEXTO, fontsize=10)
        ax_barras.set_title("Masa Recuperada\npor Material", color=COLOR_TEXTO,
                            fontsize=11, fontweight="bold", pad=12)
        ax_barras.tick_params(colors=COLOR_TEXTO)
        ax_barras.spines["top"].set_visible(False)
        ax_barras.spines["right"].set_visible(False)
        for spine in ["left", "bottom"]:
            ax_barras.spines[spine].set_color(COLOR_GRID)
        ax_barras.yaxis.label.set_color(COLOR_TEXTO)
        ax_barras.set_ylim(0, (max(masas) * 1.25) if max(masas) > 0 else 1)
        ax_barras.yaxis.grid(True, color=COLOR_GRID, linestyle="--", alpha=0.5)
        ax_barras.set_axisbelow(True)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        plt.close(fig)
