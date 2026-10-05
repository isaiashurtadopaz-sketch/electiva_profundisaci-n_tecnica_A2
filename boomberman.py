 # boomberman.py
import sys
import pygame
import configuracio
import mapas

pygame.init()

pantalla = pygame.display.set_mode((configuracio.ANCHO, configuracio.ALTO))
pygame.display.set_caption("Bomberman - Prototipo con Explosiones")

reloj = pygame.time.Clock()
ejecutando = True

# Estado dinámico inicial
mapa_actual = mapas.MAPA_1
color_suelo_actual = configuracio.SUELO_M1
color_fijo_actual = configuracio.FIJO_M1
color_destruible_actual = configuracio.DESTRUIBLE_M1

# Margen para centrar el mapa
margen_x = (configuracio.ANCHO - (configuracio.COLUMNAS * configuracio.TAMANO_BLOQUE)) // 2
margen_y = (configuracio.ALTO - (len(mapa_actual) * configuracio.TAMANO_BLOQUE)) // 2

# Posición inicial del Jugador (Casilla Fila 1, Columna 1)
pos_x = margen_x + configuracio.TAMANO_BLOQUE + (configuracio.TAMANO_BLOQUE - configuracio.TAMANO_JUGADOR) // 2
pos_y = margen_y + configuracio.TAMANO_BLOQUE + (configuracio.TAMANO_BLOQUE - configuracio.TAMANO_JUGADOR) // 2

jugador_rect = pygame.Rect(pos_x, pos_y, configuracio.TAMANO_JUGADOR, configuracio.TAMANO_JUGADOR)

# Listas de estado para bombas y explosiones
bombas = []
explosiones = []

while ejecutando:
    tiempo_actual = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        if evento.type == pygame.KEYDOWN:
            # Cambio de mapas (1, 2, 3)
            if evento.key == pygame.K_1:
                mapa_actual = mapas.MAPA_1
                color_suelo_actual = configuracio.SUELO_M1
                color_fijo_actual = configuracio.FIJO_M1
                color_destruible_actual = configuracio.DESTRUIBLE_M1
            elif evento.key == pygame.K_2:
                mapa_actual = mapas.MAPA_2
                color_suelo_actual = configuracio.SUELO_M2
                color_fijo_actual = configuracio.FIJO_M2
                color_destruible_actual = configuracio.DESTRUIBLE_M2
            elif evento.key == pygame.K_3:
                mapa_actual = mapas.MAPA_3
                color_suelo_actual = configuracio.SUELO_M3
                color_fijo_actual = configuracio.FIJO_M3
                color_destruible_actual = configuracio.DESTRUIBLE_M3
            
            # Poner Bomba con ESPACIO
            if evento.key == pygame.K_SPACE:
                centro_x = jugador_rect.centerx - margen_x
                centro_y = jugador_rect.centery - margen_y
                col = centro_x // configuracio.TAMANO_BLOQUE
                fila = centro_y // configuracio.TAMANO_BLOQUE
                
                bomba_x = (col * configuracio.TAMANO_BLOQUE) + margen_x
                bomba_y = (fila * configuracio.TAMANO_BLOQUE) + margen_y
                
                nueva_bomba = pygame.Rect(bomba_x, bomba_y, configuracio.TAMANO_BLOQUE, configuracio.TAMANO_BLOQUE)
                if nueva_bomba not in [b['rect'] for b in bombas]:
                    bombas.append({
                        'rect': nueva_bomba,
                        'tiempo': tiempo_actual,
                        'col': col,
                        'fila': fila
                    })

    # --- LÓGICA DE EXPLOSIÓN Y DETONACIÓN ---
    bombas_a_eliminar = []
    for bomba in bombas:
        if tiempo_actual - bomba['tiempo'] >= configuracio.TIEMPO_BOMBA:
            bombas_a_eliminar.append(bomba)
            
            col_b = bomba['col']
            fila_b = bomba['fila']
            llamas = []
            
            # Fuego en el centro
            llamas.append(pygame.Rect(bomba['rect'].x, bomba['rect'].y, configuracio.TAMANO_BLOQUE, configuracio.TAMANO_BLOQUE))
            
            # Expansión en 4 direcciones (Arriba, Abajo, Izquierda, Derecha)
            direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for df, dc in direcciones:
                for i in range(1, configuracio.ALCANCE_BOMBA + 1):
                    f = fila_b + (df * i)
                    c = col_b + (dc * i)
                    
                    if 0 <= f < len(mapa_actual) and 0 <= c < configuracio.COLUMNAS:
                        casilla = mapa_actual[f][c]
                        x_llama = (c * configuracio.TAMANO_BLOQUE) + margen_x
                        y_llama = (f * configuracio.TAMANO_BLOQUE) + margen_y
                        
                        if casilla == 1:
                            # Muro indestructible: detiene el fuego
                            break
                        elif casilla == 2:
                            # Bloque destruible: lo rompe (vuelve 0) y detiene la onda expansiva
                            mapa_actual[f][c] = 0
                            llamas.append(pygame.Rect(x_llama, y_llama, configuracio.TAMANO_BLOQUE, configuracio.TAMANO_BLOQUE))
                            break
                        else:
                            # Suelo libre
                            llamas.append(pygame.Rect(x_llama, y_llama, configuracio.TAMANO_BLOQUE, configuracio.TAMANO_BLOQUE))

            explosiones.append({'llamas': llamas, 'tiempo': tiempo_actual})

    # Eliminar bombas detonadas
    for bomba in bombas_a_eliminar:
        bombas.remove(bomba)

    # Eliminar efectos de fuego expirados
    explosiones = [exp for exp in explosiones if tiempo_actual - exp['tiempo'] < configuracio.DURACION_EXPLOSION]

    # Controles WASD
    teclas = pygame.key.get_pressed()
    dx = 0
    dy = 0
    
    if teclas[pygame.K_a]: dx -= configuracio.VELOCIDAD_JUGADOR
    if teclas[pygame.K_d]: dx += configuracio.VELOCIDAD_JUGADOR
    if teclas[pygame.K_w]: dy -= configuracio.VELOCIDAD_JUGADOR
    if teclas[pygame.K_s]: dy += configuracio.VELOCIDAD_JUGADOR

    # Generar colisiones dinámicas con el mapa actual
    bloques_colision = []
    for fila_idx, fila in enumerate(mapa_actual):
        for col_idx, casilla in enumerate(fila):
            if casilla in (1, 2):
                x = (col_idx * configuracio.TAMANO_BLOQUE) + margen_x
                y = (fila_idx * configuracio.TAMANO_BLOQUE) + margen_y
                bloques_colision.append(pygame.Rect(x, y, configuracio.TAMANO_BLOQUE, configuracio.TAMANO_BLOQUE))

    # Colisión horizontal
    jugador_rect.x += dx
    for bloque in bloques_colision:
        if jugador_rect.colliderect(bloque):
            if dx > 0: jugador_rect.right = bloque.left
            if dx < 0: jugador_rect.left = bloque.right

    # Colisión vertical
    jugador_rect.y += dy
    for bloque in bloques_colision:
        if jugador_rect.colliderect(bloque):
            if dy > 0: jugador_rect.bottom = bloque.top
            if dy < 0: jugador_rect.top = bloque.bottom

    # --- RENDERIZADO ---
    pantalla.fill(color_suelo_actual)
    
    # Dibujar casillas del mapa
    for fila_idx, fila in enumerate(mapa_actual):
        for col_idx, casilla in enumerate(fila):
            x = (col_idx * configuracio.TAMANO_BLOQUE) + margen_x
            y = (fila_idx * configuracio.TAMANO_BLOQUE) + margen_y
            
            if casilla == 1:
                pygame.draw.rect(pantalla, color_fijo_actual, (x, y, configuracio.TAMANO_BLOQUE, configuracio.TAMANO_BLOQUE))
                pygame.draw.rect(pantalla, configuracio.COLOR_BORDE_NEGRO, (x, y, configuracio.TAMANO_BLOQUE, configuracio.TAMANO_BLOQUE), 2)
            elif casilla == 2:
                pygame.draw.rect(pantalla, color_destruible_actual, (x, y, configuracio.TAMANO_BLOQUE, configuracio.TAMANO_BLOQUE))
                pygame.draw.rect(pantalla, configuracio.COLOR_LINEA_CAJA, (x, y, configuracio.TAMANO_BLOQUE, configuracio.TAMANO_BLOQUE), 2)
                pygame.draw.line(pantalla, configuracio.COLOR_LINEA_CAJA, (x, y), (x + configuracio.TAMANO_BLOQUE, y + configuracio.TAMANO_BLOQUE), 2)
                pygame.draw.line(pantalla, configuracio.COLOR_LINEA_CAJA, (x + configuracio.TAMANO_BLOQUE, y), (x, y + configuracio.TAMANO_BLOQUE), 2)

    # Dibujar fuego de las explosiones
    for exp in explosiones:
        for llama in exp['llamas']:
            pygame.draw.rect(pantalla, configuracio.COLOR_FUEGO, llama)

    # Dibujar bombas activas
    for bomba in bombas:
        pygame.draw.circle(pantalla, configuracio.COLOR_BOMBA, bomba['rect'].center, configuracio.TAMANO_BLOQUE // 3)

    # Dibujar jugador
    pygame.draw.rect(pantalla, configuracio.COLOR_JUGADOR, jugador_rect)

    pygame.display.flip()
    reloj.tick(configuracio.FPS)

pygame.quit()
sys.exit()