'''
# install fastapi

pip install fastapi

# install uvicorn
pip install uvicorn

#lancer le server
uvicorn main:app –reload
# intallation de package de gestion de base de données
pip install fastapi[all] sqlalchemy psycopg2-binary
'''


from fastapi import (FastAPI,UploadFile, File,Form, Depends,Request,HTTPException,Query)
from typing import Union,List, Optional
from fastapi.responses import (HTMLResponse, StreamingResponse, RedirectResponse)
from sqlalchemy.orm import Session
from schemas.database import get_db,engine, SessionLocal
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from schemas import schemas, utils
from schemas.utils import safe_json_response
import pandas as pd
import  os
from datetime import datetime, date
from calendar import month_name
from schemas import models
from sqlalchemy import and_, or_, func, extract, case
from datetime import timedelta
import io
import jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas.models import User

"********************* Creation de l'Api *************************************"

app = FastAPI()

# Configuration de sécurité
SECRET_KEY = os.getenv("SECRET_KEY","votre_clé_secrète_très_longue_et_complexe_ici_2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration de la sécurité pour l'authentification
security = HTTPBearer()

# Monter le dossier "static" pour les fichiers CSS, JS, images...
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dossier pour les fichiers HTML (Jinja2)
templates = Jinja2Templates(directory="templates")

# Créer les dossiers nécessaires
os.makedirs("data_nettoyee", exist_ok=True)
os.makedirs("logs", exist_ok=True)

donnees_corrigees_df = None
rapport = {}
iscriteres=False
nbErreur = 0

# Creer toute les
models.Base.metadata.create_all(bind=engine)

# ==================== SYSTÈME DE RÔLES ET PERMISSIONS ====================

# Fonction alternative pour l'authentification avec gestion des rôles via token en paramètre
async def get_authenticated_user_from_token(request: Request, db: Session = Depends(get_db)):
    """Récupère l'utilisateur authentifié à partir du token dans les paramètres ou headers"""
    # Essayer d'abord le header Authorization
    auth_header = request.headers.get("Authorization")
    token = None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        # Essayer le token dans les paramètres de requête
        token = request.query_params.get("token")
    
    if not token:
        # Pour la navigation directe, rediriger vers la page de login
        raise HTTPException(status_code=401, detail="Token d'authentification requis")
    
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    
    return user

async def get_admin_user_from_token(request: Request, db: Session = Depends(get_db)):
    """Récupère l'utilisateur admin à partir du token dans les paramètres ou headers"""
    user = await get_authenticated_user_from_token(request, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return user

async def get_analyst_user_from_token(request: Request, db: Session = Depends(get_db)):
    """Récupère l'utilisateur analyst ou admin à partir du token"""
    user = await get_authenticated_user_from_token(request, db)
    if user.role not in ["analyst", "admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux analystes et administrateurs")
    return user

async def get_authority_user_from_token(request: Request, db: Session = Depends(get_db)):
    """Récupère l'utilisateur authority, analyst ou admin à partir du token"""
    user = await get_authenticated_user_from_token(request, db)
    if user.role not in ["authority", "analyst", "admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux autorités, analystes et administrateurs")
    return user

# Fonctions simplifiées pour la navigation directe (sans token requis)
async def get_authenticated_user_optional(request: Request, db: Session = Depends(get_db)):
    """Récupère l'utilisateur authentifié de manière optionnelle pour la navigation"""
    try:
        return await get_authenticated_user_from_token(request, db)
    except HTTPException:
        return None

async def get_authority_user_optional(request: Request, db: Session = Depends(get_db)):
    """Récupère l'utilisateur authority de manière optionnelle pour la navigation"""
    try:
        return await get_authority_user_from_token(request, db)
    except HTTPException:
        return None

async def get_analyst_user_optional(request: Request, db: Session = Depends(get_db)):
    """Récupère l'utilisateur analyst de manière optionnelle pour la navigation"""
    try:
        return await get_analyst_user_from_token(request, db)
    except HTTPException:
        return None



"======================================================================================="
" ******************* Section Authentification ********************************* "

# Fonctions utilitaires pour l'authentification
def verify_password(plain_password, hashed_password):
    """Vérifie si le mot de passe correspond au hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Génère un hash du mot de passe"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token d'accès JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Vérifie et décode un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Récupère l'utilisateur actuel à partir du token"""
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    
    return user

# Role-based access control functions
def admin_required(current_user: models.User = Depends(get_current_user)):
    """Vérifie que l'utilisateur a le rôle admin"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return current_user

def analyst_required(current_user: models.User = Depends(get_current_user)):
    """Vérifie que l'utilisateur a le rôle analyst ou admin"""
    if current_user.role not in ["analyst", "admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux analystes et administrateurs")
    return current_user

def authority_required(current_user: models.User = Depends(get_current_user)):
    """Vérifie que l'utilisateur a le rôle authority, analyst ou admin"""
    if current_user.role not in ["authority", "analyst", "admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux autorités, analystes et administrateurs")
    return current_user

def user_required(current_user: models.User = Depends(get_current_user)):
    """Vérifie que l'utilisateur est authentifié (tous les rôles)"""
    return current_user

# Endpoints d'authentification
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Page de connexion"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Endpoint de connexion"""
    # Rechercher l'utilisateur par email
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    # Créer le token d'accès
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES if not remember else 60*24*7)  # 7 jours si "se souvenir"
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    }

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Page d'inscription"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    terms: bool = Form(False),
    newsletter: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Endpoint d'inscription"""
    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(models.User).filter(
        (models.User.email == email) | (models.User.username == username)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ou nom d'utilisateur déjà utilisé")
    
    # Vérifier les conditions d'utilisation
    if not terms:
        raise HTTPException(status_code=400, detail="Vous devez accepter les conditions d'utilisation")
    
    # Créer le nouvel utilisateur (toujours role='user')
    hashed_password = get_password_hash(password)
    db_user = models.User(
        first_name=firstName,
        last_name=lastName,
        email=email,
        username=username,
        hashed_password=hashed_password,
        role="user",
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Compte créé avec succès"}

@app.post("/logout")
async def logout():
    """Endpoint de déconnexion"""
    # En production, vous pourriez ajouter le token à une liste noire
    return {"message": "Déconnexion réussie"}

@app.get("/profile")
async def get_profile(current_user: models.User = Depends(get_current_user)):
    """Récupérer le profil de l'utilisateur connecté"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }

@app.get("/api/auth/status")
async def get_auth_status(request: Request):
    """Vérifier l'état d'authentification de l'utilisateur"""
    try:
        # Vérifier si un token est présent dans les cookies ou headers
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            if payload:
                # Récupérer les informations de l'utilisateur
                db = next(get_db())
                user = db.query(models.User).filter(models.User.username == payload.get("sub")).first()
                if user:
                    return {
                        "authenticated": True,
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "role": user.role,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "avatar": user.first_name[0].upper() if user.first_name else user.username[0].upper()
                        }
                    }
        
        return {"authenticated": False, "user": None}
    except Exception as e:
        return {"authenticated": False, "user": None, "error": str(e)}

@app.put("/profile")
async def update_profile(
    first_name: str = Form(None),
    last_name: str = Form(None),
    email: str = Form(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mettre à jour le profil de l'utilisateur"""
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name
    if email:
        # Vérifier que l'email n'est pas déjà utilisé
        existing_user = db.query(models.User).filter(
            models.User.email == email,
            models.User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        current_user.email = email
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Profil mis à jour avec succès"}

@app.post("/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Changer le mot de passe de l'utilisateur"""
    # Vérifier l'ancien mot de passe
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    
    # Mettre à jour le mot de passe
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Mot de passe modifié avec succès"}

# Endpoints pour mot de passe oublié
@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    """Page de mot de passe oublié"""
    return templates.TemplateResponse("forgot-password.html", {"request": request})

@app.post("/forgot-password")
async def forgot_password(
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """Endpoint pour demander la réinitialisation du mot de passe"""
    # Vérifier si l'utilisateur existe
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        # Pour des raisons de sécurité, on ne révèle pas si l'email existe ou non
        return {"message": "Si cet email existe dans notre base, vous recevrez un lien de réinitialisation."}
    
    # Générer un token de réinitialisation (valide 1 heure)
    reset_token = create_access_token(
        data={"sub": user.username, "type": "password_reset"},
        expires_delta=timedelta(hours=1)
    )
    
    # En production, vous enverriez un email ici
    # Pour l'instant, on retourne le token dans la réponse
    return {
        "message": "Lien de réinitialisation envoyé",
        "reset_token": reset_token,  # À retirer en production
        "reset_url": f"/reset-password?token={reset_token}"
    }

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str = Query(None)):
    """Page de réinitialisation du mot de passe"""
    return templates.TemplateResponse("reset-password.html", {"request": request, "token": token})

@app.post("/reset-password")
async def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Endpoint pour réinitialiser le mot de passe"""
    # Vérifier le token
    payload = verify_token(token)
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(status_code=400, detail="Token de réinitialisation invalide ou expiré")
    
    username = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Utilisateur non trouvé")
    
    # Vérifier que les mots de passe correspondent
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Les mots de passe ne correspondent pas")
    
    # Mettre à jour le mot de passe
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Mot de passe réinitialisé avec succès"}

# Middleware pour protéger les routes
def require_auth(func):
    """Décorateur pour protéger les routes"""
    async def wrapper(*args, **kwargs):
        # Ici vous pouvez ajouter la logique de vérification d'authentification
        # Pour l'instant, on laisse passer
        return await func(*args, **kwargs)
    return wrapper

"======================================================================================="

" ******************* La page d'accueille ***********************************"

#Page d'accueille

@app.get("/", response_class=HTMLResponse)
async def get_accueil(request: Request, db: Session = Depends(get_db)):
    '''if not current_user:
        return templates.TemplateResponse("login.html", {"request": request})

    
    mail = current_user.email if current_user else "admin@gmail.com"
    await utils.gestion_alertes_epidemiologiques(db=db, usermail=mail)
        '''
    return templates.TemplateResponse("accueil.html", {"request": request})


"======================================================================================="
" ******************* Section Cas de Dengue ********************************* "
"                       ********* Ajout des données dans la base ********            "

# Requete de mise à jour (ajout de cas  de dengue ) : plusieurs à la fois en format json
# l'endpoint pour ajouter plusieurs cas de dengue
@app.post("/add-listCasDengue-json/")
def ajouter_cas_dengue(cas_list: List[schemas.ValidationCasDengue], db: Session = Depends(get_db)):
    """_summary_

    Args:
        cas_list (List[centreSanteValidator]): _description_
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _type_: _description_
    """
    # Liste des centre de santé
    db_cas_list = [models.ModelCasDengue(**cas.model_dump()) for cas in cas_list]
    
    # inserer dans la base
    db.add_all(db_cas_list)

    # make migration
    db.commit()
    #db.refresh(db_cas_list)
    return db_cas_list

# ==================== ROUTES DE MISE À JOUR (AUTHORITY, ANALYST, ADMIN) ====================

# formulaire d'analyse de données
@app.get("/mise-a-jour-form", response_class=HTMLResponse)   
async def afficher_formulaire_analyse(request: Request, current_user: Optional[models.User] = Depends(get_analyst_user_optional)):
    """Formulaire d'analyse de données - Analyst, Admin seulement"""
    return templates.TemplateResponse("mise-a-jour-form.html",
                                       {"request": request,
                                        "current_user": current_user})

# endpoint pour traiter le fichier csv
@app.post("/analyse") # l'url de la page de traitement
async def analyser(request: Request, file: UploadFile = File(...), corriger: str = Form("true"), current_user: Optional[models.User] = Depends(get_analyst_user_optional)):
    """Analyser un fichier CSV - Analyst, Admin seulement"""
    global donnees_corrigees_df, rapport, nbErreur
    contents = await file.read()
    donnees_corrigees_df, rapport,nbErreur = utils.analyser_et_corriger_csv(contents, corriger)
    return rapport_analyse(request)



# endpoint pour afficher le rapport d'analyse
@app.get("/le-rapport", response_class=HTMLResponse)
def rapport_analyse(request: Request, current_user: Optional[models.User] = Depends(get_analyst_user_optional)):
    global rapport, nbErreur
    
    return templates.TemplateResponse("rapport-Form.html", {
        "request": request,
        "rapport": rapport,
        "corrige": 'True',
        "isRapport": True,  # si le rapport existe
        "nbErreur": nbErreur,
        "current_user": current_user
    })

# endpoint pour afficher les données corrigées
@app.get("/donnees-corrigees", response_class=HTMLResponse)
async def voir_donnees_corrigees(request: Request, current_user: Optional[models.User] = Depends(get_analyst_user_optional)):
    global donnees_corrigees_df
    if donnees_corrigees_df is not None:
    
        # Limiter l'affichage à 100 lignes pour éviter de surcharger la page
        donnees_corrigees_df = donnees_corrigees_df[1:100]  # Limiter l'affichage à 100 lignes
        colonnes = donnees_corrigees_df.columns.tolist()
        donnees = donnees_corrigees_df.values.tolist()
    else:
        colonnes = []
        donnees = []

    return templates.TemplateResponse("rapport-Form.html", {
        "request": request,
        "colonnes": colonnes,
        "donnees": donnees,
        "isRapport": False,
        "show_correction": True,  # si les données corrigées existent
        "current_user": current_user
    })

"======================================================================================="
# endpoint pour exporter le rapport d'analyse
@app.get("/export-rapport")
async def exporter_rapport(
    format: str = Query("json", enum=["json", "csv", "pdf"]),
    request: Request = None,
    current_user: Optional[models.User] = Depends(get_analyst_user_optional)
):
    """
    Endpoint pour exporter le rapport d'analyse d'erreurs.
    
    Args:
        format (str): Format d'export (json, csv, pdf)
        request (Request): Requête FastAPI
        
    Returns:
        Response: Fichier à télécharger ou JSON
    """
    global rapport
    
    if not rapport:
        return {
            "message": "Aucun rapport d'analyse disponible. Veuillez d'abord analyser un fichier.",
            "erreurs_par_colonnes": {},
            "erreurs_par_types": {},
            "resume": {}
        }
    
    try:
        # Exporter le rapport
        export_data = utils.exporter_rapport_erreurs(rapport, format)
        
        if format == "json":
            return export_data
        
        elif format == "csv":
            # Retourner le fichier CSV
            return StreamingResponse(
                io.StringIO(export_data["content"]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={export_data['filename']}"
                }
            )
        
        elif format == "pdf":
            # Retourner le fichier PDF
            return StreamingResponse(
                io.BytesIO(export_data["content"]),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={export_data['filename']}"
                }
            )
            
    except Exception as e:
        return {
            "message": f"Erreur lors de l'export: {str(e)}",
            "error": True
        }

# endpoint pour exporter les données corrigées
@app.get("/export-corrected")
async def exporter_donnees_corrigees(
    format: str = Query("csv", enum=["csv", "json", "excel"]),
    request: Request = None,
    current_user: Optional[models.User] = Depends(get_analyst_user_optional)
):
    """
    Endpoint pour exporter les données corrigées.
    
    Args:
        format (str): Format d'export (csv, json, excel)
        request (Request): Requête FastAPI
        
    Returns:
        Response: Fichier à télécharger ou JSON
    """
    global donnees_corrigees_df
    
    if donnees_corrigees_df is None or donnees_corrigees_df.empty:
        return {
            "message": "Aucune donnée corrigée disponible. Veuillez d'abord analyser un fichier.",
            "error": True
        }
    
    try:
        # Préparer le nom du fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            # Convertir en JSON
            data_json = donnees_corrigees_df.to_dict(orient="records")
            return {
                "message": "Données corrigées exportées",
                "data": data_json,
                "filename": f"donnees_corrigees_{timestamp}.json",
                "total_lignes": len(data_json)
            }
        
        elif format == "csv":
            # Convertir en CSV
            csv_buffer = io.StringIO()
            donnees_corrigees_df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            
            return StreamingResponse(
                io.StringIO(csv_content),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=donnees_corrigees_{timestamp}.csv"
                }
            )
        
        elif format == "excel":
            # Convertir en Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                donnees_corrigees_df.to_excel(writer, sheet_name='Données Corrigées', index=False)
            
            excel_buffer.seek(0)
            
            return StreamingResponse(
                io.BytesIO(excel_buffer.read()),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=donnees_corrigees_{timestamp}.xlsx"
                }
            )
            
    except Exception as e:
        return {
            "message": f"Erreur lors de l'export: {str(e)}",
            "error": True
        }

" ******************** Section Soumission des données ********************************* "

# ==================== ROUTES DE SOUMISSION DE DONNÉES (AUTHORITY, ANALYST, ADMIN) ====================

# Endpoint pour afficher le formulaire de soumission
@app.get("/formulaire-de-soumission", response_class=HTMLResponse)
def formulaire(request: Request, current_user: Optional[models.User] = Depends(get_authority_user_optional)):
    """Formulaire de soumission de données - Authority, Analyst, Admin"""
    return templates.TemplateResponse("dataSoumission-Form.html", {"request": request, "current_user": current_user})

@app.post("/submit-data-form")
def submit_data(
    corriger: str = 'True',
    username: str = Form(...),
    centre: str = Form(...),
    poste: str = Form(...),
    apikey: str = Form(...),
    periode_debut: str = Form(...),
    periode_fin: str = Form(...),
    description: str = Form(...),
    source : str = Form(...),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_analyst_user_optional)
):
    global donnees_corrigees_df, rapport


    try:
        date_debut = datetime.strptime(periode_debut, "%Y-%m-%d").date()
        date_fin = datetime.strptime(periode_fin, "%Y-%m-%d").date()
    except ValueError:
        return {"message": "Erreur dans les dates"}

    soumission = models.ModelSoumissionDonnee(
        username=username,
        centre=centre,
        poste=poste,
        apikey=apikey,
        periode_debut=date_debut,
        periode_fin=date_fin,
        date_soumission=datetime.now().date(),
        sources=source,
        description=description
    )
    db.add(soumission)
    db.commit()

    # Récupérer la dernière soumission dont la date est aujourd'hui
    id_source = (
        db.query(models.ModelSoumissionDonnee)
        .filter(models.ModelSoumissionDonnee.date_soumission == datetime.now().date())
        .order_by(models.ModelSoumissionDonnee.id.desc())
        .first()
    )

    if not id_source:
        raise HTTPException(status_code=500, detail="Erreur: Veuillez renseigner le formulaire de soumission et ressayer.")
    
    id_source = id_source.id
    # donnees_corrigees_df=None
    if donnees_corrigees_df is None:
        raise HTTPException(status_code=400, detail="Aucune donnée à insérer.")

    if corriger.lower() == "true":
        try:
            utils.inserer_donnees_csv_corrigees(df=donnees_corrigees_df,idSource=id_source, db=db)
            rapport = {}
            donnees_corrigees_df= None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'insertion des données corrigées: {str(e)}")
    
    return {"message": "Les données ont été soumises avec succès."}


"                       ********* Exporter des données de la base en csv  ********            "

"========================================================================================"

# ==================== ROUTES D'EXPORTATION (TOUS LES UTILISATEURS AUTHENTIFIÉS) ====================

# Endpoint pour afficher le formulaire d'exportation
@app.get("/exploration", response_class=HTMLResponse)
async def afficher_formulaire(request: Request, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_authenticated_user_optional)):
    """Formulaire d'exportation - Tous les utilisateurs authentifiés"""
    regions = db.query(models.ModelCasDengue.region).distinct().all()
    regions = [r[0] for r in regions]
    regions.insert(0, "Toutes")

    return templates.TemplateResponse("exploration.html", {
        "request": request,
        "donnees": None,
        "regions": regions,
        "date_debut": "",
        "date_fin": "",
        "region": "Toutes",
        "limit": 100,
        "page_size": 25,
        "page": 1,
        "iscriteres": False,
        "current_user": current_user
    })

# Endpoint pour afficher les données avant exportation
@app.post("/affichage-donnees", response_class=HTMLResponse)
async def affichage_donnees(
    request: Request,
    date_debut: str = Form(...),
    date_fin: str = Form(...),
    region: str = Form("Toutes"),
    limit: int = Form(100),
    page_size: int = Form(25),
    page: int = Form(1),
    scroll_to_table: str = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_authenticated_user_optional)
):
    errors = []
    form_data = {
        "date_debut": date_debut,
        "date_fin": date_fin,
        "region": region,
        "limit": limit,
        "page_size": page_size,
        "page": page
    }

    # ✅ Vérification du champ limit
    try:
        limit = int(limit)
        if limit <= 0:
            errors.append("La limite doit être un entier positif.")
    except ValueError:
        errors.append("La limite doit être un entier valide.")

    # ✅ Vérification du format et de l'ordre des dates
    try:
        debut = datetime.strptime(date_debut, "%Y-%m-%d")
        fin = datetime.strptime(date_fin, "%Y-%m-%d")
        if debut > fin:
            errors.append("La date de début doit être antérieure ou égale à la date de fin.")
    except ValueError:
        errors.append("Veuillez remplir les champs.")

    # ✅ Si erreurs, on retourne vers le formulaire avec les messages
    if errors:
        regions = db.query(models.ModelCasDengue.region).distinct().all()
        regions = [r[0] for r in regions]
        regions.insert(0, "Toutes")

        return templates.TemplateResponse("exploration.html", {
            "request": request,
            "errors": errors,
            "form_data": form_data,
            "colonnes": [],
            "donnees": [],
            "regions": regions,
            "iscriteres": False,
            "date_debut": date_debut,
            "date_fin": date_fin,
            "region": region,
            "limit": limit,
            "page_size": page_size,
            "page": page
        })

    # ✅ Exécution de la requête
    query = db.query(models.ModelCasDengue).filter(
        models.ModelCasDengue.date_consultation >= date_debut,
        models.ModelCasDengue.date_consultation <= date_fin
    )

    if region != "Toutes":
        query = query.filter(models.ModelCasDengue.region == region)

    # Récupérer le nombre total d'enregistrements
    total_count = query.count()
    
    # Limiter le nombre total d'enregistrements récupérés
    query = query.limit(limit)
    
    # Appliquer la pagination
    offset = (page - 1) * page_size
    donnees = query.offset(offset).limit(page_size).all()

    # Conversion des données en DataFrame
    data_dicts = [d.__dict__ for d in donnees]
    for d in data_dicts:
        d.pop('_sa_instance_state', None)

    df = pd.DataFrame(data_dicts)

    # Calculer les informations de pagination
    total_pages = min((total_count + page_size - 1) // page_size, (limit + page_size - 1) // page_size)
    start_record = offset + 1
    end_record = min(offset + page_size, total_count, limit)
    
    # Générer les liens de pagination
    pagination_links = []
    for p in range(max(1, page - 2), min(total_pages + 1, page + 3)):
        pagination_links.append({
            'page': p,
            'active': p == page,
            'disabled': False
        })
    
    # Calculer les valeurs pour la navigation
    prev_page = page - 1 if page > 1 else 1
    next_page = page + 1 if page < total_pages else total_pages

    regions = db.query(models.ModelCasDengue.region).distinct().all()
    regions = [r[0] for r in regions]
    regions.insert(0, "Toutes")

    return templates.TemplateResponse("exploration.html", {
        "request": request,
        "colonnes": df.columns.tolist(),
        "donnees": df.values.tolist(),
        "date_debut": date_debut,
        "date_fin": date_fin,
        "limit": limit,
        "page_size": page_size,
        "page": page,
        "region": region,
        "scroll_to_table": scroll_to_table,
        "iscriteres": True,
        "regions": regions,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "start_record": start_record,
            "end_record": end_record,
            "page_size": page_size,
            "links": pagination_links,
            "prev_page": prev_page,
            "next_page": next_page,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }
    })

# Endpoint pour exporter les données vers un fichier CSV
@app.post("/export-data-form")
async def exportation_form(
    format:str = Query('json', enum= ["json","csv","excel"]),
    date_debut: Optional[str] = Form(...),
    date_fin: Optional[str] = Form(...),
    region: Optional[str] = Form(...),
    districts: Optional[List[str]] = Query(None),
    limit: Optional[int] = Form(...),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_authenticated_user_optional)

):
    """_summary_
    cette fonction permet d'exporter des données filtrées en format csv ou json
    Args:
        typefile (Optional[str], optional): _description_. Defaults to Query('json', enum= ["json","csv"]).
        date_debut (Optional[str], optional): _description_. Defaults to Form(...).
        date_fin (Optional[str], optional): _description_. Defaults to Form(...).
        region (Optional[str], optional): _description_. Defaults to Form(...).
        districts (Optional[List[str]], optional): _description_. Defaults to Query(None).
        limit (Optional[int], optional): _description_. Defaults to Form(...).
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _type_: _description_
    """
    try:
        result = utils.exporter_donnees(
            format=format,
            date_debut=date_debut,
            date_fin=date_fin,
            region=region,
            districts=districts,
            limit=limit,
            db=db
        )
        return safe_json_response(result)
    except Exception as e:
        return {
            "error": "Export error",
            "message": str(e),
            "data": None
        }
   

@app.get("/export-data")
async def exportation(
    format: str = Query('json', enum=["json", "csv", "excel"]),
    date_debut: str = Query(None),
    date_fin: str = Query(None),
    region: Optional[str] = Query("Toutes"),
    districts: Optional[List[str]] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_authenticated_user_optional)
):
    """
    Cette fonction permet d'exporter des données filtrées en format CSV ou JSON.
    """
    try:
        result = utils.exporter_donnees(
            format=format,
            date_debut=date_debut,
            date_fin=date_fin,
            region=region,
            districts=districts,
            limit=limit,
            db=db
        )
        return safe_json_response(result)
    except Exception as e:
        return {
            "error": "Export error",
            "message": str(e),
            "data": None
        }
"========================================================================================"
" ******************* Section Statistiques ********************************* "


@app.get("/api/stats")
async def get_stats_api(db: Session = Depends(get_db)):
    """Endpoint pour récupérer les statistiques annuelles et hebdomadaires"""
    try:
        result = utils.get_stats(db)
        return safe_json_response(result)
    except Exception as e:
        return {
            "error": "Stats error",
            "message": str(e),
            "data": None
        }



@app.get("/api/series-hebdomadaires")
async def get_series_hebdomadaires(
    date_debut: str,
    date_fin: str,
    frequence: str = "W",
    region: str = "Toutes",
    district: str = "Toutes",
    variable: str = "issue",
    db: Session = Depends(get_db)
):
    """Endpoint pour récupérer les séries hebdomadaires"""
    try:
        result = utils.series_hebd_mensuelles(
            date_debut=date_debut,
            date_fin=date_fin,
            frequence=frequence,
            region=region,
            district=district,
            variable=variable,
            db=db
        )
        return safe_json_response(result)
    except Exception as e:
        return {
            "error": "Series hebdomadaires error",
            "message": str(e),
            "data": None
        }

" ******************* Section Alertes ********************************* "
# endpoint pour configurer les seuils d'alerte
@app.get("/api/alerts/config", response_class=HTMLResponse)
async def configurer_alerte(request: Request):
    return templates.TemplateResponse("configuration-alertes.html", {"request": request})

# Endpoint pour déclencher manuellement les alertes
@app.post("/api/alerts/verifier")
async def verifier_alertes(
    date_debut: str = Query(None),
    date_fin: str = Query(None),
    region: str = Query("Toutes"),
    district: str = Query("Toutes"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Déclenche manuellement la vérification des alertes"""
    usermail = current_user.email if current_user else "admin@gmail.com"
    try:
        
        resultat = utils.gestion_alertes_epidemiologiques(
            db, usermail, date_debut, date_fin, region, district
        )
        return {
            "success": True,
            "message": f"Vérification terminée. {resultat['alertes_generes']} alertes générées.",
            "data": resultat
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification: {str(e)}")

# Endpoint pour configurer les seuils d'un utilisateur
@app.post("/api/alerts/config/seuils")
async def configurer_seuils(
    request: Request,
    db: Session = Depends(get_db)
):
    data = await request.json()
    return utils.seuils_alertes_config(data, db)



# Endpoint pour récupérer les seuils d'un utilisateur
@app.get("/api/alerts/seuils/{usermail}")
async def recuperer_seuils(
    usermail: str,
    db: Session = Depends(get_db)
):
    """Récupère les seuils d'alerte d'un utilisateur"""
    try:
        seuils = utils.recuperer_seuils_utilisateur(db, usermail)
        return {"success": True, "data": seuils}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

# Endpoint pour la vérification automatique des alertes
@app.post("/api/alerts/verification-automatique")
async def verification_automatique(db: Session = Depends(get_db)):
    """Déclenche la vérification automatique des alertes sur toutes les régions"""
    try:
        resultat = utils.verification_automatique_alertes(db)
        return {
            "success": True,
            "message": f"Vérification automatique terminée. {resultat['total_alertes_generes']} alertes générées.",
            "data": resultat
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification automatique: {str(e)}")

# Endpoint pour obtenir les indicateurs épidémiologiques actuels
@app.get("/api/alerts/indicateurs")
async def obtenir_indicateurs_actuels(
    date_debut: Optional[datetime] = Query(None, description="Date de début pour filtrer les indicateurs"),
    date_fin: Optional[datetime] = Query(None, description="Date de fin pour filtrer les indicateurs"),
    region: str = Query("Toutes"),
    district: str = Query("Toutes"),
    db: Session = Depends(get_db)
):
    # si date_debut et date_fin sont vides, on prend la semaine en cours
    """if date_debut is None:
        date_debut = datetime.now() - timedelta(days=7)
    if date_fin is None:
        date_fin = datetime.now()"""
    #r=test
    date_debut = datetime(2025, 1, 1)
    date_fin = datetime(2025, 6, 30)
    """Récupère les indicateurs épidémiologiques actuels"""
    try:
        indicateurs = utils.calculer_indicateurs_epidemiologiques(
            db, date_debut, date_fin, region, district
        )
        return {"success": True, "data": indicateurs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul des indicateurs: {str(e)}")

# Endpoint pour afficher la page de détails des alertes
@app.get("/api/alerts/detail", response_class=HTMLResponse)
def alertes_detail(request: Request, db: Session = Depends(get_db)):
    """Affiche la page de détails des alertes"""
    # Récupérer les régions distinctes depuis la base de données
    regions = utils.recuperer_regions_distinctes(db)
    
    return templates.TemplateResponse("alertes-detail.html", {
        "request": request,
        "regions": regions
    })

# Endpoint pour afficher la page d'historique des alertes
@app.get("/api/historique-alertes", response_class=HTMLResponse)
def historique_alertes(request: Request, db: Session = Depends(get_db)):
    """Affiche la page d'historique des alertes"""
    # Récupérer les régions distinctes depuis la base de données
    regions = db.query(models.ModelCasDengue.region).distinct().all()
    regions = [r[0] for r in regions if r[0]]
    regions.insert(0, "Toutes")
    
    return templates.TemplateResponse("historique-alertes.html", {
        "request": request,
        "regions": regions
    })

# Endpoint pour marquer une alerte comme résolue
@app.put("/api/alerts/{alerte_id}/resolve")
async def marquer_alerte_resolue(
    alerte_id: int,
    db: Session = Depends(get_db)
):
    """Marque une alerte comme résolue"""
    try:
        alerte = db.query(models.AlertLog).filter(models.AlertLog.id == alerte_id).first()
        
        if not alerte:
            raise HTTPException(status_code=404, detail="Alerte non trouvée")
        
        alerte.status = "0"  # 0 = résolu, 1 = actif
        db.commit()
        
        return {"success": True, "message": "Alerte marquée comme résolue"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

# Endpoint pour exporter les alertes
@app.get("/api/alerts/logs/export")
async def exporter_alertes(
    limit: int = Query(100, description="Nombre maximum d'alertes à exporter"),
    usermail: str = Query(None, description="Email de l'utilisateur pour filtrer"),
    region: str = Query(None, description="Région pour filtrer les alertes"),
    severity: str = Query(None, description="Sévérité de l'alerte"),
    status: str = Query(None, description="Statut de l'alerte"),
    date_debut: str = Query(None, description="Date de début pour filtrer"),
    date_fin: str = Query(None, description="Date de fin pour filtrer"),
    format: str = Query("csv", description="Format d'export (csv, json, excel)"),
    db: Session = Depends(get_db)
):
    """Exporte les alertes selon les filtres spécifiés"""
    try:
        # Construire la requête de base
        query = db.query(models.AlertLog)
        
        # Appliquer les filtres
        if usermail:
            query = query.filter(models.AlertLog.usermail == usermail)
        
        if region:
            query = query.filter(models.AlertLog.region == region)
        
        if severity:
            query = query.filter(models.AlertLog.severity == severity)
        
        if status:
            query = query.filter(models.AlertLog.status == status)
        
        if date_debut:
            query = query.filter(models.AlertLog.created_at >= date_debut)
        
        if date_fin:
            query = query.filter(models.AlertLog.created_at <= date_fin)
        
        # Trier par date de création (plus récent en premier)
        query = query.order_by(models.AlertLog.created_at.desc())
        
        # Limiter le nombre de résultats
        alertes = query.limit(limit).all()
        
        # Convertir en DataFrame
        alertes_data = []
        for alerte in alertes:
            alerte_dict = {
                "ID": alerte.id,
                "Email": alerte.usermail,
                "Région": alerte.region or "Toutes",
                "District": alerte.district or "Tous",
                "Type": alerte.notification_type or "N/A",
                "Destinataire": alerte.recipient or "N/A",
                "Sévérité": alerte.severity,
                "Statut": "Actif" if alerte.status == "1" else "Résolu",
                "Message": alerte.message,
                "Date de création": alerte.created_at.isoformat() if alerte.created_at else None
            }
            alertes_data.append(alerte_dict)
        
        df = pd.DataFrame(alertes_data)
        
        # Exporter selon le format demandé
        if format.lower() == "json":
            return df.to_dict(orient="records")
        
        elif format.lower() == "csv":
            stream = io.StringIO()
            df.to_csv(stream, index=False)
            return StreamingResponse(
                iter([stream.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=alertes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
            )
        
        elif format.lower() == "excel":
            stream = io.BytesIO()
            df.to_excel(stream, index=False, engine="openpyxl")
            stream.seek(0)
            return StreamingResponse(
                stream,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=alertes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Format non supporté : choisissez 'json', 'csv' ou 'excel'")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export: {str(e)}")

# Endpoint pour obtenir les logs d'alertes
@app.get("/api/alerts/logs")
async def obtenir_logs_alertes(
    limit: int = Query(10, description="Nombre maximum d'alertes à retourner"),
    usermail: str = Query(None, description="Email de l'utilisateur pour filtrer"),
    region: str = Query(None, description="Région pour filtrer les alertes"),
    severity: str = Query(None, description="Sévérité de l'alerte (warning, critical, info)"),
    status: str = Query(None, description="Statut de l'alerte (active, resolved)"),
    date_debut: str = Query(None, description="Date de début pour filtrer"),
    date_fin: str = Query(None, description="Date de fin pour filtrer"),
    db: Session = Depends(get_db)
):
    """Obtenir les logs d'alertes avec filtres optionnels"""

    try:
        # Construire la requête de base
        query = db.query(models.AlertLog)
        
        # Appliquer les filtres
        if usermail:
            query = query.filter(models.AlertLog.usermail == usermail)
        
        if region:
            query = query.filter(models.AlertLog.region == region)
        
        if severity:
            query = query.filter(models.AlertLog.severity == severity)
        
        if status:
            query = query.filter(models.AlertLog.status == status)
        
        if date_debut:
            query = query.filter(models.AlertLog.created_at >= date_debut)
        
        if date_fin:
            query = query.filter(models.AlertLog.created_at <= date_fin)
        
        # Trier par date de création (plus récent en premier)
        query = query.order_by(models.AlertLog.created_at.desc())
        
        # Limiter le nombre de résultats
        alertes = query.limit(limit).all()
        
        # Convertir en dictionnaires
        alertes_data = []
        for alerte in alertes:
            alerte_dict = {
                "id": alerte.id,
                "usermail": alerte.usermail,
                "region": alerte.region,
                "district": alerte.district,
                "notification_type": alerte.notification_type,
                "recipient": alerte.recipient,
                #"current_value": alerte.current_value,
                "severity": alerte.severity,
                "status": alerte.status,
                "message": alerte.message,
                #"description": alerte.description,
                "created_at": alerte.created_at.isoformat() if alerte.created_at else None,
                #"updated_at": alerte.updated_at.isoformat() if alerte.updated_at else None
            }
            alertes_data.append(alerte_dict)
        
        return safe_json_response({
            "success": True,
            "data": alertes_data,
            "total": len(alertes_data),
            "limit": limit
        })
        
    except Exception as e:
        return safe_json_response({
            "success": False,
            "message": f"Erreur lors de la récupération des logs d'alertes: {str(e)}",
            "data": []
        })

    """# test
    return {
            "success": True,
            "data":[{"id":1,"usermail":"admin@gmail.com","region":"Toutes","indicator_type":"positivite","threshold_value":20,"current_value":30,"severity":"warning","status":"1","message":"","description":"","created_at":"2025-06-30T10:00:00","updated_at":None}], # test
            "total": 1, #len(alertes_data),
            "limit": 10
        }
    """
" ******************* Section Indicateurs ********************************* "




@app.get("/api/data/mensuels")
def data_mensuels(
    annee: Optional[str] = Query(None, description="Année à filtrer"),
    region: Optional[str] = Query("Toutes", description="Région à filtrer"),
    district: Optional[str] = Query("Toutes", description="District à filtrer"),
    db: Session = Depends(get_db)
):
    # Validation et conversion des paramètres
    annee_int = date.today().year
    if annee and annee != "undefined":
        try:
            annee_int = int(annee)
        except ValueError:
            annee_int = date.today().year
    
    region_str = "Toutes"
    if region and region != "undefined":
        region_str = region
    
    district_str = "Toutes"
    if district and district != "undefined":
        district_str = district
    
    return utils.mensuel_data(annee_int, region_str, district_str, db)


@app.get("/api/dashboard", response_class=HTMLResponse)
def show_dashboard(request: Request, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_authenticated_user_optional)):
    """Dashboard principal - Tous les utilisateurs authentifiés"""
    regions = db.query(models.ModelCasDengue.region).distinct().all()
    regions = [r[0] for r in regions]
    regions.insert(0, "Toutes")
    return templates.TemplateResponse("dashboard.html",
                     {"request": request,
                      "regions": regions,
                      "current_user": current_user})


@app.get("/api/data/hebdomadaires")
def data_hebdomadaires(
    region : Optional[str] = Query(None), 
    annee : Optional[str] = Query(None), 
    mois : Optional[str] = Query(None), 
    district : Optional[str] = Query(None),
    db: Session = Depends(get_db)
    ):
    
    try:
        # Conversion et validation des paramètres
        annee_int = None
        if annee and annee != "undefined":
            try:
                annee_int = int(annee)
            except ValueError:
                annee_int = None
        
        mois_int = None
        if mois and mois != "undefined":
            try:
                mois_int = int(mois)
            except ValueError:
                mois_int = None
        
        result = utils.hebdo_data(annee_int, mois_int, region, district, db)
        return safe_json_response(result)
    except Exception as e:
        return {
            "error": "Weekly data error",
            "message": str(e),
            "data": None
        }

"========================================================================================"

#Data

@app.get("/api/data")
def data(
    date_debut: str = None,
    date_fin: str = None,
    region: str = None,
    district: str = None,
    limit: int = None,
    page: int = None,
    db: Session = Depends(get_db)
):
    try:
        result = utils.data(date_debut, date_fin, region, district, limit, page, db)
        return safe_json_response(result)
    except Exception as e:
        return {
            "error": "Data retrieval error",
            "message": str(e),
            "data": None
        }


#1. 📅 Nombre total de cas (sur une période donnée)
@app.get("/indicateurs/nombre-par-issue")
def nombres_cas(
    date_debut: str, 
    date_fin: str,
    region:str = "Toutes",
    district: str = "Toutes", 
    db: Session = Depends(get_db)
):
    """_summary_

    Args:
        date_debut (str): _description_
        date_fin (str): _description_
        region (str, optional): _description_. Defaults to "Toutes".
        district (str, optional): _description_. Defaults to "Toutes".
        db (Session, optional): _description_. Defaults to Depends(get_db).
    """
    def nb(statut):

        query = db.query(models.ModelCasDengue).filter(
            and_(
                models.ModelCasDengue.date_consultation >= date_debut,
                models.ModelCasDengue.date_consultation <= date_fin,
                models.ModelCasDengue.issue == statut
            )
        )
        if district != "Toutes":
            query = query.filter(models.ModelCasDengue.district == district)

        nombre = query.filter(models.ModelCasDengue.region == region).count()\
        if region != "Toutes" else query.count()
        return nombre
    
    # statuts : Guéri / En traitement / Décédé/ inconnue
    return {
        "nbgueri":nb("Guéri"),
        "nbtraitement":nb("En traitement"),
        "nbdeces":nb("Décédé"),
        "nbinconnue":nb("Inconnue"),
        "nbtotal": nb("Inconnue")+nb("Décédé")+\
        nb("En traitement")+nb("Guéri")
        }


#2. 🕒 Nombre de cas par semaine ou mois
@app.get("/indicateurs/cas_par_periode")
def cas_par_periode(
    date_debut: str,
    date_fin: str, 
    frequence: str = 'W', 
    db: Session = Depends(get_db)
):
    """_summary_

    Args:
        date_debut (str): _description_
        date_fin (str): _description_
        frequence (str, optional): _description_. Defaults to 'W'.
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _type_: _description_
    """

    cas = db.query(models.ModelCasDengue).filter(
        and_(models.ModelCasDengue.date_consultation >= date_debut,
        models.ModelCasDengue.date_consultation <= date_fin)).all()
    
    df = pd.DataFrame([c.__dict__ for c in cas])
    df['date_consultation'] = pd.to_datetime(df['date_consultation'])
    df = df.set_index('date_consultation')
    grouped = df.resample(frequence).size() # 'W' pour semaine, 'M' pour mois
    return grouped.to_dict()


#4. ⚠️ Détection de pics ou seuils d'alerte

@app.get("/indicateurs/pics-par-district")
def detection_pics_par_district(
    date_debut: str,
    date_fin: str,
    type: str = Query("confirmé", enum=["hospitalisation" , "confirmé"]),
    seuil: int = 50,
    db: Session = Depends(get_db)
):
    # Vérification des paramètres
    if type not in ["hospitalisation", "confirmé"]:
        return {"message": "Type non valide. Choisissez entre 'hospitalisation' ou 'confirmé'."}
    
    # Requête des cas sur la période
    cas = db.query(models.ModelCasDengue)\
        .filter(models.ModelCasDengue.date_consultation >= date_debut)\
        .filter(models.ModelCasDengue.date_consultation <= date_fin)\
        
    # Filtrer par type
    if type == "hospitalisation":
        cas = cas.filter(models.ModelCasDengue.hospitalisation == "Oui")
    elif type == "confirmé":
        cas = cas.filter(models.ModelCasDengue.resultat_test == "Positif")
    
    cas = cas.all()
    # Vérification si des cas existent
    if not cas:
        return {"message": "Aucun cas trouvé dans la période sélectionnée."}

    # Conversion en DataFrame
    data = []
    for c in cas:
        d = c.__dict__.copy()
        d.pop('_sa_instance_state', None)
        data.append(d)

    df = pd.DataFrame(data)
    df['date_consultation'] = pd.to_datetime(df['date_consultation'])

    # Grouper par semaine et district
    df.set_index('date_consultation', inplace=True)
    grouped = df.groupby('district').resample('W').size().reset_index(name='nb_cas')

    # Détection des pics : nb_cas > seuil
    pics = grouped[grouped['nb_cas'] > seuil]

    # Conversion des types pour JSON
    pics['date_consultation'] = pics['date_consultation'].astype(str)
    pics['nb_cas'] = pics['nb_cas'].astype(int)

    return { 
        "seuil": seuil,
        "pics_par_district": pics.to_dict(orient='records')
    }

#5. 📊 Séries hebdomadaires et mensuelles
# Endpoint pour obtenir les indicateurs hebdomadaires
@app.get("/indicateurs/indicateurs_hebdo")
def indicateurs_hebdo(
    date_debut: str, 
    date_fin: str,
    frequence: str = "W", 
    region: str = "Toutes", 
    district: str = "Toutes",
    variable : str = "issue",
    db: Session = Depends(get_db)
):
    """_summary_

    Args:
        date_debut (str): _description_
        date_fin (str): _description_
        frequence (str, optional): _description_. Defaults to "W".
        region (str, optional): _description_. Defaults to "Toutes".
        district (str, optional): _description_. Defaults to "Toutes".
        variable (str, optional): _description_. Defaults to "issue".
        db (Session, optional): _description_. Defaults to Depends(get_db).
    """
    return utils.series_hebd_mensuelles(
        date_debut=date_debut,
        date_fin=date_fin,
        frequence=frequence,
        region=region,
        district=district,
        variable=variable,
        db=db
    )

#6. 🏥 Taux d'hospitalisation
@app.get("/indicateurs/taux-hospitalisation")
def taux_hospitalisation(
    date_debut: str,
    date_fin: str,
    region: str = Query("Toutes"),
    district: str = Query("Toutes"),
    db: Session = Depends(get_db)
):
    # Construction de la requête
    query = db.query(models.ModelCasDengue)\
        .filter(models.ModelCasDengue.date_consultation >= date_debut)\
        .filter(models.ModelCasDengue.date_consultation <= date_fin)

    if region != "Toutes":
        query = query.filter(models.ModelCasDengue.region == region)
    if district != "Toutes":
        query = query.filter(models.ModelCasDengue.district == district)

    cas = query.all()

    if not cas:
        return {"message": "Aucun cas trouvé pour les critères fournis."}

    # Préparer les données
    data = []
    for c in cas:
        d = c.__dict__.copy()
        d.pop('_sa_instance_state', None)
        data.append(d)

    df = pd.DataFrame(data)

    total_cas = len(df)
    nb_hospitalises = df[df['hospitalise'] == 'Oui'].shape[0]

    taux = (nb_hospitalises / total_cas) * 100

    return {
        "region": region or "Toutes",
        "district": district or "Tous",
        "periode": f"{date_debut} au {date_fin}",
        "total_cas": total_cas,
        "hospitalisations": nb_hospitalises,
        "taux_hospitalisation": round(taux, 2)
    }

#7. 🗺️ Répartition géographique des cas
@app.get("/indicateurs/geographiques")
def indicateurs_geographiques(
    date_debut: str,
    date_fin: str,
    niveau: str = Query("region", enum=["region", "district"]),
    Issue: str = Query("Cas", enum=["Cas", "Déces", "Cas Confirmé"]),
    serotype: str = Query("Tous", enum=["Tous", "DEN2", "DEN3"]),
    db: Session = Depends(get_db)
):
    # Vérification des paramètres
    
    if serotype not in ["DEN2", "DEN3", "Tous"]:
        return {"message": "Serotype non valide. Choisissez entre 'DEN2', 'DEN3' ou 'Tous'."}
    
    if niveau not in ["region", "district"]:
        return {"message": "Niveau non valide. Choisissez entre 'region' ou 'district'."}
    if Issue not in ["Cas", "Déces", "Cas Confirmé"]:
        return {"message": "Issue non valide. Choisissez entre 'Cas', 'Déces' ou 'Cas Confirmé'."}
    
    # Requête principale
    query = db.query(models.ModelCasDengue)\
        .filter(models.ModelCasDengue.date_consultation >= date_debut)\
        .filter(models.ModelCasDengue.date_consultation <= date_fin)
    
    # Filtrer par serotype
    if serotype == "DEN2":
        query = query.filter(models.ModelCasDengue.serotype == "DEN2")
    elif serotype == "DEN3":
        query = query.filter(models.ModelCasDengue.serotype == "DEN3")

    # Filtrer par issue
    if Issue == "Déces":
        query = query.filter(models.ModelCasDengue.issue == "Décédé")
    elif Issue == "Cas Confirmé":
        query = query.filter(models.ModelCasDengue.resultat_test == "Positif")
    
    cas = query.all()

    if not cas:
        return {"message": "Aucun cas trouvé pour la période donnée."}

    # Transformer en DataFrame
    data = []
    for c in cas:
        d = c.__dict__.copy()
        d.pop('_sa_instance_state', None)
        data.append(d)

    df = pd.DataFrame(data)

    # Vérification que le champ existe
    if niveau not in df.columns:
        return {"message": f"Champ {niveau} non trouvé dans les données."}

    # Comptage des cas par région ou district
    repartition = df[niveau].value_counts().reset_index()
    repartition.columns = [niveau, "nombre_de_cas"]

    # Identifier la région avec le plus de cas
    hotspot = repartition.iloc[0]
    zone_froide = repartition.iloc[-1]

    return {
        "periode": f"{date_debut} au {date_fin}",
        "niveau": niveau,
        "repartition": repartition.to_dict(orient="records"),
        "hotspot": {
            niveau: hotspot[niveau],
            "nombre_de_cas": int(hotspot["nombre_de_cas"])
        },
        "zone_froide": {
            niveau: zone_froide[niveau],
            "nombre_de_cas": int(zone_froide["nombre_de_cas"])
        }
    }

#8. 🏥 Taux de létalité
@app.get("/indicateurs/taux-deletalite")
def taux_deletalite(
    date_debut: str,
    date_fin: str,
    niveau: str = Query("region", enum=["region", "district"]),
    serotype: str = Query("Tous", enum=["Tous", "DEN2", "DEN3"]),
    db: Session = Depends(get_db)
):
    # Construction de la requête
    query = db.query(models.ModelCasDengue)\
        .filter(models.ModelCasDengue.date_consultation >= date_debut)\
        .filter(models.ModelCasDengue.date_consultation <= date_fin)

    if serotype not in ["DEN2", "DEN3", "Tous"]:
        return {"message": "Serotype non valide. Choisissez entre 'DEN2', 'DEN3' ou 'Tous'."}   
    if niveau not in ["region", "district"]:
        return {"message": "Niveau non valide. Choisissez entre 'region' ou 'district'."}
    
    # Filtrer par serotype
    if serotype == "DEN2":
        query = query.filter(models.ModelCasDengue.serotype == "DEN2")
    elif serotype == "DEN3":
        query = query.filter(models.ModelCasDengue.serotype == "DEN3")

    cas = query.all()

    if not cas:
        return {"message": "Aucun cas trouvé pour les critères fournis."}

    # Conversion en DataFrame
    data = [c.__dict__.copy() for c in cas]
    for d in data:
        d.pop('_sa_instance_state', None)
    df = pd.DataFrame(data)

    if niveau not in df.columns:
        return {"message": f"Le champ '{niveau}' est introuvable dans les données."}

    # Total de cas et de décès par niveau (region ou district)
    grouped = df.groupby(niveau).agg(
        total_cas=('idCas', 'count'),
        total_deces=('issue', lambda x: (x == 'Décédé').sum())
    ).reset_index()

    grouped['taux_deletalite'] = round((grouped['total_deces'] / grouped['total_cas']) * 100, 2)

    return safe_json_response({
        "niveau": niveau,
        "periode": f"{date_debut} au {date_fin}",
        "resultats": grouped.to_dict(orient="records")
    })

#9. 📈 Taux de positivité
@app.get("/indicateurs/taux-positivite")
def taux_positivite(
    date_debut: str,
    date_fin: str,
    region: str = Query(None),
    district: str = Query(None),
    db: Session = Depends(get_db)
):
    # Construction de la requête
    query = db.query(models.ModelCasDengue)\
        .filter(models.ModelCasDengue.date_consultation >= date_debut)\
        .filter(models.ModelCasDengue.date_consultation <= date_fin)

    if region:
        query = query.filter(models.ModelCasDengue.region == region)
    if district:
        query = query.filter(models.ModelCasDengue.district == district)

    cas = query.all()

    if not cas:
        return {"message": "Aucun cas trouvé pour les critères fournis."}

    # Conversion en DataFrame
    data = [c.__dict__.copy() for c in cas]
    for d in data:
        d.pop('_sa_instance_state', None)
    df = pd.DataFrame(data)

    total_cas = len(df)
    nb_positifs = df[df['resultat_test'] == 'Positif'].shape[0]

    taux = (nb_positifs / total_cas) * 100

    return {
        "region": region or "Toutes",
        "district": district or "Tous",
        "periode": f"{date_debut} au {date_fin}",
        "total_cas": total_cas,
        "cas_positifs": nb_positifs,
        "taux_positivite": round(taux, 2)
    }

#10 . 🧑‍🤝‍🧑 Indicateurs démographiques
@app.get("/indicateurs/demographiques")
def indicateurs_demographiques(
    date_debut: str,
    date_fin: str,
    region: str = Query(None),
    district: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.ModelCasDengue)\
        .filter(models.ModelCasDengue.date_consultation >= date_debut)\
        .filter(models.ModelCasDengue.date_consultation <= date_fin)
    
    if region:
        query = query.filter(models.ModelCasDengue.region == region)
    if district:
        query = query.filter(models.ModelCasDengue.district == district)

    cas = query.all()
    if not cas:
        return {"message": "Aucun cas trouvé pour les critères fournis."}

    # Préparation des données
    data = [c.__dict__.copy() for c in cas]
    for d in data:
        d.pop('_sa_instance_state', None)
    df = pd.DataFrame(data)

    total = len(df)

    # 🧑‍🤝‍🧑 Répartition par sexe
    repartition_sexe = df['sexe'].value_counts(normalize=True).mul(100).round(2).to_dict()

    # 👶🧓 Répartition par tranches d'âge
    def tranche_age(age):
        if pd.isna(age):
            return "Inconnu"
        if age < 5:
            return "0-4 ans"
        elif age < 10:
            return "5-9 ans"
        if age < 15:
            return "10-14 ans"
        elif age < 20:
            return "15-19 ans"
        elif age < 25:
            return "20-24 ans"
        elif age < 30:
            return "25-29 ans"
        elif age < 35:
            return "30-34 ans"
        elif age < 40:
            return "35-39 ans"
        elif age < 45:
            return "40-44 ans"
        elif age < 50:
            return "45-49 ans"
        else:
            return "50 ans et plus"
    # Appliquer la fonction de tranche d'âge
    
    df['tranche_age'] = df['age'].apply(tranche_age)
    repartition_age = df['tranche_age'].value_counts(normalize=True).mul(100).round(2).to_dict()

    # 📊 Taux de létalité global
    total_deces = df[df['issue'] == 'Décédé'].shape[0]
    taux_deletalite = round((total_deces / total) * 100, 2)

    return {
        "periode": f"{date_debut} au {date_fin}",
        "region": region or "Toutes",
        "district": district or "Tous",
        "total_cas": total,
        "taux_deletalite_global": taux_deletalite,
        "repartition_par_sexe": repartition_sexe,
        "repartition_par_tranches_age": repartition_age
    }


#11. 📈 Évolution épidémique
@app.get("/indicateurs/api/dashboard")
def evolution_epidemique(
    date_debut: str,
    date_fin: str,
    region: str = Query(None),
    district: str = Query(None),
    db: Session = Depends(get_db)
):
    # 1. Requête des cas filtrés
    query = db.query(models.ModelCasDengue)\
        .filter(models.ModelCasDengue.date_consultation >= date_debut)\
        .filter(models.ModelCasDengue.date_consultation <= date_fin)
    
    if region:
        query = query.filter(models.ModelCasDengue.region == region)
    if district:
        query = query.filter(models.ModelCasDengue.district == district)
    
    cas = query.all()
    
    if not cas:
        return {"message": "Aucun cas trouvé."}
    
    # 2. Conversion en DataFrame
    df = pd.DataFrame([c.__dict__ for c in cas])
    df['date_consultation'] = pd.to_datetime(df['date_consultation'])
    df = df.set_index('date_consultation')
    
    # 3. 🔁 Variation hebdomadaire
    cas_hebdo = df.resample('W').size()
    variation = cas_hebdo.pct_change().fillna(0).map(lambda x: round(x * 100, 2))
    
    # 4. 🔺 Détection de tendance
    if len(variation) >= 2:
        derniere_variation = variation.iloc[-1]
    else:
        derniere_variation = 0.0

    if derniere_variation > 10:
        tendance = "Hausse"
    elif derniere_variation < -10:
        tendance = "Baisse"
    else:
        tendance = "Stable"

    # 5. 📊 Durée moyenne entre consultation et issue
    if 'date_issue' in df.columns and df['date_issue'].notna().any():
        df['date_issue'] = pd.to_datetime(df['date_issue'], errors='coerce')
        df['duree'] = (df['date_issue'] - df.index).dt.days
        duree_moyenne = round(df['duree'].dropna().mean(), 2)
    else:
        duree_moyenne = None
    
    # 6. Retour du résultat
    return {
        "periode": f"{date_debut} au {date_fin}",
        "region": region or "Toutes",
        "district": district or "Tous",
        "variation_hebdomadaire": variation.dropna().to_dict(),
        "derniere_variation_%": round(derniere_variation, 2),
        "tendance": tendance,
        "duree_moyenne_consultation_issue": duree_moyenne
    }


#12. 📊 Série temporelle complète
@app.get("/api/time-series")
async def get_time_series(
    date_debut: str = Query(None, description="Date de début (format YYYY-MM-DD)"),
    date_fin: str = Query(None, description="Date de fin (format YYYY-MM-DD)"),
    frequence: str = Query("W", description="Fréquence des données (W: semaine, M: mois)"),
    region: str = Query(None, description="Région à filtrer"),
    district: str = Query(None, description="District à filtrer"),
    db: Session = Depends(get_db),
    #current_user: Optional[models.User] = Depends(get_authenticated_user_optional)
):
    """
    Endpoint pour récupérer les données de série temporelle.
    
    Retourne des données épidémiologiques agrégées par période (semaine ou mois)
    avec des statistiques détaillées incluant cas, décès, guérisons, etc.
    """
    try:
        # Utiliser la fonction utils pour générer les données
        result = utils.get_time_series_data(
            date_debut=date_debut,
            date_fin=date_fin,
            frequence=frequence,
            region=region,
            district=district,
            db=db
        )
        
        return safe_json_response(result)
        
    except Exception as e:
        return safe_json_response({
            "success": False,
            "message": f"Erreur lors de la récupération des données de série temporelle: {str(e)}",
            "data": [],
            "summary": {}
        })

@app.get("/dashboard/indicateurs", response_class=HTMLResponse)
def dashboard_indicateurs(
    request: Request,
    date_debut: str = Query(None),
    date_fin: str = Query(None),
    frequence: str = 'W',
    region: str = "Toutes",
    district: str = "Toutes",
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_authenticated_user_optional)
):
    result = None

    if date_debut and date_fin:
        # --- 1. Nombre par issue ---
        def nb(statut):
            query = db.query(models.ModelCasDengue).filter(
                and_(
                    models.ModelCasDengue.date_consultation >= date_debut,
                    models.ModelCasDengue.date_consultation <= date_fin,
                    models.ModelCasDengue.issue == statut
                )
            )
            if district != "Toutes":
                query = query.filter(models.ModelCasDengue.district == district)
            if region != "Toutes":
                query = query.filter(models.ModelCasDengue.region == region)
            return query.count()
        
        issues = {
            "Guéri": nb("Guéri"),
            "En traitement": nb("En traitement"),
            "Décédé": nb("Décédé"),
            "Inconnue": nb("Inconnue"),
            "Total": sum([nb(s) for s in ["Guéri", "En traitement", "Décédé", "Inconnue"]])
        }

        # --- 2. Cas par période ---
        cas = db.query(models.ModelCasDengue).filter(
            and_(
                models.ModelCasDengue.date_consultation >= date_debut,
                models.ModelCasDengue.date_consultation <= date_fin
            )
        )
        if district != "Toutes":
            cas = cas.filter(models.ModelCasDengue.district == district)
        if region != "Toutes":
            cas = cas.filter(models.ModelCasDengue.region == region)

        data = [c.__dict__ for c in cas.all()]
        df = pd.DataFrame(data)
        if not df.empty:
            df['date_consultation'] = pd.to_datetime(df['date_consultation'])
            df = df.set_index('date_consultation')
            cas_par_periode = df.resample(frequence).size().to_dict()
        else:
            cas_par_periode = {}

        result = {
            "issues": issues,
            "par_periode": cas_par_periode
        }

    return templates.TemplateResponse("indicateurs.html", {
        "request": request,
        "result": result,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "frequence": frequence,
        "region": region,
        "district": district
    })

@app.get("/dashboard/indicateurs-powerbi", response_class=HTMLResponse)
def dashboard_indicateurs_serie(request: Request):
    """ Affiche la page des indicateurs de série
    Args:
        request (Request): La requête HTTP.
    Returns:
        HTMLResponse: La réponse HTML avec le template des indicateurs de série.
    """
    return templates.TemplateResponse("page-indicateurs.html", {
        "request": request,
    })

@app.get("/configuration-alertes", response_class=HTMLResponse)
def configuration_alertes(request: Request):
    """Affiche la page de configuration des alertes"""
    return templates.TemplateResponse("configuration-alertes.html", {
        "request": request,
    })

@app.get("/page-indicateurs", response_class=HTMLResponse)
def page_indicateurs(request: Request):
    """Affiche la page d'indicateurs avec PowerBI"""
    return templates.TemplateResponse("page-indicateurs.html", {
        "request": request,
    })

@app.get("/api/regions")
def get_regions(db: Session = Depends(get_db)):
    """Récupère la liste des régions distinctes"""
    try:
        regions = utils.recuperer_regions_distinctes(db)
        return safe_json_response(regions)
    except Exception as e:
        return safe_json_response({
            "error": "Regions error",
            "message": str(e),
            "data": None
        })

@app.get("/api/districts")
def get_districts(region: str = Query(None), db: Session = Depends(get_db)):
    """Récupère la liste des districts distincts, optionnellement filtrés par région"""
    try:
        if region and region != "Toutes":
            districts = db.query(models.ModelCasDengue.district).filter(
                models.ModelCasDengue.region == region
            ).distinct().all()
        else:
            districts = db.query(models.ModelCasDengue.district).distinct().all()
        
        result = [d[0] for d in districts if d[0]]
        return safe_json_response(result)
    except Exception as e:
        return safe_json_response({
            "error": "Districts error",
            "message": str(e),
            "data": None
        })

#    la documentation

@app.get("/api/documentation", response_class=HTMLResponse)
def documentation(request: Request):
    """Affiche la page de documentation"""
    return templates.TemplateResponse("guide.html", {
        "request": request,
    })



# ==================== ROUTES ADMIN (ADMIN SEULEMENT) ====================

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request, current_user: models.User = Depends(get_admin_user_from_token)):
    """Dashboard administrateur - Admin seulement"""
    return templates.TemplateResponse("admin-dashboard.html", {"request": request, "admin": current_user})

@app.get("/admin/create-user", response_class=HTMLResponse)
async def admin_create_user_page(request: Request, current_user: models.User = Depends(get_admin_user_from_token)):
    """Page de création d'utilisateur - Admin seulement"""
    return templates.TemplateResponse("admin-create-user.html", {"request": request, "admin": current_user})

@app.post("/admin/create-user")
async def admin_create_user(
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_required)
):
    """Créer un utilisateur - Admin seulement"""
    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(models.User).filter(
        (models.User.email == email) | (models.User.username == username)
    ).first()
    if existing_user:
        return {"success": False, "message": "Email ou nom d'utilisateur déjà utilisé"}
    # Créer le nouvel utilisateur
    hashed_password = get_password_hash(password)
    db_user = models.User(
        first_name=firstName,
        last_name=lastName,
        email=email,
        username=username,
        hashed_password=hashed_password,
        role=role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"success": True, "message": "Utilisateur créé avec succès"}

# Création automatique de l'admin au démarrage
def create_admin_user(statut = " local"):
    if statut == "deploying":
    
        username = "said"
        email = "yamsaid74@gmail.com"
        mot_passe = "1122Aa"
        first_name = "Said"
        last_name = "YAMEOGO"
        role = "admin"
        is_active = True
        db: Session = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        if not user:
            hashed_password = pwd_context.hash(mot_passe)
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
            print("Utilisateur admin créé automatiquement.")
        else:
            print("L'utilisateur admin existe déjà.")
        db.close()

# Appeler la fonction au démarrage
#create_admin_user(statut = "deploying")

#create_admin_user(statut = "local")

# derniere mise à jour des données

@app.get("/api/derniere-mise-a-jour")
def get_derniere_soumission(db: Session = Depends(get_db)):
    """Retourne la date de la dernière soumission dans la base Soumission"""
    try:
        derniere = db.query(models.ModelSoumissionDonnee.date_soumission).order_by(models.ModelSoumissionDonnee.date_soumission.desc()).first()
        if derniere and derniere[0]:
            return {"statut": True, "derniere_mise_a_jour": derniere[0].isoformat()}
        else:
            return {"statut": True, "derniere_mise_a_jour": None, "message": "Aucune soumission trouvée."}
    except Exception as e:
        return {"statut": False,"message":f"Erreur lors de la récupération de la dernière soumission: {str(e)}"}
    
# la documentation du package dengsurvap-bf

@app.get("/api/documentation-dengsurvap-bf", response_class=HTMLResponse)
def documentation_dengsurvap_bf(request: Request):
    """Affiche la page de documentation du package dengsurvap-bf"""
    return templates.TemplateResponse("dengsurvap-bf-docs.html", {
        "request": request,
    })