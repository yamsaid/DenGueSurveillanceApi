# crud.py ou utils.py
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Query
from schemas.database import get_db
from schemas import models
import pandas as pd
import numpy as np
import io
from datetime import datetime, date, timedelta
import os
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy import and_, func, or_, not_
from typing import List, Optional
from sqlalchemy.sql import case, extract
from calendar import month_name


"======== Fonction pour vérifier et corriger le CSV ========"
# Code pour analyser et corriger un fichier CSV
# Cette fonction prend le contenu du fichier CSV et le corrige
# selon les règles définies. Elle retourne le DataFrame corrigé et un rapport des corrections effectuées.
totat_erreur = 0
def analyser_et_corriger_csv(file_contents: bytes, consentement_correction = "true"):
    df = pd.read_csv(io.BytesIO(file_contents))
    rapport_global = {}
    global totat_erreur
    
    # Colonnes attendues
    colonnes = ["date_consultation","region","district","sexe","age","resultat_test","serotype","hospitalise","issue"]
    df_columns = df.columns.tolist()
    if sum([c in df_columns for c in colonnes]) != len(colonnes):
        raise HTTPException(status_code=400, detail=f"Le fichier doit contenir toutes les colonnes requises. Colonnes attendues : {colonnes}")
        
    # ==== Vérification et correction de la colonne date_consultation ====
    def normaliser_date(date_str):
        formats_possibles = [
            "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d",
            "%m/%d/%Y", "%Y.%m.%d", "%d.%m.%Y", "%Y%m%d"
        ]
        for fmt in formats_possibles:
            try:
                return datetime.strptime(str(date_str).strip(), fmt).strftime("%Y-%m-%d")
            except:
                continue
        return None

    def verifier_et_corriger_colonne_date(df, colonne="date_consultation"):
        rapport = {}
        col_data = df[colonne].astype(str)
        dates_corrigees = []
        invalides = []
        global totat_erreur

        for i, val in enumerate(col_data):
            date_corr = normaliser_date(val)
            if date_corr:
                dates_corrigees.append(date_corr)
            else:
                dates_corrigees.append(None)
                invalides.append({"index": i, "valeur": val})
        totat_erreur += len(invalides)
        rapport["valeurs_invalides"] = len(invalides)
        rapport["dates_invalides"] = invalides
        rapport["date_par_defaut"] = "1999-12-12"

        # Correction si consentement
        dates_corrigees = [d if d else "1999-12-12" for d in dates_corrigees]
        df[colonne] = pd.to_datetime(dates_corrigees)


        return rapport, df

    # ==== Vérification et correction de la colonne âge ====
    def verifier_et_corriger_colonne_age(df, colonne="age", age_min=0, age_max=120):
        rapport = {}
        col_data = df[colonne]
        col_numeric = pd.to_numeric(col_data, errors="coerce")
        global totat_erreur

        nb_manquantes = col_data.isnull().sum()
        nb_non_numeriques = col_numeric.isnull().sum() - nb_manquantes
        nb_hors_plage = ((col_numeric < age_min) | (col_numeric > age_max)).sum()

        col_corrige = col_numeric.copy()
        col_corrige[(col_corrige < age_min) | (col_corrige > age_max)] = np.nan

        age_median = int(col_corrige.median()) if not col_corrige.dropna().empty else 30

        rapport["valeurs_manquantes_initiales"] = int(nb_manquantes)
        rapport["valeurs_non_numeriques"] = int(nb_non_numeriques)
        rapport["valeurs_hors_plage"] = int(nb_hors_plage)
        rapport["valeur_utilisée_pour_correction"] = age_median
        rapport["total_valeurs_corrigées"] = int(col_corrige.isna().sum())
        totat_erreur += int(col_corrige.isna().sum())

        col_corrige.fillna(age_median, inplace=True)
        df[colonne] = col_corrige.astype(int)

        return rapport, df

    def verifier_et_corriger_resultat_test(df, colonne="issue", liste={"guéri": "Guéri", "en traitement": "En traitement","inconnue":"Inconnue","décédé":"Décédé"},consentement_correction="true",defaut="En traitement"):
        """
        Vérifie et corrige les valeurs de la colonne 'resultat_test'.
        Valeurs valides : 'Guéri', 'En traitement'.
        """
        rapport = {}
        col_data = df[colonne].astype(str)
        valeurs_corrigees = []
        invalides = []
        global totat_erreur

        valeurs_valides = liste

        for i, val in enumerate(col_data):
            val_normalise = val.strip().lower()
            if val_normalise in valeurs_valides:
                valeurs_corrigees.append(valeurs_valides[val_normalise])
            else:
                valeurs_corrigees.append(None)
                invalides.append({"index": i, "valeur": val})

        totat_erreur += len(invalides)
        rapport["valeurs_invalides"] = len(invalides)
        rapport["valeurs_invalides_detail"] = invalides
        rapport["valeur_par_defaut"] = defaut

        # Correction si consentement

        valeurs_corrigees = [
            v if v else defaut for v in valeurs_corrigees
        ]
        df[colonne] = valeurs_corrigees
        return rapport, df


    # === Appliquer les deux fonctions ===
    rapport_date, df = verifier_et_corriger_colonne_date(df)
    rapport_age, df = verifier_et_corriger_colonne_age(df)
    rapport_issue, df = verifier_et_corriger_resultat_test(df)
    rapport_test, df = verifier_et_corriger_resultat_test(df,"resultat_test",{"positif": "Positif", "négatif": "Négatif"},consentement_correction=consentement_correction,defaut="Négatif")
    rapport_serotype, df = verifier_et_corriger_resultat_test(df,"serotype",{"denv2": "DENV2", "denv3": "DENV3"},consentement_correction=consentement_correction,defaut="DENV2")
    rapport_hospitalise, df = verifier_et_corriger_resultat_test(df,"hospitalise",{"oui": "Oui", "non": "Non"},consentement_correction=consentement_correction,defaut="Non")
    rapport_sexe, df = verifier_et_corriger_resultat_test(df,"sexe",{"femme": "Femme", "homme": "Homme"},consentement_correction=consentement_correction,defaut="Homme")
    # === Créer le rapport global ===
    rapport_global["date_consultation"] = rapport_date
    rapport_global["issue"] = rapport_issue
    rapport_global["resultat_test"] = rapport_test
    rapport_global["serotype"] = rapport_serotype
    rapport_global["hospitalise"] = rapport_hospitalise
    rapport_global["age"] = rapport_age
    rapport_global["sexe"] = rapport_sexe
    
    # Ajouter les informations de la première ligne du DataFrame

    return df, rapport_global, totat_erreur
    

"""======== Fonction pour insérer les données corrigées dans la base de données ========"""
# Fonction pour insérer les données corrigées dans la base de données
# Cette fonction prend les données corrigé et l'insère dans la base de données

def inserer_donnees_csv_corrigees(df,idSource, db: Session = Depends(get_db)):
    try:
        for _, row in df.iterrows():
            nouvelle_entree = models.ModelCasDengue(
                #idCas=str(row["idCas"]),
                date_consultation=row["date_consultation"],
                region=row["region"],
                district=row["district"],
                sexe=row["sexe"],
                age=int(row["age"]),
                resultat_test=row["resultat_test"],
                serotype=row["serotype"],
                hospitalise=row["hospitalise"],
                issue=row["issue"],
                id_source = idSource
            )
            db.add(nouvelle_entree)
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(f"Erreur insertion en base : {e}")


"""======== Fonction pour exporter les données vers un fichier CSV ========"""
# Fonction pour exporter les données vers un fichier CSV



def exporter_donnees(
    format: str = Query('json', enum= ["json","csv","excel"]),
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    region: Optional[str] = 'Toutes',
    districts: Optional[List[str]] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.ModelCasDengue)

    if date_debut:
        query = query.filter(models.ModelCasDengue.date_consultation >= date_debut)
    if date_fin:
        query = query.filter(models.ModelCasDengue.date_consultation <= date_fin)

    if region != "Toutes":
        query = query.filter(models.ModelCasDengue.region == region)

    if districts:
        query = query.filter(models.ModelCasDengue.district.in_(districts))

    if limit:
        query = query.limit(limit)

    donnees = query.all()

    if not donnees:
        raise HTTPException(status_code=404, detail="Aucune donnée trouvée")

    # Convertir en DataFrame
    data = [{"id": c.idCas, "region": c.region, "date": c.date_consultation, "distric":c.district,
             "issue":c.issue, "age":c.age, "sexe":c.sexe, "serotype":c.serotype, "hospitalise":c.hospitalise,
              "test":c.resultat_test } for c in donnees]
    df = pd.DataFrame(data)

    # Exporter selon le format demandé
    if format.lower() == "json":
        return df.to_dict(orient="records")
    
    elif format.lower() == "csv":
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        return StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=dengue_cases.csv"}
        )
    
    elif format.lower() == "xlsx":
        stream = io.BytesIO()
        df.to_excel(stream, index=False, engine="openpyxl")
        stream.seek(0)
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=dengue_cases.xlsx"}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Format non supporté : choisissez 'json', 'csv' ou 'xlsx'")


""" =========== fonction pour les series hebdomadaires et mensuelles =========== """

def serie_hebdo(
    df, 
    frequence = "W", 
    filtre_colonne=None, 
    filtre_valeur=None, 
    nom_colonne='valeur'
):

    """
    Crée une série hebdomadaire à partir d'un DataFrame filtré.

    Arguments :
    - df : le DataFrame pandas (avec index = date)
    - filtre_colonne : nom de la colonne à filtrer (ex: 'issue')
    - filtre_valeur : valeur à filtrer (ex: 'Décédé')
    - frequence : fréquence de la série ('W' pour hebdomadaire, 'M' pour mensuel)
    - nom_colonne : nom de la colonne de sortie

    Retour :
    - DataFrame avec colonnes : date_consultation, nom_colonne
    """

    df_filtre = df.copy()
    if filtre_colonne and filtre_valeur:
        df_filtre = df_filtre[df_filtre[filtre_colonne] == filtre_valeur]

    grouped = df_filtre.resample(frequence).size().reset_index(name=nom_colonne)
    return grouped

def series_hebd_mensuelles(
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
    
    # Requête pour récupérer les données entre deux dates
    cas = db.query(models.ModelCasDengue).filter(
        and_(
            models.ModelCasDengue.date_consultation >= date_debut,
            models.ModelCasDengue.date_consultation <= date_fin
        )
    )
    # Filtrer par région et district si spécifié
    if region != "Toutes":
        cas = cas.filter(models.ModelCasDengue.region == region)
    
    if district != "Toutes":
            cas = cas.filter(models.ModelCasDengue.district == district)

    # Exécuter la requête
    cas = cas.all()
        
    # Convertir en DataFrame
    data_ = [c.__dict__ for c in cas]
    for d in data_:
        d.pop('_sa_instance_state', None)

    df = pd.DataFrame(data_)

    df['date_consultation'] = pd.to_datetime(df['date_consultation'])
    df = df.set_index('date_consultation')
    df_merged = df.copy()
    if variable == "issue":
        # Les serie hebdo des indicateurs par issue (deces, en traitement, guéri, inconnue)
        df_traitement = serie_hebdo(df,frequence=frequence, filtre_colonne='issue', filtre_valeur='En traitement',nom_colonne="en_traitement")
        df_gueri = serie_hebdo(df,frequence=frequence, filtre_colonne='issue', filtre_valeur='Guéri',nom_colonne="gueri")
        df_inconnue = serie_hebdo(df,frequence=frequence, filtre_colonne='issue', filtre_valeur='Inconnue',nom_colonne="inconnue")
        df_deces = serie_hebdo(df,frequence=frequence, filtre_colonne='issue', filtre_valeur='Décédé',nom_colonne="decede")

        #Fusionner les DataFrames
        df_merged = df_deces.merge(df_traitement, on='date_consultation', how='outer')\
                    .merge(df_gueri, on='date_consultation', how='outer')\
                    .merge(df_inconnue, on='date_consultation', how='outer')\
                    .fillna(0)
    elif variable == "serotype":
        # Les serie hebdo des indicateurs par serotype
        df_serotype2 = serie_hebdo(df,frequence=frequence, filtre_colonne='serotype', filtre_valeur='DENV2',nom_colonne="DENV2")
        df_serotype3 = serie_hebdo(df,frequence=frequence, filtre_colonne='serotype', filtre_valeur='DENV3',nom_colonne="DENV3")
        
        # Fusionner les DataFrames
        df_merged = df_serotype2.merge(df_serotype3, on='date_consultation', how='outer')\
                    .fillna(0)
    elif variable == "sexe":
        # Les serie hebdo des indicateurs par sexe
        df_sexe_homme = serie_hebdo(df,frequence=frequence, filtre_colonne='sexe', filtre_valeur='Homme',nom_colonne="Homme")
        df_sexe_femme = serie_hebdo(df,frequence=frequence, filtre_colonne='sexe', filtre_valeur='Femme',nom_colonne="Femme")

        # Fusionner les DataFrames
        df_merged = df_sexe_homme.merge(df_sexe_femme, on='date_consultation', how='outer')\
                    .fillna(0)
    
    return df_merged.to_dict(orient='records')


""" =========== fonction pour les statistiques de base =========== """
def statistiques_base(
    date_debut: str, 
    date_fin: str,
    region: str = "Toutes", 
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
    
    # Requête pour récupérer les données entre deux dates
    cas = db.query(models.ModelCasDengue).filter(
        and_(
            models.ModelCasDengue.date_consultation >= date_debut,
            models.ModelCasDengue.date_consultation <= date_fin
        )
    )
    
    # Filtrer par région et district si spécifié
    if region != "Toutes":
        cas = cas.filter(models.ModelCasDengue.region == region)
    
    if district != "Toutes":
            cas = cas.filter(models.ModelCasDengue.district == district)

    # Exécuter la requête
    cas = cas.all()
        
    # Convertir en DataFrame
    data_ = [c.__dict__ for c in cas]
    for d in data_:
        d.pop('_sa_instance_state', None)

    df = pd.DataFrame(data_)
    
    # Calculer les statistiques de base
    stats = {
        "total_cases": len(df),
        "total_deaths": df[df['issue'] == 'Décédé'].shape[0],
        "total_recovered": df[df['issue'] == 'Guéri'].shape[0],
        "total_treated": df[df['issue'] == 'En traitement'].shape[0],
        "average_age": df['age'].mean()
    }


def get_stats(db: Session = Depends(get_db)):
    
    today = date.today()
    #today = date(2025, 2, 1) # pour tester
    # Dates pour l'année en cours
    start_year = date(today.year, 1, 1)
    end_year = today
    # Dates pour l'année précédente
    start_last_year = date(today.year - 1, 1, 1)
    end_last_year = date(today.year - 1, today.month, today.day)

    # Semaine en cours (lundi à dimanche)
    iso_year, iso_week, iso_weekday = today.isocalendar()
    start_week = today - timedelta(days=iso_weekday - 1)
    end_week = start_week + timedelta(days=6)
    # Semaine précédente
    start_last_week = start_week - timedelta(days=7)
    end_last_week = start_week - timedelta(days=1)

    def get_period_stats(start, end):
        # Total cas
        total_cases = db.query(func.count(models.ModelCasDengue.idCas)).filter(
            models.ModelCasDengue.date_consultation >= start,
            models.ModelCasDengue.date_consultation <= end
        ).scalar() or 0

        variants = db.query(func.count(func.distinct(models.ModelCasDengue.serotype))).filter(
            models.ModelCasDengue.date_consultation >= start,
            models.ModelCasDengue.date_consultation <= end
        ).scalar() or 0

        # Décès
        total_deaths = db.query(func.count(models.ModelCasDengue.idCas)).filter(
            models.ModelCasDengue.date_consultation >= start,
            models.ModelCasDengue.date_consultation <= end,
            models.ModelCasDengue.issue == "Décédé"
        ).scalar() or 0
        # Positifs
        total_positives = db.query(func.count(models.ModelCasDengue.idCas)).filter(
            models.ModelCasDengue.date_consultation >= start,
            models.ModelCasDengue.date_consultation <= end,
            models.ModelCasDengue.resultat_test == "Positif"
        ).scalar() or 0
        # Hospitalisés
        total_hospitalized = db.query(func.count(models.ModelCasDengue.idCas)).filter(
            models.ModelCasDengue.date_consultation >= start,
            models.ModelCasDengue.date_consultation <= end,
            models.ModelCasDengue.hospitalise == "Oui"
        ).scalar() or 0
        # Région la plus touchée
        top_region_data = db.query(
            models.ModelCasDengue.region,
            func.count(models.ModelCasDengue.idCas).label("nb")
        ).filter(
            models.ModelCasDengue.date_consultation >= start,
            models.ModelCasDengue.date_consultation <= end
        ).group_by(models.ModelCasDengue.region).order_by(func.count(models.ModelCasDengue.idCas).desc())
        
        nb_top_region = top_region_data.count()
        if nb_top_region > 0:
            top_region_data = top_region_data.first()
            top_region = top_region_data[0]
            nb_cases_top_region = top_region_data[1]
        else:
            top_region = "Aucune donnée"
            nb_cases_top_region = 0

        # District le plus touché
        top_district_data = db.query(
            models.ModelCasDengue.district,
            func.count(models.ModelCasDengue.idCas).label("nb")
        ).filter(
            models.ModelCasDengue.date_consultation >= start,
            models.ModelCasDengue.date_consultation <= end
        ).group_by(models.ModelCasDengue.district).order_by(func.count(models.ModelCasDengue.idCas).desc())
        
        nb_top_district = top_district_data.count()
        if nb_top_district > 0:
            top_district_data = top_district_data.first()
            top_district = top_district_data[0]
            nb_cases_top_district = top_district_data[1]
        else:
            top_district = "Aucune donnée"
            nb_cases_top_district = 0

        
        return {
            "total_cases": total_cases,
            "total_deaths": total_deaths,
            "total_positives": total_positives,
            "total_hospitalized": total_hospitalized,
            "top_region": top_region,
            "top_district": top_district,
            "nb_top_region": nb_top_region,
            "nb_top_district": nb_top_district,
            "nb_cases_top_region": nb_cases_top_region,
            "nb_cases_top_district": nb_cases_top_district,
            "current_year": today.year,
            "variants": variants
        }

    # Stats année en cours et année précédente
    stats_year = get_period_stats(start_year, end_year)
    stats_last_year = get_period_stats(start_last_year, end_last_year)
    # Stats semaine en cours et semaine précédente
    stats_week = get_period_stats(start_week, end_week)
    stats_last_week = get_period_stats(start_last_week, end_last_week)

    def growth(current, previous):
        return round((current - previous) / max(1, previous) * 100, 2)

    return {
        "annee_en_cours": {
            **stats_year,
            "growth_cases": growth(stats_year["total_cases"], stats_last_year["total_cases"]),
            "growth_deaths": growth(stats_year["total_deaths"], stats_last_year["total_deaths"]),
            "growth_positives": growth(stats_year["total_positives"], stats_last_year["total_positives"]),
            "growth_hospitalized": growth(stats_year["total_hospitalized"], stats_last_year["total_hospitalized"]),
        },
        "semaine_en_cours": {
            **stats_week,
            "growth_cases": growth(stats_week["total_cases"], stats_last_week["total_cases"]),
            "growth_deaths": growth(stats_week["total_deaths"], stats_last_week["total_deaths"]),
            "growth_positives": growth(stats_week["total_positives"], stats_last_week["total_positives"]),
            "growth_hospitalized": growth(stats_week["total_hospitalized"], stats_last_week["total_hospitalized"]),
        }
    }

def hebdo_data(
    annee: int = date.today().year,
    mois: int = None,
    region: str = "Toutes",
    district: str = "Toutes",
    db: Session = Depends(get_db)
):
    # Validation des paramètres
    if annee is None or str(annee) == "undefined":
        annee = date.today().year
    if mois is None or str(mois) == "undefined" or mois == 0:
        mois = None
    
    # Construire la requête de base
    query = db.query(
        func.date_trunc("week", models.ModelCasDengue.date_consultation).label("semaine"),
        func.count(models.ModelCasDengue.idCas).label("cas"),
        func.sum(case((models.ModelCasDengue.issue == "Décédé", 1), else_=0)).label("deces"),
        func.sum(case((models.ModelCasDengue.hospitalise == "Oui", 1), else_=0)).label("hospitalises"),
        func.sum(case((models.ModelCasDengue.resultat_test == "Positif", 1), else_=0)).label("positifs"),
        func.extract("week", models.ModelCasDengue.date_consultation).label("num_semaine"),
        func.extract("year", models.ModelCasDengue.date_consultation).label("annee")
    )
    
    # Filtrer par année
    query = query.filter(func.extract("year", models.ModelCasDengue.date_consultation) == annee)
    
    # Filtrer par mois seulement si spécifié et valide
    if mois and mois > 0 and mois <= 12:
        query = query.filter(func.extract("month", models.ModelCasDengue.date_consultation) == mois)

    if region != "Toutes":
        query = query.filter(models.ModelCasDengue.region == region)
    if district != "Toutes":
        query = query.filter(models.ModelCasDengue.district == district)

    resultats = query.group_by("semaine", "num_semaine", "annee").order_by("semaine").all()

    return [
        {
            "annee": int(r.annee),
            "semaine": f"S{int(r.num_semaine)}",  # ex: S1, S2
            "cas": r.cas,
            "deces": r.deces,
            "hospitalises": r.hospitalises,
            "positifs": r.positifs,
        }
        for r in resultats
    ]

def mensuel_data(
    annee: int = None,
    region: str = "Toutes",
    district: str = "Toutes",
    db: Session = Depends(get_db)
):
    # Validation des paramètres
    if annee is None or str(annee) == "undefined":
        annee = date.today().year
    if region is None or str(region) == "undefined":
        region = "Toutes"
    if district is None or str(district) == "undefined":
        district = "Toutes"
    query = db.query(
        func.extract("month", models.ModelCasDengue.date_consultation).label("mois"),
        func.count(models.ModelCasDengue.idCas).label("cas"),
        func.sum(case((models.ModelCasDengue.issue == "Décédé", 1), else_=0)).label("deces"),
        func.sum(case((models.ModelCasDengue.hospitalise == "Oui", 1), else_=0)).label("hospitalises"),
        func.sum(case((models.ModelCasDengue.resultat_test == "Positif", 1), else_=0)).label("positifs"),
    ).filter(
        func.extract("year", models.ModelCasDengue.date_consultation) == annee
    )

    if region != "Toutes":
        query = query.filter(models.ModelCasDengue.region == region)
    if district != "Toutes":
        query = query.filter(models.ModelCasDengue.district == district)

    resultats = query.group_by("mois").order_by("mois").all()

    return [
        {
            "mois": month_name[int(r.mois)],  # Ex: "Janvier", "Février"
            "cas": r.cas,
            "deces": r.deces,
            "hospitalises": r.hospitalises,
            "positifs": r.positifs,
        }
        for r in resultats
    ]

"""======== Fonction pour la gestion des alertes épidémiologiques ========"""

# configuration des seuils d'alerte
def seuils_alertes_config(data: dict, db: Session = Depends(get_db)):
    """Configure les seuils d'alerte pour un utilisateur"""
    try:
        # Récupérer les données JSON du body
        #data = await request.json()
        
        # Extraire les valeurs avec des valeurs par défaut
        usermail = data.get("usermail", "admin@gmail.com")
        seuil_positivite = data.get("seuil_positivite", 10)
        seuil_hospitalisation = data.get("seuil_hospitalisation", 10)
        seuil_deces = data.get("seuil_deces", 5)
        seuil_positivite_region = data.get("seuil_positivite_region", 15)
        seuil_hospitalisation_region = data.get("seuil_hospitalisation_region", 15)
        seuil_deces_region = data.get("seuil_deces_region", 8)
        seuil_positivite_district = data.get("seuil_positivite_district", 20)
        seuil_hospitalisation_district = data.get("seuil_hospitalisation_district", 20)
        seuil_deces_district = data.get("seuil_deces_district", 10)
        intervalle = data.get("intervalle", "1")  # 1: hebdomadaire, 2: mensuel, 3: annuel
        
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
            seuils_existants.created_at = datetime.now()
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



def recuperer_seuils_utilisateur(db: Session, usermail: str) -> dict:
    """
    Récupère les seuils personnalisés d'un utilisateur ou retourne les seuils par défaut
    
    Args:
        db: Session de base de données
        usermail: Email de l'utilisateur
    
    Returns:
        dict: Dictionnaire contenant tous les seuils
    """
    # 1. Chercher les seuils personnalisés de l'utilisateur
    seuils_perso = db.query(models.SeuilAlert).filter(
        models.SeuilAlert.usermail == usermail
    ).first()
    
    # 2. Si pas de seuils personnalisés, utiliser les seuils par défaut
    if not seuils_perso:
        seuils_perso = db.query(models.SeuilAlert).filter(
            models.SeuilAlert.usermail == "admin@gmail.com"
        ).first()
        
        # Si aucun seuil par défaut n'existe, créer des seuils par défaut
        if not seuils_perso:
            seuils_perso = models.SeuilAlert(
                usermail="admin@gmail.com",
                intervalle="1",  # hebdomadaire
                seuil_positivite=10,
                seuil_hospitalisation=10,
                seuil_deces=5,
                seuil_positivite_region=15,
                seuil_hospitalisation_region=15,
                seuil_deces_region=8,
                seuil_positivite_district=20,
                seuil_hospitalisation_district=20,
                seuil_deces_district=10
            )
            db.add(seuils_perso)
            db.commit()
            db.refresh(seuils_perso)
    
    # 3. Retourner les seuils sous forme de dictionnaire
    return {
        "id": seuils_perso.id,
        "usermail": seuils_perso.usermail,
        "intervalle": seuils_perso.intervalle,
        "seuil_positivite": seuils_perso.seuil_positivite,
        "seuil_hospitalisation": seuils_perso.seuil_hospitalisation,
        "seuil_deces": seuils_perso.seuil_deces,
        "seuil_positivite_region": seuils_perso.seuil_positivite_region,
        "seuil_hospitalisation_region": seuils_perso.seuil_hospitalisation_region,
        "seuil_deces_region": seuils_perso.seuil_deces_region,
        "seuil_positivite_district": seuils_perso.seuil_positivite_district,
        "seuil_hospitalisation_district": seuils_perso.seuil_hospitalisation_district,
        "seuil_deces_district": seuils_perso.seuil_deces_district
    }

# Fonction pour calculer les indicateurs épidémiologiques 
def calculer_indicateurs_epidemiologiques(
    db: Session,
    date_debut: str,
    date_fin: str,
    region: str = "Toutes",
    district: str = "Toutes"
) -> dict:
    """
    Calcule les indicateurs épidémiologiques pour la période donnée
    
    Args:
        db: Session de base de données
        date_debut: Date de début
        date_fin: Date de fin
        region: Région à analyser
        district: District à analyser
    
    Returns:
        dict: Indicateurs calculés
    """
    
    # Construire la requête de base
    query = db.query(models.ModelCasDengue).filter(
        and_(
            models.ModelCasDengue.date_consultation >= date_debut,
            models.ModelCasDengue.date_consultation <= date_fin
        )
    )
    
    # Appliquer les filtres géographiques
    if region != "Toutes":
        query = query.filter(models.ModelCasDengue.region == region)
    if district != "Toutes":
        query = query.filter(models.ModelCasDengue.district == district)
    
    # Récupérer tous les cas
    cas = query.all()
    
    if not cas:
        return {
            "total_cas": 0,
            "cas_positifs": 0,
            "cas_hospitalises": 0,
            "cas_deces": 0,
            "taux_positivite": 0,
            "taux_hospitalisation": 0,
            "taux_deces": 0
        }
    
    # Convertir en DataFrame pour les calculs
    data = [c.__dict__ for c in cas]
    for d in data:
        d.pop('_sa_instance_state', None)
    
    df = pd.DataFrame(data)
    
    # Calculs des indicateurs
    total_cas = len(df)
    cas_positifs = df[df['resultat_test'] == 'Positif'].shape[0]
    cas_hospitalises = df[df['hospitalise'] == 'Oui'].shape[0]
    cas_deces = df[df['issue'] == 'Décédé'].shape[0]
    
    return {
        "total_cas": total_cas,
        "cas_positifs": cas_positifs,
        "cas_hospitalises": cas_hospitalises,
        "cas_deces": cas_deces,
        "taux_positivite": round((cas_positifs / total_cas) * 100, 2) if total_cas > 0 else 0,
        "taux_hospitalisation": round((cas_hospitalises / total_cas) * 100, 2) if total_cas > 0 else 0,
        "taux_deces": round((cas_deces / total_cas) * 100, 2) if total_cas > 0 else 0
    }


def verifier_seuils_alertes(
    indicateurs: dict,
    seuils: dict,
    region: str,
    district: str
) -> list:
    """
    Vérifie si les indicateurs dépassent les seuils et génère les alertes
    
    Args:
        indicateurs: Dictionnaire des indicateurs calculés
        seuils: Dictionnaire des seuils
        region: Région analysée
        district: District analysé
    
    Returns:
        list: Liste des alertes à déclencher
    """
    alertes = []
    
    # Déterminer le niveau géographique pour les seuils
    if district != "Toutes":
        niveau = "district"
    elif region != "Toutes":
        niveau = "region"
    else:
        niveau = "global"
    
    # Vérifier le taux de positivité
    if niveau == "district":
        seuil_positivite = seuils.get("seuil_positivite_district", seuils["seuil_positivite"])
    elif niveau == "region":
        seuil_positivite = seuils.get("seuil_positivite_region", seuils["seuil_positivite"])
    else:
        seuil_positivite = seuils["seuil_positivite"]
    
    if indicateurs["taux_positivite"] > seuil_positivite:
        niveau_alerte = "warning" if indicateurs["taux_positivite"] < seuil_positivite * 1.5 else "critical"
        alertes.append({
            "type": "positivite",
            "niveau": niveau_alerte,
            "message": f"Taux de positivité élevé: {indicateurs['taux_positivite']}% (seuil: {seuil_positivite}%)",
            "valeur_actuelle": indicateurs["taux_positivite"],
            "seuil": seuil_positivite
        })
    
    # Vérifier le taux d'hospitalisation
    if niveau == "district":
        seuil_hospitalisation = seuils.get("seuil_hospitalisation_district", seuils["seuil_hospitalisation"])
    elif niveau == "region":
        seuil_hospitalisation = seuils.get("seuil_hospitalisation_region", seuils["seuil_hospitalisation"])
    else:
        seuil_hospitalisation = seuils["seuil_hospitalisation"]
    
    if indicateurs["taux_hospitalisation"] > seuil_hospitalisation:
        niveau_alerte = "warning" if indicateurs["taux_hospitalisation"] < seuil_hospitalisation * 1.5 else "critical"
        alertes.append({
            "type": "hospitalisation",
            "niveau": niveau_alerte,
            "message": f"Taux d'hospitalisation élevé: {indicateurs['taux_hospitalisation']}% (seuil: {seuil_hospitalisation}%)",
            "valeur_actuelle": indicateurs["taux_hospitalisation"],
            "seuil": seuil_hospitalisation
        })
    
    # Vérifier le taux de décès
    if niveau == "district":
        seuil_deces = seuils.get("seuil_deces_district", seuils["seuil_deces"])
    elif niveau == "region":
        seuil_deces = seuils.get("seuil_deces_region", seuils["seuil_deces"])
    else:
        seuil_deces = seuils["seuil_deces"]
    
    if indicateurs["taux_deces"] > seuil_deces:
        alertes.append({
            "type": "deces",
            "niveau": "critical",  # Les décès sont toujours critiques
            "message": f"Taux de décès élevé: {indicateurs['taux_deces']}% (seuil: {seuil_deces}%)",
            "valeur_actuelle": indicateurs["taux_deces"],
            "seuil": seuil_deces
        })
    
    return alertes


def sauvegarder_alertes(
    db: Session,
    alertes: list,
    seuils: dict,
    region: str,
    district: str,
    usermail: str
) -> list:
    """
    Sauvegarde les alertes dans la base de données
    
    Args:
        db: Session de base de données
        alertes: Liste des alertes à sauvegarder
        seuils: Dictionnaire des seuils utilisés
        region: Région concernée
        district: District concerné
        usermail: Email de l'utilisateur
    
    Returns:
        list: Liste des alertes sauvegardées
    """
    alertes_sauvegardees = []
    
    for alerte in alertes:
        # Vérifier si une alerte similaire existe déjà récemment (éviter les doublons)
        alerte_existante = db.query(models.AlertLog).filter(
            and_(
                models.AlertLog.message.like(f"%{alerte['type']}%"),
                models.AlertLog.region == (region if region != "Toutes" else None),
                models.AlertLog.district == (district if district != "Toutes" else None),
                models.AlertLog.created_at >= datetime.now() - timedelta(hours=24)
            )
        ).first()
        
        if not alerte_existante:
            # Créer la nouvelle alerte
            nouvelle_alerte = models.AlertLog(
                id_seuil=seuils.get("id"),  # ID du seuil utilisé
                usermail=usermail,
                severity=alerte["niveau"],
                status="1",
                message=alerte["message"],
                region=region if region != "Toutes" else None,
                district=district if district != "Toutes" else None,
                notification_type=alerte["niveau"],
                recipient=usermail,
                created_at=datetime.now()
            )
            
            db.add(nouvelle_alerte)
            alertes_sauvegardees.append(nouvelle_alerte)
    
    if alertes_sauvegardees:
        db.commit()
    
    return alertes_sauvegardees


def gestion_alertes_epidemiologiques(
    db: Session,
    usermail: str = "admin@gmail.com",
    date_debut: str = None,
    date_fin: str = None,
    region: str = "Toutes",
    district: str = "Toutes",
    force_verification: bool = False
) -> dict:
    """
    Fonction principale de gestion des alertes épidémiologiques
    
    Args:
        db: Session de base de données
        usermail: Email de l'utilisateur pour récupérer ses seuils personnalisés
        date_debut: Date de début de la période d'analyse (format YYYY-MM-DD)
        date_fin: Date de fin de la période d'analyse (format YYYY-MM-DD)
        region: Région à analyser ("Toutes" pour toutes les régions)
        district: District à analyser ("Toutes" pour tous les districts)
        force_verification: Force la vérification même si une alerte récente existe
    
    Returns:
        dict: Résumé des alertes générées
    """
    # 1. Définir la période d'analyse si non fournie
    if not date_debut or not date_fin:
        # Utiliser la dernière semaine par défaut
        date_fin = datetime.now().date()
        date_debut = date_fin - timedelta(days=7)
        date_debut = date_debut.strftime("%Y-%m-%d")
        date_fin = date_fin.strftime("%Y-%m-%d")
    
    # 2. Récupérer les seuils de l'utilisateur
    seuils = recuperer_seuils_utilisateur(db, usermail)
    
    # 3. Calculer les indicateurs épidémiologiques
    indicateurs = calculer_indicateurs_epidemiologiques(
        db, date_debut, date_fin, region, district
    )
    
    # 4. Vérifier les seuils et générer les alertes
    alertes = verifier_seuils_alertes(indicateurs, seuils, region, district)
    
    # 5. Sauvegarder les alertes dans la base
    alertes_sauvegardees = sauvegarder_alertes(
        db, alertes, seuils, region, district, usermail
    )
    
    # 6. Préparer le résumé
    resume = {
        "periode_analyse": f"{date_debut} au {date_fin}",
        "region": region,
        "district": district,
        "utilisateur": usermail,
        "indicateurs_calcules": indicateurs,
        "seuils_utilises": {
            k: v for k, v in seuils.items() 
            if k not in ["id", "usermail", "created_at"]
        },
        "alertes_generes": len(alertes),
        "alertes_sauvegardees": len(alertes_sauvegardees),
        "details_alertes": [
            {
                "type": a["type"],
                "niveau": a["niveau"],
                "message": a["message"],
                "valeur_actuelle": a["valeur_actuelle"],
                "seuil": a["seuil"]
            }
            for a in alertes
        ]
    }
    
    return resume


def recuperer_regions_distinctes(db: Session) -> List[str]:
    """
    Récupère toutes les régions distinctes depuis la base de données
    
    Args:
        db: Session de base de données
    
    Returns:
        List[str]: Liste des régions distinctes
    """
    regions = db.query(models.ModelCasDengue.region).distinct().all()
    return [r[0] for r in regions if r[0]]


def verification_automatique_alertes(db: Session) -> dict:
    """
    Fonction pour la vérification automatique des alertes sur toutes les régions
    
    Args:
        db: Session de base de données
    
    Returns:
        dict: Résumé des vérifications effectuées
    """
    # Récupérer toutes les régions distinctes
    regions = db.query(models.ModelCasDengue.region).distinct().all()
    regions = [r[0] for r in regions if r[0]]
    
    resultats = []
    
    for region in regions:
        try:
            resultat = gestion_alertes_epidemiologiques(
                db=db,
                usermail="admin@gmail.com",
                region=region
            )
            resultats.append(resultat)
        except Exception as e:
            resultats.append({
                "region": region,
                "erreur": str(e),
                "alertes_generes": 0
            })
    
    # Vérification globale (toutes régions confondues)
    try:
        resultat_global = gestion_alertes_epidemiologiques(
            db=db,
            usermail="admin@gmail.com",
            region="Toutes"
        )
        resultats.append(resultat_global)
    except Exception as e:
        resultats.append({
            "region": "Global",
            "erreur": str(e),
            "alertes_generes": 0
        })
    
    return {
        "date_verification": datetime.now().isoformat(),
        "total_regions_verifiees": len(regions) + 1,  # +1 pour la vérification globale
        "resultats": resultats,
        "total_alertes_generes": sum(r.get("alertes_generes", 0) for r in resultats)
    }




