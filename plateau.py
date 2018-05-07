from tp4.error import *
from tp4.ui.theme_manager import Theme


class Jeton:
    """
    Cette classe représente un jeton.

    Les attributs d'un jeton sont:
    - lettre: str, représentant la lettre écrite sur le jeton. Par convention toutes les lettres au scrabble sont en
                majuscules. Dans ce travail nous ne considérons pas les jetons jokers qui n'ont aucune lettre inscrite.
    - valeur: int, compris entre 0 et 20 inclusivement et représentant le nombre de points associé au jeton.
    """
    def __init__(self, lettre, valeur):
        """
        Constructeur de la classe. Permet de créer un Jeton à partir d'une lettre et d'un nombre de points
        :param lettre: str, représentant la lettre écrite sur le jeton.
        :param valeur: int, > 0 représentant le nombre de points associé au jeton.
        :exception: Levez une exception avec assert si la valeur ne respecte pas
        la condition suivante 0 <= valeur <= 20 ou si la lettre n'est pas en majuscule.
        """
        if len(lettre) != 1 or not lettre.isupper() or not lettre.isalpha():
            raise ScrabbleSystemError("La Lettre d'un jeton doit être compris entre A et Z.")

        if valeur <= 0 or valeur > 20:
            raise ScrabbleSystemError("La valeur du jeton doit être comprise entre 0 et 20 (inclusivement)")

        self.lettre = lettre
        self.valeur = valeur

    def __str__(self):
        """ *** Vous n'avez pas à coder cette méthode ***
        Formatage d'un jeton. Cette méthode est appelée lorsque vous faites str(v) où v est un jeton.
        :return: str, correspondant au formatage du jeton.
        """
        if self.valeur < 10:
            res = "{}{}".format(self.lettre, chr(0x2080 + self.valeur))
        else:
            res = "{}{}{}".format(self.lettre, chr(0x2080 + int(self.valeur/10)), chr(0x2080 + int(self.valeur % 10)))
        return res


class Case:
    """
    Cette classe représente une case sur un tableau de scrabble.

    Les attributs d'une case sont:
    - multiplicateur: int, >= 1 et <= 3.
                        Si la case n'est pas spéciale son multiplicateur de points est de 1.
                        Autrement, il sera de 2 dans le cas d'une case compte double ou
                        3 dans le cas d'une case compte triple.
    - type: str, 'M' si la case est spéciale et affecte le pointage des mots;
                 'L' si la case est spéciale et affecte le pointage des lettres;
                 None si la case n'est pas spéciale.
    - jeton_occupant: Jeton,
    """

    def __init__(self, multiplicateur=1, case_type=None):
        """
        Constructeur de la classe.
        Notez qu'une case nouvellement créée est vide, c'est-à-dire le jeton occupant est None.
        :param multiplicateur: (int, optionel) multiplicateur de la case.
        :param case_type: (str, optionel) type de la case.
        :exception: Levez une exception avec assert si le multiplicateur ne respecte pas
        la condition suivante 1 <= multiplicateur <= 3 ou si le type n'est ni None, ni 'M', ni 'L'.
        """
        if multiplicateur < 1 or multiplicateur > 3:
            raise ScrabbleSystemError("Le Multiplicateur d'une case doit être compris entre 1 et 3 (inclusivement).")

        if case_type is not None and case_type not in "ML":
            raise ScrabbleSystemError("Le type d'une case doit être None, M ou L")

        self.multiplicateur = multiplicateur
        self.type = case_type
        self.jeton_occupant: Jeton = None

    def est_vide(self):
        """
        Vérifie si une case est vide ou pas (jeton_occupant est None ou pas).
        :return: True si la case est vide, False sinon.
        """
        return self.jeton_occupant is None

    def placer_jeton(self, jeton):
        """
        Place un jeton dans la case.
        :param jeton: Jeton, objet à placer dans la case.
        :return: Ne retourne rien.
        :exception: Levez une exception avec assert si la case est déjà occupée.
        """
        if not self.est_vide():
            raise PositionNonVideError()

        self.jeton_occupant = jeton

    def retirer_jeton(self):
        """
        Retire le jeton de la case.
        :return: Le jeton retiré.
        :exception: Levez une exception avec assert si la case est vide.
        """
        if self.est_vide():
            raise PositionVideError()

        jeton = self.jeton_occupant
        self.jeton_occupant = None
        return jeton

    def valeur_jeton(self):
        """
        Permet de trouver la valeur du jeton dans la case.
        :return: int, valeur du jeton occupant.
        :exception: Levez une exception avec assert si la case est vide.
        """
        if self.est_vide():
            raise PositionVideError()

        return self.jeton_occupant.valeur

    def lettre_jeton(self):
        """
        Permet de trouver la lettre inscrite sur le jeton dans la case.
        :return: str, lettre du jeton occupant.
        :exception: Levez une exception avec assert si la case est vide.
        """
        if self.est_vide():
            PositionVideError()

        return self.jeton_occupant.lettre
    
    @property
    def code_couleur(self):
        """  *** Vous n'avez pas à coder cette méthode ***
        Méthode permettant de trouver la couleur associée à une case.
        :return: int, code de couleur de la case.
        """
        if self.type == "M" and self.multiplicateur == 2:
            return Theme.theme_actif.m2
        elif self.type == "M" and self.multiplicateur == 3:
            return Theme.theme_actif.m3
        elif self.type == "L" and self.multiplicateur == 2:
            return Theme.theme_actif.l2
        elif self.type == "L" and self.multiplicateur == 3:
            return Theme.theme_actif.l3
        else:
            return Theme.theme_actif.reg

    @property
    def text_case(self):
        """  *** Vous n'avez pas à coder cette méthode ***
        Méthode permettant de trouver le texte associé à une case.
        :return: int, texte de la case.
        """
        if self.type == "M" and self.multiplicateur == 2:
            return "Mot\nDouble"
        elif self.type == "M" and self.multiplicateur == 3:
            return "Mot\nTriple"
        elif self.type == "L" and self.multiplicateur == 2:
            return "Lettre\nDouble"
        elif self.type == "L" and self.multiplicateur == 3:
            return "Lettre\nTriple"
        else:
            return ''

    def __str__(self):
        """  *** Vous n'avez pas à coder cette méthode ***
        Formatage d'une case. Cette méthode est appelée lorsque vous faites str(v) où v est un case
        :return: str, correspondant au formatage de la case.
        """
        s = "" if self.est_vide() else str(self.jeton_occupant)
        return "\x1b[0;30;{}m{:^4s}\x1b[0m".format(self.code_couleur, s)


class Plateau:
    """
    Cette classe représente un plateau de scrabble.
    Une partie de la logique du jeu sera implémentée ici donc lisez bien les spécifications de chaque méthode.
    ex:
             1    2    3    4    5    6    7    8    9   10   11   12   13   14   15
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        A |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | A
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        B |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | B
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        C |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | C
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        D |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | D
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        E |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | E
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        F |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | F
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        G |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | G
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        H |    |    |    |    |    |    |    | ★  |    |    |    |    |    |    |    | H
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        I |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | I
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        J |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | J
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        K |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | K
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        L |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | L
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        M |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | M
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        N |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | N
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
        O |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    | O
          +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
             1    2    3    4    5    6    7    8    9   10   11   12   13   14   15

    Nous avons un attribut de classe:
    - DIMENSION qui représente la dimension (nombre de lignes ou de colonnes) pour le plateu de scrabble.
            Par défaut sa valeur est de 15.

    Un plateau de scrabble a pour attribut:
    - cases: Case list list, une liste de liste de cases.
            Le programmeur peut avoir accès et manipuler les cases du plateau avec des indexes i et j,
                tels que 0 <= i < Plateau.DIMENSION et 0 <= i < Plateau.DIMENSION.
            Pour vous aider un peu:
                * cases[i] vous retourne la i+1 ème ligne du plateau. (L'index i == 0 correspond donc à la première
                            ligne, et ainsi de suite).
                * cases[i][j] vous donne la case au croisement de la i+1 ème ligne et de la j+1 ème colonne du plateau.
                            (L'index j == 0 correspond donc à la première colonne, et ainsi de suite).

            L'utilisateur de la classe, désignera les cases grâce à un code au format « XY » où X représente une lettre
                comprise entre 'A' et 'O', et Y un nombre compris entre 1 et 15. Ex: K9, E15.
            - La lettre désigne une ligne: 'A' pour la 1ère ligne, B pour la seconde ligne, etc.
            - Le nombre désigne une colonne: 5 correspond à la 5ème colonne.
            Par exemple:
            - K9 permet de désigner la case à l'intersection de la 11ème ligne et de la 9ème colonne.
            - E15 permet de désigner la case à l'intersection de la 5ème ligne et 15ème colonne.
            Note: Vous pouvez vour servir du graphe ASCII plus haut pour une meilleure compréhension.
    """
    DIMENSION = 15

    def __init__(self):
        """ *** Vous n'avez pas à coder cette méthode ***
        Constructeur d'un plateau.
        Pour compléter cette méthode vous devez vous référer à la configuration réelle d'un plateau de scrabble.
        Vous pouvez commencer par créer l'attribut cases en considérant qu'aucune case n'est spéciale.
        Regardez ensuite sur un vrai plateau de scrabble quelles positions sont spéciales, créer ces cases spéciales et
            remplacez les anciennes cases.
        """
        self.cases = [[Case() for _ in range(Plateau.DIMENSION)] for _ in range(Plateau.DIMENSION)]
        for (i, j) in [(0, 0), (0, 7), (0, 14), (7, 0), (7, 14), (14, 0), (14, 7), (14, 14)]:
            self.cases[i][j] = Case(3, 'M')
        for (i, j) in [(1, 5), (1, 9), (5, 1), (5, 5), (5, 9), (5, 13),
                       (9, 1), (9, 5), (9, 9), (9, 13), (13, 5), (13, 9)]:
            self.cases[i][j] = Case(3, 'L')
        for i in [1, 2, 3, 4]:
            self.cases[i][i] = Case(2, 'M')
            self.cases[i][Plateau.DIMENSION - i - 1] = Case(2, 'M')
            self.cases[Plateau.DIMENSION - i - 1][Plateau.DIMENSION - i - 1] = Case(2, 'M')
            self.cases[Plateau.DIMENSION - i - 1][i] = Case(2, 'M')
        for i, j in [(1, 1), (4, 0), (0, 4), (5, 1), (1, 5), (7, 4)]:
            self.cases[7 - i][7 - j] = Case(2, 'L')
            self.cases[7 + i][7 - j] = Case(2, 'L')
            self.cases[7 - i][7 + j] = Case(2, 'L')
            self.cases[7 + i][7 + j] = Case(2, 'L')
        self.cases[7][7] = Case(2, 'M')

    @staticmethod
    def code_position_est_valide(code):
        """ *** Vous n'avez pas à coder cette méthode ***
        Méthode statique permettant de valider si un code de positionnement sur le tableau est valide ou pas.
        :param code: str au format « XY » ou « xy » représentant un code de positionnement.
        :return: True si le code passé en argument est un code de positionnement au format « XY » ou « xy » valide.
                En gros, c'est insensible à la casse.
        """
        code = code.upper()
        valide = 2 <= len(code) <= 3 and code[0].isalpha() and code[1:].isdigit()
        if valide:
            index_ligne = ord(code[0]) - ord('A')
            index_colonne = int(code[1:]) - 1
            return 0 <= index_ligne < Plateau.DIMENSION and 0 <= index_colonne < Plateau.DIMENSION
        return False

    @staticmethod
    def decode_position(code):
        """
        Méthode statique servant à transformer un code de positionnement sur le plateau
        en index d'accès de ligne et de colonne sur le plateau.

        :param code: str au format « XY » ou « xy » représentant un code de positionnement.

        :return: tuple (int, int), l'index de la ligne et l'index de la colonne associés au code.
        :exception: Levez une exception avec assert si le code de la position est invalide. Pensez à utiliser
            Plateau.code_position_est_valide.
        """
        if not Plateau.code_position_est_valide(code):
            raise PositionInvalidError
        code = code.upper()
        index_ligne = ord(code[0]) - ord('A')
        index_colonne = int(code[1:]) - 1
        return index_ligne, index_colonne

    @staticmethod
    def encode_position(ligne, column):
        """
        TODO: DOC (see above)
        """
        return format("{}{}".format(chr(ligne + ord('A')), column+1))

    def case_est_vide(self, position_code):
        """
        Permet de déterminer si une case est vide, c'est-à-dire qu'elle ne contient pas de jeton.
        :param position_code: str, au format « XY » ou « xy » qui un code de positionnement de la case sur le plateau.
        :return: True si la case est vide, False sinon.
        :exception: Levez une exception avec assert si le code de la position est invalide.
        """
        index_ligne, index_colonne = Plateau.decode_position(position_code)
        return self.cases[index_ligne][index_colonne].est_vide()

    def est_vide(self):
        """
        Permet de déterminer si le plateau est vide, c'est à dire que toutes les cases sont vides.
        :return: True si le plateau est vide, False sinon.
        """
        return all([case.est_vide() for ligne in self.cases for case in ligne])

    def ajouter_jeton(self, jeton, position_code):
        """
        Permet d'ajouter un jeton dans une case vide du plateau. La case est indiquée grâce à son code de
            positionnement.
        :param jeton: Jeton, le jeton à ajouter sur le plateau.
        :param position_code: str, la position où ajouter (au format « XY » ou « xy »)
        :return: Ne retourne rien.
        :exception: Levez une exception avec assert si le code de la position est invalide ou la case n'est pas vide.
        """
        index_ligne, index_colonne = Plateau.decode_position(position_code)

        if not self.case_est_vide(position_code):
            raise PositionNonVideError

        self.cases[index_ligne][index_colonne].placer_jeton(jeton)

    def retirer_jeton(self, position_code):
        """
        Permet d'enlever le jeton dans une case du plateau. La case est indiquée grâce à son code de positionnement.
        :param position_code: str, la position où enlever le jeton (au format « XY » ou « xy »).
        :return: Jeton, le jeton à enlever du plateau. Rappelez-vous qu'il existe une méthode retirer_jeton disponible
                pour les objets de type Case.
        :exception: Levez une exception avec assert si le code de la position est invalide ou la case n'est pas vide.
        """
        index_ligne, index_colonne = Plateau.decode_position(position_code)

        if self.case_est_vide(position_code):
            raise PositionVideError

        jeton = self.cases[index_ligne][index_colonne].retirer_jeton()
        return jeton

    def cases_adjacentes_occupees(self, position_code):
        """ *** Vous n'avez pas à coder cette méthode ***
        Étant donnée une position, cette méthode permet de voir si au moins l'une de ses positions voisines est occupée.
        Les cases voisines sont les cases juste en haut, en bas, à gauche et à droite de la case concernée.
        NB: Les cases voisines diagonales ne comptent pas.
        :param position_code: str, la position d'intérêt.
        :return: True si au moins l'une des cases voisines est occupée, False si aucune case voisine n'est occupée.
        :exception: Levez une exception avec assert si le code de la position est invalide
        """
        index_ligne, index_colonne = Plateau.decode_position(position_code)
        voisins = [(index_ligne, index_colonne - 1),
                   (index_ligne, index_colonne + 1),
                   (index_ligne + 1, index_colonne),
                   (index_ligne - 1, index_colonne)]
        voisins = [(i, j) for i, j in voisins if (0 <= i < Plateau.DIMENSION)
                   and (0 <= j < Plateau.DIMENSION)]
        return any([not self.cases[i][j].est_vide() for (i, j) in voisins])

    def valider_positions_avant_ajout(self, positions_codes):
        """ *** Vous n'avez pas à coder cette méthode ***
        Cette méthode implémente certaines règles du jeu donc soyez attentifs au texte ci-dessous.
        Étant données des positions_codes où un utilisateur veut placer ses jetons, cette méthode permet de valider s'il
            peut réelement ajouter les jetons à ces positions.
        Les positions sont valides si:
         - elles sont toutes vides;
         - elles sont toutes sur la même ligne ou la même colonne;
         - une fois qu'elles seront placées sur une même ligne ou une même colonne, elles formeront un mot et pas plus
            sur cette même ligne ou colonne. Ici, le mot formé n'est pas important du tout donc n'essayez pas de
            le trouver;
            Par exemple, si toutes les positions sont sur la ligne 5, votre code doit juste s'assurer qu'entre les
            positions où vous devez ajouter des jetons, des cases ne sont vides.
         - si le plateau est vide, le centre du plateau doit être dans les positions;
         - sinon, au moins une des positions doit être adjacente à une des cases occupées
         du plateau (Pensez à réutilisez cases_adjacentes_occupees et case_est_vide).
        :param positions_codes: str list, liste de string représentant les positions où on veut ajouter des jetons.
        :return: True si les positions sont valides, False sinon.
        :exception: Levez une exception avec assert si le code d'une des positions est invalide.
        """
        positions_decodees = [Plateau.decode_position(p) for p in positions_codes]
        lignes, cols = zip(*positions_decodees)
        lignes, cols = list(set(lignes)), list(set(cols))
        meme_ligne, meme_col = len(lignes) == 1, len(cols) == 1
        valide = meme_ligne or meme_col
        valide = valide and all([self.case_est_vide(p) for p in positions_codes])
        if valide:
            if self.est_vide():
                valide = (7, 7) in positions_decodees
            else:
                valide = any([self.cases_adjacentes_occupees(pos) for pos in positions_codes])

            if valide and meme_ligne:
                ligne, n, m = lignes[0], min(cols), max(cols)
                valide = all([(not self.cases[ligne][i].est_vide()) for i in range(n, m + 1) if i not in cols])
            elif valide and meme_col:
                col, n, m = cols[0], min(lignes), max(lignes)
                valide = all([(not self.cases[i][col].est_vide()) for i in range(n, m + 1) if i not in lignes])

        return valide

    def placer_mots(self, jetons_a_ajouter, position_codes):
        """
        Permet de placer plusieurs jetons sur le plateau afin de former un ou plusieurs mots.
        Pensez à réutiliser valider_positions_avant_ajout.
        :param jetons_a_ajouter: Jetons à ajouter pour placer nos mots.
        :param position_codes: str list, liste de chaînes de caractères représentant les positions où on veut placer
                les jetons.
        :return: tuple de type (str list, int):
            - Le premier élement est la liste des mots formés avec les jetons si l'ajout a été fait, liste vide sinon.
            - Le second élément est le score obtenu si l'ajout a été fait, 0 sinon.
        :exception: Levez une exception avec assert si les positions sont invalides.
        """
        if not self.valider_positions_avant_ajout(position_codes):
            raise PositionInvalidError()

        for jeton, pos in zip(jetons_a_ajouter, position_codes):
            self.ajouter_jeton(jeton, pos)

        mots, score = self.mots_score_obtenus(position_codes)
        return mots, score

    def mots_score_obtenus(self, nouvelles_positions):
        """ *** Vous n'avez pas à coder cette méthode ***
        Trouver les mots ajoutés et le score total obtenu lorsque le joueur vient juste d'ajouter des jetons aux
            positions de la liste en argument.
        :param nouvelles_positions: str list, liste de chaînes de caractères représentant les dernières positions où
            des jetons ont été ajoutés.
        :return: L'ensemble des mots formés par l'ajout de jetons aux nouvelles positions.
        """
        positions_decodees = [Plateau.decode_position(p) for p in nouvelles_positions]
        score_total = 0
        lignes, cols = zip(*positions_decodees)
        mots = []
        for ligne in set(lignes):
            lmots, score = self.__mots_et_score_sur_ligne_ou_colonne(positions_decodees, ligne)
            mots += lmots
            score_total += score
        for col in set(cols):
            lmots, score = self.__mots_et_score_sur_ligne_ou_colonne(positions_decodees, colonne=col)
            mots += lmots
            score_total += score
        return mots, score_total

    def __mots_et_score_sur_ligne_ou_colonne(self, positions_decodees, ligne=None, colonne=None):
        """ *** Vous n'avez pas à coder cette méthode ***
        Permet de trouver les mots sur une ligne ou une colonne et le score associé.
        :param positions_decodees:  str list, liste de chaînes de caractères représentant les dernières positions où
                des jetons ont été ajoutés.
        :param ligne: (int, optionel), index de la ligne d'intérêt
        :param colonne: (int, optionel), index de la colonne d'intérêt
        :return: tuple (str list, int), la liste des mots trouvés sur la ligne ou la colonne et le score total.
        Plus précisément la liste devra contenir au maximum un élément car un tout nouvel ajout de jetons ne peut pas
                créer plus d'un mot sur la même ligne ou colonne.
        :exception: Levez une exception avec assert si la ligne et la colonne sont spécifiées ou aucun des deux ne
                    l'est.
        """
        if ((ligne is None) and (colonne is None)) or ((ligne is not None) and (colonne is not None)):
            raise ScrabbleSystemError("Précisez seulement la ligne ou la colonne, pas les deux.")

        mots, score_total = [], 0
        mot, score_mot, multiplicateur, pos_mot = "", 0, 1, []
        for i in range(Plateau.DIMENSION):
            pos = (ligne, i) if ligne is not None else (i, colonne)
            case = self.cases[pos[0]][pos[1]]
            if case.est_vide():
                if len(mot) > 1 and any([p in pos_mot for p in positions_decodees]):
                    mots.append(mot)
                    score_total += score_mot * multiplicateur
                mot, score_mot, multiplicateur, pos_mot = "", 0, 1, []
            else:
                mot += case.lettre_jeton()
                pos_mot.append(pos)
                if pos in positions_decodees and case.type == "L":
                    score_mot += case.valeur_jeton() * case.multiplicateur
                else:
                    score_mot += case.valeur_jeton()
                if pos in positions_decodees and case.type == "M":
                    multiplicateur *= case.multiplicateur
        if len(mot) > 1 and any([p in pos_mot for p in positions_decodees]):
            mots.append(mot)
            score_total += score_mot * multiplicateur

        return mots, score_total

    def __str__(self):
        """ *** Vous n'avez pas à coder cette méthode ***
         Formatage du plateau pour l'affichage.
         Utilise des codes Unicode, ce qui pourrait causer des problèmes avec le système d'exploitation utilisé par
         certains.
         :return: str, correspondant au formatage du plateau.
        """
        ligne_separation = '  +' + '----+' * Plateau.DIMENSION + '\n'
        chaine = '   '
        for colonne in range(Plateau.DIMENSION):
            chaine += "{:^5d}".format(colonne+1)
        chaine += '\n'
        chaine += ligne_separation
        for rangee in range(Plateau.DIMENSION):
            chaine += '{} |'.format(chr(ord('A')+rangee))
            for colonne in range(Plateau.DIMENSION):
                if rangee == colonne and rangee == 7 and self.cases[rangee][colonne].est_vide():
                    s = "\x1b[0;30;{}m{:^4s}\x1b[0m".format(self.cases[rangee][colonne].code_couleur, '\u2605')
                else:
                    s = "{:^4s}".format(str(self.cases[rangee][colonne]))
                chaine += s + '|'
            chaine += ' {}\n'.format(chr(ord('A') + rangee))
            chaine += ligne_separation
        chaine += '   '
        for colonne in range(Plateau.DIMENSION):
            chaine += "{:^5d}".format(colonne+1)
        chaine += '\n'
        return chaine
