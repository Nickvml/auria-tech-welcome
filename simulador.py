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
    posicion_conos: PosicionConos = PosicionConos(
        conos=[
            (10, 5), (30, 5),   # Lado inferior
            (10, 15), (30, 15), # Lado superior
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
    # El giro afecta más a velocidades altas. La velocidad angular es giro * velocidad.
    cambio_de_angulo = state.giro_actual * state.velocidad * DT
    state.angulo += cambio_de_angulo

    # 2. Actualizar la velocidad
    # Usamos una fórmula de movimiento simple: v_final = v_inicial + a * t
    state.velocidad += state.aceleracion_actual * DT
    # Ponemos un límite para que no vaya marcha atrás a más de cierta velocidad
    state.velocidad = max(-5.0, min(state.velocidad, 15.0))
    # 3. Actualizar la posición (X, Y)
    # Usamos trigonometría básica para mover el coche en la dirección de su ángulo.
    # distancia = velocidad * tiempo
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
    
    # La posición de los conos no cambia, pero la publicamos periódicamente
    # por si un nuevo programa (como el visualizador) se conecta a mitad de la simulación.
    mensaje_posicion_conos = state.posicion_conos

    # 5. Publicar los mensajes en sus topics
    await publish("estado.vehiculo", mensaje_estado_vehiculo)
    await publish("mundo.conos", mensaje_posicion_conos)

# --- Arranque del Programa ---
# Esta es la parte estándar para iniciar el programa.
if __name__ == "__main__":
    print("Iniciando simulador...")
    asyncio.run(start())