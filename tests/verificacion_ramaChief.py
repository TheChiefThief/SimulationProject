"""
Verificación integral para ramaChief — GCL + Distribuciones + Simulación completa.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gcl import GeneradorCongruencialLineal
from core.distribuciones import Distribuciones
from core.prueba_estadistica import PruebaKolmogorovSmirnov
from core.parametros import ParametrosSistema
from core.simulacion_service import SimulacionService

print("=== GCL ===")
gcl = GeneradorCongruencialLineal(42)
print(f"Semilla: {gcl.semilla}  Iteraciones iniciales: {gcl.iteraciones}")
muestras = [gcl.siguiente_u() for _ in range(10)]
print(f"Primeras 10 U(0,1): {[round(x,4) for x in muestras]}")
assert all(0.0 <= x < 1.0 for x in muestras), "ERROR: valores fuera de [0,1)"
print("OK: todos en [0, 1)")

print()
print("=== DISTRIBUCIONES (via clase Distribuciones) ===")
gcl2 = GeneradorCongruencialLineal(42)
d = Distribuciones(gcl2)

# Exponencial
exp_vals = [d.siguiente_exponencial(3.0) for _ in range(5000)]
media_exp = sum(exp_vals)/len(exp_vals)
print(f"Exp(media=3.0): media_muestral={media_exp:.3f}  (esperado ~3.0)")
assert all(v > 0 for v in exp_vals), "ERROR: valor exponencial <= 0"

# Bernoulli
gcl3 = GeneradorCongruencialLineal(99)
d3 = Distribuciones(gcl3)
b_vals = [d3.siguiente_bernoulli(0.25) for _ in range(10000)]
tasa = sum(b_vals)/len(b_vals)
print(f"Bernoulli(p=0.25): tasa={tasa:.3f}  (esperado ~0.25)")

gcl3b = GeneradorCongruencialLineal(99)
d3b = Distribuciones(gcl3b)
b2 = [d3b.siguiente_bernoulli(0.113) for _ in range(10000)]
print(f"Bernoulli(p=0.113): tasa={sum(b2)/len(b2):.3f}  (esperado ~0.113)")

# Uniforme
gcl4 = GeneradorCongruencialLineal(55)
d4 = Distribuciones(gcl4)
r_vals = [d4.siguiente_rango(0.9, 1.4) for _ in range(5000)]
print(f"Uniforme(0.9, 1.4): media={sum(r_vals)/len(r_vals):.3f}  (esperado ~1.15)")
assert all(0.9 <= x < 1.4 for x in r_vals), "ERROR: valor fuera del rango"

# Entero
gcl5 = GeneradorCongruencialLineal(66)
d5 = Distribuciones(gcl5)
ent_vals = [d5.siguiente_entero(250, 2000) for _ in range(5000)]
print(f"Entero(250,2000): media={sum(ent_vals)/len(ent_vals):.1f}  (esperado ~1125)")
assert all(250 <= x <= 2000 for x in ent_vals), "ERROR: entero fuera del rango"

# Normal (Box-Muller)
gcl7 = GeneradorCongruencialLineal(88)
d7 = Distribuciones(gcl7)
n_vals = [d7.siguiente_normal(0, 1) for _ in range(5000)]
media_n = sum(n_vals)/len(n_vals)
print(f"Normal(0,1): media={media_n:.3f}  (esperado ~0.0)")

print()
print("=== PRUEBA KOLMOGOROV-SMIRNOV ===")
gcl_ks = GeneradorCongruencialLineal(123)
ks = PruebaKolmogorovSmirnov(gcl_ks)
res = ks.ejecutar_prueba(n=1000, alpha=0.05)
print(f"  D_calculado = {res['d_calculado']:.4f}")
print(f"  D_critico   = {res['d_critico']:.4f}")
print(f"  Aprobado    = {res['aprobado']}")
assert res['aprobado'], "FALLO: K-S no aprobó uniformidad!"

print()
print("=== SIMULACION COMPLETA ===")
params = ParametrosSistema()
svc = SimulacionService(params)
r = svc.simular_lote(100.0)
print(f"B=100 kg -> peso_acumulado={r.peso_acumulado:.2f} kg")
print(f"  Camaras: {r.cant_cam}  DVRs: {r.cant_dvr}  Reventa: {r.equipos_reventa}")
print(f"  Valor total: {r.valor_total:,.0f} ARS")
print(f"  Ocupacion E1: {r.ocupacion_1:.1f}%  E4 (placas): {r.ocupacion_4:.1f}%")
print(f"  Cuellos de botella: {r.cuellos_botella or 'Ninguno'}")
assert r.peso_acumulado >= 100.0, "ERROR: no alcanzó el peso B"
assert r.n_total > 0, "ERROR: no se procesó ningún dispositivo"

print()
print("=== TODAS LAS VERIFICACIONES PASARON ===")
