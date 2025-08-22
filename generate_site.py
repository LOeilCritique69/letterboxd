import requests
import xml.etree.ElementTree as ET
import re
import html
from bs4 import BeautifulSoup

# --- CONFIG ---
RSS_FEED_URL = 'https://letterboxd.com/oni_le_chan/rss/'
FILMS_HTML_FILE = 'films.html'
LIST_KEYWORD = 'SAGA'  # Mot clé pour identifier une liste dans le RSS

# --- FILMS / REVIEWS ---
def generate_films_html(rss_url, output_file):
    try:
        response = requests.get(rss_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except Exception as e:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"<p>Erreur de chargement films: {e}</p>")
        return

    films_html = ""
    for item in root.findall('.//item'):
        title_full = item.find('title').text if item.find('title') is not None else ''
        link = item.find('link').text if item.find('link') is not None else '#'
        description_html = item.find('description').text if item.find('description') is not None else ''

        # On ignore les listes
        if LIST_KEYWORD in title_full.upper():
            continue

        match_title = re.match(r'^(.*?),\s*(\d{4})', title_full)
        film_title = match_title.group(1).strip() if match_title else title_full
        film_year = match_title.group(2) if match_title else ''

        match_img = re.search(r'<img src="(.*?)"', description_html)
        image_url = match_img.group(1) if match_img else ''

        review_text = description_html
        review_text = re.sub(r'^.*?<p>(.*?)<\/p>', r'\1', review_text, count=1, flags=re.DOTALL)
        review_text = re.sub(r'<[^>]+>', '', review_text).strip()
        review_text = html.unescape(review_text)
        review_text = review_text.replace('\n', '<br />')

        lb_member_rating = item.find('{https://letterboxd.com}memberRating')
        rating_html = ''
        if lb_member_rating is not None and lb_member_rating.text:
            try:
                rating_value = float(lb_member_rating.text)
                rating_html = '<span class="rating-stars">'
                for _ in range(int(rating_value)):
                    rating_html += '<i class="fas fa-star"></i>'
                if rating_value - int(rating_value) >= 0.5:
                    rating_html += '<i class="fas fa-star-half-alt"></i>'
                for _ in range(int(5 - rating_value - (0.5 if rating_value - int(rating_value) >= 0.5 else 0))):
                    rating_html += '<i class="far fa-star"></i>'
                rating_html += '</span>'
            except ValueError:
                pass

        films_html += f"""
        <div class="film-item">
            {f'<img src="{image_url}" alt="Affiche de {film_title}" class="film-poster">' if image_url else ''}
            <div class="film-content">
                <h3 class="film-title">{film_title} ({film_year})</h3>
                {f'<p class="film-rating">Note: {rating_html}</p>' if rating_html else ''}
                <p class="film-review-text">{review_text}</p>
                <a href="{link}" target="_blank" rel="noopener noreferrer" class="button-letterboxd">Voir sur Letterboxd</a>
            </div>
        </div>
        """

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{films_html}")
    print(f"Films HTML généré dans {output_file}")


# --- MAIN ---
if __name__ == "__main__":
    generate_films_html(RSS_FEED_URL, FILMS_HTML_FILE)
    print("Génération terminée.")
