import pygame
import random
import sys

pygame.init()

# WINDOW
WIDTH = 710
HEIGHT = 1600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Boss Game")

clock = pygame.time.Clock()

# FONTS
font = pygame.font.SysFont("arial", 35)
big_font = pygame.font.SysFont("arial", 70)

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 255)
RED = (255, 60, 60)
GREEN = (0, 200, 100)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)
PURPLE = (170, 0, 255)
ORANGE = (255, 170, 0)

def reset_game():
    global player_x, player_y
    global vel_y, on_ground
    global enemy_x, enemy_speed
    global boss_active, boss_x, boss_y
    global boss_hp
    global bullets
    global little_enemies
    global meteors
    global lasers
    global score, lives
    global game_over, win
    global facing
    global paused
    global shadow_mode
    global boss_dir
    global storm_active, storm_timer, last_triggered_score, storm_scores

    player_x = 100
    player_y = 380

    vel_y = 0
    on_ground = True

    facing = "right"

    enemy_x = WIDTH
    enemy_speed = 6

    boss_active = False

    boss_x = 650
    boss_y = 100

    boss_hp = 120
    boss_max_hp = 120

    bullets = []
    little_enemies = []
    meteors = []
    lasers = []

    score = 0  
    lives = 10

    game_over = False
    win = False
    paused = False
    shadow_mode = False
    boss_dir = 1
    
    # METEOR STORM VARIABLES
    storm_active = False
    storm_timer = 0
    last_triggered_score = -1
    
    # Select exactly 10 unique random scores between 1 and 98 for the meteor storms
    storm_scores = random.sample(range(1, 99), 10)

    return boss_max_hp

# PLAYER
player_w = 50
player_h = 50
player_speed = 7
jump_power = -17
gravity = 1

# ENEMY
enemy_y = 380

# BOSS
boss_w = 230
boss_h = 230

# BUTTONS
btn_y = 460
left_btn = pygame.Rect(20, btn_y, 110, 60)
right_btn = pygame.Rect(150, btn_y, 110, 60)
jump_btn = pygame.Rect(280, btn_y, 110, 60)
shoot_btn = pygame.Rect(420, btn_y, 120, 60)
pause_btn = pygame.Rect(560, btn_y, 120, 60)
restart_btn = pygame.Rect(300, 350, 230, 70)

move_left = False
move_right = False

# STARS
stars = []
for i in range(200):
    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(2, 4)
    ])

boss_max_hp = reset_game()
attack_timer = 0
running = True

while running:
    clock.tick(99)

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if pause_btn.collidepoint(x, y):
                paused = not paused

            if not game_over and not paused:
                if left_btn.collidepoint(x, y):
                    move_left = True
                if right_btn.collidepoint(x, y):
                    move_right = True
                if jump_btn.collidepoint(x, y):
                    if on_ground:
                        vel_y = jump_power
                        on_ground = False
                if shoot_btn.collidepoint(x, y):
                    if facing == "right":
                        bullets.append([player_x + player_w, player_y + 20, 1])
                    else:
                        bullets.append([player_x - 10, player_y + 20, -1])
            else:
                if restart_btn.collidepoint(x, y):
                    boss_max_hp = reset_game()
                    attack_timer = 0

        if event.type == pygame.MOUSEBUTTONUP:
            move_left = False
            move_right = False

    # GAME LOGIC
    if not game_over and not paused:
        # PLAYER MOVE
        if move_left:
            player_x -= player_speed
            facing = "left"
        if move_right:
            player_x += player_speed
            facing = "right"

        # LIMITS
        if player_x < 0: player_x = 0
        if player_x > WIDTH - player_w: player_x = WIDTH - player_w

        # GRAVITY
        vel_y += gravity
        player_y += vel_y
        if player_y >= 380:
            player_y = 380
            vel_y = 0
            on_ground = True

        # NORMAL ENEMY
        if not boss_active:
            enemy_x -= enemy_speed
            if enemy_x < -60:
                enemy_x = WIDTH + random.randint(100, 300)
                score += 1

        # RANDOM METEOR STORM LOGIC (BEFORE BOSS) - SET TO 10 TIMES
        if not boss_active:
            if score in storm_scores and score != last_triggered_score:
                storm_active = True
                storm_timer = 150  
                last_triggered_score = score

            if storm_active:
                storm_timer -= 1
                
                # Decreased frequency: spawns every 8 frames instead of 4 (fewer meteors)
                if storm_timer % 8 == 0:
                    meteors.append([random.randint(0, WIDTH), -50, random.randint(6, 12)])
                
                if storm_timer <= 0:
                    storm_active = False

        # START BOSS
        if score >= 99:
            boss_active = True
            enemy_x = WIDTH + 9999
            storm_active = False  

        # BULLETS MOVE
        for bullet in bullets:
            bullet[0] += bullet[2] * 15
        bullets = [b for b in bullets if -100 < b[0] < WIDTH + 100]

        player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
        enemy_rect = pygame.Rect(enemy_x, enemy_y, 50, 50)

        # NORMAL ENEMY DAMAGE
        if not boss_active and player_rect.colliderect(enemy_rect):
            lives -= 1
            enemy_x = WIDTH + random.randint(100, 300)
            if lives <= 0: game_over = True

        # BOSS ACTIVE LOGIC
        if boss_active:
            attack_timer += 1

            # BOSS MOVE
            boss_x += 4 * boss_dir
            if boss_x < 500: boss_dir = 1
            if boss_x > 760: boss_dir = -1

            # FOLLOW PLAYER
            if player_y < boss_y: boss_y -= 2
            if player_y > boss_y: boss_y += 2

            # SHADOW MODE
            shadow_mode = True if (attack_timer % 300 < 80) else False

            # FAST RANDOM LASERS
            if attack_timer % 35 == 0:
                lasers.clear() 
                lasers.append([
                    random.randint(0, WIDTH - 30),
                    0,
                    25,
                    HEIGHT,
                    random.choice([RED, ORANGE])
                ])

            # LITTLE ENEMIES
            if attack_timer % 120 == 0:
                for i in range(3):
                    little_enemies.append([WIDTH + random.randint(0, 300), 380, random.randint(7, 12)])

            # BOSS METEORS
            if attack_timer % 80 == 0:
                for i in range(4):
                    meteors.append([random.randint(0, WIDTH), -50, random.randint(7, 15)])

        # LASER DAMAGE
        for laser in lasers[:]:
            laser_rect = pygame.Rect(laser[0], laser[1], laser[2], laser[3])
            if player_rect.colliderect(laser_rect):
                lives -= 1
                if laser in lasers: lasers.remove(laser)
                if lives <= 0: game_over = True

        # LITTLE ENEMY MOVE
        for enemy in little_enemies[:]:
            enemy[0] -= enemy[2]
            enemy_rect2 = pygame.Rect(enemy[0], enemy[1], 40, 40)
            if player_rect.colliderect(enemy_rect2):
                lives -= 1
                if enemy in little_enemies: little_enemies.remove(enemy)
                if lives <= 0: game_over = True
            if enemy[0] < -100:
                if enemy in little_enemies: little_enemies.remove(enemy)

        # METEOR MOVE
        for meteor in meteors[:]:
            meteor[1] += meteor[2]
            meteor_rect = pygame.Rect(meteor[0], meteor[1], 35, 35)
            if player_rect.colliderect(meteor_rect):
                lives -= 1
                if meteor in meteors: meteors.remove(meteor)
                if lives <= 0: game_over = True
            elif meteor[1] > HEIGHT + 100:
                if meteor in meteors: meteors.remove(meteor)

        # BOSS HIT
        boss_rect = pygame.Rect(boss_x, boss_y, boss_w, boss_h)
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 15, 6)
            if boss_active and bullet_rect.colliderect(boss_rect):
                boss_hp -= 1
                if bullet in bullets: bullets.remove(bullet)
                if boss_hp <= 0:
                    win = True
                    game_over = True

    # ==================
    # DRAW SECTION
    # ==================
    screen.fill((15, 15, 30))

    # STARS
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[2])

    # GROUND
    pygame.draw.rect(screen, GREEN, (0, 430, WIDTH, 120))

    # PLAYER
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_w, player_h), border_radius=12)
    pygame.draw.circle(screen, WHITE, (player_x + 35, player_y + 15), 5)

    # GUN
    if facing == "right":
        pygame.draw.rect(screen, BLACK, (player_x + 40, player_y + 22, 25, 8))
    else:
        pygame.draw.rect(screen, BLACK, (player_x - 15, player_y + 22, 25, 8))

    # NORMAL ENEMY
    if not boss_active:
        pygame.draw.rect(screen, RED, (enemy_x, enemy_y, 50, 50), border_radius=12)

    # BOSS DRAW
    if boss_active:
        if shadow_mode:
            shadow_surface = pygame.Surface((boss_w, boss_h))
            shadow_surface.set_alpha(100)
            shadow_surface.fill((50, 0, 0))
            screen.blit(shadow_surface, (boss_x, boss_y))

        pygame.draw.rect(screen, PURPLE, (boss_x, boss_y, boss_w, boss_h), border_radius=25)
        pygame.draw.circle(screen, WHITE, (boss_x + 60, boss_y + 70), 15)
        pygame.draw.circle(screen, WHITE, (boss_x + 170, boss_y + 70), 15)

        # HP BAR
        bar_x, bar_y, bar_width, bar_height = 250, 15, 500, 40
        pygame.draw.rect(screen, BLACK, (bar_x - 4, bar_y - 4, bar_width + 8, bar_height + 8), border_radius=18)
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=15)
        
        current_width = (max(0, boss_hp) / boss_max_hp) * bar_width
        hp_color = GREEN
        if boss_hp <= 70: hp_color = ORANGE
        if boss_hp <= 30: hp_color = RED

        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, current_width, bar_height), border_radius=15)
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 4, border_radius=15)
        
        boss_name = font.render("ULTIMATE SHADOW KING", True, WHITE)
        screen.blit(boss_name, (260, 65))

    # BULLETS
    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW, (bullet[0], bullet[1], 15, 6), border_radius=4)

    # LITTLE ENEMIES
    for enemy in little_enemies:
        pygame.draw.rect(screen, RED, (enemy[0], enemy[1], 40, 40), border_radius=10)
        pygame.draw.circle(screen, WHITE, (enemy[0] + 12, enemy[1] + 12), 4)
        pygame.draw.circle(screen, WHITE, (enemy[0] + 28, enemy[1] + 12), 4)

    # METEORS
    for meteor in meteors:
        pygame.draw.circle(screen, ORANGE, (int(meteor[0]), int(meteor[1])), 20)

    # LASERS DRAW
    for laser in lasers:
        pygame.draw.rect(screen, laser[4], (laser[0], laser[1], laser[2], laser[3]))

    # UI BUTTONS
    pygame.draw.rect(screen, GRAY, left_btn, border_radius=20)
    pygame.draw.rect(screen, GRAY, right_btn, border_radius=20)
    pygame.draw.rect(screen, PURPLE, jump_btn, border_radius=20)
    pygame.draw.rect(screen, ORANGE, shoot_btn, border_radius=20)
    pygame.draw.rect(screen, RED, pause_btn, border_radius=20)

    screen.blit(font.render("LEFT", True, BLACK), (35, btn_y + 10))
    screen.blit(font.render("RIGHT", True, BLACK), (160, btn_y + 10))
    screen.blit(font.render("JUMP", True, BLACK), (290, btn_y + 10))
    screen.blit(font.render("SHOOT", True, BLACK), (420, btn_y + 10))
    screen.blit(font.render("PAUSE", True, BLACK), (565, btn_y + 10))

    # TEXT DETAILS
    screen.blit(font.render(f"Score: {score}", True, YELLOW), (20, 20))
    screen.blit(font.render(f"Lives: {lives}", True, WHITE), (20, 60))

    # METEOR STORM WARNING
    if storm_active:
        storm_text = font.render("WARNING: METEOR STORM ACTIVE!", True, ORANGE)
        screen.blit(storm_text, (WIDTH // 2 - 220, 80))

    if paused:
        screen.blit(big_font.render("PAUSED", True, WHITE), (250, 250))

    if game_over:
        text = big_font.render("YOU WIN!" if win else "GAME OVER", True, GREEN if win else RED)
        screen.blit(text, (260, 180))
        pygame.draw.rect(screen, ORANGE, restart_btn, border_radius=20)
        screen.blit(font.render("RESTART", True, BLACK), (345, 365))

    pygame.display.update()

pygame.quit()
sys.exit()