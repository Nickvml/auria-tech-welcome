import asyncio
import math
from msgspec import Struct

# Importamos las definiciones de mensajes que creamos en la Fase 1
from mensajes import ControlVehiculo, EstadoVehiculo, PosicionConos

# Importamos las herramientas que nos dieron en el starting_pack
from starting_pack import subscribe, timer, publish, start

# --- Estado del Simulador ---
# Esta clase guardará toda la información de nuestro mundo.
class SimuladorState(Struct):
    # Estado del vehículo
    pos_x: float = 0.0
    pos_y: float = 0.0
    angulo: float = 0.0  # Apuntando a la derecha (eje X positivo)
    velocidad: float = 0.0

    # Últimos controles recibidos del conductor autónomo
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
@subscribe("controles.vehiculo", ControlVehiculo)
async def on_control_recibido(msg: ControlVehiculo):
    """
    Callback que se activa al recibir un mensaje de control.
    Actualiza el estado del simulador con los últimos valores de aceleración y giro.
    """
    state.aceleracion_actual = msg.aceleracion
    state.giro_actual = msg.giro
# (Aquí añadiremos las funciones de @subscribe y @timer en los siguientes pasos)


# --- Arranque del Programa ---
# Esta es la parte estándar para iniciar el programa.
if __name__ == "__main__":
    print("Iniciando simulador...")
    asyncio.run(start())