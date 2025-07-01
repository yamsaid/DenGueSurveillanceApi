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
from fastapi.responses import (HTMLResponse, StreamingResponse)
from sqlalchemy.orm import Session
from schemas.database import get_db,engine
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from schemas import schemas, utils
import pandas as pd
import  os
from datetime import datetime
from calendar import month_name
from schemas import models
from sqlalchemy import and_, or_, func, extract, case
from datetime import timedelta

"********************* Creation de l'Api *************************************"

app = FastAPI()

# Monter le dossier "static" pour les fichiers CSS, JS, images...
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dossier pour les fichiers HTML (Jinja2)
templates = Jinja2Templates(directory="templates")

os.makedirs("data_nettoyee", exist_ok=True)

donnees_corrigees_df = None
rapport = {}
iscriteres=False
nbErreur = 0

# Creer toute les
models.Base.metadata.create_all(bind=engine)

" ******************* La page d'accueille ***********************************"

#Page d'accueille

@app.get("/", response_class=HTMLResponse)
def get_accueil(request: Request):
    return templates.TemplateResponse("accueil.html", {"request": request})

#models.Base.metadata.create_all(bind=engine)

" ******************* Routes de gestions des pages HTML ***************"

@app.get("/index.html", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login.html", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register.html", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/forgot-password.html", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})

@app.get("/blank.html", response_class=HTMLResponse)
async def blank_page(request: Request):
    return templates.TemplateResponse("blank.html", {"request": request})

@app.get("/404.html", response_class=HTMLResponse)
async def E404_page(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})


"======================================================================================="
" ******************* Section Cas de Dengue ********************************* "
"                       ********* Ajout des données dans la base ********            "

# Requete de mise à jour (ajout de cas  de dengue ) : plusieurs à la fois en format json
# l'endpoint pour ajouter plusieurs cas de dengue
@app.post("/add-listCasDengue-json/")
def ajouter_cas_dengue(cas_list: List[schemas.CasDengueValidator], db: Session = Depends(get_db)):
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

# formulaire d'analyse de données
@app.get("/mise-a-jour-form", response_class=HTMLResponse)   
async def afficher_formulaire_analyse(request: Request):
            
    return templates.TemplateResponse("mise-a-jour-form.html",
                                       {"request": request})

# endpoint pour traiter le fichier csv
@app.post("/analyse") # l'url de la page de traitement
async def analyser(request: Request, file: UploadFile = File(...), corriger: str = Form("true")):
    global donnees_corrigees_df, rapport, nbErreur
    contents = await file.read()
    donnees_corrigees_df, rapport,nbErreur = utils.analyser_et_corriger_csv(contents, corriger)
    return rapport_analyse(request)


# endpoint pour afficher le rapport d'analyse
@app.get("/le-rapport", response_class=HTMLResponse)
def rapport_analyse(request: Request):
    global rapport, nbErreur
    
    return templates.TemplateResponse("rapport-Form.html", {
        "request": request,
        "rapport": rapport,
        "corrige": 'True',
        "isRapport": True,  # si le rapport existe
        "nbErreur": nbErreur
    })

# endpoint pour afficher les données corrigées
@app.get("/donnees-corrigees", response_class=HTMLResponse)
async def voir_donnees_corrigees(request: Request):
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
        "show_correction": True  # si les données corrigées existent
    })


" ******************** Section Soumission des données ********************************* "

donnees = {}
# Endpoint pour afficher le formulaire de soumission
@app.get("/formulaire-de-soumission", response_class=HTMLResponse)
def formulaire(request: Request):
    return templates.TemplateResponse("dataSoumission-Form.html", {"request": request})

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
    db: Session = Depends(get_db)
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
    
    return {"message": "Les données corrigées ont été insérées avec succès."}


"                       ********* Exporter des données de la base en csv  ********            "

"========================================================================================"

# Endpoint pour afficher le formulaire d'exportation
@app.get("/exploration", response_class=HTMLResponse)
async def afficher_formulaire(request: Request, db: Session = Depends(get_db)):
    regions = db.query(models.ModelCasDengue.region).distinct().all()
    regions = [r[0] for r in regions]
    regions.insert(0, "Toutes")

    return templates.TemplateResponse("explorationForm.html", {
        "request": request,
        "donnees": None,
        "regions": regions,
    })

# Endpoint pour afficher les données avant exportation
@app.post("/affichage-donnees", response_class=HTMLResponse)
async def affichage_donnees(
    request: Request,
    date_debut: str = Form(...),
    date_fin: str = Form(...),
    region: str = Form("Toutes"),
    limit: int = Form(10),
    db: Session = Depends(get_db)
):
    errors = []
    form_data = {
        "date_debut": date_debut,
        "date_fin": date_fin,
        "region": region,
        "limit": limit
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

        return templates.TemplateResponse("explorationForm.html", {
            "request": request,
            "errors": errors,
            "form_data": form_data,
            "colonnes": [],
            "donnees": [],
            "regions": regions,
            "iscriteres": False,
        })

    # ✅ Exécution de la requête
    query = db.query(models.ModelCasDengue).filter(
        models.ModelCasDengue.date_consultation >= date_debut,
        models.ModelCasDengue.date_consultation <= date_fin
    )

    if region != "Toutes":
        query = query.filter(models.ModelCasDengue.region == region)

    donnees = query.limit(limit).all()

    # ✅ Conversion des données en DataFrame
    data_dicts = [d.__dict__ for d in donnees]
    for d in data_dicts:
        d.pop('_sa_instance_state', None)

    df = pd.DataFrame(data_dicts)

    regions = db.query(models.ModelCasDengue.region).distinct().all()
    regions = [r[0] for r in regions]
    regions.insert(0, "Toutes")

    return templates.TemplateResponse("explorationForm.html", {
        "request": request,
        "colonnes": df.columns.tolist(),
        "donnees": df.values.tolist(),
        "date_debut": date_debut,
        "date_fin": date_fin,
        "limit": limit,
        "region": region,
        "iscriteres": True,
        "regions": regions,
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
    db: Session = Depends(get_db)

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
    return utils.exporter_donnees(
        format=format,
        date_debut=date_debut,
        date_fin=date_fin,
        region=region,
        districts=districts,
        limit=limit,
        db=db
    )
   

@app.get("/export-data")
async def exportation(
    format: str = Query('json', enum=["json", "csv", "excel"]),
    date_debut: str = Query(None),
    date_fin: str = Query(None),
    region: Optional[str] = Query("Toutes"),
    districts: Optional[List[str]] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Cette fonction permet d'exporter des données filtrées en format CSV ou JSON.
    """
    return utils.exporter_donnees(
        format=format,
        date_debut=date_debut,
        date_fin=date_fin,
        region=region,
        districts=districts,
        limit=limit,
        db=db
    )
"========================================================================================"
" ******************* Section Statistiques ********************************* "


@app.get("/api/stats")
async def get_stats_api(db: Session = Depends(get_db)):
    """Endpoint pour récupérer les statistiques annuelles et hebdomadaires"""
    return utils.get_stats(db)

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
    return utils.series_hebd_mensuelles(
        date_debut=date_debut,
        date_fin=date_fin,
        frequence=frequence,
        region=region,
        district=district,
        variable=variable,
        db=db
    )

" ******************* Section Alertes ********************************* "
# endpoint pour configurer les seuils d'alerte
@app.get("/api/alerts/config", response_class=HTMLResponse)
async def configurer_alerte(request: Request):
    return templates.TemplateResponse("configuration-alertes.html", {"request": request})

# Endpoint pour déclencher manuellement les alertes
@app.post("/api/alerts/verifier")
async def verifier_alertes(
    usermail: str = Query("admin@gmail.com"),
    date_debut: str = Query(None),
    date_fin: str = Query(None),
    region: str = Query("Toutes"),
    district: str = Query("Toutes"),
    db: Session = Depends(get_db)
):
    """Déclenche manuellement la vérification des alertes"""
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
@app.post("/api/alerts/seuils")
async def configurer_seuils(
    usermail: str = Form(...),
    seuil_positivite: int = Form(10),
    seuil_hospitalisation: int = Form(10),
    seuil_deces: int = Form(5),
    seuil_positivite_region: int = Form(15),
    seuil_hospitalisation_region: int = Form(15),
    seuil_deces_region: int = Form(8),
    seuil_positivite_district: int = Form(20),
    seuil_hospitalisation_district: int = Form(20),
    seuil_deces_district: int = Form(10),
    intervalle: str = Form("1"), #-- 1: hebdomadaire, 2: mensuel, 3: annuel
    db: Session = Depends(get_db)
):
    """Configure les seuils d'alerte pour un utilisateur"""
    try:
        # Vérifier si l'utilisateur a déjà des seuils
        seuils_existants = db.query(models.SeuilAlert).filter(
            models.SeuilAlert.usermail == usermail
        ).first()
        
        if seuils_existants:
            # Mettre à jour les seuils existants
            seuils_existants.seuil_positivite = seuil_positivite
            seuils_existants.seuil_hospitalisation = seuil_hospitalisation
            seuils_existants.seuil_deces = seuil_deces
            seuils_existants.seuil_positivite_region = seuil_positivite_region
            seuils_existants.seuil_hospitalisation_region = seuil_hospitalisation_region
            seuils_existants.seuil_deces_region = seuil_deces_region
            seuils_existants.seuil_positivite_district = seuil_positivite_district
            seuils_existants.seuil_hospitalisation_district = seuil_hospitalisation_district
            seuils_existants.seuil_deces_district = seuil_deces_district
            seuils_existants.intervalle = intervalle
        else:
            # Créer de nouveaux seuils
            nouveaux_seuils = models.SeuilAlert(
                usermail=usermail,
                seuil_positivite=seuil_positivite,
                seuil_hospitalisation=seuil_hospitalisation,
                seuil_deces=seuil_deces,
                seuil_positivite_region=seuil_positivite_region,
                seuil_hospitalisation_region=seuil_hospitalisation_region,
                seuil_deces_region=seuil_deces_region,
                seuil_positivite_district=seuil_positivite_district,
                seuil_hospitalisation_district=seuil_hospitalisation_district,
                seuil_deces_district=seuil_deces_district,
                intervalle=intervalle
            )
            db.add(nouveaux_seuils)
        
        db.commit()
        return {"success": True, "message": "Seuils configurés avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la configuration: {str(e)}")

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
    date_debut: str = Query(None),
    date_fin: str = Query(None),
    region: str = Query("Toutes"),
    district: str = Query("Toutes"),
    db: Session = Depends(get_db)
):
    """Récupère les indicateurs épidémiologiques actuels"""
    try:
        indicateurs = utils.calculer_indicateurs_epidemiologiques(
            db, date_debut, date_fin, region, district
        )
        return {"success": True, "data": indicateurs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul des indicateurs: {str(e)}")

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
    """
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
                "indicator_type": alerte.indicator_type,
                "threshold_value": alerte.threshold_value,
                "current_value": alerte.current_value,
                "severity": alerte.severity,
                "status": alerte.status,
                "message": alerte.message,
                "description": alerte.description,
                "created_at": alerte.created_at.isoformat() if alerte.created_at else None,
                "updated_at": alerte.updated_at.isoformat() if alerte.updated_at else None
            }
            alertes_data.append(alerte_dict)
        
        return {
            "success": True,
            #"data": alertes_data,
            "data":[{"id":1,"usermail":"admin@gmail.com","region":"Toutes","indicator_type":"positivite","threshold_value":20,"current_value":30,"severity":"warning","status":"1","message":"","description":"","created_at":"2025-06-30T10:00:00","updated_at":None}], # test
            "total": 1, #len(alertes_data),
            "limit": limit
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur lors de la récupération des logs d'alertes: {str(e)}",
            "data": []
        }
  """
  # test
    return {
            "success": True,
            "data":[{"id":1,"usermail":"admin@gmail.com","region":"Toutes","indicator_type":"positivite","threshold_value":20,"current_value":30,"severity":"warning","status":"1","message":"","description":"","created_at":"2025-06-30T10:00:00","updated_at":None}], # test
            "total": 1, #len(alertes_data),
            "limit": 10
        }
" ******************* Section Indicateurs ********************************* "




@app.get("/indicateurs-mensuels")
def indicateurs_mensuels(
    annee: int = Query(datetime.now().year, description="Année à filtrer"),
    region: str = Query("Toutes", description="Région à filtrer"),
    db: Session = Depends(get_db)
):
    query = db.query(
        func.extract("month", models.ModelCasDengue.date_consultation).label("mois"),
        func.count(models.ModelCasDengue.idCas).label("cas"),
        func.sum(case((models.ModelCasDengue.issue == "Décédé", 1), else_=0)).label("deces"),
        func.sum(case((models.ModelCasDengue.hospitalise == "Oui", 1), else_=0)).label("hospitalises"),
    ).filter(
        func.extract("year", models.ModelCasDengue.date_consultation) == annee
    )

    if region != "Toutes":
        query = query.filter(models.ModelCasDengue.region == region)

    resultats = query.group_by("mois").order_by("mois").all()

    return [
        {
            "mois": month_name[int(r.mois)],  # Ex: "Janvier", "Février"
            "cas": r.cas,
            "deces": r.deces,
            "hospitalises": r.hospitalises,
        }
        for r in resultats
    ]


@app.get("/api/dashboard", response_class=HTMLResponse)
def show_evolution(request: Request,db: Session = Depends(get_db)):
    regions = db.query(models.ModelCasDengue.region).distinct().all()
    regions = [r[0] for r in regions]
    regions.insert(0, "Toutes")
    return templates.TemplateResponse("dashboard.html",
                     {"request": request,
                      "regions": regions})


@app.get("/indicateurs-hebdomadaires")
def indicateurs_hebdomadaires(region = None, db: Session = Depends(get_db)):
    query = db.query(
        func.date_trunc("week", models.ModelCasDengue.date_consultation).label("semaine"),
        func.count(models.ModelCasDengue.idCas).label("cas"),
        func.sum(case((models.ModelCasDengue.issue == "Décédé", 1), else_=0)).label("deces"),
        func.sum(case((models.ModelCasDengue.hospitalise == "Oui", 1), else_=0)).label("hospitalises"),
        func.extract("week", models.ModelCasDengue.date_consultation).label("num_semaine"),
        func.extract("year", models.ModelCasDengue.date_consultation).label("annee")
    )

    query = query.filter(
        func.extract("year", models.ModelCasDengue.date_consultation) == datetime.now().year
    )

    if region:
        query = query.filter(models.ModelCasDengue.region == region)

    resultats = query.group_by("semaine", "num_semaine", "annee").order_by("semaine").all()

    return [
        {
            "annee": int(r.annee),
            "semaine": f"S{int(r.num_semaine)}",  # ex: S1, S2
            "cas": r.cas,
            "deces": r.deces,
            "hospitalises": r.hospitalises,
        }
        for r in resultats
    ]

"========================================================================================"


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

    return {
        "niveau": niveau,
        "periode": f"{date_debut} au {date_fin}",
        "resultats": grouped.to_dict(orient="records")
    }

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

@app.get("/dashboard/indicateurs", response_class=HTMLResponse)
def dashboard_indicateurs(
    request: Request,
    date_debut: str = Query(None),
    date_fin: str = Query(None),
    frequence: str = 'W',
    region: str = "Toutes",
    district: str = "Toutes",
    db: Session = Depends(get_db)
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

@app.get("/alertes-detail", response_class=HTMLResponse)
def alertes_detail(request: Request):
    """Affiche la page de détails des alertes"""
    return templates.TemplateResponse("alertes-detail.html", {
        "request": request,
    })