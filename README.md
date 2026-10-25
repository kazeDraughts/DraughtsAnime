# Kaze, le vent du damier

Un anime au style « TV japonaise des années 80 » sur le jeu de dames international (10×10),
inspiré de l'histoire vraie d'un joueur du Nord de la France.
Épisodes de 1 à 2 minutes, chacun se termine par un cliffhanger.

> Titre de travail, à valider.

## Où trouver quoi

| Fichier | Contenu |
|---|---|
| [bible/01-concept.md](bible/01-concept.md) | Le pitch, le thème, le public, le ton |
| [bible/02-personnages.md](bible/02-personnages.md) | Les personnages et leur arc |
| [bible/03-monde-et-dames.md](bible/03-monde-et-dames.md) | Les lieux (anagrammes), l'époque, les règles et les coups spéciaux |
| [bible/04-style-visuel.md](bible/04-style-visuel.md) | Le style graphique et les prompts d'images |
| [bible/05-format-et-voix.md](bible/05-format-et-voix.md) | La structure d'un épisode, les règles de clarté, les voix |
| [saisons/saison-1.md](saisons/saison-1.md) | Les 36 épisodes de la saison 1 |
| [saisons/saisons-2-et-3.md](saisons/saisons-2-et-3.md) | Les grandes lignes des saisons 2 et 3 |
| [matiere-premiere/anecdotes.md](matiere-premiere/anecdotes.md) | Les souvenirs réels et l'épisode où chacun est utilisé |
| [episodes/](episodes/) | Les scénarios découpés plan par plan (épisode 1 = le pilote, épisode 2 en brouillon) |
| [visuels/concepts/](visuels/concepts/) | Les premières images de style |
| [visuels/positions/](visuels/positions/) | Les diagrammes exacts des positions (PNG + GIF animé) |
| [visuels/personnages/](visuels/personnages/), [visuels/decors/](visuels/decors/) | Personnages détourés et décors réutilisables (ciel étoilé) |
| [outils/](outils/) | Le moteur de règles, le dessin des positions, le montage des animatiques ; `outils/plans/` : les corrections propres à un plan |

## Les outils de damier

Il faut Python 3 et Pillow (`pip install pillow`).

```bash
cd outils
python3 positions.py        # vérifie toutes les positions du catalogue
python3 dessiner.py s01e01  # dessine une position et sa solution
python3 damier_mental.py    # rend les plans du damier mental (images et animations)
```

Pour ajouter une position, il suffit d'écrire son FEN et sa solution dans `outils/positions.py`. Le
script refuse toute position illégale ou toute solution où un coup annoncé comme « forcé » ne l'est
pas.

## L'animatique

Il faut aussi `ffmpeg`. Les corrections de `outils/plans/` utilisent en plus NumPy et OpenCV
(`pip install numpy opencv-python-headless`).

```bash
python3 outils/animatique.py episodes/s01e01-test-voix.json   # → montages/s01e01-test-voix.mp4
```

Un fichier JSON décrit les plans : image, voix, sous-titre, zoom, tic-tac, image figée « À suivre ».
**Les voix (`audio/`) et les vidéos (`montages/`) ne sont jamais envoyées sur GitHub**, car le dépôt
est public. Elles restent sur la machine.

## La méthode

1. **L'histoire d'abord.** Bible, arcs, épisodes, scénario, storyboard. Les images viennent en dernier.
2. **Un pilote parfait avant de produire.** On peaufine l'épisode 1 jusqu'à ce qu'il soit excellent,
   puis on en fait le modèle des suivants.
3. **Le damier n'est jamais inventé par l'IA.** Les positions sont construites et vérifiées par programme.
4. **Ce dépôt est la mémoire du projet.** Chaque nouvelle session repart d'ici.

## Où on en est

- [x] Entretien et matière première
- [x] Bible v0.1 et liste des épisodes de la saison 1
- [x] Premières images de style (8 essais)
- [x] Moteur de règles et diagrammes exacts, avec la position de l'épisode 1 vérifiée
- [x] Découpage plan par plan de l'épisode 1 (brouillon)
- [x] Validation des grandes lignes par l'auteur (revanche de fiction, passé d'Armand, noms)
- [x] Test des voix (3 répliques) et première animatique de 18 secondes
- [x] Choix des voix : Léo doublé par la compagne de l'auteur, voix naturelle
- [ ] Choix du titre
- [x] Visuels de référence de Léo, Armand et la classe (utilisés pour le pilote)
- [x] Pilote : les 12 images de l'épisode 1, corrigées, et l'animatique complète (1 min 25)
- [ ] Pilote : enregistrer les 10 répliques manquantes, musique, montage final
- [x] Épisode 2 : découpage et répliques (brouillon), pour enregistrer les épisodes 1 et 2 ensemble
- [ ] Production par lots de 5 épisodes

## Dédicace

À Gilbert Charles, qui est un jour entré dans une classe avec un damier sous le bras.
