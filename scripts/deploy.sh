#!/bin/bash

# Script de déploiement automatisé pour Surveillance Dengue
# Usage: ./deploy.sh [local|docker|railway]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Vérification des prérequis
check_prerequisites() {
    print_header "Vérification des prérequis"
    
    # Vérifier Python
    if command -v python3 &> /dev/null; then
        print_message "Python 3 trouvé: $(python3 --version)"
    else
        print_error "Python 3 n'est pas installé"
        exit 1
    fi
    
    # Vérifier pip
    if command -v pip3 &> /dev/null; then
        print_message "pip3 trouvé"
    else
        print_error "pip3 n'est pas installé"
        exit 1
    fi
    
    # Vérifier Git
    if command -v git &> /dev/null; then
        print_message "Git trouvé: $(git --version)"
    else
        print_error "Git n'est pas installé"
        exit 1
    fi
}

# Configuration de l'environnement
setup_environment() {
    print_header "Configuration de l'environnement"
    
    # Créer l'environnement virtuel
    if [ ! -d "venv" ]; then
        print_message "Création de l'environnement virtuel..."
        python3 -m venv venv
    fi
    
    # Activer l'environnement virtuel
    source venv/bin/activate
    
    # Installer les dépendances
    print_message "Installation des dépendances..."
    pip install -r requirements.txt
    
    # Installer Gunicorn si pas présent
    pip install gunicorn uvicorn
}

# Configuration de la base de données
setup_database() {
    print_header "Configuration de la base de données"
    
    # Vérifier si PostgreSQL est installé
    if ! command -v psql &> /dev/null; then
        print_warning "PostgreSQL n'est pas installé. Installation..."
        sudo apt update
        sudo apt install -y postgresql postgresql-contrib
    fi
    
    # Démarrer PostgreSQL
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Créer la base de données et l'utilisateur
    print_message "Configuration de la base de données..."
    
    sudo -u postgres psql << EOF
CREATE DATABASE dengue_surveillance;
CREATE USER dengue_user WITH PASSWORD 'dengue_password_2024';
GRANT ALL PRIVILEGES ON DATABASE dengue_surveillance TO dengue_user;
\q
EOF
    
    print_message "Base de données configurée avec succès"
}

# Configuration des variables d'environnement
setup_env_file() {
    print_header "Configuration des variables d'environnement"
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
DATABASE_URL=postgresql://dengue_user:dengue_password_2024@localhost:5432/dengue_surveillance
SECRET_KEY=your_super_secret_key_change_this_in_production_2024
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
EOF
        print_message "Fichier .env créé"
    else
        print_warning "Fichier .env existe déjà"
    fi
}

# Configuration Gunicorn
setup_gunicorn() {
    print_header "Configuration de Gunicorn"
    
    cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
EOF
    
    print_message "Configuration Gunicorn créée"
}

# Configuration Systemd
setup_systemd() {
    print_header "Configuration du service Systemd"
    
    # Créer le répertoire de logs
    sudo mkdir -p /var/log/dengue-surveillance
    
    # Créer le service systemd
    sudo tee /etc/systemd/system/dengue-surveillance.service > /dev/null << EOF
[Unit]
Description=Dengue Surveillance FastAPI Application
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/gunicorn -c gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Démarrer le service
    sudo systemctl daemon-reload
    sudo systemctl enable dengue-surveillance
    sudo systemctl start dengue-surveillance
    
    print_message "Service Systemd configuré et démarré"
}

# Configuration Nginx
setup_nginx() {
    print_header "Configuration de Nginx"
    
    # Installer Nginx si pas présent
    if ! command -v nginx &> /dev/null; then
        print_message "Installation de Nginx..."
        sudo apt install -y nginx
    fi
    
    # Créer la configuration Nginx
    sudo tee /etc/nginx/sites-available/dengue-surveillance > /dev/null << EOF
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias $(pwd)/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Sécurité
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
EOF
    
    # Activer le site
    sudo ln -sf /etc/nginx/sites-available/dengue-surveillance /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    
    print_message "Nginx configuré"
}

# Déploiement Docker
deploy_docker() {
    print_header "Déploiement Docker"
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé"
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Créer docker-compose.yml si pas présent
    if [ ! -f "docker-compose.yml" ]; then
        cat > docker-compose.yml << EOF
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: dengue_surveillance
      POSTGRES_USER: dengue_user
      POSTGRES_PASSWORD: dengue_password_2024
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    environment:
      DATABASE_URL: postgresql://dengue_user:dengue_password_2024@db:5432/dengue_surveillance
      SECRET_KEY: your_super_secret_key_change_this_in_production_2024
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
      - ./data_nettoyee:/app/data_nettoyee

volumes:
  postgres_data:
EOF
    fi
    
    # Construire et démarrer
    docker-compose up -d --build
    
    print_message "Application déployée avec Docker"
}

# Déploiement Railway
deploy_railway() {
    print_header "Déploiement Railway"
    
    # Vérifier Railway CLI
    if ! command -v railway &> /dev/null; then
        print_message "Installation de Railway CLI..."
        npm install -g @railway/cli
    fi
    
    # Se connecter à Railway
    railway login
    
    # Initialiser le projet
    railway init
    
    # Déployer
    railway up
    
    print_message "Application déployée sur Railway"
}

# Test de l'application
test_application() {
    print_header "Test de l'application"
    
    # Attendre que l'application démarre
    sleep 5
    
    # Tester l'endpoint de santé
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_message "✅ Application accessible"
    else
        print_error "❌ Application non accessible"
        return 1
    fi
    
    # Tester la base de données
    if psql -h localhost -U dengue_user -d dengue_surveillance -c "SELECT 1;" > /dev/null 2>&1; then
        print_message "✅ Base de données accessible"
    else
        print_error "❌ Base de données non accessible"
        return 1
    fi
}

# Fonction principale
main() {
    print_header "Déploiement Surveillance Dengue"
    
    DEPLOYMENT_TYPE=${1:-local}
    
    case $DEPLOYMENT_TYPE in
        "local")
            print_message "Déploiement local sélectionné"
            check_prerequisites
            setup_environment
            setup_database
            setup_env_file
            setup_gunicorn
            setup_systemd
            setup_nginx
            test_application
            ;;
        "docker")
            print_message "Déploiement Docker sélectionné"
            deploy_docker
            test_application
            ;;
        "railway")
            print_message "Déploiement Railway sélectionné"
            deploy_railway
            ;;
        *)
            print_error "Type de déploiement invalide. Utilisez: local, docker, ou railway"
            exit 1
            ;;
    esac
    
    print_header "Déploiement terminé"
    print_message "Votre application est accessible sur:"
    print_message "  - Local: http://localhost"
    print_message "  - API: http://localhost:8000"
    print_message "  - Health: http://localhost:8000/health"
}

# Exécution du script
main "$@" 