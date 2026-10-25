# 05 · Format, clarté et voix

## Le format

- **Durée :** de 60 à 120 secondes par épisode.
- **Image :** **vertical 9:16** (TikTok, Reels, Shorts), parce que le public visé est jeune. Les
  plans sont composés avec l'action au centre, pour pouvoir sortir une version 16:9 plus tard
  (compilation d'une saison sur YouTube, par exemple). *À valider.*
- **Sous-titres incrustés, toujours.** Beaucoup regardent sans le son.
- **Langue :** français, avec le ton théâtral des doublages des années 80.

## La structure d'un épisode

| Temps | Bloc | Contenu |
|---|---|---|
| 0:00 – 0:06 | **Précédemment** | Le narrateur et 2 ou 3 images de l'épisode d'avant |
| 0:06 – 0:10 | **Titre** | Carton-titre façon années 80 et jingle de 3 secondes |
| 0:10 – 0:25 | **La question** | L'enjeu de l'épisode, posé clairement |
| 0:25 – 1:10 | **La montée** | Monologue intérieur, damier mental, flash-back, réactions des autres |
| 1:10 – 1:25 | **Le retournement** | La surprise, le coup, la révélation |
| 1:25 – 1:35 | **Le cliffhanger** | Image figée, virée sépia-rouge, « À suivre… » |
| 1:35 – 1:45 | **Le teaser** | Le narrateur : « Ne manquez pas le prochain épisode : *[titre]* ! » |

Un épisode plus court (60 secondes) garde les mêmes blocs, en plus serré.

**Le générique complet** (une chanson en français dans l'esprit des génériques chantés des années 80)
n'est pas dans chaque épisode : c'est une vidéo à part, la bande-annonce de la série. **La dédicace à
Gilbert Charles** figure au générique, à la fin de chaque saison et dans la description des vidéos.

## Les règles de clarté

C'est la leçon des essais précédents : *« c'était pas très compréhensible »*.

1. **Une seule question par épisode**, posée dans les 15 premières secondes. *« Léo va-t-il trouver
   le coup ? »*
2. **Le spectateur sait toujours trois choses :** qui mène, quelle est la menace, ce que le héros doit
   trouver.
3. **Le narrateur pose l'enjeu** au début et la question à la fin. Il parle aux enfants, pas aux
   joueurs classés.
4. **Au moment clé, on montre un vrai diagramme lisible** : vue du dessus, flèches, cases qui
   s'allument. Un enfant de 8 ans doit comprendre ce qui se passe.
5. **Trois personnages qui parlent, au maximum**, par épisode.
6. **Des phrases courtes.** Le monologue intérieur tient en quelques mots : *« Si je prends… il
   reprend… et là… non ! »*
7. **Un seul mot de jargon par épisode**, expliqué par l'histoire (rafle, dame, remise, prise
   obligatoire…).
8. **Le test des 3 secondes :** sur chaque plan, on doit comprendre en 3 secondes où regarder.

## Les voix

C'est l'autre leçon des essais précédents : les voix déçoivent. Le plan :

### Option recommandée : des voix humaines

- **L'auteur et sa compagne enregistrent les dialogues.** Pourquoi pas aussi des amis du club pour des
  apparitions : la « petite famille » du damier, jusque dans les voix.
- **Pour les voix d'enfants**, on garde votre jeu d'acteur (l'émotion, le rythme) et on transforme
  seulement le timbre avec un changeur de voix IA. **À tester sur 3 répliques avant de décider.**
- **Le narrateur** est la voix iconique des années 80 : grave, enthousiaste, dramatique.
  *« Ne manquez pas le prochain épisode ! »*
  - Idée à discuter : **le narrateur, c'est Léo adulte.** Il raconte ses souvenirs (*« J'avais 10 ans
    quand un homme est entré dans ma classe avec un damier sous le bras… »*), ce qui donne beaucoup
    d'émotion et boucle avec le dernier épisode.

### Test du 25 octobre 2026 (3 répliques de l'épisode 1)

Prises de l'auteur au téléphone : propres, sans saturation, bruit de fond vers −55 dB. On peut donc
enregistrer au téléphone.

| Version de Léo | Hauteur | Compréhension (transcription auto) | Coût |
|---|---|---|---|
| Voix d'origine | 116 Hz | Parfaite | — |
| **Locale** (hauteur ~270 Hz, timbre ×1,15) | 270 Hz | **Parfaite** | Gratuit |
| Locale poussée (timbre ×1,25) | 267 Hz | Abîmée (« J-J-J'ai crois ») | Gratuit |
| IA Higgsfield, voix « Miles » | 181 Hz | Abîmée (« Les **thèmes** », « jeu **du** vieux ») | 1 crédit |
| IA Higgsfield, voix « Cody » | — | La conversion a échoué | — |

**Conclusion provisoire :** la version locale garde le jeu d'acteur et la compréhension. La voix IA
anglophone déforme le français. **Avis de l'auteur à l'oreille : en attente.**

**L'autre piste, la plus authentique :** dans les animes, les jeunes garçons sont très souvent doublés
par des femmes (Son Goku enfant, au Japon, par exemple). La compagne de l'auteur pourrait jouer Léo
avec sa voix naturelle, sans aucune transformation, et l'auteur jouerait Armand (avec l'accent du
Sud) et le narrateur.

**Réglage de la transformation locale :** Praat, fonction « Change gender » : hauteur médiane 270 Hz,
formants ×1,15, amplitude de hauteur ×1,0 (×1,3 pour une réplique chuchotée).

### Comment bien enregistrer avec un téléphone

- Choisir une pièce pleine de tissus (une chambre, ou face à une penderie ouverte). Éviter la cuisine
  et la salle de bain.
- Tenir le téléphone à 20 cm de la bouche, un peu de côté.
- Faire 3 prises par réplique, en surjouant. Le doublage des années 80 est théâtral.
- Garder une seconde de silence avant et après chaque prise.
- Un fichier par réplique, nommé `s01e01_r03_leo_prise2.m4a` (épisode, réplique, personnage, prise).

### La musique et les bruitages

- **La musique :** synthétiseurs et cuivres façon années 80, un thème héroïque pour Léo, un thème
  inquiétant pour la Tenaille, un thème calme et doré pour le Grand Maître.
- **Les bruitages signatures :** le *CLAC* du pion posé fort, le tic-tac de la pendule, le
  *whoosh* du plongeon dans le damier mental, le bruit de verre brisé d'une variante qui échoue.
- **Le jingle** de 3 secondes au titre, et la petite musique du « À suivre… ».
