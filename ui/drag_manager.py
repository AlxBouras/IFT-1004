from tp4.ui.scrabble_canvas import ScrabbleCanvas
from tp4.scrabble import Scrabble
from tp4.plateau import Plateau


class DragManager:
    """
    Classe permettant de gérer le Drag-n-Drop.

    Les Drag-n-drop sont "sticky" c'est à dire que le drop repositionne l'élément sur la case
    sélectionné (sous le curseur)

    Lors de la création d'un Drag-n-Drop, on peut associer plusieurs item du canvas, qui vont tous suivre les
    même delta.  Par convention, il y 2 toujours 2 item ici, le jeton (rectangle) et son libellé (text)
    """
    def __init__(self, canvas, ids, index_jeton, moves: {}):
        self.__x, self.__y = None, None
        self.__xorigin, self.__yorigin = None, None
        self.__items = ids
        self.__canvas: ScrabbleCanvas = canvas
        self.__index_jeton = index_jeton
        self.__moves: {} = moves

        # Pour tous les objets, attacker les fonctions du drag-n-drop
        for item in self.__items:
            self.__canvas.tag_bind(item, "<ButtonPress-1>", self.on_start)
            self.__canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            self.__canvas.tag_bind(item, "<ButtonRelease-1>", self.on_drop)

    def on_start(self, event):
        """
        Prendre le jeton

        Lors du début di déplacement, on enregisre:
            les position x, y d'origine (en x, y scrabble)
            Les position x, y en cours (en version pixel)

        On élève égallement les composantes dans l'écran (le libellé sur le rectangle).
        :param event: évènement généré par tkinter
        :return: rien
        """

        self.__x = event.x
        self.__y = event.y

        self.__xorigin, self.__yorigin = self.__canvas.get_xy(event.x, event.y)

        self.__canvas.lift(self.__items[0])
        self.__canvas.lift(self.__items[1])

    def on_drag(self, event):
        """
        Déplacer le jeton
        :param event: évènement généré par tkinter
        :return: rien
        """
        # Calculer la distance de déplacement en cours
        delta_x = event.x - self.__x
        delta_y = event.y - self.__y

        # Déplacement des objet lié du delta
        for item in self.__items:
            self.__canvas.move(item, delta_x, delta_y)

        # Enregistrement des nouvelles positions
        self.__x = event.x
        self.__y = event.y

    def on_drop(self, event):
        """
        Déposer le jeton.

        Plusieurs cas complexe sont géré ici :
            - Déposer le jeton sur le plateau
                Attache le jeton à la case vide de plateau sous le curseur
                Il ne doit pas y avoir d'autre jetons en cours de déplacement
                On doit ajouter le déplacement dans la listes des déplacement à faire en fin de tour
            - Déposer le jeton sur une case vide du chevalet du joueur actif
                Si le jeton était enregistrer comme un déplacement de ce tour, on le retire de cette liste
            - Compenser un déplacement invalide
                Si la cible du dépôt n'est pas l'une des 2 situation précédente, on retourne le jeton à son origine

        :param event: évènement généré par tkinter
        :return: rien
        """
        x, y = self.__canvas.get_xy(event.x, event.y)

        # Déposer le jetons sur une place vide du plateau
        if x < Plateau.DIMENSION \
                and y < Plateau.DIMENSION \
                and Scrabble.instance.plateau.cases[x][y].est_vide()\
                and Plateau.encode_position(x, y) not in self.__moves.values():
            self.__canvas.move_shape(self.__items[0], x, y)
            self.__canvas.move_lettre(self.__items[1], x, y)

            self.__moves.update({self.__index_jeton: Plateau.encode_position(x, y)})

            return

        # Chercher si on est sur une case vide de chevalet
        occupe = chevalet = False
        for item in self.__canvas.find_overlapping(event.x, event.y, event.x, event.y):
            if item not in self.__items:
                tags = self.__canvas.gettags(item)
                chevalet = True \
                    if ("chevalet" in tags
                        and y == (Scrabble.instance.joueurs.index(Scrabble.instance.joueur_actif) + 1) * 2)\
                    else chevalet

                occupe = True if "jeton" in tags else occupe

        # déposer le jeton sur une case vide du chevalet
        if not occupe and chevalet:
            self.__canvas.move_shape(self.__items[0], x, y)
            self.__canvas.move_lettre(self.__items[1], x, y)

            if self.__index_jeton in self.__moves.keys():
                self.__moves.pop(self.__index_jeton)

            return

        # Retour à la position original
        print(self.__xorigin, self.__yorigin)
        self.__canvas.move_shape(self.__items[0], self.__xorigin, self.__yorigin)
        self.__canvas.move_lettre(self.__items[1], self.__xorigin, self.__yorigin)
