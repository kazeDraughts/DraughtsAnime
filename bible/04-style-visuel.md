# 04 · Style visuel

## L'intention

On veut qu'on croie à un vrai anime TV japonais des années 80 doublé en français, retrouvé sur une
vieille cassette. Mais les personnages, le damier et les lieux sont 100 % originaux. **On ne copie
aucune série existante :** on reprend le style d'une époque.

## Les marqueurs du style

- **Celluloïd :** contours encrés épais, ombres plates en deux tons (pas de dégradés), reflets
  blancs nets dans les cheveux et les yeux.
- **Décors peints à la gouache**, plus détaillés et plus doux que les personnages.
- **Palette :** bleu ciel saturé, coucher de soleil doré, bleu nuit profond pour le damier mental.
  Le rouge est réservé à l'écharpe de Léo et au drapeau de la pendule.
- **Texture :** léger grain de pellicule, image un peu douce, très légère bavure de couleur façon VHS.
  À doser : on doit rester lisible sur un téléphone.
- **Animation limitée** (et c'est une force) : images fixes, panoramiques sur un décor, zooms, lignes
  de vitesse, plans répétés. On anime peu, mais au bon moment.

## Les plans signatures

| Plan | Quand | Description |
|---|---|---|
| **L'œil-damier** | Quand un joueur voit une combinaison | Gros plan sur un œil, le damier s'y reflète et une étincelle brille |
| **Le plongeon** | Quand on entre dans le damier mental | Zoom dans la pupille, on traverse, damier infini sous les étoiles |
| **CLAC !** | Un coup décisif | La main frappe le pion, lignes d'impact, onomatopée à l'écran |
| **La goutte** | Le stress | Une goutte de sueur glisse sur la tempe, en très gros plan |
| **Le drapeau** | Le temps presse | Le drapeau rouge de la pendule se soulève, tic-tac amplifié |
| **Le visage dans le ciel** | Un souvenir du mentor | Le visage d'Armand apparaît en transparence dans le ciel |
| **Le freeze final** | Le cliffhanger | Image figée, virée en sépia-rouge, texte « À suivre… » |

## Les règles du damier à l'image

- **10×10 cases.** Jamais 8×8, jamais d'échiquier.
- **Pions plats et ronds**, de type jeton. Jamais de pièces d'échecs.
- Les pions sont **uniquement sur les cases foncées**.
- La case du coin en bas à gauche de chaque joueur est **foncée**.
- **Les positions qui comptent ne sont jamais générées par l'IA.** Elles sont dessinées par programme
  à partir d'une position vérifiée, puis intégrées à l'image. Les plans d'ambiance (damier flou, de
  loin) peuvent être générés.

## Le prompt de base (images)

À coller au début de chaque prompt, puis on décrit la scène :

```
Authentic 1980s Japanese TV anime cel animation still. Hand-inked bold outlines, flat two-tone cel
shading with hard shadows, hand-painted gouache background, saturated retro palette, soft film
grain, slight analog TV softness. Original characters, French setting.
```

Pour tout plan avec un damier, ajouter :

```
The board is an international draughts board: 10 by 10 squares, flat round disc pieces like
checkers (no chess pieces), pieces only on the dark squares.
```

## Les fiches de référence des personnages

Pour que les visages ne changent pas d'un plan à l'autre :

1. On génère et on choisit **une image de référence par personnage** (de face, en pied, fond neutre).
2. On la réutilise **comme image de référence** dans chaque génération où le personnage apparaît.
3. On note ici l'identifiant de l'image retenue.

| Personnage | Référence retenue |
|---|---|
| Léo | Candidate : [1-leo.jpg](../visuels/concepts/1-leo.jpg) (Higgsfield `4c08abba-d807-41d2-b2c6-efae4b39df27`) |
| Antoine | *à générer* |
| Monsieur Armand | Candidate : [2-armand.jpg](../visuels/concepts/2-armand.jpg) (`dfe5e3ad-c42e-4d30-a7ad-2eba7b63cb7f`) |
| Dorian et Kévin | Candidate : [3-tenaille.jpg](../visuels/concepts/3-tenaille.jpg) (`84796778-01cc-4395-9dd7-2748d091fe23`) |
| Le Grand Maître | Candidate : [4-grand-maitre.jpg](../visuels/concepts/4-grand-maitre.jpg) (`31bf69c8-550c-471c-901b-bc3ab7ad1316`) |

## Premiers essais (25 octobre 2026)

Huit images générées avec le prompt de base (modèle GPT Image 2.5, qualité haute), dans
[visuels/concepts/](../visuels/concepts/).

**Ce qui marche :** le style celluloïd, les couleurs, l'écharpe rouge, le damier mental, le freeze
« À suivre… », les textes en français sur l'affiche et au tableau de la classe.

**Ce qui confirme la règle « le damier n'est jamais laissé à l'IA » :**
- Sur le tableau de la classe, il y a des coordonnées d'échecs (A–J, 1–10) au lieu de la numérotation
  1–50, et des pions sur les cases claires.
- Le damier d'Armand a des pions rouges et noirs.
- Dans le damier mental, les pions sont posés aussi sur les cases claires. C'est acceptable pour un
  plan d'ambiance, jamais pour une position qui compte.

**Les positions exactes** sont dessinées par [outils/dessiner.py](../outils/dessiner.py), comme
[celle de l'épisode 1](../visuels/positions/s01e01/).

## Images du pilote (25 octobre 2026)

13 images générées (12 plans + 1 régénération), avec les dessins validés de Léo, d'Armand et de la
classe passés en **images de référence** : les visages et les tenues restent cohérents d'un plan à
l'autre.

**Défauts trouvés et corrigés :**
- Le damier mural de la classe recopiait les lettres d'échecs (A–J) de la référence. Il est remplacé
  par le vrai damier, incrusté en perspective par [outils/incruster.py](../outils/incruster.py), avec
  des cases carrées et l'énoncé « Les blancs jouent et gagnent » sous le damier.
- Une pancarte en japonais sur le mur (plan de l'horloge) : effacée.
- Des pions sur les cases claires (plan des mains) : plan régénéré en plus serré puis recadré.

**Leçon :** plus un damier est grand et lisible à l'image, plus il faut l'incruster par programme.
Les gros plans sur une seule case passent mieux.
