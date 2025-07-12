import pygame
import os
import random

SCREEN_WIDTH = 450
SCREEN_HEIGHT = 700

BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "base.png")))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bg.png")))
BIRD_IMAGES = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird3.png")))
]
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "pipe.png")))

pygame.font.init()
SCORE_FONT = pygame.font.SysFont("Courier", 30, bold = True)



class Bird:
    IMAGES = BIRD_IMAGES
    # Bird animation
    MAX_ROTATION = 25
    ROTATION_SPEED = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.image_count = 0
        self.image = self.IMAGES[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        # Displacement calculate
        self.time += 1
        displacement = 1.5 * (self.time ** 2) + self.speed * self.time

        # Displacement limit
        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2

        self.y += displacement

        # Bird angle
        if displacement < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_SPEED

    def show(self, screen):
        self.image_count += 1

        # Define bird image
        if self.image_count < self.ANIMATION_TIME:
            self.image = self.IMAGES[0]
        elif self.image_count < self.ANIMATION_TIME * 2:
            self.image = self.IMAGES[1]
        elif self.image_count < self.ANIMATION_TIME * 3:
            self.image = self.IMAGES[2]
        elif self.image_count < self.ANIMATION_TIME * 4:
            self.image = self.IMAGES[1]
        elif self.image_count >= self.ANIMATION_TIME * 4 + 1:
            self.image = self.IMAGES[0]
            self.image_count = 0

        # Bird falling
        if self.angle <= -80:
            self.image = self.IMAGES[1]
            self.image_count = self.ANIMATION_TIME * 2

        # Show image
        image_rotation = pygame.transform.rotate(self.image, self.angle)
        center_position = self.image.get_rect(topleft = (self.x, self.y)).center
        rectangle = image_rotation.get_rect(center = center_position)
        screen.blit(image_rotation, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)



class Pipe:
    DISTANCE = 250
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_position = 0
        self.base_position = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BASE = PIPE_IMAGE
        self.passed = False
        self.define_height()

    def define_height(self):
        self.height = random.randrange(50, 340)
        self.top_position = self.height - self.PIPE_TOP.get_height()
        self.base_position = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    def show(self, screen):
        screen.blit(self.PIPE_TOP, (self.x, self.top_position))
        screen.blit(self.PIPE_BASE, (self.x, self.base_position))

    def colide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        base_mask = pygame.mask.from_surface(self.PIPE_BASE)

        top_distance = (self.x - bird.x, self.top_position - round(bird.y))
        base_distance = (self.x - bird.x, self.base_position - round(bird.y))

        top_colide = bird_mask.overlap(top_mask, top_distance)
        base_colide = bird_mask.overlap(base_mask, base_distance)

        if top_colide or base_colide:
            return True
        else:
            return False



class Base:
    SPEED = 5
    WIDTH = BASE_IMAGE.get_width()
    IMAGE = BASE_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def show(self, screen):
        screen.blit(self.IMAGE, (self.x1, self.y))
        screen.blit(self.IMAGE, (self.x2, self.y))



def show_game(screen, bird, pipes, base, score):
    screen.blit(BACKGROUND_IMAGE, (0, -150))
    for birdd in bird:
        birdd.show(screen)
    for pipe in pipes:
        pipe.show(screen)
    base.show(screen)

    text = SCORE_FONT.render(f"Score: {score}", 1, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH - 20 - text.get_width(), 20))

    pygame.display.update()



def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    bird = [Bird(180, 200)]
    pipes = [Pipe(700)]
    base = Base(640)
    score = 0
    clock = pygame.time.Clock()

    on = True

    while on:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for birdd in bird:
                        birdd.jump()

        for birdd in bird:
            birdd.move()
        base.move()

        add_pipe = False
        pipe_remove = []
        for pipe in pipes:
            for i, birdd in enumerate(bird):
                if pipe.colide(birdd):
                    bird.pop(i)
                if not pipe.passed and birdd.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                pipe_remove.append(pipe)

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))

        for pipe in pipe_remove:
            pipes.remove(pipe)

        for i, birdd in enumerate(bird):
            if (birdd.y + birdd.image.get_height()) > base.y or birdd.y < 0:
                bird.pop(i)

        show_game(screen, bird, pipes, base, score)



if __name__ == "__main__":
    main()
