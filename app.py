from flask import Flask, jsonify, request, render_template, send_file, send_from_directory, Response, redirect, url_for
from PIL import Image
import os
import subprocess
import socket


app = Flask(__name__, static_folder='static')

# Répertoire où sont stockés les projets Docker Compose
DOCKER_PROJECTS_PATH = os.getenv("DOCKER_PROJECTS_PATH", "/root/projects-docker-compose")

from concurrent.futures import ThreadPoolExecutor

@app.route('/api/projects', methods=['GET'])
def list_projects():
    urls = get_project_urls(DOCKER_PROJECTS_PATH)

    project_dirs = sorted([
        item for item in os.listdir(DOCKER_PROJECTS_PATH)
        if os.path.isdir(os.path.join(DOCKER_PROJECTS_PATH, item)) and
           os.path.exists(os.path.join(DOCKER_PROJECTS_PATH, item, 'docker-compose.yml'))
    ], key=str.lower)

    def build_project_entry(item):
        path = os.path.join(DOCKER_PROJECTS_PATH, item)
        status = get_project_status(path)
        return {
            'name': item,
            'status': status,
            'url': urls.get(item)  # ← injecte l'URL ici
        }

    with ThreadPoolExecutor(max_workers=8) as executor:
        projects = list(executor.map(build_project_entry, project_dirs))

    return jsonify(projects)


def get_project_urls(projects_path):
    urls = {}
    for project_name in os.listdir(projects_path):
        compose_path = os.path.join(projects_path, project_name, "docker-compose.yml")
        if os.path.isfile(compose_path):
            with open(compose_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line.startswith("#http"):
                    urls[project_name] = first_line.lstrip("#").strip()
    return urls

urls = get_project_urls(DOCKER_PROJECTS_PATH)
print("🔗 URLs détectées :", urls)

def get_status(service_name, projects_path):
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "-q", service_name],
            cwd=os.path.join(projects_path, service_name),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        return "running" if result.stdout.strip() else "stopped"
    except Exception as e:
        print(f"⚠️ Erreur get_status pour {service_name} :", e)
        return "stopped"

def get_all_services(projects_path):
    return [
        name for name in os.listdir(projects_path)
        if os.path.isdir(os.path.join(projects_path, name))
    ]

services = []
for service_name in get_all_services(DOCKER_PROJECTS_PATH):
    services.append({
        "name": service_name,
        "status": get_status(service_name, DOCKER_PROJECTS_PATH),
        "url": urls.get(service_name)
    })



def get_project_status(project_path):
    """Vérifier si un projet est en cours d'exécution"""
    result = subprocess.run(['docker', 'compose', 'ps', '-q'], cwd=project_path, capture_output=True, text=True)
    return 'running' if result.stdout.strip() else 'stopped'

@app.route('/api/containers', methods=['GET'])
def list_containers():
    """Lister tous les conteneurs en cours d'exécution"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.ID}} {{.Image}} {{.Names}}'],
            capture_output=True, text=True
        )
        containers = [
            {'id': line.split()[0], 'image': line.split()[1], 'name': line.split()[2]}
            for line in result.stdout.strip().split('\n')
            if line
        ]
        return jsonify(containers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_name>/start', methods=['POST'])
def start_project(project_name):
    """Démarrer un projet Docker Compose"""
    project_path = os.path.join(DOCKER_PROJECTS_PATH, project_name)
    if not os.path.exists(os.path.join(project_path, 'docker-compose.yml')):
        return jsonify({'error': 'Projet introuvable'}), 404

    try:
        subprocess.run(['docker', 'compose', 'up', '-d'], cwd=project_path, check=True)
        return jsonify({'status': 'started', 'project': project_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_name>/stop', methods=['POST'])
def stop_project(project_name):
    """Arrêter un projet Docker Compose"""
    project_path = os.path.join(DOCKER_PROJECTS_PATH, project_name)
    if not os.path.exists(os.path.join(project_path, 'docker-compose.yml')):
        return jsonify({'error': 'Projet introuvable'}), 404

    try:
        subprocess.run(['docker', 'compose', 'down'], cwd=project_path, check=True)
        return jsonify({'status': 'stopped', 'project': project_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<project_name>/restart', methods=['POST'])
def restart_project(project_name):
    """Redémarrer un projet Docker Compose"""
    project_path = os.path.join(DOCKER_PROJECTS_PATH, project_name)
    if not os.path.exists(os.path.join(project_path, 'docker-compose.yml')):
        return jsonify({'error': 'Projet introuvable'}), 404

    try:
        subprocess.run(['docker', 'compose', 'restart'], cwd=project_path, check=True)
        return jsonify({'status': 'restarted', 'project': project_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/projects/<project_name>/logo.png')
def get_logo(project_name):
    """Servir les logos des projets Docker Compose avec redimensionnement"""
    logo_path = os.path.join(DOCKER_PROJECTS_PATH, project_name, "logo.png")

    if not os.path.exists(logo_path):
        return '', 404  # Retourne 404 si le logo est introuvable
    
    # Charger et redimensionner l’image
    img = Image.open(logo_path)
    img.thumbnail((50, 50))  # Taille maximale sans déformation

    # Sauvegarder l’image temporairement et l’envoyer
    temp_path = f"/tmp/{project_name}_logo_resized.png"
    img.save(temp_path, format="PNG")

    return send_file(temp_path, mimetype='image/png')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


@app.route('/')
def home():
    """Afficher l'interface HTML"""
    return render_template('index.html')



import subprocess

@app.route('/logs/<container_name>')
def get_logs(container_name):
    """Récupérer les logs en streaming pour un conteneur donné"""
    # Lancer les logs Docker en streaming
    def generate():
        log_process = subprocess.Popen(["docker", "logs", "-f", container_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in iter(log_process.stdout.readline, ''):
            yield f"data: {line.strip()}\n\n"  # Format EventSource

    return Response(generate(), content_type='text/event-stream')

@app.route('/compose/<project_name>')
def get_compose_file(project_name):
    """Lire le fichier docker-compose.yml du projet"""
    compose_path = f"{DOCKER_PROJECTS_PATH}/{project_name}/docker-compose.yml"

    if not os.path.exists(compose_path):
        return f"Fichier `docker-compose.yml` introuvable pour {project_name}.", 404

    with open(compose_path, "r") as file:
        content = file.read()

    return Response(content, content_type="text/plain")


@app.route('/edit/<project_name>', methods=['GET'])
def edit_compose(project_name):
    path = os.path.join(DOCKER_PROJECTS_PATH, project_name, 'docker-compose.yml')
    if not os.path.isfile(path):
        return f"Fichier introuvable pour {project_name}", 404

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    return render_template('edit.html', project_name=project_name, compose_content=content)

@app.route('/edit/<project_name>', methods=['POST'])
def save_compose(project_name):
    new_content = request.form['compose_content']
    path = os.path.join(DOCKER_PROJECTS_PATH, project_name, 'docker-compose.yml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return redirect(url_for('index'))
import subprocess

def get_containers_for_project(project_name):
    """Lister les conteneurs appartenant réellement à ce projet via docker compose"""
    project_path = os.path.join(DOCKER_PROJECTS_PATH, project_name)
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "-a", "--format", "{{.Name}}"],
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        names = result.stdout.strip().split("\n")
        return [{"name": name} for name in names if name]

    except subprocess.CalledProcessError as e:
        print(f"Erreur Docker discovery pour {project_name} : {e.stderr}")
        return []
    except Exception as e:
        print(f"Erreur inattendue discovery pour {project_name} : {e}")
        return []

@app.route('/api/projects/<project_name>/containers')
def get_project_containers(project_name):
    containers = get_containers_for_project(project_name)
    return jsonify(containers)

@app.route('/')
def index():
    return render_template('index.html')

def get_free_port():
    """Trouve un port libre dans la plage 5001-5050 pour ttyd"""
    for port in range(5001, 5051):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    raise RuntimeError("Aucun port libre disponible entre 5001 et 5050")

def get_server_ip():
    """Renvoie l'IP réseau réelle du serveur (pas 127.0.0.1)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # ping fictif juste pour récupérer une IP locale
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

import subprocess
import time

# Dictionnaire pour stocker les instances ttyd en cours: { container_name: {"port": port, "process": Popen} }
ttyd_instances = {}

def get_shell(container_name):
    # Tester bash
    try:
        subprocess.run(['docker', 'exec', container_name, 'bash', '-c', 'exit'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return 'bash'
    except subprocess.CalledProcessError:
        pass

    # Tester sh
    try:
        subprocess.run(['docker', 'exec', container_name, 'sh', '-c', 'exit'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return 'sh'
    except subprocess.CalledProcessError:
        pass

    return None  # Aucun shell disponible
    
def start_terminal(container, shell):
    # Si terminal déjà en cours pour ce conteneur, vérifier qu'il est toujours actif
    if container in ttyd_instances:
        instance = ttyd_instances[container]
        if instance["process"].poll() is None:
            # Processus ttyd toujours actif, on réutilise le port
            return instance["port"]
        else:
            # Nettoyer s'il est mort
            del ttyd_instances[container]

    port = get_free_port()
    ttyd_cmd = [
        'ttyd',
        '-W',
        '--base-path', f'/ttyd/{port}',
        '--port', str(port),
        '--interface', '127.0.0.1',
        'docker', 'exec', '-it', container, shell
    ]
    process = subprocess.Popen(ttyd_cmd)
    
    # Stocker l'information
    ttyd_instances[container] = {"port": port, "process": process}
    
    # Laisser un court instant à ttyd pour démarrer avant d'y accéder (optionnel mais recommandé)
    time.sleep(0.5)
    return port
    
@app.route('/exec/<container>')
def open_terminal(container):
    """Ouvre une console web vers un conteneur Docker grâce à ttyd en mode conteneurisé"""
    shell = get_shell(container)
    if not shell:
        return f"Aucun shell interactif trouvé dans le conteneur {container}", 500

    try:
        port = start_terminal(container, shell)
        # Nginx route automatiquement /ttyd/<port>/ vers 127.0.0.1:<port>
        return redirect(f"/ttyd/{port}/")
    except Exception as e:
        return f"Erreur lors de l'ouverture du terminal pour {container} : {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
