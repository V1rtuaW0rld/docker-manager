FROM python:3.10.13-slim

# 🧰 Installer pip + Docker CLI (via dépôt officiel Docker avec détection d'architecture)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update && apt-get install -y \
    docker-ce-cli \
    && pip install --no-cache-dir --upgrade pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV DOCKER_PROJECTS_PATH="/home/virtua/projects-docker-compose"

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--with-threads"]
