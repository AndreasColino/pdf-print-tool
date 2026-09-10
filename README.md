# PDF Print Tool

---

## 🇫🇷 Français

### À propos du projet

Application de bureau développée en Python (CustomTkinter) permettant de préparer et d'imprimer des bons de commande à partir d'un PDF. L'outil duplique la page sélectionnée deux fois sur une même feuille A4 (format recto/verso à plier), avec la possibilité d'ajouter un texte personnalisé positionnable librement, puis d'envoyer directement l'impression vers l'imprimante choisie. Projet personnel, développé en dehors du cadre universitaire.

### Fonctionnalités principales

- **Glisser-déposer :** Chargement d'un PDF par drag & drop ou sélection manuelle.
- **Prévisualisation par miniatures :** Navigation entre les pages du document et sélection de la page à utiliser.
- **Ajout de texte :** Zone de texte libre superposée sur le document, avec taille de police réglable et positionnement précis via des curseurs X/Y.
- **Mise en page automatique :** Génération d'une feuille A4 avec la page dupliquée de part et d'autre d'une ligne de pliage.
- **Aperçu en temps réel :** Rendu instantané du document source et du rendu final avant impression.
- **Impression directe :** Sélection de l'imprimante et envoi du document sans passer par un fichier intermédiaire.
- **Interface bilingue :** Bascule Français / Anglais en un clic.

### Technologies et Outils

- **Langage :** Python
- **Interface :** CustomTkinter (thème sombre)
- **Traitement PDF :** PyMuPDF (`fitz`)
- **Images :** Pillow
- **Glisser-déposer :** tkinterdnd2
- **Impression (Windows) :** pywin32 (`win32print`, `win32ui`)

### Installation & Utilisation

*Prérequis : Windows (l'impression directe utilise l'API Windows).*

#### Option 1 : Téléchargement direct (Recommandé - Windows)

Aucune installation de Python n'est nécessaire.

1. Rends-toi dans la section [**Releases**](https://github.com/AndreasColino/pdf-print-tool/releases) de ce dépôt.
2. Télécharge le fichier `verso_rotation.exe`.
3. Double-clique sur `verso_rotation.exe` pour lancer l'application.

#### Option 2 : Exécution depuis les sources (Python)

1. **Cloner le dépôt :**

   ```bash
   git clone https://github.com/AndreasColino/pdf-print-tool.git
   cd pdf-print-tool
   ```

2. **Installer les dépendances :**

   ```bash
   pip install -r requirements.txt
   pip install pywin32
   ```

3. **Lancer l'application :**

   ```bash
   python verso_rotation.py
   ```

---

## 🇬🇧 English

### About the project

A Python desktop application (CustomTkinter) for preparing and printing order forms from a PDF. The tool duplicates the selected page twice on a single A4 sheet (a fold-in-half recto/verso layout), lets you add freely positioned custom text, and sends the print job directly to the chosen printer. Personal project, built outside of university coursework.

### Main Features

- **Drag & drop:** Load a PDF by dragging it onto the window or via manual file selection.
- **Thumbnail preview:** Browse the document's pages and pick the one to use.
- **Text overlay:** Add free text on top of the document, with adjustable font size and precise X/Y slider positioning.
- **Automatic layout:** Generates an A4 sheet with the page duplicated on both sides of a fold line.
- **Live preview:** Instant rendering of both the source page and the final print output.
- **Direct printing:** Select a printer and send the document straight to print, no intermediate file needed.
- **Bilingual interface:** One-click French / English toggle.

### Technologies & Tools

- **Language:** Python
- **UI:** CustomTkinter (dark theme)
- **PDF processing:** PyMuPDF (`fitz`)
- **Images:** Pillow
- **Drag & drop:** tkinterdnd2
- **Printing (Windows):** pywin32 (`win32print`, `win32ui`)

### Installation & Usage

*Prerequisite: Windows (direct printing relies on the Windows API).*

#### Option 1: Standalone Download (Recommended - Windows)

No Python installation required.

1. Go to the [**Releases**](https://github.com/AndreasColino/pdf-print-tool/releases) section of this repository.
2. Download `verso_rotation.exe`.
3. Double-click `verso_rotation.exe` to run the application.

#### Option 2: Run from Source (Python)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/AndreasColino/pdf-print-tool.git
   cd pdf-print-tool
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   pip install pywin32
   ```

3. **Run the application:**

   ```bash
   python verso_rotation.py
   ```
