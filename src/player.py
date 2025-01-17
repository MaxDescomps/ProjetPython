from entity import *
from crosshair import Crosshair

class Player(Entity):
    """Classe de joueur"""

    def __init__(self):
        """Constructeur de la classe Player"""

        super().__init__("player", 0, 0)

        self.ui_sprite_sheet = pygame.image.load(f"../image/techpack/UI/ui x1.png").convert_alpha() #spritesheet avec paramètre de transparence alpha

        self.max_pdv = 9 #pdv maximums
        self.pdv = self.max_pdv #pdv effectifs
        self.damage_clock = 0 #laps de temps minimum entre deux dommages consécutifs

        self.get_pdv_images()
        self.get_pdv_image()

        self.crosshair = Crosshair("../image/crosshair.png")
        self.map_manager = None #gestionnaire de carte pour ajuster la position du crosshair en jeu, attribué dans Game.__init__()

        self.weapon_index = 0
        self.weapons = []
        self.weapon_rate_clocks = [] #temps d'attente entre deux tirs de chaque arme

        self.take_weapon("ak-47")
        self.take_weapon("ksg")
        self.take_weapon("remington")
        self.take_weapon("pp-bizon")
        self.take_weapon("rocket-launcher")
        self.take_weapon("sniper")
        self.take_weapon("shadow")
        self.take_weapon("x-tech")
        self.take_weapon("ray-gun")
        self.take_weapon("atomus")
        self.take_weapon("gun")

        #raccourcis
        self.weapon = Weapon(9, 1, 4, "1")

        self.shooting = False #valeur envoyée par le joueur hôte aux invités pour indiquer qu'il tente de tirer

    def crosshair_pos(self) -> list[int]:
        """
        Récupère et convertit la position du crosshair du joueur pour correspondre au zoom et déplacement de la carte
        
        Returns:
            crosshair_pos(list[int]): la position convertie du crosshair
        """

        crosshair_pos = [None, None]
        crosshair_pos[0] = self.crosshair.rect.center[0] / self.map_manager.zoom + self.map_manager.get_group().view.x
        crosshair_pos[1] = self.crosshair.rect.center[1] / self.map_manager.zoom + self.map_manager.get_group().view.y

        return crosshair_pos

    def change_animation_list(self, direction:str):
        """
        Change la liste de sprites utilisés en fonction de la direction

        Args:
            direction(str): la direction du joueur
        """

        self.direction = direction
        self.image = self.images[self.direction][self.animation_index]


    def change_animation(self):
        """
        Change l'animation du sprite avec le mouvement
        """

        self.clock += self.speed * 8

        if self.clock >= 100:
            self.animation_index += 1

            if self.animation_index >= len(self.images[self.direction]):
                self.animation_index = 0
            
            self.clock = 0

    def take_weapon(self, name:str):
        """
        Récupération d'une arme

        Args:
            name(str): nom de l'arme
        """

        weapon = copy.copy(weapons[name]) #copie pour ne pas modifier le catalogue d'armes

        self.weapons.append(weapon)
        self.weapon_rate_clocks.append(0)

    def next_weapon(self):
        """Équipe l'arme suivante"""

        if self.weapon_index < len(self.weapons) - 1:
            self.weapon_index += 1
        else:
            self.weapon_index = 0

        self.weapon.kill() #retire l'ancienne arme des groupes d'affichage
        self.weapon = self.weapons[self.weapon_index]
        self.map_manager.get_group().add(self.weapon, layer=5) #ajoute la nouvelle arme au groupe d'affichage

    def previous_weapon(self):
        """Équipe l'arme précédente"""

        if self.weapon_index > 0:
            self.weapon_index -= 1
        else:
            self.weapon_index = len(self.weapons) - 1

        self.weapon.kill() #retire l'ancienne arme des groupes d'affichage
        self.weapon = self.weapons[self.weapon_index]
        self.map_manager.get_group().add(self.weapon, layer=5) #ajoute la nouvelle arme au groupe d'affichage

    def shoot(self):
        "Tir du joueur"

        self.shooting = True
        if not self.weapon_rate_clocks[self.weapon_index]:
            self.weapon_rate_clocks[self.weapon_index] = self.weapon.max_rate_clock
            shots = self.weapon.shoot()
            pygame.mixer.Channel(0).play(pygame.mixer.Sound("../music/gunshot_lowerer2.wav"))
            for shot in shots:
                self.map_manager.get_player_shots().append(shot)
                self.map_manager.get_group().add(shot, layer = 4)

    def update(self):
        """Mise a jour du joueur"""

        if self.pdv > 0:
            self.manage_weapon()

            self.rect.topleft = self.position #la position du joueur avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect player.feet et player.rect

    def manage_weapon(self):
        """Gestion de l'utilisation de l'arme du joueur"""

        #décrémentation du compteur de cadence de tir de l'arme en main
        if self.weapon_rate_clocks[self.weapon_index]:
            self.weapon_rate_clocks[self.weapon_index] -= 1

        self.weapon.angle = calc_angle(pygame.Vector2(self.rect.center), self.crosshair_pos()) #position en jeu du crosshair
        self.weapon.rect.center = self.rect.center

        #coefficients du vecteur de déplacement de l'arme par rapport au joueur
        self.weapon.speed_x = math.cos(self.weapon.angle)
        self.weapon.speed_y = math.sin(self.weapon.angle)

        #rotation de l'image de l'arme en fonction de l'angle
        self.weapon.rotate_img()

        #copie de la position pour pouvoir faire des calculs sur nombres flottants
        self.weapon.pos = [None, None]
        self.weapon.pos[0] = self.weapon.rect[0]
        self.weapon.pos[1] = self.weapon.rect[1]

        #met la position du tir à jour
        mult = 18 #distance entre le corps et l'arme
        if isinstance(self.weapon, Gun):
            mult -= 4

        self.weapon.pos[0] += mult * self.weapon.speed_x
        self.weapon.pos[1] += mult * self.weapon.speed_y

        #maj du rectangle d'affichage
        self.weapon.rect.topleft = self.weapon.pos

        #arme et joueur visent dans le bon sens
        if (self.weapon.angle > math.pi / 2) or (self.weapon.angle < -math.pi / 2): #côté gauche
            self.weapon.image = pygame.transform.flip(self.weapon.image, False, True)

            if (self.weapon.angle > math.pi * (3/4)) or (self.weapon.angle < -math.pi * (3/4)):
                self.change_animation_list("left")

            elif (self.weapon.angle < -math.pi/4) and (self.weapon.angle > -math.pi * (3/4)):
                self.change_animation_list("up")

            else:
                self.change_animation_list("down")

        else: #côté droit
            if (self.weapon.angle < math.pi/4) and (self.weapon.angle > -math.pi/4):
                self.change_animation_list("right")

            elif (self.weapon.angle < -math.pi/4) and (self.weapon.angle > -math.pi * (3/4)):
                self.change_animation_list("up")

            else:
                self.change_animation_list("down")

    def render_ui(self, screen:pygame.Surface):
        """
        Affichage de l'interface utilisateur du joueur

        Args:
            screen(pygame.Surface): fenêtre d'affichage
        """

        screen.blit(self.crosshair.image, self.crosshair.rect.topleft) #affichage du crosshair
        screen.blit(self.pdv_image, (100,20)) #affichage de la bar de vie
    
    def get_pdv_image(self):
        """Récupération de l'image de la bar de vie du joueur"""

        self.pdv_image = self.pdv_images[self.pdv] #image de la bar de vie

    def get_pdv_images(self):
        """Récupération des images de la bar de vie du joueur"""

        self.pdv_images = self.get_images(self.ui_sprite_sheet, 0, 1, 10)
        for i in range(len(self.pdv_images)):
            self.pdv_images[i] = pygame.transform.scale(self.pdv_images[i], (200,140)) #agrandit la bar de vie

    def take_damage(self):
        """Application des dégats au joueur"""

        if not self.damage_clock:
            pygame.mixer.Channel(1).play(pygame.mixer.Sound("../music/player_hurt.wav"))
            self.damage_clock = 60
            self.pdv -= 1
            self.get_pdv_image()

    def handle_damage(self):
        """Gestion des conséquences de la prise de dégats"""

        #compteur d'invincibilité
        if self.damage_clock:
                self.damage_clock -= 1

                #effet visuel
                if self.damage_clock > 40:
                    self.damage_effect(0.35 * ((self.damage_clock - 40)/10)) #va de 2/3 à 0
                
    
    def damage_effect(self, scale:float):
        """
        Affiche un filtre rouge progressif

        Args:
            scale(float): échelle de vert et bleu
        """

        GB = min(255, max(0, round(255 * (1-scale)))) #vert et bleu du filtre RGB, va de 85 à 255
        self.map_manager.screen.fill((255, GB, GB), special_flags = pygame.BLEND_MULT)

class PlayerMulti(Player):
    """Classe d'un joueur multijoueur importé du serveur"""
    
    def __init__(self):
        super().__init__()

        self.true_angle = 0 #angle du joueur multi dans son vrai monde

    def manage_weapon(self):
        """Gestion de l'utilisation de l'arme du joueur"""

        #décrémentation du compteur de cadence de tir de l'arme en main
        if self.weapon_rate_clocks[self.weapon_index]:
            self.weapon_rate_clocks[self.weapon_index] -= 1

        self.weapon.angle = self.true_angle #position en jeu du crosshair
        self.weapon.rect.center = self.rect.center

        #coefficients du vecteur de déplacement de l'arme par rapport au joueur
        self.weapon.speed_x = math.cos(self.weapon.angle)
        self.weapon.speed_y = math.sin(self.weapon.angle)

        #rotation de l'image de l'arme en fonction de l'angle
        self.weapon.rotate_img()

        #copie de la position pour pouvoir faire des calculs sur nombres flottants
        self.weapon.pos = [None, None]
        self.weapon.pos[0] = self.weapon.rect[0]
        self.weapon.pos[1] = self.weapon.rect[1]

        #met la position du tir à jour
        mult = 18 #distance entre le corps et l'arme
        if isinstance(self.weapon, Gun):
            mult -= 4

        self.weapon.pos[0] += mult * self.weapon.speed_x
        self.weapon.pos[1] += mult * self.weapon.speed_y

        #maj du rectangle d'affichage
        self.weapon.rect.topleft = self.weapon.pos

        #arme et joueur visent dans le bon sens
        if (self.weapon.angle > math.pi / 2) or (self.weapon.angle < -math.pi / 2): #côté gauche
            self.weapon.image = pygame.transform.flip(self.weapon.image, False, True)

            if (self.weapon.angle > math.pi * (3/4)) or (self.weapon.angle < -math.pi * (3/4)):
                self.change_animation_list("left")

            elif (self.weapon.angle < -math.pi/4) and (self.weapon.angle > -math.pi * (3/4)):
                self.change_animation_list("up")

            else:
                self.change_animation_list("down")

        else: #côté droit
            if (self.weapon.angle < math.pi/4) and (self.weapon.angle > -math.pi/4):
                self.change_animation_list("right")

            elif (self.weapon.angle < -math.pi/4) and (self.weapon.angle > -math.pi * (3/4)):
                self.change_animation_list("up")

            else:
                self.change_animation_list("down")

    def update(self):
        """Mise a jour du joueur"""

        if self.pdv > 0:
            self.manage_weapon()

            self.rect.topleft = self.position #la position du joueur avec [0,0] le coin superieur gauche
            self.feet.midbottom = self.rect.midbottom #aligne les centres des rect player.feet et player.rect
        
        if self.shooting:
            self.shoot()
            self.shooting = False

    def take_weapon(self, name:str):
        """
        Récupération d'une arme

        Args:
            name(str): nom de l'arme
        """

        weapon = copy.copy(weapons2[name]) #copie pour ne pas modifier le catalogue d'armes

        self.weapons.append(weapon)
        self.weapon_rate_clocks.append(0)