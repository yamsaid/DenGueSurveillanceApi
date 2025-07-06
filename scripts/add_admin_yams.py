import os
from sqlalchemy.orm import Session
from schemas.database import SessionLocal, engine
from schemas.models import User
from passlib.context import CryptContext

# Initialiser le contexte de hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Infos utilisateur
username = "said"
email = "yamsaid74@gmail.com"
mot_passe = "1122Aa"
first_name = "Said"
last_name = "YAMEOGO"
role = "admin"
is_active = True

# Hachage du mot de passe
hashed_password = pwd_context.hash(mot_passe)

# Créer la session
db: Session = SessionLocal()

# Vérifier si l'utilisateur existe déjà
user = db.query(User).filter(User.username == username).first()
if not user:
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        role=role,
        is_active=is_active
    )
    db.add(user)
    db.commit()
    print("Utilisateur admin créé avec succès !")
else:
    print("L'utilisateur existe déjà.")

db.close()