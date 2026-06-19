# MMotors
MMotors est un concessionnaire automobile qui a décidé d'agrandir son offre en proposant des voitures en leasin en plus de son offre d'achat de voiture initial. Afin de suivre ce renouveau, ils ont décidé de remettre leur application web à neuf et d'offrir leurs service en ligne.
Projet développé dans le cadre  du projet Bachelor en développement Python

## Git
Git est un version controller qui permet de versioner tout projet informatique au fur et à mesure du développement de celui-ci. Cela permet de revenir en arrière en cas d'erreur critique sans prendre le risque de complètement perdre le projet.
##### J'ai crée 3 branches principales:
    - main --> la branche principale à partir de laquelle sera déployer l'application
    - pre-prod --> branche servant à déployer l'application sur un environnement similaire à la prod, permettant de controller d'éventuels incidents non prévues dû à cet environnement sans impacter la production.
    - dev --> branche servant à regrouper toutes les noouvelles fonctionnalitè^és au fur et à mesure de l'évolution du projet.

##### Puis à partir de la branche dev, une branche par fonctionnalités sera développé avant d'être à nouveau merge avec la branche dev:
    - feature/**
    - feature/**
    -...

Sous forme de “bullet points”, mettez en évidence votre démarche pour développer une user Story
## US 
- Liste fonctionalité
- EPIC (page d'acceuil) ou US(login) en fonction du volume de la tâche
- Fragmentation EPIC en US 
- Chaque US à 1 objectif décrit ainsi: En tant que .../ Je souhaite.../Afin de ... 
        --> Chaque US doit spécifier tout besoin nécessaire à son commencement (maquette)
        --> Chaque US possède des critères d'acceptation pour la definir comme done

- Une US doit correspondre à la Definition Of Ready (DoR) avant de rentrer dans un sprint
        --> la DoR est établie au début du projet

- Cycle sprint pour l'US, Do-Doing-Test
- Après la phase de Test
        --> Si correspond à la Définition Of Done (DoD), US done
        --> US déployer

- Nouvelle US, nouveau cycle

### Fonctionalités:
#### Gestion users:
- User --> consultation véhicule, création compte, login, Demande d'achat/leasing véhicule/ upload documents
- Admin --> Gestion véhicule, gestion dossier client
        
#### Véhicules:
- CRUD véhicule --> Authorisation selon role
- Pagination véhicule
- Filtre véhicule

### Stack Technique:
- Front End --> Angular 21 --> déployer sur Render
- Back End --> Rest API avec Fast Api --> déployer sur fly.io
- BDD -->
    - local --> sqlite
    - prod --> PostGressql --> fly.io
- Container --> Docker
- CI/CD --> github workflows 

## Test couverture
Test Coverage > 80% - Pytest
commande --> pytest --cov=src
|Name                           | Stmts  | Miss  |Cover|
|-------------------------------|--------|-------|-----|
|src\__init__.py                |     0  |    0  | 100%|
|src\config\__init__.py         |     0  |    0  | 100%|
|src\config\database.py         |    10  |    2  |  80%|
|src\config\seed.py             |    15  |    4  |  73%|
|src\models\__init__.py         |     0  |    0  | 100%|
|src\models\car_model.py        |    12  |    0  | 100%|
|src\models\user_model.py       |    12  |    0  | 100%|
|src\routers\__init__.py        |     0  |    0  | 100%|
|src\routers\car_router.py      |    62  |    4  |  94%|
|src\routers\upload_router.py   |    24  |   11  |  54%|
|src\routers\user_router.py     |    80  |    7  |  91%|
|src\schemas\__init__.py        |     0  |    0  | 100%|
|src\schemas\car_schemas.py     |    24  |    0  | 100%|
|src\schemas\filter_schemas.py  |     9  |    0  | 100%|
|src\schemas\token_schemas.py   |     4  |    0  | 100%|
|src\schemas\user_schemas.py    |    24  |    0  | 100%|
|src\service\__init__.py        |     0  |    0  | 100%|
|src\service\auth_py.py         |    48  |    0  | 100%|
|src\service\query_service.py   |    58  |    9  |  84%|
|src\service\s3_service.py      |    29  |   16  |  45%|
|-------------------------------|--------|-------|-----|
|TOTAL                          |   411  |   53  |  87%|


## Installation en Local

- Pour le Front end --> voir repo `https://github.com/k4y4Dev/MMotorsFront`

### Prérequis
- Python (>= v3.10)
- pip (>= 20.0)
- postgresql 
- pgadmin ou pluggin Database , Database Client sur Vuîsual studio code

### Récupération projet

- `mkdir mmotors-back`
- `cd mmotors-back`
- `git init`
- `git clone https://github.com/k4y4Dev/MMotorsBack.git`

## Création environment python 
`python -m venv .venv`
`source .venv/bin/activate`  # Sur Mac/Linux
`.venv\Scripts\activate `    # Sur Windows

### Installation projet
- `pip intall requirements.txt`
- Créer fichier .env --> le mettre dans un gitignore --> Vérifier le fichier config.py pour connaitre les var env. nécessaires
- Paramétrer une DB sqlite ou une postgresql dans le fichier config/database.py
    - Si potgresql`CREATE DATABSE mmotors` 

### DATABASE minimum data
- Création seed.py
```
import random

from sqlalchemy.orm import Session
from src.models.car_model import Car
from src.models.user_model import User
from src.service.auth_py import hash_password
from .database import SessionLocal


db = SessionLocal()

car_list = [
    "Mercedes",
    "Renault",
    "Audi",
    "Peugeot",
    "Toyota",
    "Citroen",
    "BMW",
    "Ford"

]

car_images = [
    "berline_1.png",
    "berline_rouge.png",
    "decapot_1.png",
    "sporty_1.png",
    "sporty_rouge.png",
    "suv_1.png",
    "suv_rouge.png",
]

trade = [
    "leasing",
    "buying"
]

adminUser = User(
    email='admin-cobaye@random.com',
    password_hashed=hash_password('kP9#vL7n!Xm2$qR5'),
    lastname='Admin',
    firstname='Test',
    role='admin'

)

normalUser = User(
    email='user-cobaye@random.com',
    password_hashed=hash_password('tB4$mX8v!Wp3#kL6'),
    lastname='Normal User',
    firstname='Test',
    role='user'

)

normalUser2 = User(
    email='user-cobaye2@random.com',
    password_hashed=hash_password('F8oj8hE.{9z0LT8e]'),
    lastname='Normal User',
    firstname='Test',
    role='user'

)

normalUser3 = User(
    email='user-cobaye3@random.com',
    password_hashed=hash_password('5=pOv:u<2KnS864N`'),
    lastname='Normal User',
    firstname='Test',
    role='user'

)

normalUser4 = User(
    email='user-cobaye4@random.com',
    password_hashed=hash_password('#s{TD1x8As5KzJu$b'),
    lastname='Normal User',
    firstname='Test',
    role='user'

)

normalUser5 = User(
    email='user-cobaye5@random.com',
    password_hashed=hash_password('5}-5n/dx4\sD94nVM'),
    lastname='Normal User',
    firstname='Test',
    role='user'

)

def seed():
    if db.query(Car).first():
        return
    
    for i  in range(25):
        new_car = Car(
            name=f'{random.choice(car_list)} {i}', 
            price=random.randrange(1000, 45000), 
            km=random.randrange(80000, 200000),
            image=random.choice(car_images),
            trade=random.choice(trade))
        db.add(new_car)
    
    db.add(adminUser)
    db.add(normalUser)
    db.add(normalUser2)
    db.add(normalUser3)
    db.add(normalUser4)
    db.add(normalUser5)

    
    db.commit()

 ```

 - Sur main.py, décommenter le try seed.py

### Lancement projet

- `fastapi dev main.py`
- `http://localhost:8000/docs`
