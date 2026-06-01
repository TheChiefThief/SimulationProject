"""
core/exportadores.py
-------------------
Funciones para exportar los resultados de la simulación a formatos Excel (.xlsx) y PDF.
"""

from tkinter import filedialog, messagebox
from datetime import datetime
import os
import pandas as pd
from fpdf import FPDF
from core.logger import registrar_error
from core.resultados import ResultadoLote

def exportar_a_excel(resultado: ResultadoLote, parent=None):
    """
    Exporta un objeto ResultadoLote a un archivo Excel (.xlsx).
    Muestra diálogos en pantalla (filedialog, messagebox).
    """
    try:
        r = resultado
        fecha_str = getattr(r, "fecha", None)
        if fecha_str:
            fecha = fecha_str
            nombre_sugerido = f"Simulacion_{fecha.replace(':', '-').replace(' ', '_')}"
        else:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
            nombre_sugerido = f"Simulacion_{fecha.replace(':', '-').replace(' ', '_')}"

        filepath = filedialog.asksaveasfilename(
            parent=parent,
            initialfile=nombre_sugerido,
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")],
            title="Exportar a Excel"
        )
        if not filepath:
            return

        filas = [
            # Encabezado
            {"Categoría": "INFORME", "Métrica": "Fecha",         "Valor": fecha},
            {"Categoría": "INFORME", "Métrica": "Semilla GCL",   "Valor": resultado.semilla_gcl},
            {"Categoría": "", "Métrica": "", "Valor": ""},
            # Lote
            {"Categoría": "LOTE", "Métrica": "Peso ingresado B (kg)",  "Valor": resultado.b_kg_input},
            {"Categoría": "LOTE", "Métrica": "Peso procesado real (kg)","Valor": round(resultado.peso_acumulado, 3)},
            {"Categoría": "LOTE", "Métrica": "Total dispositivos (N)",  "Valor": resultado.n_total},
            {"Categoría": "LOTE", "Métrica": "CantCam (desguazadas)",   "Valor": resultado.cant_cam},
            {"Categoría": "LOTE", "Métrica": "CantDvr (desguados)",     "Valor": resultado.cant_dvr},
            {"Categoría": "LOTE", "Métrica": "CAMREC (reventa)",        "Valor": resultado.cam_rec},
            {"Categoría": "LOTE", "Métrica": "DvrREC (reventa)",        "Valor": resultado.dvr_rec},
            {"Categoría": "LOTE", "Métrica": "Total reventa",           "Valor": resultado.equipos_reventa},
            {"Categoría": "", "Métrica": "", "Valor": ""},
            # Valores
            {"Categoría": "VALORES (ARS)", "Métrica": "Cobre",     "Valor": round(resultado.valor_cobre, 2)},
            {"Categoría": "VALORES (ARS)", "Métrica": "Aluminio",  "Valor": round(resultado.valor_aluminio, 2)},
            {"Categoría": "VALORES (ARS)", "Métrica": "Oro",       "Valor": round(resultado.valor_oro, 2)},
            {"Categoría": "VALORES (ARS)", "Métrica": "Plástico",  "Valor": round(resultado.valor_plastico, 2)},
            {"Categoría": "VALORES (ARS)", "Métrica": "PMT",       "Valor": round(resultado.pmt, 2)},
            {"Categoría": "VALORES (ARS)", "Métrica": "PT",        "Valor": round(resultado.pt, 2)},
            {"Categoría": "VALORES (ARS)", "Métrica": "TOTAL",     "Valor": round(resultado.valor_total, 2)},
            {"Categoría": "", "Métrica": "", "Valor": ""},
            # Masa
            {"Categoría": "MASA (kg)", "Métrica": "MT (total)",   "Valor": round(resultado.mt, 3)},
            {"Categoría": "MASA (kg)", "Métrica": "PesoPlastico", "Valor": round(resultado.peso_plastico, 3)},
            {"Categoría": "MASA (kg)", "Métrica": "PesoMetal",    "Valor": round(resultado.peso_metal, 3)},
            {"Categoría": "MASA (kg)", "Métrica": "PesoVidrio",   "Valor": round(resultado.peso_vidrio, 3)},
            {"Categoría": "", "Métrica": "", "Valor": ""},
            # Coeficientes
            {"Categoría": "COEFICIENTES", "Métrica": "CrPlastico (%)", "Valor": round(resultado.cr_plastico, 2)},
            {"Categoría": "COEFICIENTES", "Métrica": "CrMetales (%)",  "Valor": round(resultado.cr_metales, 2)},
            {"Categoría": "COEFICIENTES", "Métrica": "CrPlacas (%)",   "Valor": round(resultado.cr_placas, 2)},
            {"Categoría": "COEFICIENTES", "Métrica": "CrHDD (%)",      "Valor": round(resultado.cr_hdd, 2)},
            {"Categoría": "COEFICIENTES", "Métrica": "CrOptica (%)",   "Valor": round(resultado.cr_opt, 2)},
            {"Categoría": "", "Métrica": "", "Valor": ""},
            # Estaciones (Ocupación)
            {"Categoría": "OCUPACIÓN (%)", "Métrica": "E1 — Revisión",      "Valor": round(resultado.ocupacion_1, 1)},
            {"Categoría": "OCUPACIÓN (%)", "Métrica": "E2 — Cámara/Ópt",   "Valor": round(resultado.ocupacion_2, 1)},
            {"Categoría": "OCUPACIÓN (%)", "Métrica": "E3 — Ópt. Mat",      "Valor": round(resultado.ocupacion_3, 1)},
            {"Categoría": "OCUPACIÓN (%)", "Métrica": "E4 — Placas",        "Valor": round(resultado.ocupacion_4, 1)},
            {"Categoría": "OCUPACIÓN (%)", "Métrica": "E5 — Desarme DVR",   "Valor": round(resultado.ocupacion_5, 1)},
            {"Categoría": "OCUPACIÓN (%)", "Métrica": "E6 — HDD",           "Valor": round(resultado.ocupacion_6, 1)},
            {"Categoría": "OCUPACIÓN (%)", "Métrica": "Cuellos de botella", "Valor": ", ".join(resultado.cuellos_botella) or "Ninguno"},
            {"Categoría": "", "Métrica": "", "Valor": ""},
            # Estaciones (Productividad)
            {"Categoría": "PRODUCTIVIDAD", "Métrica": "E1 — Revisión",      "Valor": round(resultado.productividad_1, 2)},
            {"Categoría": "PRODUCTIVIDAD", "Métrica": "E2 — Cámara/Ópt",   "Valor": round(resultado.productividad_2, 2)},
            {"Categoría": "PRODUCTIVIDAD", "Métrica": "E3 — Ópt. Mat",      "Valor": round(resultado.productividad_3, 2)},
            {"Categoría": "PRODUCTIVIDAD", "Métrica": "E4 — Placas",        "Valor": round(resultado.productividad_4, 2)},
            {"Categoría": "PRODUCTIVIDAD", "Métrica": "E5 — Desarme DVR",   "Valor": round(resultado.productividad_5, 2)},
            {"Categoría": "PRODUCTIVIDAD", "Métrica": "E6 — HDD",           "Valor": round(resultado.productividad_6, 2)},
            {"Categoría": "", "Métrica": "", "Valor": ""},
            # Demanda
            {"Categoría": "DEMANDA", "Métrica": "Horas simuladas", "Valor": resultado.horas_demanda},
            {"Categoría": "DEMANDA", "Métrica": "Clientes totales","Valor": resultado.clientes_totales},
        ]

        df = pd.DataFrame(filas)
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Reporte", index=False)

        messagebox.showinfo("Exportación Exitosa", f"Archivo Excel guardado en:\n{filepath}", parent=parent)

    except Exception as e:
        registrar_error("Error al exportar los resultados a Excel en core/exportadores.py", e)
        messagebox.showwarning("Aviso", f"No se pudo exportar a Excel:\n{e}", parent=parent)


def exportar_a_pdf(resultado: ResultadoLote, parent=None):
    """
    Exporta un objeto ResultadoLote a un archivo PDF.
    Muestra diálogos en pantalla (filedialog, messagebox).
    """
    try:
        r = resultado
        fecha_str = getattr(r, "fecha", None)
        if fecha_str:
            fecha = fecha_str
            nombre_sugerido = f"Simulacion_{fecha.replace(':', '-').replace(' ', '_')}"
        else:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
            nombre_sugerido = f"Simulacion_{fecha.replace(':', '-').replace(' ', '_')}"

        filepath = filedialog.asksaveasfilename(
            parent=parent,
            initialfile=nombre_sugerido,
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
            title="Exportar a PDF"
        )
        if not filepath:
            return

        def safe_str(text):
            # fpdf uses latin-1 by default. Replaces em-dash and en-dash with standard hyphen.
            return str(text).replace("\u2014", "-").replace("\u2013", "-").encode('latin-1', 'replace').decode('latin-1')

        pdf = FPDF()
        pdf.add_page()

        # Logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gui", "logopdf.png")
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=85, y=10, w=40)
            pdf.ln(20)
        
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

        messagebox.showinfo("Exportacion Exitosa", f"Archivo PDF guardado en:\n{filepath}", parent=parent)

    except Exception as e:
        registrar_error("Error al exportar los resultados a PDF en core/exportadores.py", e)
        messagebox.showwarning("Aviso", f"No se pudo exportar a PDF:\n{e}", parent=parent)
