import matplotlib
matplotlib.use('TkAgg')

import asyncio
import matplotlib.pyplot as plt
from msgspec import Struct
from typing import List, Tuple

# Importamos las definiciones de mensajes
from mensajes import EstadoVehiculo, PosicionConos
# Importamos las herramientas del starting_pack
from starting_pack import subscribe, timer, start

# --- Estado del Visualizador ---
# Guardaremos aquí la última información que recibamos del simulador.
class VisualizadorState(Struct):
    ultima_pos_x: float = 0.0
    ultima_pos_y: float = 0.0
    ultimo_angulo: float = 0.0
    conos: List[Tuple[float, float]] = []

state = VisualizadorState()

# --- Configuración del Gráfico (Matplotlib) ---
# Activamos el modo interactivo para que el gráfico se actualice solo.
plt.ion()
fig, ax = plt.subplots(figsize=(8, 6)) # Creamos una figura y un eje para dibujar

# --- Suscriptores a los Datos del Mundo ---

@subscribe("estado.vehiculo", EstadoVehiculo)
async def on_estado_vehiculo(msg: EstadoVehiculo):
    """Actualiza el estado local con la última posición del vehículo."""
    state.ultima_pos_x = msg.pos_x
    state.ultima_pos_y = msg.pos_y
    state.ultimo_angulo = msg.angulo

@subscribe("mundo.conos", PosicionConos)
async def on_posicion_conos(msg: PosicionConos):
    """Guarda la posición de los conos. Normalmente se recibe solo una vez."""
    if not state.conos: # Solo los guardamos la primera vez que llegan
        state.conos = msg.conos
        # Dibujamos los conos como puntos azules ('bo')
        ax.plot([c[0] for c in state.conos], [c[1] for c in state.conos], 'bo', markersize=10)
        ax.set_title("Simulador de Vehículo")
        ax.set_xlabel("Posición X (m)")
        ax.set_ylabel("Posición Y (m)")
        ax.grid(True)
        ax.set_aspect('equal', adjustable='box') # Ejes a la misma escala


# --- Bucle de Dibujado ---
# Usamos un objeto para poder referenciar el dibujo del coche y borrarlo después.
coche_plot = None

@timer(1/30) # Actualizamos el gráfico 30 veces por segundo
async def dibujar_escena():
    """Borra y redibuja la posición del coche en el gráfico."""
    global coche_plot
    
    # Si el coche ya ha sido dibujado antes, lo borramos para dibujar el nuevo.
    if coche_plot:
        # `pop` saca el elemento de la lista y lo devuelve, `remove` lo borra.
        coche_plot.pop(0).remove()

    # Dibujamos el coche como una flecha roja ('r>')
    # Usamos `plot` que es más rápido para un solo punto que `scatter`
    coche_plot = ax.plot(state.ultima_pos_x, state.ultima_pos_y, 'r>', markersize=12)

    # Forzamos a que el gráfico se actualice en la pantalla
    plt.draw()
    plt.pause(0.001)


# --- Arranque del Programa ---
if __name__ == "__main__":
    print("Iniciando visualizador...")
    print("NOTA: Cierra la ventana del gráfico para detener el programa.")
    asyncio.run(start())