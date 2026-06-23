# Cambios en la Distribución Binomial y Bernoulli

Este documento explica la diferencia entre la implementación anterior y la nueva de las distribuciones Binomial y Bernoulli en el simulador.

## Implementación Anterior (Solo Bernoulli)

Anteriormente, el método `siguiente_binomial` era simplemente un alias del ensayo de Bernoulli. No permitía realizar múltiples ensayos independientes y solo retornaba un booleano (`True` o `False`):

```python
def siguiente_bernoulli(self, p: float) -> bool:
    return self.gcl.siguiente_u() < p

# Alias por compatibilidad
def siguiente_binomial(self, p: float) -> bool:
    return self.siguiente_bernoulli(p)
```

**Limitación:** No cumplía con la definición de la distribución Binomial, la cual requiere un número $n$ de ensayos, y causaba que las pruebas unitarias que intentaban evaluar `siguiente_binomial(10, 0.5)` fallaran con un error de tipo (`TypeError`).

---

## Implementación Nueva (Binomial Real)

Se ha corregido la distribución binomial para que funcione de manera matemáticamente correcta según su definición clásica (la cantidad de éxitos en $n$ ensayos independientes de Bernoulli, cada uno con probabilidad $p$):

```python
def siguiente_binomial(self, n: int, p: float) -> int:
    if n < 0:
        raise ValueError("El número de ensayos n debe ser no negativo.")
    if not (0.0 <= p <= 1.0):
        raise ValueError("La probabilidad p debe estar en el rango [0, 1].")

    exitos = 0
    for _ in range(n):
        if self.gcl.siguiente_u() < p:
            exitos += 1
    return exitos
```

### Diferencias Clave:

1. **Parámetros:** Ahora acepta `n` (cantidad de ensayos) y `p` (probabilidad de éxito).
2. **Tipo de Retorno:** Devuelve un número entero (`int`) en el rango `[0, n]` correspondiente al conteo de éxitos, en lugar de un booleano.
3. **Consumo del GCL:** Realiza exactamente $n$ llamadas al Generador Congruencial Lineal.

### Equivalencia con Bernoulli:
Para conservar la lógica del simulador sin alterar los resultados:
- Un ensayo de Bernoulli clásico con probabilidad $p$ equivale a una Binomial con $n = 1$: `siguiente_binomial(1, p) == 1`.
- Esto consume un único número pseudoaleatorio del generador, manteniendo la misma secuencia aleatoria exacta y garantizando la reproducibilidad de los resultados.
