import random

import pygame
from pygame import freetype
from pygame import mixer
import sys
import math
from os import listdir

description = "I'll show you a real man"


def main():
    pygame.init()
    pygame.freetype.init()
    pygame.mixer.init()

    size = width, height = 768, 768

    screen = pygame.display.set_mode(size)
    # pygame.display.toggle_fullscreen()
    # pygame.display.set_icon()

    man = pygame.image.load("data/images/arealman.png")
    man_rect = man.get_rect()
    center = (round(width/2), round(height/2))
    man_rect.center = center
    man_size = [100, 100]
    man = pygame.transform.scale(man, man_size)
    man_rect.size = man_size

    apple = pygame.image.load("data/images/ObamaPrism.jpg")
    ap_size = [50, 50]
    apple = pygame.transform.scale(apple, ap_size)
    ap_rect = apple.get_rect()
    apples = []
    anum = 1
    for i in range(anum):
        ap = ap_rect.copy()
        ap.center = random.randint(0, width), random.randint(0, height)
        apples.append(ap)

    bangers_files = listdir("data/audio/bangers")
    bangers = []
    bang_channel = mixer.Channel(1)
    last_bang = None
    for bang in bangers_files:
        bangers.append(mixer.Sound("data/audio/bangers/" + bang))

    score_data = open("data/scores/scores.txt", "r+")
    scores = [int(x) for x in score_data.read().split("\n")]
    score = 0
    highscore = max(scores)
    score_counter = freetype.Font("data/fonts/GothamBook.ttf", 30)

    eat = mixer.Sound("data/audio/mario.mp3")
    sfx = mixer.Channel(0)

    color = 255, 100, 100

    w, a, s, d = pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d
    reset = pygame.K_r  # move back to middle
    can_reset = False

    clock = pygame.time.Clock()
    fps = 144
    time_queue = 0  # used to keep movement speed consistent throughout different fps

    updates_per_sec = 144  # updates per second
    speed = 1  # pixels per update
    ms_between = math.floor((1/updates_per_sec) * 1000)  # ms between each update

    fps_counter = pygame.freetype.Font("data/fonts/GothamBook.ttf", 15)
    fps_updates_per_sec = 2
    fps_ms_between = math.floor((1/fps_updates_per_sec) * 1000)
    fps_update_queue = 0
    last_fps = "FPS: " + str(fps)

    white = (255, 255, 255)

    def new_song(songs, last_song=None):
        current = songs[random.randint(0, len(songs)-1)]
        while current == last_song:
            current = songs[random.randint(0, len(songs)-1)]
        return current

    while True:
        move_dir = [0, 0]

        dt = clock.tick(fps)
        time_queue += dt  # - ms_between
        fps_update_queue += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("exiting...")
                score_data.write("\n" + str(score))
                score_data.close()
                sys.exit()

        key_down = pygame.key.get_pressed()

        # input
        while time_queue > ms_between:
            move_dir[1] -= speed if key_down[w] else 0
            move_dir[0] -= speed if key_down[a] else 0
            move_dir[1] += speed if key_down[s] else 0
            move_dir[0] += speed if key_down[d] else 0
            man_rect.center = center if key_down[reset] and can_reset else man_rect.center

            time_queue -= ms_between

        # fps
        text, rect = fps_counter.render(str(last_fps), white)
        while fps_update_queue > fps_ms_between:
            last_fps = "FPS: " + str(round(clock.get_fps()))
            text, rect = fps_counter.render(last_fps, white)
            fps_update_queue -= fps_ms_between

        man_rect.move_ip(move_dir)
        lx, ly = man_rect.topleft
        rx, ry = man_rect.bottomright

        # edge collision checking THIS IS DOG SHIT
        if not lx >= 0:
            man_rect.topleft = (0, ly)
            rx, ry = man_rect.bottomright
            lx, ly = man_rect.topleft
        if not ly >= 0:
            man_rect.topleft = (lx, 0)
            rx, ry = man_rect.bottomright
        if not rx <= width:
            man_rect.bottomright = (width, ry)
            rx, ry = man_rect.topright
        if not ry <= height:
            man_rect.bottomright = (rx, height)

        for ap in apples:
            if ap.colliderect(man_rect):
                score += 1
                if score > highscore: highscore = score
                sfx.play(eat)
                ap.center = random.randint(0, width), random.randint(0, height)
                while ap.colliderect(man_rect):
                    ap.center = random.randint(0, width), random.randint(0, height)

        score_text, srect = score_counter.render("Score: {} | High: {}".format(score, highscore), white)
        srect.center = round(width/2), 15

        screen.fill(color)
        screen.blit(man, man_rect)
        screen.blit(text, (5, 5))
        screen.blit(score_text, srect)

        for ap in apples:
            screen.blit(apple, ap)

        pygame.display.flip()

        if not bang_channel.get_busy():
            last_bang = new_song(bangers, last_bang)
            bang_channel.play(last_bang)


if __name__ == '__main__':
    main()
