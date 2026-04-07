import csv
import re
import html
from typing import Optional

# ------------------------------
# CONFIGURATION
# ------------------------------
RATINGS_CSV = "LB/ratings.csv"
REVIEWS_CSV = "LB/reviews.csv"
OUTPUT_HTML = "LB/films.html"

# ------------------------------
# UTILITAIRES
# ------------------------------

def generate_star_rating(rating: Optional[str]) -> str:
    """Convertit une note (ex: 4.5) en icônes Font Awesome."""
    if not rating or rating == "":
        return ""
    try:
        val = float(rating)
        full = int(val)
        half = (val - full) >= 0.5
        empty = 5 - full - (1 if half else 0)
        
        stars_html = (
            '<span class="rating-stars">'
            + '<i class="fas fa-star"></i>' * full
            + ('<i class="fas fa-star-half-alt"></i>' if half else "")
            + '<i class="far fa-star"></i>' * empty
            + '</span>'
        )
        return stars_html
    except ValueError:
        return ""

def rating_to_label(rating: Optional[str]) -> str:
    """Labels personnalisés basés sur ta bio Letterboxd."""
    if not rating: return ""
    val = float(rating)
    if val >= 5.0:  return "PEAK CINEMA"
    if val >= 4.5:  return "Chef-d'œuvre"
    if val >= 4.0:  return "Excellent"
    if val >= 3.5:  return "Je recommande"
    if val >= 3.0:  return "Bon film"
    if val >= 2.5:  return "Basique/Ok"
    if val >= 2.0:  return "Moyen"
    if val >= 1.5:  return "Nul"
    if val >= 1.0:  return "Catastrophique"
    return "Atrocité"

# ------------------------------
# GÉNÉRATEUR PRINCIPAL
# ------------------------------

def generate_site_from_csv():
    # 1. Charger les critiques dans un dictionnaire pour un accès rapide
    # Clé : URI du film, Valeur : Texte de la critique
    reviews_dict = {}
    try:
        with open(REVIEWS_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                reviews_dict[row['Letterboxd URI']] = row['Review']
    except FileNotFoundError:
        print("⚠️ reviews.csv non trouvé, les films n'auront pas de texte.")

    films_html = []

    # 2. Lire les notes (historique complet)
    try:
        with open(RATINGS_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # On trie par date (du plus récent au plus ancien)
            sorted_rows = sorted(list(reader), key=lambda x: x['Date'], reverse=True)

            for row in sorted_rows:
                title = row['Name']
                year = row['Year']
                rating = row['Rating']
                link = row['Letterboxd URI']
                
                # Récupérer la review si elle existe
                review_text = reviews_dict.get(link, "")
                # Nettoyage rapide du texte (limiter la longueur pour la grille)
                if len(review_text) > 300:
                    review_text = review_text[:300] + "..."

                rating_html = generate_star_rating(rating)
                rating_label = rating_to_label(rating)
                
                # Note : On ne peut pas récupérer l'URL de l'image directement dans le CSV.
                # Astuce : Letterboxd ne fournit pas l'image dans l'export, mais on peut utiliser 
                # un placeholder ou laisser l'espace pour le design.
                
                film_block = f"""
<article class="film-item">
  <div class="film-content">
    <div class="film-header">
      <h3 class="film-title">{title}</h3>
      <span class="film-year">({year})</span>
    </div>
    <div class="film-rating">
        {rating_html}
        <span class="rating-badge">{rating_label}</span>
    </div>
    <p class="film-review-text">{html.escape(review_text)}</p>
    <div class="film-actions">
      <a href="{link}" target="_blank" class="button-letterboxd">Voir sur Letterboxd</a>
    </div>
  </div>
</article>"""
                films_html.append(film_block.strip())

        # 3. Écriture du fichier final
        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write("\n".join(films_html))
            
        print(f"✅ Terminé ! {len(films_html)} films extraits de tes fichiers CSV.")

    except Exception as e:
        print(f"❌ Erreur lors de la lecture du CSV : {e}")

if __name__ == "__main__":
    generate_site_from_csv()