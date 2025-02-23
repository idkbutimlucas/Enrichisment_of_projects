# Analyse et Importation Automatisée de Sites Web vers WordPress

## Description
Ce projet permet d'extraire des informations de sites web, de les résumer via l'API OpenAI GPT-3.5-Turbo, de générer une illustration avec DALL·E, puis de publier ces données sur un site WordPress sous forme de projet.

## Fonctionnalités
- Récupération automatique du contenu HTML des sites web ciblés
- Extraction et résumé du texte pertinent via OpenAI
- Génération d'une image illustrant le site via DALL·E
- Publication des informations sur WordPress sous forme d'article
- Ajout d'une image mise en avant sur WordPress

## Prérequis
- Python 3.x
- Un compte OpenAI avec une clé API
- Un site WordPress compatible avec XML-RPC
- Un fichier `.env` contenant les informations de connexion

## Installation
1. Cloner ce dépôt :
   ```sh
   git clone https://github.com/votre-repo.git
   cd votre-repo
   ```

2. Installer les dépendances :
   ```sh
   pip install -r requirements.txt
   ```

3. Créer un fichier `.env` à la racine du projet et ajouter vos informations :
   ```ini
   OPENAI_API_KEY="votre_clé_api"
   WP_URL="https://votre-site.com/xmlrpc.php"
   WP_USER="votre_utilisateur"
   WP_PASSWORD="votre_mot_de_passe"
   ```

## Utilisation
1. Modifier la liste des URLs à analyser dans le script Python :
   ```python
   URLS = [
       "https://www.exemple.fr/",
   ]
   ```
2. Exécuter le script :
   ```sh
   python3 main.py
   ```

## Technologies utilisées
- **Python** (gestion des requêtes, traitement HTML, manipulation API)
- **Requests** (récupération de pages web)
- **BeautifulSoup** (parsing HTML)
- **OpenAI API** (génération de contenu et d'images)
- **WordPress XML-RPC** (publication automatique de contenu)
- **Dotenv** (gestion des variables d'environnement)

## Contributions
Les contributions sont les bienvenues ! Forkez le projet, créez une branche, apportez vos modifications et soumettez une pull request.

## Licence
Ce projet est sous licence MIT. Consultez le fichier `LICENSE` pour plus d'informations.

