import pygame
from board import boards
import math
import random

pygame.init()

WIDTH, HEIGHT = 900, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font("freesansbold.ttf", 20)
level = boards
color = 'blue'
PI = math.pi
player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'pacman_images/{i}.png'), (35, 35)))
red_ghost_image = pygame.transform.scale(pygame.image.load(f'ghost_images/red.png'), (35, 35))
pink_ghost_image = pygame.transform.scale(pygame.image.load(f'ghost_images/pink.png'), (35, 35))
blue_ghost_image = pygame.transform.scale(pygame.image.load(f'ghost_images/blue.png'), (35, 35))
orange_ghost_image = pygame.transform.scale(pygame.image.load(f'ghost_images/orange.png'), (35, 35))
powerup_ghost_image = pygame.transform.scale(pygame.image.load(f'ghost_images/powerup.png'), (35, 35))
dead_ghost_image = pygame.transform.scale(pygame.image.load(f'ghost_images/dead.png'), (35, 35))
player_x = 425
player_y = 520
direction = 0
red_ghost_x = 56
red_ghost_y = 54
red_ghost_direction = 0
blue_ghost_x = 440
blue_ghost_y = 305
blue_ghost_direction = 2
pink_ghost_x = 440
pink_ghost_y = 345
pink_ghost_direction = 2
orange_ghost_x = 440
orange_ghost_y = 345
orange_ghost_direction = 2
counter = 0
flicker = False
turns_allowed = [False, False, False, False]
direction_command = 0
player_speed = 2
score = 0
start_ticks = pygame.time.get_ticks()
game_time = 0
powerup = False
power_count = 0
eat_ghost = [False, False, False, False]
target = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
red_ghost_dead = False
pink_ghost_dead = False
blue_ghost_dead = False
orange_ghost_dead = False
red_ghost_box = True
pink_ghost_box = True
blue_ghost_box = True
orange_ghost_box = True
ghost_speed = 2
normal_ghost_speed = 2
slowed_ghost_speed = 1
invisible_time = 0
invisible_duration = 10 * fps
ghost_respawn_timers = [0, 0, 0, 0]
ghost_respawn_duration = 5 * fps
player_visible = True
lives = 3
moving = False
startup_counter = 0
teleport_timer = 0
teleport_interval = 20 * fps
ghost_shoot_timers = {
    'red': 0,
    'pink': 0,
    'blue': 0,
    'orange': 0
}
ghost_respawn_timers = {
    'red': 0,
    'pink': 0,
    'blue': 0,
    'orange': 0
}
respawn_duration = 5 * fps
available_positions = []

class Projectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 5
        self.rect = pygame.Rect(self.x, self.y, 10, 10)

    def move(self):
        if self.direction == 0:
            self.x += self.speed
        elif self.direction == 1:
            self.x -= self.speed
        elif self.direction == 2:
            self.y -= self.speed
        elif self.direction == 3:
            self.y += self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        pygame.draw.rect(screen, 'red', self.rect)

    def is_off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()
        self.shoot_timer = 0


    def move_out_of_box(self):
        if self.in_box:
            self.direction = 3
            self.y_pos += self.speed
            if self.y_pos >= 305 and (440 <= self.x_pos <= 460):
                self.in_box = False



    def draw(self):
        if (not powerup and not self.dead) or (eat_ghost[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eat_ghost[self.id]:
            screen.blit(powerup_ghost_image, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_ghost_image, (self.x_pos, self.y_pos))
        ghost_rect = pygame.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect

    def check_collisions(self):
        num1 = ((HEIGHT - 67) // 32)
        num2 = (WIDTH // 30)
        num3 = 16
        self.turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            if level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
                self.turns[2] = True
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (self.in_box or self.dead)):
                self.turns[1] = True
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (self.in_box or self.dead)):
                self.turns[0] = True
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                self.turns[3] = True
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                self.turns[2] = True

            if self.direction in [2, 3]:
                if 6 <= self.center_x % num2 <= 15:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[2] = True
                if 6 <= self.center_y % num1 <= 15:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[0] = True

            if self.direction in [0, 1]:
                if 6 <= self.center_x % num2 <= 15:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[2] = True
                if 6 <= self.center_y % num1 <= 15:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 < self.x_pos < 550 and 370 < self.y_pos < 480:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box

    def shoot(self, timer_key):
        global ghost_shoot_timers
        if player_visible and not self.in_box and not self.dead:  # Ghosts don't shoot when in the box or dead
            if ghost_shoot_timers[timer_key] >= 7 * fps:
                projectile = Projectile(self.center_x, self.center_y, self.direction)
                projectiles.append(projectile)
                ghost_shoot_timers[timer_key] = 0
            else:
                ghost_shoot_timers[timer_key] += 1

    def red_ghost_move(self):
        if self.dead:
            return self.x_pos, self.y_pos, self.direction

        def can_turn_to_direction(direction):
            return self.turns[direction]

        def move():
            if self.direction == 0:
                self.x_pos += self.speed
            elif self.direction == 1:
                self.x_pos -= self.speed
            elif self.direction == 2:
                self.y_pos -= self.speed
            elif self.direction == 3:
                self.y_pos += self.speed

        def choose_new_direction():
            if self.direction == 0:
                if self.target[0] > self.x_pos and can_turn_to_direction(0):
                    return 0
                elif self.target[1] > self.y_pos and can_turn_to_direction(3):
                    return 3
                elif self.target[1] < self.y_pos and can_turn_to_direction(2):
                    return 2
                elif self.target[0] < self.x_pos and can_turn_to_direction(1):
                    return 1
                elif can_turn_to_direction(3):
                    return 3
                elif can_turn_to_direction(2):
                    return 2
                elif can_turn_to_direction(1):
                    return 1
            elif self.direction == 1:
                if self.target[0] < self.x_pos and can_turn_to_direction(1):
                    return 1
                elif self.target[1] > self.y_pos and can_turn_to_direction(3):
                    return 3
                elif self.target[1] < self.y_pos and can_turn_to_direction(2):
                    return 2
                elif self.target[0] > self.x_pos and can_turn_to_direction(0):
                    return 0
                elif can_turn_to_direction(3):
                    return 3
                elif can_turn_to_direction(2):
                    return 2
                elif can_turn_to_direction(0):
                    return 0
            elif self.direction == 2:
                if self.target[1] < self.y_pos and can_turn_to_direction(2):
                    return 2
                elif self.target[0] > self.x_pos and can_turn_to_direction(0):
                    return 0
                elif self.target[0] < self.x_pos and can_turn_to_direction(1):
                    return 1
                elif self.target[1] > self.y_pos and can_turn_to_direction(3):
                    return 3
                elif can_turn_to_direction(0):
                    return 0
                elif can_turn_to_direction(1):
                    return 1
                elif can_turn_to_direction(3):
                    return 3
            elif self.direction == 3:
                if self.target[1] > self.y_pos and can_turn_to_direction(3):
                    return 3
                elif self.target[0] > self.x_pos and can_turn_to_direction(0):
                    return 0
                elif self.target[0] < self.x_pos and can_turn_to_direction(1):
                    return 1
                elif self.target[1] < self.y_pos and can_turn_to_direction(2):
                    return 2
                elif can_turn_to_direction(0):
                    return 0
                elif can_turn_to_direction(1):
                    return 1
                elif can_turn_to_direction(2):
                    return 2
            return self.direction

        if self.in_box:
            self.move_out_of_box()
        else:
            if can_turn_to_direction(self.direction):
                move()
            else:
                self.direction = choose_new_direction()
                move()

        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30

        return self.x_pos, self.y_pos, self.direction

    def pink_ghost_move(self):
        if self.dead:
            return self.x_pos, self.y_pos, self.direction

        def can_turn(new_direction):
            return self.turns[new_direction]

        def move():
            if self.direction == 0:
                self.x_pos += self.speed
            elif self.direction == 1:
                self.x_pos -= self.speed
            elif self.direction == 2:
                self.y_pos -= self.speed
            elif self.direction == 3:
                self.y_pos += self.speed

        def choose_new_direction():
            if self.direction in [0, 1]:  # horizontal movement
                if self.target[1] > self.y_pos and can_turn(3):
                    return 3
                elif self.target[1] < self.y_pos and can_turn(2):
                    return 2
            elif self.direction in [2, 3]:  # vertical movement
                if self.target[0] > self.x_pos and can_turn(0):
                    return 0
                elif self.target[0] < self.x_pos and can_turn(1):
                    return 1
            return self.direction

        if self.in_box:
            self.move_out_of_box()
        else:
            if can_turn(self.direction):
                move()
            else:
                self.direction = choose_new_direction()
                if can_turn(self.direction):
                    move()
                else:
                    if self.direction == 0:
                        if can_turn(3):
                            self.direction = 3
                        elif can_turn(2):
                            self.direction = 2
                    elif self.direction == 1:
                        if can_turn(3):
                            self.direction = 3
                        elif can_turn(2):
                            self.direction = 2
                    elif self.direction == 2:
                        if can_turn(0):
                            self.direction = 0
                        elif can_turn(1):
                            self.direction = 1
                    elif self.direction == 3:
                        if can_turn(0):
                            self.direction = 0
                        elif can_turn(1):
                            self.direction = 1
                    move()

        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30

        return self.x_pos, self.y_pos, self.direction

    def blue_ghost_move(self):
        if self.dead:
            return self.x_pos, self.y_pos, self.direction

        def can_turn_to_direction(direction):
            return self.turns[direction]

        def move():
            if self.direction == 0:
                self.x_pos += self.speed
            elif self.direction == 1:
                self.x_pos -= self.speed
            elif self.direction == 2:
                self.y_pos -= self.speed
            elif self.direction == 3:
                self.y_pos += self.speed

        def choose_vertical_direction():
            if self.target[1] > self.y_pos and can_turn_to_direction(3):
                return 3
            elif self.target[1] < self.y_pos and can_turn_to_direction(2):
                return 2
            return self.direction

        def choose_horizontal_direction():
            if self.target[0] > self.x_pos and can_turn_to_direction(0):
                return 0  # right
            elif self.target[0] < self.x_pos and can_turn_to_direction(1):
                return 1  # left
            return self.direction

        if self.in_box:
            self.move_out_of_box()
        else:
            if self.direction in [0, 1]:
                if can_turn_to_direction(self.direction):
                    move()
                else:
                    self.direction = choose_vertical_direction()
                    if can_turn_to_direction(self.direction):
                        move()
                    else:
                        self.direction = choose_horizontal_direction()
                        move()
            elif self.direction in [2, 3]:
                if can_turn_to_direction(self.direction):
                    move()
                else:
                    self.direction = choose_horizontal_direction()
                    if can_turn_to_direction(self.direction):
                        move()
                    else:
                        self.direction = choose_vertical_direction()
                        move()

        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30

        return self.x_pos, self.y_pos, self.direction

    def orange_ghost_move(self):
        if self.dead:
            return self.x_pos, self.y_pos, self.direction

        def can_turn_to_direction(new_direction):
            return self.turns[new_direction]

        def move_in_current_direction():
            if self.direction == 0:
                self.x_pos += self.speed
            elif self.direction == 1:
                self.x_pos -= self.speed
            elif self.direction == 2:
                self.y_pos -= self.speed
            elif self.direction == 3:
                self.y_pos += self.speed

        def choose_new_direction():
            if self.direction == 0:
                if self.target[1] > self.y_pos and can_turn_to_direction(3):
                    return 3
                elif self.target[1] < self.y_pos and can_turn_to_direction(2):
                    return 2
                elif self.target[0] < self.x_pos and can_turn_to_direction(1):
                    return 1
            elif self.direction == 1:  # left
                if self.target[1] > self.y_pos and can_turn_to_direction(3):
                    return 3
                elif self.target[1] < self.y_pos and can_turn_to_direction(2):
                    return 2
                elif self.target[0] > self.x_pos and can_turn_to_direction(0):
                    return 0
            elif self.direction == 2:  # up
                if self.target[0] > self.x_pos and can_turn_to_direction(0):
                    return 0
                elif self.target[0] < self.x_pos and can_turn_to_direction(1):
                    return 1
                elif self.target[1] > self.y_pos and can_turn_to_direction(3):
                    return 3
            elif self.direction == 3:  # down
                if self.target[0] > self.x_pos and can_turn_to_direction(0):
                    return 0
                elif self.target[0] < self.x_pos and can_turn_to_direction(1):
                    return 1
                elif self.target[1] < self.y_pos and can_turn_to_direction(2):
                    return 2
            return self.direction

        if self.in_box:
            self.move_out_of_box()
        else:
            if can_turn_to_direction(self.direction):
                move_in_current_direction()
            else:
                self.direction = choose_new_direction()
                move_in_current_direction()

        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos = -30

        return self.x_pos, self.y_pos, self.direction


def teleport_pacman():
    global player_x, player_y, direction
    num1 = ((HEIGHT - 67) // 32)
    num2 = (WIDTH // 30)
    available_positions = []
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] in [1, 2]:
                available_positions.append((j * num2, i * num1))

    was_moving = direction is not None

    if available_positions:
        player_x, player_y = random.choice(available_positions)
        if was_moving:
            return

    direction = random.choice([0, 1, 2, 3])

def draw_misc():
    score_text = font.render(f"Score: {score}", True, 'white')
    screen.blit(score_text, (700, 740))
    time_passed = pygame.time.get_ticks() - start_ticks
    game_time = time_passed // 1000
    time_text = font.render(f"Time: {game_time}s", True, 'white')
    screen.blit(time_text, (50, 740))
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0], (25, 25)), (400 + i * 40, 740))

def check_collisions(score, power, power_count, eat_ghost, invisible_time):
    global red_ghost_x, red_ghost_y, pink_ghost_x, pink_ghost_y, blue_ghost_x, blue_ghost_y, orange_ghost_x, orange_ghost_y
    global red_ghost_box, pink_ghost_box, blue_ghost_box, orange_ghost_box
    global red_ghost_dead, pink_ghost_dead, blue_ghost_dead, orange_ghost_dead
    global lives

    num1 = (HEIGHT - 67) // 32
    num2 = WIDTH // 30
    if 0 < player_x < 870:
        center_y = player_y + 35 // 2 - 2
        center_x = player_x + 35 // 2
        if level[center_y // num1][center_x // num2] == 1:
            level[center_y // num1][center_x // num2] = 0
            score += 10
        if level[center_y // num1][center_x // num2] == 2:
            level[center_y // num1][center_x // num2] = 0
            score += 50
            power = True
            power_count = 0
            eat_ghost = [False, False, False, False]
            invisible_time = 10 * fps

        pacman_rect = pygame.Rect(player_x, player_y, 35, 35)
        ghost_rects = [
            pygame.Rect(red_ghost_x, red_ghost_y, 35, 35),
            pygame.Rect(pink_ghost_x, pink_ghost_y, 35, 35),
            pygame.Rect(blue_ghost_x, blue_ghost_y, 35, 35),
            pygame.Rect(orange_ghost_x, orange_ghost_y, 35, 35)
        ]

        for i, ghost_rect in enumerate(ghost_rects):
            if pacman_rect.colliderect(ghost_rect):
                if not player_visible and eat_ghost[i] == False:
                    score += 200
                    eat_ghost[i] = True
                    if i == 0:
                        red_ghost_x, red_ghost_y = get_random_position()
                        red_ghost_box = True
                        red_ghost_dead = True
                        ghost_respawn_timers['red'] = pygame.time.get_ticks()
                        print("Red ghost eaten. Setting dead flag and respawn timer.")
                    elif i == 1:
                        pink_ghost_x, pink_ghost_y = get_random_position()
                        pink_ghost_box = True
                        pink_ghost_dead = True
                        ghost_respawn_timers['pink'] = pygame.time.get_ticks()
                        print("Pink ghost eaten. Setting dead flag and respawn timer.")
                    elif i == 2:
                        blue_ghost_x, blue_ghost_y = get_random_position()
                        blue_ghost_box = True
                        blue_ghost_dead = True
                        ghost_respawn_timers['blue'] = pygame.time.get_ticks()
                        print("Blue ghost eaten. Setting dead flag and respawn timer.")
                    elif i == 3:
                        orange_ghost_x, orange_ghost_y = get_random_position()
                        orange_ghost_box = True
                        orange_ghost_dead = True
                        ghost_respawn_timers['orange'] = pygame.time.get_ticks()
                        print("Orange ghost eaten. Setting dead flag and respawn timer.")
                elif player_visible:
                    lives -= 1
                    print("Pacman collided with visible ghost. Losing a life.")
                    reset_positions()
                    break

    return score, power, power_count, eat_ghost, invisible_time

def get_random_position():
    num1 = (HEIGHT - 67) // 32
    num2 = WIDTH // 30
    available_positions = [(j * num2, i * num1) for i in range(len(level)) for j in range(len(level[i])) if level[i][j] == 1]
    return random.choice(available_positions) if available_positions else (0, 0)

def respawn_ghosts():
    current_time = pygame.time.get_ticks()
    global red_ghost_dead, pink_ghost_dead, blue_ghost_dead, orange_ghost_dead

    if red_ghost_dead and (current_time - ghost_respawn_timers['red']) >= respawn_duration:
        red_ghost_dead = False
        red_ghost_x, red_ghost_y = get_random_position()  # Возвращаем призрака на случайную позицию
        ghost_respawn_timers['red'] = 0  # Сброс таймера

    if pink_ghost_dead and (current_time - ghost_respawn_timers['pink']) >= respawn_duration:
        pink_ghost_dead = False
        pink_ghost_x, pink_ghost_y = get_random_position()  # Возвращаем призрака на случайную позицию
        ghost_respawn_timers['pink'] = 0  # Сброс таймера

    if blue_ghost_dead and (current_time - ghost_respawn_timers['blue']) >= respawn_duration:
        blue_ghost_dead = False
        blue_ghost_x, blue_ghost_y = get_random_position()  # Возвращаем призрака на случайную позицию
        ghost_respawn_timers['blue'] = 0  # Сброс таймера

    if orange_ghost_dead and (current_time - ghost_respawn_timers['orange']) >= respawn_duration:
        orange_ghost_dead = False
        orange_ghost_x, orange_ghost_y = get_random_position()  # Возвращаем призрака на случайную позицию
        ghost_respawn_timers['orange'] = 0  # Сброс таймера


def draw_board():
    num1 = ((HEIGHT - 67) // 32)
    num2 = (WIDTH // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3:
                pygame.draw.line(screen, color, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, color, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5:
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (num1 * 0.5)), num2, num1],
                                0, PI / 2, 3)
            if level[i][j] == 6:
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 + (num1 * 0.5)), num2, num1],
                                PI / 2, PI, 3)
            if level[i][j] == 7:
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 - (num1 * 0.4)), num2, num1],
                                PI, 3 * PI / 2, 3)
            if level[i][j] == 8:
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4) - 2), (i * num1 - (num1 * 0.4)), num2, num1],
                                3 * PI / 2, 2 * PI, 3)
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)

def draw_player():
    # Right - 0, Left - 1, Up - 2, Down - 3
    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))

def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT - 67) // 32
    num2 = (WIDTH // 30)
    num3 = 16
    if centerx // 30 < 29:
        if direction == 0:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 1:
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True
        if direction == 2:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True
        if direction == 3:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True

        if direction == 2 or direction == 3:
            if 6 <= centerx % num2 <= 15:
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
            if 6 <= centery % num1 <= 15:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 6 <= centerx % num2 <= 15:
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
            if 6 <= centery % num1 <= 15:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True

    return turns



def move_player(play_x, play_y):
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    elif direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    return play_x, play_y

def reset_positions():
    global player_x, player_y, direction, powerup, power_count, eat_ghost, invisible_time
    global red_ghost_x, red_ghost_y, red_ghost_direction
    global pink_ghost_x, pink_ghost_y, pink_ghost_direction
    global blue_ghost_x, blue_ghost_y, blue_ghost_direction
    global orange_ghost_x, orange_ghost_y, orange_ghost_direction
    global projectiles

    player_x = 425
    player_y = 520
    direction = 0

    powerup = False
    power_count = 0
    eat_ghost = [False, False, False, False]
    invisible_time = 0

    red_ghost_x = 56
    red_ghost_y = 54
    red_ghost_direction = 0
    pink_ghost_x = 440
    pink_ghost_y = 345
    pink_ghost_direction = 2
    blue_ghost_x = 440
    blue_ghost_y = 305
    blue_ghost_direction = 2
    orange_ghost_x = 440
    orange_ghost_y = 345
    orange_ghost_direction = 2

    projectiles.clear()

def handle_projectiles():
    global lives
    for projectile in projectiles:
        projectile.move()
        projectile.draw()
        if projectile.is_off_screen():
            projectiles.remove(projectile)
        if projectile.rect.colliderect(pygame.Rect(player_x, player_y, 35, 35)):
            lives -= 1
            projectiles.remove(projectile)
            reset_positions()

projectiles = []

def show_game_over():
    game_over_text = font.render("You Lost! Press SPACE to exit", True, 'white')
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    pygame.display.flip()

def show_victory(score):
    victory_text = font.render(f"You Win! Score: {score} Press SPACE to exit", True, 'white')
    screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - victory_text.get_height() // 2))
    pygame.display.flip()

run = True
game_over = False
victory = False

while run:
    timer.tick(fps)
    if not game_over and not victory:
        teleport_timer += 1
        if counter < 19:
            counter += 1
            if counter > 3:
                flicker = False
        else:
            counter = 0
            flicker = True
        if powerup and power_count < 600:
            power_count += 1
        elif powerup and power_count >= 600:
            power_count = 0
            powerup = False
            eat_ghost = [False, False, False, False]

        if invisible_time > 0:
            invisible_time -= 1
            player_visible = False
            ghost_speed = slowed_ghost_speed
        else:
            player_visible = True
            ghost_speed = normal_ghost_speed
        if teleport_timer >= teleport_interval:
            teleport_pacman()
            teleport_timer = 0

        screen.fill('black')
        draw_board()

        if player_visible:
            draw_player()

        red_ghost = Ghost(red_ghost_x, red_ghost_y, target[0], ghost_speed, red_ghost_image, red_ghost_direction,
                          red_ghost_dead, red_ghost_box, 0)
        pink_ghost = Ghost(pink_ghost_x, pink_ghost_y, target[1], ghost_speed, pink_ghost_image, pink_ghost_direction,
                           pink_ghost_dead, pink_ghost_box, 1)
        blue_ghost = Ghost(blue_ghost_x, blue_ghost_y, target[2], ghost_speed, blue_ghost_image, blue_ghost_direction,
                           blue_ghost_dead, blue_ghost_box, 2)
        orange_ghost = Ghost(orange_ghost_x, orange_ghost_y, target[3], ghost_speed, orange_ghost_image,
                             orange_ghost_direction, orange_ghost_dead, orange_ghost_box, 3)
        draw_misc()

        center_x = player_x + 35 // 2
        center_y = player_y + 35 // 2 - 2
        turns_allowed = check_position(center_x, center_y)
        player_x, player_y = move_player(player_x, player_y)
        red_ghost_x, red_ghost_y, red_ghost_direction = red_ghost.red_ghost_move()
        pink_ghost_x, pink_ghost_y, pink_ghost_direction = pink_ghost.pink_ghost_move()
        blue_ghost_x, blue_ghost_y, blue_ghost_direction = blue_ghost.blue_ghost_move()
        orange_ghost_x, orange_ghost_y, orange_ghost_direction = orange_ghost.orange_ghost_move()
        score, powerup, power_count, eat_ghost, invisible_time = check_collisions(score, powerup, power_count, eat_ghost, invisible_time)

        red_ghost.shoot('red')
        pink_ghost.shoot('pink')
        blue_ghost.shoot('blue')
        orange_ghost.shoot('orange')

        handle_projectiles()

        respawn_ghosts()

        if lives <= 0:
            game_over = True


        if all(level[row][col] != 1 and level[row][col] != 2 for row in range(len(level)) for col in range(len(level[row]))):
            victory = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    direction_command = 0
                if event.key == pygame.K_LEFT:
                    direction_command = 1
                if event.key == pygame.K_UP:
                    direction_command = 2
                if event.key == pygame.K_DOWN:
                    direction_command = 3
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT and direction_command == 0:
                    direction_command = direction
                if event.key == pygame.K_LEFT and direction_command == 1:
                    direction_command = direction
                if event.key == pygame.K_UP and direction_command == 2:
                    direction_command = direction
                if event.key == pygame.K_DOWN and direction_command == 3:
                    direction_command = direction

        if direction_command == 0 and turns_allowed[0]:
            direction = 0
        if direction_command == 1 and turns_allowed[1]:
            direction = 1
        if direction_command == 2 and turns_allowed[2]:
            direction = 2
        if direction_command == 3 and turns_allowed[3]:
            direction = 3

        if player_x > 900:
            player_x = -47
        elif player_x < -50:
            player_x = 897

        pygame.display.flip()
    elif game_over:
        show_game_over()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    run = False
    elif victory:
        show_victory(score)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    run = False

pygame.quit()