import sys
import pygame

pygame.init()

pantalla = pygame.display.set_mode((800,600))

pygame.display.set_caption("simulación de pantalla  -unidad 2")

reloj = pygame.time.Clock()

ejecutando = True

while  ejecutando:
    for  evento  in pygame.event.get():
        if evento.type ==pygame.QUIT:
            ejecutando = False

    pantalla.fill((166,132,128))
    pygame.draw.rect(pantalla, (0, 0, 255), (100, 100, 200, 100), 5)
    pygame.draw.circle(pantalla, (255, 255, 255), (400, 300), 50)
    pygame.display.flip()
    reloj.tick(60)


pygame.quit()
sys.exit()
#esquema de un mapa de 3 mocasff con figuras y desarrollado en el enorno  
#proxima clase 
