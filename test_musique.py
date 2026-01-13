import pygame

pygame.init()
pygame.mixer.init()

try:
    pygame.mixer.music.load("ambiance.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    input("Musique en cours... Appuyez sur Entrée pour quitter")
except Exception as e:
    print("Erreur:", e)