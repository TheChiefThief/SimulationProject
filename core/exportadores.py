"""
core/exportadores.py
-------------------
Funciones para exportar los resultados de la simulación a formatos Excel (.xlsx) y PDF.
"""

from tkinter import filedialog, messagebox
from datetime import datetime
import os
import pandas as pd

from core.logger import registrar_error
from core.resultados import ResultadoLote
from core.estimador_tiempo import estimar_tiempo_procesamiento, formatear_tiempo

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
            {"Categoría": "LOTE", "Métrica": "Tiempo est. proceso",     "Valor": formatear_tiempo(estimar_tiempo_procesamiento(resultado), resultado.horas_jornada)},
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
        ]

        df = pd.DataFrame(filas)
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Reporte", index=False)

        messagebox.showinfo("Exportación Exitosa", f"Archivo Excel guardado en:\n{filepath}", parent=parent)

    except Exception as e:
        registrar_error("Error al exportar los resultados a Excel en core/exportadores.py", e)
        messagebox.showwarning("Aviso", f"No se pudo exportar a Excel:\n{e}", parent=parent)



