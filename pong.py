import pygame
import random
import sys

# ---------------------------
# Конфигурација
# ---------------------------
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Paddle (лeва палка)
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 120
PADDLE_SPEED = 6

# Ball
BALL_SIZE = 18
BALL_INITIAL_SPEED_X = 4.0  # почетна хоризонтална брзина (апсолутна вредност)
BALL_INITIAL_SPEED_Y = 2.0  # почетна вертикална компонента

# Бои
BG_COLOR = (15, 15, 15)
PADDLE_COLOR = (0, 200, 0)
BALL_COLOR = (240, 80, 80)
TEXT_COLOR = (240, 240, 240)
STATUS_COLOR = (200, 200, 0)

# ---------------------------
# Помошни функции
# ---------------------------

def reset_game():
    """
    Враќа почетни вредности за позицијата на палката, топката, брзините, поените и др.
    """
    # Позиција на палка (лево центрирано вертикално)
    paddle_x = 20
    paddle_y = (WINDOW_HEIGHT - PADDLE_HEIGHT) // 2

    # Топка во средина, ја даваме почетна насока кон лево или десно (посакувано: кон играчот)
    ball_x = WINDOW_WIDTH // 2
    ball_y = WINDOW_HEIGHT // 2

    # Насока: да дојде кон палката (од десно кон лево), па vx треба да биде негативно
    vx = -BALL_INITIAL_SPEED_X
    vy = random.choice([-1, 1]) * BALL_INITIAL_SPEED_Y

    score = 0
    game_over = False

    return {
        "paddle_x": paddle_x,
        "paddle_y": paddle_y,
        "ball_x": float(ball_x),
        "ball_y": float(ball_y),
        "vx": vx,
        "vy": vy,
        "score": score,
        "game_over": game_over
    }

def draw_text(surface, text, size, x, y, color=TEXT_COLOR, center=False):
    font = pygame.font.SysFont("Arial", size)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(surf, rect)

# ---------------------------
# Главна функција
# ---------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pong - Lab Exercise")
    clock = pygame.time.Clock()

    # Почетни вредности
    state = reset_game()
    paused = False

    # За да избегнеме повеќекратно детектирање на брзи судири додека топката е „внатре“ во палката,
    # користиме flag кој овозможува повторно судирање само откако топката ќе се "отстрани" малку.
    can_collide_with_paddle = True

    running = True
    while running:
        dt = clock.tick(FPS)

        # ------------ ЕВЕНТИ ------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Pause / resume
                if event.key == pygame.K_p:
                    paused = not paused

                # Restart
                if event.key == pygame.K_r:
                    state = reset_game()
                    paused = False
                    can_collide_with_paddle = True

        # ------------ ЛОГИКА (ако не е паузирано и не е game over) ------------
        keys = pygame.key.get_pressed()
        if not paused and not state["game_over"]:
            # Палка контрола (GORE / DOLU)
            if keys[pygame.K_UP]:
                state["paddle_y"] -= PADDLE_SPEED
            if keys[pygame.K_DOWN]:
                state["paddle_y"] += PADDLE_SPEED

            # Ограничување на палката внатре во екран
            if state["paddle_y"] < 0:
                state["paddle_y"] = 0
            if state["paddle_y"] > WINDOW_HEIGHT - PADDLE_HEIGHT:
                state["paddle_y"] = WINDOW_HEIGHT - PADDLE_HEIGHT

            # Поместување на топката
            state["ball_x"] += state["vx"]
            state["ball_y"] += state["vy"]

            # Судир со горен и долен предел - промени насока по y
            if state["ball_y"] <= 0:
                state["ball_y"] = 0
                state["vy"] = -state["vy"]
            elif state["ball_y"] + BALL_SIZE >= WINDOW_HEIGHT:
                state["ball_y"] = WINDOW_HEIGHT - BALL_SIZE
                state["vy"] = -state["vy"]

            # Судир со десниот зид - топката само се одбива (менува насока по x)
            if state["ball_x"] + BALL_SIZE >= WINDOW_WIDTH:
                state["ball_x"] = WINDOW_WIDTH - BALL_SIZE
                state["vx"] = -state["vx"]

            # Судир со палката (лево). Прво креираме Rects за collision detection
            paddle_rect = pygame.Rect(state["paddle_x"], state["paddle_y"], PADDLE_WIDTH, PADDLE_HEIGHT)
            ball_rect = pygame.Rect(int(state["ball_x"]), int(state["ball_y"]), BALL_SIZE, BALL_SIZE)

            # Севкупно услов за судир: ball_rect intersects paddle_rect и топката се движи кон палката (vx < 0)
            if ball_rect.colliderect(paddle_rect) and state["vx"] < 0 and can_collide_with_paddle:
                # Поместуваме топката надвор од палката за да избегнеме повторни судири во истиот кадар
                state["ball_x"] = state["paddle_x"] + PADDLE_WIDTH

                # Реверзирај насока по x (одбивање) и малку зголеми брзина
                # Зголемување на брзина: зголеми апсолутна вредност на vx за 8%
                new_speed_x = abs(state["vx"]) * 1.08
                state["vx"] = new_speed_x  # сега топката оди кон десно (позитивно)

                # Додај мал случаен придонес во y-насока за да се менува патеката (од -2 до +2)
                delta_vy = random.uniform(-2.0, 2.0)
                state["vy"] += delta_vy

                # Ограничување на вертикалната компонента за да не стане премногу голема
                if state["vy"] > 8:
                    state["vy"] = 8
                if state["vy"] < -8:
                    state["vy"] = -8

                # Зголемување на поен
                state["score"] += 1

                # Одбивањето треба да забрани повторно судирање додека топката не се отдалечи
                can_collide_with_paddle = False

            # Ако топката се оддалечи доволно од палката во x-насока, дозволи повторно судирање
            if state["ball_x"] > state["paddle_x"] + PADDLE_WIDTH + 5:
                can_collide_with_paddle = True

            # Проверка за Game Over: ако топката помине зад палката (на левата страна)
            if state["ball_x"] + BALL_SIZE < 0:
                state["game_over"] = True

        # ------------ ЦРТАЊЕ ------------
        screen.fill(BG_COLOR)

        # Палка
        pygame.draw.rect(screen, PADDLE_COLOR, (state["paddle_x"], state["paddle_y"], PADDLE_WIDTH, PADDLE_HEIGHT))

        # Десен зид (како ѕид)
        pygame.draw.rect(screen, (100, 100, 100), (WINDOW_WIDTH - 10, 0, 10, WINDOW_HEIGHT))

        # Топка
        pygame.draw.rect(screen, BALL_COLOR, (int(state["ball_x"]), int(state["ball_y"]), BALL_SIZE, BALL_SIZE))

        # Информации: score, инструкции, pause/gameover
        draw_text(screen, f"Поени: {state['score']}", 24, 10, 10, TEXT_COLOR)
        draw_text(screen, "UP/DOWN: поместување на палката  |  P: пауза  |  R: рестарт  |  ESC: излез", 18, 10, WINDOW_HEIGHT - 30, STATUS_COLOR)

        if paused:
            draw_text(screen, "ПАУЗА — притисни P за продолжување", 32, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, TEXT_COLOR, center=True)

        if state["game_over"]:
            draw_text(screen, "Играта заврши!", 48, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40, TEXT_COLOR, center=True)
            draw_text(screen, f"Краен резултат: {state['score']}", 32, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10, TEXT_COLOR, center=True)
            draw_text(screen, "Притисни R за повторно да започнеш или ESC за излез", 20, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60, STATUS_COLOR, center=True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
