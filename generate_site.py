import requests
import xml.etree.ElementTree as ET
import re
import html # Assure-toi que cette ligne est bien présente au début

# Ton URL de flux RSS Letterboxd
RSS_FEED_URL = 'https://letterboxd.com/oni_le_chan/rss/' # Remplace par ton pseudo

# Nom du fichier HTML de sortie
OUTPUT_HTML_FILE = 'index.html'

def generate_html_from_rss(rss_url, output_file):
    try:
        response = requests.get(rss_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)

    except requests.exceptions.RequestException as e:
        # print(f"DEBUG: Erreur de connexion au flux RSS: {e}") # Debug print - REMOVED
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Erreur de Chargement</title>
    <link rel="stylesheet" href="chef_d_oeuvre.css">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="container">
        <h1>Oups ! Erreur de Chargement</h1>
        <p class="error-message">Impossible de récupérer les données de Letterboxd pour le moment. Veuillez réessayer plus tard.</p>
        <p class="error-message">Détails de l'erreur : {e}</p>
    </div>
</body>
</html>
            """)
        return
    except ET.ParseError as e:
        # print(f"DEBUG: Erreur de parsing XML: {e}") # Debug print - REMOVED
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Erreur de Parsing</title>
    <link rel="stylesheet" href="chef_d_oeuvre.css">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="container">
        <h1>Oups ! Erreur de Parsing des Données</h1>
        <p class="error-message">Les données de Letterboxd ne sont pas au bon format. Veuillez contacter le support ou vérifier le flux.</p>
        <p class="error-message">Détails de l'erreur : {e}</p>
    </div>
</body>
</html>
            """)
        return

    html_output = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mes Films & Critiques Letterboxd - Oni Lechan</title>
    <link rel="stylesheet" href="chef_d_oeuvre.css">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"> </head>
<body>
    <header class="main-header">
        <div class="container">
            <h1 class="site-title">Mes Avis Letterboxd !</h1>
            <p class="site-tagline">Les films que j'ai notés, avec mes critiques détaillées.</p>
            <a href="https://letterboxd.com/oni_le_chan/" target="_blank" class="letterboxd-link">Mon Profil Letterboxd</a>
            <a href="https://l-oeil-critique.netlify.app/" target="_blank" class="letterboxd-link">Retour à l'Accueil</a>
        </div>
    </header>

    <main class="main-content">
        <section class="critiques-films">
            <div class="container">
                <h2 class="section-title">Dernières Critiques</h2>
                <div class="film-grid">
"""
    
    # DEBUG : Compteur pour voir combien d'items sont traités - REMOVED
    # item_count = 0 

    for item in root.findall('.//item'):
        # item_count += 1 # Incrémente le compteur - REMOVED
        
        full_title = item.find('title').text if item.find('title') is not None else ''
        link = item.find('link').text if item.find('link') is not None else '#'
        description_html = item.find('description').text if item.find('description') is not None else ''
        
        # DEBUG : Affiche le titre de chaque film trouvé - REMOVED
        # print(f"DEBUG: Traitement du film: {full_title}") 

        # Extraire le titre du film et l'année
        match_title = re.match(r'^(.*?),\s*(\d{4})', full_title)
        film_title = match_title.group(1).strip() if match_title else full_title
        film_year = match_title.group(2) if match_title else ''

        # --- GESTION DES ÉTOILES AVEC FONT AWESOME ---
        rating_html = ''
        lb_member_rating = item.find('{https://letterboxd.com}memberRating')
        if lb_member_rating is not None and lb_member_rating.text:
            try:
                rating_value = float(lb_member_rating.text)
                rating_html = '<span class="rating-stars">'
                for _ in range(int(rating_value)): # Étoiles pleines
                    rating_html += '<i class="fas fa-star"></i>'
                if rating_value - int(rating_value) >= 0.5: # Demi-étoile
                    rating_html += '<i class="fas fa-star-half-alt"></i>'
                # Ajouter des étoiles vides pour un total de 5, si désiré
                for _ in range(int(5 - rating_value - (0.5 if rating_value - int(rating_value) >= 0.5 else 0))):
                     rating_html += '<i class="far fa-star"></i>'
                rating_html += '</span>'
            except ValueError:
                pass
        # Si la note n'est pas numérique mais qu'il y a des étoiles dans le titre (ex: ★★★★★)
        elif re.search(r'★+', full_title):
            num_full_stars = len(re.search(r'★+', full_title).group(0))
            rating_html = '<span class="rating-stars">'
            for _ in range(num_full_stars):
                rating_html += '<i class="fas fa-star"></i>'
            rating_html += '</span>'
        # --- FIN GESTION ÉTOILES ---

        # Extraire l'URL de l'image de la description HTML
        image_url = ''
        match_img = re.search(r'<img src="(.*?)"', description_html)
        if match_img:
            image_url = match_img.group(1)

        # Extraire le texte de la critique de la description HTML
        review_text = description_html
        review_text = re.sub(r'^.*?<p>(.*?)<\/p>', r'\1', review_text, 1, flags=re.DOTALL) # Supprime tout avant le premier <p> après l'image
        review_text = re.sub(r'<[^>]+>', '', review_text).strip() # Supprime toutes les balises HTML restantes
        review_text = review_text.replace('&nbsp;', ' ').replace('&#8230;', '...').replace('…', '...') # Nettoyage des entités
        review_text = html.unescape(review_text) # Utilise html.unescape pour bien gérer toutes les entités HTML
        
        # DEBUG : Affiche le texte de la critique extrait (les 100 premiers caractères) - REMOVED
        # print(f"DEBUG: Review text (first 100 chars): {review_text[:100]}...")

        formatted_review_text = review_text.replace('\n', '<br />')

        html_output += f"""
            <div class="film-item">
                {f'<img src="{image_url}" alt="Affiche de {film_title}" class="film-poster">' if image_url else ''}
                <div class="film-content">
                    <h3 class="film-title">{film_title} ({film_year})</h3>
                    {f'<p class="film-rating">Note: {rating_html}</p>' if rating_html else ''}
                    <p class="film-review-text">{formatted_review_text}</p>
                    <a href="{link}" target="_blank" rel="noopener noreferrer" class="button-letterboxd">Voir sur Letterboxd</a>
                </div>
            </div>
"""

    html_output += """
                </div>
            </div>
        </section>
    </main>

    <footer class="main-footer">
        <div class="container">
            <p>&copy; 2025 Oni Lechan. Données via Letterboxd RSS.</p>
        </div>
    </footer>
</body>
</html>
"""
    # DEBUG : Affiche le nombre total d'items traités - REMOVED
    # print(f"DEBUG: Nombre total de films traités: {item_count}") 

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
    # print(f"DEBUG: Site généré avec succès dans {output_file} !") # Debug print - REMOVED

if __name__ == "__main__":
    generate_html_from_rss(RSS_FEED_URL, OUTPUT_HTML_FILE)