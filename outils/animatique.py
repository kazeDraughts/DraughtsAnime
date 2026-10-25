"""Monte une animatique verticale (1080x1920) à partir d'une liste de plans décrite en JSON.

Chaque plan : une image fixe (zoom lent ou image figée virée sépia-rouge) ou un clip animé
(clé « video »), une réplique
facultative, un sous-titre, et des bruitages (tic-tac, accord du « À suivre »).

Usage : python3 outils/animatique.py episodes/s01e01-test-voix.json
Les chemins du JSON sont relatifs à la racine du dépôt. Les voix vont dans audio/
et les vidéos sortent dans montages/ : ces deux dossiers ne sont pas versionnés.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import ImageFont

RACINE = Path(__file__).resolve().parent.parent
LARGEUR, HAUTEUR, IPS = 1080, 1920, 25
POLICE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SEPIA_ROUGE = "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,colorbalance=rs=.35:rm=.15"


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def duree(fichier: Path) -> float:
    sortie = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                             str(fichier)], capture_output=True, text=True, check=True).stdout
    return float(sortie)


def _texte(dossier: Path, nom: str, contenu: str) -> str:
    chemin = dossier / nom
    chemin.write_text(contenu, encoding="utf-8")
    return str(chemin).replace(":", r"\:")


def _taille_ajustee(texte: str, taille: int, marge: int = 70) -> int:
    """Réduit la taille de police jusqu'à ce que la ligne la plus longue tienne dans l'image."""
    while taille > 24:
        police = ImageFont.truetype(POLICE, taille)
        if max(police.getlength(ligne) for ligne in texte.split("\n")) <= LARGEUR - 2 * marge:
            break
        taille -= 2
    return taille


def plan(p: dict, n: int, tmp: Path) -> Path:
    video = RACINE / p["video"] if p.get("video") else None
    image = RACINE / p["image"] if not video else None
    avant, apres = p.get("avant", 0.3), p.get("apres", 0.4)
    voix = RACINE / p["voix"] if p.get("voix") else None
    total = avant + (duree(voix) if voix else 0) + apres if voix else p["duree"]
    images = int(total * IPS)

    # Image : remplir le 9:16 (recadrage centré), puis zoom lent ou image figée.
    filtres = [f"scale={LARGEUR * 2}:{HAUTEUR * 2}:force_original_aspect_ratio=increase",
               f"crop={LARGEUR * 2}:{HAUTEUR * 2}"]
    if p.get("fond"):
        # Un diagramme sur fond uni : assez petit pour qu'aucun zoom ne rogne ses bords.
        filtres = [f"scale={int(LARGEUR * 2 * 0.84)}:-1",
                   f"pad={LARGEUR * 2}:{HAUTEUR * 2}:(ow-iw)/2:(oh-ih)/2-200:color={p['fond']}"]
    if video:
        # Un clip animé (le damier mental) : on garde son mouvement et on fige sa dernière image.
        filtres = [f"scale={LARGEUR}:{HAUTEUR}:force_original_aspect_ratio=increase",
                   f"crop={LARGEUR}:{HAUTEUR}", f"tpad=stop_mode=clone:stop_duration={total}", f"fps={IPS}"]
    elif p.get("effet") == "fige":
        filtres += [f"scale={LARGEUR}:{HAUTEUR}", SEPIA_ROUGE, "noise=alls=12:allf=t"]
    else:
        vitesse = p.get("zoom", 0.0007)
        plafond = 1.04 if p.get("fond") else 1.15
        filtres += [f"zoompan=z='min(zoom+{vitesse},{plafond})':d={images}:x='iw/2-(iw/zoom/2)'"
                    f":y='ih/2-(ih/zoom/2)':s={LARGEUR}x{HAUTEUR}:fps={IPS}"]
    hauteur_texte = p.get("hauteur_texte", 0.80)  # position verticale des sous-titres (fraction)
    if p.get("sous_titre"):
        fichier = _texte(tmp, f"st{n}.txt", p["sous_titre"])
        corps = _taille_ajustee(p["sous_titre"], 56)
        filtres.append(f"drawtext=fontfile={POLICE}:textfile='{fichier}':fontcolor=white:fontsize={corps}"
                       f":borderw=5:bordercolor=black:x=(w-tw)/2:y=h*{hauteur_texte}:line_spacing=12:text_align=C")
    if p.get("personnage"):
        fichier = _texte(tmp, f"pers{n}.txt", p["personnage"])
        corps = _taille_ajustee(p["personnage"], 40)
        filtres.append(f"drawtext=fontfile={POLICE}:textfile='{fichier}':fontcolor=0xFFD23F:fontsize={corps}"
                       f":borderw=4:bordercolor=black:x=(w-tw)/2:y=h*{hauteur_texte}-64")
    if p.get("titre"):
        fichier = _texte(tmp, f"titre{n}.txt", p["titre"])
        filtres.append(f"drawtext=fontfile={POLICE}:textfile='{fichier}':fontcolor=0xE8452C:fontsize=120"
                       f":borderw=8:bordercolor=0x2A1206:x=(w-tw)/2:y=h*0.84")
    filtres.append("format=yuv420p")

    # Son : la voix décalée, un tic-tac discret, l'accord final.
    sons, melange = [], []
    if voix:
        sons += ["-i", str(voix)]
        melange.append(f"[{len(melange) + 1}:a]adelay={int(avant * 1000)}:all=1,apad=whole_dur={total}[s{len(melange)}]")
    if p.get("tictac"):
        volume = p["tictac"]
        sons += ["-f", "lavfi", "-i", f"aevalsrc='{volume}*sin(2*PI*(if(lt(mod(t,1),0.5),2100,1600))*t)"
                 f"*exp(-90*mod(t,0.5))':s=48000:d={total}"]
        melange.append(f"[{len(melange) + 1}:a]anull[s{len(melange)}]")
    if p.get("accord"):
        sons += ["-f", "lavfi", "-i", "aevalsrc='0.22*(sin(2*PI*110*t)+sin(2*PI*130.8*t)+sin(2*PI*164.8*t)"
                 f"+sin(2*PI*220*t))*exp(-0.9*t)':s=48000:d={total}"]
        melange.append(f"[{len(melange) + 1}:a]anull[s{len(melange)}]")
    if not melange:
        sons += ["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono:d={total}"]
        melange.append("[1:a]anull[s0]")
    entrees = "".join(f"[s{i}]" for i in range(len(melange)))
    graphe = ";".join(melange) + f";{entrees}amix=inputs={len(melange)}:normalize=0,aresample=48000[a]"

    sortie = tmp / f"plan{n:02d}.mp4"
    source = ["-i", str(video)] if video else ["-loop", "1", "-i", str(image)]
    ffmpeg(*source, *sons, "-filter_complex", graphe, "-map", "0:v", "-map", "[a]",
           "-vf", ",".join(filtres), "-t", f"{total:.3f}", "-r", str(IPS), "-c:v", "libx264", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k", "-ac", "1", str(sortie))
    return sortie


def monter(spec: Path) -> Path:
    description = json.loads(spec.read_text(encoding="utf-8"))
    sortie = RACINE / "montages" / f"{description['nom']}.mp4"
    sortie.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as dossier:
        tmp = Path(dossier)
        plans = [plan(p, n, tmp) for n, p in enumerate(description["plans"])]
        liste = tmp / "liste.txt"
        liste.write_text("".join(f"file '{p}'\n" for p in plans))
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(liste), "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5",
               "-c:a", "aac", "-b:a", "192k", str(sortie))
    return sortie


if __name__ == "__main__":
    print("→", monter(Path(sys.argv[1])))
