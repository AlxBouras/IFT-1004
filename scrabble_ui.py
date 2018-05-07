from tkinter import messagebox
from time import sleep
from threading import Thread
from tp4.ui.scrabble_components import *
from tp4.scrabble import Scrabble
from tp4.ui.theme_manager import Theme


class ScrabbleUI(Tk):
    """
    Classe responsable de la couche présentation de scrabble (Implémente tkinter.Tk).

    Le layout est une grille de <Taille Plateau + Taille Chevalet + 1> x <Taille Platean> (23 x 15 cases par défault)

    Le canvas est passé à des classes du module tp4.ui.scrabble_components pour gèrer les différentes section
    de l'affichage indépendament.

    +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
    |                                                           |   |  géré par ScrabbleTimer   |
    +                                                           +   +---------------------------+
    |                                                           |   |     Section des Joueurs   |
    +                                                           +   +                           +
    |                                                           |   | La gestion de l'affichage |
    +                                                           +   + est faites via quatre (4) +
    |                                                           |   | instance de ScrabbleJoueur|
    +                                                           +   +                           +
    |                                                           |   |                           |
    +                                                           +   +                           +
    |                                                           |   | Les cadrant associé aux   |
    +          Dection plateau géré par ScrabblePlateau         +   + joueurs sont géré par la  +
    |                                                           |   | classe ScrabbleJoueurTemps|
    +                                                           +   + et est rapellé de façon   +
    |                             *                             |   | Asynchrone                |
    +                                                           +   +                           +
    |                                                           |   |                           |
    +                                                           +   +---------------------------+
    |                                                           |   |                           |
    +                                                           +   +---------------------------+
    |                                                           |   | Section de messages, géré |
    +                                                           +   + par ScrabbleMessages      +
    |                                                           |   |                           |
    +                                                           +   +---------------------------+
    |                                                           |   |                           |
    +                                                           +   +---------------------------+
    |                                                           |   | Section des boutons, géré |
    +                                                           +   + par ScrabbleActions       +
    |                                                           |   |                           |
    +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+

    """

    def __init__(self):
        """
        Initialisation de l'écran de jeu
        """
        super().__init__()
        Scrabble(self)

        # Propriétés général de la fenêtre
        self.title('Scrabble')
        self.geometry("800x522")
        self.aspect(Plateau.DIMENSION + Joueur.TAILLE_CHEVALET + 1, Plateau.DIMENSION,
                    Plateau.DIMENSION + Joueur.TAILLE_CHEVALET + 1, Plateau.DIMENSION)

        # Création du canvas principal
        self.__canvas = ScrabbleCanvas(self, highlightthickness=0)
        self.__canvas.place(x=0)

        # Ajout des instances responssable de la gestion de l'affichage
        self.__components = []

        self.__components.append(ScrabbleActions(self.__canvas))
        self.__components.append(ScrabbleMessages(self.__canvas))
        self.__components.append(ScrabblePlateau(self.__canvas))
        self.__components.append(ScrabbleTimer(self.__canvas))
        for i in range(4):
            self.__components.append(ScrabbleJoueur(canvas=self.__canvas, player_index=i))
            self.__components.append(ScrabbleJoueurTimer(self.__canvas, i))

        # Création du menu de haut de page
        TopMenu(self)

        # Instantiation du module d'auto-refresh
        AsyncRefresher(self.__components).start()

        # Bind de dessiner, pour re-dessiner la page en cas de redimentionnement
        self.bind('<Configure>', self.dessiner)

    def dessiner(self, event: Event=None):
        """
        Orchestrateur de l'affichage des différentes composantes de la fenêtre

        Cette méthode calcule la nouvelle dimenssion d'une unité (équivalent à 1 jeton) en pixel.
        Il va ensuite demander à toutes les composantes de se re-dessiner

        :param event: paramêtre obligatoire pour permettre le binding sur l'évènement Configure de la fenêtre
        :return: rien
        """

        # Calcul les nouvelles dimensions d'une case, et la dimention du canvas pour respecter le ratio 23x15
        self.__canvas.unit_size = (self.winfo_height()-2) // Plateau.DIMENSION
        self.__canvas.configure(width=self.__canvas.unit_size * (Plateau.DIMENSION + Joueur.TAILLE_CHEVALET + 2),
                                height=self.__canvas.unit_size * Plateau.DIMENSION + 1)

        self.configure(background=Theme.theme_actif.major)
        self.__canvas.configure(background=Theme.theme_actif.major)

        # Redessine les différentes composantes
        for components in self.__components:
            components.dessiner()

    def clear(self):
        """
        Permmet d'exécuter faire le ménage des composantes (supression de composante graphique et de référence objet)

        :return: rien
        """
        # Supprimer les référence persistante
        for components in self.__components:
            components.clear()


class TopMenu(Menu):
    """
    Voici le menu de haut de fenêtre.
    Il ne compose que 2 section, soit fichier et À propos.

    Les action de niveau administrative sont ici (Nouvelle partie, charger, sauvegarder, quitter, règlement, etc...)

    """

    def __init__(self, master: ScrabbleUI):
        super().__init__(master)
        self.theme = StringVar()
        self.theme.set('Université Laval - Inversé')

        # Création du sous-menu Fichier
        menu_fichier = Menu(self)
        menu_fichier.add_command(label='Nouvelle partie', command=lambda: NewGamePopup(master))
        menu_fichier.add_command(label='Charger une partie', command=self.message_sauvegarde_avant_charger_partie)
        menu_fichier.add_separator()
        menu_fichier.add_command(label='Sauvegarger la partie', command=Scrabble.instance.sauvegarder_partie)
        menu_fichier.add_separator()
        menu_fichier.add_command(label='Quitter', command=self.message_sauvegarde_avant_quitter)
        self.add_cascade(label='Fichier', menu=menu_fichier)

        # Création du sous-menu Thème
        menu_theme = Menu(self)
        for i, theme in enumerate(Theme.theme_list.keys()):
            menu_theme.add_radiobutton(label=theme, value=theme, variable=self.theme, command=self.changer_theme)
        self.add_cascade(label='Thème', menu=menu_theme)

        # Création du sous-menu A propos
        menu_a_propos = Menu(self)
        menu_a_propos.add_command(label='Règlements du Scrabble', command=lambda: RulesPopup(master))
        self.add_cascade(label='À propos', menu=menu_a_propos)

        # Affichage de la barre de menu
        master.config(menu=self)

    def changer_theme(self):
        Theme.theme_actif = Theme.theme_list[self.theme.get()]
        self.master.dessiner()

    def message_sauvegarde_avant_charger_partie(self):
        """
        Affiche un message demandant à l'utilisateur s'il veut sauvegarder avant de charger une partie

        Le message n'est demandé que s'il y a une partie en cours

        Si le joueur demande une sauvegarde, mais annule la sauvegarde, tout l'action de chargement est annulé
        :return: aucun
        """

        # Demander pour la sauvegarde
        if Scrabble.instance.joueur_actif is not None and messagebox.askyesno(
                title="Sauvegarder avant de charger une partie",
                parent=self, icon="question",
                message="Voulez-vous sauvegarder avant de charger une autre partie?"):

            if not Scrabble.instance.sauvegarder_partie():
                return

        # Charger la partie
        Scrabble.instance.charger_partie()

        # Effacer les message en cours et rafraichir l'écran
        ScrabbleMessages.ui.message("")
        self.master.dessiner()

    def message_sauvegarde_avant_quitter(self):
        """
        Affiche un message demandant à l'utilisateur s'il veut sauvegarder avant de quitter la partie

        Le message n'est pas afficher s'il n'y a pas de partie en cours

        :return: aucun
        """

        # Demander si l'on doit sauvegarder
        if Scrabble.instance.joueur_actif is not None and messagebox.askyesno(
                title="Sauvegarder avant de quitter",
                parent=self, icon="question",
                message="Voulez-vous sauvegarder avant de quitter?"):

            if not Scrabble.instance.sauvegarder_partie():
                return

        self.master.destroy()


class NewGamePopup(Toplevel):
    """
    Nouvelle fenêtre permettant de sélectionner le nombre de joueurs et la langue de jeu.
    Les valeurs par défaut est de 2 joueurs et fr
    :return: 2, 3 ou 4, soit le nombre de joueurs sélectionnés ainsi que fr ou en, soit la langue sélectionnée
    """

    def __init__(self, master: ScrabbleUI):
        super().__init__(master)

        self.wm_title("Nombre de joueurs et choix de langue de jeu")

        self.nbre_joueurs = IntVar()
        self.nbre_joueurs.set(2)
        self.choix_langue = StringVar()
        self.choix_langue.set("fr")

        Label(self, text="Veuillez choisir le nombre de joueurs pour la partie:", padx=20).grid(sticky="w")
        Radiobutton(self, text="2 joueurs", padx=20, variable=self.nbre_joueurs, value=2).grid(sticky="w")
        Radiobutton(self, text="3 joueurs", padx=20, variable=self.nbre_joueurs, value=3).grid(sticky="w")
        Radiobutton(self, text="4 joueurs", padx=20, variable=self.nbre_joueurs, value=4).grid(sticky="w")

        Label(self, text="Veuillez choisir la langue de jeu pour la partie:", padx=20).grid(sticky="w")
        Radiobutton(self, text="Français", padx=20, variable=self.choix_langue, value="fr").grid(sticky="w")
        Radiobutton(self, text="Anglais", padx=20, variable=self.choix_langue, value="en").grid(sticky="w")

        Button(self, text="OK", command=self.close).grid()

        ScrabbleMessages.ui.message("")

    def close(self):
        """
        Fermeture de la fenêtre
        :return: rien
        """
        Scrabble.instance.initialiser_jeu(self.nbre_joueurs.get(), self.choix_langue.get())
        self.master.clear()
        self.master.dessiner()
        self.destroy()


class RulesPopup(Toplevel):
    """
    Nouvelle fenêtre affichant les règles du jeu
    """

    def __init__(self, master):
        super().__init__(master)

        self.wm_title("Règlements du jeu de Scrabble")

        # Chargement des rêgles
        fichier = open("reglements.txt", "r")
        reglements = fichier.read()
        fichier.close()

        # Création d'un frame dans la fenêtre
        frame_reglements = Frame(self)
        frame_reglements.grid()

        # création d'un widget de texte pour afficher les règlements
        texte_reglements = Text(frame_reglements, height=20, width=100, borderwidth=3)
        texte_reglements.config(font=("times", 16), undo=True, wrap='word')
        texte_reglements.insert("end", reglements)
        texte_reglements.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # création d'une barre de déroulement
        scrollb = Scrollbar(frame_reglements, command=texte_reglements.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        texte_reglements['yscrollcommand'] = scrollb.set

        Button(frame_reglements, text="Fermer fenêtre", command=self.destroy).grid()


class AsyncRefresher(Thread):
    """
    Classe utilitaire permettant de rafraichir dynamiquement des section de l'écran (à interval régulier, dans un 2em
    thread

    Lors de sa créations, les composantes passé en paramêtre sont analysé pour découvrire celle qui sont asynchrone.

    Les composantes asynchrone sont par la suite re-dessiné à interval régulier (quart de secondes)
    """

    instance = None

    def __init__(self, components):
        super().__init__()
        self.daemon = True
        self.__async_components: [ScrabbleComponent] = []

        # Enregistrement des composantes déclaré asynchrone
        for component in components:
            if component.async:
                self.__async_components.append(component)

        AsyncRefresher.instance = self

    def run(self):
        # Ne pas commencer avant que la partie débute
        while Scrabble.instance.joueur_actif is None:
            sleep(1)

        while True:
            try:
                sleep(1 / 4)
                for component in self.__async_components:
                    component.dessiner()
            except:
                pass  # I know this is bad... but ignore...


if __name__ == '__main__':
    ScrabbleUI().mainloop()
