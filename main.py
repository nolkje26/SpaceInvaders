import pygame, os, time, random
pygame.font.init()

# Set up pygame window 
# pygame.display.set_mode(<TUPPLE>), i.e., <TUPPLE> = (width, height)
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
# Caption
pygame.display.set_caption("Space Shooter")

# Load images

'''
pygame.image.load() : From the pygame module, use the image.load method
os.path.join(location, filename) : located in directory called assets w/ filename pixel_ship_red_small.png
os.path.join(location, filename) == location/filename, e.g. assets/pixel_ship_red_small.png
'''
RED_SPACESHIP_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACESHIP_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACESHIP_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#Player Ship
YELLOW_SPACESHIP_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Load lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Load background
BG = pygame.image.load(os.path.join("assets", "background-black.png"))
BG_RESIZED = pygame.transform.scale(BG, (WIDTH, HEIGHT))

# -----------------------------------------------------------------------------------------------------

class Ship:
    COOLDOWN = 30 # half a second
    
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

    def move_laser(self, vel, obj):
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
        super().__init__(x, y, health) # uses Ship's initialization method 
        self.ship_img = YELLOW_SPACESHIP_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) # Take ship_img and make a mask of it - a mask lets us do pixel perfect collision
        self.max_health = health

    def move_laser(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs: # for every enemy ship, check if laser has collided with ship. If so, remove the ship and laser
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):

    # COLOR_MAP = class variable
    COLOR_MAP = {
                "red" : (RED_SPACESHIP_SHIP, RED_LASER), 
                "green" : (GREEN_SPACESHIP_SHIP, GREEN_LASER), 
                "blue" : (BLUE_SPACESHIP_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    # Enemey ships will move down the screen
    def move(self, vel):
        self.y += vel

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
        return not(self.y < height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

def collide(obj1, obj2):
    ''' 
    In order to know if objects are overlapping, you need to come up witha an offset. An offset tells us the distance between the two top-left corners
    of the objects. If they intersect, you'll get a tuple of where they intersected; otherwise it'll return None
    '''
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1 .mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Create a main loop that handles all the events, i.e., collisions, actions, quite game, etc.
def main():
    run = True # dictates wheter loop will run or not
    FPS = 60 # Frames Per Second - the higher the number, the faster game runs; the lower the number, the slower the game runs
    lost_seconds = 3 # number of seconds to show lost message
    clock = pygame.time.Clock() 

    # Player
    level = 0
    lives = 5
    player_vel = 5 # velocity (you can move 5 pixels per click)
    player = Player(300, 630)
    lost = False
    lost_count = 0
    player_laser_vel = -5

    # Text
    ''' 
    How can we draw text to a window? 
    Place at the top of page: pygame.font.init()

    Create a font object in pygame:
    pygame.font.SysFont(<fontname>, <size>) 
    '''
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    # Enemies
    enemies = [] # where enemies are stored
    wave_length = 5 # starting number of enemies
    enemy_vel = 1 # starting velocity of enemies
    enemy_laser_vel = 8

    '''
    How redrawing/refreshing window works:
    We have a bunch of things called "surfaces."
    These surfaces can be drawn on. We can "blit" things on to them, i.e., put an image on to it
    How it works ideally: we have one surface and everytime we loop (60 times a second) we're going to redraw everything on to the screen and then 
    refresh it so it has the updated version, so the first thing we have to do since we have to redraw everything is draw a background image as our first
    thing, so what will do is it will cover any stuff that was behind or drawn before and then we draw everything on top of that background image that's 
    going to be shown for the next frame.
    '''
    def redraw_window():
        # Take coord (0,0) and redraw (blits) BG image
        WIN.blit(BG_RESIZED, (0,0))  
        # draw text .render(<text>, 1, <RGB>)
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        # updates display
        WIN.blit(lives_label, (10, 10))
        # .get_width() gets width of text label
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # draw enemy ships
        for enemy in enemies:
            enemy.draw(WIN)

        # draw ship
        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You lost!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        # this checks events "60" times per second (according to FPS)
        # Every time we run this loop (60 times every second), we're going to loop through every event that pygame knows and check if an event has occured
        # If the event has occured, do something
        clock.tick(FPS) 
        redraw_window()

        # Checks if player has lost: increment level and amount of enemies 
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        # Action after player loses
        if lost:
            if lost_count > FPS * lost_seconds:
                run = False
            else:
                continue
        
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                quit()
        ''' 
        pygame.key.get_pressed() returns a dictionary of all of the keys and tells you whether they are pressed or not at the current time. 
        Since it runs 60 times every second, it'll check if we're pressing a key, if we are, we'll move in specified direction
        '''
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_vel > 0 : # left
            player.x -= player_vel # move player_vel pixels 
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_vel > 0: # up
            player.y -= player_vel
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_laser(enemy_laser_vel, player)

            if random.randrange(0, FPS) == 1:
                enemy.shoot()
            
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        

        player.move_laser(player_laser_vel, enemies) 

# Whent to start/end game
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True

    while run: 
        WIN.blit(BG_RESIZED, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()
    
main_menu()
