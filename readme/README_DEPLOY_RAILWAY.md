# 🚀 Déploiement FastAPI sur Railway

## 1. Préparer le projet

- Vérifier la présence des fichiers suivants :
  - `requirements.txt` (toutes les dépendances, ex : fastapi, uvicorn, gunicorn, pandas, etc.)
  - `Procfile` à la racine :
    ```
    web: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    ```
  - `runtime.txt` (exemple : `python-3.12.1`)

---

## 2. Initialiser Railway

```bash
npx @railway/cli login
npx @railway/cli init
```

---

## 3. Ajouter la base PostgreSQL

```bash
npx @railway/cli add
# Sélectionner "PostgreSQL"
```

---

## 4. Configurer les variables d'environnement

```bash
npx @railway/cli variables --set "SECRET_KEY=ta_cle_secrete"
npx @railway/cli variables --set "ENVIRONMENT=production"
npx @railway/cli variables --set "DEBUG=False"
# DATABASE_URL est ajouté automatiquement par Railway avec PostgreSQL
```

---

## 5. Déployer l'application

```bash
npx @railway/cli up
```

---

## 6. Obtenir l'URL de l'application

```bash
npx @railway/cli status
# ou
npx @railway/cli domain
```
- L'URL ressemble à :
  `https://nom-du-projet-production.up.railway.app`

---

## 7. Initialiser la base (tables, admin, etc.)

```bash
npx @railway/cli run python init_db.py
npx @railway/cli run python scripts/create_admin.py
# ou, si automatisé dans main.py, juste redéployer suffit
```

---

## 8. Vérifier sur Railway

- Tables créées et données présentes dans l'onglet **Data**
- Application accessible via l'URL Railway

---

**Besoin d'un guide détaillé pour chaque étape ?**
N'hésitez pas à demander ! 