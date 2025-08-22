import requests
import xml.etree.ElementTree as ET
import re
import html
from bs4 import BeautifulSoup

# --- CONFIG ---
RSS_FEED_URL = 'https://letterboxd.com/oni_le_chan/rss/'
LISTS_URL = 'https://letterboxd.com/oni_le_chan/lists/'
FILMS_HTML_FILE = 'films.html'
LISTS_HTML_FILE = 'lists.html'
LIST_KEYWORD = 'SAGA'  # Mot clé pour identifier une liste dans le RSS

# --- FILMS ---
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

        # Ignorer les listes identifiées par le mot clé
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


# --- LISTES ---
def generate_lists_html(rss_url, lists_url, output_file):
    lists_html = ""

    # 1️⃣ Listes détectées dans le RSS
    try:
        response = requests.get(rss_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        for item in root.findall('.//item'):
            title_full = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else '#'
            description = item.find('description').text if item.find('description') is not None else ''

            if LIST_KEYWORD in title_full.upper():
                # Extraire films de la liste
                films = [f.strip() for f in re.split(r'\s{2,}', description) if f.strip()]
                ranking_html = "<ol>" + "".join(f"<li>{f}</li>" for f in films) + "</ol>" if films else ""
                match_img = re.search(r'<img src="(.*?)"', description)
                image_url = match_img.group(1) if match_img else ''

                lists_html += f"""
                <div class="film-item">
                    {f'<img src="{image_url}" alt="Liste {title_full}" class="film-poster">' if image_url else ''}
                    <div class="film-content">
                        <h3 class="film-title">{title_full}</h3>
                        {ranking_html}
                        <a href="{link}" target="_blank" rel="noopener noreferrer" class="button-letterboxd">Voir sur Letterboxd</a>
                    </div>
                </div>
                """
    except Exception as e:
        lists_html += f"<p>Erreur récupération listes RSS: {e}</p>"

    # 2️⃣ Listes officielles depuis /lists/
    try:
        res = requests.get(lists_url)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, 'html.parser')
        list_items = soup.select('li.list-item')
        for li in list_items:
            a_tag = li.find('a')
            if not a_tag:
                continue
            list_title = a_tag.get_text(strip=True)
            list_link = 'https://letterboxd.com' + a_tag['href']

            # Récupérer les films et première image pour ranking
            try:
                list_res = requests.get(list_link)
                list_res.raise_for_status()
                list_soup = BeautifulSoup(list_res.content, 'html.parser')
                films = [img['alt'] for img in list_soup.select('td.poster-container img[alt]')]
                ranking_html = "<ol>" + "".join(f"<li>{f}</li>" for f in films) + "</ol>" if films else ""
                first_img_tag = list_soup.select_one('td.poster-container img')
                first_img_url = first_img_tag['data-src'] if first_img_tag and first_img_tag.has_attr('data-src') else ''
            except Exception as e:
                ranking_html = ""
                first_img_url = ''

            lists_html += f"""
            <div class="film-item">
                {f'<img src="{first_img_url}" alt="Liste {list_title}" class="film-poster">' if first_img_url else ''}
                <div class="film-content">
                    <h3 class="film-title">{list_title}</h3>
                    {ranking_html}
                    <a href="{list_link}" target="_blank" rel="noopener noreferrer" class="button-letterboxd">Voir la liste</a>
                </div>
            </div>
            """
    except Exception as e:
        lists_html += f"<p>Impossible de récupérer les listes: {e}</p>"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(lists_html)
    print(f"Listes HTML généré dans {output_file}")


if __name__ == "__main__":
    generate_films_html(RSS_FEED_URL, FILMS_HTML_FILE)
    generate_lists_html(RSS_FEED_URL, LISTS_URL, LISTS_HTML_FILE)
    print("Génération terminée.")
# --- END OF SCRIPT ---