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