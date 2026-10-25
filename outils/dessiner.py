"""Dessine les positions du catalogue en images exactes (PNG par étape + GIF animé).

Usage : python3 outils/dessiner.py s01e01
Sortie : visuels/positions/<nom>/
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from damier import Position, trouver_coup, vers_coord
from positions import POSITIONS, verifier

CASE = 84
BORD = 36
COULEURS = {
    "clair": "#F3E6C9",
    "fonce": "#9C6136",
    "cadre": "#4A2A14",
    "blanc": "#FBF8F1",
    "blanc_ombre": "#B9B2A3",
    "noir": "#26211E",
    "noir_reflet": "#5A514B",
    "fleche": "#E8452C",
    "prise": "#E8452C",
    "numero": "#E9D2B0",
    "fond_texte": "#1B2A4A",
    "texte": "#FFF6E0",
}
RACINE = Path(__file__).resolve().parent.parent


def _police(taille: int, gras: bool = False):
    noms = ["DejaVuSans-Bold.ttf" if gras else "DejaVuSans.ttf", "Arial Bold.ttf" if gras else "Arial.ttf"]
    for nom in noms:
        for dossier in ["/usr/share/fonts/truetype/dejavu", "C:/Windows/Fonts", "/Library/Fonts"]:
            try:
                return ImageFont.truetype(f"{dossier}/{nom}", taille)
            except OSError:
                continue
    return ImageFont.load_default()


def _centre(case: int) -> tuple[int, int]:
    ligne, colonne = vers_coord(case)
    return BORD + colonne * CASE + CASE // 2, BORD + ligne * CASE + CASE // 2


def dessiner(pos: Position, fleche: list[int] | None = None, prises: list[int] | None = None,
             legende: str = "") -> Image.Image:
    taille = 10 * CASE + 2 * BORD
    hauteur_texte = 110 if legende else 0
    img = Image.new("RGB", (taille, taille + hauteur_texte), COULEURS["cadre"])
    d = ImageDraw.Draw(img)
    police_num = _police(15)

    for ligne in range(10):
        for colonne in range(10):
            x, y = BORD + colonne * CASE, BORD + ligne * CASE
            fonce = (ligne + colonne) % 2 == 1
            d.rectangle([x, y, x + CASE, y + CASE], fill=COULEURS["fonce" if fonce else "clair"])
            if fonce:
                numero = ligne * 5 + colonne // 2 + 1
                d.text((x + 5, y + 3), str(numero), fill=COULEURS["numero"], font=police_num)

    rayon = int(CASE * 0.38)
    for case, piece in pos.pieces.items():
        cx, cy = _centre(case)
        blanc = piece.lower() == "w"
        corps, ombre = (COULEURS["blanc"], COULEURS["blanc_ombre"]) if blanc else (COULEURS["noir"], COULEURS["noir_reflet"])
        # Épaisseur du jeton, puis dessus avec un anneau.
        d.ellipse([cx - rayon, cy - rayon + 6, cx + rayon, cy + rayon + 6], fill=ombre)
        d.ellipse([cx - rayon, cy - rayon, cx + rayon, cy + rayon], fill=corps, outline=ombre, width=3)
        d.ellipse([cx - rayon * 0.62, cy - rayon * 0.62, cx + rayon * 0.62, cy + rayon * 0.62], outline=ombre, width=2)
        if piece.isupper():
            d.text((cx, cy), "♛", fill=ombre, font=_police(30, True), anchor="mm")

    for case in prises or []:
        cx, cy = _centre(case)
        r = rayon + 4
        d.line([cx - r, cy - r, cx + r, cy + r], fill=COULEURS["prise"], width=9)
        d.line([cx - r, cy + r, cx + r, cy - r], fill=COULEURS["prise"], width=9)

    if fleche:
        points = [_centre(c) for c in fleche]
        d.line(points, fill=COULEURS["fleche"], width=10, joint="curve")
        (x0, y0), (x1, y1) = points[-2], points[-1]
        import math
        angle = math.atan2(y1 - y0, x1 - x0)
        pointe = [(x1 + 6 * math.cos(angle), y1 + 6 * math.sin(angle))]
        for delta in (2.6, -2.6):
            pointe.append((x1 + 30 * math.cos(angle + delta), y1 + 30 * math.sin(angle + delta)))
        d.polygon(pointe, fill=COULEURS["fleche"])

    if legende:
        d.rectangle([0, taille, taille, taille + hauteur_texte], fill=COULEURS["fond_texte"])
        lignes = legende.split("\n")
        hauteur_ligne = hauteur_texte // (len(lignes) + 1)
        for i, texte in enumerate(lignes):
            corps = 34 if i == 0 else 26
            while corps > 12 and d.textlength(texte, font=_police(corps, i == 0)) > taille - 40:
                corps -= 1
            d.text((taille // 2, taille + hauteur_ligne * (i + 1)), texte, fill=COULEURS["texte"],
                   font=_police(corps, i == 0), anchor="mm")
    return img


def exporter(nom: str) -> Path:
    fiche = POSITIONS[nom]
    etapes = verifier(nom)
    dossier = RACINE / "visuels" / "positions" / nom
    dossier.mkdir(parents=True, exist_ok=True)

    images = [dessiner(etapes[0], legende=fiche["titre"])]
    for i, (notation, commentaire, _) in enumerate(fiche["solution"]):
        coup = trouver_coup(etapes[i], notation)
        legende = f"{notation}\n{commentaire}"
        images.append(dessiner(etapes[i], fleche=coup.chemin, prises=coup.prises, legende=legende))
        images.append(dessiner(etapes[i + 1], legende=legende))

    for n, image in enumerate(images):
        image.save(dossier / f"{n:02d}.png")
    # Version sans légende, pour l'incruster dans les vidéos (les sous-titres prennent sa place).
    dessiner(etapes[0]).save(dossier / "plateau.png")
    durees = [2600] + [1700, 1200] * len(fiche["solution"])
    durees[-1] = 3000
    images[0].save(dossier / f"{nom}.gif", save_all=True, append_images=images[1:], duration=durees, loop=0)
    return dossier


if __name__ == "__main__":
    for nom in sys.argv[1:] or POSITIONS:
        print("→", exporter(nom))
