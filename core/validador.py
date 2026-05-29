"""core/validador.py
------------------
Módulo centralizado de validación de entradas. Proporciona métodos estrictos
para validar tipos de datos enteros, reales, fracciones y restricciones de negocio.
"""

import math


class Validador:
    """
    Clase estática para validar y parsear datos de entrada.
    Lanza ValueError con mensajes claros en español ante cualquier inconsistencia.
    """

    @staticmethod
    def validar_entero(texto: str, nombre_campo: str, min_valor: int = None, max_valor: int = None) -> int:
        """
        Valida que un texto sea un número entero válido y esté dentro de un rango opcional.

        Args:
            texto: Texto ingresado.
            nombre_campo: Nombre descriptivo para el error.
            min_valor: Valor mínimo permitido (inclusive).
            max_valor: Valor máximo permitido (inclusive).

        Returns:
            El número entero parseado.
        """
        texto_limpio = texto.strip()
        if not texto_limpio:
            raise ValueError(f"El campo '{nombre_campo}' no puede estar vacío.")

        try:
            # Intentamos el cast directo. Python rechaza letras y flotantes como '1.5' en int()
            valor = int(texto_limpio)
        except ValueError:
            raise ValueError(
                f"El campo '{nombre_campo}' debe ser un número entero válido. "
                f"No se aceptan letras, decimales ni caracteres especiales."
            )

        if min_valor is not None and valor < min_valor:
            raise ValueError(f"El valor de '{nombre_campo}' no puede ser menor a {min_valor}.")

        if max_valor is not None and valor > max_valor:
            raise ValueError(f"El valor de '{nombre_campo}' no puede ser mayor a {max_valor}.")

        return valor

    @staticmethod
    def validar_float(texto: str, nombre_campo: str, min_valor: float = None, max_valor: float = None) -> float:
        """
        Valida que un texto sea un número decimal válido y esté dentro de un rango opcional.

        Args:
            texto: Texto ingresado.
            nombre_campo: Nombre descriptivo para el error.
            min_valor: Valor mínimo permitido (inclusive).
            max_valor: Valor máximo permitido (inclusive).

        Returns:
            El número decimal (float) parseado.
        """
        texto_limpio = texto.strip()
        if not texto_limpio:
            raise ValueError(f"El campo '{nombre_campo}' no puede estar vacío.")

        # Evitamos 'inf', 'nan' y similares que float() acepta por defecto en Python
        if texto_limpio.lower() in ("inf", "infinity", "nan", "-inf", "-infinity", "+inf", "+infinity"):
            raise ValueError(
                f"El campo '{nombre_campo}' contiene un valor no permitido."
            )

        try:
            valor = float(texto_limpio)
        except ValueError:
            raise ValueError(
                f"El campo '{nombre_campo}' debe ser un número decimal válido. "
                f"No se aceptan letras ni caracteres especiales."
            )

        if math.isnan(valor) or math.isinf(valor):
            raise ValueError(f"El campo '{nombre_campo}' contiene un número decimal inválido.")

        if min_valor is not None and valor < min_valor:
            raise ValueError(f"El valor de '{nombre_campo}' no puede ser menor a {min_valor}.")

        if max_valor is not None and valor > max_valor:
            raise ValueError(f"El valor de '{nombre_campo}' no puede ser mayor a {max_valor}.")

        return valor

    @staticmethod
    def validar_fraccion(texto: str, nombre_campo: str) -> float:
        """
        Valida que un texto sea una fracción decimal válida en el rango [0.0, 1.0].
        """
        return Validador.validar_float(texto, nombre_campo, min_valor=0.0, max_valor=1.0)

    @staticmethod
    def validar_precio(texto: str, nombre_campo: str) -> float:
        """
        Valida que un texto sea un precio válido (mayor a 0.0).
        """
        return Validador.validar_float(texto, nombre_campo, min_valor=0.01)

    @staticmethod
    def validar_suma_cercana_uno(valores: list[float], nombres: list[str], dispositivo: str) -> None:
        """
        Valida que la suma de fracciones sea aproximadamente 1.0 (100%).
        Rango de tolerancia técnica estricta: [0.99, 1.01].
        """
        suma = sum(valores)
        if not (0.99 <= suma <= 1.01):
            detalle_valores = ", ".join(f"{nom}: {val*100:.1f}%" for nom, val in zip(nombres, valores))
            raise ValueError(
                f"La suma de las fracciones de {dispositivo} debe ser aproximadamente 100% (1.0).\n"
                f"Suma actual: {suma*100:.1f}%\n"
                f"Composición actual: ({detalle_valores})"
            )
