#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script : letterboxd_films_parser.py
Description : Génère un HTML propre à partir du flux RSS Letterboxd.
Auteur : Yanis (refonte GPT-5)
"""

import requests
import xml.etree.ElementTree as ET
import re
import html
from bs4 import BeautifulSoup
from typing import Optional

# ------------------------------
# CONFIGURATION
# ------------------------------
RSS_FEED_URL = "https://letterboxd.com/oni_le_chan/rss/"
OUTPUT_HTML = "films.html"
LIST_KEYWORD = "SAGA"

# ------------------------------
# FONCTIONS UTILITAIRES
# ------------------------------
def extract_text_from_html(raw_html: str) -> str:
    """Nettoie et extrait le texte lisible d'une description HTML Letterboxd."""
    soup = BeautifulSoup(raw_html, "html.parser")

    # Supprime les images et balises inutiles
    for tag in soup(["img", "script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ").strip()
    return html.unescape(re.sub(r"\s+", " ", text))


def extract_image_url(description_html: str) -> Optional[str]:
    """Récupère l'URL de l'affiche du film à partir de la description HTML."""
    match = re.search(r'<img src="(.*?)"', description_html)
    return match.group(1) if match else None


def generate_star_rating(rating: Optional[str]) -> str:
    """Convertit une note numérique Letterboxd en icônes HTML."""
    if not rating:
        return ""

    try:
        rating_value = float(rating)
        full_stars = int(rating_value)
        half_star = rating_value - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)

        stars_html = (
            '<span class="rating-stars">'
            + '<i class="fas fa-star"></i>' * full_stars
            + ('<i class="fas fa-star-half-alt"></i>' if half_star else "")
            + '<i class="far fa-star"></i>' * empty_stars
            + "</span>"
        )
        return stars_html

    except ValueError:
        return ""


# ------------------------------
# COEUR DU SCRIPT
# ------------------------------
def generate_films_html(rss_url: str, output_file: str):
    """Génère un HTML complet à partir du flux RSS Letterboxd."""
    try:
        response = requests.get(rss_url, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except Exception as e:
        error_html = f"<p class='error'>Erreur de chargement du flux : {e}</p>"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(error_html)
        print("❌ Erreur lors du chargement du flux RSS.")
        return

    films_html = []

    for item in root.findall(".//item"):
        title_full = item.findtext("title", "")
        link = item.findtext("link", "#")
        description_html = item.findtext("description", "")

        # Ignore les listes Letterboxd (Sagas, etc.)
        if LIST_KEYWORD in title_full.upper():
            continue

        # Extraction du titre et de l'année
        match = re.match(r"^(.*?),\s*(\d{4})", title_full)
        film_title = match.group(1).strip() if match else title_full
        film_year = match.group(2) if match else "—"

        # Image du film
        image_url = extract_image_url(description_html)

        # Review nettoyée
        review_text = extract_text_from_html(description_html)
        review_text = review_text.replace("★", "").strip()

        # Note Letterboxd
        rating_node = item.find("{https://letterboxd.com}memberRating")
        rating_html = generate_star_rating(rating_node.text if rating_node is not None else None)

        film_html = f"""
        <article class="film-item">
            <div class="film-poster-container">
                {'<img src="' + image_url + '" alt="Affiche de ' + film_title + '" class="film-poster" loading="lazy">' if image_url else ''}
            </div>
            <div class="film-content">
                <h3 class="film-title">{film_title} <span class="film-year">({film_year})</span></h3>
                {f'<div class="film-rating">{rating_html}</div>' if rating_html else ''}
                <p class="film-review-text">{review_text}</p>
                <a href="{link}" target="_blank" rel="noopener noreferrer" class="button-letterboxd">Voir sur Letterboxd</a>
            </div>
        </article>
        """
        films_html.append(film_html.strip())

    # Structure finale
    final_html = f"""
    <!-- === FILMS IMPORTÉS DE LETTERBOXD === -->
    <section id="films-section" class="films-section">
        {''.join(films_html) if films_html else '<p>Aucun film trouvé.</p>'}
    </section>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_html.strip())

    print(f"✅ {len(films_html)} films générés dans {output_file}")


# ------------------------------
# MAIN
# ------------------------------
if __name__ == "__main__":
    print("🚀 Génération du flux Letterboxd en HTML...")
    generate_films_html(RSS_FEED_URL, OUTPUT_HTML)
    print("🎬 Terminé.")
