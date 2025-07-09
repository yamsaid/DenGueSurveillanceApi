from pydantic import BaseModel
from typing import Optional
from datetime import date
import io
import pandas as pd
import numpy as np
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class CasDengueValidator(BaseModel):
    model_config = {
        "from_attributes": True
    }
    centre_sante_id: int
    sexe: str
    age: int
    date_debut_symptomes: Optional[date]
    symptomes: Optional[str]
    date_consultation: Optional[date]
    test_realise: Optional[bool]
    date_test: Optional[date]
    resultat_test: Optional[str]
    gravite: Optional[str]
    hospitalisation: Optional[bool]
    date_hospitalisation: Optional[date]
    issue_cas: Optional[str]
    adresse: Optional[str]
    zone: Optional[str]
    date_declaration: Optional[date]

class centreSanteValidator(BaseModel):

    """
    docstring
    """
    model_config = {
        "from_attributes": True
    }
    nom :Optional[str]
    type: Optional[str] # -- CSPS, CMA, CHR, etc.
    region: Optional[str]
    province: Optional[str]
    commune: Optional[str]
    code_centre :Optional[str]
    contact_agent: Optional[str]



"======== fonction pour vérifier la coherence des données ========="
# cas de dengue 

class ValidationCasDengue(BaseModel):
    """
    
    Args:
        BaseModel (_type_): _description_
    """
    model_config = {
        "from_attributes": True
    }
    
    sexe: str = Field(description="Le sexe du patient")
    age: int = Field(gt=0, description="L'âge du patient / an")
    region : Optional[str]= Field(default="Centre",min_length=2, max_length=50) # Centre, Hauts Bassins
    date_consultation: Optional[str]
    district : Optional[str]
    resultat_test: Optional[str] #Positif / Négatif"
    serotype: Optional[str] #DENV2 / DENV3
    hospitalisation: Optional[str]
    issue: Optional[str] = Field(default="Guéri",min_length=2, max_length=50) # Guéri / En traitement / Décédé/inconnue
    id_source: int = Field(description="L'identifiant de la soumission de données associée à ce cas")   
    
    

    @field_validator("region")
    def region_must_be_valid(cls, v):
        valid_regions = ["centre", "hauts-Bassins"]
        if v not in valid_regions:
            raise ValueError(f"Région invalide. Choisissez parmi {valid_regions}")
        return v
    
    @field_validator("issue")
    def issue_must_be_valid(cls, v):
        """_summary_

        Args:
            v (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        valid_issue = ["guéri","en traitement","décédé","inconnue"]
        if v not in valid_issue:
            raise ValueError(f"Issue invalide. Choisissez parmi {valid_issue}")
        return v
    
    @field_validator("resultat_test")
    def test_must_be_valid(cls, v):
        """_summary_

        Args:
            v (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        valid_test = ["positif","négatif"]
        if v not in valid_test:
            raise ValueError(f"Resultat de test invalide. Choisissez parmi {valid_test}")
        return v
    
    @field_validator("serotype")
    def variant_must_be_valid(cls, v):
        """_summary_

        Args:
            v (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        valid_variant = ["denv2","denv3"]
        if v not in valid_variant:
            raise ValueError(f"variant de dengue invalide. Choisissez parmi {valid_variant}")
        return v
    
    @field_validator("sexe")
    def sexe_must_be_valid(cls, v):
        """_summary_

        Args:
            v (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        valid_sexe = ["feminin","masculin","f","m",'homme','femme']
        if v not in valid_sexe:
            raise ValueError(f"sexe invalide. Choisissez parmi {valid_sexe}")
        return v

 

    
'''cas=centreSanteValidator(nom='saidou',type='yu',region='cn',province='nm',commune='tg',code_centre='sy',contact_agent='gjf')
print(cas.model_dump())'''


#cas=ValidationCasDengue(idCas=1,date_consultation="2023-06-25",region="Centre",district="DS Baskuy",sexe="Homme",age=20,statut_test="Positif",serotype="DENV3",hospitalisation="Oui",issue="En traitement")
#print(cas.model_dump())

class ValidationSoumissionBase(BaseModel):
    model_config = {
        "from_attributes": True
    }
    username: str
    date_soumission: date
    centre: str
    poste: str
    apikey: str
    periode_debut: date
    periode_fin: date
    description: str
    sources: str


# Modèle Pydantic pour la réponse
class AlertLogResponse(BaseModel):
    model_config = {
        "from_attributes": True
    }
    id: int
    message: str
    region: str
    district: Optional[str] = None
    notification_type: str
    recipient: str
    created_at: datetime

    
