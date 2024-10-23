import pygame
import os
import time
import random
import sys

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Tutorial")

# Load images for the game
# Enemies
ENEMY_1 = pygame.image.load(os.path.join("assets", "Enemy_1.png"))
ENEMY_2 = pygame.image.load(os.path.join("assets", "Enemy_2.png"))
ENEMY_3 = pygame.image.load(os.path.join("assets", "Enemy_3.png"))

# Player
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "Player_1.png"))

# Bullets 
# Player
PLAYER_LASER = pygame.image.load(os.path.join("assets", "player_laser.png"))

# Enemies
MISSILE_GREEN = pygame.image.load(os.path.join("assets", "Missile_1.png"))
MISSILE_BLUE = pygame.image.load(os.path.join("assets", "Missile_2.png"))
MISSILE_RED = pygame.image.load(os.path.join("assets", "Missile_3.png"))


# Load parallax backgrounds (your custom backgrounds)
backgrounds = [
    pygame.image.load(os.path.join("assets", "prx-1.png")).convert_alpha(),
    pygame.image.load(os.path.join("assets", "prx-2.png")).convert_alpha(),
    pygame.image.load(os.path.join("assets", "prx-3.png")).convert_alpha(),
    pygame.image.load(os.path.join("assets", "prx-4.png")).convert_alpha(),
    pygame.image.load(os.path.join("assets", "prx-5.png")).convert_alpha(),
]

# Set Parallax Speed
speeds = [0.1, 0.3, 0.5, 0.7, 0.9]

# Set Background Opacity
opacities = [255, 220, 200, 180, 160]

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = pygame.transform.smoothscale(PLAYER_SHIP, (60, 60))  # Ubah Ukuran Sprite Player
        self.laser_img = pygame.transform.smoothscale(PLAYER_LASER, (10, 40)) # Ubah ukuran laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.hit_timer = 0  # Timer for hit effect
        self.shake_timer = 0  # Timer for screen shake effect

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
        shake_x = 0
        shake_y = 0

        if self.shake_timer > 0:
            shake_x = random.randint(-5, 5)  # Random shake offset
            shake_y = random.randint(-5, 5)  # Random shake offset
            self.shake_timer -= 1  # Decrease shake timer
            
        # Create a white tint effect when hit
        if self.hit_timer > 0:
            tint_surface = pygame.Surface(self.ship_img.get_size())
            tint_surface.fill((255, 255, 255))  # Fill with white
            window.blit(self.ship_img, (self.x + shake_x, self.y + shake_y))  # Draw original sprite
            window.blit(tint_surface, (self.x + shake_x, self.y + shake_y), special_flags=pygame.BLEND_ADD)
            self.hit_timer -= 1  # Decrease hit timer
        else:
            window.blit(self.ship_img, (self.x + shake_x, self.y + shake_y))  # Draw normal sprite

        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))

    def shoot(self):
        if self.cool_down_counter == 0:

            # Pusatkan laser di tengah sprite
            laser_x = self.x + (self.get_width() // 2) - (self.laser_img.get_width() // 2)
            laser = Laser(laser_x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Enemy(Ship):
    COLOR_MAP = {
        "red": (ENEMY_1, MISSILE_RED),
        "green": (ENEMY_2, MISSILE_GREEN),
        "blue": (ENEMY_3, MISSILE_BLUE)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        
        self.ship_img = pygame.transform.smoothscale(self.COLOR_MAP[color][0], (80, 80))
        self.laser_img = pygame.transform.smoothscale(self.COLOR_MAP[color][1], (25, 25))  # Ubah ukuran peluru/laser musuh jika diperlukan
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            # Pusatkan laser di tengah sprite
            laser_x = self.x + (self.get_width() // 2) - (self.laser_img.get_width() // 2)
            laser = Laser(laser_x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Parallax drawing function
def draw_backgrounds(screen, scroll_y):
    for i, background in enumerate(backgrounds):
        # Create surface with alpha transparency
        surface = pygame.Surface(background.get_size(), pygame.SRCALPHA)
        surface.blit(background, (0, 0))
        
        # Set opacity for each layer
        surface.set_alpha(opacities[i])
        
        # Repeat background with vertical scrolling
        relative_y = scroll_y * speeds[i] % background.get_rect().height
        screen.blit(surface, (0, relative_y - background.get_rect().height))
        screen.blit(surface, (0, relative_y))

def main():
    # Set Background Music
    pygame.mixer.music.load(os.path.join("assets", "space.mp3"))  # Pastikan file musik ada di folder 'assets'
    pygame.mixer.music.set_volume(0.3)  # Atur volume musik
    pygame.mixer.music.play(-1)  # Putar musik secara berulang

    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    scroll_y = 0  # Initial scroll value

    def redraw_window():
        # Draw parallax background
        draw_backgrounds(WIN, scroll_y)

        # Draw game elements
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        # Scroll background
        scroll_y += 2  # Adjust the scroll speed

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        # Ambil salah satu background dari daftar, misal background pertama
        WIN.blit(backgrounds[0], (0, 0))
        
        # Tampilkan teks di tengah layar
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()
