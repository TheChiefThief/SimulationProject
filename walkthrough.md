# Refactorización de Componentes de la Interfaz

¡La separación de código repetido en clases ha sido completada exitosamente! 

## Cambios Realizados

1. **Nuevo módulo `gui/componentes.py`**:
   - `CTKLabeledEntry`: Un componente personalizado (hereda de `CTkFrame`) que agrupa la creación y el empaquetado de la etiqueta principal (`CTkLabel`), la etiqueta secundaria de ayuda, y el campo de entrada (`CTkEntry`). Incluye métodos útiles como `.get()` y `.set()`.
   - `CTKResultRow`: Un componente personalizado para mostrar las filas de resultados en formato de solo lectura, con soporte integrado para iconos y prefijos.

2. **Limpieza en `gui/vista_gerente.py`**:
   - Reemplazamos todos los bloques repetitivos de creación manual de entradas por instancias limpias de `CTKLabeledEntry`.
   - El código de construcción de la interfaz es ahora mucho más corto, legible y directo.

3. **Limpieza en `gui/vista_config.py`**:
   - Actualizamos el método local `_campo` para que utilice internamente el nuevo `CTKLabeledEntry`. 
   - El módulo completo ahora requiere muchas menos configuraciones manuales de empaquetado.

4. **Limpieza en `gui/vista_usuario.py`**:
   - Eliminamos la función interna repetitiva `_fila_resultado` y el método `_set_entry`.
   - Ahora utilizamos el objeto `CTKResultRow` que permite actualizar los valores calculados de forma orientada a objetos (usando `self.out_peso.set(...)`).

5. **Scrollable en `gui/vista_config.py`**:
   - Envolvimos las tres columnas de campos de configuración en un `ctk.CTkScrollableFrame` (`self.scroll_contenedor`) dentro de VistaConfig.
   - Esto evita que los campos inferiores (como "Almacenamiento máx $/GB") se deformen o queden ocultos en pantallas de menor resolución, manteniendo el botón "Guardar Configuración" fijado estáticamente en la parte inferior para una mejor experiencia de usuario.

6. **Remoción de pruebas obsoletas**:
   - Eliminamos `tests/test_prueba_estadistica.py` dado que hacía referencia a la clase `PruebaKolmogorovSmirnov` que fue previamente eliminada por estar sin uso ("al pedo").

## Fase 2: Implementación del Patrón Observer (Event Bus)

Hemos desacoplado la comunicación directa entre las vistas mediante un sistema de publicación/suscripción:

1. **Observer en `ParametrosSistema` (`core/parametros.py`)**:
   - Agregamos los métodos `suscribir(evento, callback)` y `notificar(evento)`.
   - Convertimos `parametros_cargados` en una `@property` de Python. Cuando este valor pasa a `True` desde cualquier origen, automáticamente se llama a `notificar("parametros_cargados")`.

2. **Suscripción de `VistaUsuario` (`gui/vista_usuario.py`)**:
   - En el `__init__`, la vista del usuario se suscribe al evento `"parametros_cargados"` para actualizar su estado de manera automática mediante `self.actualizar_estado_parametros`.

3. **Remoción de callbacks manuales**:
   - Eliminamos los callbacks y propagaciones directas (`callback_parametros_cargados` y `callback_config_guardada`) en `gui/app.py`, `gui/vista_gerente.py` y `gui/vista_config.py`.

## Mejoras de Diseño y Responsividad

- **Rediseño de la Vista del Gerente (`gui/vista_gerente.py`)**:
  - Eliminamos la sección de "Indicadores de Productividad" que no se utilizaba en esta vista.
  - Trasladamos los botones de acción ("Cargar Parámetros", "Valores Base") y el panel de presets al panel derecho ("Estado del Sistema"), dejando el panel izquierdo exclusivamente para los campos de entrada de parámetros operativos, lo cual resulta en una interfaz mucho más equilibrada y limpia.
- **Filas de Reporte Responsivas (`gui/componentes.py` -> `CTKKeyValueRow`)**:
  - Cambiamos el layout de `CTKKeyValueRow` a sistema de cuadrícula (grid) y enlazamos el evento `<Configure>`.
  - Ahora el ancho para el texto del valor se calcula dinámicamente según el tamaño de la ventana (usando `wraplength`). Esto hace que listas largas (como las estaciones de cuello de botella) se ajusten y muestren en varias líneas sin solapar el texto de la etiqueta izquierda al escalar la ventana.
- **Separación Ajustable en Ventana de Resultados (`gui/ventana_resultados.py`)**:
  - Implementamos un panel deslizable (`tk.PanedWindow`) en lugar del diseño de rejilla fija.
  - El usuario ahora puede arrastrar el divisor central para ajustar el ancho del panel de informe izquierdo y del panel de gráficos derecho a su gusto.

## Mejoras de Exportación

- **Nombre de archivo por defecto basado en la fecha**: Ahora, cuando exportas una simulación desde el historial (o a través de la ventana de detalles del historial), el diálogo de guardado sugiere automáticamente un nombre predefinido que incluye la fecha y hora de dicha simulación (ej. `Simulacion_2026-06-01_16-50-36.pdf` / `.xlsx`), facilitando la organización de los archivos.

## Fase 3: Desacoplamiento de Lógica (Controladores / MVC)

Hemos aplicado el patrón MVC (Modelo-Vista-Controlador) para desacoplar completamente la lógica de negocio y de validación de las interfaces gráficas:

1. **Controladores Reutilizables**:
   - Creación de [`gui/controllers/config_controller.py`](file:///c:/Users/lucia/Desktop/Simulador\SimulationProject/gui/controllers/config_controller.py): Contiene toda la lógica de validación de entradas de precios, fracciones y composición de la configuración.
   - Creación de [`gui/controllers/gerente_controller.py`](file:///c:/Users/lucia/Desktop/Simulador\SimulationProject/gui/controllers/gerente_controller.py): Agrupa la validación de parámetros de jornada, gestión de presets de simulación, y restauración de valores por defecto.

2. **Vistas Pasivas**:
   - Refactorizamos `VistaConfig` y `VistaGerente` para que actúen como "vistas pasivas". Ya no contienen lógica de validación ni interactúan con el modelo directamente al guardar; en su lugar instancian a su respectivo controlador y exponen una interfaz limpia con métodos como `.obtener_datos()`, `.cargar_datos()`, `.mostrar_error()`, y `.mostrar_exito()`.

## Fase 4: Optimización de Navegación (Lazy Loading)

Hemos optimizado el arranque de la aplicación cargando las pestañas bajo demanda:

1. **Instanciación bajo Demanda (`gui/app.py`)**:
   - Eliminamos las importaciones estáticas de las vistas y removimos su inicialización al iniciar.
   - En su lugar, el diccionario `self.vistas_cacheadas` almacena las vistas a medida que el usuario navega a ellas.
   - Si la vista solicitada no está instanciada, se importa dinámicamente y se monta en caliente dentro de `_mostrar_vista(nombre_vista)`, optimizando notablemente el uso de memoria y la velocidad de arranque inicial de la UI.

## Restauración de Pruebas Estadísticas

- **Bondad de Ajuste K-S**: Restauramos completamente la clase de análisis estadístico de Kolmogorov-Smirnov (`PruebaKolmogorovSmirnov`) en [`core/prueba_estadistica.py`](file:///c:/Users/lucia/Desktop/Simulador/SimulationProject/core/prueba_estadistica.py) junto con sus tests unitarios en [`tests/test_prueba_estadistica.py`](file:///c:/Users/lucia/Desktop/Simulador/SimulationProject/tests/test_prueba_estadistica.py).

## Verificación

- Ejecutamos la suite de pruebas mediante `python -m pytest` y los **55 tests existentes** (incluyendo las pruebas de uniformidad del GCL) pasaron correctamente sin fallos.
- La navegación en la UI responde de manera fluida y realiza la instanciación tardía de forma transparente para el usuario.

> [!TIP]
> Al estar separados, si en un futuro decides cambiar el estilo gráfico de los *inputs* (por ejemplo, hacerlos más redondeados, o cambiarles la fuente globalmente), ¡solo tendrás que modificar `componentes.py` una vez!
