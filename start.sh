#!/bin/bash

# 🧱 Démarrer Nginx
echo "🔧 Lancement de Nginx..."
service nginx start

# 🐍 Démarrer Flask
echo "🚀 Lancement de Flask..."
flask run --host=127.0.0.1 --port=5050 --with-threads

