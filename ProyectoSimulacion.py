import math
import tkinter as tk
import customtkinter as ctk


# --- 1. MODELO MATEMÁTICO (Basado en TP1-TP3 de UTN) ---
# [cite: 3]
class GeneradorUTN:
    """Generador Congruencial Mixto según Ejercicio 5 del PDF[cite: 3]"""

    def __init__(self, semilla=1237):
        self.n = semilla
        self.a = 4309  # Multiplicador[cite: 3]
        self.c = 2311  # Constante aditiva[cite: 3]
        self.m = 6031  # Módulo[cite: 3]

    def proximo_u(self):
        """Genera el siguiente número pseudoaleatorio entre 0 y 1"""
        self.n = (self.a * self.n + self.c) % self.m
        return self.n / self.m


def simular_proceso_dispositivo(u_generador, es_camara=True):
    """Lógica de simulación aplicando Transformación Inversa y Rechazo[cite: 3]"""
    # 1. Determinación de Recuperabilidad (Variable Discreta)
    u1 = u_generador.proximo_u()
    # Usando el 72% de recuperabilidad del Excel de especificaciones
    es_recuperable = u1 <= 0.72

    # 2. Tiempo de Procesamiento (Distribución Exponencial)
    # Fórmula de la cátedra: -media * ln(u)[cite: 3]
    u2 = u_generador.proximo_u()
    media_tiempo = 5 if es_camara else 8  # Minutos promedio por estación[cite: 2]
    tiempo = -media_tiempo * math.log(max(u2, 0.0001))

    # 3. Valor Económico (Distribución Uniforme)
    # Fórmula: Min + (Max-Min) * u[cite: 3]
    u3 = u_generador.proximo_u()
    if es_recuperable:
        # Precios basados en el Excel (Chatarra vs Metal base)[cite: 1]
        v_min, v_max = 1500, 8500
        valor = v_min + (v_max - v_min) * u3
    else:
        # Si no es recuperable, el valor es el del plástico base[cite: 1]
        valor = 60

    return tiempo, es_recuperable, valor


# --- 2. INTERFAZ GRÁFICA (Basada en Prototipo Avance 1) ---
# [cite: 1]
class AppSimulador(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("UTN - Simulador e-waste")
        self.geometry("950x600")
        ctk.set_appearance_mode("dark")

        # Configuración de columnas
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SECCIÓN IZQUIERDA: ENTRADA ---
        self.f_izq = ctk.CTkFrame(self)
        self.f_izq.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.f_izq, text="Ingresar Lote", font=("Arial", 22, "bold")).pack(pady=20)

        ctk.CTkLabel(self.f_izq, text="Cantidad Residuos (Kg)").pack(anchor="w", padx=30)
        self.in_residuos = ctk.CTkEntry(self.f_izq, width=250)
        self.in_residuos.pack(pady=5, padx=30)
        self.in_residuos.insert(0, "1500")  # Dato típico del Excel[cite: 1]

        ctk.CTkLabel(self.f_izq, text="Cantidad de Dispositivos").pack(anchor="w", padx=30)
        self.in_camaras = ctk.CTkEntry(self.f_izq, width=250)
        self.in_camaras.pack(pady=5, padx=30)
        self.in_camaras.insert(0, "10")

        self.btn_run = ctk.CTkButton(self.f_izq, text="Ejecutar Pruebas",
                                     command=self.correr_pruebas,
                                     fg_color="#1f538d", hover_color="#14375e")
        self.btn_run.pack(pady=40)

        # --- SECCIÓN DERECHA: LOG DE PRUEBAS ---
        # Color azul petróleo similar al prototipo "Resultados"[cite: 1]
        self.f_der = ctk.CTkFrame(self, fg_color="#0d212d")
        self.f_der.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.f_der, text="Consola de Simulación", font=("Arial", 22, "bold")).pack(pady=20)

        self.txt_log = tk.Text(self.f_der, height=18, bg="#0d212d", fg="#00ff00",
                               font=("Consolas", 11), borderwidth=0)
        self.txt_log.pack(pady=10, padx=20, fill="both")

    def correr_pruebas(self):
        """Ejecuta la simulación y muestra los resultados paso a paso[cite: 2]"""
        self.txt_log.delete("1.0", tk.END)
        gen = GeneradorUTN()  # Semilla inicial fija para pruebas repetibles[cite: 3]

        try:
            n = int(self.in_camaras.get())
        except ValueError:
            n = 5

        self.txt_log.insert(tk.END, f">>> INICIANDO TEST: LOTE DE {n} UNIDADES\n")
        self.txt_log.insert(tk.END, f">>> PARÁMETROS: Media=5min | Rec=72%\n")
        self.txt_log.insert(tk.END, "=" * 45 + "\n")

        t_total = 0
        v_total = 0
        exitos = 0

        for i in range(1, n + 1):
            t, rec, val = simular_proceso_dispositivo(gen)
            t_total += t
            v_total += val
            if rec: exitos += 1

            # Formato de salida profesional para el cliente[cite: 1]
            status = "RECUPERADO" if rec else "DESCARTE  "
            self.txt_log.insert(tk.END, f"ITEM {i:02d} | {t:4.2f} min | {status} | ${val:7.0f}\n")

        # --- CÁLCULO DE MÉTRICAS (Etapa 1-2) ---
        # [cite: 1]
        self.txt_log.insert(tk.END, "=" * 45 + "\n")
        self.txt_log.insert(tk.END, f"RESUMEN OPERATIVO:\n")
        self.txt_log.insert(tk.END, f"- Tiempo Total de Línea: {t_total:.2f} min\n")
        self.txt_log.insert(tk.END, f"- Tasa de Recuperación: {(exitos / n) * 100:.1f}%\n")
        self.txt_log.insert(tk.END, f"- Valor Económico Estimado: ${v_total:,.2f}\n")

        # Lógica de cuellos de botella (Teoría de Colas - Avance 2)[cite: 2]
        if t_total > 480:  # Si excede jornada laboral de 8hs
            self.txt_log.insert(tk.END, "\n[!] ALERTA: CAPACIDAD EXCEDIDA (8hs+)\n")
            self.txt_log.insert(tk.END, "Se requieren horas extras o más personal.\n")


if __name__ == "__main__":
    app = AppSimulador()
    app.mainloop()