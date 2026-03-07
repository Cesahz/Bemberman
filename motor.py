import numpy as np
import os
import sys
from config import *

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
        self.fuegos_activos = [] # lista de ParticulaFuego
        self.construir_acero()
        
    def construir_acero(self):
        for y in range(self.alto):
            for x in range(self.ancho):
                if (y == 0 or y == self.alto-1) or (x == 0 or x == self.ancho-1):
                    self.matriz[y][x] = MURO_ACERO
                elif (y % 2 == 0 and x % 2 == 0):
                    self.matriz[y][x] = MURO_ACERO

    def es_caminable(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.ancho or y < 0 or y >= self.alto:
            return False
        return self.matriz[y][x] == VACIO
        
    # LOGICA DE EXPLOSION (Direccional)
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
        # limpiamos las llamas que ya se consumieron
        fuegos_vivos = []
        for fuego in self.fuegos_activos:
            if not fuego.debe_apagarse(tiempo_actual):
                fuegos_vivos.append(fuego)
        self.fuegos_activos = fuegos_vivos

    def evaluar_muertes(self, lista_entidades):
        # evaluacion de impacto: si estas sobre el fuego, mueres.
        for entidad in lista_entidades:
            if not entidad.vivo:
                continue
            for fuego in self.fuegos_activos:
                if entidad.x == fuego.x and entidad.y == fuego.y:
                    entidad.vivo = False
                    entidad.emoji = "💀" # actualizamos la textura al morir

    def renderizar_consola(self, lista_entidades, lista_bombas):
        sys.stdout.write('\033[H') 
        frame_buffer = []
        
        for y in range(self.alto):
            fila_temporal = []
            for x in range(self.ancho):
                
                # control de capas (Z-Index): Entidad > Fuego > Bomba > Mapa Base
                entidad_aqui = None
                for e in lista_entidades:
                    if e.x == x and e.y == y:
                        entidad_aqui = e
                        break # evitamos iterar de mas si ya encontramos una
                        
                fuego_aqui = any(f.x == x and f.y == y for f in self.fuegos_activos)
                bomba_aqui = any(b.x == x and b.y == y for b in lista_bombas)
                
                if entidad_aqui:
                    fila_temporal.append(entidad_aqui.emoji)
                elif fuego_aqui:
                    fila_temporal.append(DICCIONARIO_SIMBOLOS[FUEGO])
                elif bomba_aqui:
                    fila_temporal.append(DICCIONARIO_SIMBOLOS[BOMBA])
                else:
                    codigo_celda = self.matriz[y][x]
                    fila_temporal.append(DICCIONARIO_SIMBOLOS[codigo_celda])
            
            frame_buffer.append("".join(fila_temporal) + "\n")
            
        sys.stdout.write("".join(frame_buffer))
        sys.stdout.flush()