"""Catalogue des positions de l'anime, avec leur solution.

Lancer `python3 outils/positions.py` vérifie que chaque position est légale et que
chaque coup de la solution est bien le seul coup possible quand l'histoire le dit
(prise obligatoire, prise majoritaire).
"""

from __future__ import annotations

from damier import BLANC, NOIR, Position, coups_legaux, jouer, materiel, trouver_coup

POSITIONS = {
    "s01e01": {
        "titre": "Les blancs jouent et gagnent",
        "episodes": "S01E01 (le problème au tableau), S01E02 (la solution de Léo)",
        "fen": "W:W29,33,34,36,47,49:B11,12,21,32,35",
        # (coup, commentaire, forcé ?) ; forcé = c'est le seul coup légal.
        "solution": [
            ("33-28", "Léo donne un pion ! Toute la classe rit.", False),
            ("32x23", "Les noirs sont OBLIGÉS de prendre.", True),
            ("29x18x7x16x27", "La rafle : quatre pions d'un coup, en zigzag.", True),
            ("35-40", "Le dernier pion noir n'a qu'un seul coup.", True),
            ("34x45", "Et il se fait prendre. Les noirs n'ont plus rien.", True),
        ],
    },
}


def verifier(nom: str) -> list[Position]:
    """Rejoue la solution et renvoie la liste des positions successives."""
    fiche = POSITIONS[nom]
    pos = Position.depuis_fen(fiche["fen"])
    assert not coups_legaux(pos)[0].prises, f"{nom} : il y a déjà une prise au départ"
    etapes = [pos]
    for notation, commentaire, force in fiche["solution"]:
        legaux = coups_legaux(pos)
        coup = trouver_coup(pos, notation)
        if force:
            assert len(legaux) == 1, f"{nom} : {notation} devrait être forcé, il y a {len(legaux)} coups"
        pos = jouer(pos, coup)
        etapes.append(pos)
    return etapes


if __name__ == "__main__":
    for nom, fiche in POSITIONS.items():
        etapes = verifier(nom)
        fin = etapes[-1]
        perdant = fin.trait
        bilan = "plus aucun coup" if not coups_legaux(fin) else "la partie continue"
        print(f"✔ {nom} – {fiche['titre']}")
        print(f"  départ : {fiche['fen']}")
        print(f"  arrivée : {fin.fen()}  ({'noirs' if perdant == NOIR else 'blancs'} au trait : {bilan})")
        print(f"  matériel final : blancs {materiel(fin, BLANC)}, noirs {materiel(fin, NOIR)}")
