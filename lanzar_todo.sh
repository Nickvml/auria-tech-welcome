#!/bin/bash

# Esta función se ejecutará cuando pulsemos Ctrl+C
cleanup() {
    echo -e "\n\n🛑 Deteniendo todos los procesos de la simulación..."
    pkill -P $$
    echo "¡Procesos detenidos!"
}

# "Si alguna vez recibes la señal de interrupción (Ctrl+C), ejecuta la función 'cleanup'"
trap cleanup SIGINT

# --- El resto del script es igual ---

echo "Lanzando el ecosistema de simulación completo..."
echo "---------------------------------------------"

echo "Activando entorno virtual..."
source .venv/bin/activate

echo "Iniciando simulador..."
python3 simulador.py &

echo "Iniciando visualizador..."
python3 visualizador.py &

echo "Iniciando conductor autónomo..."
python3 conductor.py &

echo "---------------------------------------------"
echo "✅ ¡Todo en marcha!"
echo "Para detener todos los procesos, presiona Ctrl+C en esta terminal."

wait