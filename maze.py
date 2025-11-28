import pygame, sys, random

# --- CONFIG ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 60
GRID_COLS = 8
GRID_ROWS = 6
STATUS_BAR = 80
FPS = 30

BLACK    = (0, 0, 0)
GRAY     = (150,150,150)
WHITE    = (255,255,255)
DARKGRAY = (50,50,50)
GREEN    = (0,200,0)
RED      = (200,0,0)
BLUE     = (0,0,200)

# ------------------------------------------------------
# HELPERS
# ------------------------------------------------------

def grid_origin():
    w = GRID_COLS * CELL_SIZE
    h = GRID_ROWS * CELL_SIZE
    return (WINDOW_WIDTH - w)//2, STATUS_BAR + (WINDOW_HEIGHT - STATUS_BAR - h)//2

def random_level():
    # генерира случајни 5 стапици, S и E се фиксни
    traps = set()
    while len(traps) < 5:
        r = random.randint(0, GRID_ROWS-1)
        c = random.randint(0, GRID_COLS-1)
        if (c,r) not in [(0,4), (7,1)]:   # да не бидат врз S или E
            traps.add((c,r))
    return traps

# ------------------------------------------------------
# DRAW
# ------------------------------------------------------

def draw_board(screen, player, traps, exitp, reveal):
    screen.fill(BLACK)
    gx, gy = grid_origin()

    # статус бар
    pygame.draw.rect(screen, DARKGRAY, (0, 0, WINDOW_WIDTH, STATUS_BAR))

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            rect = pygame.Rect(gx + c*CELL_SIZE, gy + r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, DARKGRAY, rect, 1)

            # Exit
            if (c, r) == exitp:
                pygame.draw.rect(screen, BLUE, rect)

            # Player
            if (c, r) == tuple(player):
                p_rect = pygame.Rect(rect.x+10, rect.y+10, CELL_SIZE-20, CELL_SIZE-20)
                pygame.draw.rect(screen, GREEN, p_rect)

            # Reveal traps (only during the first 4 seconds)
            if reveal and (c, r) in traps:
                pygame.draw.rect(screen, RED, rect)

def draw_status(screen, msg, lives, moves):
    text_font = pygame.font.Font("freesansbold.ttf", 26)
    msg_surf = text_font.render(msg, True, WHITE)
    lives_surf = text_font.render(f"Животи: {lives}   Потези: {moves}", True, WHITE)

    screen.blit(msg_surf, (20, 20))
    screen.blit(lives_surf, (420, 20))


# ------------------------------------------------------
# MAIN GAME LOOP
# ------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Trap Maze")
    clock = pygame.time.Clock()

    start = (0,4)
    exitp = (7,1)
    traps = random_level()

    player = list(start)
    lives = 3
    moves = 0

    state = "REVEAL"
    msg = "Запамти ги стапиците!"
    reveal_start = pygame.time.get_ticks()
    REVEAL_MS = 4000

    while True:
        clock.tick(FPS)

        # CHECK REVEAL END
        if state == "REVEAL" and pygame.time.get_ticks() - reveal_start > REVEAL_MS:
            state = "PLAY"
            msg = "Почни да се движиш!"

        # INPUT
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_ESCAPE:
                    sys.exit()

                if e.key == pygame.K_r:
                    main()

                if state == "PLAY":
                    new_c, new_r = player

                    if e.key == pygame.K_UP:    new_r -= 1
                    if e.key == pygame.K_DOWN:  new_r += 1
                    if e.key == pygame.K_LEFT:  new_c -= 1
                    if e.key == pygame.K_RIGHT: new_c += 1

                    # CHECK BOUNDS
                    if not (0 <= new_c < GRID_COLS and 0 <= new_r < GRID_ROWS):
                        msg = "Не можеш таму!"
                        continue

                    player = [new_c, new_r]
                    moves += 1

                    # TRAP HIT
                    if (new_c, new_r) in traps:
                        lives -= 1
                        msg = f"Удри во стапица! Преостанати животи: {lives}"
                        player = list(start)

                        if lives == 0:
                            msg = "Играта заврши!"
                            draw_board(screen, player, traps, exitp, False)
                            draw_status(screen, msg, lives, moves)
                            pygame.display.update()
                            pygame.time.delay(2000)
                            main()

                    # EXIT
                    if (new_c, new_r) == exitp:
                        msg = "Успешно го завршивте нивото!"
                        draw_board(screen, player, traps, exitp, False)
                        draw_status(screen, msg, lives, moves)
                        pygame.display.update()
                        pygame.time.delay(2000)
                        main()

        # DRAW
        draw_board(screen, player, traps, exitp, state == "REVEAL")
        draw_status(screen, msg, lives, moves)
        pygame.display.update()


if __name__ == "__main__":
    main()
