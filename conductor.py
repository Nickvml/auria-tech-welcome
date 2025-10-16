import asyncio
import math
from msgspec import Struct

from starting_pack import subscribe, timer, publish, start
from mensajes import EstadoVehiculo, PosicionConos, ControlVehiculo

# --- Funciones de Geometría (las mismas que antes) ---
def distancia_entre_puntos(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def angulo_hacia_punto(pos_actual, angulo_actual, punto_objetivo):
    angulo_objetivo = math.atan2(punto_objetivo[1] - pos_actual[1], punto_objetivo[0] - pos_actual[0])
    error_angulo = angulo_objetivo - angulo_actual
    while error_angulo > math.pi: error_angulo -= 2 * math.pi
    while error_angulo < -math.pi: error_angulo += 2 * math.pi
    return error_angulo

# --- Estado del Conductor ---
class ConductorState(Struct):
    pos_x: float = 0.0
    pos_y: float = 0.0
    angulo: float = 0.0
    conos_interiores: list[tuple[float, float]] = []
    conos_exteriores: list[tuple[float, float]] = []

state = ConductorState()

# --- Suscriptores de Información ---
@subscribe("estado.vehiculo", EstadoVehiculo)
async def on_estado_vehiculo(msg: EstadoVehiculo):
    state.pos_x, state.pos_y, state.angulo = msg.pos_x, msg.pos_y, msg.angulo

@subscribe("mundo.conos", PosicionConos)
async def on_posicion_conos(msg: PosicionConos):
    if not state.conos_interiores:
        state.conos_interiores = msg.conos_interiores
        state.conos_exteriores = msg.conos_exteriores

# --- Lógica de Conducción Autónoma ---
@timer(1/20)
async def bucle_conduccion():
    """El cerebro del piloto: decide y publica los controles."""
    if not state.conos_interiores:
        await publish("controles.vehiculo", ControlVehiculo(aceleracion=0.0, giro=0.0))
        return

    pos_coche = (state.pos_x, state.pos_y)

    # 1. Encontrar el par de conos más cercano para saber dónde estamos.
    distancias = [distancia_entre_puntos(pos_coche, cono) for cono in state.conos_interiores]
    idx_cono_cercano = min(range(len(distancias)), key=distancias.__getitem__)
    
    # 2. Mirar UN punto hacia adelante para suavizar la trayectoria.
    idx_objetivo = (idx_cono_cercano + 1) % len(state.conos_interiores)
    cono_interior_obj = state.conos_interiores[idx_objetivo]
    cono_exterior_obj = state.conos_exteriores[idx_objetivo]

    # 3. Calcular el punto objetivo con un BIAS hacia el exterior.
    BIAS_EXTERIOR = 0.65 # Ajustado a 65% para un buen equilibrio
    punto_objetivo = (
        cono_interior_obj[0] * (1 - BIAS_EXTERIOR) + cono_exterior_obj[0] * BIAS_EXTERIOR,
        cono_interior_obj[1] * (1 - BIAS_EXTERIOR) + cono_exterior_obj[1] * BIAS_EXTERIOR
    )

    # 4. Calcular el giro necesario.
    error_de_angulo = angulo_hacia_punto(pos_coche, state.angulo, punto_objetivo)
    giro_calculado = error_de_angulo * 4.0 # Aumentamos la agresividad del giro

    # 5. ¡NUEVO! CÁLCULO DE VELOCIDAD DINÁMICA
    # Cuanto mayor sea el error de ángulo (más cerrada la curva), menor será la aceleración.
    # abs() calcula el valor absoluto, no nos importa si la curva es a izq. o der.
    factor_frenado = abs(error_de_angulo) * 0.8 
    aceleracion_calculada = 1.5 - factor_frenado
    # Nos aseguramos de que el coche siempre vaya un poco hacia adelante.
    aceleracion_calculada = max(0.3, aceleracion_calculada) 

    # Publicar los controles.
    control = ControlVehiculo(aceleracion=aceleracion_calculada, giro=giro_calculado)
    await publish("controles.vehiculo", control)

# --- Arranque ---
if __name__ == "__main__":
    print("Iniciando conductor autónomo (modo carril)...")
    asyncio.run(start())