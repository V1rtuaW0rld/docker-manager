# 🐳 Docker Manager

A lightweight, modern web interface to manage your Docker Compose projects across different architectures.

[English Version Below] | [Version Française ci-dessous]

---

## 🇬🇧 English Description

**Docker Manager** is a minimalist but powerful web dashboard designed to centralize the management of multiple Docker Compose stacks. It allows you to monitor, control, and edit your projects through a sleek, responsive interface.

### ✨ Key Features
- **Project Grid**: Automatically discovers projects in your designated folder.
- **Cycle Management**: Start, Stop, and Restart stacks with real-time status updates.
- **Interactive Terminal**: Access any container's shell directly in your browser using integrated `ttyd`.
- **Streaming Logs**: Watch your container logs in real-time within the UI.
- **In-Browser Editor**: Modify your `docker-compose.yml` files directly from the web interface.
- **Multi-Architecture**: Fully compatible with `amd64` (Server/Desktop) and `arm64` (Raspberry Pi).
- **Smart Discovery**: Robustly identifies containers belonging to each project using directory-based lookups (no naming conventions required).

### 🚀 Quick Start
1. Mount your projects directory to `/root/projects-docker-compose`.
2. Mount the Docker socket: `/var/run/docker.sock`.
3. Set `SERVER_IP` environment variable for terminal routing.
4. Access via port `5000`.

---

## 🇫🇷 Description Française

**Docker Manager** est un tableau de bord web minimaliste et puissant conçu pour centraliser la gestion de vos différentes piles Docker Compose. Il vous permet de surveiller, contrôler et éditer vos projets via une interface moderne et réactive.

### ✨ Caractéristiques principales
- **Grille de Projets** : Découverte automatique des projets dans votre dossier dédié.
- **Gestion du Cycle de Vie** : Démarrez, Arrêtez et Redémarrez vos stacks avec mise à jour du statut en temps réel.
- **Terminal Interactif** : Accédez au shell de n'importe quel conteneur directement dans votre navigateur grâce à l'intégration de `ttyd`.
- **Logs en Streaming** : Visualisez les logs de vos conteneurs en temps réel depuis l'interface.
- **Éditeur Intégré** : Modifiez vos fichiers `docker-compose.yml` directement depuis l'interface web.
- **Multi-Architecture** : Entièrement compatible avec `amd64` (Serveur/PC) et `arm64` (Raspberry Pi).
- **Découverte Intelligente** : Identifie de manière robuste les conteneurs appartenant à chaque projet via une recherche basée sur les répertoires (aucune convention de nommage imposée).

### 🚀 Démarrage Rapide
1. Montez votre répertoire de projets dans `/root/projects-docker-compose`.
2. Montez le socket Docker : `/var/run/docker.sock`.
3. Configurez la variable d'environnement `SERVER_IP` pour le routage du terminal.
4. Accédez via le port `5000`.

---

### 🛠 Tech Stack
- **Backend**: Python / Flask
- **Frontend**: Vanilla JS / CSS3 (Modern UI)
- **Terminal**: ttyd
- **Reverse Proxy**: Nginx (integrated)
