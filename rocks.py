# program name:	rocks.pyw
# programmer:	Bennett Wenger
# date:		    2016, 2023

# ROCKS
# A modification of 'Astrocrash'

# imports
import math, random, time, pygame
from superwires import games, color

# initiate game screen
games.init(screen_width = 800, screen_height = 600, fps = 50)

# wrapper class
class Wrapper(games.Sprite):
    def update(self):
        if self.top > games.screen.height:
            self.bottom = 0

        if self.bottom < 0:
            self.top = games.screen.height

        if self.left > games.screen.width:
            self.right = 0

        if self.right < 0:
            self.left = games.screen.width

    def die(self):
        self.destroy()

# collider class
class Collider(Wrapper):
    def update(self):
        super(Collider, self).update()

        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                sprite.die()
            self.die()

    def die(self):
        new_explosion = Explosion(x = self.x, y = self.y)
        games.screen.add(new_explosion)
        self.destroy()

# explosion class
class Explosion(games.Animation):
    sound = games.load_sound("lib\\snd\\explosion.ogg")
    images = ["lib\\img\\explosion1.png",
              "lib\\img\\explosion2.png",
              "lib\\img\\explosion3.png",
              "lib\\img\\explosion4.png",
              "lib\\img\\explosion5.png",
              "lib\\img\\explosion6.png",
              "lib\\img\\explosion7.png",
              "lib\\img\\explosion8.png",
              "lib\\img\\explosion9.png"]

    def __init__(self, x, y):
        super(Explosion, self).__init__(images = Explosion.images,
                                        x = x, y = y,
                                        repeat_interval = 4,
                                        n_repeats = 1,
                                        is_collideable = False)
        Explosion.sound.play()

# rock class
class Rock(Wrapper):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    images = {SMALL  : games.load_image("lib\\img\\asteroid_small.png"),
              MEDIUM : games.load_image("lib\\img\\asteroid_med.png"),
              LARGE  : games.load_image("lib\\img\\asteroid_big.png")}
    
    SPEED = 2
    SPAWN = 2
    POINTS = 30

    total = 0

    def __init__(self, game, x, y, size):
        Rock.total += 1
        super(Rock, self).__init__(
            image = Rock.images[size],
            x = x, y = y,
            dx = random.choice([1, -1]) * Rock.SPEED * random.random()/size,
            dy = random.choice([1, -1]) * Rock.SPEED * random.random()/size)
        
        self.size = size
        self.game = game        

    def die(self):
        Rock.total -= 1
        self.game.score.value += int(Rock.POINTS / self.size)
        self.game.score.right = games.screen.width - 20
        if self.size != Rock.SMALL:
            for i in range(Rock.SPAWN):
                new_rock = Rock(game = self.game,
                                x = self.x, y = self.y,
                                size = self.size - 1)
                games.screen.add(new_rock)
        if Rock.total == 0:
            self.game.advance()
            
        super(Rock, self).die()

# ship class
class Ship(Collider):
    image = games.load_image("lib\\img\\ship.png")
    sound = games.load_sound("lib\\snd\\thrust.ogg")
    ROTATION_STEP = 3
    VELOCITY_STEP = .03
    MISSILE_DELAY = 10
    VELOCITY_MAX = 3

    def __init__(self, game, x, y):
        super(Ship, self).__init__(image = Ship.image, x = x, y = y)
        self.game = game
        self.missile_wait = 0

    def update(self):
        super(Ship, self).update()
        
        if self.missile_wait > 0:
            self.missile_wait -= 1
            
        if games.keyboard.is_pressed(games.K_LEFT):
            self.angle -= Ship.ROTATION_STEP
            
        if games.keyboard.is_pressed(games.K_RIGHT):
            self.angle += Ship.ROTATION_STEP
            
        if games.keyboard.is_pressed(games.K_UP):
            Ship.sound.play()
            angle = self.angle * math.pi / 180
            self.dx += Ship.VELOCITY_STEP * math.sin(angle)
            self.dy += Ship.VELOCITY_STEP * -math.cos(angle)
            
        if games.keyboard.is_pressed(games.K_SPACE) and self.missile_wait == 0:
            new_missile = Missile(self.x, self.y, self.angle)
            games.screen.add(new_missile)
            self.missile_wait = Ship.MISSILE_DELAY

    def die(self):
        self.game.end()
        super(Ship, self).die()

# missile class
class Missile(Collider):
    image = games.load_image("lib\\img\\missile.png")
    sound = games.load_sound("lib\\snd\\missile.ogg")
    BUFFER = 50
    VELOCITY_FACTOR = 20
    LIFETIME = 20

    def __init__(self, ship_x, ship_y, ship_angle):
        Missile.sound.play()
        angle = ship_angle * math.pi / 180
        buffer_x = Missile.BUFFER * math.sin(angle)
        buffer_y = Missile.BUFFER * -math.cos(angle)
        x = ship_x + buffer_x
        y = ship_y + buffer_y
        dx = Missile.VELOCITY_FACTOR * math.sin(angle)
        dy = Missile.VELOCITY_FACTOR * -math.cos(angle)

        super(Missile, self).__init__(image = Missile.image,
                                      x = x, y = y,
                                      dx = dx, dy = dy)
        self.lifetime = Missile.LIFETIME

    def update(self):
        super(Missile, self).update()
        
        self.lifetime -= 1
        if self.lifetime == 0:
            self.destroy()

# game class
class Game(object):
    def __init__(self):
        self.level = 0
        self.sound = games.load_sound("lib\\snd\\level.ogg")
        self.score = games.Text(value = 0,
                                size = 40,
                                color = color.white,
                                right = games.screen.width - 20,
                                top = 20,
                                is_collideable = False)
        games.screen.add(self.score)

        self.ship = Ship(game = self,
                         x = games.screen.width/2,
                         y = games.screen.height/2)
        games.screen.add(self.ship)

    def play(self):
        games.music.load("lib\\snd\\theme.ogg")
        games.music.play(-1)

        games.screen.background = games.load_image("lib\\img\\background.jpg",
                                                   transparent = 0)
        self.advance()
        games.screen.mainloop()

    def advance(self):
        self.level += 1

        BUFFER = 150

        if self.level == 1:
            time.sleep(5)

        for i in range(self.level):
            x_min = random.randrange(BUFFER)
            y_min = BUFFER - x_min

            x_distance = random.randrange(x_min, games.screen.width - x_min)
            y_distance = random.randrange(y_min, games.screen.height - y_min)

            x = self.ship.x + x_distance
            y = self.ship.y + y_distance

            x %= games.screen.width
            y %= games.screen.height

            new_rock = Rock(game = self,
                            x = x, y = y,
                            size = Rock.LARGE)
            games.screen.add(new_rock)

        level_message = games.Message(value = "level " + str(self.level),
                                      size = 40,
                                      color = color.white,
                                      x = games.screen.width / 2,
                                      top = 20,
                                      lifetime = 3 * games.screen.fps,
                                      is_collideable = False)
        games.screen.add(level_message)

        if self.level > 1:
            self.sound.play()

    def end(self):
        end_message = games.Message(value = "GAME OVER",
                                    size = 80,
                                    color = color.white,
                                    x = games.screen.width / 2,
                                    y = games.screen.height / 2,
                                    lifetime = 10 * games.screen.fps,
                                    after_death = games.screen.quit,
                                    is_collideable = False)
        games.screen.add(end_message)

# main method
def main():
    pygame.display.set_caption("ROCKS")

    rocks = Game()
    rocks.play()

# invoke main method
main()

