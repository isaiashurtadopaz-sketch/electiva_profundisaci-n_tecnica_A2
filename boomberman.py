# boomberman.py
import sys
import random
import pygame
import configuracio
import mapas

# ==============================================================================
# 1. INICIALIZACIÓN DE PYGAME
# ==============================================================================
pygame.init()
pygame.font.init()

pantalla_completa = False
pantalla = pygame.display.set_mode((configuracio.ANCHO, configuracio.ALTO))
pygame.display.set_caption("Bomberman - NES Style")

reloj = pygame.time.Clock()

# Fuentes estables independientes del sistema
fuente_titulo = pygame.font.SysFont("arial", 54, bold=True)
fuente_subtitulo = pygame.font.SysFont("arial", 26, bold=True)
fuente_juego = pygame.font.SysFont("arial", 20)

# ==============================================================================
# 2. VARIABLES DE ESTADO Y BOTÓN
# ==============================================================================
estado_juego = "MENU"
ejecutando = True

ANCHO_BOTON, ALTO_BOTON = 280, 60
rect_boton_inicio = pygame.Rect(
    (configuracio.ANCHO // 2) - (ANCHO_BOTON // 2),
    (configuracio.ALTO // 2) - (ALTO_BOTON // 2),
    ANCHO_BOTON,
    ALTO_BOTON
)

DATOS_NIVELES = [
    {
        "mapa": mapas.MAPA_1,
        "suelo": getattr(configuracio, "SUELO_M1", (34, 139, 34)),
        "fijo": getattr(configuracio, "FIJO_M1", (100, 100, 100)),
        "destruible": getattr(configuracio, "DESTRUIBLE_M1", (205, 133, 63)),
        "enemigos": 3
    },
    {
        "mapa": mapas.MAPA_2,
        "suelo": getattr(configuracio, "SUELO_M2", (40, 116, 166)),
        "fijo": getattr(configuracio, "FIJO_M2", (90, 100, 110)),
        "destruible": getattr(configuracio, "DESTRUIBLE_M2", (210, 140, 80)),
        "enemigos": 4
    },
    {
        "mapa": mapas.MAPA_3,
        "suelo": getattr(configuracio, "SUELO_M3", (120, 40, 140)),
        "fijo": getattr(configuracio, "FIJO_M3", (80, 70, 90)),
        "destruible": getattr(configuracio, "DESTRUIBLE_M3", (180, 100, 150)),
        "enemigos": 5
    }
]

indice_nivel = 0

# ==============================================================================
# 3. FUNCIONES AUXILIARES
# ==============================================================================

def obtener_rect_casilla(fila, col, total_filas, total_cols):
    total_filas = max(1, total_filas)
    total_cols = max(1, total_cols)
    
    tamano_casilla = min(configuracio.ANCHO // total_cols, configuracio.ALTO // total_filas)
    tamano_casilla = max(10, tamano_casilla)
    
    offset_x = (configuracio.ANCHO - (total_cols * tamano_casilla)) // 2
    offset_y = (configuracio.ALTO - (total_filas * tamano_casilla)) // 2
    
    x = offset_x + col * tamano_casilla
    y = offset_y + fila * tamano_casilla
    return pygame.Rect(x, y, tamano_casilla, tamano_casilla)


def crear_enemigos(mapa, cantidad):
    enemigos = []
    casillas_libres = []
    total_filas = len(mapa)
    total_cols = len(mapa[0]) if total_filas > 0 else configuracio.COLUMNAS
    
    for f_idx, fila in enumerate(mapa):
        for c_idx, casilla in enumerate(fila):
            if int(casilla) == 0 and not (f_idx <= 2 and c_idx <= 2):
                casillas_libres.append((f_idx, c_idx))
                
    if not casillas_libres:
        casillas_libres = [(1, 2), (2, 1)]

    posiciones = random.sample(casillas_libres, min(cantidad, len(casillas_libres)))
    direcciones_posibles = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    tam_enemigo = getattr(configuracio, "TAMANO_ENEMIGO", 24)
    vel_enemigo = getattr(configuracio, "VELOCIDAD_ENEMIGO", 2)

    for f, c in posiciones:
        rect_casilla = obtener_rect_casilla(f, c, total_filas, total_cols)
        rect_enemigo = pygame.Rect(0, 0, tam_enemigo, tam_enemigo)
        rect_enemigo.center = rect_casilla.center
        
        dir_x, dir_y = random.choice(direcciones_posibles)
        enemigos.append({
            'rect': rect_enemigo,
            'dx': dir_x * vel_enemigo,
            'dy': dir_y * vel_enemigo
        })
    return enemigos


def cargar_nivel(num_nivel):
    global mapa_actual, color_suelo_actual, color_fijo_actual, color_destruible_actual
    global jugador_rect, bombas, explosiones, enemigos, jugador_vivo, nivel_completado
    
    datos = DATOS_NIVELES[num_nivel]
    mapa_actual = [list(map(int, fila)) for fila in datos["mapa"]]
    color_suelo_actual = datos["suelo"]
    color_fijo_actual = datos["fijo"]
    color_destruible_actual = datos["destruible"]
    
    total_filas = len(mapa_actual)
    total_cols = len(mapa_actual[0]) if total_filas > 0 else configuracio.COLUMNAS
    rect_inicio = obtener_rect_casilla(1, 1, total_filas, total_cols)
    
    tam_jugador = getattr(configuracio, "TAMANO_JUGADOR", 26)
    jugador_rect = pygame.Rect(0, 0, tam_jugador, tam_jugador)
    jugador_rect.center = rect_inicio.center
    
    bombas = []
    explosiones = []
    enemigos = crear_enemigos(mapa_actual, datos["enemigos"])
    jugador_vivo = True
    nivel_completado = False

# ==============================================================================
# 4. BUCLE PRINCIPAL
# ==============================================================================
while ejecutando:
    tiempo_actual = pygame.time.get_ticks()
    pos_raton = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        # Pantalla completa con F11
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
            pantalla_completa = not pantalla_completa
            if pantalla_completa:
                pantalla = pygame.display.set_mode((configuracio.ANCHO, configuracio.ALTO), pygame.FULLSCREEN | pygame.SCALED)
            else:
                pantalla = pygame.display.set_mode((configuracio.ANCHO, configuracio.ALTO))

        # Eventos en el Menú (Cualquier clic o tecla inicia la partida)
        if estado_juego == "MENU":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                indice_nivel = 0
                cargar_nivel(indice_nivel)
                estado_juego = "JUGANDO"

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False
                else:
                    indice_nivel = 0
                    cargar_nivel(indice_nivel)
                    estado_juego = "JUGANDO"

        # Eventos durante el Juego
        elif estado_juego == "JUGANDO" and evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                estado_juego = "MENU"

            if evento.key == pygame.K_r and not jugador_vivo:
                cargar_nivel(indice_nivel)
                
            if evento.key == pygame.K_RETURN and nivel_completado:
                if indice_nivel < len(DATOS_NIVELES) - 1:
                    indice_nivel += 1
                else:
                    indice_nivel = 0
                    estado_juego = "MENU"
                cargar_nivel(indice_nivel)
            
            if evento.key == pygame.K_SPACE and jugador_vivo and not nivel_completado:
                total_filas = len(mapa_actual)
                total_cols = len(mapa_actual[0])
                
                tamano_casilla = min(configuracio.ANCHO // total_cols, configuracio.ALTO // total_filas)
                offset_x = (configuracio.ANCHO - (total_cols * tamano_casilla)) // 2
                offset_y = (configuracio.ALTO - (total_filas * tamano_casilla)) // 2
                
                col = int((jugador_rect.centerx - offset_x) // tamano_casilla)
                fila = int((jugador_rect.centery - offset_y) // tamano_casilla)
                
                col = max(0, min(total_cols - 1, col))
                fila = max(0, min(total_filas - 1, fila))
                
                rect_bomba = obtener_rect_casilla(fila, col, total_filas, total_cols)
                if rect_bomba not in [b['rect'] for b in bombas]:
                    bombas.append({
                        'rect': rect_bomba,
                        'tiempo': tiempo_actual,
                        'col': col,
                        'fila': fila
                    })

    # ==============================================================================
    # RENDERIZADO VISUAL
    # ==============================================================================
    if estado_juego == "MENU":
        # Fondo azul oscuro garantizado (evita pantalla en negro)
        pantalla.fill((25, 30, 50))
        
        txt_sombra = fuente_titulo.render("BOMBERMAN", True, (0, 0, 0))
        txt_titulo = fuente_titulo.render("BOMBERMAN", True, (241, 196, 15))
        pantalla.blit(txt_sombra, txt_sombra.get_rect(center=(configuracio.ANCHO // 2 + 3, 113)))
        pantalla.blit(txt_titulo, txt_titulo.get_rect(center=(configuracio.ANCHO // 2, 110)))
        
        # Botón
        hover = rect_boton_inicio.collidepoint(pos_raton)
        color_boton = (230, 126, 34) if hover else (211, 84, 0)
        color_borde = (255, 255, 255) if hover else (241, 196, 15)

        pygame.draw.rect(pantalla, color_boton, rect_boton_inicio, border_radius=12)
        pygame.draw.rect(pantalla, color_borde, rect_boton_inicio, 3, border_radius=12)

        txt_boton = fuente_subtitulo.render("INICIAR JUEGO", True, (255, 255, 255))
        pantalla.blit(txt_boton, txt_boton.get_rect(center=rect_boton_inicio.center))

        # Indicaciones de inicio
        txt_tecla = fuente_subtitulo.render("Presiona ENTER, ESPACIO o Clic para empezar", True, (46, 204, 113))
        pantalla.blit(txt_tecla, txt_tecla.get_rect(center=(configuracio.ANCHO // 2, 370)))

        ctrl_1 = fuente_juego.render("Controles: WASD = Moverse | ESPACIO = Bomba", True, (200, 210, 225))
        ctrl_2 = fuente_juego.render("R = Reiniciar | ESC = Menú | F11 = Pantalla Completa", True, (200, 210, 225))
        pantalla.blit(ctrl_1, ctrl_1.get_rect(center=(configuracio.ANCHO // 2, 450)))
        pantalla.blit(ctrl_2, ctrl_2.get_rect(center=(configuracio.ANCHO // 2, 485)))

    elif estado_juego == "JUGANDO":
        total_filas = len(mapa_actual)
        total_cols = len(mapa_actual[0])

        bloques_colision = []
        for fila_idx, fila in enumerate(mapa_actual):
            for col_idx, casilla in enumerate(fila):
                if casilla in (1, 2):
                    bloques_colision.append(obtener_rect_casilla(fila_idx, col_idx, total_filas, total_cols))

        if jugador_vivo and not nivel_completado:
            teclas = pygame.key.get_pressed()
            dx, dy = 0, 0
            vel_jugador = getattr(configuracio, "VELOCIDAD_JUGADOR", 3)
            if teclas[pygame.K_a]: dx -= vel_jugador
            if teclas[pygame.K_d]: dx += vel_jugador
            if teclas[pygame.K_w]: dy -= vel_jugador
            if teclas[pygame.K_s]: dy += vel_jugador

            jugador_rect.x += dx
            for bloque in bloques_colision:
                if jugador_rect.colliderect(bloque):
                    if dx > 0: jugador_rect.right = bloque.left
                    if dx < 0: jugador_rect.left = bloque.right

            jugador_rect.y += dy
            for bloque in bloques_colision:
                if jugador_rect.colliderect(bloque):
                    if dy > 0: jugador_rect.bottom = bloque.top
                    if dy < 0: jugador_rect.top = bloque.bottom

            for enemigo in enemigos:
                enemigo['rect'].x += enemigo['dx']
                if any(enemigo['rect'].colliderect(b) for b in bloques_colision):
                    enemigo['rect'].x -= enemigo['dx']
                    enemigo['dx'] *= -1

                enemigo['rect'].y += enemigo['dy']
                if any(enemigo['rect'].colliderect(b) for b in bloques_colision):
                    enemigo['rect'].y -= enemigo['dy']
                    enemigo['dy'] *= -1

                if random.random() < 0.02:
                    vel_e = getattr(configuracio, "VELOCIDAD_ENEMIGO", 2)
                    dirs = [(-vel_e, 0), (vel_e, 0), (0, -vel_e), (0, vel_e)]
                    enemigo['dx'], enemigo['dy'] = random.choice(dirs)

                if jugador_rect.colliderect(enemigo['rect']):
                    jugador_vivo = False

        tiempo_bomba = getattr(configuracio, "TIEMPO_BOMBA", 3000)
        alcance_bomba = getattr(configuracio, "ALCANCE_BOMBA", 2)
        duracion_explosion = getattr(configuracio, "DURACION_EXPLOSION", 500)

        bombas_a_eliminar = []
        for bomba in bombas:
            if tiempo_actual - bomba['tiempo'] >= tiempo_bomba:
                bombas_a_eliminar.append(bomba)
                col_b, fila_b = bomba['col'], bomba['fila']
                llamas = [obtener_rect_casilla(fila_b, col_b, total_filas, total_cols)]
                
                direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                for df, dc in direcciones:
                    for i in range(1, alcance_bomba + 1):
                        f, c = fila_b + (df * i), col_b + (dc * i)
                        if 0 <= f < total_filas and 0 <= c < total_cols:
                            casilla = mapa_actual[f][c]
                            rect_llama = obtener_rect_casilla(f, c, total_filas, total_cols)
                            
                            if casilla == 1:
                                break
                            elif casilla == 2:
                                mapa_actual[f][c] = 0
                                llamas.append(rect_llama)
                                break
                            else:
                                llamas.append(rect_llama)

                explosiones.append({'llamas': llamas, 'tiempo': tiempo_actual})

        for bomba in bombas_a_eliminar:
            bombas.remove(bomba)

        explosiones = [exp for exp in explosiones if tiempo_actual - exp['tiempo'] < duracion_explosion]

        enemigos_a_eliminar = []
        for exp in explosiones:
            for llama in exp['llamas']:
                if jugador_vivo and jugador_rect.colliderect(llama):
                    jugador_vivo = False
                
                for enemigo in enemigos:
                    if enemigo['rect'].colliderect(llama) and enemigo not in enemigos_a_eliminar:
                        enemigos_a_eliminar.append(enemigo)

        for enemigo in enemigos_a_eliminar:
            enemigos.remove(enemigo)

        if jugador_vivo and len(enemigos) == 0:
            nivel_completado = True

        pantalla.fill((20, 24, 32))
        
        tamano_casilla = min(configuracio.ANCHO // total_cols, configuracio.ALTO // total_filas)
        offset_x = (configuracio.ANCHO - (total_cols * tamano_casilla)) // 2
        offset_y = (configuracio.ALTO - (total_filas * tamano_casilla)) // 2
        
        rect_tablero = pygame.Rect(offset_x, offset_y, total_cols * tamano_casilla, total_filas * tamano_casilla)
        pygame.draw.rect(pantalla, color_suelo_actual, rect_tablero)

        color_fuego = getattr(configuracio, "COLOR_FUEGO", (231, 76, 60))
        color_bomba = getattr(configuracio, "COLOR_BOMBA", (0, 0, 0))
        color_enemigo = getattr(configuracio, "COLOR_ENEMIGO", (155, 89, 182))
        color_jugador = getattr(configuracio, "COLOR_JUGADOR", (241, 196, 15))

        for fila_idx, fila in enumerate(mapa_actual):
            for col_idx, casilla in enumerate(fila):
                rect = obtener_rect_casilla(fila_idx, col_idx, total_filas, total_cols)
                
                if casilla == 1:
                    pygame.draw.rect(pantalla, color_fijo_actual, rect)
                    pygame.draw.rect(pantalla, (0, 0, 0), rect, 2)
                elif casilla == 2:
                    pygame.draw.rect(pantalla, color_destruible_actual, rect)
                    pygame.draw.rect(pantalla, (100, 50, 20), rect, 2)

        for exp in explosiones:
            for llama in exp['llamas']:
                pygame.draw.rect(pantalla, color_fuego, llama)

        for bomba in bombas:
            pygame.draw.circle(pantalla, color_bomba, bomba['rect'].center, min(bomba['rect'].width, bomba['rect'].height) // 3)

        for enemigo in enemigos:
            pygame.draw.rect(pantalla, color_enemigo, enemigo['rect'])

        if jugador_vivo:
            pygame.draw.rect(pantalla, color_jugador, jugador_rect)

        txt_nivel = fuente_juego.render(f"Nivel {indice_nivel + 1}", True, (255, 255, 255))
        pantalla.blit(txt_nivel, (15, 10))

        if nivel_completado:
            es_ultimo = (indice_nivel == len(DATOS_NIVELES) - 1)
            msg_principal = "¡JUEGO COMPLETADO!" if es_ultimo else f"¡NIVEL {indice_nivel + 1} SUPERADO!"
            msg_sub = "ENTER: Volver al Menú" if es_ultimo else "ENTER: Siguiente Nivel"
            
            txt_1 = fuente_subtitulo.render(msg_principal, True, (46, 204, 113))
            txt_2 = fuente_juego.render(msg_sub, True, (255, 255, 255))
            
            s = pygame.Surface((480, 90))
            s.set_alpha(220)
            s.fill((0, 0, 0))
            
            pantalla.blit(s, (configuracio.ANCHO // 2 - 240, configuracio.ALTO // 2 - 45))
            pantalla.blit(txt_1, txt_1.get_rect(center=(configuracio.ANCHO // 2, configuracio.ALTO // 2 - 15)))
            pantalla.blit(txt_2, txt_2.get_rect(center=(configuracio.ANCHO // 2, configuracio.ALTO // 2 + 20)))

        elif not jugador_vivo:
            txt_game_over = fuente_subtitulo.render("¡HAS MUERTO! Presiona R", True, (231, 76, 60))
            
            s = pygame.Surface((380, 60))
            s.set_alpha(200)
            s.fill((0, 0, 0))
            
            pantalla.blit(s, (configuracio.ANCHO // 2 - 190, configuracio.ALTO // 2 - 30))
            pantalla.blit(txt_game_over, txt_game_over.get_rect(center=(configuracio.ANCHO // 2, configuracio.ALTO // 2)))

    pygame.display.flip()
    reloj.tick(getattr(configuracio, "FPS", 60))

pygame.quit()
sys.exit()