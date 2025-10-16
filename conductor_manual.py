import asyncio
from pynput import keyboard

from mensajes import ControlVehiculo
# ¡Importamos timer y start!
from starting_pack import publish, start, timer

# --- Estado del Conductor ---
# Guardaremos aquí el estado actual de los controles.
controles = ControlVehiculo(aceleracion=0.0, giro=0.0)

# --- Bucle de Publicación con @timer ---
# Esta es la forma correcta: el @timer se asegura de que esto
# solo empiece a ejecutarse DESPUÉS de que start() haya conectado.
@timer(1/30)
async def publicar_controles_timer():
    """Publica el estado actual de los controles 30 veces por segundo."""
    await publish("controles.vehiculo", controles)

# --- Lógica de Pulsación de Teclas (sin cambios) ---
def on_press(key):
    """Se activa cuando se presiona una tecla."""
    try:
        if key == keyboard.Key.up:
            controles.aceleracion = 2.5
        elif key == keyboard.Key.down:
            controles.aceleracion = -2.0
        elif key == keyboard.Key.left:
            controles.giro = -1.5  # Aumentamos la velocidad de giro
        elif key == keyboard.Key.right:
            controles.giro = 1.5   # Aumentamos la velocidad de giro
    except AttributeError:
        pass

def on_release(key):
    """Se activa cuando se suelta una tecla."""
    try:
        if key in [keyboard.Key.up, keyboard.Key.down]:
            controles.aceleracion = 0.0
        elif key in [keyboard.Key.left, keyboard.Key.right]:
            controles.giro = 0.0
        if key == keyboard.Key.esc:
            return False
    except AttributeError:
        pass

# --- Arranque del Programa (más simple y correcto) ---
if __name__ == "__main__":
    # Inicia el listener del teclado en un hilo separado.
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    print("Conductor manual iniciado. Usa las flechas para mover el coche.")
    print("Haz clic en la ventana del gráfico para que detecte las teclas.")
    print("Pulsa 'Esc' en la ventana de esta terminal para salir.")
    
    # Arrancamos el sistema. start() se encargará de ejecutar el @timer por nosotros.
    asyncio.run(start())