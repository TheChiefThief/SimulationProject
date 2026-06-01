# Arquitectura Modular Completada

He finalizado exitosamente el proceso de modularización del motor de simulación. Ahora el proyecto es más mantenible, cada clase tiene una única responsabilidad y la dependencia del archivo monolítico `simulacion.py` ha sido completamente removida.

> [!NOTE]
> La refactorización se hizo respetando estrictamente la lógica matemática y los resultados originales.

## Cambios Realizados

1.  **Extracción de Modelos de Datos**
    - Se creó un nuevo archivo limpio **[`core/resultados.py`](SimulationProject/core/resultados.py)**.
    - Se movieron las clases que almacenan el estado y dinero resultante (`ResultadoCamara`, `ResultadoDVR`, `ResultadoLote`) a este nuevo archivo.
2.  **Eliminación de Código Muerto y Duplicado**
    - Se eliminó completamente el archivo gigante **`core/simulacion.py`**, ya que todo su contenido funcional había sido trasladado a `simuladores/` (por la IA anterior) y ahora sus modelos de datos a `resultados.py`.
3.  **Actualización de Enrutamiento (Imports)**
    - Se actualizaron todos los archivos del proyecto que dependían del antiguo motor centralizado para que apunten a los nuevos módulos específicos:
        - `core/simuladores/simulador_camara.py`
        - `core/simuladores/simulador_dvr.py`
        - `core/simulacion_service.py`
        - `core/indicadores/calculador.py`
        - `gui/ventana_resultados.py`
4. **Limpieza en `gui/vista_usuario.py`**:
   - Eliminamos la función interna repetitiva `_fila_resultado` y el método `_set_entry`.
   - Ahora utilizamos el objeto `CTKResultRow` que permite actualizar los valores calculados de forma orientada a objetos (usando `self.out_peso.set(...)`).

5. **Scrollable en `gui/vista_config.py`**:
   - Envolvimos las tres columnas de campos de configuración en un `ctk.CTkScrollableFrame` (`self.scroll_contenedor`) dentro de `VistaConfig`.
   - Esto evita que los campos inferiores (como "Almacenamiento máx $/GB") se deformen o queden ocultos en pantallas de menor resolución, manteniendo el botón "Guardar Configuración" fijado estáticamente en la parte inferior para una mejor experiencia de usuario.

6. **Remoción de pruebas obsoletas**:
   - Eliminamos `tests/test_prueba_estadistica.py` dado que hacía referencia a la clase `PruebaKolmogorovSmirnov` que fue previamente eliminada por estar sin uso ("al pedo").

## Verificación

- Ejecutamos la suite de pruebas mediante `python -m pytest` y los 49 tests existentes pasaron correctamente.
- Si vuelves a iniciar el programa, la pestaña **Configuración** ahora permitirá scroll si la ventana es pequeña y todos los inputs se verán legibles y con su tamaño correcto.

> [!TIP]
> Al estar separados, si en un futuro decides cambiar el estilo gráfico de los *inputs* (por ejemplo, hacerlos más redondeados, o cambiarles la fuente globalmente), ¡solo tendrás que modificar `componentes.py` una vez!

El proyecto está listo para continuar su desarrollo. ¡La base de código ahora es mucho más limpia y profesional!
