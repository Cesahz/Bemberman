import numpy as np # el estandar para calculo matricial
import os # para la limpieza de la terminal
from config import * # trae las constantes del adn del juego

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
                    
    # metodo para renderizar la consola
    def renderizar_consola(self):
        os.system('cls' if os.name == 'nt' else 'clear') # limpiar la terminal
        
        for fila in self.matriz:
            texto_fila = "".join(DICCIONARIO_SIMBOLOS[celda] for celda in fila)
            print(texto_fila)