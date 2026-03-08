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
    
    # 3. game loop principal (bucle de tiempo real)
    while True:
        tiempo_actual = time.time()
        
        # diccionarios de intenciones por defecto
        # asumimos reposo absoluto al inicio de cada milisegundo
        movimientos = {ent.tipo: (0, 0) for ent in lista_entidades}
        acciones = {ent.tipo: False for ent in lista_entidades}
        
        # --- captura de eventos ---
        if keyboard.is_pressed('esc'):
            print("\nApagando motores...")
            break
            
        # controles humano 1 (wasd + espacio)
        if keyboard.is_pressed('w'): movimientos['humano1'] = (0, -1)
        elif keyboard.is_pressed('s'): movimientos['humano1'] = (0, 1)
        elif keyboard.is_pressed('a'): movimientos['humano1'] = (-1, 0)
        elif keyboard.is_pressed('d'): movimientos['humano1'] = (1, 0)
        if keyboard.is_pressed('space'): acciones['humano1'] = True
            
        # controles humano 2 (flechas + enter) - listos para el modo 3
        if keyboard.is_pressed('up'): movimientos['humano2'] = (0, -1)
        elif keyboard.is_pressed('down'): movimientos['humano2'] = (0, 1)
        elif keyboard.is_pressed('left'): movimientos['humano2'] = (-1, 0)
        elif keyboard.is_pressed('right'): movimientos['humano2'] = (1, 0)
        if keyboard.is_pressed('enter'): acciones['humano2'] = True
            
        # logica de la ia
        for entidad in lista_entidades:
            if entidad.tipo == "ia":
                # Le preguntamos al cerebro que quiere hacer
                movimiento, quiere_bomba = ia_bot.procesar_estado_ia(entidad, mi_juego, bombas_activas)
                movimientos[entidad.tipo] = movimiento
                acciones[entidad.tipo] = quiere_bomba
        
        # --- fisica de entidades ---
        for entidad in lista_entidades:
            dx, dy = movimientos.get(entidad.tipo, (0, 0))
            quiere_bomba = acciones.get(entidad.tipo, False)
            
            # resolucion de acciones
            if quiere_bomba:
                entidad.plantar_bomba(tiempo_actual, bombas_activas)
                
            if dx != 0 or dy != 0:
                entidad.intentar_mover(dx, dy, tiempo_actual, mi_juego, bombas_activas)
                
        # --- fisica de bombas y fuego ---
        bombas_sobrevivientes = []
        for b in bombas_activas:
            if b.debe_explotar(tiempo_actual):
                # inyecta el fuego direccional en el tablero
                mi_juego.detonar_bomba(b, tiempo_actual) 
            else:
                bombas_sobrevivientes.append(b)
        
        # actualizacion del vector de explosivos
        bombas_activas = bombas_sobrevivientes
        
        mi_juego.actualizar_fuego(tiempo_actual) # recolector de basura para llamas expiradas
        mi_juego.evaluar_muertes(lista_entidades) # aplica daño letal a entidades interceptadas
        
        # --- renderizado ---
        mi_juego.renderizar_consola(lista_entidades, bombas_activas)
        time.sleep(0.016) # limite de 60 fotogramas por segundo para no saturar cpu

if __name__ == "__main__":
    main()