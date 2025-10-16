# Simulador de Vehículo Autónomo para Auria Technologies

Este proyecto es una simulación de un vehículo autónomo desarrollado como parte del proceso de selección de Auria Technologies. El sistema utiliza una arquitectura de productor/suscriptor con NATS y `msgspec` para la comunicación en tiempo real entre sus componentes modulares.

## Características Principales

* **Conducción Autónoma por Waypoints:** El conductor calcula una línea de carrera óptima y utiliza un algoritmo con memoria para seguirla, ajustando dinámicamente su velocidad en las curvas.
* **Visualizador Interactivo:** La simulación se muestra en una ventana gráfica con una cámara que sigue al vehículo y permite hacer zoom con la rueda del ratón.
* **Control Manual Opcional:** Incluye un script separado para controlar el vehículo manualmente con las flechas del teclado, ideal para pruebas.
* **Sistema Modular:** Los tres componentes (`simulador`, `conductor`, `visualizador`) son programas independientes que se comunican a través de una red de mensajería, demostrando una arquitectura robusta.

## Requisitos Previos

Para ejecutar este proyecto, necesitas tener instalado:

* Python 3.10 o superior
* Docker
* Git

## Instalación

Sigue estos pasos para configurar el entorno de trabajo:

1.  **Clona el repositorio:**
    ```bash
    # ¡IMPORTANTE! Asegúrate de que esta es la URL correcta de tu repositorio
    git clone [https://github.com/Nickvml/auria-t# auria-tech-wel# Simulador de Vehículo Autónomo para Auria Technologies

Este proyecto es una simulación de un vehículo autónomo desarrollado como parte del proceso de selección de Auria Technologies. El sistema utiliza una arquitectura de productor/suscriptor con NATS y `msgspec` para la comunicación entre los diferentes componentes.

## Componentes

El ecosistema consta de tres programas principales que se ejecutan de forma concurrente:

* **`simulador.py`**: El corazón de la simulación. Gestiona la física del vehículo y el estado del circuito (posición de los conos).
* **`conductor.py`**: El cerebro del vehículo. Recibe datos del simulador y utiliza un algoritmo de seguimiento de waypoints para calcular y enviar los comandos de control (aceleración y giro).
* **`visualizador.py`**: Los ojos del sistema. Se suscribe a los datos del simulador y muestra el estado del circuito y el vehículo en un gráfico en tiempo real.

## Requisitos Previos

Para ejecutar este proyecto, necesitas tener instalado:

* Python 3.10 o superior
* Docker y Docker Compose
* Git

## Instalación

Sigue estos pasos para configurar el entorno de trabajo:

1.  **Clona el repositorio:**
    ```bash
    # ¡IMPORTANTE! Reemplaza esta URL por la de tu propio repositorio
    git clone [https://github.com/Nickvml/auria-tech-welcome.git](https://github.comz/Nickvml/auria-tech-welcome.git)
    ```

2.  **Navega a la carpeta del proyecto:**
    ```bash
    cd auria-tech-welcome
    ```

3.  **Crea y activa el entorno virtual de Python:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Uso

El sistema requiere dos terminales para funcionar: una para el servidor de comunicaciones y otra para la simulación.

1.  **En una primera terminal**, inicia el servidor NATS. Este debe permanecer en ejecución:
    ```bash
    bash nats_server.sh
    ```

2.  **En una segunda terminal**, utiliza el script de lanzamiento para iniciar todos los componentes de la simulación a la vez:
    ```bash
    ./lanzar_todo.sh
    ```

Aparecerá una ventana mostrando la simulación. Para detener todos los procesos, simplemente cierra la segunda terminal o presiona `Ctrl+C` en ella. comeech-welcome.git](https://github.com/Nickvml/auria-tech-welcome.git)
    ```

2.  **Navega a la carpeta del proyecto:**
    ```bash
    cd auria-tech-welcome
    ```

3.  **Crea y activa el entorno virtual de Python:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Uso

El sistema requiere dos terminales para funcionar: una para el servidor de comunicaciones y otra para la simulación.

#### 1. Iniciar el Servidor NATS

En una **primera terminal**, inicia el servidor NATS. Este debe permanecer en ejecución durante toda la simulación.

```bash
bash nats_server.sh