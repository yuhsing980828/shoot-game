import pygame
import sys
import random
import os
import pytmx

FPS = 60

WIDTH = 1512
HEIGHT = 810

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("game")
clock = pygame.time.Clock()
now = pygame.time.get_ticks()


# 設定資源路徑(取得目前執行的 Python 檔案的所在資料夾路徑)
current_dir = os.path.dirname(os.path.abspath(__file__))
map_data = pytmx.load_pygame(os.path.join(current_dir, "map_embedded.tmx")) # 載入地圖

# 確保所有圖片路徑正確
for tileset in map_data.tilesets:
    if tileset.source: # 檢查這個 tileset 是否有設定來源檔案路徑
        image_path = os.path.join(current_dir, os.path.basename(tileset.source)) # 組合圖像路徑(os.path.basename()為取出檔名)
        if os.path.exists(image_path): # 若圖像檔路徑存在
            tileset.source = image_path # 更新來源為該路徑

wall_rects = []

for layer in map_data.objectgroups: # 遍歷物件層
    if layer.name == "物件層 1":
        for obj in layer: # 遍歷物件
            wall_rects.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height)) # 每個物件轉換為矩形物件


# 載入玩家圖片
playerA_img = pygame.image.load(os.path.join("image", "playerA.png")).convert()

playerA_img = pygame.transform.scale(playerA_img, (50, 50))
playerA_img.set_colorkey((BLACK))

playerA_right_img = playerA_img
playerA_left_img = pygame.transform.flip(playerA_img, True, False)

playerB_img = pygame.image.load(os.path.join("image", "playerB.png")).convert()

playerB_img = pygame.transform.scale(playerB_img, (50, 50))
playerB_img.set_colorkey((BLACK))

playerB_right_img = playerB_img
playerB_left_img = pygame.transform.flip(playerB_img, True, False)


# 載入生命數圖片
lives_img = pygame.image.load(os.path.join("image", "heart.png")).convert()
lives_img = pygame.transform.scale(lives_img, (40, 40))
lives_img.set_colorkey((BLACK))

# 載入buff圖片
buff_img = {}
buff_lightning_img = pygame.image.load(os.path.join("image", "buff_lightning.png")).convert()
buff_sword_img = pygame.image.load(os.path.join("image", "buff_sword.png")).convert()
buff_shield_img = pygame.image.load(os.path.join("image", "buff_shield.png")).convert()

buff_lightning_img = pygame.transform.scale(buff_lightning_img, (30, 30))
buff_sword_img = pygame.transform.scale(buff_sword_img, (30, 30))
buff_shield_img = pygame.transform.scale(buff_shield_img, (30, 30))

buff_lightning_img.set_colorkey(BLACK)
buff_sword_img.set_colorkey(BLACK)
buff_shield_img.set_colorkey(BLACK)

buff_img["lightning"] = buff_lightning_img
buff_img["sword"] = buff_sword_img
buff_img["shield"] = buff_shield_img

chest_img = pygame.image.load(os.path.join("image", "chest_generation_3.png")).convert()
chest_img = pygame.transform.scale(chest_img, (53, 53))
chest_img.set_colorkey(BLACK)

# 載入寶箱動畫
chest_anim = {}
chest_anim["generation"] = [] # 寶箱生成動畫
chest_anim["disappear"] = [] # 寶箱消失動畫

for i in range(4):
    generation_img = pygame.image.load(os.path.join("image", f"chest_generation_{i}.png")).convert()
    generation_img.set_colorkey(BLACK)
    chest_anim["generation"].append(pygame.transform.scale(generation_img, (30, 30)))
    disappear_img = pygame.image.load(os.path.join("image", f"chest_disappear_{i}.png")).convert()
    disappear_img.set_colorkey(BLACK)
    chest_anim["disappear"].append(pygame.transform.scale(disappear_img, (30, 30)))



# 設定一個事件(寶箱生成), 每隔一段隨機時間觸發
ADD_CHESTS_EVENT = pygame.USEREVENT + 1  
pygame.time.set_timer(ADD_CHESTS_EVENT, random.randint(10000, 20000))

# 確認目前是否在射擊
playerA_is_not_shooting = True
playerB_is_not_shooting = True

font_name = os.path.join("font.ttf")
def draw_text(surf, text, size, x, y, color):
    font = pygame.font.Font(font_name, size)  # 建立一個指定大小的字體對象        
    text_surface = font.render(text, True, color)  # 將文字渲染成圖像
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)         

def draw_init():
    screen.fill(BLACK)
    draw_text(screen, "SHOOT GAME", 64, WIDTH/2, HEIGHT/4, WHITE)
    draw_text(screen, "PlayerA: WASD移動, LIJK射擊", 22, WIDTH/2, HEIGHT/2, WHITE)
    draw_text(screen, "PlayerB: 方向鍵移動, 數字鍵射擊", 22, WIDTH/2, HEIGHT/2 + 40, WHITE)
    draw_text(screen, "按任意鍵開始遊戲!", 22, WIDTH/2, HEIGHT*3/4, WHITE)

def draw_win(x, y):
    # 創建半透明遮罩
    overlay = pygame.Surface((WIDTH//2, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # 半透明黑色
    screen.blit(overlay, (x, y))
    draw_text(screen, "WIN", 64, x + WIDTH//4, HEIGHT//2, GREEN)
    draw_text(screen, "按任意鍵再玩一次", 22, x + WIDTH//4, HEIGHT*3/4, WHITE)

def draw_lose(x, y):    
    # 創建半透明遮罩
    overlay = pygame.Surface((WIDTH//2, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # 半透明黑色
    screen.blit(overlay, (x, y))
    draw_text(screen, "LOSE", 64, x + WIDTH//4, HEIGHT//2, RED)
    draw_text(screen, "按任意鍵再玩一次", 22, x + WIDTH//4, HEIGHT*3/4, WHITE)

def draw_respawn_overlay(x, y, remaining_time):
    overlay = pygame.Surface((WIDTH//2, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # 半透明黑色
    screen.blit(overlay, (x, y))
    draw_text(screen, f"復活倒數: {remaining_time}秒", 32, x + WIDTH//4, HEIGHT//2, WHITE)

def draw_map(surf):
    for layer in map_data.visible_layers: # 取得所有可見圖層
        if isinstance(layer, pytmx.TiledTileLayer): # 避免誤處理物件圖層或圖片圖層
            for x, y, gid in layer: # x, y 格子座標 , git(global id) 圖像id
                tile = map_data.get_tile_image_by_gid(gid) # 根據git取得對應的圖像
                if tile: # 確保非空白
                    pos = (x*map_data.tilewidth, y*map_data.tileheight) # 把格子座標轉成實際座標
                    surf.blit(tile, pos)

def draw_hp(surf, hp, length, height, x, y, hp_fill):
    if hp < 0:
        hp = 0
    fill = (hp/hp_fill)*length # hp_fill 滿血時血量
    outline_rect = pygame.Rect(x, y, length, height)  
    fill_rect = pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 33*i
        img_rect.y = y
        surf.blit(img, img_rect)
    
class PlayerA(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = playerA_right_img
        self.rect = self.image.get_rect()  
        self.rect.centerx = 40
        self.rect.centery = HEIGHT/2
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.speedx = 3 * self.speed_multiplier
        self.speedy = 3 * self.speed_multiplier
        self.last_shoot_time = 0
        self.shoot_delay = 250
        self.hp = 100
        self.lives = 3
        self.death_count = 0 
        self.hidden = False
        self.hide_time = 0
        self.attack = 10
        self.respawn_time = 0
        self.is_respawning = False
        
    def update(self):
        if self.is_respawning:
            current_time = pygame.time.get_ticks()
            if current_time - self.respawn_time >= 5000:  # 5秒後復活
                self.is_respawning = False
                self.hidden = False
                self.rect.centerx = 40
                self.rect.centery = HEIGHT/2
                self.hp = 100
            return

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = 40
            self.rect.bottom = HEIGHT/2
        old_rect = self.rect.copy()
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_d]:
            if playerA_is_not_shooting == True:
                playerA.image = playerA_right_img
            self.rect.x += self.speedx * self.speed_multiplier
        if key_pressed[pygame.K_a]:
            if playerA_is_not_shooting == True:
                playerA.image = playerA_left_img
            self.rect.x -= self.speedx * self.speed_multiplier
        if key_pressed[pygame.K_w]:
            self.rect.y -= self.speedy * self.speed_multiplier
        if key_pressed[pygame.K_s]:
            self.rect.y += self.speedy * self.speed_multiplier

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        # 玩家碰撞判定
        if self.rect.colliderect(playerB.rect):
            self.rect = old_rect  

        # 牆壁碰撞判定
        if any (self.rect.colliderect(wall) for wall in wall_rects):
            self.rect = old_rect

        # 寶箱碰撞判定
        if any (self.rect.colliderect(chest.rect) for chest in chests):
            self.rect = old_rect

    def shoot_UP(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, 0, -20, self)
        all_sprites.add(bullet)   
        bullets.add(bullet)

    def shoot_DOWN(self):
        bullet = Bullet(self.rect.centerx, self.rect.bottom, 0, 20, self)
        all_sprites.add(bullet)   
        bullets.add(bullet) 

    def shoot_LEFT(self):
        bullet = Bullet(self.rect.left, self.rect.centery, -20, 0, self)
        all_sprites.add(bullet)   
        bullets.add(bullet)

    def shoot_RIGHT(self):
        bullet = Bullet(self.rect.right, self.rect.centery, 20, 0, self)
        all_sprites.add(bullet)   
        bullets.add(bullet)      

    def respawn(self):
        self.is_respawning = True
        self.respawn_time = pygame.time.get_ticks()
        self.hidden = True
        self.rect.center = (WIDTH/2, HEIGHT+500)

class PlayerB(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = playerB_left_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH - 40
        self.rect.centery = HEIGHT/2
        self.speed_multiplier = 1.0  
        self.damage_multiplier = 1.0
        self.speedx = 3 * self.speed_multiplier
        self.speedy = 3 * self.speed_multiplier
        self.last_shoot_time = 0
        self.shoot_delay = 250
        self.hp = 100
        self.lives = 3 
        self.death_count = 0
        self.hidden = False
        self.hide_time = 0
        self.attack = 10
        self.respawn_time = 0
        self.is_respawning = False
        
    def update(self):
        if self.is_respawning:
            current_time = pygame.time.get_ticks()
            if current_time - self.respawn_time >= 5000:  # 5秒後復活
                self.is_respawning = False
                self.hidden = False
                self.rect.centerx = WIDTH - 40
                self.rect.centery = HEIGHT/2
                self.hp = 100
            return

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH - 40
            self.rect.bottom = HEIGHT/2
        old_rect = self.rect.copy()
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            if playerB_is_not_shooting == True:
                playerB.image = playerB_right_img
            self.rect.x += self.speedx * self.speed_multiplier
        if key_pressed[pygame.K_LEFT]:
            if playerB_is_not_shooting == True:
                playerB.image = playerB_left_img
            self.rect.x -= self.speedx * self.speed_multiplier
        if key_pressed[pygame.K_UP]:
            self.rect.y -= self.speedy * self.speed_multiplier
        if key_pressed[pygame.K_DOWN]:
            self.rect.y += self.speedy * self.speed_multiplier

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        # 玩家碰撞判定
        if self.rect.colliderect(playerA.rect):
            self.rect = old_rect   

        # 牆壁碰撞判定
        if any (self.rect.colliderect(wall) for wall in wall_rects):
            self.rect = old_rect

        # 寶箱碰撞判定
        if any (self.rect.colliderect(chest.rect) for chest in chests):
            self.rect = old_rect

    def shoot_UP(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, 0, -20, self)
        all_sprites.add(bullet)   
        bullets.add(bullet)

    def shoot_DOWN(self):
        bullet = Bullet(self.rect.centerx, self.rect.bottom, 0, 20, self)
        all_sprites.add(bullet)   
        bullets.add(bullet) 

    def shoot_LEFT(self):
        bullet = Bullet(self.rect.left, self.rect.centery, -20, 0, self)
        all_sprites.add(bullet)   
        bullets.add(bullet)

    def shoot_RIGHT(self):
        bullet = Bullet(self.rect.right, self.rect.centery, 20, 0, self)
        all_sprites.add(bullet)   
        bullets.add(bullet)

    def respawn(self):
        self.is_respawning = True
        self.respawn_time = pygame.time.get_ticks()
        self.hidden = True
        self.rect.center = (WIDTH/2, HEIGHT+500)

class Bullet (pygame.sprite.Sprite):  
    def __init__(self, x, y, dx, dy, owner):               
        super().__init__()  
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()  
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedx = dx
        self.speedy = dy
        self.owner = owner
        self.damage = 10 * owner.damage_multiplier  # 根據傷害倍率計算傷害
        

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.bottom < 0 or self.rect.bottom > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
        if any (self.rect.colliderect(wall) for wall in wall_rects):
            self.kill()

class Treasure_chest(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = chest_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH-self.rect.width)
        self.rect.y = random.randint(0, HEIGHT-self.rect.height)
        self.hp = 25     

class Buff (pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.type = random.choice(["lightning", "sword", "shield"])
        self.image = buff_img[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
    
class anim (pygame.sprite.Sprite):  
    def __init__(self, center, size):               
        pygame.sprite.Sprite.__init__(self)  
        self.size = size
        self.image = chest_anim[self.size][0]
        self.rect = self.image.get_rect()  
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(chest_anim[self.size]):
                self.kill()
            else:
                self.image = chest_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect() 
                self.rect.center = center 

playerA = PlayerA()
playerB = PlayerB()
chest = Treasure_chest()
chests = pygame.sprite.Group()
bullets = pygame.sprite.Group()
buffs = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(playerA)
all_sprites.add(playerB)
running = True

# 遊戲狀態
GAME_INIT = 0
GAME_RUNNING = 1
GAME_OVER = 2

game_state = GAME_INIT
winner = None

# 主遊戲迴圈
while running:
    now = pygame.time.get_ticks()
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if game_state == GAME_INIT:
                if event.key != pygame.K_ESCAPE:
                    game_state = GAME_RUNNING
                    # 重置遊戲狀態
                    playerA = PlayerA()
                    playerB = PlayerB()
                    all_sprites = pygame.sprite.Group()
                    all_sprites.add(playerA)
                    all_sprites.add(playerB)
                    chests = pygame.sprite.Group()
                    bullets = pygame.sprite.Group()
                    buffs = pygame.sprite.Group()
                    
            elif game_state == GAME_OVER:
                if event.key != pygame.K_ESCAPE:
                    game_state = GAME_INIT
                    
            if event.key == pygame.K_ESCAPE:
                running = False
                
            # 遊戲運行時處理射擊按鍵
            if game_state == GAME_RUNNING:
                if event.key == pygame.K_i and playerA_is_not_shooting and now - playerA.last_shoot_time > playerA.shoot_delay and playerA.lives > 0:
                    playerA.shoot_UP()
                    playerA_is_not_shooting = False
                    playerA.last_shoot_time = now
                if event.key == pygame.K_j and playerA_is_not_shooting and now - playerA.last_shoot_time > playerA.shoot_delay and playerA.lives > 0:
                    playerA.shoot_LEFT()
                    playerA.image = playerA_left_img
                    playerA_is_not_shooting = False
                    playerA.last_shoot_time = now
                if event.key == pygame.K_l and playerA_is_not_shooting and now - playerA.last_shoot_time > playerA.shoot_delay and playerA.lives > 0:
                    playerA.shoot_RIGHT()
                    playerA.image = playerA_right_img
                    playerA_is_not_shooting = False
                    playerA.last_shoot_time = now
                if event.key == pygame.K_k and playerA_is_not_shooting and now - playerA.last_shoot_time > playerA.shoot_delay and playerA.lives > 0:
                    playerA.shoot_DOWN()
                    playerA_is_not_shooting = False
                    playerA.last_shoot_time = now

                if event.key == pygame.K_KP8 and playerB_is_not_shooting and now - playerB.last_shoot_time > playerB.shoot_delay and playerB.lives > 0:
                    playerB.shoot_UP()
                    playerB_is_not_shooting = False
                    playerB.last_shoot_time = now
                if event.key == pygame.K_KP4 and playerB_is_not_shooting and now - playerB.last_shoot_time > playerB.shoot_delay and playerB.lives > 0:
                    playerB.shoot_LEFT()
                    playerB.image = playerB_left_img
                    playerB_is_not_shooting = False
                    playerB.last_shoot_time = now
                if event.key == pygame.K_KP6 and playerB_is_not_shooting and now - playerB.last_shoot_time > playerB.shoot_delay and playerB.lives > 0:
                    playerB.shoot_RIGHT()
                    playerB.image = playerB_right_img
                    playerB_is_not_shooting = False
                    playerB.last_shoot_time = now
                if event.key == pygame.K_KP2 and playerB_is_not_shooting and now - playerB.last_shoot_time > playerB.shoot_delay and playerB.lives > 0:
                    playerB.shoot_DOWN()
                    playerB_is_not_shooting = False
                    playerB.last_shoot_time = now

        elif event.type == pygame.KEYUP:
            if game_state == GAME_RUNNING:
                if event.key in(pygame.K_i, pygame.K_j, pygame.K_l, pygame.K_k):
                    playerA_is_not_shooting = True
                if event.key in(pygame.K_KP8, pygame.K_KP4, pygame.K_KP6, pygame.K_KP2):
                    playerB_is_not_shooting = True
                    
        # 遊戲運行時處理寶箱生成事件
        if game_state == GAME_RUNNING and event.type == ADD_CHESTS_EVENT:
            for i in range(random.randint(2, 3)):
                while True:
                    chest = Treasure_chest()
                    if chest.rect.colliderect(playerA.rect) or chest.rect.colliderect(playerB.rect) or any (chest.rect.colliderect(wall) for wall in wall_rects):
                        continue
                    else:
                        generation = anim(chest.rect.center, "generation")
                        chests.add(chest)
                        all_sprites.add(chest)
                        all_sprites.add(generation)
                        break
            pygame.time.set_timer(ADD_CHESTS_EVENT, random.randint(10000, 20000))

    # 根據遊戲狀態更新畫面
    screen.fill(WHITE)
    
    if game_state == GAME_INIT:
        draw_init()
        
    elif game_state == GAME_RUNNING:
        # 射擊時,移速歸零
        if playerA_is_not_shooting:
            playerA.speedx = 2.5 * playerA.speed_multiplier
            playerA.speedy = 2.5 * playerA.speed_multiplier
        else:
            playerA.speedx = 0
            playerA.speedy = 0       

        if playerB_is_not_shooting:
            playerB.speedx = 2.5 * playerB.speed_multiplier
            playerB.speedy = 2.5 * playerB.speed_multiplier
        else:
            playerB.speedx = 0
            playerB.speedy = 0     

        all_sprites.update()

        # 玩家, 子彈碰撞判定
        hits = pygame.sprite.spritecollide(playerA, bullets, True, pygame.sprite.collide_rect)
        for hit in hits:
            if hit.owner != playerA:
                playerA.hp -= hit.damage
                if playerA.hp <= 0:
                    playerA.death_count += 1
                    if playerA.death_count < 3:
                        playerA.lives -= 1
                        playerA.respawn()
                    else:
                        playerA.hp = 0
                        playerA.kill()
                        playerA.hidden = True
                        game_state = GAME_OVER
                        winner = "PlayerB"

        hits = pygame.sprite.spritecollide(playerB, bullets, True, pygame.sprite.collide_rect)
        for hit in hits:
            if hit.owner != playerB:
                playerB.hp -= hit.damage
                if playerB.hp <= 0:
                    playerB.death_count += 1
                    if playerB.death_count < 3:
                        playerB.lives -= 1
                        playerB.respawn()
                    else:
                        playerB.hp = 0
                        playerB.kill()
                        playerB.hidden = True
                        game_state = GAME_OVER
                        winner = "PlayerA"

        # 寶箱, 子彈碰撞判定
        for chest in chests:
            hits = pygame.sprite.spritecollide(chest, bullets, True, pygame.sprite.collide_rect)
            for hit in hits:
                chest.hp -= 5
                if chest.hp <= 0:
                    disappear = anim(hit.rect.center, "disappear")
                    all_sprites.add(disappear)
                    chests.remove(chest)
                    chest.kill()
                    buff = Buff(hit.rect.center)
                    all_sprites.add(buff)
                    buffs.add(buff)

        # 寶物, 玩家碰撞判定
        hits = pygame.sprite.spritecollide(playerA, buffs, True, pygame.sprite.collide_rect)
        for hit in hits:
            if hit.type == "shield":
                playerA.hp += 25
                if playerA.hp > 100:
                    playerA.hp = 100
            elif hit.type == "lightning":
                playerA.speed_multiplier = 1.5  # 增加50%移動速度
                pygame.time.set_timer(pygame.USEREVENT + 2, 0) # 重置時間
                pygame.time.set_timer(pygame.USEREVENT + 2, 5000)  # 5秒後恢復
            elif hit.type == "sword":
                playerA.damage_multiplier = 1.5  # 增加50%傷害
                pygame.time.set_timer(pygame.USEREVENT + 3, 0) # 重置時間
                pygame.time.set_timer(pygame.USEREVENT + 3, 5000)  # 5秒後恢復

        hits = pygame.sprite.spritecollide(playerB, buffs, True, pygame.sprite.collide_rect)
        for hit in hits:
            if hit.type == "shield":
                playerB.hp += 25
                if playerB.hp > 100:
                    playerB.hp = 100
            elif hit.type == "lightning":
                playerB.speed_multiplier = 1.5  # 增加50%移動速度
                pygame.time.set_timer(pygame.USEREVENT + 4, 0) # 重置時間
                pygame.time.set_timer(pygame.USEREVENT + 4, 5000)  # 5秒後恢復
            elif hit.type == "sword":
                playerB.damage_multiplier = 1.5  # 增加50%傷害
                pygame.time.set_timer(pygame.USEREVENT + 5, 0) # 重置時間
                pygame.time.set_timer(pygame.USEREVENT + 5, 5000)  # 5秒後恢復

        # buff 結束處理
        if event.type == pygame.USEREVENT + 2:  # playerA lightning buff結束
            playerA.speed_multiplier = 1.0
        elif event.type == pygame.USEREVENT + 3:  # playerA sword buff結束
            playerA.damage_multiplier = 1.0
        elif event.type == pygame.USEREVENT + 4:  # playerB lightning buff結束
            playerB.speed_multiplier = 1.0
        elif event.type == pygame.USEREVENT + 5:  # playerB sword buff結束
            playerB.damage_multiplier = 1.0

        # 繪製遊戲畫面
        draw_map(screen)
        all_sprites.draw(screen)
        draw_hp(screen, playerA.hp, 150, 10, 5, 45, 100)
        draw_hp(screen, playerB.hp, 150, 10, WIDTH-155, 45, 100)
        for chest in chests:
            draw_hp(screen, chest.hp, 75, 10, chest.rect.x-20, chest.rect.y-20, 25)
        draw_lives(screen, playerA.lives,lives_img, 5, 5)
        draw_lives(screen, playerB.lives,lives_img, WIDTH-105, 5)

        # 血條跟隨
        draw_hp(screen, playerA.hp, 75, 10, playerA.rect.x-20, playerA.rect.y-20, 100)
        draw_hp(screen, playerB.hp, 75, 10, playerB.rect.x-20, playerB.rect.y-20, 100)

        draw_text(screen, "PlayerA", 16, playerA.rect.x+20, playerA.rect.y-45, BLACK)
        draw_text(screen, "PlayerB", 16, playerB.rect.x+20, playerB.rect.y-45, BLACK)
        
        # 復活倒數
        if playerA.is_respawning:
            remaining_time = 5 - (pygame.time.get_ticks() - playerA.respawn_time) // 1000
            if remaining_time > 0:
                draw_respawn_overlay(0, 0, remaining_time)
        
        if playerB.is_respawning:
            remaining_time = 5 - (pygame.time.get_ticks() - playerB.respawn_time) // 1000
            if remaining_time > 0:
                draw_respawn_overlay(WIDTH//2, 0, remaining_time)

    elif game_state == GAME_OVER:
        draw_map(screen)
        
        # 隱藏玩家和寶箱
        for sprite in all_sprites:
            if isinstance(sprite, (PlayerA, PlayerB, Treasure_chest, Buff)):
                sprite.kill()
        
        # 顯示勝敗畫面
        if winner == "PlayerA":
            draw_win(0, 0)
            draw_lose(WIDTH//2, 0)
        else:
            draw_win(WIDTH//2, 0)
            draw_lose(0, 0)

    pygame.display.flip()

pygame.quit()
sys.exit()