 # boombeman.py
import sys
import pygame
import configuracio
import mapas

pygame.init()

pantalla = pygame.display.set_mode((configuracio.ANCHO, configuracio.ALTO))
pygame.display.set_caption("Bomberman - Multinivel con Paletas Dinámicas")

reloj = pygame.time.Clock()
ejecutando = True

# Estado dinámico inicial con las nuevas variables independientes
mapa_actual = mapas.MAPA_1
color_suelo_actual = configuracio.SUELO_M1
color_fijo_actual = configuracio.FIJO_M1
color_destruible_actual = configuracio.DESTRUIBLE_M1

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_1:
                mapa_actual = mapas.MAPA_1
                color_suelo_actual = configuracio.SUELO_M1
                color_fijo_actual = configuracio.FIJO_M1
                color_destruible_actual = configuracio.DESTRUIBLE_M1
                print("[SISTEMA] Conmutado a: Mapa 1 (Clásico)")
            elif evento.key == pygame.K_2:
                mapa_actual = mapas.MAPA_2
                color_suelo_actual = configuracio.SUELO_M2
                color_fijo_actual = configuracio.FIJO_M2
                color_destruible_actual = configuracio.DESTRUIBLE_M2
                print("[SISTEMA] Conmutado a: Mapa 2 (Mundo de Fuego)")
            elif evento.key == pygame.K_3:
                mapa_actual = mapas.MAPA_3
                color_suelo_actual = configuracio.SUELO_M3
                color_fijo_actual = configuracio.FIJO_M3
                color_destruible_actual = configuracio.DESTRUIBLE_M3
                print("[SISTEMA] Conmutado a: Mapa 3 (Mundo de Bosque)")
            
    # Dibujamos usando los colores actuales del estado mutante
    pantalla.fill(color_suelo_actual)
    
    margen_x = (configuracio.ANCHO - (configuracio.COLUMNAS * configuracio.TAMANO_BLOQUE)) // 2
    margen_y = (configuracio.ALTO - (len(mapa_actual) * configuracio.TAMANO_BLOQUE)) // 2
    
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

    pygame.display.flip()
    reloj.tick(configuracio.FPS)

pygame.quit()
sys.exit()


