import random
from config import *

def generar_laberinto_dfs(matriz,ancho,alto):
    # rellenar todo el vacio con ladrillos
    for y in range(alto):
        for x in range(ancho):
            if matriz[y][x] == VACIO:
                matriz[y][x] = MURO_LADRILLO
    # DFS para tallar ruta principal
    visitado = set()
    
    def dfs(x,y):
        visitado.add((x,y))
        matriz[y][x] = VACIO 
        
        #direciones, saltos de a 2
        direcciones = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(direcciones) # aleatorizar para variedad de mapas
        
        for dx, dy in direcciones:
            nx = x + dx
            ny = y + dy
            # validar limites
            if 0 < nx < ancho-1 and 0 < ny < alto-1 and (nx, ny) not in visitado:
                # tallar el muro intermedio
                matriz[y + dy//2][x + dx//2] = VACIO
                dfs(nx, ny)
    #iniciar dfs desde player 1
    dfs(1,1)
    
    #dinamitar muros extra
    for y in range(1, alto-1):
        for x in range(1, ancho-1):
            if matriz[y][x] == MURO_LADRILLO and random.random() < 0.4:
                matriz[y][x] = VACIO
    
    #despejar zonas de spawn
    zonas_seguras = [(1,1), (1,2), (2,1), (ancho-2, alto-2), (ancho-3, alto-2), (ancho-2, alto-3)]
    for zx, zy in zonas_seguras:
        matriz[zy][zx] = VACIO