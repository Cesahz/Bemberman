import time
import keyboard
import os
from config import *
import entidades
import motor

def inicializar_entorno():
    if os.name == 'nt':
        os.system('')
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    inicializar_entorno()
    mi_juego = motor.Tablero(ANCHO,ALTO)
    gato_jugador = entidades.Entidad(1,1,"😺",COOLDOWN_MOVIMIENTO)
    while True:
        tiempo_actual = time.time()
        dx = 0
        dy = 0
        if keyboard.is_pressed('w'):
            dy = -1
        elif keyboard.is_pressed('s'):
            dy = 1
        elif keyboard.is_pressed('a'):
            dx = -1
        elif keyboard.is_pressed('d'):
            dx = 1
        elif keyboard.is_pressed('esc'):
            print("Saliendo del juego...")
            break
        if dx != 0 or dy != 0:
            gato_jugador.intentar_mover(dx,dy,tiempo_actual,mi_juego)
        mi_juego.renderizar_consola(gato_jugador)
        time.sleep(0.016)
if __name__ == "__main__":
    main()