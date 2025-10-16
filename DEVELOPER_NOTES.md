# Notas del Desarrollador para el Proyecto de Simulación

Aquí se documentan algunas decisiones de diseño, el estado actual del proyecto y posibles ideas para futuras mejoras.

## Estado Actual del Proyecto

El proyecto está 100% funcional y cumple con todos los requisitos del enunciado.

- **Simulador:** La física del vehículo es estable y el circuito se puede personalizar fácilmente modificando las coordenadas de los conos en `simuladorpy`.
- **Conductor Autónomo:** Se ha implementado un algoritmo robusto de seguimiento de "waypotouch lanzar_todo.shts" con memoria. El coche calcula una línea de carrera óptima y ajusta su velocidad dinámicamente en las curvas para mantenerse en la pista.
- **Visualizador:** Es interactivo, con una cámara que sigue al vehículo y una función de zoom con la rueda del ratón.
- **Control Manual:** Se incluye un `conductor_manual.py` para pruebas y depuración, que permite controlar el coche con el teclado.

## Decisiones de Diseño Clave 💡

- **Seguimiento de Waypoints:** Después de probar algoritmos más simples (como seguir al cono más cercano), se optó por un sistema de waypoints. Este método es mucho más estable y predecible, ya que el coche sigue una ruta pre-calculada en lugar de reaccionar constantemente a los límites del circuito. Esto evita que el coche "dude" o tome atajos indeseados.
- **Velocidad Dinámica:** Se implementó una lógica donde el coche frena en las curvas (cuando el error de ángulo es grande) y acelera en las rectas. Esto fue crucial para evitar que se saliera de la pista en las curvas cerradas y le da un comportamiento mucho más realista.
- **Arquitectura Modular:** La separación estricta entre el simulador, el conductor y el visualizador permite que cualquier parte pueda ser modificada o reemplazada sin afectar a las demás. Por ejemplo, se podría crear un nuevo `conductor.py` con un algoritmo de redes neuronales sin cambiar una sola línea del simulador.

## Posibles Mejoras a Futuro

Si se continuara con el proyecto, estos serían los siguientes pasos lógicos:

- **Mejorar la Física:** Añadir conceptos como la fricción o la inercia para un comportamiento aún más realista.
- **Circuitos Múltiples:** Permitir cargar diferentes trazados de circuitos desde archivos externos (por ejemplo, un archivo JSON).
- **Guardar el punto de salida:** Guardar el punto de salida como variable para no tener que actualizarlo cuando cambies el circuito.