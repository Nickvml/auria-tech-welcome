import asyncio
import math
from msgspec import Struct

# Importamos todos los mensajes necesarios aquí arriba
from mensajes import ControlVehiculo, EstadoVehiculo, PosicionConos, ComandoSimulador
from starting_pack import subscribe, timer, publish, start

# --- CONSTANTES DE SIMULACIÓN ---
DT = 1 / 60  # Delta de tiempo: simulamos a 60 "frames" por segundo.

# --- Estado del Simulador ---
class SimuladorState(Struct):
    # Estado del vehículo
    pos_x: float = 20.0
    pos_y: float = 15.0
    angulo: float = 0.0
    velocidad: float = 0.0

    # Últimos controles recibidos
    aceleracion_actual: float = 0.0
    giro_actual: float = 0.0

    #Circuito1 En mi opinión más sencillo, recorrido circular simple
    posicion_conos: PosicionConos = PosicionConos(
        conos_interiores=[
            (20, 20), (50, 20), (70, 30), (70, 50), (50, 60), (20, 60), (10, 50), (10, 30),
        ],
        conos_exteriores=[
            (20, 10), (50, 10), (80, 30), (80, 50), (50, 70), (20, 70), (0, 50), (0, 30),
        ]
    )
    """
    #Circuito1 En mi opinión más difícil, recorrido triangular 
    posicion_conos: PosicionConos = PosicionConos(
    # Borde interior
    conos_interiores=[
        (10, 20), (30, 20), (30, 40),
    ],
    # Borde exterior
    conos_exteriores=[
        (10, 10), (40, 10), (40, 40),
    ]
)
"""
state = SimuladorState()

# --- Lógica del Simulador ---

@subscribe("controles.vehiculo", ControlVehiculo)
async def on_control_recibido(msg: ControlVehiculo):
    """Actualiza el estado con los últimos valores de aceleración y giro."""
    state.aceleracion_actual = msg.aceleracion
    state.giro_actual = msg.giro

@subscribe("simulador.comando", ComandoSimulador)
async def on_comando_recibido(msg: ComandoSimulador):
    """Escucha comandos especiales como el de reseteo."""
    if msg.comando == "reset_posicion":
        print("¡Reseteando posición del vehículo a la línea de salida!")
        # Reseteamos a la posición inicial correcta
        state.pos_x = 20.0
        state.pos_y = 15.0
        state.angulo = 0.0
        state.velocidad = 0.0

@timer(DT)
async def bucle_principal():
    """Realiza un paso de la simulación física y publica el estado del mundo."""
    # 1. Actualizar física
    state.angulo += state.giro_actual * DT
    state.velocidad += state.aceleracion_actual * DT
    state.velocidad = max(-5.0, min(state.velocidad, 15.0))
    distancia_recorrida = state.velocidad * DT
    state.pos_x += math.cos(state.angulo) * distancia_recorrida
    state.pos_y += math.sin(state.angulo) * distancia_recorrida

    # 2. Publicar mensajes
    mensaje_estado = EstadoVehiculo(
        pos_x=state.pos_x, pos_y=state.pos_y, angulo=state.angulo, velocidad=state.velocidad
    )
    mensaje_conos = PosicionConos(
        conos_interiores=state.posicion_conos.conos_interiores,
        conos_exteriores=state.posicion_conos.conos_exteriores
    )
    await publish("estado.vehiculo", mensaje_estado)
    await publish("mundo.conos", mensaje_conos)

# --- Arranque del Programa ---
if __name__ == "__main__":
    print("Iniciando simulador...")
    asyncio.run(start())