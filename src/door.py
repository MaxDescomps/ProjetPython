import pygame

class Door(pygame.sprite.Sprite):
    """
    Classe des portes en jeu. Les portes sont toutes initialement ouvertes.
    Les portes d'une pièce hostile se ferment et se réouvrent quand elle ne l'est plus.
    """
    
    def __init__(self, rect:pygame.Rect):
        """
        Constructeur de la classe Door

        Args:
            rect(pygame.Rect): rectangle d'affichage de la porte
        """

        super().__init__()
        self.speed = 2 #vitesse d'animation
        self.clock = 0 #compteur d'animation

        self.opening = True #initialement sur True, indique que la porte s'ouvre
        self.closing = False #initialement sur False, indique que la porte se ferme

        self.opened = False #informe sur l'état ouvert de la porte (mis sur True à l'ouverture du jeu)
        self.blocked = False #collision temporaire de la porte parfois nécessaire

        self.animation_index = 0
        self.rect = rect

    def update(self):
        """Gère l'animation d'ouverture et fermeture d'une porte"""

        if self.opened == False:
            self.open_animation()
        else:
            self.close_animation()

    def open_animation(self):
        """Ouverture d'une porte avec animation"""

        if self.opening:
            images_len = len(self.images)

            self.image = self.images[self.animation_index]
            self.clock += self.speed * 10

            if self.clock >= 100:
                self.animation_index += 1

                if self.animation_index >= images_len:
                    self.animation_index = images_len - 1

                    self.opening = False
                    self.closing = False #empêche l'execution d'une fermeture demandée avant quand self.opened == False
                    self.opened = True #on désactive la collision en dernier pour que le joueur attende la fin de l'animation d'ouverture
                
                self.clock = 0

    def close_animation(self):
        """Fermeture d'une porte avec animation"""

        if self.closing:
            self.blocked = True #on active la collision temporaire en premier pour éviter que le joueur traverse la porte pendant l'animation

            self.image = self.images[self.animation_index]
            self.clock += self.speed * 10

            if self.clock >= 100:
                self.animation_index -= 1

                if self.animation_index < 0:
                    self.animation_index = 0

                    self.closing = False
                    self.opening = False #empêche l'execution d'une ouverture demandée avant quand self.opened == True
                    self.opened = False #active la collision définitive

                    self.blocked = False #plus besoin de la collision temporaire elle est assurée au dessus
                
                self.clock = 0

class HDoor(Door):
    """
    Classe des portes horizontales en jeu (haut - bas).
    """
    
    def __init__(self, rect:pygame.Rect):
        """
        Constructeur de la classe HDoor

        Args:
            rect(pygame.Rect): rectangle d'affichage de la porte
        """

        super().__init__(rect)

        self.sprite_sheet = pygame.image.load("../image/techpack/Props and Items/props and items x1.png").convert_alpha() #spritesheet avec paramètre de transparence alpha
        
        self.images = self.get_images(16)
        self.image = self.images[0]

        self.collision_rect = rect

    def get_images(self, y:int) -> list[pygame.Surface]:
        """
        Récupère les sprites d'une ligne d'un spritesheet 32*64
        
        Args:
            y(int): numéro de ligne sur le spritesheet

        Returns:
            images(list[pygame.Surface]): liste des sprites de la porte
        """

        images = []
        
        for i in range(0,12):
            x = i*64
            image = self.get_image(x, y*32)
            images.append(image)
        
        return images

    def get_image(self, x:float, y:float) -> pygame.Surface:
        """
        Récupère un sprite de 32*64
        
        Args:
            x(float): coordonnée horizontale du sprite sur le spritesheet
            y(float): coordonnée verticale du sprite sur le spritesheet

        Returns:
            image(pygame.Surface): sprite de la porte
        """

        image = pygame.Surface([64, 32], pygame.SRCALPHA)#surface avec un parametre de transparence (alpha = 0)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 64, 32)) #canvas.blit (ajout, (coord sur canvas), (rect de l'ajout sur l'image source))

        return image.convert_alpha()

class VRDoor(Door):
    """
    Classe des portes verticales à droite en jeu.
    """
    
    def __init__(self, rect:pygame.Rect):
        """
        Constructeur de la classe VRDoor

        Args:
            rect(pygame.Rect): rectangle d'affichage de la porte
        """

        super().__init__(rect)

        self.speed = 1 #vitesse d'animation
        self.collision_rect = pygame.Rect(self.rect.x + 24, self.rect.y, 8, self.rect.height)

        self.sprite_sheet = pygame.image.load("../image/techpack/tileset x1.png").convert_alpha() #spritesheet avec paramètre de transparence alpha

        self.images = self.get_images(26, 11)
        self.image = self.images[0]

    def get_images(self, x: int, y: int) -> list[pygame.Surface]:
        """
        Récupère des sprites d'une ligne d'un spritesheet 64x32
        
        Args:
            x(int): numéro de colonne sur le spritesheet
            y(int): numéro de ligne sur le spritesheet

        Returns:
            images(list[pygame.Surface]): une liste d'images
        """

        images = []
        
        for i in range(0,4):
            image = self.get_image(x*32 + i*32, y*32)
            images.append(image)
        
        return images

    def get_image(self, x: float, y: float) -> pygame.Surface:
        """
        Récupère un sprite 64x32
        
        Args:
            x(float): coordonnée horizontale du sprite sur le spritesheet
            y(float): coordonnée verticale du sprite sur le spritesheet

        Returns:
            image(pygame.Surface): sprite de la porte
        """

        image = pygame.Surface([32, 64], pygame.SRCALPHA)#surface avec un parametre de transparence (alpha = 0)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 64)) #canvas.blit (ajout, (coord sur canvas), (rect de l'ajout sur l'image source))

        return image.convert_alpha()

class VLDoor(Door):
    """
    Classe des portes verticales à gauche en jeu.
    """
    
    def __init__(self, rect:pygame.Rect):
        """
        Constructeur de la classe VLDoor

        Args:
            rect(pygame.Rect): rectangle d'affichage de la porte
        """

        super().__init__(rect)

        self.collision_rect = pygame.Rect(self.rect.x, self.rect.y, 8, self.rect.height)
        self.speed = 1 #vitesse d'animation

        self.sprite_sheet = pygame.image.load("../image/techpack/tileset x1.png").convert_alpha() #spritesheet avec paramètre de transparence alpha

        self.images = self.get_images(26, 9)
        self.image = self.images[0]

    def get_images(self, x: int, y: int) -> list[pygame.Surface]:
        """
        Récupère des sprites d'une ligne d'un spritesheet 64x32
        
        Args:
            x(int): numéro de colonne sur le spritesheet
            y(int): numéro de ligne sur le spritesheet

        Returns:
            images(list[pygame.Surface]): une liste d'images
        """

        images = []
        
        for i in range(0,4):
            image = self.get_image(x*32 + i*32, y*32)
            images.append(image)
        
        return images

    def get_image(self, x: float, y: float) -> pygame.Surface:
        """
        Récupère un sprite 64x32
        
        Args:
            x(float): coordonnée horizontale du sprite sur le spritesheet
            y(float): coordonnée verticale du sprite sur le spritesheet

        Returns:
            image(pygame.Surface): sprite de la porte
        """

        image = pygame.Surface([32, 64], pygame.SRCALPHA)#surface avec un parametre de transparence (alpha = 0)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 64)) #canvas.blit (ajout, (coord sur canvas), (rect de l'ajout sur l'image source))

        return image.convert_alpha()