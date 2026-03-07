from config import *
import motor
def main():
    mi_juego = motor.Tablero(ANCHO, ALTO)
    mi_juego.renderizar_consola()
main()