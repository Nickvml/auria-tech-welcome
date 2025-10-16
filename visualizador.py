import matplotlib
matplotlib.use('TkAgg')

import asyncio
import math
import matplotlib.pyplot as plt
from msgspec import Struct
from typing import List, Tuple

from mensajes import EstadoVehiculo, PosicionConos
from starting_pack import subscribe, timer, start

# --- Estado del Visualizador ---
class VisualizadorState(Struct):
    ultima_pos_x: float = 0.0
    ultima_pos_y: float = 0.0
    ultimo_angulo: float = 0.0
    conos_interiores: List[Tuple[float, float]] = []
    conos_exteriores: List[Tuple[float, float]] = []
    # Nuevo flag para controlar el dibujado del circuito
    circuito_dibujado: bool = False

state = VisualizadorState()

# --- Configuración del Gráfico ---
plt.ion()
fig, ax = plt.subplots(figsize=(8, 8))
coche_plot_artists = []

# --- Suscriptores (Ahora solo guardan datos) ---

@subscribe("estado.vehiculo", EstadoVehiculo)
async def on_estado_vehiculo(msg: EstadoVehiculo):
    state.ultima_pos_x = msg.pos_x
    state.ultima_pos_y = msg.pos_y
    state.ultimo_angulo = msg.angulo

@subscribe("mundo.conos", PosicionConos)
async def on_posicion_conos(msg: PosicionConos):
    # Esta función ahora es muy simple: solo guarda los datos de los conos.
    if not state.conos_interiores:
        state.conos_interiores = msg.conos_interiores
        state.conos_exteriores = msg.conos_exteriores

# --- Bucle Principal de Dibujado (Ahora lo hace todo) ---

@timer(1/30)
async def dibujar_escena():
    """Dibuja el circuito (si es necesario) y actualiza el coche."""
    global coche_plot_artists
    
    # 1. DIBUJAR EL CIRCUITO (solo una vez)
    # Si tenemos los datos de los conos Y no hemos dibujado el circuito antes...
    if state.conos_interiores and not state.circuito_dibujado:
        ax.plot([c[0] for c in state.conos_interiores], [c[1] for c in state.conos_interiores], 'bo', markersize=10, label='Interior')
        ax.plot([c[0] for c in state.conos_exteriores], [c[1] for c in state.conos_exteriores], 'go', markersize=10, label='Exterior')
        
        ax.set_title("Simulador de Vehículo Autónomo")
        ax.set_xlabel("Posición X (m)")
        ax.set_ylabel("Posición Y (m)")
        ax.grid(True)
        ax.set_aspect('equal', adjustable='box')
        ax.legend()
        
        # Activamos el flag para no volver a dibujarlo
        state.circuito_dibujado = True

    # 2. ACTUALIZAR EL COCHE (en cada fotograma)
    if coche_plot_artists:
        for artist in coche_plot_artists:
            artist.remove()
        coche_plot_artists = []

    transformacion = matplotlib.transforms.Affine2D().rotate(state.ultimo_angulo)
    coche_plot_artists = ax.plot(state.ultima_pos_x, state.ultima_pos_y,
                                 marker=matplotlib.markers.MarkerStyle(marker='>', transform=transformacion),
                                 linestyle='none', markersize=15, color='r')

    plt.draw()
    plt.pause(0.001)

# --- Arranque del Programa ---
if __name__ == "__main__":
    print("Iniciando visualizador...")
    print("NOTA: Cierra la ventana del gráfico para detener el programa.")
    asyncio.run(start())