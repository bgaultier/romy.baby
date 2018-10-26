# romy.baby
Romy.baby est un journal de bord en ligne à destination des jeunes parents (un peu geeks) qui souhaitent suivre les activités de bébé.

![Aperçu du tableau de bord](romy/static/img/Screenshot_1.png)

## Fonctionnalités
* Suivi d'activités : biberons, couches, bains...
* Ajout de commentaires par activité
* Gestion de la multiparentalité
* Analyse et graphiques depuis la naissance de bébé

## Utilisation sur le site romy.baby
1. Connectez-vous sur le site https://romy.baby/ et entrez votre adresse email pour recevoir un compte gratuit et privé sur notre serveur communautaire (hébergé chez https://www.alwaysdata.com/fr/). Ce service est fourni gratuitement et nous nous engageons à respecter votre vie privée et vos données dans le cadre de la licence [GPL Affero](https://www.gnu.org/licenses/agpl-3.0.fr.html)
2. Vous recevrez par email un identifiant et un mot de passe vous permettant d'accéder à l'interface web : ![Aperçu des statistiques](romy/static/img/Screenshot_2.png)

## Installation sur votre serveur
1. Clonez ce dépôt github
```bash
git clone git@github.com:bgaultier/romy.baby.git
```
2. Déployez l'application web en suivant les instructions mentionnées sur la documentation [Django](https://docs.djangoproject.com/fr/2.1/ref/django-admin/)
```bash
cd romy/
python manage.py migrate
python manage.py runserver
```
