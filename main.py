"""
main.py
--------
Punto de entrada del Simulador de Reciclaje RAEE.

Ejecutar con:
    python main.py
"""

from gui.app import AppSimulador


if __name__ == "__main__":
    app = AppSimulador()
    app.mainloop()
