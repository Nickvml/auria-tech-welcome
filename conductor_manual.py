import asyncio
from pynput import keyboard

from mensajes import ControlVehiculo, ComandoSimulador
from starting_pack import publish, start, timer

# --- Estado del Conductor ---
controles = ControlVehiculo(aceleracion=0.0, giro=0.0)
reset_solicitado = False
# --- Bucle de Publicación con @timer ---
@timer(1/30)
async def bucle_principal_conductor():
    """Bucle principal que publica controles y gestiona comandos."""
    global reset_solicitado
    # Publicamos el estado normal de los controles.
    await publish("controles.vehiculo", controles)

    # Si el hilo del teclado ha solicitado un reseteo...
    if reset_solicitado:
        print("Enviando comando de reseteo...")
        await publish("simulador.comando", ComandoSimulador(comando="reset_posicion"))
        reset_solicitado = False # Apagamos la bandera para no enviarlo más veces.
        
# --- Lógica de Pulsación de Teclas (sin cambios) ---
def on_press(key):
    """Se activa cuando se presiona una tecla."""
    global reset_solicitado
    try:
        # Primero comprobamos si es una tecla de caracter, como 'r'
        if key.char == 'r':
            reset_solicitado = True
    except AttributeError:
        # Si da error, es una tecla especial (como las flechas)
        try:
            if key == keyboard.Key.up:
                controles.aceleracion = 2.5
            elif key == keyboard.Key.down:
                controles.aceleracion = -2.0
            elif key == keyboard.Key.left:
                controles.giro = -1.5
            elif key == keyboard.Key.right:
                controles.giro = 1.5
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