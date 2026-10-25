"""Plan 4 de l'épisode 1 : Armand arrive avec un damier sous le bras.

L'IA avait dessiné un damier faux (pions rouges, pions sur les cases claires). On le retourne :
Armand porte le damier côté dos, et on ne voit que le panneau de bois. C'est aussi plus
vraisemblable, puisqu'on ne transporte pas un damier garni de pions.

Usage : python3 outils/plans/s01e01_p04.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RACINE = Path(__file__).resolve().parents[2]
BRUT = RACINE / "visuels/s01e01/brut/p04-porte.jpg"
SORTIE = RACINE / "visuels/s01e01/p04-porte.jpg"

# Bord du damier entier (le coin haut-droit est caché sous le bras).
DAMIER = [(267, 389), (391, 348), (425, 513), (302, 554)]
# Le coin du damier qui dépasse sous la manche, à droite.
COIN = [(407, 464), (427, 513), (396, 519), (392, 503), (400, 497), (405, 480)]
BOIS = np.array([150, 98, 52])
BOIS_FONCE = np.array([92, 56, 28])


def main() -> Path:
    fond = Image.open(BRUT).convert("RGB")
    tableau = np.asarray(fond).astype(float)
    h, w, _ = tableau.shape

    # Partie visible du damier : dans son contour, les pixels sombres (le damier est en contre-jour,
    # le gilet et la main d'Armand sont nettement plus clairs). On écarte les traits fins.
    import cv2

    contour = Image.new("L", (w, h), 0)
    ImageDraw.Draw(contour).polygon(DAMIER, fill=255)
    contour = np.asarray(contour.filter(ImageFilter.MaxFilter(7))) > 0
    luminosite = tableau.max(axis=2) / 255
    sombre = ((luminosite < 0.66) & contour).astype(np.uint8)
    sombre = cv2.morphologyEx(sombre, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    sombre = cv2.morphologyEx(sombre, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, etiquettes, stats, _ = cv2.connectedComponentsWithStats(sombre)
    principal = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    plein = (etiquettes == principal).astype(np.uint8)
    # Les cases claires sont des trous entourés de cases foncées : on les bouche.
    inonde = plein.copy()
    cv2.floodFill(inonde, None, (0, 0), 1)
    plein = plein | (1 - inonde)
    coin = Image.new("L", (w, h), 0)
    ImageDraw.Draw(coin).polygon(COIN, fill=1)
    plein = (plein | np.asarray(coin)) & contour
    masque = Image.fromarray((plein * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    m = np.asarray(masque).astype(float) / 255

    # La lumière d'origine (contre-jour de la porte) module le bois.
    lumiere = np.asarray(fond.convert("L").filter(ImageFilter.GaussianBlur(14))).astype(float)
    lumiere = (lumiere / max(lumiere[m > 0.5].mean(), 1)).clip(0.6, 1.5)[..., None]

    # Veinage : bandes douces dans le sens de la longueur du panneau.
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    axe = np.array([391 - 267, 348 - 389], float)
    axe /= np.linalg.norm(axe)
    travers = -(xs - 267) * axe[1] + (ys - 389) * axe[0]
    veines = (np.sin(travers * 0.35) * 0.6 + np.sin(travers * 0.9 + 1.7) * 0.25)[..., None]
    bois = (BOIS + veines * 6) * lumiere

    # Liseré plus sombre le long du bord (le cadre du panneau).
    cadre = Image.new("L", (w, h), 0)
    ImageDraw.Draw(cadre).line(DAMIER + [DAMIER[0]], fill=255, width=9)
    c = np.asarray(cadre.filter(ImageFilter.GaussianBlur(1))).astype(float)[..., None] / 255
    bois = bois * (1 - c) + BOIS_FONCE * lumiere * c

    # Quelques traits de veinage à l'encre, parallèles au grand côté du panneau.
    traits = Image.new("L", (w, h), 0)
    dt = ImageDraw.Draw(traits)
    normale = np.array([axe[1], -axe[0]])
    for decalage, longueur, phase in ((22, 0.7, 0.0), (58, 0.55, 1.3), (97, 0.65, 2.1), (131, 0.45, 0.7)):
        depart = np.array([272, 397], float) - normale * decalage * 0.95 + axe * 10
        points = [tuple(depart + axe * 125 * longueur * s + normale * 2.2 * np.sin(6 * s + phase))
                  for s in np.linspace(0, 1, 14)]
        dt.line(points, fill=70, width=1)
    trait = np.asarray(traits).astype(float)[..., None] / 255
    bois = bois * (1 - trait) + (BOIS_FONCE * 0.8 * lumiere) * trait

    resultat = tableau * (1 - m[..., None]) + bois * m[..., None]
    image = Image.fromarray(resultat.clip(0, 255).astype(np.uint8))

    # Trait d'encre sur les bords visibles du panneau, comme le reste du dessin.
    d = ImageDraw.Draw(image)
    d.line([(332, 373), (267, 389), (302, 554), (352, 539)], fill=(40, 22, 10), width=3)
    d.line([(407, 464), (427, 513), (396, 519)], fill=(40, 22, 10), width=3)
    image.save(SORTIE, quality=90)
    return SORTIE


if __name__ == "__main__":
    print("→", main())
