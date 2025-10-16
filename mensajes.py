from msgspec import Struct
from typing import List, Tuple

# --- Mensajes de Control ---
# Enviado por el conductor para mover el vehículo.
class ControlVehiculo(Struct):
    aceleracion: float  # Valor positivo para acelerar, negativo para frenar/reversa.
    giro: float         # Valor positivo para girar a la derecha, negativo a la izquierda.

# --- Mensajes de Estado del Mundo ---
# Publicado por el simulador para describir dónde están las cosas.

class EstadoVehiculo(Struct):
    pos_x: float
    pos_y: float
    angulo: float       # En radianes, 0 es apuntando a la derecha.
    velocidad: float

# Usamos una tupla de dos floats para representar las coordenadas (x, y) de un cono.
# El mensaje contendrá una lista de todas estas tuplas.
class PosicionConos(Struct, frozen=True):
    conos: List[Tuple[float, float]]