import algoritmos
from collections import deque
from config import MURO_LADRILLO, RANGO_BOMBA_INICIAL
import entidades

# recibe lista_entidades para evitar colisiones dinamicas
def bfs_escape(inicio_x, inicio_y, tablero, zonas_peligro, bombas_activas, lista_entidades):
    cola = deque([(inicio_x, inicio_y, [])])
    visitados = set([(inicio_x, inicio_y)])
    fuegos = set((f.x, f.y) for f in tablero.fuegos_activos)
    while cola:
        cx, cy, camino = cola.popleft()
        
        # si la celda es segura, retornar el primer vector del camino
        if (cx, cy) not in zonas_peligro:
            if len(camino) > 0: return camino[0]
            return (0, 0)
            
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            # filtro topologico total
            if tablero.es_caminable(nx, ny, bombas_activas, lista_entidades) and (nx, ny) not in visitados and (nx, ny) not in fuegos:
                visitados.add((nx, ny))
                cola.append((nx, ny, camino + [(dx, dy)]))
                
    return (0, 0)

# recibe zonas_peligro y lista_entidades para navegacion segura
def bfs_buscar_ladrillo(inicio_x, inicio_y, tablero, bombas_activas, zonas_peligro, lista_entidades):
    cola = deque([(inicio_x, inicio_y, [])])
    visitado = set([(inicio_x, inicio_y)])
    direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    while cola:
        cx, cy, camino = cola.popleft()
        
        # escaneo ofensivo de objetivos adyacentes
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            if 0 <= nx < tablero.ancho and 0 <= ny < tablero.alto:
                if tablero.matriz[ny][nx] == MURO_LADRILLO:
                    if len(camino) > 0: return camino[0]
                    else: return (0,0)
                    
        # expansion tactica evadiendo fuego y entidades
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            if tablero.es_caminable(nx, ny, bombas_activas, lista_entidades) and (nx, ny) not in visitado and (nx, ny) not in zonas_peligro:
                visitado.add((nx,ny))
                cola.append((nx, ny, camino + [(dx, dy)]))
                
    return (0, 0) 


def bfs_buscar_enemigo(inicio_x,inicio_y,tablero,bombas_activas,zonas_peligro,lista_entidades,mi_entidad):
    cola = deque([(inicio_x, inicio_y, [])])
    visitado = set([(inicio_x, inicio_y)])
    direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    #identificar coordenadas de la presa
    enemigos = [(e.x, e.y) for e in lista_entidades if e.vivo and e != mi_entidad]
    if not enemigos:
        return (0, 0)
    while cola:
        cx, cy, camino = cola.popleft()
        #escanear contacto
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            if (nx, ny) in enemigos:
                if len(camino) > 0: return camino[0]
                else: return (0, 0) #cuerpo a cuerpo
                
        #expansion tactica hacia el objetivo
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            if tablero.es_caminable(nx, ny, bombas_activas, lista_entidades) and (nx, ny) not in visitado and (nx, ny) not in zonas_peligro:
                visitado.add((nx,ny))
                cola.append((nx, ny, camino + [(dx, dy)]))
    return (0, 0) #presa inalcanzable/bloqueada por muros
        
        
    

# nucleo logico de la maquina de estados
def procesar_estado_ia(ia_entidad, tablero, bombas_activas, lista_entidades):
    if not ia_entidad.vivo:
        return (0, 0), False
        
    zonas_peligro = algoritmos.obtener_mapa_peligro(tablero, bombas_activas)
    
    # estado 1: supervivencia (evasion incondicional)
    if (ia_entidad.x, ia_entidad.y) in zonas_peligro:
        mov = bfs_escape(ia_entidad.x, ia_entidad.y, tablero, zonas_peligro, bombas_activas, lista_entidades)
        return mov, False
    
    # estado 2: granjero (recoleccion y limpieza)
    movimiento_granjero = bfs_buscar_ladrillo(ia_entidad.x, ia_entidad.y, tablero, bombas_activas, zonas_peligro, lista_entidades)
    
    if movimiento_granjero == (0,0):
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        ladrillo_cerca = False
        for dx,dy in direcciones:
            nx = ia_entidad.x + dx
            ny = ia_entidad.y + dy
            # validacion estricta de limites para evitar wrap-around
            if 0 <= nx < tablero.ancho and 0 <= ny < tablero.alto:
                if tablero.matriz[ny][nx] == MURO_LADRILLO:
                    ladrillo_cerca = True
                    break
                    
        if ladrillo_cerca:
            # protocolo anti-suicidio predictivo
            bomba_falsa = entidades.Bomba(ia_entidad.x, ia_entidad.y, RANGO_BOMBA_INICIAL, 0, ia_entidad)
            peligro_futuro = algoritmos.obtener_mapa_peligro(tablero, bombas_activas + [bomba_falsa])
            
            # evaluar viabilidad de escape
            escape = bfs_escape(ia_entidad.x, ia_entidad.y, tablero, peligro_futuro, bombas_activas + [bomba_falsa], lista_entidades)
            
            if escape != (0, 0): 
                return (0,0), True # detonacion autorizada
            else:
                return (0,0), False # auto-preservacion: detonacion abortada
    
    if movimiento_granjero != (0,0):
        return movimiento_granjero, False
    
    return (0, 0), False