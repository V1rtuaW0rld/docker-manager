# 🐳 Docker Manager

A lightweight, modern web interface to manage your Docker Compose projects across different architectures.

<img width="615" height="435" alt="image" src="https://github.com/user-attachments/assets/d9fb868a-e4c4-49ad-94a0-a973471613cf" />

---

## 🇬🇧 English Description

**Docker Manager** is a minimalist but powerful web dashboard designed to centralize the management of multiple Docker Compose stacks.

### ✨ Key Features & Usage

#### 1. Clickable Titles (Project Links)
To make a project name clickable and redirect to its web interface, simply add a commented URL as the **very first line** of your `docker-compose.yml` file:
```yaml
#https://jellyfin.example.com
services:
  jellyfin:
    image: jellyfin/jellyfin
...
```

#### 2. Automatic Logos
To display a logo for a project, just place a file named `logo.png` in the same directory as your `docker-compose.yml`. The application will automatically detect and resize it for the dashboard.

#### 3. Smart Discovery
Identify containers belonging to each project using directory-based lookups. No specific naming convention is required for your containers anymore.

### 🚀 Quick Start (Deployment)
To run Docker Manager, use the following volume mapping and environment variables:

```yaml
services:
  docker-manager:
    image: virtuaworld/docker-manager:latest
    ports:
      - "5000:5000"
    environment:
      - SERVER_IP=192.168.0.x # Your server IP for terminal access
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /your/local/projects-directory:/root/projects-docker-compose
```

---

## 🇫🇷 Description Française

**Docker Manager** est un tableau de bord web minimaliste et puissant conçu pour centraliser la gestion de vos piles Docker Compose.

### ✨ Fonctionnalités & Utilisation

#### 1. Titres Cliquables (Liens Projets)
Pour qu'un nom de projet devienne un lien vers son interface web, ajoutez simplement l'URL en commentaire sur la **toute première ligne** de votre fichier `docker-compose.yml` :
```yaml
#https://jellyfin.virtuaworld.org
services:
  jellyfin:
    image: jellyfin/jellyfin
...
```

#### 2. Logos Automatiques
Pour afficher un logo, glissez simplement un fichier `logo.png` à côté de votre `docker-compose.yml`. L'application le détectera et le redimensionnera automatiquement.

#### 3. Découverte Intelligente
L'application identifie les conteneurs appartenant à chaque projet via une recherche basée sur les répertoires. Aucune convention de nommage n'est désormais imposée pour vos conteneurs.

### 🚀 Démarrage Rapide (Déploiement)
Pour lancer Docker Manager, utilisez les montages de volumes et variables suivants :

```yaml
services:
  docker-manager:
    image: virtuaworld/docker-manager:latest
    ports:
      - "5000:5000"
    environment:
      - SERVER_IP=192.168.0.x # L'IP de votre serveur pour le terminal
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /votre/chemin/local/projets:/root/projects-docker-compose
```

---

### 🛠 Tech Stack
- **Backend**: Python / Flask
- **Frontend**: Vanilla JS / CSS3 (Modern UI)
- **Terminal**: ttyd
- **Reverse Proxy**: Nginx (integrated)
