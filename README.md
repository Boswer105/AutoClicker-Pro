# 🖱️ AutoClicker Pro

**Un autoclicker open-source léger avec contrôle de souris, clavier et molette, interface moderne et séquences d'actions personnalisables.**

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## ✨ Fonctionnalités

- 🎯 **Multi-Points & Séquences** — Enregistrez une suite d'actions (clics, touches, molette) et rejouez-les en boucle.
- ⌨️ **Détection Clavier Intelligente** — Appuyez simplement sur une touche pour l'enregistrer, pas besoin de connaître son nom technique.
- 🔄 **Contrôle de la Molette** — Automatisez le scroll vers le haut ou le bas avec un nombre de crans personnalisable.
- ⚡ **Vitesse Réglable** — De 1 à 1000+ CPS (Clics Par Seconde) avec une précision au millième de seconde.
- 🖱️ **Boutons Configurables** — Clic gauche, droit, milieu, ou mode "Aucun" pour ne faire que du clavier/molette.
- 🎨 **Interface Moderne** — Design sombre (Dark Mode) épuré avec indicateur LED d'état en temps réel.
- 💾 **Sauvegarde JSON** — Exportez et importez vos configurations en un clic.
- 🧵 **Exécution en Thread** — L'interface reste fluide pendant l'automatisation.

  <img width="698" height="829" alt="Capture d&#39;écran 2026-11-13 151233" src="https://github.com/user-attachments/assets/91118c10-ff8a-4b9e-9222-ff9580c69a91" />

---

## ⌨️ Raccourcis Clavier

| Touche | Action |
|--------|--------|
| `F1` | Ajouter rapidement un point de clic à la position actuelle |
| `F6` | Démarrer / Arrêter l'automatisation |
| `F7` | Quitter l'application proprement |

---

## 🚀 Installation

### 🔹 1. Pour les utilisateurs (Méthode rapide)
Aucune installation requise !
1. Allez dans l'onglet **[Releases](https://github.com/Boswer105/AutoClicker-Pro/releases)**
2. Téléchargez le fichier `AutoClicker.exe`
3. Lancez-le. C'est tout !

### 🔹 2. Pour les développeurs (Depuis le code source)
Si vous préférez compiler le projet vous-même ou modifier le code :

```bash
git clone https://github.com/Boswer105/AutoClicker-Pro.git
cd AutoClicker-Pro
pip install -r requirements.txt
python autoclicker.py les dépendances installées : python -m PyInstaller --noconsole --onefile autoclicker.py)
```
💡 Compiler votre propre .exe (sans fenêtre CMD) :

```
python -m PyInstaller --noconsole --onefile autoclicker.py
```
Le fichier exécutable sera disponible dans le dossier dist/.
