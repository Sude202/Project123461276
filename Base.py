import pygame
import random
import math
import time
import os
import sys

storage_time = []
storage_points = []

START_SIZE = 25, 25
SIZE = 20, 20
SIZE_ENEMY = 30, 30
BOOST_RADIUS = round(15 * math.sqrt(2))
S_EXP = 5, 5
WIND_S = WIDTH_S, HEIGHT_S  = 800, 600
FPS = 120

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
main_ = pygame.sprite.Group()
exp = pygame.sprite.Group()
boost = pygame.sprite.Group()
SCORE = 0
IS_PROTECTED = 0

def load_image(name):
    fullname = os.path.join(name)
    image = pygame.image.load(fullname)
    return image


class Main(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.Surface(SIZE)
        self.image.fill(pygame.Color("#760be0"))
        self.rect  = self.image.get_rect()
        self.rect.x = WIDTH_S / 2 - SIZE[0] / 2
        self.rect.y = HEIGHT_S / 2 - SIZE[1] / 2
        self.image = self.image.convert_alpha()

    def update(self):
        global IS_PROTECTED
        if WIDTH_S >  pygame.mouse.get_pos()[0] + SIZE[0] / 2\
                and pygame.mouse.get_pos()[0] - SIZE[0] / 2 > 0\
                and HEIGHT_S > pygame.mouse.get_pos()[1] + SIZE[1] / 2\
                and pygame.mouse.get_pos()[1] - SIZE[1] / 2 > 0:
            self.rect.x = pygame.mouse.get_pos()[0] - SIZE[0] // 2
            self.rect.y = pygame.mouse.get_pos()[1] - SIZE[1] // 2
        if pygame.sprite.spritecollideany(self, enemies) and IS_PROTECTED == 1:
            IS_PROTECTED = 0
            pygame.sprite.spritecollide(self, enemies, True)
        if pygame.sprite.spritecollideany(self, enemies) and IS_PROTECTED == 0:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.Surface(SIZE_ENEMY)
        self.image = self.image.convert_alpha()
        self.image.fill(pygame.Color("#290440"))
        self.rect = self.image.get_rect()
        self.vars = list(range(1, 5))
        self.start = random.choice(self.vars)
        self.vars.pop(self.start - 1)
        self.end = random.choice(self.vars)
        self.x0, self.y0 = self.first_cords()
        self.x1, self.y1 = self.end_cords()
        self.rect.x, self.rect.y = self.x0, self.y0
        self.speed = 3
        self.trajectory()

    def first_cords(self):
        if self.start % 2:
            if self.start == 1:
                return random.randint(0, WIDTH_S - SIZE_ENEMY[0]), 0
            return random.randint(0, WIDTH_S - SIZE_ENEMY[0]), HEIGHT_S - SIZE_ENEMY[1]
        else:
            if self.start == 4:
                return 0, random.randint(0, HEIGHT_S - SIZE_ENEMY[1])
            return WIDTH_S - SIZE_ENEMY[0], random.randint(0, HEIGHT_S - SIZE_ENEMY[1])

    def end_cords(self):
        if self.end % 2:
            if self.end == 1:
                return random.randint(SIZE_ENEMY[0], WIDTH_S - SIZE_ENEMY[0]), 0
            return random.randint(SIZE_ENEMY[0], WIDTH_S - SIZE_ENEMY[0]), HEIGHT_S - SIZE_ENEMY[1]
        else:
            if self.end == 4:
                return 0, random.randint(0, HEIGHT_S - SIZE_ENEMY[1])
            return WIDTH_S - SIZE_ENEMY[0], random.randint(0, HEIGHT_S - SIZE_ENEMY[1])

    def trajectory(self):
        self.v1 = pygame.math.Vector2(self.x1 - self.x0, self.y1 - self.y0)
        self.v2 = pygame.math.Vector2(0 - self.x0, 0 - self.y0)
        try:
            self.cos = (self.v1 * self.v2) / (self.v1.length() * self.v2.length())
        except Exception:
            self.cos = 0
        try:
            self.alfa = math.degrees(math.acos(self.cos))
        except Exception:
            self.alfa = 60
        self.vx = self.speed * abs(self.cos)
        self.vy = self.speed * (1 - self.cos ** 2) ** 0.5
        if self.x0 > self.x1:
            self.vx *= -1
        if self.y0 > self.y1:
            self.vy *= -1
        self.image = pygame.transform.rotate(self.image, self.alfa)

    def update(self):
        try:
            self.rect = self.rect.move( self.vx, self.vy)
        except Exception:
            self.kill()
        if self.rect[0] + SIZE_ENEMY[0] + 2 < 0 or self.rect[0] - SIZE_ENEMY[0] - 2 > WIDTH_S or\
                self.rect[1] + SIZE_ENEMY[1] + 2 < 0 or self.rect[1] - SIZE_ENEMY[1] - 2 > HEIGHT_S:
            self.kill()


class EXP(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.Surface(S_EXP)
        self.image.fill(pygame.Color("yellow"))
        self.image = self.image.convert_alpha()
        self.image = pygame.transform.rotate(self.image, 45)
        self.rect  = self.image.get_rect()
        self.rect.x = random.randint(S_EXP[0], WIDTH_S - S_EXP[0] + 1)
        self.rect.y = random.randint(S_EXP[1], HEIGHT_S - S_EXP[1] + 1)

    def update(self):
        global SCORE
        if pygame.sprite.spritecollideany(self, main_):
            SCORE += 1
            self.kill()
            EXP(all_sprites, exp)


class Boost(Enemy):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.Surface((BOOST_RADIUS * 2, BOOST_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, pygame.Color("#00c4ff"),
                           (BOOST_RADIUS, BOOST_RADIUS), BOOST_RADIUS, int(BOOST_RADIUS))
        pygame.draw.circle(self.image, pygame.Color("#0084ff"),
                           (BOOST_RADIUS, BOOST_RADIUS), BOOST_RADIUS, 5)
        self.rect = self.image.get_rect()
        self.vars = list(range(1, 5))
        self.start = random.choice(self.vars)
        self.vars.pop(self.start - 1)
        self.end = random.choice(self.vars)
        self.x0, self.y0 = self.first_cords()
        self.x1, self.y1 = self.end_cords()
        self.rect.x, self.rect.y = self.x0, self.y0
        self.speed = 4
        self.trajectory()

    def first_cords(self):
        if self.start % 2:
            if self.start == 1:
                return random.randint(0, WIDTH_S - 2 * BOOST_RADIUS), 0
            return random.randint(0, WIDTH_S - 2 * BOOST_RADIUS), HEIGHT_S - 2 * BOOST_RADIUS
        else:
            if self.start == 4:
                return 0, random.randint(0, HEIGHT_S - 2 * BOOST_RADIUS)
            return WIDTH_S - 2 * BOOST_RADIUS, random.randint(0, HEIGHT_S - 2 * BOOST_RADIUS)

    def end_cords(self):
        if self.end % 2:
            if self.end == 1:
                return random.randint(2 * BOOST_RADIUS, WIDTH_S - 2 * BOOST_RADIUS), 0
            return random.randint(2 * BOOST_RADIUS, WIDTH_S - 2 * BOOST_RADIUS), HEIGHT_S - 2 * BOOST_RADIUS
        else:
            if self.end == 4:
                return 0, random.randint(0, HEIGHT_S - 2 * BOOST_RADIUS)
            return WIDTH_S - 2 * BOOST_RADIUS, random.randint(0, HEIGHT_S - 2 * BOOST_RADIUS)

    def trajectory(self):
        self.v1 = pygame.math.Vector2(self.x1 - self.x0, self.y1 - self.y0)
        self.v2 = pygame.math.Vector2(0 - self.x0, 0 - self.y0)
        try:
            self.cos = (self.v1 * self.v2) / (self.v1.length() * self.v2.length())
        except Exception:
            self.cos = 0
        self.alfa = math.degrees(math.acos(self.cos))
        self.vx = self.speed * abs(self.cos)
        self.vy = self.speed * (1 - self.cos ** 2) ** 0.5
        if self.x0 > self.x1:
            self.vx *= -1
        if self.y0 > self.y1:
            self.vy *= -1

    def update(self):
        global IS_PROTECTED
        self.rect = self.rect.move(round(self.vx, 3), round(self.vy, 3))
        if self.rect[0] + 2 * BOOST_RADIUS + 2 < 0 or self.rect[0] - 2 * BOOST_RADIUS - 2 > WIDTH_S or\
                self.rect[1] + 2 * BOOST_RADIUS + 2 < 0 or self.rect[1] - 2 * BOOST_RADIUS - 2 > HEIGHT_S:
            self.kill()
        if pygame.sprite.spritecollideany(self, main_):
            IS_PROTECTED = 1
            self.kill()


def close():
    pygame.quit()
    sys.exit()


class Start(pygame.sprite.Sprite):
    image = load_image("start.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Start.image
        self.image = pygame.transform.scale2x(pygame.transform.scale2x(self.image))
        self.rect = self.image.get_rect()
        self.rect.x = 350
        self.rect.y = 250

    def update(self, *args):
        global S
        if args and self.rect.collidepoint(args[0].pos):
            S = 1


class Restart(pygame.sprite.Sprite):
    image = load_image("restart.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Restart.image
        self.image = pygame.transform.scale2x(pygame.transform.scale2x(self.image))
        self.rect = self.image.get_rect()
        self.rect.x = 350
        self.rect.y = 250

    def update(self, *args):
        global S
        if args and self.rect.collidepoint(args[0].pos):
            S = 1


class Exit(pygame.sprite.Sprite):
    image = load_image("exit.png")

    def __init__(self,x, y,  *group):
        super().__init__(*group)
        self.image = Exit.image
        self.image = pygame.transform.scale2x(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        global S
        if args and self.rect.collidepoint(args[0].pos):
            S = -1


S = 0
def start_screen():
    start = pygame.sprite.Group()
    exit = pygame.sprite.Group()
    screen.fill((255, 255, 255))
    Start(start)
    Exit(WIDTH_S - 290, 275, exit)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                start.update(event)
                exit.update(event)
                if S == 1:
                    return
                if S == -1:
                    running = False
        start.draw(screen)
        exit.draw(screen)
        pygame.display.flip()
    close()


def main():
    WAIT = 0
    cause = 0
    global seconds
    seconds = 0
    EXP_PER_SCREEN = 50

    FONT = pygame.font.SysFont(None, 36)

    running = True

    date_start = time.time()
    clock = pygame.time.Clock()

    for i in range(EXP_PER_SCREEN):
        EXP(all_sprites, exp)
    Main(all_sprites, main_)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not WAIT % 6:
            Enemy(all_sprites, enemies)
        if not WAIT % 40 and WAIT != 0 and IS_PROTECTED != 1:
            Boost(all_sprites, boost)
        if IS_PROTECTED:
            for i in boost:
                i.kill()
        if not any(main_):
            running = False
            cause = 1

        screen.fill(pygame.Color('#867491'))
        all_sprites.draw(screen)
        WAIT += 1

        enemies.update()
        boost.update()
        exp.update()
        main_.update()

        date_cur = time.time()
        seconds = str(round(date_cur - date_start, 2))

        screen.blit(FONT.render(str(SCORE), True, (0, 0, 0)), (5, 5))
        screen.blit(FONT.render(seconds, True, (0, 0, 0)), (5, 41))
        pygame.draw.rect(screen, pygame.SRCALPHA, pygame.Rect((0, 0), (100, 72)), 4)

        pygame.display.flip()
        clock.tick(FPS)
    for i in all_sprites:
        i.kill()
    if cause:
        return
    close()


def lose():
    storage_time.append(float(seconds))
    storage_points.append(SCORE)
    FONT = pygame.font.SysFont(None, 52)
    screen.fill((255, 255, 255))
    restart = pygame.sprite.Group()
    exit = pygame.sprite.Group()
    Restart(restart)
    Exit(100, 100, exit)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                restart.update(event)
                exit.update(event)
                if S == 1:
                    return True
                if S == -1:
                    running = False
        restart.draw(screen)
        exit.draw(screen)
        screen.blit(FONT.render(f'SCORE: {str(SCORE)}', True,
                                (0, 0, 0)), (300, 150))
        screen.blit(FONT.render(f'TIME: {seconds}s', True,
                                (0, 0, 0)), (300, 200))
        screen.blit(FONT.render(f'MAX SCORE: {max(storage_points)}',
                                True, (0, 0, 0)), (300, 400))
        screen.blit(FONT.render(f'MAX TIME: {max(storage_time)}s',
                                True, (0, 0, 0)), (300, 450))
        pygame.display.flip()
    return False


running_all = True
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(WIND_S)
    start_screen()
    while running_all:
        main()
        S = 0
        running_all = lose()
        SCORE *= 0
