import algoritmos
from collections import deque

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
            if tablero.es_caminable(nx, ny) and (nx, ny) not in visitados:
                visitados.add((nx, ny))
                #guardamos la ruta historial agregando el nuevo paso
                cola.append((nx, ny, camino + [(dx, dy)]))
                
    return (0, 0) # si no hay escape, quedarse quieto

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
    #temporal hasta tener mas estados
    return (0, 0), False