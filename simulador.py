import asyncio
import math
from msgspec import Struct

from mensajes import ControlVehiculo, EstadoVehiculo, PosicionConos, ComandoSimulador
from starting_pack import subscribe, timer, publish, start

# --- Estado del Simulador ---
# Esta clase guardará toda la información de nuestro mundo.
class SimuladorState(Struct):
    # Estado del vehículo
    pos_x: float = 0.0
    pos_y: float = 0.0
    angulo: float = 0.0  # Apuntando a la derecha (eje X positivo)
    velocidad: float = 0.0

    # Últimos controles recibidos del conductor autónomorom mensajes import ControlVehiculo, EstadoVehiculo, PosicionConos, ComandoSimulador

    aceleracion_actual: float = 0.0
    giro_actual: float = 0.0

    # El circuito: una lista de coordenadas (x, y) de los conos
    # Vamos a crear un circuito simple con forma de rectángulo.
    # Puedes cambiar estos valores para crear tu propio circuito!
    # Cámbialo por ESTO:
    posicion_conos: PosicionConos = PosicionConos(
    # Borde interior de la pista
    conos_interiores=[
        (20, 20), (50, 20), (70, 30), (70, 50), (50, 60), (20, 60), (10, 50), (10, 30),
    ],
    # Borde exterior de la pista
    conos_exteriores=[
        (20, 10), (50, 10), (80, 30), (80, 50), (50, 70), (20, 70), (0, 50), (0, 30),
    ]
)
# Creamos una instancia única de nuestro estado que usaremos en todo el programa.
state = SimuladorState()


# --- Lógica del Simulador ---

# Esta función se ejecutará cada vez que llegue un mensaje al topic "controles.vehiculo"
# Oyente 1: Escucha los controles de movimiento del vehículo
@subscribe("controles.vehiculo", ControlVehiculo)
async def on_control_recibido(msg: ControlVehiculo):
    """
    Callback que se activa al recibir un mensaje de control.
    Actualiza el estado del simulador con los últimos valores de aceleración y giro.
    """
    state.aceleracion_actual = msg.aceleracion
    state.giro_actual = msg.giro

# Oyente 2: Escucha comandos especiales como el de reseteo
@subscribe("simulador.comando", ComandoSimulador)
async def on_comando_recibido(msg: ComandoSimulador):
    """Escucha comandos especiales para el simulador."""
    if msg.comando == "reset_posicion":
        print("¡Reseteando posición del vehículo!")
        state.pos_x = 0.0
        state.pos_y = 0.0
        state.angulo = 0.0
        state.velocidad = 0.0
    """
    Callback que se activa al recibir un mensaje de control.
    Actualiza el estado del simulador con los últimos valores de aceleración y giro.
    """
    state.aceleracion_actual = msg.aceleracion
    state.giro_actual = msg.giro
# Constantes de la simulación
DT = 1 / 60  # Delta de tiempo: simulamos a 60 "frames" por segundo.
# Esta función se ejecutará 60 veces por segundo. Es el motor de nuestra simulación.

@timer(DT)
async def bucle_principal():
    """
    Realiza un paso de la simulación física y publica el estado del mundo.
    """
    # 1. Actualizar el ángulo del vehículo
    cambio_de_angulo = state.giro_actual * DT
    state.angulo += cambio_de_angulo

    # 2. Actualizar la velocidad
    state.velocidad += state.aceleracion_actual * DT
    state.velocidad = max(-5.0, min(state.velocidad, 15.0)) 

    # 3. Actualizar la posición (X, Y)
    distancia_recorrida = state.velocidad * DT
    state.pos_x += math.cos(state.angulo) * distancia_recorrida
    state.pos_y += math.sin(state.angulo) * distancia_recorrida

    # 4. Crear los mensajes con el estado actualizado del mundo
    mensaje_estado_vehiculo = EstadoVehiculo(
        pos_x=state.pos_x,
        pos_y=state.pos_y,
        angulo=state.angulo,
        velocidad=state.velocidad,
    )
    
    # ***** ESTA ES LA PARTE QUE CAMBIAMOS *****
    # Ahora creamos el mensaje usando la nueva estructura con dos listas de conos.
    mensaje_posicion_conos = PosicionConos(
        conos_interiores=state.posicion_conos.conos_interiores,
        conos_exteriores=state.posicion_conos.conos_exteriores
    )

    # 5. Publicar los mensajes en sus topics
    await publish("estado.vehiculo", mensaje_estado_vehiculo)
    await publish("mundo.conos", mensaje_posicion_conos)

# --- Arranque del Programa ---
# Esta es la parte estándar para iniciar el programa.
if __name__ == "__main__":
    print("Iniciando simulador...")
    asyncio.run(start())