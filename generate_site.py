import requests
import xml.etree.ElementTree as ET
import re

# Ton URL de flux RSS Letterboxd
RSS_FEED_URL = 'https://letterboxd.com/oni_le_chan/rss/' # Remplace par ton pseudo

# Nom du fichier HTML de sortie
OUTPUT_HTML_FILE = 'index.html'

def generate_html_from_rss(rss_url, output_file):
    try:
        response = requests.get(rss_url)
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP en erreur (4xx ou 5xx)
        rss_content = response.content

        # Nettoyage rudimentaire pour les caractères non valides si besoin, bien que simplexml_load_file gère bien
        # xml_content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', rss_content.decode('utf-8'))
        # root = ET.fromstring(xml_content)

        root = ET.fromstring(rss_content)
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion au flux RSS: {e}")
        return
    except ET.ParseError as e:
        print(f"Erreur de parsing XML: {e}")
        return

    html_output = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mes Films & Critiques Letterboxd - Oni Lechan</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* Styles CSS de base pour rendre le site joli */
        body {{
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f7f6; /* Couleur de fond légère */
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1000px;
            margin: 20px auto;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0 0 15px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        h1, h2 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }}
        .film-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
            justify-content: center;
        }}
        .film-item {{
            background-color: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            display: flex;
            flex-direction: column;
        }}
        .film-item:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        }}
        .film-item img {{
            width: 100%;
            height: 400px; /* Hauteur fixe pour les images */
            object-fit: cover; /* Recadre l'image sans déformer */
            border-bottom: 1px solid #eee;
        }}
        .film-content {{
            padding: 20px;
            display: flex;
            flex-direction: column;
            flex-grow: 1; /* Pour que le contenu s'étende */
        }}
        .film-content h3 {{
            margin-top: 0;
            margin-bottom: 10px;
            color: #34495e;
            font-size: 1.5em;
        }}
        .film-content p {{
            font-size: 0.95em;
            color: #555;
            flex-grow: 1; /* Pour que la review prenne l'espace disponible */
        }}
        .film-content .rating {{
            font-weight: bold;
            color: #f39c12; /* Couleur pour les étoiles */
            margin-bottom: 10px;
        }}
        .film-content a {{
            display: inline-block;
            margin-top: 15px;
            padding: 10px 15px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.2s ease-in-out;
            align-self: flex-start; /* Aligne le bouton à gauche */
        }}
        .film-content a:hover {{
            background-color: #2980b9;
        }}
        .error-message {{
            color: #e74c3c;
            text-align: center;
            font-size: 1.1em;
            margin-top: 50px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Mes Critiques de Films Letterboxd</h1>
        <div class="film-grid">
"""

    for item in root.findall('.//item'):
        full_title = item.find('title').text if item.find('title') is not None else ''
        link = item.find('link').text if item.find('link') is not None else '#'
        description_html = item.find('description').text if item.find('description') is not None else ''

        # Extraire le titre du film et l'année
        match_title = re.match(r'^(.*?),\s*(\d{4})', full_title)
        film_title = match_title.group(1).strip() if match_title else full_title
        film_year = match_title.group(2) if match_title else ''

        # Extraire la note
        rating_stars = ''
        match_rating = re.search(r'★+', full_title)
        if match_rating:
            rating_stars = match_rating.group(0)
        else:
            # Essayer de récupérer la note numérique et la convertir en étoiles
            lb_member_rating = item.find('{https://letterboxd.com}memberRating')
            if lb_member_rating is not None and lb_member_rating.text:
                try:
                    rating_value = float(lb_member_rating.text)
                    rating_stars = '★' * int(rating_value)
                    if rating_value - int(rating_value) >= 0.5:
                        rating_stars += '½'
                except ValueError:
                    pass

        # Extraire l'URL de l'image de la description HTML
        image_url = ''
        match_img = re.search(r'<img src="(.*?)"', description_html)
        if match_img:
            image_url = match_img.group(1)

        # Extraire le texte de la critique de la description HTML
        # On retire la partie image et tout ce qui est avant le premier <p> après l'image
        review_text = description_html
        review_text = re.sub(r'^.*?<p>(.*?)<\/p>', r'\1', review_text, 1, flags=re.DOTALL) # Capture le contenu du premier <p> après l'image
        review_text = re.sub(r'<[^>]+>', '', review_text).strip() # Supprime toutes les balises HTML restantes
        review_text = review_text.replace('&nbsp;', ' ').replace('&#8230;', '...').replace('…', '...') # Nettoyage des entités
        
        # nl2br équivalent en Python (simple remplacement des retours chariot par <br />)
        formatted_review_text = review_text.replace('\n', '<br />')

        html_output += f"""
            <div class="film-item">
                {f'<img src="{image_url}" alt="Affiche de {film_title}">' if image_url else ''}
                <div class="film-content">
                    <h3>{film_title} ({film_year})</h3>
                    {f'<p class="rating">Note: {rating_stars}</p>' if rating_stars else ''}
                    <p>{formatted_review_text}</p>
                    <a href="{link}" target="_blank" rel="noopener noreferrer">Voir sur Letterboxd</a>
                </div>
            </div>
"""

    html_output += """
        </div>
    </div>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
    print(f"Site généré avec succès dans {output_file} !")

if __name__ == "__main__":
    # Assure-toi d'installer 'requests' si ce n'est pas déjà fait : pip install requests
    # Dans ton terminal: pip install requests
    generate_html_from_rss(RSS_FEED_URL, OUTPUT_HTML_FILE)

# ... (ton code Python de generate_site.py) ...
# Assure-toi que cette ligne est correcte !
RSS_FEED_URL = 'https://letterboxd.com/oni_le_chan/rss/'
# ... (le reste du code) ...