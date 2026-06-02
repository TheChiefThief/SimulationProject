"""
Este archivo contiene la lógica matemática y de testeo de la distribución de Poisson 
que fue eliminada del flujo principal del simulador por no aportar valor a las 
métricas de reciclaje del lote, tal como se evaluó en la revisión final.
"""

import math
import random

# ── Algoritmo matemático extraído de core/distribuciones.py ──
def siguiente_poisson(lam: float, generador_u) -> int:
    """
    Genera un número con distribución de Poisson (algoritmo de Knuth).
    Adaptado para recibir un generador de Uniformes(0,1).
    """
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        u = generador_u()
        p *= u
        if p <= L:
            return k - 1


# ── Prueba Unitaria extraída de tests/verificacion_ramaChief.py ──
if __name__ == "__main__":
    print("--- Test de Poisson Histórico ---")
    
    # Mockeamos el generador U(0,1) para la prueba
    def mock_generador_u():
        return random.random()

    lam_test = 114.15
    p_vals = [siguiente_poisson(lam_test, mock_generador_u) for _ in range(10000)]
    media = sum(p_vals) / len(p_vals)
    print(f"Poisson(lambda={lam_test}): media={media:.3f}  (esperado ~{lam_test})")
    assert all(v >= 0 for v in p_vals), "ERROR: Poisson negativo"
    print("Test Exitoso.")
