"""
Función de exportación a PDF eliminada de core/exportadores.py.
Se resguarda aquí en Trash a petición del usuario.
"""

from tkinter import filedialog, messagebox
from datetime import datetime
import os
from fpdf import FPDF
from core.logger import registrar_error

def exportar_a_pdf(resultado, parent=None):
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
            return str(text).replace("\u2014", "-").replace("\u2013", "-").encode('latin-1', 'replace').decode('latin-1')

        pdf = FPDF()
        pdf.add_page()

        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gui", "logopdf.png")
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=85, y=10, w=40)
            pdf.ln(20)
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, safe_str("Informe de Simulacion - Resultados Generales"), ln=True, align='C')
        
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, safe_str(f"Fecha: {fecha} | Semilla GCL: {r.semilla_gcl}"), ln=True, align='C')
        
        def add_section(title):
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 8, safe_str(title), ln=True, align='L')
            pdf.set_font("Arial", '', 11)
            pdf.set_text_color(0, 0, 0)
            
        def add_row(label, value):
            pdf.cell(100, 6, safe_str(label), ln=False)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(90, 6, safe_str(value), ln=True, align='R')
            pdf.set_font("Arial", '', 11)

        add_section("Lote Procesado")
        add_row("Peso ingresado (B)", f"{r.b_kg_input:.2f} kg")
        add_row("Peso procesado real", f"{r.peso_acumulado:.3f} kg")
        add_row("Total dispositivos (N)", f"{r.n_total}")
        add_row("Camaras desguazadas (CantCam)", f"{r.cant_cam}")
        add_row("DVRs desguazados (CantDvr)", f"{r.cant_dvr}")
        add_row("Camaras reventa (CAMREC)", f"{r.cam_rec}")
        add_row("DVRs reventa (DvrREC)", f"{r.dvr_rec}")
        add_row("Total reventa", f"{r.equipos_reventa}")

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

        add_section("Masa Recuperada (kg)")
        add_row("MT - Material Total", f"{r.mt:.3f} kg")
        add_row("PesoPlastico", f"{r.peso_plastico:.3f} kg")
        add_row("PesoMetal (total)", f"{r.peso_metal:.3f} kg")
        add_row("  Cobre", f"{r.peso_cobre:.3f} kg")
        add_row("  Aluminio", f"{r.peso_aluminio:.3f} kg")
        add_row("  Oro", f"{r.peso_oro:.4f} kg")
        add_row("PesoVidrio", f"{r.peso_vidrio:.3f} kg")

        add_section("Coeficientes de Recuperacion")
        add_row("CrPlastico", f"{r.cr_plastico:.2f} %")
        add_row("CrMetales", f"{r.cr_metales:.2f} %")
        add_row("CrPlacas", f"{r.cr_placas:.2f} % (PlacasF={r.placas_f} / PlacasT={r.placas_t})")
        add_row("CrHDD", f"{r.cr_hdd:.2f} % (HDDF={r.hdd_f} / HDDT={r.hdd_t})")
        add_row("CrOptica", f"{r.cr_opt:.2f} %")

        add_section("Ocupacion y Productividad")
        add_row("E1 - Revision", f"Ocup: {r.ocupacion_1:.1f}% | Prod: {r.productividad_1:.2f} | C1={r.c1}")
        add_row("E2 - Camara/Opt", f"Ocup: {r.ocupacion_2:.1f}% | Prod: {r.productividad_2:.2f} | C2={r.c2}")
        add_row("E3 - Opt. Mat.", f"Ocup: {r.ocupacion_3:.1f}% | Prod: {r.productividad_3:.2f} | C3={r.c3}")
        add_row("E4 - Placas", f"Ocup: {r.ocupacion_4:.1f}% | Prod: {r.productividad_4:.2f} | C4={r.c4}")
        add_row("E5 - Desarme DVR", f"Ocup: {r.ocupacion_5:.1f}% | Prod: {r.productividad_5:.2f} | C5={r.c5}")
        add_row("E6 - HDD", f"Ocup: {r.ocupacion_6:.1f}% | Prod: {r.productividad_6:.2f} | C6={r.c6}")
        
        cuellos_str = ", ".join(r.cuellos_botella) if r.cuellos_botella else "Ninguno"
        add_row("Cuellos de Botella", cuellos_str)

        pdf.output(filepath)

        messagebox.showinfo("Exportacion Exitosa", f"Archivo PDF guardado en:\n{filepath}", parent=parent)

    except Exception as e:
        registrar_error("Error al exportar los resultados a PDF en core/exportadores.py", e)
        messagebox.showwarning("Aviso", f"No se pudo exportar a PDF:\n{e}", parent=parent)
