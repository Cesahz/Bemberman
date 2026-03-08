import algoritmos
from collections import deque
from config import MURO_LADRILLO, RANGO_BOMBA_INICIAL
import entidades
import math
import heapq

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
                    if len(camino) > 0: return camino[0], len(camino)
                    else: return (0,0), 0
                    
        # expansion tactica evadiendo fuego y entidades
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            if tablero.es_caminable(nx, ny, bombas_activas, lista_entidades) and (nx, ny) not in visitado and (nx, ny) not in zonas_peligro:
                visitado.add((nx,ny))
                cola.append((nx, ny, camino + [(dx, dy)]))
                
    return (0, 0), 999

def astar_buscar_enemigo(inicio_x, inicio_y, tablero, bombas_activas, zonas_peligro, lista_entidades, mi_entidad):
    # identificar coordenadas de la presa
    enemigos = [(e.x, e.y) for e in lista_entidades if e.vivo and e != mi_entidad]
    if not enemigos:
        return (0, 0)
        
    objetivo_x, objetivo_y = enemigos[0]
    
    # heuristica de distancia manhattan
    def heuristica(cx, cy):
        return abs(cx - objetivo_x) + abs(cy - objetivo_y)

    # la cola guarda tuplas: (f_score, costo_g, x, y, camino)
    open_heap = [(heuristica(inicio_x, inicio_y), 0, inicio_x, inicio_y, [])]
    visitados = set([(inicio_x, inicio_y)])
    direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    while open_heap:
        _, costo, cx, cy, camino = heapq.heappop(open_heap)
        
        # escanear contacto cuerpo a cuerpo
        for dx, dy in direcciones:
            if (cx + dx, cy + dy) == (objetivo_x, objetivo_y):
                if len(camino) > 0: return camino[0]
                else: return (0, 0)
                
        # expansion dirigida por heuristica
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            if tablero.es_caminable(nx, ny, bombas_activas, lista_entidades) and (nx, ny) not in visitados and (nx, ny) not in zonas_peligro:
                visitados.add((nx, ny))
                nuevo_costo = costo + 1
                nuevo_camino = camino + [(dx, dy)]
                f_score = nuevo_costo + heuristica(nx, ny)
                heapq.heappush(open_heap, (f_score, nuevo_costo, nx, ny, nuevo_camino))
                
    return (0, 0) # presa inalcanzable
        

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
    

def medir_jaula_control(x, y, tablero, bombas_activas, zonas_peligro, lista_entidades, limite_area=20):
    """
    flood fill optimizado. mide el area real en la que una entidad esta atrapada.
    si el area es menor a 4, la entidad esta virtualmente muerta.
    """
    cola = deque([(x, y)])
    visitados = set([(x, y)])
    area_disponible = 0
    
    direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    while cola and area_disponible < limite_area:
        cx, cy = cola.popleft()
        area_disponible += 1
        
        for dx, dy in direcciones:
            nx = cx + dx
            ny = cy + dy
            # las bombas simuladas cuentan como paredes solidas aqui, aislando areas
            if tablero.es_caminable(nx, ny, bombas_activas, lista_entidades) and (nx, ny) not in visitados and (nx, ny) not in zonas_peligro:
                visitados.add((nx, ny))
                cola.append((nx, ny))
                
    return area_disponible

def evaluar_tablero_minimax(ia_x, ia_y, ene_x, ene_y, tablero, bombas_simuladas, lista_entidades):
    peligro_simulado = algoritmos.obtener_mapa_peligro(tablero, bombas_simuladas)
    
    # castigo absoluto
    if (ia_x, ia_y) in peligro_simulado:
        return -math.inf
        
    ene_area = medir_jaula_control(ene_x, ene_y, tablero, bombas_simuladas, peligro_simulado, lista_entidades)
    
    # recompensa absoluta: si el enemigo cae en peligro o su jaula es menor a 2 (jaque mate ineludible)
    if (ene_x, ene_y) in peligro_simulado or ene_area <= 1:
        return math.inf
        
    ia_area = medir_jaula_control(ia_x, ia_y, tablero, bombas_simuladas, peligro_simulado, lista_entidades)
    distancia = abs(ia_x - ene_x) + abs(ia_y - ene_y)
    
    bono_cadena = 0
    if len(bombas_simuladas) > 1:
        for b1 in bombas_simuladas:
            for b2 in bombas_simuladas:
                if b1 != b2:
                    if linea_de_vision_despejada(b1.x, b1.y, b2.x, b2.y, tablero, []):
                        dist_bombas = abs(b1.x - b2.x) + abs(b1.y - b2.y)
                        if dist_bombas <= b1.rango:
                            bono_cadena += 50
    
    # la magia del acorralamiento: penalizamos fuertemente el area que le dejamos al enemigo.
    # si la simulacion de poner una bomba reduce su area a 3 casillas, la puntuacion se dispara.
    puntuacion = (ia_area * 5) - (ene_area * 30) - (distancia * 5) + bono_cadena
    return puntuacion

def minimax_ab(profundidad, ia_x, ia_y, ene_x, ene_y, tablero, bombas_simuladas, lista_entidades, alfa, beta, es_ia):
    if profundidad == 0:
        return evaluar_tablero_minimax(ia_x, ia_y, ene_x, ene_y, tablero, bombas_simuladas, lista_entidades)
        
    direcciones = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)]
    
    if es_ia:
        max_eval = -math.inf
        for dx, dy in direcciones:
            nx, ny = ia_x + dx, ia_y + dy
            if tablero.es_caminable(nx, ny, bombas_simuladas, lista_entidades):
                eval_actual = minimax_ab(profundidad - 1, nx, ny, ene_x, ene_y, tablero, bombas_simuladas, lista_entidades, alfa, beta, False)
                max_eval = max(max_eval, eval_actual)
                alfa = max(alfa, eval_actual)
                if beta <= alfa:
                    break
        return max_eval
        
    else:
        min_eval = math.inf
        for dx, dy in direcciones:
            nx, ny = ene_x + dx, ene_y + dy
            if tablero.es_caminable(nx, ny, bombas_simuladas, lista_entidades):
                eval_actual = minimax_ab(profundidad - 1, ia_x, ia_y, nx, ny, tablero, bombas_simuladas, lista_entidades, alfa, beta, True)
                min_eval = min(min_eval, eval_actual)
                beta = min(beta, eval_actual)
                if beta <= alfa:
                    break
        return min_eval

def decidir_movimiento_letal(ia_entidad, enemigo_objetivo, tablero, bombas_activas, lista_entidades, profundidad_inicial=3):
    mejor_mov = (0, 0)
    poner_bomba = False
    mejor_puntaje = -math.inf
    alfa = -math.inf
    beta = math.inf
    direcciones = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)]
    
    for dx, dy in direcciones:
        nx, ny = ia_entidad.x + dx, ia_entidad.y + dy
        if tablero.es_caminable(nx, ny, bombas_activas, lista_entidades):
            #rama A: movimiento puro
            puntaje_mov = minimax_ab(profundidad_inicial - 1, nx, ny, enemigo_objetivo.x, enemigo_objetivo.y, tablero, bombas_activas, lista_entidades, alfa, beta, False)
            
            #rama B: soltar bomba y moverse
            bomba_falsa = entidades.Bomba(ia_entidad.x, ia_entidad.y, RANGO_BOMBA_INICIAL, 0, ia_entidad)
            bombas_futuras = bombas_activas + [bomba_falsa]
            puntaje_bomba = minimax_ab(profundidad_inicial - 1, nx, ny, enemigo_objetivo.x, enemigo_objetivo.y, tablero, bombas_futuras, lista_entidades, alfa, beta, False)
            
            if puntaje_mov > mejor_puntaje:
                mejor_puntaje = puntaje_mov
                mejor_mov = (dx, dy)
                poner_bomba = False
                
            if puntaje_bomba > mejor_puntaje:
                mejor_puntaje = puntaje_bomba
                mejor_mov = (dx, dy)
                poner_bomba = True
                
            alfa = max(alfa, mejor_puntaje)
            
    return mejor_mov, poner_bomba

# nucleo logico de la maquina de estados
def procesar_estado_ia(ia_entidad, tablero, bombas_activas, lista_entidades):
    if not ia_entidad.vivo:
        return (0, 0), False
        
    zonas_peligro = algoritmos.obtener_mapa_peligro(tablero, bombas_activas)
    
    # estado 1: supervivencia (evasion incondicional)
    if (ia_entidad.x, ia_entidad.y) in zonas_peligro:
        mov = bfs_escape(ia_entidad.x, ia_entidad.y, tablero, zonas_peligro, bombas_activas, lista_entidades)
        return mov, False
        
    enemigos = [e for e in lista_entidades if e.vivo and e != ia_entidad]
    enemigo_objetivo = enemigos[0] if enemigos else None
    
    # metricas espaciales para la toma de decisiones clinicas
    distancia_enemigo = math.inf
    if enemigo_objetivo:
        distancia_enemigo = abs(ia_entidad.x - enemigo_objetivo.x) + abs(ia_entidad.y - enemigo_objetivo.y)
        
    movimiento_granjero, distancia_ladrillo = bfs_buscar_ladrillo(ia_entidad.x, ia_entidad.y, tablero, bombas_activas, zonas_peligro, lista_entidades)
    
    vision_clara = False
    if enemigo_objetivo:
        vision_clara = linea_de_vision_despejada(ia_entidad.x, ia_entidad.y, enemigo_objetivo.x, enemigo_objetivo.y, tablero, bombas_activas)

    # jerarquia de la amenaza
    modo_caza_activo = enemigo_objetivo and (vision_clara or distancia_enemigo <= 3 or (distancia_enemigo <= 7 and distancia_enemigo < distancia_ladrillo))
    
    # estado 2: cazador (prioridad letal)
    if modo_caza_activo:
        mov_optimo, soltar_carga = decidir_movimiento_letal(ia_entidad, enemigo_objetivo, tablero, bombas_activas, lista_entidades, profundidad_inicial=6)
        
        if soltar_carga:
            return mov_optimo, True # acorralar 
        elif mov_optimo != (0,0):
            return mov_optimo, False # avanzar sobre la presa
            
    # estado 3: espera tactica (disciplina de posicionamiento)
    # si acabamos de poner una bomba o hay una cerca, y ya estamos en zona segura, 
    # nos quedamos quietos esperando la detonacion en lugar de buscar otra caja lejana.
    if bombas_activas:
        for b in bombas_activas:
            # calculamos si estamos en el perimetro de observacion (rango + 2 casillas maximo)
            dist_bomba = abs(ia_entidad.x - b.x) + abs(ia_entidad.y - b.y)
            if dist_bomba <= b.rango + 2:
                return (0, 0), False # inmovilidad tactica absoluta
                
    # estado 4: granjero (expansion de dominio en el entorno cercano)
    if movimiento_granjero == (0,0) and distancia_ladrillo == 0:
        direcciones = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        ladrillo_cerca = False
        for dx,dy in direcciones:
            nx = ia_entidad.x + dx
            ny = ia_entidad.y + dy
            # validacion estricta de limites
            if 0 <= nx < tablero.ancho and 0 <= ny < tablero.alto:
                if tablero.matriz[ny][nx] == MURO_LADRILLO:
                    ladrillo_cerca = True
                    break
                    
        if ladrillo_cerca:
            # simulacion de supervivencia post-detonacion
            bomba_falsa = entidades.Bomba(ia_entidad.x, ia_entidad.y, RANGO_BOMBA_INICIAL, 0, ia_entidad)
            peligro_futuro = algoritmos.obtener_mapa_peligro(tablero, bombas_activas + [bomba_falsa])
            escape = bfs_escape(ia_entidad.x, ia_entidad.y, tablero, peligro_futuro, bombas_activas + [bomba_falsa], lista_entidades)
            
            if escape != (0, 0): 
                return (0,0), True # detonacion autorizada
            else:
                return (0,0), False # auto-preservacion tactica
                
    if movimiento_granjero != (0,0):
        return movimiento_granjero, False

    # estado 5: rastreo pasivo (si no hay ladrillos y el enemigo esta fuera de rango)
    if enemigo_objetivo:
        # actualizamos la llamada a la nueva funcion a*
        movimiento_rastreo = astar_buscar_enemigo(ia_entidad.x, ia_entidad.y, tablero, bombas_activas, zonas_peligro, lista_entidades, ia_entidad)
        if movimiento_rastreo != (0,0):
            return movimiento_rastreo, False

    return (0, 0), False