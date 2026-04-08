#!/bin/bash
# Démarrer Nginx en arrière-plan
service nginx start

# Démarrer Flask au premier plan sur le port interne 8080
export FLASK_APP=app.py
export FLASK_ENV=production
flask run --host=127.0.0.1 --port=8080 --with-threads
