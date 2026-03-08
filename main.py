import time
import keyboard
import os
import sys
from config import *
import entidades
import motor
import ia_bot

def inicializar_entorno():
    # prepara la terminal segun el sistema operativo
    if os.name == 'nt':
        os.system('')
    os.system('cls' if os.name == 'nt' else 'clear')

def menu_modos():
    print("=== MOTOR MAHORAGA: COLAPSO DE DOMINIO ===")
    print("1. Jugador vs IA")
    print("2. IA vs IA")
    print("3. Jugador vs Jugador (PvP Experimental)")
    modo = input("Elige un modo operativo (1-3): ")
    return modo

def main():
    inicializar_entorno()
    modo = menu_modos()
    
    # 1. instancias base del ecosistema
    mi_juego = motor.Tablero(ANCHO, ALTO)
    lista_entidades = []
    
    # 2. arquitectura de modos y poblacion del mapa
    if modo == '1':
        lista_entidades.append(entidades.Entidad(1, 1, "🐱", COOLDOWN_MOVIMIENTO, "humano1"))
        lista_entidades.append(entidades.Entidad(ANCHO-2, ALTO-2, "🤖", COOLDOWN_MOVIMIENTO, "ia"))
    elif modo == '2':
        lista_entidades.append(entidades.Entidad(1, 1, "👾", COOLDOWN_MOVIMIENTO, "ia"))
        lista_entidades.append(entidades.Entidad(ANCHO-2, ALTO-2, "🤖", COOLDOWN_MOVIMIENTO, "ia"))
    elif modo == '3':
        lista_entidades.append(entidades.Entidad(1, 1, "🐱", COOLDOWN_MOVIMIENTO, "humano1"))
        # el jugador 2 usa otra etiqueta para separar sus controles de entrada
        lista_entidades.append(entidades.Entidad(ANCHO-2, ALTO-2, "🦊", COOLDOWN_MOVIMIENTO, "humano2")) 
    else:
        print("Modo no reconocido. Cerrando protocolo.")
        sys.exit()

    bombas_activas = []
    inicializar_entorno() # limpiamos el texto del menu inicial
    
    #game loop principal (bucle de tiempo real)
    while True:
        tiempo_actual = time.time()
        movimientos = {ent: (0, 0) for ent in lista_entidades}
        acciones = {ent: False for ent in lista_entidades}
        
        # --- captura de eventos ---
        if keyboard.is_pressed('esc'):
            print("\nApagando motores...")
            break
            
        # para asignar controles humanos, buscamos quienes son en la lista
        for entidad in lista_entidades:
            if entidad.tipo == "humano1":
                if keyboard.is_pressed('w'): movimientos[entidad] = (0, -1)
                elif keyboard.is_pressed('s'): movimientos[entidad] = (0, 1)
                elif keyboard.is_pressed('a'): movimientos[entidad] = (-1, 0)
                elif keyboard.is_pressed('d'): movimientos[entidad] = (1, 0)
                if keyboard.is_pressed('space'): acciones[entidad] = True
                
            elif entidad.tipo == "humano2":
                if keyboard.is_pressed('up'): movimientos[entidad] = (0, -1)
                elif keyboard.is_pressed('down'): movimientos[entidad] = (0, 1)
                elif keyboard.is_pressed('left'): movimientos[entidad] = (-1, 0)
                elif keyboard.is_pressed('right'): movimientos[entidad] = (1, 0)
                if keyboard.is_pressed('enter'): acciones[entidad] = True
                
            elif entidad.tipo == "ia":
                movimiento, quiere_bomba = ia_bot.procesar_estado_ia(entidad, mi_juego, bombas_activas)
                movimientos[entidad] = movimiento
                acciones[entidad] = quiere_bomba
        
        # --- fisica de entidades ---
        for entidad in lista_entidades:
            dx, dy = movimientos.get(entidad, (0, 0))
            quiere_bomba = acciones.get(entidad, False)
            
            if quiere_bomba:
                entidad.plantar_bomba(tiempo_actual, bombas_activas)
                
            if dx != 0 or dy != 0:
                entidad.intentar_mover(dx, dy, tiempo_actual, mi_juego, bombas_activas)
                
        # --- fisica de bombas y fuego ---
        bombas_sobrevivientes = []
        for b in bombas_activas:
            if b.debe_explotar(tiempo_actual):
                mi_juego.detonar_bomba(b, tiempo_actual) 
            else:
                bombas_sobrevivientes.append(b)
        
        bombas_activas = bombas_sobrevivientes
        mi_juego.actualizar_fuego(tiempo_actual) 
        mi_juego.evaluar_muertes(lista_entidades) 
        
        # --- renderizado ---
        mi_juego.renderizar_consola(lista_entidades, bombas_activas)
        time.sleep(0.016)

if __name__ == "__main__":
    main()