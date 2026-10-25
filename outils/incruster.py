"""Incruste une position exacte dans une image générée (par exemple le damier mural de la classe).

L'IA dessine des damiers faux (lettres d'échecs, pions sur les cases claires). On remplace le
damier de l'image par un damier mural dessiné à partir d'une position vérifiée, déformé en
perspective sur les quatre coins repérés dans l'image.

Usage : python3 outils/incruster.py
(les incrustations à faire sont listées dans INCRUSTATIONS ci-dessous)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from damier import Position, vers_coord
from positions import POSITIONS

RACINE = Path(__file__).resolve().parent.parent

# Couleurs « bois d'école », assorties à la palette des images.
MURAL = {
    "cadre": (78, 45, 22),
    "marge": (201, 146, 82),
    "clair": (233, 196, 135),
    "fonce": (128, 82, 44),
    "blanc": (244, 237, 220),
    "blanc_ombre": (170, 156, 130),
    "noir": (30, 36, 52),
    "noir_reflet": (70, 80, 100),
    "trait": (52, 30, 14),
}

# image brute (générée par l'IA), image corrigée, position, coins du damier (haut-gauche, haut-droit, bas-droit, bas-gauche)
INCRUSTATIONS = [
    ("visuels/s01e01/brut/p08a-eleves.jpg", "visuels/s01e01/p08a-eleves.jpg", "s01e01",
     [(450, 122), (738, 99), (738, 511), (452, 515)]),
    ("visuels/s01e01/brut/p12-main-levee.jpg", "visuels/s01e01/p12-main-levee.jpg", "s01e01",
     [(480, 122), (751, 96), (751, 478), (487, 488)]),
]


def dessiner_mural(pos: Position, case: int = 60, ratio: float = 1.0, legende: str = "") -> Image.Image:
    """Damier de démonstration en bois : cadre, marge, 10x10 à cases carrées, sans numéros.

    `ratio` (largeur / hauteur) épouse la forme du panneau de l'image : si le panneau est plus
    haut que large, la place libre sous le damier accueille la légende.
    """
    cadre, marge = case // 3, case // 2
    cote = 10 * case + 2 * (cadre + marge)
    hauteur = max(cote, int(cote / ratio))
    img = Image.new("RGB", (cote, hauteur), MURAL["cadre"])
    d = ImageDraw.Draw(img)
    d.rectangle([cadre, cadre, cote - cadre, hauteur - cadre], fill=MURAL["marge"], outline=MURAL["trait"], width=3)
    origine = cadre + marge
    if legende and hauteur - cote > case:
        place = hauteur - cote
        lignes = legende.upper().split("\n")
        taille = min(int(place * 0.42), case)
        while taille > 10 and max(d.textlength(l, font=_police(taille)) for l in lignes) > 10 * case:
            taille -= 2
        police = _police(taille)
        for i, texte in enumerate(lignes):
            y = cote - marge // 2 + place * (i + 1) / (len(lignes) + 1)
            d.text((cote / 2, y), texte, fill=MURAL["trait"], font=police, anchor="mm")
    for ligne in range(10):
        for colonne in range(10):
            x, y = origine + colonne * case, origine + ligne * case
            couleur = MURAL["fonce"] if (ligne + colonne) % 2 else MURAL["clair"]
            d.rectangle([x, y, x + case, y + case], fill=couleur)
    d.rectangle([origine, origine, origine + 10 * case, origine + 10 * case], outline=MURAL["trait"], width=3)
    rayon = int(case * 0.36)
    for numero, piece in pos.pieces.items():
        ligne, colonne = vers_coord(numero)
        cx, cy = origine + colonne * case + case // 2, origine + ligne * case + case // 2
        blanc = piece.lower() == "w"
        corps = MURAL["blanc"] if blanc else MURAL["noir"]
        ombre = MURAL["blanc_ombre"] if blanc else MURAL["noir_reflet"]
        d.ellipse([cx - rayon, cy - rayon + 5, cx + rayon, cy + rayon + 5], fill=(40, 24, 12))
        d.ellipse([cx - rayon, cy - rayon, cx + rayon, cy + rayon], fill=corps, outline=MURAL["trait"], width=2)
        d.ellipse([cx - rayon * 0.6, cy - rayon * 0.6, cx + rayon * 0.6, cy + rayon * 0.6], outline=ombre, width=2)
    return img


def _police(taille: int):
    for chemin in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf",
                   "/Library/Fonts/Arial Bold.ttf"]:
        try:
            return ImageFont.truetype(chemin, taille)
        except OSError:
            continue
    return ImageFont.load_default()


def _coefficients(destination, source):
    """Coefficients PIL pour envoyer le quadrilatère `destination` sur le rectangle `source`."""
    matrice, vecteur = [], []
    for (x, y), (u, v) in zip(destination, source):
        matrice.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); vecteur.append(u)
        matrice.append([0, 0, 0, x, y, 1, -v * x, -v * y]); vecteur.append(v)
    return np.linalg.solve(np.array(matrice, float), np.array(vecteur, float)).tolist()


def incruster(source: str, sortie: str, nom_position: str, coins, garder_traits_blancs: bool = True) -> Path:
    fond = Image.open(RACINE / source).convert("RGB")
    (hg, hd, bd, bg) = coins
    largeur = (np.hypot(*np.subtract(hd, hg)) + np.hypot(*np.subtract(bd, bg))) / 2
    hauteur = (np.hypot(*np.subtract(bg, hg)) + np.hypot(*np.subtract(bd, hd))) / 2
    fiche = POSITIONS[nom_position]
    planche = dessiner_mural(Position.depuis_fen(fiche["fen"]), ratio=largeur / hauteur,
                             legende=fiche["titre"].replace(" jouent", "\njouent"))
    w, h = planche.size

    # On travaille en x3 pour des bords nets, puis on réduit.
    k = 3
    grand = (fond.width * k, fond.height * k)
    coins_k = [(x * k, y * k) for x, y in coins]
    coeffs_k = _coefficients(coins_k, [(0, 0), (w, 0), (w, h), (0, h)])
    calque = planche.transform(grand, Image.PERSPECTIVE, coeffs_k, Image.BICUBIC)
    masque = Image.new("L", grand, 0)
    ImageDraw.Draw(masque).polygon(coins_k, fill=255)
    calque = calque.resize(fond.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
    masque = masque.resize(fond.size, Image.LANCZOS)

    resultat = Image.composite(calque, fond, masque)

    if garder_traits_blancs:
        # Les lignes de vitesse blanches qui passaient devant le damier restent devant.
        tableau = np.asarray(fond).astype(int)
        blanc_pur = (tableau.min(axis=2) >= 246)
        traits = Image.fromarray((blanc_pur * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))
        traits = Image.composite(traits, Image.new("L", fond.size, 0), masque)
        resultat = Image.composite(fond, resultat, traits)

    # Grain léger pour fondre l'incrustation dans l'image.
    bruit = np.random.default_rng(0).normal(0, 4, (fond.height, fond.width, 1))
    tableau = np.clip(np.asarray(resultat).astype(float) + bruit * (np.asarray(masque)[..., None] / 255), 0, 255)
    resultat = Image.fromarray(tableau.astype(np.uint8))

    chemin = RACINE / sortie
    resultat.save(chemin, quality=90)
    return chemin


if __name__ == "__main__":
    for source, sortie, nom, coins in INCRUSTATIONS:
        print("→", incruster(source, sortie, nom, coins))
