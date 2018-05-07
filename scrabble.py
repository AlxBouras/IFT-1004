import pickle
from random import randint, shuffle
from time import sleep
from tp4.joueur import Joueur
from tp4.plateau import Plateau, Jeton
from tkinter import filedialog
from tp4.error import *
from threading import Thread


class Scrabble:
    """
    Classe Scrabble qui implémente aussi une partie de la logique de jeu.

    Les attributs d'un scrabble sont:
    - dictionnaire: set, contient tous les mots qui peuvent être joués sur dans cette partie.
    En gros pour savoir si un mot est permis on va regarder dans le dictionnaire.
    - plateau: Plateau, un objet de la classe Plateau on y place des jetons et il nous dit le nombre de points gagnés.
    - jetons_libres: Jeton list, la liste de tous les jetons dans le sac, c'est là que chaque joueur
                    peut prendre des jetons quand il en a besoin.
    - joueurs: Joueur list,  L'ensemble des joueurs de la partie.
    - joueur_actif: Joueur, le joueur qui est entrain de jouer le tour en cours. Si aucun joueur alors None.
    """
    TEMPS_PAR_TOUR = 60

    # Available as a singleton
    instance = None
    ui = None

    def __init__(self, ui):
        self.plateau = Plateau()
        self.joueur_actif = None
        self.joueurs: [Joueur] = None
        self.temps_restant = None
        self.dictionnaire = {}
        self.nb_joueurs = None
        self.langue = None
        self.jetons_libres: [Jeton] = None

        Scrabble.instance = self
        Scrabble.ui = ui

    def initialiser_jeu(self, nb_joueurs, langue, plateau: Plateau=None, joueurs: [Joueur]=None, joueur_actif=None,
                        jetons_libre=None, temps_restant=None):
        """
        Étant donnés un nombre de joueurs et une langue. Le constructeur crée une partie de scrabble.
        Pour une nouvelle partie de scrabble,
        - un nouvel objet Plateau est créé;
        - La liste des joueurs est créée et chaque joueur porte automatiquement le nom Joueur 1, Joueur 2, ... Joueur n
            où n est le nombre de joueurs;
        - Le joueur_actif est None.

        :param nb_joueurs: int, nombre de joueurs de la partie au minimun 2 au maximum 4.
        :param langue: str, FR pour la langue française, et EN pour la langue anglaise. Dépendamment de la langue, vous
                        devez ouvrir, lire, charger en mémoire le fichier "dictionnaire_francais.txt" ou
                        "dictionnaire_anglais.txt" ensuite il faudra ensuite extraire les mots contenus pour construire
                        un set avec le mot clé set.
        :param plateau: Optionnel, un plateau à utiliser
        :param joueurs: Optionnel, une liste de joueurs à utiliser
        :param joueur_actif: Optionnel, un joueur_actif à utiliser
        :param jetons_libre: Optionnel, les jetons_libre à considérer
        :param temps_restant: Optionnel, le temps restant du tours en cours

        :exception: ScrabbleSystemError si la Langue n'est pas conforme (FR ou EN) ou qu'il n'y a pas de 2 à 4 joueurs
        """
        Timer.exit()

        if langue.upper() not in ['FR', 'EN']:
            ScrabbleSystemError('Langue {} non supportée.'.format(langue.upper()))

        if not (2 <= nb_joueurs <= 4):
            ScrabbleSystemError("Il faut entre 2 et 4 personnes pour jouer.")

        self.plateau = Plateau() if plateau is None else plateau
        self.joueur_actif = None if joueur_actif is None else joueur_actif
        self.joueurs: [Joueur] = \
            [Joueur("Joueur {}".format(i + 1)) for i in range(nb_joueurs)] if joueurs is None else joueurs

        if jetons_libre is None:
            data = []
            if langue.upper() == 'FR':
                # Infos disponibles sur https://fr.wikipedia.org/wiki/Lettres_du_Scrabble
                data = [('E', 15, 1), ('A', 9, 1), ('I', 8, 1), ('N', 6, 1), ('O', 6, 1),
                        ('R', 6, 1), ('S', 6, 1), ('T', 6, 1), ('U', 6, 1), ('L', 5, 1),
                        ('D', 3, 2), ('M', 3, 2), ('G', 2, 2), ('B', 2, 3), ('C', 2, 3),
                        ('P', 2, 3), ('F', 2, 4), ('H', 2, 4), ('V', 2, 4), ('J', 1, 8),
                        ('Q', 1, 8), ('K', 1, 10), ('W', 1, 10), ('X', 1, 10), ('Y', 1, 10),
                        ('Z', 1, 10)]

            elif langue.upper() == 'EN':
                # Infos disponibles sur https://fr.wikipedia.org/wiki/Lettres_du_Scrabble
                data = [('E', 12, 1), ('A', 9, 1), ('I', 9, 1), ('N', 6, 1), ('O', 8, 1),
                        ('R', 6, 1), ('S', 4, 1), ('T', 6, 1), ('U', 4, 1), ('L', 4, 1),
                        ('D', 4, 2), ('M', 2, 3), ('G', 3, 2), ('B', 2, 3), ('C', 2, 3),
                        ('P', 2, 3), ('F', 2, 4), ('H', 2, 4), ('V', 2, 4), ('J', 1, 8),
                        ('Q', 1, 10), ('K', 1, 5), ('W', 2, 4), ('X', 1, 8), ('Y', 2, 4),
                        ('Z', 1, 10)]

            self.jetons_libres = \
                [Jeton(lettre, valeur) for lettre, occurences, valeur in data for i in range(occurences)]
        else:
            self.jetons_libres = jetons_libre

        nom_fichier_dictionnaire = 'dictionnaire_francais.txt' if langue.upper() == 'FR' else 'dictionnaire_anglais.txt'
        with open(nom_fichier_dictionnaire, 'r') as f:
            self.dictionnaire = set([x[:-1].upper() for x in f.readlines() if len(x[:-1]) > 1])

        self.nb_joueurs = nb_joueurs
        self.langue = langue

        self.temps_restant = 0.0 if temps_restant is None else temps_restant

        if joueur_actif is None:
            self.joueur_suivant()

        Timer.reset()

    def mot_permis(self, mot):
        """
        Permet de savoir si un mot est permis dans la partie ou pas en regardant dans le dictionnaire.
        :param mot: str, mot à vérifier.
        :return: bool, True si le mot est dans le dictionnaire, False sinon.
        """
        return mot in self.dictionnaire

    def determiner_gagnant(self):
        """
        Détermine le joueur gagnant, s'il y en a un. Pour déterminer si un joueur est le gagnant,
        il doit avoir le pointage le plus élevé de tous.

        :return: Joueur, un des joueurs gagnants, i.e si plusieurs sont à égalité on prend un au hasard.
        """
        return sorted(self.joueurs, key=lambda j: j.points, reverse=True)[0]

    def partie_terminee(self):
        """
        Vérifie si la partie est terminée. Une partie est terminée si il
        n'existe plus de jetons libres ou il reste moins de deux (2) joueurs. C'est la règle que nous avons choisi
        d'utiliser pour ce travail, donc essayez de négliger les autres que vous connaissez ou avez lu sur Internet.

        Returns:
            bool: True si la partie est terminée, et False autrement.
        """
        return len(self.jetons_libres) == 0 or len(self.joueurs) < 2

    def joueur_suivant(self):
        """
        Change le joueur actif.
        Le nouveau joueur actif est celui à l'index du (joueur courant + 1)% nb_joueurs.
        Si on n'a aucun joueur actif, on détermine au harsard le suivant.
        """

        if self.joueur_actif is None:
            self.joueur_actif = self.joueurs[randint(0, len(self.joueurs) - 1)]
        else:
            self.joueur_actif.moves = {}
            self.joueur_actif = self.joueurs[(self.joueurs.index(self.joueur_actif) + 1) % len(self.joueurs)]

        if self.joueur_actif.nb_a_tirer > 0:
            for jeton in self.tirer_jetons(self.joueur_actif.nb_a_tirer):
                self.joueur_actif.ajouter_jeton(jeton)

    def tirer_jetons(self, n):
        """
        Simule le tirage de n jetons du sac à jetons et renvoie ceux-ci. Il s'agit de prendre au hasard des jetons dans
            self.jetons_libres et de les retourner.
        Pensez à utiliser la fonction shuffle du module random.
        :param n: le nombre de jetons à tirer.
        :return: Jeton list, la liste des jetons tirés.
        :exception: Levez une exception avec assert si n ne respecte pas la condition 0 <= n <= 7.
        """
        if not (0 <= n <= len(self.jetons_libres)):
            ScrabbleSystemError("n doit être compris entre 0 et le nombre total de jetons libres.")

        shuffle(self.jetons_libres)
        res = self.jetons_libres[:n]
        self.jetons_libres = self.jetons_libres[n:]
        return res

    def demander_positions(self):
        """ *** Vous n'avez pas à coder cette méthode ***
        Demande à l'utilisateur d'entrer les positions sur le chevalet et le plateau
        pour jouer son coup.
        Si les positions entrées sont valides, on retourne les listes de ces positions. On doit
        redemander tant que l'utilisateur ne donne pas des positions valides.
        Valide ici veut dire uniquement dans les limites donc pensez à utilisez valider_positions_avant_ajout et
            Joueur.position_est_valide.

        :return: tuple (int list, str list): Deux listes, la première contient les positions du chevalet
            (plus précisement il s'agit des indexes de ces positions) et l'autre liste contient les positions
            codées du plateau.
        """
        pos_chevalet = []
        pos_plateau = []

        valide = False
        while not valide:
            input_pos_chevalet = input(
                "Entrez les positions du chevalet à jouer séparées par un espace: ").upper().strip()
            pos_chevalet = [int(x) - 1 for x in input_pos_chevalet.split(' ')]
            valide = all([Joueur.position_est_valide(pos) for pos in pos_chevalet])
            valide = valide and len(pos_chevalet) == len(set(pos_chevalet))

        valide = False
        while not valide:
            input_pos_plateau = input(
                "Entrez les positions de chacune de ces lettres séparées par un espace: ").upper().strip()
            pos_plateau = input_pos_plateau.split(' ')

            if len(pos_chevalet) != len(pos_plateau):
                print("Les nombres de jetons et de positions ne sont pas les mêmes.")
                valide = False
            else:
                valide = len(pos_plateau) == len(set(pos_plateau))
                valide = valide and self.plateau.valider_positions_avant_ajout(pos_plateau)

        return pos_chevalet, pos_plateau

    def jouer_un_tour(self):
        """
        Permet de jouer un tour

        La liste des déplacement de jetons sont pris sans le joueur_actif, propriété "moves"
        """
        if len(self.joueur_actif.moves) > 0:
            pos_chevalet = list(self.joueur_actif.moves.keys())
            pos_plateau = list(self.joueur_actif.moves.values())

            # Valider que les positions du plateau sont valide avant de retirer les jetons
            if not self.plateau.valider_positions_avant_ajout(pos_plateau):
                raise PositionPlateauError

            # Retirer les jetons du chevalets
            jetons = [self.joueur_actif.retirer_jeton(p) for p in pos_chevalet]

            # calculer le nouveau score
            mots, score = self.plateau.placer_mots(jetons, pos_plateau)
            if any([not self.mot_permis(m) for m in mots]):
                for i, pos in enumerate(pos_plateau):
                    jeton = self.plateau.retirer_jeton(pos)
                    self.joueur_actif.ajouter_jeton(jeton, pos_chevalet[i])
                raise MotAbsentError
            else:
                print("Mots formés:", mots)
                print("Score obtenu:", score)
                self.joueur_actif.ajouter_points(score)

    def sauvegarder_partie(self):
        """ *** Vous n'avez pas à coder cette méthode ***
        Permet de sauvegarder l'objet courant dans le fichier portant le nom spécifié.
        La sauvegarde se fera grâce à la fonction dump du module pickle.
        :return: True si la sauvegarde s'est bien passé, False si une erreur s'est passé durant la sauvegarde.
        """

        nom_fichier = filedialog.asksaveasfilename(initialdir="/", title='Sauvegarder la partie')
        if nom_fichier is None:
            return False

        liste = [self.plateau, self.joueurs, self.joueur_actif, self.nb_joueurs,
                 self.langue, self.jetons_libres, self.temps_restant]

        try:
            with open(nom_fichier, "wb") as f:
                pickle.dump(liste, f)
        except IOError:
            return False
        return True

    @staticmethod
    def charger_partie():
        """ *** Vous n'avez pas à coder cette méthode ***
        Méthode statique permettant de mettre à jour l'instance Scrabble.instance en lisant le fichier dans
        lequel l'objet avait été sauvegardé précédemment. Pensez à utiliser la fonction load du module pickle.
        :return: rien
        """

        nom_fichier = filedialog.askopenfilename(initialdir="/", title='Charger une partie')

        with open(nom_fichier, "rb") as f:
            liste = pickle.load(f)

        plateau = liste[0]
        joueurs = liste[1]
        joueur_actif = liste[2]
        nb_joueurs = liste[3]
        langue = liste[4]
        jetons_libres = liste[5]
        temps_restant = liste[6]

        Scrabble.instance.initialiser_jeu(nb_joueurs,
                                          langue,
                                          plateau,
                                          joueurs,
                                          joueur_actif,
                                          jetons_libres,
                                          temps_restant)


class Timer(Thread):
    """
    Timer de la partie, calcule le temps de jeu du joueur en cours, et un chrono de 60 secondes pour compléter son tour

    Exécution asynchrone
    """

    __instance = None

    def __init__(self):
        super().__init__()
        self.daemon = True

        self.__reset = False
        self.__exit = False

    def run(self):
        # Attendre qu'il y ai une partie en cours
        while Scrabble.instance.joueur_actif is None:
            sleep(1/4)

        # Tant que la partie n'est pas terminé, ou qu'un arrêt n'et pas demandé, on compte...
        while Scrabble.instance.joueur_actif is not None and not self.__exit:
            Scrabble.instance.temps_restant = Scrabble.TEMPS_PAR_TOUR

            self.countdown()

    def countdown(self):
        # Calcul du temps en cours.  Si on arrive a échéance, le joueur change
        for t in range(Scrabble.TEMPS_PAR_TOUR, -1, -1):
            for i in range(10):
                sleep(1 / 10)

                if self.__exit:
                    return

                if Scrabble.instance.joueur_actif is None:
                    return

                if self.__reset:
                    self.__reset = False
                    return

                Scrabble.instance.joueur_actif.temps_jeu_total += 1 / 10
                Scrabble.instance.temps_restant -= 1 / 10

        Scrabble.instance.joueur_suivant()
        Scrabble.ui.dessiner()

    @staticmethod
    def reset():
        """
        Permet de ré-initialiser le temps de l'horloge (lors des changement de tours)
        :return: rien
        """
        Timer.instance().__reset = True

    @staticmethod
    def exit():
        """
        Permet de terminer le temps de l'horloge (en fin de partie)
        :return:
        """
        Timer.instance().__exit = True
        Timer.__instance = None

    @staticmethod
    def instance():
        # Lazy instanciation de l'Horloge lorsque appelé
        if Timer.__instance is None:
            Timer.__instance = Timer()
            Timer.__instance.start()

        return Timer.__instance


if __name__ == '__main__':
    from tp4.scrabble_ui import ScrabbleUI
    ScrabbleUI()
