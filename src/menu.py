import pygame
from game import Game

class Character():
    def __init__(self, name):
        self.sheet = pygame.image.load(f'../image/{name}.png').convert_alpha()

    def get_image(self, player_frame, width, height, scale):
        image = pygame.Surface([width, height], pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((player_frame * width), 64, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        return image

    def get_images(self, animation_steps, player_height, player_scale):
        player_images = []

        for x in range(animation_steps):
            player_images.append(self.get_image(x, 32, player_height, player_scale))

        return player_images

class Menu():

    def __init__(self) -> None:
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # fenêtre de jeu
        self.SCREEN_WIDTH = 1920
        self.SCREEN_HEIGHT = 1080
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Dungia")

        #personnage annimé
        self.player_height = 32 #hauteur du sprite du personnage
        self.player_scale = 7 / (1920/self.SCREEN_WIDTH) #multiplicateur du sprite du personnage
        self.player = Character("player")
        self.animation_steps = 3
        self.player_images = self.player.get_images(self.animation_steps, self.player_height, self.player_scale)
        self.player_animation_cooldown = 150 #décompte avant animation du personnage

        #décor
        self.grass_height = 10 #taille de l'herbe
        self.get_ground_image()
        self.get_bg_image()

        #écritures
        self.font_size = int(40 / (800/self.SCREEN_WIDTH)) #taille
        self.font = pygame.font.SysFont("arialblack", self.font_size) #police
        self.TEXT_COL = (255, 255, 255) #couleur

    def get_ground_image(self):
        """Image du sol du menu"""

        self.ground_image = pygame.image.load(f"../image/paralax/ground.png").convert_alpha()
        self.ground_image = pygame.transform.scale(self.ground_image, (self.SCREEN_WIDTH/2.5, self.SCREEN_HEIGHT/8))
        self.ground_width = self.ground_image.get_width()
        self.ground_height = self.ground_image.get_height()

    def get_bg_image(self):
        """Image des arbres du menu"""

        self.bg_images = []
        for i in range(1, 6):
            bg_image = pygame.image.load(f"../image/paralax/plx-{i}.png").convert_alpha()
            bg_image = pygame.transform.scale(bg_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT - self.ground_height + self.grass_height))
            self.bg_images.append(bg_image)
            self.bg_height = bg_image.get_height()

        self.bg_width = self.bg_images[0].get_width()

    def play(self):

        self.scroll = 0
        last_player_update = pygame.time.get_ticks() #heure de la dernière animation du personnage
        player_frame = 0 #numéro de sprite du personnage affiché

        # music
        pygame.mixer.music.load("../music/intro.wav")
        pygame.mixer.music.play(-1) #répète la musique à indéfiniment

        run = True

        #boucle principale du menu de démarrage
        while run:

            self.clock.tick(self.FPS) #limite de FPS
            current_time = pygame.time.get_ticks()

            if current_time - last_player_update >= self.player_animation_cooldown:
                player_frame += 1
                last_player_update = current_time
                if player_frame >= len(self.player_images):
                    player_frame = 0

            #affichage
            self.draw_all(player_frame)

            #renouvellement de l'affichage une fois fini
            if self.scroll > 3000:
                self.scroll = 0
            else:
                self.scroll += 1

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pygame.mixer.music.stop()
                        game = Game(self.screen)
                        game.run()

                        #redémarre le menu si on quitte le jeu
                        pygame.mixer.music.load("../music/intro.wav")
                        pygame.mixer.music.play(-1)
                        self.scroll = 0

                if event.type == pygame.QUIT:
                    run = False


    def draw_all(self, player_frame):
        """Affichage complet du menu de démarrage"""

        self.draw_bg()
        self.draw_ground()
        self.draw_character(player_frame)
        self.draw_text("Press Space Button", self.font, self.TEXT_COL, 100, self.font_size)

    def draw_character(self, player_frame):
        """Affichage du personnage"""

        self.screen.blit(self.player_images[player_frame], (100, self.SCREEN_HEIGHT - self.ground_height + self.grass_height - self.player_height * self.player_scale))            

    def draw_bg(self):
        """Affiche l'arrière_plan"""

        for x in range(10):
            speed = 1
            for i in self.bg_images:
                self.screen.blit(i, ((x * self.bg_width) - self.scroll * speed, self.SCREEN_HEIGHT - self.ground_height - self.bg_height + self.grass_height))
                speed += 0.2

    def draw_ground(self):
        """Affiche le sol"""

        for x in range(30):
            self.screen.blit(self.ground_image, ((x * self.ground_width) - self.scroll * 2.2, self.SCREEN_HEIGHT - self.ground_height))

    def draw_text(self, text, font, text_col, x, y):
        """Affiche le texte"""

        img = font.render(text, True, text_col).convert_alpha()
        self.screen.blit(img, (x, y))