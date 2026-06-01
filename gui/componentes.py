"""
gui/componentes.py
-------------------
Módulo que contiene componentes UI reutilizables de CustomTkinter
para evitar la repetición de código en las distintas vistas de la aplicación.
"""

import customtkinter as ctk

class CTKLabeledEntry(ctk.CTkFrame):
    """
    Un componente compuesto que agrupa una etiqueta principal, una
    etiqueta de ayuda opcional (hint) y un campo de texto de entrada.
    """
    def __init__(self, master, label_text, hint_text=None, placeholder_text="", width=280, default_value=None, font_family="Azeri Sans", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Etiqueta principal
        self.lbl_main = ctk.CTkLabel(self, text=label_text, font=(font_family, 13))
        self.lbl_main.pack(anchor="w")
        
        # Etiqueta de ayuda secundaria (opcional)
        if hint_text:
            self.lbl_hint = ctk.CTkLabel(self, text=hint_text, font=(font_family, 11), text_color="#888888")
            self.lbl_hint.pack(anchor="w")
            
        # Campo de entrada
        self.entry = ctk.CTkEntry(self, width=width, placeholder_text=placeholder_text, font=(font_family, 13))
        self.entry.pack(anchor="w", pady=(2, 14))
        
        # Valor por defecto
        if default_value is not None:
            self.entry.insert(0, str(default_value))
            
    def get(self):
        """Devuelve el contenido actual del campo."""
        return self.entry.get()
        
    def set(self, value):
        """Reemplaza el contenido del campo por el valor especificado."""
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
        
    def insert(self, index, string):
        """Inserta texto en la posición especificada."""
        self.entry.insert(index, string)
        
    def delete(self, first, last=None):
        """Elimina texto del campo."""
        self.entry.delete(first, last)
        
    def configure_entry(self, **kwargs):
        """Aplica configuración directa al campo CTkEntry interno."""
        self.entry.configure(**kwargs)


class CTKResultRow(ctk.CTkFrame):
    """
    Fila para mostrar resultados de forma estructurada. 
    Contiene una etiqueta descriptiva y un campo readonly con posibles prefijos o iconos.
    """
    def __init__(self, master, etiqueta, prefijo="", icono_img=None, font_family="Azeri Sans", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Etiqueta descriptiva superior
        ctk.CTkLabel(self, text=etiqueta, font=(font_family, 13),
                     text_color="#AAAAAA", wraplength=280).pack(anchor="w")
                     
        # Fila contenedora para el entry y sus agregados
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(anchor="w", fill="x", pady=(0, 14), expand=True)
        
        if icono_img:
            ctk.CTkLabel(row, image=icono_img, text="").pack(side="left", padx=(0, 10), pady=4)
            
        if prefijo:
            ctk.CTkLabel(row, text=prefijo, font=(font_family, 15, "bold"),
                         text_color="#4FC3F7").pack(side="left", padx=(0, 8))
                         
        # Campo de lectura
        self.entry = ctk.CTkEntry(row, state="readonly", font=(font_family, 13))
        self.entry.pack(side="left", fill="x", expand=True)
        
    def set(self, value):
        """Actualiza el valor mostrado en el campo de solo lectura."""
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
        self.entry.configure(state="readonly")


class CTKKeyValueRow(ctk.CTkFrame):
    """
    Fila para mostrar pares clave-valor (usado frecuentemente en informes).
    """
    def __init__(self, master, etiqueta: str, valor: str, destacar: bool = False, font_family="Azeri Sans", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.pack(fill="x", pady=2, padx=(5, 20))
        
        color_val = "#F06292" if destacar else "#E0E0E0"
        
        # Usamos grid para evitar superposición bajo cualquier circunstancia
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        # Etiqueta clave a la izquierda
        self.lbl_key = ctk.CTkLabel(self, text=etiqueta, font=(font_family, 12),
                                     text_color="#AAAAAA", justify="left")
        self.lbl_key.grid(row=0, column=0, sticky="nw", padx=(0, 10))
        
        # Etiqueta valor a la derecha (con wraplength dinámico o justificado)
        self.lbl_valor = ctk.CTkLabel(self, text=valor, font=(font_family, 12, "bold"),
                                       text_color=color_val, justify="right")
        self.lbl_valor.grid(row=0, column=1, sticky="ne")
        
        # Enlace dinámico para wraplength responsive del valor
        self.bind("<Configure>", self._on_configure)
        
    def _on_configure(self, event):
        key_w = self.lbl_key.winfo_reqwidth()
        ancho_valor = max(100, event.width - key_w - 25)
        if self.lbl_valor.cget("wraplength") != ancho_valor:
            self.lbl_valor.configure(wraplength=ancho_valor)
        
    def set(self, valor_str: str):
        self.lbl_valor.configure(text=valor_str)
