from tp4.ui.scrabble_canvas import ScrabbleCanvas
from tp4.ui.drag_manager import DragManager
from tp4.scrabble import Scrabble, Timer
from tp4.error import *
from tp4.plateau import Plateau
from tp4.joueur import Joueur
from tkinter import *
from tp4.ui.theme_manager import Theme


class ScrabbleComponent:
    """
    Définition de la classe à haut niveau d'une composante

    Permet de dessiner et de faire le ménage des composantes visuel et référence mémoire
    """

    def __init__(self, async=False):
        self.async = async

    def dessiner(self):
        pass

    def clear(self):
        pass


class ScrabbleActions(ScrabbleComponent):
    """
    Composante actions, responssable de l'affichage et des évènement des boutons d'actions
    """

    def __init__(self, canvas: ScrabbleCanvas):
        super().__init__()

        self.__canvas = canvas

        # référence aux id d'objets
        self.__button_next_turn = None
        self.__label_next_turn = None

    def jouer_un_tour(self, event=None):
        """
        Actions du bouton "Terminer le tour"
        :param event: non utilisé, requis pour être bindé sur un évènement
        :return: rien
        """

        # Supprimer le message en cours
        ScrabbleMessages.ui.message(message="")
        try:
            # Jouer un tour de scrabble
            Scrabble.instance.jouer_un_tour()

            # Si la partie est calculé comme terminé, on affiche le vaincoeur dans la boite de message
            if Scrabble.instance.partie_terminee():
                self.__canvas.master.dessiner()
                gagnant = Scrabble.instance.determiner_gagnant()

                ScrabbleMessages.ui.message("Victoir de '{}' avec {} points en {:02d}:{:02d} minutes !".format(
                    gagnant.nom,
                    gagnant.points,
                    *divmod(int(gagnant.temps_jeu_total), 60)))

                # Supression du bouton, puisqu'il n'y a plus de tour à jouer
                self.__canvas.delete(self.__button_next_turn, self.__label_next_turn)
                self.__button_next_turn = None
                self.__label_next_turn = None

                # Supression du joueur actif (partie terminé, utilisé par plusieurs composantes pour ne plus se dessiner
                Scrabble.instance.joueur_actif = None
            else:
                # Si la partie n'est pas terminer, on change de joueur, et on redessine l'écran
                Scrabble.instance.joueur_suivant()
                Timer.reset()
                self.__canvas.master.dessiner()

        except ScrabbleError as e:
            # Si une erreur est détecté, on la communique à l'usager pour qu'il corrige son tour.
            ScrabbleMessages.ui.message(message=e.message)

    def dessiner(self):
        """
        Permet de dessiner les boutons et d'y attacher leurs évènement
        :return: rien
        """

        # On ne dessine que s'il y a une partie en cours
        if Scrabble.instance.joueur_actif is None:
            return

        # Lazy-loading du bouton, de son texte et des évèenement associé
        if self.__button_next_turn is None:
            self.__button_next_turn = self.__canvas.add_rectangle(0, 0, fill=Theme.theme_actif.medium, tags="actions")
            self.__label_next_turn = self.__canvas.add_text(0, 0,
                                                            font=('Times', '{}'.format(self.__canvas.unit_size // 2)),
                                                            text="Terminer le tour")
            self.__canvas.tag_bind(self.__button_next_turn, "<ButtonPress-1>", self.jouer_un_tour)
            self.__canvas.tag_bind(self.__label_next_turn, "<ButtonPress-1>", self.jouer_un_tour)

        # Déplacement vers la position requise dans l'écran
        self.__canvas.move_shape(self.__button_next_turn,
                                 Plateau.DIMENSION + Joueur.TAILLE_CHEVALET - 3,
                                 Plateau.DIMENSION - 1,
                                 width=4)
        self.__canvas.itemconfig(self.__button_next_turn, fill=Theme.theme_actif.medium)

        self.__canvas.move_lettre(self.__label_next_turn,
                                  Plateau.DIMENSION + Joueur.TAILLE_CHEVALET - 3,
                                  Plateau.DIMENSION - 1,
                                  width=4)
        self.__canvas.itemconfig(self.__label_next_turn, fill=Theme.theme_actif.major)


class ScrabbleMessages(ScrabbleComponent):
    """
    Instance "Singleton", se ré-exposant via ScrabbleMessages.ui

    Cette classe permet de communiquer des messages à l'usager, notament si son tour est invalide
    ou que la partie est terminé
    """
    ui = None

    def __init__(self, canvas: ScrabbleCanvas):
        super().__init__()

        ScrabbleMessages.ui = self
        self.__canvas = canvas
        self.__message = ''
        self.__box = None
        self.__text = None

    def message(self, message: str):
        # Affichage d'un message à la demande
        self.__message = message
        self.dessiner()

    def dessiner(self):
        """
        Permet de dessiner la boite de message et son texte
        :return: rien
        """

        # On ne dessine que s'il y a une partie en cours
        if Scrabble.instance.joueur_actif is None:
            return

        # Lazy-Loading des éléments graphyque
        if self.__box is None:
            self.__box = self.__canvas.add_rectangle(0, 0)
            self.__text = self.__canvas.add_text(0, 0, font=('Times', '{}'.format(self.__canvas.unit_size // 2)))

        # Déplacement à l'endroit approprié de l'écran
        self.__canvas.move_shape(self.__box, Plateau.DIMENSION + 1, 10, width=Joueur.TAILLE_CHEVALET, height=2)
        self.__canvas.move_lettre(self.__text, Plateau.DIMENSION + 1, 10, width=Joueur.TAILLE_CHEVALET, height=2)

        # Mise à jour du message
        self.__canvas.itemconfigure(self.__text,
                                    fill=Theme.theme_actif.medium,
                                    text=self.__message,
                                    width=self.__canvas.unit_size * Joueur.TAILLE_CHEVALET)


class ScrabblePlateau(ScrabbleComponent):
    """
    Classe responssable de l'affichage du plateau

    """
    def __init__(self, canvas: ScrabbleCanvas):
        super().__init__()

        self.__canvas = canvas
        self.__cases: [[tuple]] = None

    def dessiner(self):
        """
        Dessine le plateau selon le contenu de Scrbble.plateau
        :return:
        """
        plateau_case = Scrabble.instance.plateau.cases

        # Lazy-Loading des cases du plateau
        if self.__cases is None:
            self.__cases = []

            for i in range(Plateau.DIMENSION):
                self.__cases.append([])

                for j in range(Plateau.DIMENSION):
                    self.__cases[i].append((
                        self.__canvas.add_rectangle(i, j,
                                                    fill=plateau_case[i][j].code_couleur,
                                                    tags='case_plateau'),
                        self.__canvas.add_text(i, j, justify=CENTER)
                    ))

        # Refresh des cases
        for i in range(Plateau.DIMENSION):
            for j in range(Plateau.DIMENSION):

                # Déplacement selon la grosseure de la fenêtre (re-size)
                self.__canvas.move_shape(self.__cases[i][j][0], i, j)
                self.__canvas.move_lettre(self.__cases[i][j][1], i, j)

                if plateau_case[i][j].est_vide():  # affichage d'une case 'vide'

                    case_text = plateau_case[i][j].text_case
                    size = self.__canvas.unit_size // 4

                    # Si on est à la case centralle, on grossi la font et on affiche une *
                    if i == j and i == 7:
                        case_text = '\u2605'
                        size = self.__canvas.unit_size // 2

                    # Réaffichage du contenu
                    self.__canvas.itemconfigure(self.__cases[i][j][0],
                                                fill=plateau_case[i][j].code_couleur)
                    self.__canvas.itemconfigure(self.__cases[i][j][1],
                                                font=('Times', '{}'.format(size)),
                                                text=case_text)

                else:  # Affichage d'une case qui a un jeton
                    self.__canvas.itemconfigure(self.__cases[i][j][0],
                                                fill="#b9936c")
                    self.__canvas.itemconfigure(self.__cases[i][j][1],
                                                font=('Times', '{}'.format(self.__canvas.unit_size // 2)),
                                                text=plateau_case[i][j].jeton_occupant)


class ScrabbleJoueur(ScrabbleComponent):
    """
    Classe gérant l'affichage d'un joueur, de son chevalet et de ses jetons.
    Le temps de son chrono est exclus car il est asynchronnement géré
    """

    def __init__(self, canvas: ScrabbleCanvas, player_index: int):
        super().__init__()

        self.__canvas = canvas
        self.__index = player_index

        self.__nom = None
        self.__points = None
        self.__chevalet = None

        self.__jetons = []

    def clear(self):
        """
        Permet d'effacer le joueurs en cours, requis lors d'une nouvelle partir (ou d'un chargement de partie)
        :return: rien
        """
        self.__canvas.delete(self.__nom, self.__points, self.__chevalet)
        self.__nom = None
        self.__points = None
        self.__chevalet = None

        for item in self.__jetons:
            self.__canvas.delete(item[0], item[1])
        self.__jetons = []

    def dessiner(self):
        """
        Dessin/redimensionne le joueurs, son plateau et ses jetons.
        Attache le Drag-n-drop aux jetons
        :return: rien
        """
        # On ne dessine pas s'il n'y a pas de partie en cours
        if Scrabble.instance.joueur_actif is None:
            return

        # Si le joueur en cours n'existe pas (on gère toujours 4 joueurs) on ignore ce joueur
        if self.__index + 1 > len(Scrabble.instance.joueurs):
            if self.__nom is not None:
                self.clear()

            return

        # Lazy-Loading des éléments graphique et obtentions des références
        if self.__nom is None:
            self.__nom = self.__canvas.add_text(0, 0,
                                                font=('Times', '{}'.format(self.__canvas.unit_size // 2)),
                                                justify=LEFT)
            self.__points = self.__canvas.add_text(0, 0,
                                                   font=('Times', '{}'.format(self.__canvas.unit_size // 2)),
                                                   justify=RIGHT)
            self.__chevalet = self.__canvas.add_rectangle(Plateau.DIMENSION + 1, (self.__index + 1) * 2,
                                                          width=Joueur.TAILLE_CHEVALET,
                                                          fill='#97714a', tags="chevalet")

        # Déplacement / redimenssion des éléments géré
        self.__canvas.move_shape(self.__chevalet, Plateau.DIMENSION + 1, (self.__index + 1) * 2,
                                 width=Joueur.TAILLE_CHEVALET)
        self.__canvas.move_lettre(self.__nom, Plateau.DIMENSION + 1, self.__index * 2 + 1,
                                  width=Joueur.TAILLE_CHEVALET - 4)
        self.__canvas.move_lettre(self.__points, Plateau.DIMENSION + 6, self.__index * 2 + 1, width=2)

        # Mise à jours des informations du joueur
        joueur = Scrabble.instance.joueurs[self.__index]

        # Changement de la couleurs pour le joueurs actif
        color = Theme.theme_actif.medium if joueur != Scrabble.instance.joueur_actif else Theme.theme_actif.minor
        self.__canvas.itemconfigure(self.__nom, text=joueur.nom, fill=color)
        self.__canvas.itemconfigure(self.__points, text=joueur.points, fill=color)

        # Si le joueur géré n'est pas le joueurs actif, on supprime les jetons de son chevalet
        if joueur != Scrabble.instance.joueur_actif and len(self.__jetons) != 0:
            for item in self.__jetons:
                self.__canvas.delete(item[0], item[1])
                self.__jetons = []

        # Si en gère le joueur actif, on qu'il n'as pas encore de jetons, on les dessine
        if joueur == Scrabble.instance.joueur_actif and len(self.__jetons) == 0:
            for i, jeton in enumerate(joueur.jetons):
                if jeton is None:
                    continue

                self.__jetons.append((
                    self.__canvas.add_rectangle(Plateau.DIMENSION + 1 + i, (self.__index + 1) * 2,
                                                fill='#b9936c', tags='jeton'),
                    self.__canvas.add_text(Plateau.DIMENSION + 1 + i, (self.__index + 1) * 2,
                                           text=jeton, font=('Times', '{}'.format(self.__canvas.unit_size // 2)))
                ))

                # Ajout de la fonctionnalité de Drag-n-Drop
                DragManager(self.__canvas, [self.__jetons[-1][0], self.__jetons[-1][1]], i, joueur.moves)

        # Pour chaque jetons sur le plateau, on les re-dimensionne / déplace
        for item in self.__jetons:
            coord = self.__canvas.coords(item[0])
            prev_size = coord[2] - coord[0]
            x = coord[0] // prev_size
            y = coord[1] // prev_size

            self.__canvas.move_shape(item[0], x, y)
            self.__canvas.move_lettre(item[1], x, y)


class ScrabbleJoueurTimer(ScrabbleComponent):
    """
    Classe responsable d'afficher le chronomètre du joueurs.  Géré de façon asynchrone
    """

    def __init__(self, canvas: ScrabbleCanvas, player_index: int):
        super().__init__(True)

        self.__canvas = canvas
        self.__index = player_index
        self.__temps = None

    def clear(self):
        """
        Permet d'effacer le temps du joueur géré, requis lors d'une nouvelle partir (ou d'un chargement de partie)
        :return: rien
        """
        self.__canvas.delete(self.__temps)
        self.__temps = None

    def dessiner(self):
        """
        Dessine le temps de jeu de ce joueur
        :return: rien
        """
        # On ne dessine pas lorsqu'il n'y a pas de partie en cours
        if Scrabble.instance.joueur_actif is None:
            return

        # Si le joueur en cours n'existe pas (on gère toujours 4 joueurs) on ignore ce joueur
        if self.__index + 1 > len(Scrabble.instance.joueurs):
            if self.__temps is not None:
                self.__temps = None
            return

        # Lasy-Loading des éléments graphique
        if self.__temps is None:
            self.__temps = self.__canvas.add_text(0, 0, justify=RIGHT,
                                                  font=('Times', '{}'.format(self.__canvas.unit_size // 2)))

        # Déplacement / redessiner à l'endroit approprié
        self.__canvas.move_lettre(self.__temps, Plateau.DIMENSION + 4, self.__index * 2 + 1, width=2)

        # On change la couleur pour le joueur actif
        joueur = Scrabble.instance.joueurs[self.__index]
        color = Theme.theme_actif.medium if joueur != Scrabble.instance.joueur_actif else Theme.theme_actif.minor
        self.__canvas.itemconfigure(self.__temps, text="{:02}:{:02}".format(*divmod(int(joueur.temps_jeu_total), 60)),
                                    fill=color)


class ScrabbleTimer(ScrabbleComponent):
    """
    Cette classe est responsable de l'affichage du cadran de la partie.  Géré de façon asynchrone
    """
    def __init__(self, canvas: ScrabbleCanvas):
        super().__init__(True)

        self.__canvas = canvas
        self.__clock_frame = None
        self.__clock_label = None

    def dessiner(self):
        # On ne dessine pas s'il n'y a pas de partie en cours
        if Scrabble.instance.joueur_actif is None:
            return

        # Lazy-Loading des éléments de la classes
        if self.__clock_frame is None:
            self.__clock_frame = self.__canvas.add_rectangle(0, 0)
            self.__clock_label = self.__canvas.add_text(0, 0,
                                                        font=('Times', '{}'.format(self.__canvas.unit_size // 2)))

        # On déplace les éléments du cadrant
        self.__canvas.move_shape(self.__clock_frame, Plateau.DIMENSION + 1, 0, width=Joueur.TAILLE_CHEVALET)
        self.__canvas.move_lettre(self.__clock_label, Plateau.DIMENSION + 1, 0, width=Joueur.TAILLE_CHEVALET)

        # On rafraichie le temps affiché
        self.__canvas.itemconfigure(self.__clock_frame, fill=Theme.theme_actif.medium)
        self.__canvas.itemconfigure(self.__clock_label, fill=Theme.theme_actif.major,
                                    text="Temps Restant : {:02d}:{:02d}".format(*divmod(
                                        int(Scrabble.instance.temps_restant),
                                        60)))
