"""
ProyectoSimulacion.py
----------------------
Archivo original del proyecto. El código fue refactorizado en módulos.

Para ejecutar la aplicación, use:
    python main.py

Estructura del proyecto:
    main.py             → Punto de entrada
    core/
        gcl.py          → Generador Congruencial Lineal (GCL) puro
        parametros.py   → Clase ParametrosSistema (estado del sistema)
        simulacion.py   → Motor de simulación RAEE
    gui/
        app.py          → Ventana principal (AppSimulador)
        vista_usuario.py   → Tab Vista de Usuario
        vista_gerente.py   → Tab Vista del Gerente / Admin
        vista_config.py    → Tab Configuración de parámetros
        ventana_resultados.py → Ventana de informe + gráficos
"""

# Mantener compatibilidad: ejecutar desde este archivo también funciona
from gui.app import AppSimulador

if __name__ == "__main__":
    app = AppSimulador()
    app.mainloop()