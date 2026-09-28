import sys
import pygame

pygame.init()

# 1. Configuración de la pantalla y entorno
pantalla = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Simulación de pantalla - Unidad 2")

reloj = pygame.time.Clock()
ejecutando = True

# 2. Matriz completa del mapa (0 = Suelo, 1 = Fijo, 2 = Destruible)
# Se escribe en una sola lista plana para asegurar el formato sin errores
mapa_datos = [
    1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,0,0,0,0,2,2,2,0,0,0,0,1,
    1,0,1,0,1,0,1,0,1,0,1,0,1,
    1,2,0,2,2,2,2,2,2,2,0,2,1,
    1,0,1,0,1,2,1,2,1,0,1,0,1,
    1,2,0,2,2,2,0,2,2,2,0,2,1,
    1,0,1,0,1,2,1,2,1,0,1,0,1,
    1,0,0,2,2,2,2,2,2,2,0,0,1,
    1,0,1,0,1,0,1,0,1,0,1,0,1,
    1,1,1,1,1,1,1,1,1,1,1,1,1
]

# Conversión de la lista plana en una cuadrícula real de 10 filas x 13 columnas
COLUMNAS = 13
mapa = [mapa_datos[i:i + COLUMNAS] for i in range(0, len(mapa_datos), COLUMNAS)]

# Tamaño de cada bloque en píxeles
TAMANO_BLOQUE = 60

# 3. Definición de colores
COLOR_SUELO = (166, 132, 128)        # Fondo original tuyo
COLOR_FIJO = (44, 62, 80)            # Gris oscuro para bloques fijos
COLOR_DESTRUIBLE = (229, 152, 102)    # Naranja/Marrón para cajas

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
    # Fondo de la pantalla
    pantalla.fill(COLOR_SUELO)
    
    # 4. Dibujar las figuras del mapa usando filas y columnas
    for fila_idx, fila in enumerate(mapa):
        for col_idx, casilla in enumerate(fila):
            x = col_idx * TAMANO_BLOQUE
            y = fila_idx * TAMANO_BLOQUE
            
            if casilla == 1:
                # Mosaico 1: Bloque Fijo (Gris con borde negro)
                pygame.draw.rect(pantalla, COLOR_FIJO, (x, y, TAMANO_BLOQUE, TAMANO_BLOQUE))
                pygame.draw.rect(pantalla, (0, 0, 0), (x, y, TAMANO_BLOQUE, TAMANO_BLOQUE), 2)
            elif casilla == 2:
                # Mosaico 2: Bloque Destruible (Caja con una cruz decorativa)
                pygame.draw.rect(pantalla, COLOR_DESTRUIBLE, (x, y, TAMANO_BLOQUE, TAMANO_BLOQUE))
                pygame.draw.rect(pantalla, (110, 44, 2), (x, y, TAMANO_BLOQUE, TAMANO_BLOQUE), 2)
                pygame.draw.line(pantalla, (110, 44, 2), (x, y), (x + TAMANO_BLOQUE, y + TAMANO_BLOQUE), 2)
                pygame.draw.line(pantalla, (110, 44, 2), (x + TAMANO_BLOQUE, y), (x, y + TAMANO_BLOQUE), 2)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()