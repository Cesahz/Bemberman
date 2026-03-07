import numpy as np # el estandar para calculo matricial
import os # para la limpieza de la terminal
from config import * # trae las constantes del adn del juego
import sys # control de buffer de salida estandar

class Tablero:
    def __init__(self,ancho,alto):
        self.ancho = ancho
        self.alto = alto
        # inicializar matriz con ceros
        self.matriz = np.zeros((alto,ancho), dtype=np.int8)
        self.construir_acero()
        
    # metodo para construir acero en el tablero
    def construir_acero(self):
        for y in range(self.alto):
            for x in range(self.ancho):
                # en los bordes y en casillas pares
                if (y == 0 or y == self.alto-1) or (x == 0 or x == self.ancho-1):
                    self.matriz[y][x] = MURO_ACERO
                elif (y % 2 == 0 and x % 2 == 0):
                    self.matriz[y][x] = MURO_ACERO

    # verifica si una coordenada es transitable
    def es_caminable(self,x:int,y:int) -> bool:
        # evaluar limites de la matriz para evitar desbordamiento
        if x < 0 or x >= self.ancho or y < 0 or y >= self.alto:
            return False
        
        # retornar la evaluacion booleana directa
        return self.matriz[y][x] == VACIO
         
    # metodo para renderizar la consola sin parpadeo
    def renderizar_consola(self,jugador_principal):
        # mover cursor al origen (ansi escape code)
        sys.stdout.write('\033[H') 
        
        # usar lista para el buffer maestro
        frame_buffer = []
        
        for y in range(self.alto):
            # lista temporal para la fila actual
            fila_temporal = []
            for x in range(self.ancho):
                # superponer entidad si coincide la coordenada
                if jugador_principal.x == x and jugador_principal.y == y:
                    fila_temporal.append(jugador_principal.emoji)
                else:
                    codigo_celda = self.matriz[y][x]
                    fila_temporal.append(DICCIONARIO_SIMBOLOS[codigo_celda])
            
            # ensamblar la fila y agregar salto de linea
            frame_buffer.append("".join(fila_temporal) + "\n")
            
        # inyectar el fotograma completo en la terminal
        sys.stdout.write("".join(frame_buffer))
        sys.stdout.flush()