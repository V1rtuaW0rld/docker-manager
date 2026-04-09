# 🐳 Docker Manager

A lightweight, modern web interface to manage your Docker Compose projects across different architectures.

<img width="615" height="435" alt="image" src="https://github.com/user-attachments/assets/d9fb868a-e4c4-49ad-94a0-a973471613cf" />

---

## 🇬🇧 English Description

**Docker Manager** is a minimalist but powerful web dashboard designed to centralize the management of multiple Docker Compose stacks. It provides complete control over your container ecosystem from any device.

### ✨ Key Features & Usage

#### 🛠 Interactive Management
- **In-Browser Editor**: Edit your `docker-compose.yml` files directly in the web interface with instant save.
- **Real-Time Logs**: Monitor your containers' activity with a high-performance streaming log viewer.
- **Integrated Terminal**: Open a fully functional shell (bash/sh) into any container directly in your browser using hidden `ttyd` integration.

#### 🔗 Clickable Titles (Project Links)
To make a project name clickable and redirect to its web interface, simply add a commented URL as the **very first line** of your `docker-compose.yml` file:
```yaml
#https://jellyfin.example.com
services:
  jellyfin:
    image: jellyfin/jellyfin
...
```

#### 🖼 Automatic Logos
Place a file named `logo.png` in the project directory. The application will automatically detect and display it on the dashboard.

#### 🔍 Smart Discovery
Robustly identifies containers belonging to each project using directory-based `docker compose` lookups, regardless of container naming conventions.

### 🚀 Deployment
```yaml
services:
  docker-manager:
    image: virtuaworld/docker-manager:latest
    ports:
      - "5000:5000"
    environment:
      - SERVER_IP=192.168.0.x # Important for terminal access
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /your/local/projects-directory:/root/projects-docker-compose
```

---

## 🇫🇷 Description Française

**Docker Manager** est un tableau de bord web minimaliste et puissant conçu pour centraliser la gestion de vos piles Docker Compose. Gardez le contrôle total sur vos conteneurs depuis n'importe quel appareil.

### ✨ Fonctionnalités & Utilisation

#### 🛠 Gestion Interactive
- **Éditeur Intégré** : Modifiez vos fichiers `docker-compose.yml` directement depuis l'interface web avec sauvegarde instantanée.
- **Logs en Streaming** : Surveillez l'activité de vos conteneurs en temps réel avec un lecteur de logs haute performance.
- **Console Web** : Ouvrez un terminal interactif (bash/sh) dans n'importe quel conteneur via une intégration transparente de `ttyd`.

#### 🔗 Titres Cliquables (Liens Projets)
Ajoutez une URL en commentaire sur la **toute première ligne** de votre fichier `docker-compose.yml` pour rendre le titre cliquable :
```yaml
#https://jellyfin.virtuaworld.org
services:
  jellyfin:
    image: jellyfin/jellyfin
...
```

#### 🖼 Logos Automatiques
Glissez un fichier `logo.png` à côté de votre `docker-compose.yml`. L'application le détectera et l'affichera automatiquement sur le dashboard.

#### 🔍 Découverte Intelligente
Identifie de manière robuste les conteneurs appartenant à chaque projet via une recherche basée sur les répertoires, sans contrainte de nommage.

### 🚀 Déploiement
```yaml
services:
  docker-manager:
    image: virtuaworld/docker-manager:latest
    ports:
      - "5000:5000"
    environment:
      - SERVER_IP=192.168.0.x # Important pour l'accès terminal
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /votre/chemin/local/projets:/root/projects-docker-compose
```

---

### 🛠 Tech Stack
- **Backend**: Python / Flask
- **Frontend**: Vanilla JS / CSS3
- **Terminal**: ttyd
- **Architecture**: Multi-arch (AMD64, ARM64/Raspberry Pi)
