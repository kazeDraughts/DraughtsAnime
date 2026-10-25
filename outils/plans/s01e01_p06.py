"""Plan 6 de l'épisode 1 : la main d'Armand pose un pion. On garde la main (détourée par l'IA)
et on redessine dessous un damier au motif exact.

Le damier généré par l'IA n'était pas un vrai damier : la case foncée sous le pion touchait
d'autres cases foncées par les côtés. Ici le motif est calculé : la case du pion est foncée,
ses voisines de côté sont claires, et les cases foncées ne se touchent que par les coins.

Usage : python3 outils/plans/s01e01_p06.py
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RACINE = Path(__file__).resolve().parents[2]
BRUT = RACINE / "visuels/s01e01/brut/p06-mains-v2.jpg"
DETOURAGE = RACINE / "visuels/s01e01/brut/p06-mains-v2-detoure.png"
SORTIE = RACINE / "visuels/s01e01/p06-mains.jpg"

# Recadrage du plan (dans l'image brute 752x1344), puis taille finale.
RECADRAGE = (110, 370, 110 + 553, 1344)
TAILLE = (752, 1337)

# Le damier, dans l'image finale : bord gauche (cadre en bois), taille des cases, pente des rangées.
BORD_GAUCHE = 333
LARGEUR_CASE, HAUTEUR_CASE = 200, 230
PENTE = -0.15


def recadrer(image: Image.Image) -> Image.Image:
    return image.crop(RECADRAGE).resize(TAILLE, Image.LANCZOS)


def couleurs_du_damier(image: np.ndarray, masque_main: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Les deux couleurs de cases de l'image d'origine (k-moyennes à 2 groupes)."""
    zone = image[:, BORD_GAUCHE + 15:][masque_main[:, BORD_GAUCHE + 15:] < 10].reshape(-1, 3).astype(float)
    zone = zone[::7]
    centres = np.array([np.percentile(zone, 20, axis=0), np.percentile(zone, 80, axis=0)])
    for _ in range(12):
        groupe = np.argmin(((zone[:, None, :] - centres[None]) ** 2).sum(-1), axis=1)
        centres = np.array([np.median(zone[groupe == k], axis=0) for k in range(2)])
    fonce, clair = sorted(centres, key=lambda c: c.sum())
    return fonce, clair


def centre_du_pion(detourage: np.ndarray) -> tuple[float, float]:
    """Centre de la plus grande tache presque blanche et opaque du détourage : le pion
    (les traits d'impact, fins et dispersés, sont écartés)."""
    import cv2

    rgb, alpha = detourage[..., :3].astype(int), detourage[..., 3]
    blanc = ((rgb.min(axis=2) > 190) & (alpha > 200)).astype(np.uint8)
    blanc = cv2.morphologyEx(blanc, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    _, _, stats, _ = cv2.connectedComponentsWithStats(blanc)
    plus_grande = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    x, y, w, h = (stats[plus_grande][k] for k in (cv2.CC_STAT_LEFT, cv2.CC_STAT_TOP,
                                                   cv2.CC_STAT_WIDTH, cv2.CC_STAT_HEIGHT))
    # Le pouce cache le haut du pion : on part de son bord bas et de sa largeur (son diamètre).
    return x + w / 2, y + h - w / 2


def dessiner_damier(fond: np.ndarray, centre: tuple[float, float], fonce, clair) -> np.ndarray:
    hauteur, largeur, _ = fond.shape
    ys, xs = np.mgrid[0:hauteur, 0:largeur].astype(float)
    # La grille est calée pour que le pion soit au centre de sa case, et cette case est foncée.
    cx, cy = centre
    colonne = np.floor((xs - cx) / LARGEUR_CASE + 0.5)
    rangee = np.floor((ys - cy - PENTE * (xs - cx)) / HAUTEUR_CASE + 0.5)
    est_fonce = ((colonne + rangee) % 2) == 0

    rng = np.random.default_rng(6)
    veinage = rng.normal(0, 1, (1, largeur)).repeat(hauteur, axis=0)
    veinage = np.asarray(Image.fromarray(((veinage + 3) * 40).clip(0, 255).astype(np.uint8))
                         .filter(ImageFilter.GaussianBlur(1.5))).astype(float) / 40 - 3
    teinte = np.where(est_fonce[..., None], fonce, clair) + veinage[..., None] * 2.5
    damier = fond.astype(float).copy()
    zone = xs >= BORD_GAUCHE
    damier[zone] = teinte[zone]
    return damier


def traits_d_impact(image: Image.Image, centre: tuple[float, float]) -> None:
    """Traits blancs effilés autour du pion, comme dans l'image d'origine."""
    d = ImageDraw.Draw(image)
    cx, cy = centre
    for angle in (-75, -40, -10, 15, 40, 70, 115, 150):
        a = math.radians(angle)
        r0, r1 = 105, 105 + (95 if angle % 2 else 130)
        pointe = (cx + r1 * math.cos(a), cy + r1 * math.sin(a))
        base = (cx + r0 * math.cos(a), cy + r0 * math.sin(a))
        nx, ny = -math.sin(a) * 7, math.cos(a) * 7
        d.polygon([(base[0] + nx, base[1] + ny), pointe, (base[0] - nx, base[1] - ny)], fill=(250, 248, 240),
                  outline=(30, 20, 15))


def main() -> Path:
    fond = np.asarray(recadrer(Image.open(BRUT).convert("RGB")))
    detourage_img = recadrer(Image.open(DETOURAGE).convert("RGBA"))
    detourage = np.asarray(detourage_img)
    masque = detourage[..., 3]

    fonce, clair = couleurs_du_damier(fond, masque)
    centre = centre_du_pion(detourage)
    damier = dessiner_damier(fond, centre, fonce, clair)

    # Ombre portée de la main sur le damier.
    ombre = Image.fromarray(masque).transform(TAILLE, Image.AFFINE, (1, 0, -28, 0, 1, -38))
    ombre = np.asarray(ombre.filter(ImageFilter.GaussianBlur(18))).astype(float) / 255
    zone = np.zeros(masque.shape, bool)
    zone[:, BORD_GAUCHE:] = True
    damier[zone] *= (1 - 0.45 * ombre[zone])[..., None]

    image = Image.fromarray(damier.clip(0, 255).astype(np.uint8))
    traits_d_impact(image, centre)
    image = image.convert("RGBA")
    image.alpha_composite(detourage_img)
    image = image.convert("RGB")

    bruit = np.random.default_rng(1).normal(0, 3, (TAILLE[1], TAILLE[0], 1))
    image = Image.fromarray(np.clip(np.asarray(image).astype(float) + bruit, 0, 255).astype(np.uint8))
    image.save(SORTIE, quality=90)
    print(f"case foncée sous le pion centré en ({centre[0]:.0f}, {centre[1]:.0f}) ; "
          f"couleurs foncé {fonce.astype(int)}, clair {clair.astype(int)}")
    return SORTIE


if __name__ == "__main__":
    print("→", main())
