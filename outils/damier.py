"""Moteur de règles du jeu de dames international (10x10) et rendu de diagrammes.

Sert à vérifier que chaque position montrée dans l'anime est légale et que la
combinaison annoncée fonctionne vraiment, puis à dessiner le diagramme.

Notation : cases numérotées de 1 à 50 (notation officielle FMJD).
Les blancs jouent vers le haut (vers les cases 1-5), les noirs vers le bas.
"""

from __future__ import annotations

from dataclasses import dataclass, field

BLANC, NOIR = "W", "B"
DIRECTIONS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def vers_coord(case: int) -> tuple[int, int]:
    """Case 1-50 -> (ligne, colonne), ligne 0 en haut, colonne 0 à gauche."""
    ligne, i = divmod(case - 1, 5)
    colonne = 2 * i + 1 if ligne % 2 == 0 else 2 * i
    return ligne, colonne


def vers_case(ligne: int, colonne: int) -> int | None:
    if not (0 <= ligne < 10 and 0 <= colonne < 10) or (ligne + colonne) % 2 == 0:
        return None
    return ligne * 5 + colonne // 2 + 1


@dataclass
class Position:
    """pieces : case -> 'w' (pion blanc), 'W' (dame blanche), 'b', 'B'."""

    pieces: dict[int, str]
    trait: str = BLANC

    @classmethod
    def depuis_fen(cls, fen: str) -> "Position":
        """Format FMJD simplifié : 'W:W31,32,K45:B18,19' (K = dame)."""
        trait, *camps = fen.split(":")
        pieces = {}
        for camp in camps:
            couleur, liste = camp[0], camp[1:]
            for jeton in filter(None, liste.split(",")):
                dame = jeton.startswith("K")
                case = int(jeton.lstrip("K"))
                pieces[case] = couleur if dame else couleur.lower()
        return cls(pieces, trait)

    def fen(self) -> str:
        def camp(c):
            cases = sorted(k for k, v in self.pieces.items() if v.upper() == c)
            return c + ",".join(("K" if self.pieces[k].isupper() else "") + str(k) for k in cases)

        return f"{self.trait}:{camp(BLANC)}:{camp(NOIR)}"


@dataclass
class Coup:
    chemin: list[int]
    prises: list[int] = field(default_factory=list)

    def __str__(self) -> str:
        sep = "x" if self.prises else "-"
        return sep.join(str(c) for c in self.chemin)


def _adverse(piece: str, couleur: str) -> bool:
    return piece.upper() != couleur


def _prises_depuis(pos: Position, depart: int, piece: str) -> list[Coup]:
    """Toutes les rafles maximales en profondeur depuis `depart` (prises non encore filtrées)."""
    couleur = piece.upper()
    dame = piece.isupper()
    resultats: list[Coup] = []

    def explorer(case: int, chemin: list[int], prises: list[int]):
        l, c = vers_coord(case)
        prolonge = False
        for dl, dc in DIRECTIONS:
            if dame:
                # Glisse sur les cases vides jusqu'à une pièce.
                k = 1
                while True:
                    cible = vers_case(l + dl * k, c + dc * k)
                    if cible is None:
                        break
                    occupant = pos.pieces.get(cible) if cible != depart else None
                    if occupant is None:
                        k += 1
                        continue
                    if cible in prises or not _adverse(occupant, couleur):
                        break
                    # Cases d'arrivée possibles après la pièce prise.
                    m = k + 1
                    while True:
                        arrivee = vers_case(l + dl * m, c + dc * m)
                        if arrivee is None:
                            break
                        if arrivee != depart and arrivee in pos.pieces:
                            break
                        prolonge = True
                        explorer(arrivee, chemin + [arrivee], prises + [cible])
                        m += 1
                    break
            else:
                cible = vers_case(l + dl, c + dc)
                arrivee = vers_case(l + 2 * dl, c + 2 * dc)
                if cible is None or arrivee is None:
                    continue
                occupant = pos.pieces.get(cible) if cible != depart else None
                if occupant is None or cible in prises or not _adverse(occupant, couleur):
                    continue
                if arrivee != depart and arrivee in pos.pieces:
                    continue
                prolonge = True
                explorer(arrivee, chemin + [arrivee], prises + [cible])
        if not prolonge and prises:
            resultats.append(Coup(chemin, prises))

    explorer(depart, [depart], [])
    return resultats


def coups_legaux(pos: Position) -> list[Coup]:
    """Coups légaux, en appliquant la prise obligatoire et la prise majoritaire."""
    mes_pieces = [(k, v) for k, v in pos.pieces.items() if v.upper() == pos.trait]
    prises = [coup for case, piece in mes_pieces for coup in _prises_depuis(pos, case, piece)]
    if prises:
        maximum = max(len(c.prises) for c in prises)
        uniques = {}
        for coup in prises:
            if len(coup.prises) == maximum:
                uniques[(coup.chemin[0], coup.chemin[-1], tuple(sorted(coup.prises)))] = coup
        return list(uniques.values())

    coups = []
    sens = -1 if pos.trait == BLANC else 1
    for case, piece in mes_pieces:
        l, c = vers_coord(case)
        if piece.isupper():
            for dl, dc in DIRECTIONS:
                k = 1
                while (cible := vers_case(l + dl * k, c + dc * k)) and cible not in pos.pieces:
                    coups.append(Coup([case, cible]))
                    k += 1
        else:
            for dc in (-1, 1):
                cible = vers_case(l + sens, c + dc)
                if cible and cible not in pos.pieces:
                    coups.append(Coup([case, cible]))
    return coups


def jouer(pos: Position, coup: Coup) -> Position:
    pieces = dict(pos.pieces)
    piece = pieces.pop(coup.chemin[0])
    for prise in coup.prises:
        del pieces[prise]
    arrivee = coup.chemin[-1]
    ligne, _ = vers_coord(arrivee)
    if piece == "w" and ligne == 0:
        piece = "W"
    elif piece == "b" and ligne == 9:
        piece = "B"
    pieces[arrivee] = piece
    return Position(pieces, NOIR if pos.trait == BLANC else BLANC)


def trouver_coup(pos: Position, notation: str) -> Coup:
    """Retrouve un coup légal à partir de sa notation ('32-28', '23x32', '28x10')."""
    sep = "x" if "x" in notation else "-"
    cases = [int(x) for x in notation.split(sep)]
    candidats = [
        c for c in coups_legaux(pos)
        if c.chemin[0] == cases[0] and c.chemin[-1] == cases[-1]
        and all(x in c.chemin for x in cases)
    ]
    if len(candidats) != 1:
        raise ValueError(f"Coup {notation} illégal ou ambigu dans {pos.fen()} : {candidats}")
    return candidats[0]


def materiel(pos: Position, couleur: str) -> int:
    """Pion = 1, dame = 3 (barème simple pour juger une combinaison)."""
    return sum(3 if v.isupper() else 1 for v in pos.pieces.values() if v.upper() == couleur)
