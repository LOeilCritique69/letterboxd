import requests
from bs4 import BeautifulSoup
import json

USERNAME = "oni_le_chan"
URL = f"https://letterboxd.com/{USERNAME}/films/reviews/by/date/"

def get_reviews():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    film_elements = soup.select('.film-detail-content')

    films = []
    for film_detail in film_elements:
        parent = film_detail.find_parent('li')
        title_tag = film_detail.select_one('.headline-2')
        review_tag = film_detail.select_one('.truncate p')
        rating_tag = film_detail.select_one('.rating')
        poster_img = parent.select_one('.film-poster img')

        if not title_tag or not poster_img:
            continue

        film = {
            "title": title_tag.text.strip(),
            "rating": rating_tag['class'][1][-1:] if rating_tag else None,
            "review": review_tag.text.strip() if review_tag else "",
            "image": poster_img['src']
        }

        films.append(film)

    return films

def save_data(films):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(films, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    films = get_reviews()
    save_data(films)
