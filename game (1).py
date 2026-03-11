"""import pygame
import random
import math

pygame.init()

# ---------------- SCREEN ----------------
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reindeer Rush")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 64)
intro_big = pygame.font.SysFont(None, 70)
intro_font = pygame.font.SysFont(None, 40)

# ---------------- IMAGE PATHS ----------------
PLAYER_RUN1 = "C:\\Users\\czy\\Downloads\\reindeer_frame1.png"
PLAYER_RUN2 = "C:\\Users\\czy\\Downloads\\reindeer_frame2.png"
PLAYER_RUN3 = "C:\\Users\\czy\\Downloads\\reindeer_frame3.png"
PLAYER_SAD = "C:\\Users\\czy\\Downloads\\reindeer_frame4sad.png"

BIG_OBS_EXPLODE_IMG_PATH = "C:\\Users\\czy\\Downloads\\bomb_frame2.png"
BIG_OBS_IMG_PATH = "C:\\Users\\czy\\Downloads\\bomb_frame1.png"

SMALL_TARGET_IMG_PATH = "C:\\Users\\czy\\OneDrive\\Pictures\\Screenshots\\Screenshot 2026-02-25 105555.png"
STAMINA_IMG_PATH = "C:\\Users\\czy\\OneDrive\\Pictures\\Screenshots\\Screenshot 2026-02-25 105633.png"
BACKGROUND_IMG_PATH = "C:\\Users\\czy\\OneDrive\\Pictures\\Screenshots\\Screenshot 2026-02-25 105754.png"

def load_img(path, size, flip=False):
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    if flip:
        img = pygame.transform.flip(img, True, False)
    return img

# ---------------- IMAGE SIZES ----------------
PLAYER_SIZE = (60,60)      # slightly bigger than small targets
SMALL_SIZE = (50,50)       # slightly smaller than player
BOMB_SIZE = (100,100)        # unchanged
STAMINA_SIZE = (40,40)     # slightly smaller than small targets

# ---------------- LOAD IMAGES ----------------
run_imgs = [
    load_img(PLAYER_RUN1, PLAYER_SIZE, True),
    load_img(PLAYER_RUN2, PLAYER_SIZE, True),
    load_img(PLAYER_RUN3, PLAYER_SIZE, True)
]
sad_img = load_img(PLAYER_SAD, PLAYER_SIZE, True)

bomb_img = load_img(BIG_OBS_IMG_PATH, BOMB_SIZE)
bomb_explode_img = load_img(BIG_OBS_EXPLODE_IMG_PATH, BOMB_SIZE)

small_img = load_img(SMALL_TARGET_IMG_PATH, SMALL_SIZE)
stamina_img = load_img(STAMINA_IMG_PATH, STAMINA_SIZE)
bg_img = load_img(BACKGROUND_IMG_PATH,(WIDTH,HEIGHT))

# ---------------- PLAYER ----------------
player = pygame.Rect(100,220,PLAYER_SIZE[0],PLAYER_SIZE[1])
player_speed = 5
boost_speed = 10
run_frame=0
run_timer=0
player_sad_timer=0

# ---------------- PARTICLES ----------------
player_sparkles=[]
item_sparkles=[]

def spawn_sparkle(x,y,color):
    return {"x":x,"y":y,"vx":random.uniform(-1,1),
            "vy":random.uniform(-1,1),
            "life":random.randint(20,40),
            "color":color}

# ---------------- OBJECT LISTS ----------------
bombs=[]
small_targets=[]
stamina_targets=[]

# ---------------- GAME VARS ----------------
stamina=100
score=0
level=1
MAX_LEVEL=8
ROUND_TIME=30
timer=ROUND_TIME*60

spawn_timer=0
game_started=True
game_over=False
game_won=False

# ---------------- SPAWN ----------------
def spawn_big():
    y=random.randint(40,HEIGHT-100)
    bombs.append({"rect":pygame.Rect(WIDTH,y,90,90),
                  "state":"normal","timer":0})

def spawn_small():
    y=random.randint(40,HEIGHT-50)
    small_targets.append({"rect":pygame.Rect(WIDTH,y,SMALL_SIZE[0],SMALL_SIZE[1]),
                          "angle":0})

def spawn_stamina():
    y=random.randint(40,HEIGHT-50)
    stamina_targets.append({"rect":pygame.Rect(WIDTH,y,STAMINA_SIZE[0],STAMINA_SIZE[1]),
                            "angle":0})

# ---------------- LOOP ----------------
running=True

while running:
    dt=clock.tick(60)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

    if game_over or game_won:
        screen.fill((20,30,20))
        msg="YOU SAVED CHRISTMAS 🎄" if game_won else "TIME UP!"
        screen.blit(big_font.render(msg,True,(255,255,255)),(200,220))
        pygame.display.flip()
        continue

    # BACKGROUND
    if bg_img:
        screen.blit(bg_img,(0,0))
    else:
        screen.fill((30,60,50))

    # MOVEMENT
    keys=pygame.key.get_pressed()
    speed=player_speed

    moving=False

    if keys[pygame.K_LSHIFT] and stamina>0:
        speed=boost_speed
        stamina-=0.6
    else:
        stamina+=0.25

    stamina=max(0,min(100,stamina))

    if keys[pygame.K_UP]:
        player.y-=speed
        moving=True
    if keys[pygame.K_DOWN]:
        player.y+=speed
        moving=True
    if keys[pygame.K_LEFT]:
        player.x-=speed
        moving=True
    if keys[pygame.K_RIGHT]:
        player.x+=speed
        moving=True

    player.clamp_ip(screen.get_rect())

    # PLAYER SPARKLES (golden behind player)
    if moving:
        for _ in range(2):
            player_sparkles.append(
                spawn_sparkle(player.centerx - 20,
                              player.centery,
                              (255,215,0))  # golden
            )

    for s in player_sparkles[:]:
        s["x"]+=s["vx"]
        s["y"]+=s["vy"]
        s["life"]-=1
        pygame.draw.circle(screen,s["color"],
                           (int(s["x"]),int(s["y"])),3)
        if s["life"]<=0:
            player_sparkles.remove(s)

    # RUN animation
    run_timer+=dt
    if run_timer>120:
        run_frame=(run_frame+1)%3
        run_timer=0

    # SPAWN
    spawn_timer+=1
    if spawn_timer>70:
        spawn_big()
        if random.random()<0.6: spawn_small()
        if random.random()<0.25: spawn_stamina()
        spawn_timer=0

    # UPDATE SMALL TARGETS
    for t in small_targets[:]:
        t["rect"].x-=5+level*0.5
        t["angle"]+=4

        rotated=pygame.transform.rotate(small_img,t["angle"])
        new_rect=rotated.get_rect(center=t["rect"].center)
        screen.blit(rotated,new_rect.topleft)

        # Red sparkles for small targets
        item_sparkles.append(
            spawn_sparkle(t["rect"].centerx,
                          t["rect"].centery,
                          (255,50,50))
        )

        if player.colliderect(t["rect"]):
            score+=5
            small_targets.remove(t)

        if t in small_targets and t["rect"].right<0:
            small_targets.remove(t)

    # UPDATE STAMINA
    for s_obj in stamina_targets[:]:
        s_obj["rect"].x-=5+level*0.5
        s_obj["angle"]+=5

        rotated=pygame.transform.rotate(stamina_img,s_obj["angle"])
        new_rect=rotated.get_rect(center=s_obj["rect"].center)
        screen.blit(rotated,new_rect.topleft)

        # Blue sparkles for stamina
        item_sparkles.append(
            spawn_sparkle(s_obj["rect"].centerx,
                          s_obj["rect"].centery,
                          (50,200,255))
        )

        if player.colliderect(s_obj["rect"]):
            stamina+=25
            stamina_targets.remove(s_obj)

        if s_obj in stamina_targets and s_obj["rect"].right<0:
            stamina_targets.remove(s_obj)

    # ITEM SPARKLES
    for sp in item_sparkles[:]:
        sp["x"]+=sp["vx"]
        sp["y"]+=sp["vy"]
        sp["life"]-=1
        pygame.draw.circle(screen,sp["color"],
                           (int(sp["x"]),int(sp["y"])),2)
        if sp["life"]<=0:
            item_sparkles.remove(sp)

    # UPDATE BOMBS
    for b in bombs[:]:
        if b["state"]=="normal":
            b["rect"].x-=6+level*0.8
            if player.colliderect(b["rect"]):
                score-=10
                player_sad_timer=500
                b["state"]="explode"
                b["timer"]=300
        else:
            b["timer"]-=dt
            if b["timer"]<=0:
                bombs.remove(b)

        if b in bombs and b["rect"].right<0:
            bombs.remove(b)

    if player_sad_timer>0:
        player_sad_timer-=dt

    # TIMER
    timer-=1
    if timer<=0:
        if score>=10+level*10:
            level+=1
            if level>MAX_LEVEL:
                game_won=True
            else:
                timer=ROUND_TIME*60
                bombs.clear()
                small_targets.clear()
                stamina_targets.clear()
        else:
            game_over=True

    # DRAW PLAYER
    if player_sad_timer>0:
        screen.blit(sad_img,player.topleft)
    else:
        screen.blit(run_imgs[run_frame],player.topleft)

    # DRAW BOMBS
    for b in bombs:
        img=bomb_img if b["state"]=="normal" else bomb_explode_img
        screen.blit(img,b["rect"].topleft)

    # UI
    sec=timer//60
    screen.blit(font.render(f"Level: {level}/8",True,(255,255,255)),(10,10))
    screen.blit(font.render(f"Score: {score}",True,(255,255,255)),(10,40))
    screen.blit(font.render(f"Time: {sec}s",True,(255,255,255)),(WIDTH-120,10))
    screen.blit(font.render(f"Stamina: {int(stamina)}",True,(255,255,255)),(WIDTH-160,40))

    pygame.display.flip()

pygame.quit()"""

import pygame
import random
import math

pygame.init()

# ---------------- SCREEN ----------------
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Christmas Adventure")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 64)
intro_big = pygame.font.SysFont(None, 70)
intro_font = pygame.font.SysFont(None, 40)

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
PLAYER_SIZE = (60,60)      # slightly bigger than small targets
SMALL_SIZE = (50,50)       # slightly smaller than player
BOMB_SIZE = (90,90)        # unchanged
STAMINA_SIZE = (40,40)     # slightly smaller than small targets

# ---------------- LOAD IMAGES ----------------
run_imgs = [
    load_img(PLAYER_RUN1, PLAYER_SIZE, True),
    load_img(PLAYER_RUN2, PLAYER_SIZE, True),
    load_img(PLAYER_RUN3, PLAYER_SIZE, True)
]
sad_img = load_img(PLAYER_SAD, PLAYER_SIZE, True)

bomb_img = load_img(BIG_OBS_IMG_PATH, BOMB_SIZE)
bomb_explode_img = load_img(BIG_OBS_EXPLODE_IMG_PATH, BOMB_SIZE)

small_img = load_img(SMALL_TARGET_IMG_PATH, SMALL_SIZE)
stamina_img = load_img(STAMINA_IMG_PATH, STAMINA_SIZE)
bg_img = load_img(BACKGROUND_IMG_PATH,(WIDTH,HEIGHT))

# Santa animation frames
santa_happy_frames = [
    load_img(SANTA_HAPPY_1, (250,250)),
    load_img(SANTA_HAPPY_2, (250,250)),
    load_img(SANTA_HAPPY_3, (250,250)),
    load_img(SANTA_HAPPY_4, (250,250))
]

santa_sad = load_img(SANTA_SAD_PATH, (250,250))
santa_frame = 0
santa_timer = 0


# ---------------- PLAYER ----------------
player = pygame.Rect(100,220,PLAYER_SIZE[0],PLAYER_SIZE[1])
player_speed = 5
boost_speed = 10
run_frame=0
run_timer=0
player_sad_timer=0

# ---------------- CHRISTMAS INTRO EFFECTS ----------------
snowflakes = []
lights = []
for _ in range(120):
    snowflakes.append([random.randint(0,WIDTH),
                       random.randint(0,HEIGHT),
                       random.randint(2,5)])

for i in range(25):
    lights.append({
        "x": i * 36,
        "color": random.choice([(255,0,0),(0,255,0),(255,255,0),(0,200,255)]),
        "radius": random.randint(4,7),
        "pulse": random.uniform(0.5,1.5)
    })

# ---------------- PARTICLES ----------------
player_sparkles=[]
item_sparkles=[]
bomb_sparkles=[]

def spawn_sparkle(x,y,color):
    return {"x":x,"y":y,"vx":random.uniform(-1,1),
            "vy":random.uniform(-1,1),
            "life":random.randint(20,40),
            "color":color}

# ---------------- OBJECT LISTS ----------------
bombs=[]
small_targets=[]
stamina_targets=[]

# ---------------- GAME VARS ----------------
stamina=100
score=0
level=1
MAX_LEVEL=8
ROUND_TIME=30
timer=ROUND_TIME*60

spawn_timer=0
game_started=False
game_over=False
game_won=False

# ---------------- SPAWN ----------------
def spawn_big():
    y=random.randint(40,HEIGHT-100)
    bombs.append({"rect":pygame.Rect(WIDTH,y,90,90),
                  "state":"normal","timer":0})

def spawn_small():
    y=random.randint(40,HEIGHT-50)
    small_targets.append({"rect":pygame.Rect(WIDTH,y,SMALL_SIZE[0],SMALL_SIZE[1]),
                          "angle":0})

def spawn_stamina():
    y=random.randint(40,HEIGHT-50)
    stamina_targets.append({"rect":pygame.Rect(WIDTH,y,STAMINA_SIZE[0],STAMINA_SIZE[1]),
                            "angle":0})

# ---------------- INTRO SCREEN ----------------
def draw_intro():
    screen.fill((15, 30, 40))  # dark winter night

    # Falling snow
    for flake in snowflakes:
        pygame.draw.circle(screen,(255,255,255),(flake[0],flake[1]),flake[2])
        flake[1]+=flake[2]*0.5
        if flake[1] > HEIGHT:
            flake[0]=random.randint(0,WIDTH)
            flake[1]=0

    # Snow ground
    pygame.draw.rect(screen,(240,240,240),(0,HEIGHT-60,WIDTH,60))

    # Christmas lights
    for light in lights:
        glow = abs(math.sin(pygame.time.get_ticks()*0.002*light["pulse"]))
        color = tuple(min(255,int(c*glow)) for c in light["color"])
        pygame.draw.circle(screen,color,(light["x"],30),light["radius"])

    # Title with red/green layering
    title_shadow = intro_big.render("Collect GIFTS for santa!", True, (150,0,0))
    title_main = intro_big.render("Collect GIFTS for santa!", True, (0,255,0))
    screen.blit(title_shadow,(WIDTH//2-260,90))
    screen.blit(title_main,(WIDTH//2-255,85))

    # Press any key blinking
    if (pygame.time.get_ticks()//500)%2==0:
        press_text=intro_font.render("Press Any Key To Start",True,(255,255,255))
        screen.blit(press_text,(WIDTH//2-190,180))

    # Controls
    screen.blit(intro_font.render("Controls",True,(255,0,0)),(WIDTH//2-60,250))
    screen.blit(intro_font.render("W - Up",True,(255,255,255)),(250,300))
    screen.blit(intro_font.render("S - Down",True,(255,255,255)),(250,340))
    screen.blit(intro_font.render("A - Left",True,(255,255,255)),(500,300))
    screen.blit(intro_font.render("D - Right",True,(255,255,255)),(500,340))
    screen.blit(intro_font.render("Shift - Boost",True,(0,255,255)),(380,380))

    pygame.display.flip()

# ---------------- LOOP ----------------
running=True

while running:
    dt=clock.tick(60)

    for event in pygame.event.get():
        if (game_over or game_won) and event.type == pygame.KEYDOWN:
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
        if event.type==pygame.QUIT:
            running=False
        if not game_started and event.type==pygame.KEYDOWN:
            game_started=True

    if not game_started:
        draw_intro()
        continue

    if game_over or game_won:

        screen.fill((15, 25, 40))

        # Snowfall effect
        for flake in snowflakes:
            pygame.draw.circle(screen,(255,255,255),(flake[0],flake[1]),flake[2])
            flake[1]+=flake[2]*0.5
            if flake[1] > HEIGHT:
                flake[0]=random.randint(0,WIDTH)
                flake[1]=0

        if game_won:
            title = big_font.render("YOU SAVED CHRISTMAS!", True, (0,255,0))
            screen.blit(title,(WIDTH//2-260,80))

            # Animate Santa
            santa_timer += dt
            if santa_timer > 150:      # speed of animation
                santa_frame = (santa_frame + 1) % 4
                santa_timer = 0

            screen.blit(santa_happy_frames[santa_frame],
                        (WIDTH//2-125,150))
        else:
            title = big_font.render("CHRISTMAS IS RUINED!", True, (255,50,50))
            screen.blit(title,(WIDTH//2-260,80))
            screen.blit(santa_sad,(WIDTH//2-125,150))

        restart_text = font.render("Press R To Restart", True, (255,255,255))
        screen.blit(restart_text,(WIDTH//2-120,420))

        pygame.display.flip()
        continue

    # BACKGROUND
    if bg_img:
        screen.blit(bg_img,(0,0))
    else:
        screen.fill((30,60,50))

    # MOVEMENT
    keys=pygame.key.get_pressed()
    speed=player_speed

    moving=False

    if keys[pygame.K_LSHIFT] and stamina>0:
        speed=boost_speed
        stamina-=0.6
    else:
        stamina+=0.25

    stamina=max(0,min(100,stamina))

    if keys[pygame.K_w]:
        player.y-=speed
        moving=True
    if keys[pygame.K_s]:
        player.y+=speed
        moving=True
    if keys[pygame.K_a]:
        player.x-=speed
        moving=True
    if keys[pygame.K_d]:
        player.x+=speed
        moving=True

    player.clamp_ip(screen.get_rect())

    # PLAYER SPARKLES (golden behind player)
    if moving:
        for _ in range(2):
            player_sparkles.append(
                spawn_sparkle(player.centerx - 20,
                              player.centery,
                              (255,215,0))  # golden
            )

    for s in player_sparkles[:]:
        s["x"]+=s["vx"]
        s["y"]+=s["vy"]
        s["life"]-=1
        pygame.draw.circle(screen,s["color"],
                           (int(s["x"]),int(s["y"])),3)
        if s["life"]<=0:
            player_sparkles.remove(s)

    # RUN animation
    run_timer+=dt
    if run_timer>120:
        run_frame=(run_frame+1)%3
        run_timer=0

    # SPAWN
    spawn_timer+=1
    if spawn_timer>70:
        spawn_big()
        if random.random()<0.6: spawn_small()
        if random.random()<0.25: spawn_stamina()
        spawn_timer=0

    # UPDATE SMALL TARGETS
    for t in small_targets[:]:
        t["rect"].x-=5+level*0.5
        t["angle"]+=4

        rotated=pygame.transform.rotate(small_img,t["angle"])
        new_rect=rotated.get_rect(center=t["rect"].center)
        screen.blit(rotated,new_rect.topleft)

        # Red sparkles for small targets
        item_sparkles.append(
            spawn_sparkle(t["rect"].centerx,
                          t["rect"].centery,
                          (255,50,50))
        )

        if player.colliderect(t["rect"]):
            score+=5
            small_targets.remove(t)

        if t in small_targets and t["rect"].right<0:
            small_targets.remove(t)

    # UPDATE STAMINA
    for s_obj in stamina_targets[:]:
        s_obj["rect"].x-=5+level*0.5
        s_obj["angle"]+=5

        rotated=pygame.transform.rotate(stamina_img,s_obj["angle"])
        new_rect=rotated.get_rect(center=s_obj["rect"].center)
        screen.blit(rotated,new_rect.topleft)

        # Blue sparkles for stamina
        item_sparkles.append(
            spawn_sparkle(s_obj["rect"].centerx,
                          s_obj["rect"].centery,
                          (50,200,255))
        )

        if player.colliderect(s_obj["rect"]):
            stamina+=25
            stamina_targets.remove(s_obj)

        if s_obj in stamina_targets and s_obj["rect"].right<0:
            stamina_targets.remove(s_obj)

    # UPDATE BOMBS
    for b in bombs[:]:
        if b["state"]=="normal":
            b["rect"].x-=6+level*0.8

            # Gunpowder sparkles behind bomb
            for _ in range(2):
                bomb_sparkles.append(
                    spawn_sparkle(b["rect"].centerx+20,
                                  b["rect"].centery,
                                  (50,50,50))  # grey/black
                )

            if player.colliderect(b["rect"]):
                score-=10
                player_sad_timer=500
                b["state"]="explode"
                b["timer"]=300
        else:
            b["timer"]-=dt
            if b["timer"]<=0:
                bombs.remove(b)

        if b in bombs and b["rect"].right<0:
            bombs.remove(b)

    # BOMB SPARKLES
    for sp in bomb_sparkles[:]:
        sp["x"]+=sp["vx"]
        sp["y"]+=sp["vy"]
        sp["life"]-=1
        pygame.draw.circle(screen,sp["color"],
                           (int(sp["x"]),int(sp["y"])),2)
        if sp["life"]<=0:
            bomb_sparkles.remove(sp)

    if player_sad_timer>0:
        player_sad_timer-=dt

    # TIMER
    required_score = 40 + level * 10   # required presents

    timer -= 1
    if timer <= 0:
        if score >= required_score:
            level+=1
            if level>MAX_LEVEL:
                game_won=True
            else:
                timer=ROUND_TIME*60
                bombs.clear()
                small_targets.clear()
                stamina_targets.clear()
        else:
            game_over=True

    # DRAW PLAYER
    if player_sad_timer>0:
        screen.blit(sad_img,player.topleft)
    else:
        screen.blit(run_imgs[run_frame],player.topleft)

    # DRAW BOMBS
    for b in bombs:
        img=bomb_img if b["state"]=="normal" else bomb_explode_img
        screen.blit(img,b["rect"].topleft)

    # ITEM SPARKLES
    for sp in item_sparkles[:]:
        sp["x"]+=sp["vx"]
        sp["y"]+=sp["vy"]
        sp["life"]-=1
        pygame.draw.circle(screen,sp["color"],
                           (int(sp["x"]),int(sp["y"])),2)
        if sp["life"]<=0:
            item_sparkles.remove(sp)

    # UI
    sec=timer//60
    screen.blit(font.render(f"Level: {level}/8",True,(255,255,255)),(10,10))
    screen.blit(font.render(f"Score: {score}",True,(255,255,255)),(10,40))
    screen.blit(font.render(f"Presents Needed: {required_score}",True,(255,200,255)),(10,70))
    screen.blit(font.render(f"Time: {sec}s",True,(255,255,255)),(WIDTH-120,10))
    screen.blit(font.render(f"Stamina: {int(stamina)}",True,(255,255,255)),(WIDTH-160,40))

    pygame.display.flip()

pygame.quit()