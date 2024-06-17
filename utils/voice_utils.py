import os
import pygame

voice_dir = os.environ.get('PATH_VOICE')

pygame.mixer.init()

def play_sound():

    if not pygame.mixer.get_busy():
        sound = pygame.mixer.Sound(f"{voice_dir}/turn_around_with_siren.mp3")
        sound.play()
    else:
        print("SPK is busy.")

if __name__ == "__main__":
    ...