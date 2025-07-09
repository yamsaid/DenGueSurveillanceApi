## Etape 1

 Le Procfile - Qu'est-ce que c'est ?
Définition :
Le Procfile est un fichier spécial qui indique à Railway (et autres plateformes cloud) comment démarrer votre application.
C'est comme un "mode d'emploi" pour le serveur.

#Procfile (créer ce fichier à la racine de votre projet)

# web: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT

web:                    # Type de processus (web = accessible via HTTP)
gunicorn               # Serveur WSGI pour Python
main:app               # Point d'entrée (fichier main.py, variable app)
-w 4                   # 4 workers (processus parallèles)
-k uvicorn.workers.UvicornWorker  # Type de worker (compatible FastAPI)
--bind 0.0.0.0:$PORT  # Écouter sur toutes les interfaces, port Railway

Le runtime.txt - Qu'est-ce que c'est ?
Définition :
Le runtime.txt indique à Railway quelle version de Python utiliser pour votre application.

# runtime.txt (créer ce fichier à la racine de votre projet)
python-3.12.0

#Dans votre terminal, à la racine du projet

# echo "web: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:\$PORT" > Procfile 

#Créer runtime.txt
# echo "python-3.9.18" > runtime.txt

#Ajouter gunicorn à requirements.txt
# echo "gunicorn" >> requirements.txt

#Vérifier le Procfile :
# cat Procfile

#Vérifier le runtime.txt :
# cat runtime.txt
===========================================================

 ## Etape 2

 import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Utiliser la variable d'environnement DATABASE_URL de Railway
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:yamsaid@localhost:5432/api_db")

# Si Railway fournit une URL postgres://, la convertir en postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dépendance pour récupérer la session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
===============================================================================

## Étape 3 : Configuration des Variables d'Environnement
Modification de main.py pour les variables d'environnement

## Étape 4 : Installation de Railway CLI
### Se connecter à Railway

# Option 1: Avec npm (recommandé)
npm install -g @railway/cli

# Option 2: Avec yarn
yarn global add @railway/cli

# Option 3: Avec npx (sans installation)
npx @railway/cli







