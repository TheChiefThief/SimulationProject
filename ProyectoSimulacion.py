import math
import time
import tkinter as tk
import customtkinter as ctk

# --- 1. MODELO MATEMÁTICO ---
class GeneradorUTN:
    """Generador Congruencial Mixto con semilla dinámica (pseudoaleatorización)"""
    def __init__(self, semilla=None):
        # Si no se define una semilla, usa los milisegundos del reloj del sistema
        if semilla is None:
            self.n = int(time.time() * 1000) % 10000 
        else:
            self.n = semilla
            
        self.a = 4309  
        self.c = 2311  
        self.m = 6031  

    def proximo_u(self):
        self.n = (self.a * self.n + self.c) % self.m
        return self.n / self.m

def simular_proceso_dispositivo(u_generador, es_camara=True):
    """Lógica de simulación para un dispositivo individual"""
    u1 = u_generador.proximo_u()
    es_recuperable = u1 <= 0.72

    u2 = u_generador.proximo_u()
    if es_recuperable:
        # Precios base estimados
        v_min, v_max = 1500, 8500
        valor = v_min + (v_max - v_min) * u2
    else:
        valor = 60 # Valor residual por plásticos

    return es_recuperable, valor

# --- 2. INTERFAZ GRÁFICA ---
class AppSimulador(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simulador - Reciclado e-waste")
        self.geometry("1000x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.pestanas = ctk.CTkTabview(self)
        self.pestanas.pack(padx=20, pady=20, fill="both", expand=True)

        self.T_USUARIO = "Vista de Usuario"
        self.T_GERENTE = "Vista del Gerente"
        self.T_CONFIG = "Vista de Configuración"

        self.pestanas.add(self.T_USUARIO)
        self.pestanas.add(self.T_GERENTE)
        self.pestanas.add(self.T_CONFIG)

        self.armar_vista_usuario()
        self.armar_vista_gerente()
        self.armar_vista_configuracion()

    def armar_vista_usuario(self):
        tab = self.pestanas.tab(self.T_USUARIO)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        # -- PANEL IZQUIERDO: Ingresar --
        frame_izq = ctk.CTkFrame(tab, fg_color="transparent")
        frame_izq.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(frame_izq, text="Ingresar", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(frame_izq, text="Cantidad de Residuos (Kg)", font=("Arial", 14)).pack(anchor="w")
        self.in_residuos = ctk.CTkEntry(frame_izq, width=250)
        self.in_residuos.pack(anchor="w", pady=(0, 20))
        self.in_residuos.insert(0, "1500")

        ctk.CTkLabel(frame_izq, text="Cantidad de camaras", font=("Arial", 14)).pack(anchor="w")
        self.in_camaras = ctk.CTkEntry(frame_izq, width=250)
        self.in_camaras.pack(anchor="w", pady=(0, 40))
        self.in_camaras.insert(0, "50")

        # Conectamos el botón a la función lógica 'ejecutar_simulacion_usuario'
        self.btn_ejecutar_usr = ctk.CTkButton(frame_izq, text="Ejecutar", width=120, command=self.ejecutar_simulacion_usuario)
        self.btn_ejecutar_usr.pack(anchor="w")

        # -- PANEL DERECHO: Resultados --
        frame_der = ctk.CTkFrame(tab, fg_color="#1a2530", corner_radius=10)
        frame_der.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        inner_frame = ctk.CTkFrame(frame_der, fg_color="transparent")
        inner_frame.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(inner_frame, text="Resultados", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 20))

        def crear_fila_resultado(parent, texto_label):
            ctk.CTkLabel(parent, text=texto_label, font=("Arial", 14)).pack(anchor="w")
            row_frame = ctk.CTkFrame(parent, fg_color="transparent")
            row_frame.pack(anchor="w", fill="x", pady=(0, 15))
            ctk.CTkLabel(row_frame, text="$", font=("Arial", 18, "bold")).pack(side="left", padx=(0, 10))
            entry = ctk.CTkEntry(row_frame, width=200, state="readonly")
            entry.pack(side="left")
            return entry

        self.out_lentes = crear_fila_resultado(inner_frame, "Lentes recuperados")
        self.out_placas = crear_fila_resultado(inner_frame, "Placas recuperadas")
        self.out_discos = crear_fila_resultado(inner_frame, "Discos recuperados")
        self.out_total = crear_fila_resultado(inner_frame, "Valor de materiales recuperados")

        self.btn_exportar_usr = ctk.CTkButton(inner_frame, text="Exportar", width=120, fg_color="#2c3e50")
        self.btn_exportar_usr.pack(anchor="w", pady=(20, 0))

    # --- LÓGICA DE EJECUCIÓN (VISTA USUARIO) ---
    def ejecutar_simulacion_usuario(self):
        # 1. Instanciar generador con semilla basada en tiempo
        gen = GeneradorUTN() 
        
        # 2. Leer entradas del usuario
        try:
            n_camaras = int(self.in_camaras.get())
        except ValueError:
            n_camaras = 0
            
        valor_lentes = 0
        valor_placas = 0
        valor_discos = 0
        valor_total = 0

        # 3. Simular procesamiento de cada cámara
        for _ in range(n_camaras):
            # Simulamos el desguace (simplificado para el ejemplo)
            rec, val = simular_proceso_dispositivo(gen, es_camara=True)
            
            if rec:
                # Distribución arbitraria para el ejemplo visual
                valor_lentes += val * 0.3
                valor_placas += val * 0.5
                valor_discos += val * 0.2
            else:
                valor_total += val  # Se suma a materiales genéricos recuperados

        valor_total += (valor_lentes + valor_placas + valor_discos)

        # 4. Actualizar la interfaz con los resultados obtenidos
        self.actualizar_entry(self.out_lentes, f"{valor_lentes:,.2f}")
        self.actualizar_entry(self.out_placas, f"{valor_placas:,.2f}")
        self.actualizar_entry(self.out_discos, f"{valor_discos:,.2f}")
        self.actualizar_entry(self.out_total, f"{valor_total:,.2f}")

    def actualizar_entry(self, entry_widget, valor_str):
        """Función auxiliar para actualizar los campos de texto readonly"""
        entry_widget.configure(state="normal")
        entry_widget.delete(0, "end")
        entry_widget.insert(0, valor_str)
        entry_widget.configure(state="readonly")

    def armar_vista_gerente(self):
        tab = self.pestanas.tab(self.T_GERENTE)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        frame_izq = ctk.CTkFrame(tab, fg_color="transparent")
        frame_izq.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        inputs = ["Tiempo", "Cantidad empleados", "Energia consumida", "Coeficiente de pérdida"]
        for txt in inputs:
            ctk.CTkLabel(frame_izq, text=txt, font=("Arial", 14)).pack(anchor="w")
            ctk.CTkEntry(frame_izq, width=250).pack(anchor="w", pady=(0, 15))
        
        ctk.CTkLabel(frame_izq, text="Tipo de maquinaria", font=("Arial", 14)).pack(anchor="w")
        ctk.CTkOptionMenu(frame_izq, values=["Línea Automatizada", "Proceso Manual", "Híbrido"], width=250).pack(anchor="w", pady=(0, 30))

        self.btn_ejecutar_ger = ctk.CTkButton(frame_izq, text="Ejecutar", width=120)
        self.btn_ejecutar_ger.pack(anchor="w")

        frame_der = ctk.CTkFrame(tab, fg_color="#1a2530", corner_radius=10)
        frame_der.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        inner_frame = ctk.CTkFrame(frame_der, fg_color="transparent")
        inner_frame.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(inner_frame, text="Resultado", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 20))

        outputs = ["Coeficiente de productividad", "Eficacia", "Eficiencia", "Rango de mejora"]
        for txt in outputs:
            ctk.CTkLabel(inner_frame, text=txt, font=("Arial", 14)).pack(anchor="w")
            ctk.CTkEntry(inner_frame, width=250, state="readonly").pack(anchor="w", pady=(0, 15))

        self.btn_exportar_ger = ctk.CTkButton(inner_frame, text="Exportar", width=120, fg_color="#2c3e50")
        self.btn_exportar_ger.pack(anchor="w", pady=(20, 0))

    def armar_vista_configuracion(self):
        tab = self.pestanas.tab(self.T_CONFIG)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_columnconfigure(2, weight=1)

        col1 = ctk.CTkFrame(tab, fg_color="transparent")
        col1.grid(row=0, column=0, padx=20, pady=30, sticky="n")
        
        ctk.CTkLabel(col1, text="Rendimientos de\nMateriales Base", font=("Arial", 16, "bold"), justify="center").pack(pady=(0,20))
        
        ctk.CTkLabel(col1, text="Plastico", font=("Arial", 14)).pack()
        ctk.CTkSlider(col1, from_=0, to=100, width=150).pack(pady=(0,20))
        
        ctk.CTkLabel(col1, text="Metal", font=("Arial", 14)).pack()
        ctk.CTkSlider(col1, from_=0, to=100, width=150).pack(pady=(0,20))

        col2 = ctk.CTkFrame(tab, fg_color="transparent")
        col2.grid(row=0, column=1, padx=20, pady=30, sticky="n")

        ctk.CTkLabel(col2, text="Tasas de recuperacion\nde Componente", font=("Arial", 16, "bold"), justify="center").pack(pady=(0,20))
        
        tasas = ["Placas Sanas", "Opticas Sanas", "Discos Sanos"]
        for txt in tasas:
            ctk.CTkLabel(col2, text=txt, font=("Arial", 14)).pack()
            ctk.CTkEntry(col2, width=150).pack(pady=(0, 15))

        col3 = ctk.CTkFrame(tab, fg_color="transparent")
        col3.grid(row=0, column=2, padx=20, pady=30, sticky="n")

        ctk.CTkLabel(col3, text="Precios", font=("Arial", 16, "bold")).pack(pady=(0,20))
        
        precios = ["metal", "Plastico", "Lente"]
        for txt in precios:
            ctk.CTkLabel(col3, text=txt, font=("Arial", 14)).pack()
            ctk.CTkEntry(col3, width=150).pack(pady=(0, 15))

        btn_guardar = ctk.CTkButton(tab, text="Guardar", width=150, font=("Arial", 14, "bold"))
        btn_guardar.grid(row=1, column=0, columnspan=3, pady=40)

if __name__ == "__main__":
    app = AppSimulador()
    app.mainloop()