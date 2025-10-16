import matplotlib
matplotlib.use('TkAgg')

import asyncio
import matplotlib.pyplot as plt
from msgspec import Struct
from typing import List, Tuple

from mensajes import EstadoVehiculo, PosicionConos, RutaConduccion
from starting_pack import subscribe, timer, start

# --- Estado del Visualizador ---
class VisualizadorState(Struct):
    ultima_pos_x: float = 0.0
    ultima_pos_y: float = 0.0
    ultimo_angulo: float = 0.0
    # Flags para controlar qué se ha dibujado ya
    conos_dibujados: bool = False
    ruta_dibujada: bool = False

state = VisualizadorState()

# --- Configuración del Gráfico ---
plt.ion()
fig, ax = plt.subplots(figsize=(8, 8))
coche_plot_artists = []

# --- Suscriptores (Ahora solo dibujan una vez) ---

@subscribe("estado.vehiculo", EstadoVehiculo)
async def on_estado_vehiculo(msg: EstadoVehiculo):
    # Este suscriptor solo actualiza los datos, no dibuja nada
    state.ultima_pos_x = msg.pos_x
    state.ultima_pos_y = msg.pos_y
    state.ultimo_angulo = msg.angulo

@subscribe("mundo.conos", PosicionConos)
async def on_posicion_conos(msg: PosicionConos):
    # Dibuja los conos UNA SOLA VEZ
    if not state.conos_dibujados:
        ax.plot([c[0] for c in msg.conos_interiores], [c[1] for c in msg.conos_interiores], 'bo', markersize=10, label='Interior')
        ax.plot([c[0] for c in msg.conos_exteriores], [c[1] for c in msg.conos_exteriores], 'go', markersize=10, label='Exterior')
        ax.set_title("Simulador de Vehículo Autónomo")
        ax.set_xlabel("Posición X (m)")
        ax.set_ylabel("Posición Y (m)")
        ax.grid(True)
        ax.set_aspect('equal', adjustable='box')
        ax.legend() # Llama a la leyenda aquí
        state.conos_dibujados = True

@subscribe("ruta.conduccion", RutaConduccion)
async def on_ruta_recibida(msg: RutaConduccion):
    # Dibuja la ruta UNA SOLA VEZ
    if not state.ruta_dibujada:
        ax.plot([wp[0] for wp in msg.waypoints], [wp[1] for wp in msg.waypoints], 'k.:', label='Línea de Carrera')
        ax.legend() # Actualiza la leyenda para incluir la ruta
        state.ruta_dibujada = True

# --- Bucle de Dibujado (Ahora solo se ocupa del coche) ---

@timer(1/30)
async def dibujar_coche():
    global coche_plot_artists
    
    if coche_plot_artists:
        for artist in coche_plot_artists: artist.remove()
    
    transformacion = matplotlib.transforms.Affine2D().rotate(state.ultimo_angulo)
    coche_plot_artists = ax.plot(state.ultima_pos_x, state.ultima_pos_y,
                                 marker=matplotlib.markers.MarkerStyle(marker='>', transform=transformacion),
                                 linestyle='none', markersize=15, color='r')
    plt.draw()
    plt.pause(0.001)

# --- Arranque del Programa ---
if __name__ == "__main__":
    print("Iniciando visualizador...")
    asyncio.run(start())