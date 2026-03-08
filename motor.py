import numpy as np
import os
import sys
from config import *
import algoritmos

# nueva clase ligera para manejar las llamas asincronas
class ParticulaFuego:
    def __init__(self, x: int, y: int, tiempo_actual: float):
        self.x = x
        self.y = y
        self.tiempo_extincion = tiempo_actual + DURACION_FUEGO

    def debe_apagarse(self, tiempo_actual: float) -> bool:
        return tiempo_actual >= self.tiempo_extincion

class Tablero:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.matriz = np.zeros((alto, ancho), dtype=np.int8)
        self.fuegos_activos = [] # lista de particulafuego
        self.construir_acero()
        algoritmos.generar_mapa_bomberman(self.matriz, self.ancho, self.alto)
        
    def construir_acero(self):
        for y in range(self.alto):
            for x in range(self.ancho):
                if (y == 0 or y == self.alto-1) or (x == 0 or x == self.ancho-1):
                    self.matriz[y][x] = MURO_ACERO
                elif (y % 2 == 0 and x % 2 == 0):
                    self.matriz[y][x] = MURO_ACERO

    def es_caminable(self, x: int, y: int, bombas_activas: list) -> bool:
        if x < 0 or x >= self.ancho or y < 0 or y >= self.alto:
            return False
            
        # validar que no hay muros
        if self.matriz[y][x] != VACIO:
            return False
            
        # verificar si hay bomba
        for bomba in bombas_activas:
            if bomba.x == x and bomba.y == y:
                return False 
                
        return True
        
    # logica de explosion direccional
    def detonar_bomba(self, bomba, tiempo_actual: float):
        # 4 direcciones cardinales (dx, dy)
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        # el centro de la bomba siempre estalla
        self.fuegos_activos.append(ParticulaFuego(bomba.x, bomba.y, tiempo_actual))
        
        for dx, dy in direcciones:
            for paso in range(1, bomba.rango + 1):
                nx = bomba.x + (dx * paso)
                ny = bomba.y + (dy * paso)
                
                # si sale del mapa, cortamos esa linea de fuego
                if nx < 0 or nx >= self.ancho or ny < 0 or ny >= self.alto:
                    break
                    
                celda = self.matriz[ny][nx]
                
                if celda == MURO_ACERO:
                    break # el acero frena la explosion inmediatamente
                elif celda == MURO_LADRILLO:
                    # destruimos el ladrillo, ponemos fuego temporal y la linea se frena
                    self.matriz[ny][nx] = VACIO
                    self.fuegos_activos.append(ParticulaFuego(nx, ny, tiempo_actual))
                    break
                elif celda == VACIO:
                    # el fuego avanza tranquilamente
                    self.fuegos_activos.append(ParticulaFuego(nx, ny, tiempo_actual))

    def actualizar_fuego(self, tiempo_actual: float):
        # optimizacion: list comprehension para filtrar las llamas vivas directamente
        self.fuegos_activos = [fuego for fuego in self.fuegos_activos if not fuego.debe_apagarse(tiempo_actual)]

    def evaluar_muertes(self, lista_entidades):
        # evaluacion de impacto letal
        for entidad in lista_entidades:
            if not entidad.vivo:
                continue
            for fuego in self.fuegos_activos:
                if entidad.x == fuego.x and entidad.y == fuego.y:
                    entidad.vivo = False
                    entidad.emoji = "💀" # actualizamos la textura al morir
                    break # optimizacion: si ya murio, no evaluar contra mas llamas

    def renderizar_consola(self, lista_entidades, lista_bombas):
        sys.stdout.write('\033[H') 
        frame_buffer = []
        
        # optimizacion espacial o(1): mapear posiciones antes de recorrer la matriz
        # esto evita usar any() (bucle lineal) en cada una de las 273 celdas
        mapa_entidades = {(e.x, e.y): e for e in lista_entidades}
        coords_fuego = {(f.x, f.y) for f in self.fuegos_activos}
        coords_bomba = {(b.x, b.y) for b in lista_bombas}
        
        for y in range(self.alto):
            fila_temporal = []
            for x in range(self.ancho):
                # control de capas (z-index) usando busqueda o(1)
                pos = (x, y)
                if pos in mapa_entidades:
                    fila_temporal.append(mapa_entidades[pos].emoji)
                elif pos in coords_fuego:
                    fila_temporal.append(DICCIONARIO_SIMBOLOS[FUEGO])
                elif pos in coords_bomba:
                    fila_temporal.append(DICCIONARIO_SIMBOLOS[BOMBA])
                else:
                    codigo_celda = self.matriz[y][x]
                    fila_temporal.append(DICCIONARIO_SIMBOLOS[codigo_celda])
            
            frame_buffer.append("".join(fila_temporal) + "\n")
            
        sys.stdout.write("".join(frame_buffer))
        sys.stdout.flush()