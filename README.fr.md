# yt-dlp GUI

*[Read in English / Lire en Anglais](README.md)*

Une interface graphique moderne et riche en fonctionnalités pour [yt-dlp](https://github.com/yt-dlp/yt-dlp), développée en Python avec CustomTkinter.

![Capture d'écran](src/assets/icon.png)

## Fonctionnalités

-   **Interface Moderne** : Thème sombre épuré utilisant CustomTkinter.
-   **Choix du Format** : Sélectionnez Video+Audio ou Audio seul.
-   **Contrôle de la Qualité** : Choisissez la résolution (Meilleure, 1080p, 720p, etc.).
-   **File d'Attente** : Téléchargez plusieurs vidéos simultanément.
-   **Prévisualisation** : Affiche automatiquement les métadonnées (miniature, titre, durée) avant le téléchargement.
-   **Nommage Intelligent** : Modèles de noms de fichiers personnalisables.
-   **Support des Cookies** : Importez vos cookies pour les contenus restreints ou premium.
-   **Métadonnées Intégrées** : Balisage complet des fichiers et intégration des miniatures.

## Installation

### Exécutable (Windows)
1.  Téléchargez la dernière version depuis la page [Releases](https://github.com/yourusername/yt-dlp-gui/releases).
2.  Extrayez le fichier zip.
3.  Lancez `yt-dlp-gui.exe`.

### Depuis le code source
1.  **Prérequis** : Python 3.8+
2.  **Cloner le dépôt** :
    ```bash
    git clone https://github.com/yourusername/yt-dlp-gui.git
    cd yt-dlp-gui
    ```
3.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```
4.  **Lancer l'application** :
    ```bash
    python main.py
    ```

## Utilisation

1.  **Coller l'URL** : Insérez un lien YouTube (ou autre site supporté) dans le champ de saisie.
2.  **Aperçu** : L'application récupère et affiche les informations de la vidéo.
3.  **Configuration** : Choisissez le format et la qualité souhaités.
4.  **Télécharger** : Cliquez sur "Confirmer le téléchargement" ou sur le bouton principal pour ajouter à la file d'attente.
5.  **Gestion** : Suivez la progression, annulez ou relancez les téléchargements depuis la liste.


## ⚙️ Configuration & Paramètres

L'application propose plusieurs paramètres pour personnaliser votre expérience. Cliquez sur le bouton **Paramètres (⚙)** pour y accéder :

### 1. Général
-   **Dossier de téléchargement** : Le dossier où les fichiers seront enregistrés. Par défaut : `Téléchargements`.
-   **Thème** : Choisissez entre le mode "Sombre" (par défaut) ou "Clair".
-   **Dossier temporaire** : Emplacement pour les fichiers intermédiaires (utile si l'espace disque est limité sur C:).

### 2. Format de Sortie (Modèle de Nommage)
Personnalisez le nom des fichiers via les modèles `yt-dlp`.
-   **Modèle par défaut** : `%(upload_date>%Y.%m.%d)s.%(title)s [%(id)s].%(ext)s`
    -   Résultat : `2023.12.31.Titre de la Vidéo [dQw4w9WgXcQ].mp4`
-   **Variables courantes** :
    -   `%(title)s` : Titre de la vidéo.
    -   `%(id)s` : Identifiant unique de la vidéo.
    -   `%(uploader)s` : Nom de la chaîne.
    -   `%(upload_date)s` : Date de mise en ligne (AAAAMMJJ).
-   **📚 Documentation** : Pour la liste complète des variables, consultez la [Documentation des modèles yt-dlp](https://github.com/yt-dlp/yt-dlp#output-template).

### 3. Authentification (Cookies)
Requis pour télécharger :
-   **Contenu Premium** (YouTube Premium).
-   **Vidéos avec restriction d'âge**.
-   **Vidéos réservées aux membres**.

**Utilisation** :
Fournissez le chemin vers un fichier `cookies.txt` (exporté via une extension de navigateur type "Get cookies.txt").

### 4. Avancé (Binaires)
L'application tente de détecter automatiquement `yt-dlp` et `ffmpeg`.
-   **Chemin yt-dlp** : Spécifiez manuellement `yt-dlp.exe` si la version intégrée est obsolète.
-   **Chemin FFmpeg** : Spécifiez manuellement `ffmpeg.exe`. **FFmpeg est requis** pour fusionner les flux vidéo et audio haute qualité (1080p+).

---

## 📦 Dépendances & Installation

### Dépendances Python
L'application dépend de plusieurs librairies Python, listées dans `requirements.txt` :
-   `customtkinter` : Pour l'interface graphique moderne.
-   `yt-dlp` : Le moteur de téléchargement.
-   `pillow` : Pour le traitement des images (miniatures).
-   `packaging` : Pour la gestion des versions.

Pour les installer :
```bash
pip install -r requirements.txt
```

### Outils Externes (FFmpeg)
Pour une fonctionnalité complète (notamment la fusion vidéo/audio HD), **FFmpeg** est fortement recommandé.
1.  Téléchargez FFmpeg depuis [ffmpeg.org](https://ffmpeg.org/download.html).
2.  Extrayez l'archive.
3.  Ajoutez-le au PATH système ou spécifiez le chemin vers `ffmpeg.exe` dans les Paramètres de l'application.

## Licence

Licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Remerciements

-   [yt-dlp](https://github.com/yt-dlp/yt-dlp) pour le moteur de téléchargement puissant.
-   [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) pour la bibliothèque d'interface utilisateur.
