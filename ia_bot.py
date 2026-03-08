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
        

def linea_de_vision_despejada(ia_x, ia_y, objetivo_x, objetivo_y, tablero, bombas_activas):
    # verificar si esta alineado horizontal o verticalmente
    if ia_x != objetivo_x and ia_y != objetivo_y:
        return False # esta en diagonal, no hay linea de vision directa
        
    # calcular direccion del rayo
    dx = 0
    dy = 0
    if ia_x < objetivo_x: dx = 1
    elif ia_x > objetivo_x: dx = -1
    elif ia_y < objetivo_y: dy = 1
    elif ia_y > objetivo_y: dy = -1
    
    # trazar el rayo paso a paso hasta el objetivo
    cx, cy = ia_x + dx, ia_y + dy
    while (cx, cy) != (objetivo_x, objetivo_y):
        # si choca con algo solido, la vision se corta
        if not tablero.es_caminable(cx, cy, bombas_activas, []):
            return False
        cx += dx
        cy += dy
        
    return True # el pasillo esta limpio y el enemigo esta en la mira
    


# AÑADIR A ia_bot.py

def evaluar_opciones_escape(x, y, tablero, bombas_activas, zonas_peligro, lista_entidades):
    """
    Simula cuántas casillas libres tiene una entidad desde (x, y).
    Es un BFS limitado a 3 pasos para medir la "libertad de movimiento".
    """
    cola = deque([(x, y, 0)])
    visitados = set([(x, y)])
    casillas_libres = 0
    
    while cola:
        cx, cy, pasos = cola.popleft()
        if pasos >= 4: #limitar rango para rendimiento
            continue
            
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            if tablero.es_caminable(nx, ny, bombas_activas, lista_entidades) and (nx, ny) not in visitados and (nx, ny) not in zonas_peligro:
                visitados.add((nx, ny))
                casillas_libres += 1
                cola.append((nx, ny, pasos + 1))
                
    return casillas_libres



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
    
    # estado 3: cazador
    #si llegamos a este estado significa que no hay nada que nos impida atacar a la otra entidad
    movimiento_cazador = bfs_buscar_enemigo(ia_entidad.x, ia_entidad.y, tablero, bombas_activas, zonas_peligro, lista_entidades, ia_entidad)
    
    enemigos = [e for e in lista_entidades if e.vivo and e != ia_entidad]
    if enemigos:
        enemigo_objetivo = enemigos[0] #seleccionar a la presa principal
        
        # medir distancia del enemigo para aplicar acorralamiento
        # calcular distancia Manhattan
        distancia = abs(ia_entidad.x - enemigo_objetivo.x) + abs(ia_entidad.y - enemigo_objetivo.y)
        
        if distancia <= 4:
            # pensamiento predictivo(Mini-Max heuristico)
            bomba_imaginaria = entidades.Bomba(ia_entidad.x, ia_entidad.y, RANGO_BOMBA_INICIAL, 0, ia_entidad)
            bombas_futuras = bombas_activas + [bomba_imaginaria]
            peligro_futuro = algoritmos.obtener_mapa_peligro(tablero, bombas_futuras)
            
            # evaluar mi supervivencia
            mi_escape = bfs_escape(ia_entidad.x, ia_entidad.y, tablero, peligro_futuro, bombas_futuras, lista_entidades)
            
            # evaluar si nuestra bomba ataca al enemigo
            enemigo_en_peligro = (enemigo_objetivo.x, enemigo_objetivo.y) in peligro_futuro
            
            # evaluar la movilidad restante del enemigo si pongo la bomba
            movilidad_enemigo = evaluar_opciones_escape(enemigo_objetivo.x, enemigo_objetivo.y, tablero, bombas_futuras, peligro_futuro, lista_entidades)
            
            # decision final
            if mi_escape != (0, 0) and (enemigo_en_peligro or movilidad_enemigo <= 1):
                return (0, 0), True #acorralar
                
    # si no es momento de soltar bomba, ejecutar intercepcion visual 
    for enemigo in enemigos:
        if linea_de_vision_despejada(ia_entidad.x, ia_entidad.y, enemigo.x, enemigo.y, tablero, bombas_activas):
            bomba_falsa = entidades.Bomba(ia_entidad.x, ia_entidad.y, RANGO_BOMBA_INICIAL, 0, ia_entidad)
            peligro_futuro = algoritmos.obtener_mapa_peligro(tablero, bombas_activas + [bomba_falsa])
            escape = bfs_escape(ia_entidad.x, ia_entidad.y, tablero, peligro_futuro, bombas_activas + [bomba_falsa], lista_entidades)
            
            if escape != (0, 0): 
                return (0,0), True 

    # si no hay oportunidad tactica de bomba, avanzar hacia el enemigo
    if movimiento_cazador != (0, 0):
        return movimiento_cazador, False

    return (0, 0), False
