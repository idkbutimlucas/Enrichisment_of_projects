import os
import requests
from bs4 import BeautifulSoup
import openai
from builtwith import builtwith
from dotenv import load_dotenv
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.compat import xmlrpc_client

# Charger les variables d'environnement
load_dotenv()

# Récupérer les variables depuis le .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_PASSWORD = os.getenv("WP_PASSWORD")

if not OPENAI_API_KEY or not WP_URL or not WP_USER or not WP_PASSWORD:
    raise ValueError("Clé API OpenAI ou identifiants WordPress manquants. Vérifie ton fichier .env")

# Connexion à WordPress
wp_client = Client(WP_URL, WP_USER, WP_PASSWORD)

# Liste des URLs à analyser
URLS = [
        "https://www.exemple.fr/",
]

def fetch_page_content(url):
    """Récupère le contenu d'une page web."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de récupération de {url} : {e}")
        return None

def extract_text(html_content):
    """Extrait le texte utile d'une page HTML (limité à 1000 caractères)."""
    soup = BeautifulSoup(html_content, "html.parser")
    texts = soup.stripped_strings
    return " ".join(texts)[:1000]

def summarize_text(url, text):
    """Génère un résumé structuré avec OpenAI GPT-3.5-Turbo."""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
Tu dois fournir trois paragraphes distincts sans ajouter de titres :
1️⃣ Un résumé du site (500 caractères max) en une seule phrase.
2️⃣ Une description détaillée du site (1000 caractères max) en un paragraphe.
3️⃣ Une liste des technologies utilisées pour créer ce site (1000 caractères max).

Ne mets aucun label ou titre dans ton texte.

📌 Voici le texte extrait du site {url} :
{text}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Génère un résumé structuré et concis selon le format donné."},
                      {"role": "user", "content": prompt}]
        )
        summary = response.choices[0].message.content.split("\n")

        # Supprimer les lignes vides
        summary = [s for s in summary if s.strip()]
        print("📌 Résumé généré par OpenAI:", summary)
        return summary
    except Exception as e:
        print(f"❌ Erreur de résumé : {e}")
        return ["Résumé indisponible.", "Aucune description disponible.", "Technologies indisponibles."]

def generate_dalle_image(description):
    """Génère une image via OpenAI DALL·E."""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    try:
        print(f"🎨 Génération d'une image avec DALL·E pour : {description}")
        response = client.images.generate(
            model="dall-e-3",
            prompt=description,
            n=1,
            size="1024x1024",
        )
        image_url = response.data[0].url
        print(f"✅ Image générée avec succès : {image_url}")
        return image_url
    except Exception as e:
        print(f"❌ Erreur de génération d'image : {e}")
        return None

def upload_image_to_wordpress(image_url):
    """Télécharge et ajoute une image en tant qu'image mise en avant sur WordPress."""
    if not image_url:
        print("❌ Aucune URL d'image fournie.")
        return None

    print(f"📤 Téléchargement de l'image depuis : {image_url}")

    try:
        image_data = requests.get(image_url).content
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement de l'image : {e}")
        return None

    data = {
        'name': 'dalle_generated_image.jpg',
        'type': 'image/jpeg',
        'bits': xmlrpc_client.Binary(image_data)
    }

    try:
        response = wp_client.call(media.UploadFile(data))
        image_id = response.get('id')

        if not image_id:
            print("❌ L'ID de l'image n'a pas été récupéré correctement.")
            return None

        print(f"✅ Image uploadée avec succès ! ID : {image_id}")
        return image_id
    except Exception as e:
        print(f"❌ Erreur d'upload d'image sur WordPress : {e}")
        return None

def create_wordpress_project(title, short_description, description_presentation, description_techno, image_id):
    """Crée un post WordPress et assigne une image mise en avant."""
    post = WordPressPost()
    post.title = title
    post.post_status = "publish"
    post.post_type = "projet"

    post_id = wp_client.call(NewPost(post))
    print(f"✅ Projet '{title}' ajouté à WordPress avec succès (ID: {post_id})")

    if image_id:
        print(f"🖼 Ajout de l'image mise en avant (ID: {image_id}) au projet {post_id}")
        try:
            wp_client.call(posts.EditPost(post_id, {'post_thumbnail': image_id}))
            print("✅ Image mise en avant ajoutée avec succès.")
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de l'image mise en avant : {e}")

    acf_data = {
        "description_short": short_description,
        "description_presentation": description_presentation,
        "description_techno": description_techno,
    }
    print("📤 Envoi des champs ACF à WordPress :", acf_data)

    for field, value in acf_data.items():
        wp_client.call(posts.EditPost(post_id, {"custom_fields": [{"key": field, "value": value}]}))

    print("✅ Projet mis à jour avec les données ACF.")

def main():
    for url in URLS:
        print(f"🔍 Analyse de {url}...")

        html_content = fetch_page_content(url)
        if not html_content:
            print(f"❌ Impossible de récupérer la page pour {url}.")
            continue

        text_content = extract_text(html_content)
        summary = summarize_text(url, text_content)

        if len(summary) < 3:
            summary.extend(["Aucune description disponible."] * (3 - len(summary)))

        site_title = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        site_title = site_title.split(".")[0].capitalize()

        description_short = f"<p>Bienvenue sur « {site_title} » – {summary[0]}</p>\n<p><strong><a href='{url}' target='_blank'>Site : {site_title}</a></strong></p>"
        description_presentation = f"<h2><strong>Présentation de l’application « {site_title} » :</strong></h2>\n\n<p>{summary[1]}</p>"
        description_techno = f"<h2><strong>Les technologies derrière « {site_title} » :</strong></h2>\n\n<p>{summary[2]}</p>"

        image_url = generate_dalle_image(f"Illustration conceptuelle du site {site_title}")
        image_id = upload_image_to_wordpress(image_url)

        create_wordpress_project(site_title, description_short, description_presentation, description_techno, image_id)

    print("✅ Analyse et importation WordPress terminées.")

if __name__ == "__main__":
    main()
