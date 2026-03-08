import algoritmos
from collections import deque
from config import MURO_LADRILLO

def bfs_escape(inicio_x, inicio_y, tablero, zonas_peligro, bombas_activas):
    #cola de tuplas
    cola = deque([(inicio_x, inicio_y, [])])
    visitados = set([(inicio_x, inicio_y)])
    
    while cola:
        cx, cy, camino = cola.popleft()
        
        #condicion de victoria es encontrar una zona segura
        if (cx, cy) not in zonas_peligro:
            if len(camino) > 0:
                return camino[0]
            return (0, 0)
        #expansion de vecinos
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            #no pasar por las bombas
            if tablero.es_caminable(nx, ny, bombas_activas) and (nx, ny) not in visitados:
                    visitados.add((nx, ny))
                    cola.append((nx, ny, camino + [(dx, dy)]))
            #evaluar solo los caminables y no visitados
            if tablero.es_caminable(nx, ny,bombas_activas) and (nx, ny) not in visitados:
                visitados.add((nx, ny))
                #guardamos la ruta historial agregando el nuevo paso
                cola.append((nx, ny, camino + [(dx, dy)]))
                
    return (0, 0) # si no hay escape, quedarse quieto


def bfs_buscar_ladrillo(inicio_x,inicio_y,tablero,bombas_activas):
    #buscar casillas vacia mas cercana con muros rompibles adyacentes
    cola = deque([(inicio_x,inicio_y,[])])
    visitado = set([(inicio_x,inicio_y)])
    direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    while cola:
        cx, cy, camino = cola.popleft()
        #buscar muros rompibles alado
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            #validar limites
            if 0 <= nx < tablero.ancho and 0 <= ny < tablero.alto:
                if tablero.matriz[ny][nx] == MURO_LADRILLO:
                    #encontrar muro adyacente
                    if len(camino) > 0:
                        return camino[0] #primer paso hacia el objetivo
                    else:
                        #si el camino es 0 es porque estamos alao de un ladrillo
                        return (0,0)
        #expansion, si no hay ladrillos seguimos buscando
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            if tablero.es_caminable(nx, ny, bombas_activas) and (nx, ny) not in visitado:
                visitado.add((nx,ny))
                cola.append((nx, ny, camino + [(dx, dy)]))
    return (0, 0) # si no hay ladrillos en el mapa 


def procesar_estado_ia(ia_entidad,tablero,bombas_activas):
    #maquina de estados. retorna tupla y si quiere poner bomba
    if not ia_entidad.vivo:
        return (0, 0), False
    #percepcion del entorno
    zonas_peligro = algoritmos.obtener_mapa_peligro(tablero, bombas_activas)
    
    #estado 1: supervivencia (prioridad)
    if (ia_entidad.x, ia_entidad.y) in zonas_peligro:
        #apagar todo, ejecutar evasion
        movimiento_salvavidas = bfs_escape(ia_entidad.x, ia_entidad.y, tablero, zonas_peligro,bombas_activas)
        return movimiento_salvavidas, False
    
    #estado 2: granjero (destruccion y expansion)
    movimiento_granjero = bfs_buscar_ladrillo(ia_entidad.x,ia_entidad.y,tablero,bombas_activas)
    #si retorna (0,0) significa que ya estamos en un muro
    if movimiento_granjero == (0,0):
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        ladrillo_cerca = False
        for dx,dy in direcciones:
            if tablero.matriz[ia_entidad.y + dy][ia_entidad.x + dx] == MURO_LADRILLO:
                ladrillo_cerca = True
                break
        if ladrillo_cerca:
            return (0,0), True #soltar bomba
    
    if movimiento_granjero != (0,0):
        return movimiento_granjero,False
    
    #temporal
    return (0, 0), False