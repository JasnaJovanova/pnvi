import pygame
import random
import sys

pygame.init()

# --- WINDOW ---
WIDTH, HEIGHT = 600, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Scavenger")

# --- LOAD RESOURCES ---
spaceship_img = pygame.image.load("spaceship.png")
asteroid_img = pygame.image.load("asteroid.png")
crystal_img = pygame.image.load("energy_crystal.png")

# Resize for gameplay
spaceship_img = pygame.transform.scale(spaceship_img, (80, 80))
crystal_img = pygame.transform.scale(crystal_img, (60, 60))

# Sounds
pygame.mixer.music.load("background_music.wav")   # background music
clash_sound = pygame.mixer.Sound("clash_sound.wav")     # collision effect
pygame.mixer.music.play(-1)

# --- GAME VARIABLES ---
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)

player_speed = 6
asteroid_speed = 4
score = 0
game_over = False

# --- PLAYER ---
player = spaceship_img.get_rect(center=(WIDTH // 2, HEIGHT - 100))


# --- CREATE ASTEROID ---
def create_asteroid():
    size = random.randint(60, 120)
    img = pygame.transform.scale(asteroid_img, (size, size))
    rect = img.get_rect(midtop=(random.randint(50, WIDTH - 50), -size))
    return img, rect, size


# --- CREATE CRYSTAL ---
def create_crystal():
    rect = crystal_img.get_rect(midtop=(random.randint(40, WIDTH - 40), -60))
    return rect


asteroids = []
crystals = []

ASTEROID_EVENT = pygame.USEREVENT + 1
CRYSTAL_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(ASTEROID_EVENT, 1200)
pygame.time.set_timer(CRYSTAL_EVENT, 2500)

# MAIN LOOP
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Restart
                asteroids.clear()
                crystals.clear()
                score = 0
                player_speed = 6
                asteroid_speed = 4
                game_over = False

        if event.type == ASTEROID_EVENT and not game_over:
            asteroids.append(create_asteroid())

        if event.type == CRYSTAL_EVENT and not game_over:
            crystals.append(create_crystal())

    keys = pygame.key.get_pressed()

    if not game_over:
        # Player movement
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += player_speed

        # Increasing difficulty
        asteroid_speed += 0.002
        player_speed += 0.001

        # MOVE ASTEROIDS
        for asteroid in asteroids[:]:
            img, rect, size = asteroid
            rect.y += asteroid_speed

            # Collide with player
            if rect.colliderect(player):
                clash_sound.play()
                game_over = True

            if rect.top > HEIGHT:
                asteroids.remove(asteroid)

        # MOVE CRYSTALS
        for c in crystals[:]:
            c.y += 4

            # Collect
            if c.colliderect(player):
                score += 1
                crystals.remove(c)

            if c.top > HEIGHT:
                crystals.remove(c)

    # DRAW
    WIN.fill((10, 10, 25))

    # Draw objects
    for img, rect, size in asteroids:
        WIN.blit(img, rect)
    for c in crystals:
        WIN.blit(crystal_img, c)

    WIN.blit(spaceship_img, player)

    # Score
    score_text = font.render(f"Score: {score}", True, (255, 255, 120))
    WIN.blit(score_text, (10, 10))

    # Game Over
    if game_over:
        over_text = font.render("GAME OVER — Press R to Restart", True, (255, 80, 80))
        WIN.blit(over_text, (WIDTH / 2 - over_text.get_width() / 2, HEIGHT / 2))

    pygame.display.update()
    clock.tick(60)
