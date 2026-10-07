# boomberman_4.py
import sys
import os
import random
import pygame
import configuracio
import mapas

# ==============================================================================
# 1. INICIALIZACIÓN DE PYGAME, AUDIO Y VENTANA
# ==============================================================================
pygame.init()
pygame.mixer.init()
pygame.font.init()

pantalla_completa = False

# Dimensiones base del juego
ANCHO_BASE = getattr(configuracio, "ANCHO", 800)
ALTO_BASE = getattr(configuracio, "ALTO", 600)

ancho_ventana, alto_ventana = ANCHO_BASE, ALTO_BASE

pantalla = pygame.display.set_mode((ancho_ventana, alto_ventana), pygame.RESIZABLE)
pygame.display.set_caption("Bomberman - NES Style")

superficie_juego = pygame.Surface((ANCHO_BASE, ALTO_BASE))
reloj = pygame.time.Clock()

fuente_titulo = pygame.font.SysFont("arial", 54, bold=True)
fuente_subtitulo = pygame.font.SysFont("arial", 26, bold=True)
fuente_juego = pygame.font.SysFont("arial", 20)

# --- CARGA Y CONFIGURACIÓN DEL SISTEMA DE AUDIO ---
sfx_bomba = None
sfx_game_over = None

try:
    if os.path.exists("sonidodebomba.mp3"):
        sfx_bomba = pygame.mixer.Sound("sonidodebomba.mp3")
    if os.path.exists("gamerover.mp3"):
        sfx_game_over = pygame.mixer.Sound("gamerover.mp3")
    print("¡Efectos de sonido cargados correctamente!")
except Exception as e:
    print(f"Nota: No se pudieron cargar los efectos de sonido ({e})")

RUTAS_MUSICA = {
    "MENU": "musicadeintro.mp3",
    0: "nusicanivel1.mp3",
    1: "musicanivel2.mp3",
    2: "musicanivel3.mp3"
}

musica_actual_pista = None

def cambiar_musica(ruta_archivo, forzar=False):
    global musica_actual_pista
    if musica_actual_pista != ruta_archivo or forzar:
        musica_actual_pista = ruta_archivo
        if ruta_archivo and os.path.exists(ruta_archivo):
            try:
                pygame.mixer.music.load(ruta_archivo)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Error al reproducir {ruta_archivo}: {e}")
        else:
            pygame.mixer.music.stop()

# --- CARGA Y RECORTE DE HOJA DE SPRITES DEL JUGADOR ---
tam_jugador = getattr(configuracio, "TAMANO_JUGADOR", 36)
sprites_cargados = False

try:
    hoja_sprites = pygame.image.load("animaciones (1).png")
    
    if hoja_sprites.get_alpha() is not None:
        hoja_sprites = hoja_sprites.convert_alpha()
    else:
        hoja_sprites = hoja_sprites.convert()
        hoja_sprites.set_colorkey((255, 255, 255))
    
    COLUMNAS_HOJA, FILAS_HOJA = 7, 4
    ancho_f = hoja_sprites.get_width() // COLUMNAS_HOJA
    alto_f = hoja_sprites.get_height() // FILAS_HOJA
    
    MARGEN = 1 
    
    matriz_sprites = []
    for f in range(FILAS_HOJA):
        fila_s = []
        for c in range(COLUMNAS_HOJA):
            rect_corte = pygame.Rect(
                c * ancho_f + MARGEN,
                f * alto_f + MARGEN,
                max(1, ancho_f - (MARGEN * 2)),
                max(1, alto_f - (MARGEN * 2))
            )
            frame_limpio = pygame.Surface(rect_corte.size, pygame.SRCALPHA)
            frame_limpio.blit(hoja_sprites, (0, 0), rect_corte)
            frame_esc = pygame.transform.scale(frame_limpio, (tam_jugador, tam_jugador))
            fila_s.append(frame_esc)
        matriz_sprites.append(fila_s)
        
    ANIM_ABAJO = [matriz_sprites[0][0]]
    ANIM_ARRIBA = [matriz_sprites[0][1], matriz_sprites[0][2]]
    ANIM_DERECHA = [matriz_sprites[0][3], matriz_sprites[0][4], matriz_sprites[0][5], matriz_sprites[0][6]]
    ANIM_IZQUIERDA = [pygame.transform.flip(f, True, False) for f in ANIM_DERECHA]
    ANIM_VICTORIA = [matriz_sprites[1][0], matriz_sprites[1][1], matriz_sprites[1][2]]
    FRAME_BOMBA = matriz_sprites[3][0]
    
    sprites_cargados = True
    print("¡Sprites del jugador recortados correctamente!")
except Exception as e:
    print(f"Nota: Usando cuadros de color para el personaje ({e})")

# --- CARGA Y ESCALADO DEL SPRITE DE LA BOMBA ---
sprite_bomba = None
tam_bomba = int(tam_jugador * 0.8)

try:
    img_bomba_raw = pygame.image.load("bomba.png")
    if img_bomba_raw.get_alpha() is not None:
        img_bomba_raw = img_bomba_raw.convert_alpha()
    else:
        img_bomba_raw = img_bomba_raw.convert()
        img_bomba_raw.set_colorkey((255, 255, 255))
        
    rect_limpio = img_bomba_raw.get_bounding_rect()
    if rect_limpio.width > 0 and rect_limpio.height > 0:
        surf_bomba = pygame.Surface(rect_limpio.size, pygame.SRCALPHA)
        surf_bomba.blit(img_bomba_raw, (0, 0), rect_limpio)
        img_bomba_raw = surf_bomba
        
    w_orig, h_orig = img_bomba_raw.get_width(), img_bomba_raw.get_height()
    ratio = min(tam_bomba / w_orig, tam_bomba / h_orig)
    nw, nh = max(1, int(w_orig * ratio)), max(1, int(h_orig * ratio))
    
    sprite_bomba = pygame.transform.scale(img_bomba_raw, (nw, nh))
    print("¡Sprite de bomba.png cargado correctamente!")
except Exception as e:
    print(f"Nota: No se pudo cargar 'bomba.png' ({e})")

# --- CARGA DE LA HOJA DE EXPLOSIÓN ---
frames_explosion = []

try:
    nombre_archivo_exp = "exploción.png" if os.path.exists("exploción.png") else "explosion.png"
    hoja_exp = pygame.image.load(nombre_archivo_exp)
    
    if hoja_exp.get_alpha() is not None:
        hoja_exp = hoja_exp.convert_alpha()
    else:
        hoja_exp = hoja_exp.convert()
        hoja_exp.set_colorkey((255, 255, 255))

    COLS_EXP, FILAS_EXP = 4, 4
    ancho_exp_f = hoja_exp.get_width() // COLS_EXP
    alto_exp_f = hoja_exp.get_height() // FILAS_EXP

    for f in range(FILAS_EXP):
        for c in range(COLS_EXP):
            rect_corte = pygame.Rect(c * ancho_exp_f, f * alto_exp_f, ancho_exp_f, alto_exp_f)
            frame_limpio = pygame.Surface(rect_corte.size, pygame.SRCALPHA)
            frame_limpio.blit(hoja_exp, (0, 0), rect_corte)
            frames_explosion.append(frame_limpio)

    print(f"¡Animación de explosión ({len(frames_explosion)} cuadros) cargada con éxito!")
except Exception as e:
    print(f"Nota: No se pudo cargar la hoja de explosión ({e})")

# --- CARGA DE SPRITES DE ENEMIGOS POR NIVEL ---
def cargar_sprite_enemigo_individual(ruta_archivo, tam_e):
    try:
        img_raw = pygame.image.load(ruta_archivo)
        if img_raw.get_alpha() is not None:
            img_raw = img_raw.convert_alpha()
        else:
            img_raw = img_raw.convert()
            img_raw.set_colorkey((255, 255, 255))
            
        rect_limpio = img_raw.get_bounding_rect()
        if rect_limpio.width > 0 and rect_limpio.height > 0:
            surf_e = pygame.Surface(rect_limpio.size, pygame.SRCALPHA)
            surf_e.blit(img_raw, (0, 0), rect_limpio)
            img_raw = surf_e
            
        w_orig, h_orig = img_raw.get_width(), img_raw.get_height()
        ratio = min(tam_e / w_orig, tam_e / h_orig)
        nw, nh = max(1, int(w_orig * ratio)), max(1, int(h_orig * ratio))
        
        img_esc = pygame.transform.scale(img_raw, (nw, nh))
        
        surf_canvas = pygame.Surface((tam_e, tam_e), pygame.SRCALPHA)
        offset_x = (tam_e - nw) // 2
        offset_y = (tam_e - nh) // 2
        surf_canvas.blit(img_esc, (offset_x, offset_y))

        dict_dir = {}
        for dir_key in ["IZQUIERDA", "DERECHA", "ABAJO", "ARRIBA"]:
            dict_dir[dir_key] = surf_canvas

        print(f"¡Sprite cargado correctamente desde '{ruta_archivo}'!")
        return dict_dir
    except Exception as e:
        print(f"Nota: No se pudo cargar '{ruta_archivo}': {e}")
        return None

tam_e = getattr(configuracio, "TAMANO_ENEMIGO", 35)

sprites_enemigos = {
    0: cargar_sprite_enemigo_individual("enemigo1 (1).png", tam_e),
    1: cargar_sprite_enemigo_individual("enemigo(2).png", tam_e),
    2: cargar_sprite_enemigo_individual("enemigo(3).png", tam_e)
}

# --- CARGA Y RECORTADO AUTOMÁTICO DE TEXTURAS DEL MAPA ---
def cargar_y_limpiar_textura(ruta):
    if os.path.exists(ruta):
        try:
            img = pygame.image.load(ruta)
            
            # Detectar y eliminar fondos blancos o transparencias sobrantes
            if img.get_alpha() is None:
                img = img.convert()
                if img.get_at((0, 0))[:3] == (255, 255, 255):
                    img.set_colorkey((255, 255, 255))
            else:
                img = img.convert_alpha()

            rect_limpio = img.get_bounding_rect()
            if rect_limpio.width > 0 and rect_limpio.height > 0:
                surf_limpia = pygame.Surface(rect_limpio.size, pygame.SRCALPHA)
                surf_limpia.blit(img, (0, 0), rect_limpio)
                return surf_limpia
            return img
        except Exception as e:
            print(f"Error al cargar la textura '{ruta}': {e}")
    return None

# Mapeo de texturas específicas para cada nivel (0: Nivel 1, 1: Nivel 2, 2: Nivel 3)
texturas_por_nivel = {
    0: {
        "suelo": cargar_y_limpiar_textura("suelo.png"),
        "fijo": cargar_y_limpiar_textura("bloque_solido.png") or cargar_y_limpiar_textura("fijo.png"),
        "destruible": cargar_y_limpiar_textura("romplibe.png") or cargar_y_limpiar_textura("destruible.png")
    },
    1: {
        "suelo": cargar_y_limpiar_textura("suelo.png"),
        "fijo": cargar_y_limpiar_textura("bloquesolido2.png"),
        "destruible": cargar_y_limpiar_textura("rompible2.png")
    },
    2: {
        "suelo": cargar_y_limpiar_textura("suelo.png"),
        "fijo": cargar_y_limpiar_textura("solido3.png") or cargar_y_limpiar_textura("bloquesolido3.png"),
        "destruible": cargar_y_limpiar_textura("rompible3.png")
    }
}

dict_texturas_escaladas = {}

# ==============================================================================
# 2. VARIABLES DE ESTADO Y DATOS DE NIVELES
# ==============================================================================
estado_juego = "MENU"
ejecutando = True

direccion_jugador = "ABAJO"
esta_caminando = False
indice_animacion = 0
tiempo_ultima_anim = 0
VELOCIDAD_ANIMACION = 120
tiempo_anim_bomba = 0

ANCHO_BOTON, ALTO_BOTON = 280, 60
rect_boton_inicio = pygame.Rect(0, 0, ANCHO_BOTON, ALTO_BOTON)

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
    
    tamano_casilla = min(ANCHO_BASE // total_cols, ALTO_BASE // total_filas)
    tamano_casilla = max(10, tamano_casilla)
    
    offset_x = (ANCHO_BASE - (total_cols * tamano_casilla)) // 2
    offset_y = (ALTO_BASE - (total_filas * tamano_casilla)) // 2
    
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
    
    tam_enemigo = getattr(configuracio, "TAMANO_ENEMIGO", 35)
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
    global direccion_jugador, esta_caminando, indice_animacion
    
    datos = DATOS_NIVELES[num_nivel]
    mapa_actual = [list(map(int, fila)) for fila in datos["mapa"]]
    color_suelo_actual = datos["suelo"]
    color_fijo_actual = datos["fijo"]
    color_destruible_actual = datos["destruible"]
    
    total_filas = len(mapa_actual)
    total_cols = len(mapa_actual[0]) if total_filas > 0 else configuracio.COLUMNAS
    rect_inicio = obtener_rect_casilla(1, 1, total_filas, total_cols)
    
    tam_j = getattr(configuracio, "TAMANO_JUGADOR", 36)
    jugador_rect = pygame.Rect(0, 0, tam_j, tam_j)
    jugador_rect.center = rect_inicio.center
    
    bombas = []
    explosiones = []
    enemigos = crear_enemigos(mapa_actual, datos["enemigos"])
    jugador_vivo = True
    nivel_completado = False
    
    direccion_jugador = "ABAJO"
    esta_caminando = False
    indice_animacion = 0

    cambiar_musica(RUTAS_MUSICA.get(num_nivel), forzar=True)


def matar_jugador():
    global jugador_vivo, musica_actual_pista
    if jugador_vivo:
        jugador_vivo = False
        pygame.mixer.music.stop()
        musica_actual_pista = None
        if sfx_game_over:
            sfx_game_over.play()

# Iniciar música del menú
cambiar_musica(RUTAS_MUSICA["MENU"])

# ==============================================================================
# 4. BUCLE PRINCIPAL
# ==============================================================================
while ejecutando:
    tiempo_actual = pygame.time.get_ticks()
    pos_raton_real = pygame.mouse.get_pos()

    escala_x = ancho_ventana / ANCHO_BASE
    escala_y = alto_ventana / ALTO_BASE
    escala = min(escala_x, escala_y) if min(escala_x, escala_y) > 0 else 1.0

    nuevo_ancho = int(ANCHO_BASE * escala)
    nuevo_alto = int(ALTO_BASE * escala)

    offset_x_win = (ancho_ventana - nuevo_ancho) // 2
    offset_y_win = (alto_ventana - nuevo_alto) // 2

    pos_raton_x = int((pos_raton_real[0] - offset_x_win) / escala) if escala > 0 else 0
    pos_raton_y = int((pos_raton_real[1] - offset_y_win) / escala) if escala > 0 else 0
    pos_raton = (pos_raton_x, pos_raton_y)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        if evento.type == pygame.VIDEORESIZE:
            ancho_ventana, alto_ventana = evento.w, evento.h
            pantalla = pygame.display.set_mode((ancho_ventana, alto_ventana), pygame.RESIZABLE)

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.display.iconify()

            if evento.key == pygame.K_F11:
                pantalla_completa = not pantalla_completa
                if pantalla_completa:
                    pantalla = pygame.display.set_mode((ancho_ventana, alto_ventana), pygame.FULLSCREEN | pygame.SCALED)
                else:
                    pantalla = pygame.display.set_mode((ancho_ventana, alto_ventana), pygame.RESIZABLE)

        if estado_juego == "MENU":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if rect_boton_inicio.collidepoint(pos_raton):
                    indice_nivel = 0
                    cargar_nivel(indice_nivel)
                    estado_juego = "JUGANDO"

            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    indice_nivel = 0
                    cargar_nivel(indice_nivel)
                    estado_juego = "JUGANDO"

        elif estado_juego == "JUGANDO" and evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r and not jugador_vivo:
                cargar_nivel(indice_nivel)
                
            if evento.key == pygame.K_RETURN and nivel_completado:
                if indice_nivel < len(DATOS_NIVELES) - 1:
                    indice_nivel += 1
                    cargar_nivel(indice_nivel)
                else:
                    indice_nivel = 0
                    estado_juego = "MENU"
                    cambiar_musica(RUTAS_MUSICA["MENU"], forzar=True)
            
            if evento.key == pygame.K_SPACE and jugador_vivo and not nivel_completado:
                total_filas = len(mapa_actual)
                total_cols = len(mapa_actual[0])
                
                tamano_casilla = min(ANCHO_BASE // total_cols, ALTO_BASE // total_filas)
                offset_x = (ANCHO_BASE - (total_cols * tamano_casilla)) // 2
                offset_y = (ALTO_BASE - (total_filas * tamano_casilla)) // 2
                
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
                    tiempo_anim_bomba = tiempo_actual + 300

    # ==============================================================================
    # LÓGICA Y DIBUJADO EN SUPERFICIE INTERNA
    # ==============================================================================
    if estado_juego == "MENU":
        superficie_juego.fill((25, 30, 50))
        
        rect_boton_inicio.center = (ANCHO_BASE // 2, ALTO_BASE // 2)
        
        txt_sombra = fuente_titulo.render("BOMBERMAN", True, (0, 0, 0))
        txt_titulo = fuente_titulo.render("BOMBERMAN", True, (241, 196, 15))
        superficie_juego.blit(txt_sombra, txt_sombra.get_rect(center=(ANCHO_BASE // 2 + 3, 113)))
        superficie_juego.blit(txt_titulo, txt_titulo.get_rect(center=(ANCHO_BASE // 2, 110)))
        
        hover = rect_boton_inicio.collidepoint(pos_raton)
        color_boton = (230, 126, 34) if hover else (211, 84, 0)
        color_borde = (255, 255, 255) if hover else (241, 196, 15)

        pygame.draw.rect(superficie_juego, color_boton, rect_boton_inicio, border_radius=12)
        pygame.draw.rect(superficie_juego, color_borde, rect_boton_inicio, 3, border_radius=12)

        txt_boton = fuente_subtitulo.render("INICIAR JUEGO", True, (255, 255, 255))
        superficie_juego.blit(txt_boton, txt_boton.get_rect(center=rect_boton_inicio.center))

        txt_tecla = fuente_subtitulo.render("Presiona ENTER, ESPACIO o Clic para empezar", True, (46, 204, 113))
        superficie_juego.blit(txt_tecla, txt_tecla.get_rect(center=(ANCHO_BASE // 2, ALTO_BASE // 2 + 80)))

        ctrl_1 = fuente_juego.render("Controles: WASD = Moverse | ESPACIO = Bomba", True, (200, 210, 225))
        ctrl_2 = fuente_juego.render("ESC = Minimizar | F11 = Pantalla Completa | R = Reiniciar", True, (200, 210, 225))
        superficie_juego.blit(ctrl_1, ctrl_1.get_rect(center=(ANCHO_BASE // 2, ALTO_BASE - 70)))
        superficie_juego.blit(ctrl_2, ctrl_2.get_rect(center=(ANCHO_BASE // 2, ALTO_BASE - 35)))

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

            if teclas[pygame.K_a]:
                dx -= vel_jugador
                direccion_jugador = "IZQUIERDA"
            elif teclas[pygame.K_d]:
                dx += vel_jugador
                direccion_jugador = "DERECHA"

            if teclas[pygame.K_w]:
                dy -= vel_jugador
                direccion_jugador = "ARRIBA"
            elif teclas[pygame.K_s]:
                dy += vel_jugador
                direccion_jugador = "ABAJO"

            esta_caminando = (dx != 0 or dy != 0)

            if esta_caminando and tiempo_actual - tiempo_ultima_anim > VELOCIDAD_ANIMACION:
                indice_animacion += 1
                tiempo_ultima_anim = tiempo_actual

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
                    matar_jugador()

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
                if sfx_bomba:
                    sfx_bomba.play()

        for bomba in bombas_a_eliminar:
            bombas.remove(bomba)

        explosiones = [exp for exp in explosiones if tiempo_actual - exp['tiempo'] < duracion_explosion]

        enemigos_a_eliminar = []
        for exp in explosiones:
            for llama in exp['llamas']:
                if jugador_vivo and jugador_rect.colliderect(llama):
                    matar_jugador()
                
                for enemigo in enemigos:
                    if enemigo['rect'].colliderect(llama) and enemigo not in enemigos_a_eliminar:
                        enemigos_a_eliminar.append(enemigo)

        for enemigo in enemigos_a_eliminar:
            enemigos.remove(enemigo)

        if jugador_vivo and len(enemigos) == 0:
            nivel_completado = True

        superficie_juego.fill((20, 24, 32))
        
        tamano_casilla = min(ANCHO_BASE // total_cols, ALTO_BASE // total_filas)
        offset_x = (ANCHO_BASE - (total_cols * tamano_casilla)) // 2
        offset_y = (ALTO_BASE - (total_filas * tamano_casilla)) // 2
        
        # Selección de texturas según el nivel actual
        dict_tex_nivel = texturas_por_nivel.get(indice_nivel, texturas_por_nivel[0])

        if dict_texturas_escaladas.get("tamano") != tamano_casilla or dict_texturas_escaladas.get("nivel") != indice_nivel:
            dict_texturas_escaladas = {
                "tamano": tamano_casilla,
                "nivel": indice_nivel,
                "suelo": pygame.transform.scale(dict_tex_nivel["suelo"], (tamano_casilla, tamano_casilla)) if dict_tex_nivel.get("suelo") else None,
                "fijo": pygame.transform.scale(dict_tex_nivel["fijo"], (tamano_casilla, tamano_casilla)) if dict_tex_nivel.get("fijo") else None,
                "destruible": pygame.transform.scale(dict_tex_nivel["destruible"], (tamano_casilla, tamano_casilla)) if dict_tex_nivel.get("destruible") else None
            }

        color_fuego = getattr(configuracio, "COLOR_FUEGO", (231, 76, 60))
        color_bomba = getattr(configuracio, "COLOR_BOMBA", (0, 0, 0))
        color_enemigo = getattr(configuracio, "COLOR_ENEMIGO", (155, 89, 182))
        color_jugador = getattr(configuracio, "COLOR_JUGADOR", (241, 196, 15))

        # --- DIBUJO DE CASILLAS Y TEXTURAS DEL MAPA ---
        for fila_idx, fila in enumerate(mapa_actual):
            for col_idx, casilla in enumerate(fila):
                rect = obtener_rect_casilla(fila_idx, col_idx, total_filas, total_cols)
                
                # Suelo base debajo de cada celda
                if dict_texturas_escaladas.get("suelo"):
                    superficie_juego.blit(dict_texturas_escaladas["suelo"], rect)
                else:
                    pygame.draw.rect(superficie_juego, color_suelo_actual, rect)

                # Bloque Sólido (1)
                if casilla == 1:
                    if dict_texturas_escaladas.get("fijo"):
                        superficie_juego.blit(dict_texturas_escaladas["fijo"], rect)
                    else:
                        pygame.draw.rect(superficie_juego, color_fijo_actual, rect)
                        pygame.draw.rect(superficie_juego, (0, 0, 0), rect, 2)

                # Bloque Rompible (2)
                elif casilla == 2:
                    if dict_texturas_escaladas.get("destruible"):
                        superficie_juego.blit(dict_texturas_escaladas["destruible"], rect)
                    else:
                        pygame.draw.rect(superficie_juego, color_destruible_actual, rect)
                        pygame.draw.rect(superficie_juego, (100, 50, 20), rect, 2)

        # --- DIBUJO DE EXPLOSIONES ---
        for exp in explosiones:
            tiempo_transcurrido = tiempo_actual - exp['tiempo']
            if frames_explosion:
                progreso = min(1.0, max(0.0, tiempo_transcurrido / duracion_explosion))
                idx_frame = int(progreso * (len(frames_explosion) - 1))
                frame_actual_exp = frames_explosion[idx_frame]

                for llama in exp['llamas']:
                    img_exp_esc = pygame.transform.scale(frame_actual_exp, (llama.width, llama.height))
                    superficie_juego.blit(img_exp_esc, llama)
            else:
                for llama in exp['llamas']:
                    pygame.draw.rect(superficie_juego, color_fuego, llama)

        # --- DIBUJO DE BOMBA ---
        for bomba in bombas:
            if sprite_bomba:
                rect_b_img = sprite_bomba.get_rect(center=bomba['rect'].center)
                superficie_juego.blit(sprite_bomba, rect_b_img)
            else:
                pygame.draw.circle(superficie_juego, color_bomba, bomba['rect'].center, min(bomba['rect'].width, bomba['rect'].height) // 3)

        # --- DIBUJO DE ENEMIGOS ---
        dict_enemigo_actual = sprites_enemigos.get(indice_nivel)
        for enemigo in enemigos:
            if abs(enemigo['dx']) >= abs(enemigo['dy']):
                dir_e = "DERECHA" if enemigo['dx'] > 0 else "IZQUIERDA"
            else:
                dir_e = "ABAJO" if enemigo['dy'] > 0 else "ARRIBA"

            if dict_enemigo_actual is not None:
                sprite_enemigo = dict_enemigo_actual.get(dir_e, dict_enemigo_actual.get("ABAJO"))
                superficie_juego.blit(sprite_enemigo, enemigo['rect'])
            else:
                pygame.draw.rect(superficie_juego, color_enemigo, enemigo['rect'])

        # --- DIBUJO DEL JUGADOR ---
        if jugador_vivo:
            if sprites_cargados:
                if nivel_completado:
                    idx_vic = (tiempo_actual // 150) % len(ANIM_VICTORIA)
                    frame_actual = ANIM_VICTORIA[idx_vic]
                elif tiempo_actual < tiempo_anim_bomba:
                    frame_actual = FRAME_BOMBA
                else:
                    if direccion_jugador == "ARRIBA":
                        lista_frames = ANIM_ARRIBA
                    elif direccion_jugador == "DERECHA":
                        lista_frames = ANIM_DERECHA
                    elif direccion_jugador == "IZQUIERDA":
                        lista_frames = ANIM_IZQUIERDA
                    else:
                        lista_frames = ANIM_ABAJO

                    frame_actual = lista_frames[indice_animacion % len(lista_frames)] if esta_caminando else lista_frames[0]

                superficie_juego.blit(frame_actual, jugador_rect)
            else:
                pygame.draw.rect(superficie_juego, color_jugador, jugador_rect)

        txt_nivel = fuente_juego.render(f"Nivel {indice_nivel + 1}", True, (255, 255, 255))
        superficie_juego.blit(txt_nivel, (15, 10))

        if nivel_completado:
            es_ultimo = (indice_nivel == len(DATOS_NIVELES) - 1)
            msg_principal = "¡JUEGO COMPLETADO!" if es_ultimo else f"¡NIVEL {indice_nivel + 1} SUPERADO!"
            msg_sub = "ENTER: Volver al Menú" if es_ultimo else "ENTER: Siguiente Nivel"
            
            txt_1 = fuente_subtitulo.render(msg_principal, True, (46, 204, 113))
            txt_2 = fuente_juego.render(msg_sub, True, (255, 255, 255))
            
            s = pygame.Surface((480, 90))
            s.set_alpha(220)
            s.fill((0, 0, 0))
            
            superficie_juego.blit(s, (ANCHO_BASE // 2 - 240, ALTO_BASE // 2 - 45))
            superficie_juego.blit(txt_1, txt_1.get_rect(center=(ANCHO_BASE // 2, ALTO_BASE // 2 - 15)))
            superficie_juego.blit(txt_2, txt_2.get_rect(center=(ANCHO_BASE // 2, ALTO_BASE // 2 + 20)))

        elif not jugador_vivo:
            txt_game_over = fuente_subtitulo.render("¡HAS MUERTO! Presiona R", True, (231, 76, 60))
            
            s = pygame.Surface((380, 60))
            s.set_alpha(200)
            s.fill((0, 0, 0))
            
            superficie_juego.blit(s, (ANCHO_BASE // 2 - 190, ALTO_BASE // 2 - 30))
            superficie_juego.blit(txt_game_over, txt_game_over.get_rect(center=(ANCHO_BASE // 2, ALTO_BASE // 2)))

    # ==============================================================================
    # ESCALADO Y BLIT EN PANTALLA PRINCIPAL
    # ==============================================================================
    superficie_escalada = pygame.transform.scale(superficie_juego, (nuevo_ancho, nuevo_alto))
    
    pantalla.fill((10, 10, 15))
    pantalla.blit(superficie_escalada, (offset_x_win, offset_y_win))

    pygame.display.flip()
    reloj.tick(getattr(configuracio, "FPS", 60))

pygame.quit()
sys.exit()