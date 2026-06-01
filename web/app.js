/* ==========================================================================
   CineRank — Frontend Application Logic
   Segurança: DOM construído exclusivamente via createElement / textContent.
              Nenhum uso de innerHTML, outerHTML ou document.write.
   ========================================================================== */

(function () {
  'use strict';

  // -----------------------------------------------------------------------
  // State
  // -----------------------------------------------------------------------
  let movies = [];       // Array de { title, year, rating, image, imdb_rank }
  let ratings = {};      // { index: nota }
  let currentIndex = 0;  // Índice do card central no carrossel

  function getApiBaseUrl() {
    if (window.location.protocol === 'file:') {
      return 'http://127.0.0.1:5000';
    }
    return window.location.origin;
  }

  function apiFetch(path, options) {
    return fetch(getApiBaseUrl() + path, options);
  }

  function buildLocalPoster(title, rank) {
    var safeTitle = String(title || 'Filme');
    var lines = [];
    if (safeTitle.length <= 20) {
      lines = [safeTitle];
    } else if (safeTitle.length <= 40) {
      lines = [safeTitle.slice(0, 20), safeTitle.slice(20)];
    } else {
      lines = [safeTitle.slice(0, 20), safeTitle.slice(20, 40), safeTitle.slice(40, 60)];
    }

    var poster = document.createElement('div');
    poster.className = 'card-poster card-poster-fallback';

    var badge = document.createElement('div');
    badge.className = 'card-poster-fallback-badge';
    badge.textContent = '#' + (rank || '?');
    poster.appendChild(badge);

    var titleBox = document.createElement('div');
    titleBox.className = 'card-poster-fallback-title';
    lines.forEach(function (line) {
      var span = document.createElement('span');
      span.textContent = line;
      titleBox.appendChild(span);
    });
    poster.appendChild(titleBox);

    var footer = document.createElement('div');
    footer.className = 'card-poster-fallback-footer';
    footer.textContent = 'Poster indisponível';
    poster.appendChild(footer);

    return poster;
  }

  // -----------------------------------------------------------------------
  // DOM References
  // -----------------------------------------------------------------------
  const screenInput    = document.getElementById('screen-input');
  const screenCarousel = document.getElementById('screen-carousel');
  const screenResults  = document.getElementById('screen-results');

  // Screen 1
  const inputCount   = document.getElementById('movie-count');
  const btnFetch     = document.getElementById('btn-fetch');
  const loadingFetch = document.getElementById('loading-fetch');
  const errorFetch   = document.getElementById('error-fetch');

  // Screen 2
  const carouselTrack   = document.getElementById('carousel-track');
  const btnPrev         = document.getElementById('btn-prev');
  const btnNext         = document.getElementById('btn-next');
  const carouselCounter = document.getElementById('carousel-counter');
  const progressFill    = document.getElementById('progress-fill');
  const btnSubmit       = document.getElementById('btn-submit');
  const ratedCountEl    = document.getElementById('rated-count');
  const loadingCompare  = document.getElementById('loading-compare');
  const errorCompare    = document.getElementById('error-compare');

  // Screen 3
  const ringFill         = document.getElementById('ring-fill');
  const scoreNumber      = document.getElementById('score-number');
  const interpretText    = document.getElementById('interpretation-text');
  const inversionsInfo   = document.getElementById('inversions-info');
  const chartCanvas      = document.getElementById('chart-canvas');
  const imdbRankingList  = document.getElementById('imdb-ranking-list');
  const userRankingList  = document.getElementById('user-ranking-list');
  const btnRestart       = document.getElementById('btn-restart');

  // -----------------------------------------------------------------------
  // Screen Navigation
  // -----------------------------------------------------------------------
  function showScreen(screen) {
    screenInput.classList.remove('active');
    screenCarousel.classList.remove('active');
    screenResults.classList.remove('active');
    screen.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // -----------------------------------------------------------------------
  // Helpers
  // -----------------------------------------------------------------------
  function showError(el, msg) {
    el.textContent = msg;
    el.classList.add('active');
  }

  function hideError(el) {
    el.textContent = '';
    el.classList.remove('active');
  }

  function showLoading(el) { el.classList.add('active'); }
  function hideLoading(el) { el.classList.remove('active'); }

  // -----------------------------------------------------------------------
  // SCREEN 1 — Buscar filmes
  // -----------------------------------------------------------------------
  btnFetch.addEventListener('click', async function () {
    hideError(errorFetch);

    const n = parseInt(inputCount.value, 10);
    if (isNaN(n) || n < 5 || n > 250) {
      showError(errorFetch, 'Digite um número entre 5 e 250.');
      return;
    }

    btnFetch.disabled = true;
    showLoading(loadingFetch);

    try {
      const res = await apiFetch('/api/movies?n=' + encodeURIComponent(n));
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Erro ao buscar filmes.');
      }

      movies = data.movies;
      ratings = {};
      currentIndex = 0;
      buildCarousel();
      updateCarousel();
      updateProgress();
      showScreen(screenCarousel);
    } catch (err) {
      showError(errorFetch, err.message);
    } finally {
      btnFetch.disabled = false;
      hideLoading(loadingFetch);
    }
  });

  // Allow Enter key to trigger fetch
  inputCount.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { btnFetch.click(); }
  });

  // -----------------------------------------------------------------------
  // SCREEN 2 — Carrossel
  // -----------------------------------------------------------------------

  /**
   * Constrói os cards do carrossel usando DOM seguro.
   */
  function buildCarousel() {
    // Limpa cards antigos de forma segura
    carouselTrack.replaceChildren();

    movies.forEach(function (movie, idx) {
      var card = document.createElement('div');
      card.className = 'movie-card';
      card.dataset.index = idx;

      // Poster
      var posterDiv = document.createElement('div');
      posterDiv.className = 'card-poster';

      if (movie.image) {
        var img = document.createElement('img');
        img.src = movie.image;
        img.alt = movie.title;
        img.loading = 'lazy';
        img.addEventListener('error', function () {
          if (this.parentNode && this.parentNode.classList.contains('card-poster')) {
            this.parentNode.replaceWith(buildLocalPoster(movie.title, movie.imdb_rank));
          }
        });
        posterDiv.appendChild(img);
      } else {
        posterDiv.replaceWith(buildLocalPoster(movie.title, movie.imdb_rank));
      }

      card.appendChild(posterDiv);

      // Body
      var body = document.createElement('div');
      body.className = 'card-body';

      var rankLabel = document.createElement('div');
      rankLabel.className = 'card-rank';
      rankLabel.textContent = '#' + movie.imdb_rank + ' IMDb';
      body.appendChild(rankLabel);

      var title = document.createElement('div');
      title.className = 'card-title';
      title.textContent = movie.title;
      title.title = movie.title; // tooltip para títulos longos
      body.appendChild(title);

      var meta = document.createElement('div');
      meta.className = 'card-meta';

      if (movie.year) {
        var yearSpan = document.createElement('span');
        yearSpan.textContent = movie.year + ' ';
        meta.appendChild(yearSpan);
      }

      if (movie.rating) {
        var badge = document.createElement('span');
        badge.className = 'imdb-badge';
        badge.textContent = '⭐ ' + movie.rating;
        meta.appendChild(badge);
      }

      body.appendChild(meta);

      // Rating input
      var ratingGroup = document.createElement('div');
      ratingGroup.className = 'rating-input-group';

      var ratingLabel = document.createElement('label');
      ratingLabel.textContent = 'Sua nota:';
      ratingLabel.setAttribute('for', 'rating-' + idx);
      ratingGroup.appendChild(ratingLabel);

      var ratingInput = document.createElement('input');
      ratingInput.type = 'number';
      ratingInput.id = 'rating-' + idx;
      ratingInput.className = 'rating-input';
      ratingInput.min = '0';
      ratingInput.max = '10';
      ratingInput.step = '0.1';
      ratingInput.placeholder = '—';
      ratingInput.setAttribute('aria-label', 'Nota para ' + movie.title);

      ratingInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          this.dispatchEvent(new Event('change', { bubbles: true }));
          if (currentIndex < movies.length - 1) {
            currentIndex++;
            updateCarousel();
          }
          return;
        }

        if (e.key === 'ArrowLeft' && currentIndex > 0) {
          e.preventDefault();
          currentIndex--;
          updateCarousel();
        } else if (e.key === 'ArrowRight' && currentIndex < movies.length - 1) {
          e.preventDefault();
          currentIndex++;
          updateCarousel();
        }
      });

      if (ratings[idx] !== undefined) {
        ratingInput.value = ratings[idx];
        ratingInput.classList.add('rated');
      }

      ratingInput.addEventListener('change', function () {
        var val = parseFloat(this.value);
        if (!isNaN(val) && val >= 0 && val <= 10) {
          ratings[idx] = val;
          this.classList.add('rated');
        } else if (this.value === '') {
          delete ratings[idx];
          this.classList.remove('rated');
        }
        updateProgress();
      });

      ratingGroup.appendChild(ratingInput);
      body.appendChild(ratingGroup);

      card.appendChild(body);

      // Clicar no card adjacente faz navegar
      card.addEventListener('click', function () {
        var cardIdx = parseInt(this.dataset.index, 10);
        if (cardIdx !== currentIndex) {
          currentIndex = cardIdx;
          updateCarousel();
        }
      });

      carouselTrack.appendChild(card);
    });
  }

  /**
   * Atualiza as posições/classes dos cards no carrossel.
   */
  function updateCarousel() {
    var cards = carouselTrack.querySelectorAll('.movie-card');
    var n = movies.length;

    cards.forEach(function (card) {
      var idx = parseInt(card.dataset.index, 10);
      var diff = idx - currentIndex;

      // Remove todas as classes de posição
      card.classList.remove(
        'card-center', 'card-left-1', 'card-right-1',
        'card-left-2', 'card-right-2'
      );

      if (diff === 0) {
        card.classList.add('card-center');
      } else if (diff === -1) {
        card.classList.add('card-left-1');
      } else if (diff === 1) {
        card.classList.add('card-right-1');
      } else if (diff === -2) {
        card.classList.add('card-left-2');
      } else if (diff === 2) {
        card.classList.add('card-right-2');
      } else {
        // Esconder cards distantes
        card.style.opacity = '0';
        card.style.pointerEvents = 'none';
        // Posicionar fora da tela baseado na direção
        if (diff < 0) {
          card.style.transform = 'translate(calc(-50% - 500px), -50%) scale(0.3)';
        } else {
          card.style.transform = 'translate(calc(-50% + 500px), -50%) scale(0.3)';
        }
        card.style.zIndex = '0';
        return;
      }

      // Resetar estilos inline para cards visíveis (as classes CSS cuidam)
      card.style.opacity = '';
      card.style.pointerEvents = '';
      card.style.transform = '';
      card.style.zIndex = '';
    });

    // Atualizar contador
    carouselCounter.textContent = (currentIndex + 1) + ' / ' + n;

    // Atualizar estado dos botões
    btnPrev.disabled = currentIndex === 0;
    btnNext.disabled = currentIndex === n - 1;

    // Focar no input do card central
    var centerInput = document.getElementById('rating-' + currentIndex);
    if (centerInput) {
      setTimeout(function () { centerInput.focus(); }, 400);
    }
  }

  /**
   * Atualiza a barra de progresso e o botão de submit.
   */
  function updateProgress() {
    var total = movies.length;
    var rated = Object.keys(ratings).length;
    var pct = total > 0 ? (rated / total) * 100 : 0;

    progressFill.style.width = pct + '%';
    ratedCountEl.textContent = rated + ' de ' + total + ' filmes avaliados';
    btnSubmit.disabled = rated < total;
  }

  // Navigation
  btnPrev.addEventListener('click', function () {
    if (currentIndex > 0) {
      currentIndex--;
      updateCarousel();
    }
  });

  btnNext.addEventListener('click', function () {
    if (currentIndex < movies.length - 1) {
      currentIndex++;
      updateCarousel();
    }
  });

  // Keyboard nav
  document.addEventListener('keydown', function (e) {
    if (!screenCarousel.classList.contains('active')) return;

    // Não interceptar se estiver digitando no input
    if (document.activeElement && document.activeElement.classList.contains('rating-input')) {
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'Enter') return;
    }

    if (e.key === 'ArrowLeft' && currentIndex > 0) {
      currentIndex--;
      updateCarousel();
    } else if (e.key === 'ArrowRight' && currentIndex < movies.length - 1) {
      currentIndex++;
      updateCarousel();
    }
  });

  // -----------------------------------------------------------------------
  // Enviar avaliações
  // -----------------------------------------------------------------------
  btnSubmit.addEventListener('click', async function () {
    hideError(errorCompare);

    var movieTitles = movies.map(function (m) { return m.title; });
    var ratingValues = movies.map(function (_, i) { return ratings[i]; });

    // Validação final
    for (var i = 0; i < ratingValues.length; i++) {
      if (ratingValues[i] === undefined || ratingValues[i] === null) {
        showError(errorCompare, 'Faltam notas. Avalie todos os filmes.');
        return;
      }
    }

    btnSubmit.disabled = true;
    showLoading(loadingCompare);

    try {
      var res = await apiFetch('/api/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          movies: movieTitles,
          ratings: ratingValues,
        }),
      });

      var data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Erro ao calcular similaridade.');
      }

      renderResults(data);
      showScreen(screenResults);
    } catch (err) {
      showError(errorCompare, err.message);
    } finally {
      btnSubmit.disabled = false;
      hideLoading(loadingCompare);
    }
  });

  // -----------------------------------------------------------------------
  // SCREEN 3 — Resultados
  // -----------------------------------------------------------------------

  function renderResults(data) {
    // Score ring animation
    var pct = data.similarity_pct;
    var circumference = 2 * Math.PI * 80; // r=80
    var offset = circumference - (pct / 100) * circumference;

    // Reset and animate
    ringFill.style.strokeDashoffset = circumference;
    scoreNumber.textContent = '0%';

    requestAnimationFrame(function () {
      setTimeout(function () {
        ringFill.style.strokeDashoffset = offset;
        animateNumber(scoreNumber, 0, pct, 1500);
      }, 100);
    });

    // Interpretation
    interpretText.textContent = data.interpretation;
    inversionsInfo.textContent =
      data.inversions + ' inversões de um máximo de ' + data.max_inversions;

    // Draw chart
    drawComparisonChart(data);

    // Build ranking lists
    buildRankingList(imdbRankingList, data.imdb_ranking, false);
    buildRankingList(userRankingList, data.user_ranking, true);
  }

  /**
   * Anima um número de start até end no elemento.
   */
  function animateNumber(el, start, end, duration) {
    var startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      var progress = Math.min((timestamp - startTime) / duration, 1);
      var current = start + (end - start) * easeOutCubic(progress);
      el.textContent = current.toFixed(1) + '%';
      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }

    requestAnimationFrame(step);
  }

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  /**
   * Desenha o gráfico de barras agrupadas no Canvas.
   * Para cada filme, mostra duas barras: posição no ranking IMDb vs posição no ranking do usuário.
   */
  function drawComparisonChart(data) {
    var n = data.imdb_ranking.length;
    var canvas = chartCanvas;
    var dpr = window.devicePixelRatio || 1;

    // Dimensionar canvas
    var chartWidth = Math.max(600, n * 80);
    canvas.style.width = chartWidth + 'px';
    canvas.style.height = '400px';
    canvas.width = chartWidth * dpr;
    canvas.height = 400 * dpr;

    var ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    // Limites
    var padTop = 30;
    var padBottom = 100;
    var padLeft = 50;
    var padRight = 20;
    var plotW = chartWidth - padLeft - padRight;
    var plotH = 400 - padTop - padBottom;

    // Limpar
    ctx.clearRect(0, 0, chartWidth, 400);

    // Construir dados: para cada filme (na ordem IMDb), encontrar sua posição no ranking do usuário
    var moviePositions = [];
    for (var i = 0; i < n; i++) {
      var imdbTitle = data.imdb_ranking[i].title;
      var userPos = -1;
      for (var j = 0; j < data.user_ranking.length; j++) {
        if (data.user_ranking[j].title === imdbTitle) {
          userPos = data.user_ranking[j].rank;
          break;
        }
      }
      moviePositions.push({
        title: imdbTitle,
        imdbRank: data.imdb_ranking[i].rank,
        userRank: userPos,
      });
    }

    var barGroupWidth = plotW / n;
    var barWidth = Math.min(barGroupWidth * 0.35, 30);
    var gap = 4;

    // Eixo Y (posições de 1 a n, invertido: 1 no topo)
    ctx.strokeStyle = 'rgba(155, 89, 182, 0.15)';
    ctx.lineWidth = 1;
    ctx.fillStyle = '#7b6fa0';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';

    var ySteps = Math.min(n, 10);
    for (var s = 0; s <= ySteps; s++) {
      var rankVal = Math.round(1 + (n - 1) * (s / ySteps));
      var y = padTop + (rankVal - 1) / (n - 1) * plotH;

      ctx.beginPath();
      ctx.moveTo(padLeft, y);
      ctx.lineTo(chartWidth - padRight, y);
      ctx.stroke();

      ctx.fillText(rankVal.toString(), padLeft - 8, y);
    }

    // Label eixo Y
    ctx.save();
    ctx.translate(12, padTop + plotH / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = 'center';
    ctx.fillStyle = '#b8a9d4';
    ctx.font = '12px Inter, sans-serif';
    ctx.fillText('Posição no Ranking', 0, 0);
    ctx.restore();

    // Barras: quanto melhor o ranking, maior a barra.
    for (var k = 0; k < n; k++) {
      var x = padLeft + k * barGroupWidth + barGroupWidth / 2;

      var imdbValue = n - moviePositions[k].imdbRank + 1;
      var userValue = n - moviePositions[k].userRank + 1;

      var imdbBarH = imdbValue / n * plotH;
      var userBarH = userValue / n * plotH;

      var imdbY = padTop + plotH - imdbBarH;
      var userY = padTop + plotH - userBarH;

      // IMDb bar (purple)
      drawRoundedBar(ctx, x - barWidth - gap / 2, imdbY, barWidth, imdbBarH, 4, '#9b59b6', 0.85);

      // User bar (green)
      drawRoundedBar(ctx, x + gap / 2, userY, barWidth, userBarH, 4, '#6abf69', 0.85);

      // Rank labels acima das barras
      ctx.fillStyle = '#e8daf5';
      ctx.font = 'bold 10px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.fillText(moviePositions[k].imdbRank.toString(), x - barWidth / 2 - gap / 2, Math.max(imdbY - 6, padTop + 10));
      ctx.fillText(moviePositions[k].userRank.toString(), x + barWidth / 2 + gap / 2, Math.max(userY - 6, padTop + 10));

      // Movie title (eixo X)
      ctx.save();
      ctx.translate(x, 400 - padBottom + 12);
      ctx.rotate(-Math.PI / 4);
      ctx.textAlign = 'right';
      ctx.textBaseline = 'top';
      ctx.fillStyle = '#7b6fa0';
      ctx.font = '10px Inter, sans-serif';
      var shortTitle = moviePositions[k].title.length > 18
        ? moviePositions[k].title.substring(0, 16) + '…'
        : moviePositions[k].title;
      ctx.fillText(shortTitle, 0, 0);
      ctx.restore();
    }
  }

  /**
   * Desenha uma barra com bordas arredondadas no Canvas.
   */
  function drawRoundedBar(ctx, x, y, w, h, r, color, alpha) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  /**
   * Constrói a lista de ranking usando DOM seguro.
   */
  function buildRankingList(container, items, showRating) {
    container.replaceChildren();

    items.forEach(function (item) {
      var row = document.createElement('div');
      row.className = 'ranking-item';

      var pos = document.createElement('div');
      pos.className = 'ranking-position';
      pos.textContent = item.rank;
      row.appendChild(pos);

      var titleEl = document.createElement('span');
      titleEl.className = 'ranking-movie-title';
      titleEl.textContent = item.title;
      titleEl.title = item.title;
      row.appendChild(titleEl);

      if (showRating && item.rating !== undefined) {
        var badge = document.createElement('span');
        badge.className = 'ranking-rating-badge';
        badge.textContent = '⭐ ' + item.rating.toFixed(1);
        row.appendChild(badge);
      }

      container.appendChild(row);
    });
  }

  // -----------------------------------------------------------------------
  // Reiniciar
  // -----------------------------------------------------------------------
  btnRestart.addEventListener('click', function () {
    movies = [];
    ratings = {};
    currentIndex = 0;
    carouselTrack.replaceChildren();
    imdbRankingList.replaceChildren();
    userRankingList.replaceChildren();
    showScreen(screenInput);
  });

})();
