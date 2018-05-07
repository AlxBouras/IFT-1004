class ScrabbleError(Exception):
    """
    Base Exception class
    """
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


class MotAbsentError(ScrabbleError):

    def __init__(self):
        super().__init__("Au moins l'un des mots formés est absent du dictionnaire.")


class PositionPlateauError(ScrabbleError):

    def __init__(self):
        super().__init__("Les positions sur le plateau sont invalides.")


class PositionInvalidError(ScrabbleError):

    def __init__(self):
        super().__init__("Une ou plusieurs position identifié sont invalide.")


class PositionVideError(ScrabbleError):

    def __init__(self):
        super().__init__("Aucun jeton à cette position.")


class PositionNonVideError(ScrabbleError):

    def __init__(self):
        super().__init__("La position est déjà occupée.")


class NomVideError(ScrabbleError):

    def __init__(self):
        super().__init__("Le nom du joueur ne doit pas être non vide.")


class ScrabbleSystemError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
