// Charge les films depuis l'API et affiche dans #film-list
async function loadFilms() {
  const container = document.getElementById("film-list");
  container.innerHTML = "<p>Chargement des films...</p>";

  try {
    const res = await fetch("/api/films");
    if (!res.ok) throw new Error(`Erreur HTTP ${res.status}`);
    const films = await res.json();

    if (films.length === 0) {
      container.innerHTML = "<p>Aucun film noté trouvé.</p>";
      return;
    }

    container.innerHTML = ""; // Clear message

    films.forEach(film => {
      const card = document.createElement("div");
      card.className = "film-card";

      card.innerHTML = `
        <img src="${film.poster}" alt="${film.title}" class="film-poster" />
        <div class="film-info">
          <div class="film-title">${film.title}</div>
          <div class="film-rating">${film.rating || ""}</div>
          <a href="${film.link}" target="_blank" rel="noopener" class="film-link">Voir sur Letterboxd</a>
        </div>
      `;

      container.appendChild(card);
    });

  } catch (error) {
    container.innerHTML = `<p>Erreur lors du chargement des films : ${error.message}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", loadFilms);
