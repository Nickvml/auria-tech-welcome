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
    conos_dibujados: bool = False
    ruta_dibujada: bool = False
    # ¡NUEVO! Guardamos el nivel de zoom actual
    zoom_level: float = 30.0 # Empezamos con una vista de 30 metros

state = VisualizadorState()

# --- Configuración del Gráfico ---
plt.ion()
fig, ax = plt.subplots(figsize=(8, 8), num='Simulador de Vehículo Auria Technologies- Vicente Nicolás')
coche_plot_artists = []

# --- ¡NUEVO! Función de Zoom ---
def on_scroll(event):
    """Se activa al usar la rueda del ratón sobre el gráfico."""
    # 'up' para acercar, 'down' para alejar
    if event.button == 'up':
        # Acercar: reducimos el tamaño de la vista (mínimo 5 metros)
        state.zoom_level = max(5.0, state.zoom_level / 1.2)
    elif event.button == 'down':
        # Alejar: aumentamos el tamaño de la vista (máximo 100 metros)
        state.zoom_level = min(100.0, state.zoom_level * 1.2)

# Conectamos nuestra función de zoom al gráfico
fig.canvas.mpl_connect('scroll_event', on_scroll)


# --- Suscriptores (Sin cambios) ---
@subscribe("estado.vehiculo", EstadoVehiculo)
async def on_estado_vehiculo(msg: EstadoVehiculo):
    state.ultima_pos_x = msg.pos_x
    state.ultima_pos_y = msg.pos_y
    state.ultimo_angulo = msg.angulo

@subscribe("mundo.conos", PosicionConos)
async def on_posicion_conos(msg: PosicionConos):
    if not state.conos_dibujados:
        ax.plot([c[0] for c in msg.conos_interiores], [c[1] for c in msg.conos_interiores], 'bo', markersize=10, label='Interior')
        ax.plot([c[0] for c in msg.conos_exteriores], [c[1] for c in msg.conos_exteriores], 'go', markersize=10, label='Exterior')
        ax.set_title("Simulador de Vehículo Autónomo")
        ax.set_xlabel("Posición X (m)")
        ax.set_ylabel("Posición Y (m)")
        ax.grid(True)
        ax.set_aspect('equal', adjustable='box')
        ax.legend()
        state.conos_dibujados = True

@subscribe("ruta.conduccion", RutaConduccion)
async def on_ruta_recibida(msg: RutaConduccion):
    if not state.ruta_dibujada:
        # ax.plot([wp[0] for wp in msg.waypoints], [wp[1] for wp in msg.waypoints], 'k.:', label='Línea de Carrera')
        ax.legend()
        state.ruta_dibujada = True

# --- Bucle de Dibujado (Modificado para usar el zoom) ---
@timer(1/30)
async def dibujar_coche():
    global coche_plot_artists
    
    if coche_plot_artists:
        for artist in coche_plot_artists: artist.remove()
    
    transformacion = matplotlib.transforms.Affine2D().rotate(state.ultimo_angulo)
    coche_plot_artists = ax.plot(state.ultima_pos_x, state.ultima_pos_y,
                                 marker=matplotlib.markers.MarkerStyle(marker='>', transform=transformacion),
                                 linestyle='none', markersize=15, color='r')
    
    # --- CÁMARA CON ZOOM ---
    # Centramos la vista, pero el tamaño ahora depende del nivel de zoom
    radio_vista = state.zoom_level / 2
    ax.set_xlim(state.ultima_pos_x - radio_vista, state.ultima_pos_x + radio_vista)
    ax.set_ylim(state.ultima_pos_y - radio_vista, state.ultima_pos_y + radio_vista)
    
    plt.draw()
    plt.pause(0.001)

# --- Arranque del Programa ---
if __name__ == "__main__":
    print("Iniciando visualizador...")
    print("¡Usa la rueda del ratón sobre el gráfico para hacer zoom!")
    asyncio.run(start())