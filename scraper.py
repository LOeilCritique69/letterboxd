import requests
from bs4 import BeautifulSoup
import json

USERNAME = "oni_le_chan"
BASE_URL = f"https://letterboxd.com/{USERNAME}/films/ratings/"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def scrape_ratings(page=1):
    url = f"{BASE_URL}page/{page}/"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Erreur HTTP {response.status_code} pour la page {page}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    film_list = soup.select(".poster-container")

    data = []
    for film in film_list:
        film_data = {}
        anchor = film.find("a")
        img = film.find("img")
        rating_span = film.select_one(".rating")

        if anchor:
            film_data["link"] = "https://letterboxd.com" + anchor["href"]
        if img:
            film_data["title"] = img["alt"]
            film_data["poster"] = img["data-src"] if "data-src" in img.attrs else img["src"]
        if rating_span:
            film_data["rating"] = rating_span.text.strip()

        data.append(film_data)

    return data


def scrape_all_pages(max_pages=5):
    all_data = []
    for page in range(1, max_pages + 1):
        page_data = scrape_ratings(page)
        if not page_data:
            break
        all_data.extend(page_data)
    return all_data


def save_to_json(data, filename="data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("Scraping en cours...")
    result = scrape_all_pages(max_pages=10)
    save_to_json(result)
    print(f"{len(result)} films extraits et sauvegardés dans data.json")
