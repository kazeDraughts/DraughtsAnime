"""Le damier mental : un damier infini en perspective sous un ciel étoilé, dessiné à partir
d'une position exacte.

Le vrai damier 10x10 est au centre, entouré d'un liseré lumineux ; le motif continue jusqu'à
l'horizon. Les pions ne sont posés que sur les cases foncées de la vraie position. On peut
montrer un coup : traînée lumineuse, pion qui glisse, pion qui saute pour prendre.

Usage : python3 outils/damier_mental.py   (rend les plans listés dans PLANS)
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from damier import Position, vers_coord
from positions import POSITIONS

RACINE = Path(__file__).resolve().parent.parent

COULEURS = {
    "fonce": np.array([32, 48, 98]),
    "clair": np.array([226, 222, 206]),
    "horizon": np.array([96, 112, 170]),
    "ciel_haut": np.array([8, 12, 38]),
    "ciel_bas": np.array([44, 58, 120]),
    "liseré": (150, 200, 255),
    "blanc_dessus": (246, 243, 234),
    "blanc_cote": (190, 184, 168),
    "noir_dessus": (30, 34, 46),
    "noir_cote": (14, 16, 24),
    "reflet_noir": (120, 160, 230),
    "trait": (10, 10, 20),
}


@dataclass
class Camera:
    """Caméra placée côté blancs (au sud), qui regarde vers le nord et vers le bas.

    Coordonnées du monde : x = colonne (0 à 10, de gauche à droite pour les blancs),
    y = rangée (0 = bord des noirs, 10 = bord des blancs), z = hauteur. Une case = 1.
    """

    x: float = 5.0
    y: float = 15.0
    z: float = 3.2
    tangage: float = 14.0  # degrés vers le bas
    focale: float = 1.15  # en largeurs d'image
    largeur: int = 1080
    hauteur: int = 1920
    centre_y: float = 0.52  # position verticale du point principal (fraction de la hauteur)

    def axes(self):
        t = math.radians(self.tangage)
        avant = np.array([0.0, -math.cos(t), -math.sin(t)])
        droite = np.array([1.0, 0.0, 0.0])
        haut = np.array([0.0, -math.sin(t), math.cos(t)])
        return avant, droite, haut

    def projeter(self, points: np.ndarray) -> np.ndarray:
        """Points du monde (N, 3) -> pixels (N, 2)."""
        avant, droite, haut = self.axes()
        rel = points - np.array([self.x, self.y, self.z])
        profondeur = rel @ avant
        f = self.focale * self.largeur
        sx = self.largeur / 2 + f * (rel @ droite) / profondeur
        sy = self.hauteur * self.centre_y - f * (rel @ haut) / profondeur
        return np.stack([sx, sy], axis=1)

    def profondeur(self, point) -> float:
        avant, _, _ = self.axes()
        return float((np.asarray(point) - np.array([self.x, self.y, self.z])) @ avant)


@dataclass
class Coup:
    """Un coup à mettre en scène : le pion part de `depart` et suit `chemin` (cases)."""

    depart: int
    chemin: list[int]
    avancement: float = 1.0  # 0 = au départ, 1 = arrivé
    saut: float = 0.0  # hauteur du pion pendant une prise
    lueur: tuple = (255, 255, 255)
    trainee: bool = True


@dataclass
class Plan:
    nom: str
    position: str
    camera: Camera = field(default_factory=Camera)
    coups: list[Coup] = field(default_factory=list)
    personnage: tuple | None = None  # (image détourée, x, y, hauteur en cases, recadrage)
    ciel: tuple | None = None  # (image peinte, fraction de sa hauteur occupée par le ciel)
    estompes: dict = field(default_factory=dict)  # case de départ -> 0 (visible) à 1 (disparu)
    eclair: tuple | None = None  # (case, intensité 0 à 1) : éclair au moment d'une prise


def centre_case(case: int) -> np.ndarray:
    ligne, colonne = vers_coord(case)
    return np.array([colonne + 0.5, ligne + 0.5])


def _ciel_et_sol(cam: Camera, sur: int = 2) -> Image.Image:
    """Ciel étoilé et damier infini, calculés pixel par pixel (sur-échantillonnés)."""
    L, H = cam.largeur * sur, cam.hauteur * sur
    avant, droite, haut = cam.axes()
    f = cam.focale * L
    sx, sy = np.meshgrid(np.arange(L) + 0.5, np.arange(H) + 0.5)
    dx = (sx - L / 2) / f
    dy = (H * cam.centre_y - sy) / f
    direction = avant[None, None] + dx[..., None] * droite + dy[..., None] * haut
    dz = direction[..., 2]

    # Ciel : dégradé, puis étoiles.
    hauteur_ciel = np.clip(dz * 3 + 0.15, 0, 1)[..., None]
    image = COULEURS["ciel_bas"] * (1 - hauteur_ciel) + COULEURS["ciel_haut"] * hauteur_ciel

    sol = dz < -1e-4
    t = np.where(sol, -cam.z / np.where(sol, dz, -1), 0)
    gx = cam.x + t * direction[..., 0]
    gy = cam.y + t * direction[..., 1]
    fonce = ((np.floor(gx) + np.floor(gy)) % 2) == 1
    couleur_sol = np.where(fonce[..., None], COULEURS["fonce"], COULEURS["clair"])
    distance = np.hypot(gx - cam.x, gy - cam.y)
    brume = (1 - np.exp(-np.clip(distance - 6, 0, None) / 22))[..., None]
    couleur_sol = couleur_sol * (1 - brume) + COULEURS["horizon"] * brume
    # Variations douces, comme une gouache : un bruit très flou par case.
    rng = np.random.default_rng(11)
    variation = rng.normal(0, 1, (64, 64))
    vx = (np.floor(gx).astype(int) % 64 + 64) % 64
    vy = (np.floor(gy).astype(int) % 64 + 64) % 64
    couleur_sol = couleur_sol + (variation[vy, vx] * 6)[..., None]
    lueur_horizon = np.exp(-np.clip(-dz, 0, None) * 40)[..., None] * 60
    couleur_sol = couleur_sol + lueur_horizon * np.array([0.7, 0.8, 1.0])
    image = np.where(sol[..., None], couleur_sol, image)

    img = Image.fromarray(image.clip(0, 255).astype(np.uint8)).resize((cam.largeur, cam.hauteur), Image.LANCZOS)

    rng = np.random.default_rng(3)
    d = ImageDraw.Draw(img)
    horizon = int(cam.hauteur * cam.centre_y - cam.focale * cam.largeur * math.tan(math.radians(cam.tangage)))
    for _ in range(420):
        x, y = rng.uniform(0, cam.largeur), rng.uniform(0, max(horizon - 10, 1))
        r = rng.choice([0.6, 0.9, 1.4, 2.2], p=[0.55, 0.3, 0.12, 0.03])
        lum = int(rng.uniform(150, 255))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(lum, lum, min(255, lum + 20)))
    return img


def _liseré(img: Image.Image, cam: Camera) -> Image.Image:
    """Lueur autour du vrai damier 10x10."""
    coins = np.array([[0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 10, 0], [0, 0, 0]], float)
    pts = [tuple(p) for p in cam.projeter(coins)]
    calque = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(calque).line(pts, fill=COULEURS["liseré"] + (255,), width=10)
    lueur = calque.filter(ImageFilter.GaussianBlur(12))
    img = img.convert("RGBA")
    img.alpha_composite(lueur)
    trait = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(trait).line(pts, fill=(235, 245, 255, 230), width=3)
    img.alpha_composite(trait)
    return img


def _cylindre(d: ImageDraw.ImageDraw, cam: Camera, centre, z0: float, blanc: bool,
              rayon=0.38, epaisseur=0.13, n=60):
    angles = np.linspace(0, 2 * math.pi, n, endpoint=False)
    cercle = np.stack([centre[0] + rayon * np.cos(angles), centre[1] + rayon * np.sin(angles)], axis=1)
    bas = cam.projeter(np.column_stack([cercle, np.full(n, z0)]))
    haut = cam.projeter(np.column_stack([cercle, np.full(n, z0 + epaisseur)]))
    cote = COULEURS["blanc_cote" if blanc else "noir_cote"]
    dessus = COULEURS["blanc_dessus" if blanc else "noir_dessus"]
    for i in range(n):
        j = (i + 1) % n
        d.polygon([tuple(bas[i]), tuple(bas[j]), tuple(haut[j]), tuple(haut[i])], fill=cote)
    d.polygon([tuple(p) for p in bas], outline=COULEURS["trait"])
    d.polygon([tuple(p) for p in haut], fill=dessus, outline=COULEURS["trait"])
    anneau = cam.projeter(np.column_stack([centre[0] + rayon * 0.62 * np.cos(angles),
                                           centre[1] + rayon * 0.62 * np.sin(angles),
                                           np.full(n, z0 + epaisseur)]))
    d.polygon([tuple(p) for p in anneau], outline=cote if blanc else COULEURS["reflet_noir"])
    if not blanc:
        # Liseré bleuté pour détacher les pions noirs des cases foncées.
        d.line([tuple(p) for p in haut] + [tuple(haut[0])], fill=COULEURS["reflet_noir"], width=2)


def _position_du_coup(coup: Coup) -> tuple[np.ndarray, list[np.ndarray]]:
    etapes = [centre_case(coup.depart)] + [centre_case(c) for c in coup.chemin]
    longueurs = [np.linalg.norm(b - a) for a, b in zip(etapes, etapes[1:])]
    restant = coup.avancement * sum(longueurs)
    parcouru = [etapes[0]]
    for a, b, l in zip(etapes, etapes[1:], longueurs):
        if restant >= l:
            parcouru.append(b)
            restant -= l
        else:
            parcouru.append(a + (b - a) * (restant / l))
            break
    return parcouru[-1], parcouru


def _ciel_peint(img: Image.Image, cam: Camera, chemin: str, part: float) -> Image.Image:
    """Remplace le ciel calculé par le haut d'une image peinte, fondu vers l'horizon."""
    horizon = int(cam.hauteur * cam.centre_y - cam.focale * cam.largeur * math.tan(math.radians(cam.tangage)))
    source = Image.open(RACINE / chemin).convert("RGB")
    source = source.crop((0, 0, source.width, int(source.height * part)))
    ciel = source.resize((cam.largeur, horizon), Image.LANCZOS)
    masque = np.ones((horizon, cam.largeur))
    fondu = min(120, horizon // 3)
    masque[-fondu:] = np.linspace(1, 0, fondu)[:, None]
    calque = img.copy()
    calque.paste(ciel, (0, 0))
    m = Image.new("L", img.size, 0)
    m.paste(Image.fromarray((masque * 255).astype(np.uint8)), (0, 0))
    return Image.composite(calque, img, m)


_FONDS: dict = {}


def _fond(plan: Plan) -> Image.Image:
    cle = (repr(plan.camera), plan.ciel)
    if cle not in _FONDS:
        fond = _ciel_et_sol(plan.camera)
        if plan.ciel:
            fond = _ciel_peint(fond, plan.camera, *plan.ciel)
        _FONDS[cle] = _liseré(fond, plan.camera)
    return _FONDS[cle].copy()


def rendre(plan: Plan) -> Image.Image:
    cam = plan.camera
    pos = Position.depuis_fen(POSITIONS[plan.position]["fen"])
    img = _fond(plan)

    en_mouvement = {c.depart: c for c in plan.coups}
    pieces = []  # (profondeur, centre xy, z, blanc, coup)
    for case, piece in pos.pieces.items():
        if plan.estompes.get(case, 0) >= 1:
            continue
        coup = en_mouvement.get(case)
        if coup:
            xy, parcours = _position_du_coup(coup)
            z = coup.saut * math.sin(math.pi * min(coup.avancement, 1.0))
        else:
            xy, parcours, z = centre_case(case), None, 0.0
        pieces.append((cam.profondeur([xy[0], xy[1], 0]), xy, z, piece.lower() == "w", coup, parcours, case))

    # Traînées lumineuses au sol.
    calque = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(calque)
    for _, _, _, _, coup, parcours, _ in pieces:
        if coup and coup.trainee and parcours and len(parcours) > 1:
            pts = [tuple(p) for p in cam.projeter(np.column_stack([np.array(parcours), np.full(len(parcours), 0.02)]))]
            dc.line(pts, fill=coup.lueur + (255,), width=26, joint="curve")
    img.alpha_composite(calque.filter(ImageFilter.GaussianBlur(14)))
    calque2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dc2 = ImageDraw.Draw(calque2)
    for _, _, _, _, coup, parcours, _ in pieces:
        if coup and coup.trainee and parcours and len(parcours) > 1:
            pts = [tuple(p) for p in cam.projeter(np.column_stack([np.array(parcours), np.full(len(parcours), 0.02)]))]
            dc2.line(pts, fill=(255, 255, 255, 235), width=7, joint="curve")
    img.alpha_composite(calque2)

    # Pion qui saute : ombre au sol et arc lumineux depuis sa case de départ.
    for _, xy, z, _, coup, _, _ in pieces:
        if coup and coup.saut > 0 and 0 < coup.avancement < 1:
            ombre = Image.new("RGBA", img.size, (0, 0, 0, 0))
            angles = np.linspace(0, 2 * math.pi, 40)
            cercle = np.column_stack([xy[0] + 0.36 * np.cos(angles), xy[1] + 0.36 * np.sin(angles), np.zeros(40)])
            ImageDraw.Draw(ombre).polygon([tuple(p) for p in cam.projeter(cercle)], fill=(0, 0, 15, 150))
            img.alpha_composite(ombre.filter(ImageFilter.GaussianBlur(6)))
            depart = centre_case(coup.depart)
            arc = []
            for k in np.linspace(0, coup.avancement, 24):
                q = depart + (xy - depart) * (k / max(coup.avancement, 1e-6))
                arc.append([q[0], q[1], coup.saut * math.sin(math.pi * k) + 0.07])
            pts = [tuple(p) for p in cam.projeter(np.array(arc))]
            trace = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ImageDraw.Draw(trace).line(pts, fill=coup.lueur + (255,), width=18, joint="curve")
            img.alpha_composite(trace.filter(ImageFilter.GaussianBlur(9)))
            trace2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ImageDraw.Draw(trace2).line(pts, fill=(255, 235, 230, 230), width=5, joint="curve")
            img.alpha_composite(trace2)

    # Pions, du plus loin au plus proche ; lueur autour des pions en mouvement.
    for prof, xy, z, blanc, coup, _, case in sorted(pieces, key=lambda p: -p[0]):
        if coup:
            halo = Image.new("RGBA", img.size, (0, 0, 0, 0))
            _cylindre(ImageDraw.Draw(halo), cam, xy, z, blanc, rayon=0.5, epaisseur=0.2)
            couleur = Image.new("RGBA", img.size, coup.lueur + (0,))
            couleur.putalpha(halo.getchannel("A"))
            img.alpha_composite(couleur.filter(ImageFilter.GaussianBlur(16)))
        estompe = plan.estompes.get(case, 0)
        if estompe > 0:
            calque = Image.new("RGBA", img.size, (0, 0, 0, 0))
            _cylindre(ImageDraw.Draw(calque), cam, xy, z, blanc)
            alpha = calque.getchannel("A").point(lambda a: int(a * (1 - estompe)))
            calque.putalpha(alpha)
            img.alpha_composite(calque)
        else:
            _cylindre(ImageDraw.Draw(img), cam, xy, z, blanc)

    if plan.eclair and plan.eclair[1] > 0:
        case, force = plan.eclair
        cx, cy = cam.projeter(np.array([[*centre_case(case), 0.1]]))[0]
        eclat = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(eclat)
        r = 60 + 140 * force
        d.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], fill=(255, 255, 255, int(220 * force)))
        for k in range(12):
            a = k * math.pi / 6
            d.line([(cx, cy), (cx + math.cos(a) * r * 1.8, cy + math.sin(a) * r * 1.1)],
                   fill=(255, 250, 230, int(255 * force)), width=6)
        img.alpha_composite(eclat.filter(ImageFilter.GaussianBlur(5)))

    if plan.personnage:
        chemin, px, py, taille, boite = plan.personnage
        perso = Image.open(RACINE / chemin).convert("RGBA")
        if boite:
            perso = perso.crop(boite)
        perso = perso.crop(perso.getbbox())
        pieds = cam.projeter(np.array([[px, py, 0.0], [px, py, taille]]))
        h = int(abs(pieds[0][1] - pieds[1][1]))
        w = int(perso.width * h / perso.height)
        perso = perso.resize((w, h), Image.LANCZOS)
        ombre = Image.new("RGBA", img.size, (0, 0, 0, 0))
        bx, by = pieds[0]
        ImageDraw.Draw(ombre).ellipse([bx - w * 0.45, by - h * 0.03, bx + w * 0.45, by + h * 0.03], fill=(0, 0, 20, 140))
        img.alpha_composite(ombre.filter(ImageFilter.GaussianBlur(8)))
        img.alpha_composite(perso, (int(bx - w / 2), int(by - h)))

    # Grain de pellicule.
    tableau = np.asarray(img.convert("RGB")).astype(float)
    tableau += np.random.default_rng(5).normal(0, 4, tableau.shape[:2])[..., None]
    return Image.fromarray(tableau.clip(0, 255).astype(np.uint8))


CAMERA_P10 = Camera(x=4.6, y=9.4, z=2.4, tangage=17.0, focale=0.9, centre_y=0.50)
CIEL = ("visuels/decors/ciel-etoile.jpg", 1.0)
LEO = ("visuels/personnages/leo-damier-mental.png", 7.2, 3.2, 2.6, None)


def _lisse(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def s01e01_p10(t: float) -> Plan:
    """Épisode 1, plan 10 : le pion blanc glisse de 33 à 28, le pion noir de 32 saute et le prend."""
    glisse = _lisse((t - 0.4) / 1.0)
    saut = _lisse((t - 1.7) / 1.0)
    passage = 1.7 + 0.5  # le pion noir passe au-dessus de 28
    estompe = _lisse((t - passage) / 0.35)
    eclair = max(0.0, 1 - abs(t - passage) / 0.25)
    return Plan(
        nom="", position="s01e01", camera=CAMERA_P10, ciel=CIEL, personnage=LEO,
        coups=[Coup(depart=33, chemin=[28], avancement=glisse, lueur=(170, 220, 255)),
               Coup(depart=32, chemin=[23], avancement=saut, saut=1.1 if saut > 0 else 0,
                    lueur=(255, 70, 60), trainee=False)],
        estompes={33: estompe}, eclair=(28, eclair),
    )


# Carton-titre : le ciel peint de l'affiche (logo, visage d'Armand) au-dessus d'un vrai damier
# en position de départ, et Léo devant les blancs.
TITRE = Plan(
    nom="", position="depart",
    camera=Camera(x=5.0, y=14.5, z=3.6, tangage=15.0, focale=1.0, centre_y=0.62),
    ciel=("visuels/concepts/0-affiche.jpg", 0.47),
    personnage=("visuels/personnages/leo-heroique.png", 5.0, 11.0, 2.7, None),
)

# Images fixes : (fichier, plan)
PLANS = [
    ("visuels/s01e01/p10-damier-mental.jpg", s01e01_p10(2.05)),
    ("visuels/s01e01/p02-titre.jpg", TITRE),
]

# Animations : (fichier vidéo, durée en secondes, fonction t -> plan)
ANIMATIONS = [
    ("visuels/s01e01/p10-damier-mental.mp4", 4.0, s01e01_p10),
]


def animer(sortie: str, duree: float, scene, ips: int = 25) -> Path:
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as dossier:
        for n in range(int(duree * ips)):
            rendre(scene(n / ips)).save(f"{dossier}/{n:04d}.png")
        chemin = RACINE / sortie
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(ips), "-i", f"{dossier}/%04d.png",
                        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", str(chemin)], check=True)
    return chemin


if __name__ == "__main__":
    for fichier, plan in PLANS:
        rendre(plan).save(RACINE / fichier, quality=92)
        print("→", fichier)
    if "--sans-animation" not in sys.argv:
        for fichier, duree, scene in ANIMATIONS:
            print("→", animer(fichier, duree, scene))
