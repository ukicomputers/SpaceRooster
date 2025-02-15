import pygame as pg
import random

ASSET_PATH = "./assets/"
CHICKEN_SHIT = ASSET_PATH + "egg.png"
AMMO_ASSET = ASSET_PATH + "packet.png"
DEAD_EFFECT = ASSET_PATH + "dead.ogg"
EGG_EFFECT = ASSET_PATH + "egg.ogg"
MINI_EFFECT = ASSET_PATH + "mini_life.ogg"

DEF_CHICKEN_LIVES = 2
DEF_SHIT_RATE = 5
DEF_SHIT_TIMER = 2250

class Chickens():
    def __init__(self, location, window, chicken_lives=DEF_CHICKEN_LIVES, shit_rate=DEF_SHIT_RATE, shit_timer=DEF_SHIT_TIMER):
        ww = window.get_width()
        self.chickens = []
        self.chicken_shit = []
        self.speed = 10  # per pixel
        self.img = pg.image.load(location).convert_alpha()
        self.shit_asset = pg.image.load(CHICKEN_SHIT).convert_alpha()
        self.ammo_asset = pg.image.load(AMMO_ASSET).convert_alpha()
        self.dead_effect = pg.mixer.Sound(DEAD_EFFECT)
        self.dead_effect.set_volume(0.3)
        self.egg_effect = pg.mixer.Sound(EGG_EFFECT)
        self.mini_effect = pg.mixer.Sound(MINI_EFFECT)
        self.mini_effect.set_volume(0.4)
        self.window = window
        self.last_shit_time = 0
        self.shit_rate = shit_rate
        self.shit_timer = shit_timer

        for row in range(5):
            for col in range(8):
                if col % 2 == 0:
                    x = -(col * (self.img.get_width() + 10)) - self.img.get_width()
                else:
                    x = ww + (col * (self.img.get_width() + 10))

                y = (row * (self.img.get_height() + 10)) + 80
                target_x = (col * (self.img.get_width() + 10)) + (ww // 2 - self.img.get_width() * 5 + 70)
                self.chickens.append({"x": x, "y": y, "target_x": target_x, "target_y": y, "lives": chicken_lives, "packet": False})

        if random.getrandbits(1):
            random.choice(self.chickens)["packet"] = True

    def slide(self, lr=False, ud=False, spaceship=None):
        ww, wh = self.window.get_size()
        reached = True

        for chicken in self.chickens:
            self.window.blit(self.img, (chicken["x"], chicken["y"]))

            if chicken["x"] != chicken["target_x"]:
                if abs(chicken["x"] - chicken["target_x"]) <= self.speed:
                    chicken["x"] = chicken["target_x"]
                elif chicken["x"] > chicken["target_x"]:
                    chicken["x"] -= random.randint(1, self.speed)
                    reached = False
                elif chicken["x"] < chicken["target_x"]:
                    chicken["x"] += random.randint(1, self.speed)
                    reached = False

            if chicken["y"] != chicken["target_y"]:
                if abs(chicken["y"] - chicken["target_y"]) <= self.speed:
                    chicken["y"] = chicken["target_y"]
                elif chicken["y"] > chicken["target_y"]:
                    chicken["y"] -= random.randint(1, self.speed)
                    reached = False
                elif chicken["y"] < chicken["target_y"]:
                    chicken["y"] += random.randint(1, self.speed)
                    reached = False

            if lr and chicken["target_x"] == chicken["x"]:
                chicken["target_x"] = random.randint(0, ww - self.img.get_width())

            if ud and chicken["target_y"] == chicken["y"]:
                chicken["target_y"] = random.randint(0, wh - self.img.get_height() - 162)

        return reached
    
    def slide_shit(self):
        wh = self.window.get_height()
        self.shit()

        for shit in self.chicken_shit:
            shit["y"] += random.randint(1, self.speed)
            self.window.blit(self.ammo_asset if shit["packet"] else self.shit_asset, (shit["x"], shit["y"]))
        
            if shit["y"] > wh:
                self.chicken_shit.remove(shit)
                self.egg_effect.play()
    
    def collided(self, ammo, kill_rate=1):
        out = False

        for chicken in self.chickens:
            if ammo.colliderect(self.img.get_rect(x=chicken["x"], y=chicken["y"])):
                chicken["lives"] -= kill_rate
                if chicken["lives"] <= 0:
                    if chicken["packet"]:
                        self.chicken_shit.append({"x": chicken["x"] + self.img.get_width() // 2, "y": chicken["y"] + self.img.get_height(), "packet": True})
                    self.chickens.remove(chicken)
                    self.dead_effect.play()
                out = True
                self.mini_effect.play()

        return out
    
    def collided_shit(self, spaceship=None):
        for shit in self.chicken_shit:
            if spaceship.colliderect(self.shit_asset.get_rect(x=shit["x"], y=shit["y"])):
                self.chicken_shit.remove(shit)
                return "ammo" if shit["packet"] else "egg"
        
        return ""
    
    def shit(self):
        ticks = pg.time.get_ticks()
        if ticks - self.last_shit_time >= self.shit_timer:
            self.last_shit_time = ticks
            if len(self.chickens) > 0:
                for _ in range(self.shit_rate):
                    chicken = random.choice(self.chickens)
                    self.chicken_shit.append({"x": chicken["x"] + self.img.get_width() // 2, "y": chicken["y"] + self.img.get_height(), "packet": False})

    def is_over(self):
        return len(self.chickens) <= 0 and len(self.chicken_shit) <= 0
