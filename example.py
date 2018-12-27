import random
import traceback
from math import inf

import pygame
from pygame.locals import *

from vectors import Vector2D
from physics import PhysicsWorld, RigidBody

pygame.display.init()
pygame.font.init()
pygame.display.set_caption("Simple physics example")
default_font = pygame.font.Font(None, 24)
screen_size = (1280, 768)
game_surface = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()

world = PhysicsWorld()
world.add(
    RigidBody(100, 100, 100, 100, mass=inf),
    RigidBody(100, 100, screen_size[0] - 100, 100, mass=inf),
    RigidBody(100, 100, screen_size[0] - 100, screen_size[1] - 100, mass=inf),
    RigidBody(100, 100, 100, screen_size[1] - 100, mass=inf),
)
screen_center = Vector2D(screen_size) / 2
mouse_pos = screen_center


def get_input():
    mouse_buttons = pygame.mouse.get_pressed()
    global mouse_pos
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == QUIT:
            return False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                return False
        elif event.type == pygame.MOUSEBUTTONUP and mouse_buttons[0]:
            body = RigidBody(
                50, 50,
                screen_center.x, screen_center.y,
                angle=random.randint(0, 90)
            )
            world.add(body)
            body.velocity = Vector2D(mouse_pos) - screen_center
    return True


def draw():
    game_surface.fill((40, 40, 40))

    for body in world.bodies:
        body.draw(game_surface)
    pygame.draw.line(game_surface, (0, 255, 0), screen_center, mouse_pos, 2)

    game_surface.blit(default_font.render('Objects: {}'.format(len(world.bodies)), True, (255, 255, 255)), (0, 0))
    game_surface.blit(default_font.render('FPS: {0:.0f}'.format(clock.get_fps()), True, (255, 255, 255)), (0, 24))
    pygame.display.update()


def main():
    dt = 1 / 60
    while True:
        if not get_input():
            break
        world.update(dt)
        for body in world.bodies:
            if body.position.x < 0 or body.position.x > screen_size[0] or \
                    body.position.y < 0 or body.position.y > screen_size[1]:
                world.remove(body)
        draw()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        pygame.quit()
        input()
