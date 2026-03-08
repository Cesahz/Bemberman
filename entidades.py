import time
from config import *

class Bomba:
    # constructor de la amenaza
    def __init__(self, x: int, y: int, rango: int, tiempo_actual: float, propietario):
        self.x = x
        self.y = y
        self.rango = rango
        self.tiempo_detonacion = tiempo_actual + TIEMPO_EXPLOSION_BOMBA
        self.propietario = propietario # guardamos quien la puso para futuras metricas

    # evalua si la mecha se consumio
    def debe_explotar(self, tiempo_actual: float) -> bool:
        return tiempo_actual >= self.tiempo_detonacion

class Entidad:
    def __init__(self, x_inicial: int, y_inicial: int, emoji_visual: str, cooldown_segundos: float, tipo: str):
        self.x = x_inicial
        self.y = y_inicial
        self.emoji = emoji_visual
        self.cooldown = cooldown_segundos
        self.ultimo_movimiento = 0.0
        self.vivo = True
        self.tipo = tipo
        self.max_bombas = 1

    def intentar_mover(self, delta_x: int, delta_y: int, tiempo_actual_pc: float, tablero_juego, lista_bombas_activas: list) -> bool:
        # los muertos no caminan
        if not self.vivo:
            return False
            
        # escudo de cooldown (rendimiento e igualdad)
        if (tiempo_actual_pc - self.ultimo_movimiento) < self.cooldown:
            return False
            
        futuro_x = self.x + delta_x
        futuro_y = self.y + delta_y
        
        # pasar la bomba al validador
        if tablero_juego.es_caminable(futuro_x, futuro_y, lista_bombas_activas):
            self.x = futuro_x
            self.y = futuro_y
            self.ultimo_movimiento = tiempo_actual_pc
            return True
        
        # consulta de colision
        if tablero_juego.es_caminable(futuro_x, futuro_y):
            self.x = futuro_x
            self.y = futuro_y
            self.ultimo_movimiento = tiempo_actual_pc
            return True
        return False

    def plantar_bomba(self, tiempo_actual: float, lista_bombas_activas: list):
        if not self.vivo:
            return
        # validar cantidad de bombas
        bombas_propias = [b for b in lista_bombas_activas if b.propietario == self]
        if len(bombas_propias) >= self.max_bombas:
            return
        
        # no apilar bombas en la misma celda
        for bomba in lista_bombas_activas:
            if bomba.x == self.x and bomba.y == self.y:
                return # abortar
                
        # instanciar y agregar al ecosistema
        nueva_bomba = Bomba(self.x, self.y, RANGO_BOMBA_INICIAL, tiempo_actual, self)
        lista_bombas_activas.append(nueva_bomba)