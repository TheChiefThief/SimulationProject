"""
core/parametros.py
------------------
Define la clase ParametrosSistema, que actúa como contenedor de estado
global para toda la aplicación. Almacena precios, composiciones, tasas
de recuperación y parámetros operativos.

El flag `parametros_cargados` controla si el sistema está habilitado
para ejecutar una simulación. La aplicación NO debe correr sin carga
previa de parámetros.
"""


class ParametrosSistema:
    """
    Contenedor de todos los parámetros configurables del simulador.

    Atributos de precios (ARS):
        precio_oro          : ARS por kg de oro
        precio_vidrio       : ARS por kg de vidrio
        precio_lentes       : ARS por unidad de lente funcional
        precio_cobre        : ARS por kg de cobre
        precio_aluminio     : ARS por kg de aluminio
        precio_plastico     : ARS por kg de plástico
        precio_almacenamiento_min : ARS por GB (mínimo)
        precio_almacenamiento_max : ARS por GB (máximo)

    Atributos de composición (fracción 0–1):
        camara_fraccion_plastico   : fracción de plástico en cámaras
        camara_fraccion_placas     : fracción de placas en cámaras
        camara_fraccion_metal      : fracción de metal en cámaras
        camara_fraccion_opticos    : fracción de ópticos en cámaras
        dvr_fraccion_hdd           : fracción de HDD en DVRs
        dvr_fraccion_metal         : fracción de metal en DVRs
        dvr_fraccion_placas        : fracción de placas en DVRs

    Atributos de peso promedio (kg):
        peso_camara : peso promedio de una cámara
        peso_dvr    : peso promedio de un DVR

    Tasas de recuperación (fracción 0–1):
        tasa_placas_sanas    : fracción de placas recuperadas funcionalmente
        tasa_opticas_sanas   : fracción de componentes ópticos sanos
        tasa_discos_sanos    : fracción de HDDs operativos

    Parámetros operativos (cargados desde Vista Gerente):
        horas_trabajo        : horas por jornada
        cantidad_empleados   : número de operarios
        energia_consumida    : kWh consumidos
        coeficiente_perdida  : fracción de pérdida en el proceso (0–1)
        tipo_maquinaria      : string descriptivo del tipo de equipo

    Control de flujo:
        parametros_cargados  : True solo si los parámetros operativos
                               fueron validados y guardados por el usuario.
    """

    def __init__(self):
        # ----------------------------------------------------------------
        # Precios de referencia (ARS) — valores por defecto del documento
        # ----------------------------------------------------------------
        self.precio_oro: float = 210_000.0        # ARS/kg
        self.precio_vidrio: float = 150_000.0     # ARS/kg
        self.precio_lentes: float = 60_000.0      # ARS/unidad
        self.precio_cobre: float = 8_500.0        # ARS/kg
        self.precio_aluminio: float = 1_500.0     # ARS/kg
        self.precio_plastico: float = 60.0        # ARS/kg
        self.precio_almacenamiento_min: float = 50.0   # ARS/GB
        self.precio_almacenamiento_max: float = 100.0  # ARS/GB

        # ----------------------------------------------------------------
        # Composición de materiales (fracción del peso total)
        # ----------------------------------------------------------------
        # Cámaras de seguridad
        self.camara_fraccion_plastico: float = 0.60
        self.camara_fraccion_placas: float = 0.20
        self.camara_fraccion_metal: float = 0.10
        self.camara_fraccion_opticos: float = 0.10

        # DVRs
        self.dvr_fraccion_hdd: float = 0.45
        self.dvr_fraccion_metal: float = 0.30
        self.dvr_fraccion_placas: float = 0.25

        # ----------------------------------------------------------------
        # Peso promedio por dispositivo (kg)
        # ----------------------------------------------------------------
        self.peso_camara: float = 1.14
        self.peso_dvr: float = 1.12

        # ----------------------------------------------------------------
        # Tasas de recuperación por componente (fracción 0–1)
        # ----------------------------------------------------------------
        self.tasa_placas_sanas: float = 0.75
        self.tasa_opticas_sanas: float = 0.70
        self.tasa_discos_sanos: float = 0.65

        # ----------------------------------------------------------------
        # Parámetros operativos (a cargar desde Vista Gerente)
        # ----------------------------------------------------------------
        self.horas_trabajo: float = 8.0
        self.cantidad_empleados: int = 5
        self.energia_consumida: float = 100.0     # kWh
        self.coeficiente_perdida: float = 0.05    # 5% de pérdida
        self.tipo_maquinaria: str = "Proceso Manual"

        # ----------------------------------------------------------------
        # Rendimientos de materiales base (fracción 0–1)
        # ----------------------------------------------------------------
        self.rendimiento_plastico: float = 0.80
        self.rendimiento_metal: float = 0.85

        # ----------------------------------------------------------------
        # Control de flujo — CRÍTICO
        # ----------------------------------------------------------------
        self.parametros_cargados: bool = False

    def validar(self) -> list[str]:
        """
        Valida la coherencia interna de los parámetros.

        Returns:
            Lista de mensajes de error. Lista vacía si todo es válido.
        """
        errores = []

        # Precios no negativos
        precios = {
            "Precio Oro": self.precio_oro,
            "Precio Vidrio": self.precio_vidrio,
            "Precio Lentes": self.precio_lentes,
            "Precio Cobre": self.precio_cobre,
            "Precio Aluminio": self.precio_aluminio,
            "Precio Plástico": self.precio_plastico,
            "Precio Almacenamiento Mín": self.precio_almacenamiento_min,
            "Precio Almacenamiento Máx": self.precio_almacenamiento_max,
        }
        for nombre, valor in precios.items():
            if valor < 0:
                errores.append(f"{nombre} no puede ser negativo.")

        # Coeficiente de pérdida en [0, 1]
        if not (0.0 <= self.coeficiente_perdida <= 1.0):
            errores.append("El coeficiente de pérdida debe estar entre 0 y 1.")

        # Horas y empleados positivos
        if self.horas_trabajo <= 0:
            errores.append("Las horas de trabajo deben ser mayores a 0.")
        if self.cantidad_empleados <= 0:
            errores.append("La cantidad de empleados debe ser mayor a 0.")
        if self.energia_consumida < 0:
            errores.append("La energía consumida no puede ser negativa.")

        # Precio mín ≤ precio máx de almacenamiento
        if self.precio_almacenamiento_min > self.precio_almacenamiento_max:
            errores.append(
                "El precio mínimo de almacenamiento no puede superar al máximo."
            )

        return errores

    def __repr__(self) -> str:
        estado = "CARGADOS" if self.parametros_cargados else "NO CARGADOS"
        return f"ParametrosSistema(estado={estado})"
