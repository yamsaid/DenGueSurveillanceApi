from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from schemas.database import Base
from datetime import date as datime, datetime
from sqlalchemy import DateTime

# -*- coding: utf-8 -*-
"""Schemas pour les modèles de données de l'application
Ce fichier contient les définitions des modèles de données utilisés dans l'application.
Il est utilisé pour créer les tables de la base de données et pour définir les relations entre les tables.
Les modèles sont utilisés pour stocker les données de l'application et pour interagir avec la base de données.
Les modèles sont utilisés pour créer les tables de la base de données et pour définir les relations entre les tables.
"""


"========= La construction de la table ModelCasDengue ============"
# #-- La table ModelCasDengue est une table de référence pour les cas de dengue
# #-- Elle contient les informations sur les cas de dengue
### #-- Elle est utilisée pour stocker les données de dengue
class ModelCasDengue(Base):
    """_summary_

    Args:
        Base (_type_): _description_
    
    Créer la table automatiquement avec Base.metadata.create_all(bind=engine)

    Lire/écrire des données dans cette table depuis l' API

    Lier les routes FastAPI à cette table avec des CRUDs (Create, Read, Update, Delete)
    """
    __tablename__ = "tdengue2"
    
    idCas =Column(Integer, primary_key=True, index=True)
    date_consultation= Column(Date)
    region =Column(String)
    district=Column(String)
    sexe =Column(String)
    age = Column(Integer)
    resultat_test =Column(String) #-- Positif / Négatif
    serotype =Column(String)    #-- DENV2 / DENV3
    hospitalise = Column(String) #-- Oui / Non
    issue =Column(String)   #-- Guéri / En traitement / Décédé/ inconnue
    id_source = Column(Integer, ForeignKey("tsoumissions2.id"), nullable=False)

"========= La construction de la table ModelSoumissionDonnee ============"
# #-- La table ModelSoumissionDonnee est utilisée pour stocker les soumissions de données
# #-- Elle contient les informations sur les soumissions de données
class ModelSoumissionDonnee(Base):
    __tablename__ = "tsoumissions2"

    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    date_soumission = Column(Date)
    username = Column(String(255))
    centre = Column(String(255))
    poste = Column(String(255))
    apikey = Column(String(64))
    periode_debut = Column(Date)
    periode_fin = Column(Date)
    sources = Column(String(255))  #-- Sources des données soumises
    description = Column(Text)


"========= La construction de la table AlertLog ============"
# #-- La table AlertLog est utilisée pour stocker les logs d'alerte
# #-- Elle contient les informations sur les logs d'alerte
class AlertLog(Base):
    __tablename__ = "alert_logs"
    id = Column(Integer, primary_key=True)
    id_seuil = Column(Integer, ForeignKey("seuil_alert.id"))
    usermail = Column(String, nullable=True)
    severity = Column(String, nullable=True) #-- 1: faible, 2: moyen, 3: élevé
    status = Column(String, nullable=True) #-- 1: en attente, 2: en cours, 3: terminé
    message = Column(String, nullable=True)
    region = Column(String, nullable=True)
    district = Column(String, nullable=True)
    notification_type = Column(String, nullable=True)
    recipient = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class SeuilAlert(Base):
    __tablename__ = "seuil_alert"
    id = Column(Integer, primary_key=True)
    usermail = Column(String, nullable=False, unique=True, default="admin@gmail.com")
    intervalle = Column(String, default="1") #-- 1: hebdomadaire, 2: mensuel, 3: annuel
    seuil_positivite = Column(Integer, default=10)
    seuil_hospitalisation = Column(Integer, default=10)
    seuil_deces = Column(Integer, default=10)
    seuil_positivite_region = Column(Integer, default=10)
    seuil_hospitalisation_region = Column(Integer, default=10)
    seuil_deces_region = Column(Integer, default=10)
    seuil_positivite_district = Column(Integer, default=10)
    seuil_hospitalisation_district = Column(Integer, default=10)
    seuil_deces_district = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.now)


"========= La construction de la table User ============"
# #-- La table User est utilisée pour stocker les informations des utilisateurs
# #-- Elle contient les informations d'authentification et de profil
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    role = Column(String(20), default="user")  # user, analyst, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)








