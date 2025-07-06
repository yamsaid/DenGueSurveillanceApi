# 🚀 Guide de Déploiement - Surveillance Dengue

Ce guide vous accompagne pour déployer votre application FastAPI avec PostgreSQL en production.

## 📋 Prérequis

- Python 3.8+
- PostgreSQL 12+
- Git
- Serveur Linux/Windows avec accès SSH

## 🎯 Options de Déploiement

### 1. **Déploiement Local/On-Premise** (Recommandé pour débuter)
### 2. **Déploiement Cloud** (AWS, Azure, GCP)
### 3. **Déploiement Containerisé** (Docker)
### 4. **Déploiement PaaS** (Heroku, Railway, Render)

---

## 🏠 Option 1: Déploiement Local/On-Premise

### 1.1 Préparation du Serveur

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# Installation de Node.js (pour les assets si nécessaire)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 1.2 Configuration PostgreSQL

```bash
# Démarrer PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Accéder à PostgreSQL
sudo -u postgres psql

# Créer la base de données et l'utilisateur
CREATE DATABASE dengue_surveillance;
CREATE USER dengue_user WITH PASSWORD 'votre_mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE dengue_surveillance TO dengue_user;
\q
```

### 1.3 Configuration de l'Application

```bash
# Cloner votre projet
git clone <votre-repo> /opt/dengue-surveillance
cd /opt/dengue-surveillance

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env
cat > .env << EOF
DATABASE_URL=postgresql://dengue_user:votre_mot_de_passe_securise@localhost:5432/dengue_surveillance
SECRET_KEY=votre_cle_secrete_tres_longue_et_complexe
ENVIRONMENT=production
DEBUG=False
EOF
```

### 1.4 Configuration Gunicorn

```bash
# Installer Gunicorn
pip install gunicorn

# Créer le fichier de configuration Gunicorn
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
EOF
```

### 1.5 Configuration Systemd

```bash
# Créer le service systemd
sudo tee /etc/systemd/system/dengue-surveillance.service > /dev/null << EOF
[Unit]
Description=Dengue Surveillance FastAPI Application
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/dengue-surveillance
Environment=PATH=/opt/dengue-surveillance/venv/bin
ExecStart=/opt/dengue-surveillance/venv/bin/gunicorn -c gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Démarrer le service
sudo systemctl daemon-reload
sudo systemctl enable dengue-surveillance
sudo systemctl start dengue-surveillance
```

### 1.6 Configuration Nginx

```bash
# Créer la configuration Nginx
sudo tee /etc/nginx/sites-available/dengue-surveillance > /dev/null << EOF
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    # Redirection HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.com www.votre-domaine.com;

    # Certificats SSL (à configurer)
    ssl_certificate /etc/letsencrypt/live/votre-domaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre-domaine.com/privkey.pem;

    # Configuration SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Proxy vers l'application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    # Assets statiques
    location /static/ {
        alias /opt/dengue-surveillance/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Sécurité
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
EOF

# Activer le site
sudo ln -s /etc/nginx/sites-available/dengue-surveillance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ☁️ Option 2: Déploiement Cloud (AWS)

### 2.1 Préparation AWS

```bash
# Installer AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configurer AWS
aws configure
```

### 2.2 Infrastructure avec Terraform

```hcl
# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "dengue-surveillance-vpc"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "dengue_db" {
  identifier           = "dengue-surveillance-db"
  engine              = "postgres"
  engine_version      = "13.7"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  storage_type        = "gp2"
  
  db_name  = "dengue_surveillance"
  username = "dengue_user"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
}

# EC2 Instance
resource "aws_instance" "app" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.small"
  
  vpc_security_group_ids = [aws_security_group.app.id]
  subnet_id              = aws_subnet.main.id
  
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y python3 python3-pip postgresql
              
              # Cloner l'application
              git clone ${var.repo_url} /opt/dengue-surveillance
              cd /opt/dengue-surveillance
              
              # Installer les dépendances
              python3 -m venv venv
              source venv/bin/activate
              pip install -r requirements.txt
              
              # Configurer l'application
              cat > .env << EOL
              DATABASE_URL=postgresql://dengue_user:${var.db_password}@${aws_db_instance.dengue_db.endpoint}/dengue_surveillance
              SECRET_KEY=${var.secret_key}
              ENVIRONMENT=production
              EOL
              
              # Démarrer l'application
              nohup gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 &
              EOF
  
  tags = {
    Name = "dengue-surveillance-app"
  }
}
```

---

## 🐳 Option 3: Déploiement Containerisé (Docker)

### 3.1 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création de l'utilisateur non-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exposition du port
EXPOSE 8000

# Commande de démarrage
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
```

### 3.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: dengue_surveillance
      POSTGRES_USER: dengue_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - dengue-network

  app:
    build: .
    environment:
      DATABASE_URL: postgresql://dengue_user:${DB_PASSWORD}@db:5432/dengue_surveillance
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    depends_on:
      - db
    networks:
      - dengue-network
    volumes:
      - ./logs:/app/logs
      - ./data_nettoyee:/app/data_nettoyee

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    networks:
      - dengue-network

volumes:
  postgres_data:

networks:
  dengue-network:
    driver: bridge
```

### 3.3 Déploiement

```bash
# Construire et démarrer les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Arrêter les services
docker-compose down
```

---

## 🚀 Option 4: Déploiement PaaS (Railway)

### 4.1 Configuration Railway

```json
// railway.json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 4.2 Variables d'Environnement

```bash
# Dans l'interface Railway ou via CLI
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=votre_cle_secrete
ENVIRONMENT=production
DEBUG=False
```

### 4.3 Déploiement

```bash
# Installer Railway CLI
npm install -g @railway/cli

# Se connecter
railway login

# Initialiser le projet
railway init

# Déployer
railway up
```

---

## 🔧 Configuration de Production

### Variables d'Environnement

```bash
# .env.production
DATABASE_URL=postgresql://user:password@host:5432/dengue_surveillance
SECRET_KEY=votre_cle_secrete_tres_longue_et_complexe
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
CORS_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com
```

### Sécurité

```python
# main.py - Configuration de sécurité
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(title="Surveillance Dengue API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "").split(",")
)
```

### Monitoring et Logs

```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'logs/app.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
```

---

## 📊 Monitoring et Maintenance

### Health Check

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

### Backup Automatique

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup PostgreSQL
pg_dump -h localhost -U dengue_user dengue_surveillance > $BACKUP_DIR/db_backup_$DATE.sql

# Compression
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Nettoyage des anciens backups (garde 7 jours)
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete
```

### Cron Job

```bash
# Ajouter au crontab
0 2 * * * /opt/dengue-surveillance/backup.sh
```

---

## 🚨 Dépannage

### Problèmes Courants

1. **Erreur de connexion à la base de données**
   ```bash
   # Vérifier PostgreSQL
   sudo systemctl status postgresql
   
   # Tester la connexion
   psql -h localhost -U dengue_user -d dengue_surveillance
   ```

2. **Application ne démarre pas**
   ```bash
   # Vérifier les logs
   sudo journalctl -u dengue-surveillance -f
   
   # Tester manuellement
   cd /opt/dengue-surveillance
   source venv/bin/activate
   python main.py
   ```

3. **Problèmes de permissions**
   ```bash
   # Corriger les permissions
   sudo chown -R www-data:www-data /opt/dengue-surveillance
   sudo chmod -R 755 /opt/dengue-surveillance
   ```

---

## 📞 Support

Pour toute question ou problème de déploiement :

1. Vérifiez les logs : `sudo journalctl -u dengue-surveillance -f`
2. Testez la connectivité : `curl http://localhost:8000/health`
3. Vérifiez la base de données : `sudo -u postgres psql -d dengue_surveillance`

---

## 🎯 Recommandations

### Pour un Déploiement de Production

1. **Utilisez HTTPS** avec Let's Encrypt
2. **Configurez un firewall** (UFW)
3. **Mettez en place des backups** automatiques
4. **Monitorez les performances** avec Prometheus/Grafana
5. **Utilisez un CDN** pour les assets statiques
6. **Configurez des alertes** en cas de problème

### Sécurité

1. **Changez les mots de passe par défaut**
2. **Utilisez des clés SSH** au lieu des mots de passe
3. **Mettez à jour régulièrement** le système
4. **Limitez l'accès** aux ports nécessaires
5. **Utilisez des certificats SSL** valides

---

**🎉 Votre application est maintenant prête pour la production !** 