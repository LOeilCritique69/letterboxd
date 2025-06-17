fetch('/api/films')
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById('films');
    data.forEach(film => {
      const div = document.createElement('div');
      div.className = 'film';
      div.innerHTML = `
        <img src="${film.image}" alt="${film.title}">
        <div class="film-content">
          <h2>${film.title}</h2>
          <div class="rating">★ ${film.rating || 'N/A'}</div>
          <div class="review">${film.review}</div>
        </div>
      `;
      container.appendChild(div);
    });
  })
  .catch(err => {
    document.getElementById('films').innerText = "Erreur lors du chargement des films.";
    console.error(err);
  });
