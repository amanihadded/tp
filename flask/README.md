# TP Flask — premier projet

Mémo pour créer un projet Flask de zéro sous Windows (PowerShell).

## C'est quoi Flask ?

Un outil pour fabriquer des sites web en Python.

Sans Flask, Python ne sait pas répondre à un navigateur. Flask s'occupe de tout
ce qui se passe entre les deux : il écoute les demandes du navigateur, appelle
notre code Python, et renvoie une page HTML.

On dit que c'est un **micro**-framework. « Micro » ne veut pas dire limité, mais
qu'il ne fournit que l'essentiel. Deux conséquences :

- **Ce qu'il fait** : le routage d'URL (associer une adresse à une fonction
  Python) et la génération de pages HTML avec un moteur de modèles, Jinja2.
  Ce sont les deux choses qu'on utilise dans ce TP.
- **Ce qu'il ne fait pas** : parler à une base de données, par exemple. Il n'a
  pas d'ORM — l'outil qui traduit les tables d'une base en objets Python. Si on
  en a besoin, on l'ajoute séparément.

L'avantage : on n'installe que ce dont on a besoin, et le projet reste simple à
comprendre. L'inconvénient : sur un gros projet, il faut assembler soi-même les
pièces que d'autres frameworks fournissent déjà.

## Les autres frameworks web Python

Flask n'est pas le seul. Les principaux, et à quoi ils servent :

| Framework | À quoi il sert |
| --- | --- |
| **Django** | Tout inclus, ORM compris. Pour les gros projets. |
| **Flask** | Micro-framework. Léger, on ajoute ce qu'on veut. |
| **FastAPI** | Orienté performance. Pour créer des API rapidement. |
| **Tornado** | Applications réseau en temps réel (chat, notifications). |
| **Pyramid** | Minimaliste et flexible. |
| **Bottle** | Très proche de Flask, encore plus petit. |
| **CherryPy** | Organise les fonctionnalités sous forme de pages web. |
| **Web2py** | Cherche à simplifier le développement web. |
| **Sanic** | Asynchrone : traite plusieurs demandes en parallèle. |
| **Dash** | Spécialisé dans les tableaux de bord interactifs. |

**Lequel choisir ?** La règle simple :

- **Gros projet** → Django. Il fournit déjà la base de données, l'authentification,
  l'interface d'administration. On gagne du temps.
- **Petit ou moyen projet** → Flask, FastAPI ou un autre micro-framework. Moins de
  choses à apprendre avant de commencer.

## Structure finale

```
v1_test/
├── mon_env/          le venv (ne se partage pas, ne se commite pas)
├── app.py            le code Python
├── static/           CSS, JS, images
│   └── style.css
└── templates/        les pages HTML
    ├── index.html
    └── salut.html
```

Les noms `static` et `templates` sont imposés par Flask. Il les cherche
automatiquement à côté de `app.py` : on ne les déclare nulle part dans le code.
Si on les renomme (`template` au singulier, `Static` avec une majuscule),
Flask ne trouve plus rien.

## 1. Créer le dossier du projet

```powershell
cd "C:\Users\amani\Desktop\Cycle ingénieur\2éme_ing\prog_python\tp\flask"
mkdir v1_test
cd v1_test
```

Attention : si le nom du dossier contient un espace, il faut des guillemets.
`cd v1 test` échoue, PowerShell lit deux arguments. `cd "v1 test"` fonctionne.

## 2. Créer le venv et l'activer

```powershell
python -m venv mon_env
.\mon_env\Scripts\Activate
```

`(mon_env)` apparaît au début de la ligne : le venv est actif. Tout ce qu'on
installe avec pip va dedans, pas dans le Python global du système.

Sous Linux/Mac la commande d'activation est `source mon_env/bin/activate`.
Sous Windows elle ne marche pas : `source` n'existe pas en PowerShell.

## 3. Installer Flask

```powershell
pip install Flask
```

## 4. Créer les dossiers static et templates

```powershell
mkdir static, templates
```

La virgule permet de créer les deux d'un coup en PowerShell.

## 5. Créer app.py

```python
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def accueil():
    return render_template('index.html')


@app.route('/salut/<nom>')
def salut(nom):
    return render_template('salut.html', nom=nom)


if __name__ == '__main__':
    app.run(debug=True)
```

- `Flask(__name__)` crée l'application. `__name__` indique à Flask où il se
  trouve : c'est comme ça qu'il sait où chercher `templates/` et `static/`.
- `@app.route('/')` associe une URL à la fonction juste en dessous.
- `<nom>` dans l'URL est une variable : elle est passée en argument à la
  fonction. L'URL `/salut/amani` appelle `salut('amani')`.
- `render_template('index.html')` va chercher le fichier dans `templates/`.
  On donne juste le nom, pas le chemin.
- `debug=True` recharge le serveur automatiquement à chaque modification.

## 6. Créer templates/index.html

```html
<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Mon premier site Flask</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Bonjour, Flask fonctionne !</h1>
    <a href="{{ url_for('salut', nom='amani') }}">Page de salutation</a>
</body>
</html>
```

Les `{{ ... }}` sont du Jinja2, le moteur de templates de Flask : c'est du code
exécuté côté serveur, avant l'envoi de la page au navigateur.

- `url_for('static', filename='style.css')` devient `/static/style.css`.
- `url_for('salut', nom='amani')` devient `/salut/amani`. On donne le nom de la
  fonction Python, pas l'URL : si on change la route dans `app.py`, les liens
  suivent automatiquement.

## 7. Créer templates/salut.html

```html
<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Salutation</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Salut {{ nom }} !</h1>
    <a href="{{ url_for('accueil') }}">Retour à l'accueil</a>
</body>
</html>
```

`{{ nom }}` affiche la variable passée par `render_template('salut.html', nom=nom)`.

## 8. Créer static/style.css

```css
body {
    font-family: Arial, sans-serif;
    max-width: 600px;
    margin: 60px auto;
    padding: 0 20px;
    line-height: 1.6;
    color: #222;
}

h1 {
    color: #0a6;
}
```

## 9. Lancer le serveur

```powershell
python app.py
```

Ouvrir http://127.0.0.1:5000. Si le titre est vert, le CSS est chargé, donc
`static/` fonctionne. Tester aussi http://127.0.0.1:5000/salut/amani.

`Ctrl+C` pour arrêter le serveur.

## Erreurs rencontrées et leur cause

| Message | Cause |
| --- | --- |
| `can't open file 'app.py'` | Le fichier n'existe pas, ou on n'est pas dans le bon dossier. Vérifier avec `ls`. |
| `Could not locate a Flask application` | `flask run` cherche un `app.py` ou `wsgi.py` dans le dossier courant et n'en trouve pas. |
| `source n'est pas reconnu` | Commande Linux. Sous Windows : `.\mon_env\Scripts\Activate`. |
| `Impossible de trouver un paramètre positionnel` | Espace dans un chemin sans guillemets : `cd "v1 test"`. |
| `TemplateNotFound` | Le fichier HTML n'est pas dans `templates/`, ou le dossier est mal nommé. |
| Page sans style | Le CSS n'est pas dans `static/`, ou le `url_for` est mal écrit. |

## Note sur le venv

`mon_env/` ne se partage pas et ne se commite pas (voir `.gitignore`). Sur une
autre machine on le recrée avec `python -m venv mon_env` puis on réinstalle les
dépendances. Pour garder la liste des paquets installés :

```powershell
pip freeze > requirements.txt
```

Et pour tout réinstaller ailleurs :

```powershell
pip install -r requirements.txt
```
