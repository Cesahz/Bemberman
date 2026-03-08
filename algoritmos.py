import random
from config import *

def generar_mapa_bomberman(matriz, ancho, alto):
    # rellenar con probabilidad
    for y in range(alto):
        for x in range(ancho):
            if matriz[y][x] == VACIO:
                if random.random() < 0.75:
                    matriz[y][x] = MURO_LADRILLO

    # despejar zonas de inicio para los jugadores
    zonas_seguras = [
        #esquina superior izquierda
        (1, 1), (2, 1), (1, 2),
        #esquina inferior derecha
        (ancho-2, alto-2), (ancho-3, alto-2), (ancho-2, alto-3),
        #esquina superior derecha
        (ancho-2, 1), (ancho-3, 1), (ancho-2, 2),
        #esquina inferior izquierda
        (1, alto-2), (2, alto-2), (1, alto-3)
    ]
    
    for zx, zy in zonas_seguras:
        matriz[zy][zx] = VACIO

def obtener_mapa_peligro(tablero, bombas_activas):
    peligro = set()
    
    # el fuego actual es muerte inmediata
    for fuego in tablero.fuegos_activos:
        peligro.add((fuego.x, fuego.y))
        
    for bomba in bombas_activas:
        peligro.add((bomba.x, bomba.y)) # el centro de la bomba es peligroso
        # 4 direcciones
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in direcciones:
            for paso in range(1, bomba.rango + 1):
                nx = bomba.x + (dx * paso)
                ny = bomba.y + (dy * paso)
                
                #si sale del mapa se corta 
                if nx < 0 or nx >= tablero.ancho or ny < 0 or ny >= tablero.alto:
                    break
                
                celda = tablero.matriz[ny][nx]
                if celda == MURO_ACERO:
                    break
                peligro.add((nx, ny)) #zona de muerte
                
                if celda == MURO_LADRILLO:
                    break # absorbe la explosion jeje
    return peligro