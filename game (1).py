import sys
import pygame
import random
import math


def run_level1(screen, clock):
    """
    Runs Level 1 inside the existing pygame screen.
    Returns True if player wins, False otherwise.
    """
    pygame.init()

    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Christmas Adventure")

    font = pygame.font.SysFont(None, 32)
    big_font = pygame.font.SysFont(None, 64)

    # ---------------- IMAGE PATHS ----------------
    PLAYER_RUN1 = "assets/reindeer_frame1.png"
    PLAYER_RUN2 = "assets/reindeer_frame2.png"
    PLAYER_RUN3 = "assets/reindeer_frame3.png"
    PLAYER_SAD = "assets/reindeer_frame4sad.png"

    BIG_OBS_EXPLODE_IMG_PATH = "assets/bomb_frame2.png"
    BIG_OBS_IMG_PATH = "assets/bomb_frame1.png"

    SMALL_TARGET_IMG_PATH = "assets/small_target.png"
    STAMINA_IMG_PATH = "assets/stamina_item.png"
    BACKGROUND_IMG_PATH = "assets/background.png"

    SANTA_HAPPY_1 = "assets/santaend_frame1.png"
    SANTA_HAPPY_2 = "assets/santaend_frame2.png"
    SANTA_HAPPY_3 = "assets/santaend_frame3.png"
    SANTA_HAPPY_4 = "assets/santaend_frame4.png"

    SANTA_SAD_PATH = "assets/sad_santa.jpg"

    def load_img(path, size, flip=False):
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, size)
        if flip:
            img = pygame.transform.flip(img, True, False)
        return img

    # ---------------- IMAGE SIZES ----------------
    PLAYER_SIZE = (60, 60)
    SMALL_SIZE = (50, 50)
    BOMB_SIZE = (90, 90)
    STAMINA_SIZE = (40, 40)

    # ---------------- LOAD IMAGES ----------------
    run_imgs = [
        load_img(PLAYER_RUN1, PLAYER_SIZE, True),
        load_img(PLAYER_RUN2, PLAYER_SIZE, True),
        load_img(PLAYER_RUN3, PLAYER_SIZE, True),
    ]
    sad_img = load_img(PLAYER_SAD, PLAYER_SIZE, True)

    bomb_img = load_img(BIG_OBS_IMG_PATH, BOMB_SIZE)
    bomb_explode_img = load_img(BIG_OBS_EXPLODE_IMG_PATH, BOMB_SIZE)

    small_img = load_img(SMALL_TARGET_IMG_PATH, SMALL_SIZE)
    stamina_img = load_img(STAMINA_IMG_PATH, STAMINA_SIZE)
    bg_img = load_img(BACKGROUND_IMG_PATH, (WIDTH, HEIGHT))

    santa_happy_frames = [
        load_img(SANTA_HAPPY_1, (250, 250)),
        load_img(SANTA_HAPPY_2, (250, 250)),
        load_img(SANTA_HAPPY_3, (250, 250)),
        load_img(SANTA_HAPPY_4, (250, 250)),
    ]
    santa_sad = load_img(SANTA_SAD_PATH, (250, 250))
    santa_frame = 0
    santa_timer = 0

    # ---------------- PLAYER ----------------
    player = pygame.Rect(100, 220, PLAYER_SIZE[0], PLAYER_SIZE[1])
    player_speed = 5
    boost_speed = 10
    run_frame = 0
    run_timer = 0
    player_sad_timer = 0

    # ---------------- CHRISTMAS EFFECTS ----------------
    snowflakes = []
    for _ in range(120):
        snowflakes.append([random.randint(0, WIDTH),
                           random.randint(0, HEIGHT),
                           random.randint(2, 5)])

    # ---------------- PARTICLES ----------------
    player_sparkles = []
    item_sparkles = []
    bomb_sparkles = []

    def spawn_sparkle(x, y, color):
        return {
            "x": x,
            "y": y,
            "vx": random.uniform(-1, 1),
            "vy": random.uniform(-1, 1),
            "life": random.randint(20, 40),
            "color": color,
        }

    # ---------------- OBJECT LISTS ----------------
    bombs = []
    small_targets = []
    stamina_targets = []

    # ---------------- GAME VARS ----------------
    stamina = 100
    score = 0
    level = 1
    MAX_LEVEL = 4
    ROUND_TIME = 30
    timer = ROUND_TIME * 60

    spawn_timer = 0
    base_small_chance = 0.6
    game_over = False
    game_won = False
    paused = False
    pause_mode = "MENU"

    pause_title_font = pygame.font.SysFont("arial", 48, bold=True)
    pause_font = pygame.font.SysFont("arial", 28)

    def pause_ui_layout():
        panel = pygame.Rect(0, 0, 420, 360)
        panel.center = (WIDTH // 2, HEIGHT // 2)
        btn_w, btn_h = 220, 42
        resume = pygame.Rect(0, 0, btn_w, btn_h)
        options = pygame.Rect(0, 0, btn_w, btn_h)
        exit_btn = pygame.Rect(0, 0, btn_w, btn_h)
        resume.center = (panel.centerx, panel.y + 130)
        options.center = (panel.centerx, panel.y + 190)
        exit_btn.center = (panel.centerx, panel.y + 250)

        options_panel = pygame.Rect(0, 0, 380, 220)
        options_panel.center = (WIDTH // 2, HEIGHT // 2)
        options_close = pygame.Rect(options_panel.right - 38, options_panel.y + 10, 24, 24)

        music_minus = pygame.Rect(options_panel.x + 40, options_panel.y + 90, 30, 30)
        music_plus = pygame.Rect(options_panel.right - 70, options_panel.y + 90, 30, 30)
        sfx_minus = pygame.Rect(options_panel.x + 40, options_panel.y + 140, 30, 30)
        sfx_plus = pygame.Rect(options_panel.right - 70, options_panel.y + 140, 30, 30)

        return {
            "panel": panel,
            "resume": resume,
            "options": options,
            "exit": exit_btn,
            "options_panel": options_panel,
            "options_close": options_close,
            "music_minus": music_minus,
            "music_plus": music_plus,
            "sfx_minus": sfx_minus,
            "sfx_plus": sfx_plus,
        }

    def draw_pause_panel(surface, mode):
        layout = pause_ui_layout()
        panel = layout["panel"]
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))
        pygame.draw.rect(surface, (180, 180, 180), panel, border_radius=12)
        pygame.draw.rect(surface, (100, 100, 100), panel, 2, border_radius=12)
        title = pause_title_font.render("PAUSED", True, (30, 30, 30))
        surface.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 30))

        def draw_button(rect, text):
            pygame.draw.rect(surface, (230, 230, 230), rect, border_radius=8)
            pygame.draw.rect(surface, (120, 120, 120), rect, 2, border_radius=8)
            label = pause_font.render(text, True, (20, 20, 20))
            surface.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

        draw_button(layout["resume"], "RESUME")
        draw_button(layout["options"], "OPTIONS")
        draw_button(layout["exit"], "EXIT")

        if mode == "OPTIONS":
            opt = layout["options_panel"]
            pygame.draw.rect(surface, (190, 190, 190), opt, border_radius=10)
            pygame.draw.rect(surface, (100, 100, 100), opt, 2, border_radius=10)
            close_rect = layout["options_close"]
            pygame.draw.rect(surface, (230, 230, 230), close_rect, border_radius=6)
            pygame.draw.rect(surface, (120, 120, 120), close_rect, 2, border_radius=6)
            x_label = pause_font.render("X", True, (20, 20, 20))
            surface.blit(x_label, (close_rect.centerx - x_label.get_width() // 2, close_rect.centery - x_label.get_height() // 2))

            music = pause_font.render(f"Music: {int(pygame.mixer.music.get_volume() * 100)}%", True, (30, 30, 30))
            sfx = pause_font.render(f"SFX: {int(pygame.mixer.music.get_volume() * 100)}%", True, (30, 30, 30))
            surface.blit(music, (opt.x + 80, opt.y + 90))
            surface.blit(sfx, (opt.x + 80, opt.y + 140))

            for key in ("music_minus", "music_plus", "sfx_minus", "sfx_plus"):
                rect = layout[key]
                pygame.draw.rect(surface, (230, 230, 230), rect, border_radius=6)
                pygame.draw.rect(surface, (120, 120, 120), rect, 2, border_radius=6)
            minus = pause_font.render("-", True, (20, 20, 20))
            plus = pause_font.render("+", True, (20, 20, 20))
            surface.blit(minus, (layout["music_minus"].centerx - minus.get_width() // 2, layout["music_minus"].centery - minus.get_height() // 2))
            surface.blit(plus, (layout["music_plus"].centerx - plus.get_width() // 2, layout["music_plus"].centery - plus.get_height() // 2))
            surface.blit(minus, (layout["sfx_minus"].centerx - minus.get_width() // 2, layout["sfx_minus"].centery - minus.get_height() // 2))
            surface.blit(plus, (layout["sfx_plus"].centerx - plus.get_width() // 2, layout["sfx_plus"].centery - plus.get_height() // 2))
        return layout
    # ---------------- SPAWN ----------------
    def spawn_big():
        y = random.randint(40, HEIGHT - 100)
        bombs.append({"rect": pygame.Rect(WIDTH, y, 90, 90),
                      "state": "normal", "timer": 0})

    def spawn_small():
        y = random.randint(40, HEIGHT - 50)
        small_targets.append({"rect": pygame.Rect(WIDTH, y, SMALL_SIZE[0], SMALL_SIZE[1]),
                              "angle": 0})

    def spawn_stamina():
        y = random.randint(40, HEIGHT - 50)
        stamina_targets.append({"rect": pygame.Rect(WIDTH, y, STAMINA_SIZE[0], STAMINA_SIZE[1]),
                                "angle": 0})

    # ---------------- LOOP ----------------
    running = True

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if (not game_over) and (not game_won) and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = not paused
                pause_mode = "MENU"

            if (not game_over) and (not game_won) and (not paused) and event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
                # DEV SKIP: Jump to level 2
                return True

            if (not game_over) and (not game_won) and paused and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                layout = pause_ui_layout()
                if layout["resume"].collidepoint(event.pos):
                    paused = False
                elif layout["options"].collidepoint(event.pos):
                    pause_mode = "OPTIONS" if pause_mode == "MENU" else "MENU"
                elif layout["exit"].collidepoint(event.pos):
                    return None

                if pause_mode == "OPTIONS":
                    if layout["music_minus"].collidepoint(event.pos):
                        pygame.mixer.music.set_volume(max(0.0, pygame.mixer.music.get_volume() - 0.1))
                    elif layout["music_plus"].collidepoint(event.pos):
                        pygame.mixer.music.set_volume(min(1.0, pygame.mixer.music.get_volume() + 0.1))
            if event.type == pygame.QUIT:
                return None
            if (game_over or game_won) and event.type == pygame.KEYDOWN:
                if game_won:
                    return True
                if event.key == pygame.K_r:
                    level = 1
                    score = 0
                    stamina = 100
                    timer = ROUND_TIME * 60
                    bombs.clear()
                    small_targets.clear()
                    stamina_targets.clear()
                    game_over = False
                    game_won = False
                else:
                    return False

        if (not game_over) and (not game_won) and paused:
            draw_pause_panel(screen, pause_mode)
            pygame.display.flip()
            continue
        if game_over or game_won:
            screen.fill((15, 25, 40))

            # Snowfall effect
            for flake in snowflakes:
                pygame.draw.circle(screen, (255, 255, 255), (flake[0], flake[1]), flake[2])
                flake[1] += flake[2] * 0.5
                if flake[1] > HEIGHT:
                    flake[0] = random.randint(0, WIDTH)
                    flake[1] = 0

            if game_won:
                title = big_font.render("YOU SAVED SANTA!", True, (0, 255, 0))
                screen.blit(title, (WIDTH // 2 - 260, 80))

                santa_timer += dt
                if santa_timer > 150:
                    santa_frame = (santa_frame + 1) % 4
                    santa_timer = 0

                screen.blit(santa_happy_frames[santa_frame], (WIDTH // 2 - 125, 150))
            else:
                title = big_font.render("CHRISTMAS IS RUINED!", True, (255, 50, 50))
                screen.blit(title, (WIDTH // 2 - 260, 80))
                screen.blit(santa_sad, (WIDTH // 2 - 125, 150))

            restart_text = font.render("Press Any Key to continue", True, (255, 255, 255))
            screen.blit(restart_text, (WIDTH // 2 - 120, 420))

            pygame.display.flip()
            continue

        # BACKGROUND
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill((30, 60, 50))

        # MOVEMENT
        keys = pygame.key.get_pressed()
        speed = player_speed
        moving = False

        if keys[pygame.K_LSHIFT] and stamina > 0:
            speed = boost_speed
            stamina -= 0.6
        else:
            stamina += 0.25

        stamina = max(0, min(100, stamina))

        if keys[pygame.K_w]:
            player.y -= speed
            moving = True
        if keys[pygame.K_s]:
            player.y += speed
            moving = True
        if keys[pygame.K_a]:
            player.x -= speed
            moving = True
        if keys[pygame.K_d]:
            player.x += speed
            moving = True

        player.clamp_ip(screen.get_rect())

        # PLAYER SPARKLES
        if moving:
            for _ in range(2):
                player_sparkles.append(
                    spawn_sparkle(player.centerx - 20, player.centery, (255, 215, 0))
                )

        for s in player_sparkles[:]:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["life"] -= 1
            pygame.draw.circle(screen, s["color"], (int(s["x"]), int(s["y"])), 3)
            if s["life"] <= 0:
                player_sparkles.remove(s)

        # RUN animation
        run_timer += dt
        if run_timer > 120:
            run_frame = (run_frame + 1) % 3
            run_timer = 0

        # SPAWN
        spawn_timer += 1
        if spawn_timer > 70:
            spawn_big()
            small_chance = min(base_small_chance + (level - 1) * 0.07, 0.95)
            if random.random() < small_chance:
                spawn_small()
            if random.random() < 0.25:
                spawn_stamina()
            spawn_timer = 0

        # UPDATE SMALL TARGETS
        speed_bonus = (level - 1) * 0.3
        for t in small_targets[:]:
            t["rect"].x -= 5 + level * 0.5 + speed_bonus
            t["angle"] += 4

            rotated = pygame.transform.rotate(small_img, t["angle"])
            new_rect = rotated.get_rect(center=t["rect"].center)
            screen.blit(rotated, new_rect.topleft)

            item_sparkles.append(
                spawn_sparkle(t["rect"].centerx, t["rect"].centery, (255, 50, 50))
            )

            if player.colliderect(t["rect"]):
                score += 5
                small_targets.remove(t)

            if t in small_targets and t["rect"].right < 0:
                small_targets.remove(t)

        # UPDATE STAMINA
        for s_obj in stamina_targets[:]:
            s_obj["rect"].x -= 5 + level * 0.5 + speed_bonus
            s_obj["angle"] += 5

            rotated = pygame.transform.rotate(stamina_img, s_obj["angle"])
            new_rect = rotated.get_rect(center=s_obj["rect"].center)
            screen.blit(rotated, new_rect.topleft)

            item_sparkles.append(
                spawn_sparkle(s_obj["rect"].centerx, s_obj["rect"].centery, (50, 200, 255))
            )

            if player.colliderect(s_obj["rect"]):
                stamina += 25
                stamina_targets.remove(s_obj)

            if s_obj in stamina_targets and s_obj["rect"].right < 0:
                stamina_targets.remove(s_obj)

        # UPDATE BOMBS
        for b in bombs[:]:
            if b["state"] == "normal":
                b["rect"].x -= 6 + level * 0.8 + speed_bonus

                for _ in range(2):
                    bomb_sparkles.append(
                        spawn_sparkle(b["rect"].centerx + 20,
                                      b["rect"].centery,
                                      (50, 50, 50))
                    )

                if player.colliderect(b["rect"]):
                    score -= 10
                    player_sad_timer = 500
                    b["state"] = "explode"
                    b["timer"] = 300
            else:
                b["timer"] -= dt
                if b["timer"] <= 0:
                    bombs.remove(b)

            if b in bombs and b["rect"].right < 0:
                bombs.remove(b)

        # BOMB SPARKLES
        for sp in bomb_sparkles[:]:
            sp["x"] += sp["vx"]
            sp["y"] += sp["vy"]
            sp["life"] -= 1
            pygame.draw.circle(screen, sp["color"], (int(sp["x"]), int(sp["y"])), 2)
            if sp["life"] <= 0:
                bomb_sparkles.remove(sp)

        if player_sad_timer > 0:
            player_sad_timer -= dt

        # TIMER
        required_score = 40 + level * 10

        timer -= 1
        if timer <= 0:
            if score >= required_score:
                level += 1
                if level > MAX_LEVEL:
                    game_won = True
                else:
                    score = 0
                    timer = ROUND_TIME * 60
                    bombs.clear()
                    small_targets.clear()
                    stamina_targets.clear()
            else:
                game_over = True

        # DRAW PLAYER
        if player_sad_timer > 0:
            screen.blit(sad_img, player.topleft)
        else:
            screen.blit(run_imgs[run_frame], player.topleft)

        # DRAW BOMBS
        for b in bombs:
            img = bomb_img if b["state"] == "normal" else bomb_explode_img
            screen.blit(img, b["rect"].topleft)

        # ITEM SPARKLES
        for sp in item_sparkles[:]:
            sp["x"] += sp["vx"]
            sp["y"] += sp["vy"]
            sp["life"] -= 1
            pygame.draw.circle(screen, sp["color"], (int(sp["x"]), int(sp["y"])), 2)
            if sp["life"] <= 0:
                item_sparkles.remove(sp)

        # UI
        sec = timer // 60
        screen.blit(font.render(f"Level: {level}/{MAX_LEVEL}", True, (255, 255, 255)), (10, 10))
        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (10, 40))
        screen.blit(font.render(f"Presents Needed: {required_score}", True, (255, 200, 255)), (10, 70))
        screen.blit(font.render(f"Time: {sec}s", True, (255, 255, 255)), (WIDTH - 120, 10))
        screen.blit(font.render(f"Stamina: {int(stamina)}", True, (255, 255, 255)), (WIDTH - 160, 40))

        pygame.display.flip()

    return game_won






