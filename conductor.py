import asyncio
import math
from msgspec import Struct

from mensajes import EstadoVehiculo, PosicionConos, ControlVehiculo, RutaConduccion
from starting_pack import subscribe, timer, publish, start

# --- Funciones de Geometría (sin cambios) ---
def distancia_entre_puntos(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def angulo_hacia_punto(pos_actual, angulo_actual, punto_objetivo):
    angulo_objetivo = math.atan2(punto_objetivo[1] - pos_actual[1], punto_objetivo[0] - pos_actual[0])
    error_angulo = angulo_objetivo - angulo_actual
    while error_angulo > math.pi: error_angulo -= 2 * math.pi
    while error_angulo < -math.pi: error_angulo += 2 * math.pi
    return error_angulo

# --- Estado del Conductor (con memoria) ---
class ConductorState(Struct):
    pos_x: float = 0.0
    pos_y: float = 0.0
    angulo: float = 0.0
    ruta: list[tuple[float, float]] = []
    # ¡NUEVO! Guardamos el índice del waypoint al que nos dirigimos
    idx_waypoint_actual: int = 0

state = ConductorState()

# --- Suscriptores ---
@subscribe("estado.vehiculo", EstadoVehiculo)
async def on_estado_vehiculo(msg: EstadoVehiculo):
    state.pos_x, state.pos_y, state.angulo = msg.pos_x, msg.pos_y, msg.angulo

@subscribe("mundo.conos", PosicionConos)
async def on_posicion_conos(msg: PosicionConos):
    if not state.ruta:
        print("Recibidos datos del circuito. Calculando la línea de carrera...")
        nueva_ruta = []
        BIAS_EXTERIOR = 0.6
        for i in range(len(msg.conos_interiores)):
            cono_int, cono_ext = msg.conos_interiores[i], msg.conos_exteriores[i]
            waypoint = (
                cono_int[0] * (1 - BIAS_EXTERIOR) + cono_ext[0] * BIAS_EXTERIOR,
                cono_int[1] * (1 - BIAS_EXTERIOR) + cono_ext[1] * BIAS_EXTERIOR
            )
            nueva_ruta.append(waypoint)
        state.ruta = nueva_ruta
        state.idx_waypoint_actual = 0 # Empezamos apuntando al primer waypoint
        await publish("ruta.conduccion", RutaConduccion(waypoints=state.ruta))

# --- Lógica de Conducción (con memoria) ---
@timer(1/20)
async def bucle_conduccion():
    if not state.ruta:
        await publish("controles.vehiculo", ControlVehiculo(aceleracion=0.0, giro=0.0))
        return

    # 1. Nuestro punto objetivo es el waypoint actual de nuestra memoria.
    punto_objetivo = state.ruta[state.idx_waypoint_actual]
    pos_coche = (state.pos_x, state.pos_y)

    # 2. Comprobar si hemos llegado a nuestro objetivo.
    distancia_al_objetivo = distancia_entre_puntos(pos_coche, punto_objetivo)
    # Si estamos lo suficientemente cerca...
    if distancia_al_objetivo < 5.0: # Umbral de 5 metros
        print(f"Waypoint {state.idx_waypoint_actual} alcanzado! Siguiente...")
        # ...actualizamos nuestro objetivo al siguiente waypoint de la lista.
        state.idx_waypoint_actual = (state.idx_waypoint_actual + 1) % len(state.ruta)

    # 3. El resto de la lógica de control es la misma que antes.
    error_de_angulo = angulo_hacia_punto(pos_coche, state.angulo, punto_objetivo)
    giro_calculado = error_de_angulo * 3.5

    factor_frenado = abs(error_de_angulo) * 0.7
    aceleracion_calculada = 1.2 - factor_frenado
    aceleracion_calculada = max(0.4, aceleracion_calculada)

    control = ControlVehiculo(aceleracion=aceleracion_calculada, giro=giro_calculado)
    await publish("controles.vehiculo", control)

# --- Arranque ---
if __name__ == "__main__":
    print("Iniciando conductor autónomo (modo waypoints con memoria)...")
    asyncio.run(start())