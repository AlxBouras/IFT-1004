from tkinter import Canvas, LEFT, RIGHT


class ScrabbleCanvas(Canvas):
    """
    Classe de Canvas Étendu

    Ce Canvas permet de positionner facilement les chose en représentant les x et y par des positions dans un écran
    "Scrabble".  C'est à dire que l'écran composé de 23x15 cases contient les élément <0,0> à <22,14>

    Contient égallement des fonction utilitaire simplifiants les déplacement, en consiférent plusieurs convention
    utilisé dans l'écran du jeu
    """

    unit_size = 1  # Taille en pixel d'une case (re-calculer à chaque dessin de l'écran)

    def __init__(self, master=None, **args):
        super().__init__(master, args)

    def get_xy(self, x, y):
        """
        Obtenir les coordonnée en case du XY fournis en pixel
        :return: tuple (x, y)
        """
        return x // self.unit_size, y // self.unit_size

    def move_shape(self, item, x: int, y: int, width=1, height=1):
        """
        Déplacement simple d'une forme (rectangle uniquement) dans l'écran de scrabble et redimensionnement lorsque
        requis
        :param item: ID de l'élément à déplacer
        :param x: position x version scrabble (0 <= x <= 22 générallement)
        :param y: position y version scrabble (0 <= y <= 14 générallement)
        :param width: largeur en nombre de case (1 par défaut)
        :param height: hauteur en nombre de case (1 par défault)
        :return: rien
        """
        x1 = x * self.unit_size
        y1 = y * self.unit_size

        x2 = x1 + width * self.unit_size
        y2 = y1 + height * self.unit_size

        self.coords(item, x1, y1, x2, y2)

    def move_lettre(self, item, x: int, y: int, width=1, height=1, **args):
        """
        Déplacement simple d'un text dans l'écran de scrabble et redimensionnement lorsque
        requis.

        Note, la position final est influencé par "justify" si l'argument est présent

        :param item: ID de l'élément à déplacer
        :param x: position x version scrabble (0 <= x <= 22 générallement)
        :param y: position y version scrabble (0 <= y <= 14 générallement)
        :param width: largeur en nombre de case (1 par défaut)
        :param height: hauteur en nombre de case (1 par défault)
        :param args: autres paramètre à transféré à coords
        :return: rien
        """
        x1 = x * self.unit_size + width * self.unit_size // 2
        y1 = y * self.unit_size + height * self.unit_size // 2

        if "justify" in args.keys():
            if args.get("justify") == LEFT:
                x1 = (x + 1) * self.unit_size + self.unit_size // 2
            elif args.get("justify") == RIGHT:
                x1 = (x + width - 1) * self.unit_size + self.unit_size // 2

        self.coords(item, x1, y1)

    def add_rectangle(self, x: int, y: int, width=1, height=1, **args):
        """
        Ajout d'un rectangle au canvas à la position scrabble x,y position

        :param x: position x version scrabble (0 <= x <= 22 générallement)
        :param y: position y version scrabble (0 <= y <= 14 générallement)
        :param width: largeur en nombre de case (1 par défaut)
        :param height: hauteur en nombre de case (1 par défault)
        :param args: autres paramètre à transféré à create_rectangle
        :return: the created rectangle id
        """
        x1, y1 = x * self.unit_size, y * self.unit_size
        x2, y2 = x1 + width * self.unit_size, y1 + height * self.unit_size

        return self.create_rectangle(x1, y1, x2, y2, args)

    def add_text(self, x: int, y: int, width: int=1, height: int=1, **args):
        """
        Ajout d'un texte au canvas à la position scrabble x,y position

        :param x: position x version scrabble (0 <= x <= 22 générallement)
        :param y: position y version scrabble (0 <= y <= 14 générallement)
        :param width: largeur en nombre de case (1 par défaut)
        :param height: hauteur en nombre de case (1 par défault)
        :param args: autres paramètre à transféré à create_text
        :return: the created rectangle id
        """

        x1 = x * self.unit_size + width * self.unit_size // 2
        y1 = y * self.unit_size + height * self.unit_size // 2

        if "justify" in args.keys():
            if args.get("justify") == LEFT:
                x1 = (x + 1) * self.unit_size + self.unit_size // 2
            elif args.get("justify") == RIGHT:
                x1 = (x + width - 1) * self.unit_size + self.unit_size // 2

        return self.create_text(x1, y1, args)
