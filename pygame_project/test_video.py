import pygame
from ffpyplayer.player import MediaPlayer
pygame.init()
screen = pygame.display.set_mode((1280, 720))
player = MediaPlayer('images/booting_animation.webm')
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
    
    frame, val = player.get_frame()
    if val == 'eof':
        running = False
    elif frame is not None:
        img, t = frame
        data = img.to_memoryview()[0]
        surf = pygame.image.frombuffer(data, img.get_size(), 'RGB')
        surf = pygame.transform.scale(surf, (1280, 720))
        screen.blit(surf, (0, 0))
        
    pygame.display.flip()
    clock.tick(60)
pygame.quit()