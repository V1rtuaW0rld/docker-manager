from flask import Flask, jsonify, request, render_template, send_file, send_from_directory, Response, redirect, url_for
from PIL import Image
import os
import subprocess
import socket
import re
import sys

app = Flask(__name__, static_folder='static')

# Répertoire où sont stockés les projets Docker Compose
DOCKER_PROJECTS_PATH = os.getenv("DOCKER_PROJECTS_PATH", "/root/projects-docker-compose")

from concurrent.futures import ThreadPoolExecutor

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """Lister les projets Docker Compose (avec parallélisation du statut)"""
    
    # 🔍 Lister les dossiers valides contenant un docker-compose.yml
    project_dirs = sorted([
        item for item in os.listdir(DOCKER_PROJECTS_PATH)
        if os.path.isdir(os.path.join(DOCKER_PROJECTS_PATH, item)) and
           os.path.exists(os.path.join(DOCKER_PROJECTS_PATH, item, 'docker-compose.yml'))
    ], key=str.lower)  # ⬅️ Tri alphabétique insensible à la casse

    def build_project_entry(item):
        path = os.path.join(DOCKER_PROJECTS_PATH, item)
        status = get_project_status(path)
        return {'name': item, 'status': status}

    # ⚙️ Parallélisation de la construction des entrées
    with ThreadPoolExecutor(max_workers=8) as executor:
        projects = list(executor.map(build_project_entry, project_dirs))

    return jsonify(projects)


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

@app.route('/logs/<project_name>')
def get_logs(project_name):
    """Récupérer les logs en streaming, avec gestion insensible à la casse"""
    
    # Trouver le bon nom du conteneur
    result = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}"], capture_output=True, text=True)
    container_names = result.stdout.splitlines()
    
    real_name = next((name for name in container_names if name.lower() == project_name.lower()), None)
    
    if not real_name:
        return f"Conteneur '{project_name}' introuvable.", 404
    
    # Lancer les logs Docker en streaming
    def generate():
        log_process = subprocess.Popen(["docker", "logs", "-f", real_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        containers = [
            {"name": name}
            for name in result.stdout.strip().split("\n")
            if project_name.lower() in name.lower()
        ]
        return containers

    except subprocess.CalledProcessError as e:
        print(f"Erreur Docker : {e.stderr}")
        return []

@app.route('/api/projects/<project_name>/containers')
def get_project_containers(project_name):
    containers = get_containers_for_project(project_name)
    return jsonify(containers)

@app.route('/')
def index():
    return render_template('index.html')


def cleanup_ttyd():
    try:
        subprocess.run(['pkill', '-f', 'ttyd'], check=False)
        print("✅ Processus ttyd existants nettoyés")
    except Exception as e:
        print(f"⚠️ Erreur lors du nettoyage des processus ttyd : {e}")

def get_free_port(start_port=30000, end_port=40000):
    for port in range(start_port, end_port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', port))
            s.close()
            print(f"✅ Port libre trouvé : {port}")
            return port
        except OSError as e:
            print(f"⚠️ Port {port} non disponible : {e}")
            continue
    raise RuntimeError("Aucun port libre trouvé dans la plage")


def get_server_ip():
    """Renvoie l’IP réelle de la machine hôte"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        print(f"IP détectée dans get_server_ip : {ip}")
        sys.stdout.flush()
        return ip
    finally:
        s.close()

def get_shell(container_name):
    """Détecte le shell disponible dans le conteneur Docker"""
    for shell_cmd in ['bash', 'sh']:
        try:
            subprocess.run(
                ['docker', 'exec', container_name, shell_cmd, '-c', 'exit'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return shell_cmd
        except subprocess.CalledProcessError:
            continue
    return None  # Aucun shell disponible

import os
import subprocess

def register_nginx_proxy(container, ttyd_port):
    template_path = "/etc/nginx/templates/ttyd.conf"
    conf_path = "/etc/nginx/conf.d/ttyd.conf"

    try:
        with open(template_path, "r") as f:
            template = f.read()
        print(f"✅ Template lu : {template_path}")
    except Exception as e:
        print(f"❌ Erreur : template Nginx non trouvé : {e}")
        return f"Template introuvable à {template_path}", 500

    existing_conf = ""
    try:
        with open(conf_path, "r") as f:
            existing_conf = f.read()
    except FileNotFoundError:
        existing_conf = """
server {
    listen 4480;
    server_name localhost;

    # Les blocs location seront ajoutés ici
}
"""

    new_location = template.replace("__CONTAINER__", container).replace("__TTYD_PORT__", str(ttyd_port))
    print(f"📝 Nouveau bloc location pour {container} sur port {ttyd_port}:\n{new_location}")

    existing_conf = re.sub(rf'location /terminal/{container} {{[^}}]*}}', '', existing_conf)
    server_end = existing_conf.rfind('}')
    new_conf = existing_conf[:server_end] + new_location + existing_conf[server_end:]

    try:
        with open(conf_path, "w") as f:
            f.write(new_conf)
        print(f"✅ Fichier écrit : {conf_path}")
    except Exception as e:
        print(f"❌ Erreur lors de l’écriture : {e}")
        return f"Erreur écriture conf Nginx : {str(e)}", 500

    check = subprocess.run(["nginx", "-t"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check.returncode != 0:
        error = check.stderr.decode()
        print(f"❌ Config Nginx invalide :\n{error}")
        return f"Erreur Nginx config :\n{error}", 500

    subprocess.run(["nginx", "-s", "reload"])
    print(f"✅ Nginx rechargé pour /terminal/{container}")
    return True



@app.route('/exec/<container>')
def open_terminal(container):
    print(f"Début de open_terminal pour {container}")
    shell = get_shell(container)
    if not shell:
        print(f"Aucun shell interactif trouvé dans {container}")
        return f"Aucun shell interactif trouvé dans le conteneur {container}", 500

    print("Nettoyage des processus ttyd")
    cleanup_ttyd()

    ttyd_port = get_free_port()
    print(f"Port ttyd trouvé : {ttyd_port}")

    ttyd_cmd = ['ttyd', '--port', str(ttyd_port), '--interface', '0.0.0.0', 'docker', 'exec', '-it', container, shell]
    print(f"Commande ttyd : {' '.join(ttyd_cmd)}")

    try:
        process = subprocess.Popen(ttyd_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"ttyd lancé avec PID {process.pid}")
    except Exception as e:
        print(f"Exception ttyd : {str(e)}")
        return f"Erreur lancement ttyd : {str(e)}", 500

    print("Enregistrement du proxy Nginx")
    result = register_nginx_proxy(container, ttyd_port)
    if result is not True:
        print(f"Erreur Nginx : {result}")
        return result

    server_ip = os.getenv("SERVER_IP", get_server_ip())
    print(f"IP détectée pour redirection : {server_ip}")
    print(f"Redirection vers http://{server_ip}:4480/terminal/{container}")
    return redirect(f"http://{server_ip}:4480/terminal/{container}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
