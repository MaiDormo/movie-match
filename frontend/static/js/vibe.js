const ENDPOINTS = {
    vibes: '/api/v1/vibes',
    moviesByVibe: '/api/v1/vibe/movies'
};

const CACHE_KEYS = {
    vibes: 'movieMatch:vibes',
    moviePrefix: 'movieMatch:vibeMovies:'
};

const CACHE_TTL_MS = 15 * 60 * 1000;

const state = {
    vibes: [],
    selectedVibes: new Set(),
    requestController: null
};

const els = {
    vibeList: document.getElementById('vibe-list'),
    discoverBtn: document.getElementById('discover-btn'),
    feedback: document.getElementById('feedback'),
    resultCount: document.getElementById('result-count'),
    resultsSection: document.getElementById('results-section'),
    loadingState: document.getElementById('loading-state'),
    emptyState: document.getElementById('empty-state'),
    movieGrid: document.getElementById('movie-grid')
};

function getCachedValue(key) {
    const raw = sessionStorage.getItem(key);
    if (!raw) return null;
    try {
        const p = JSON.parse(raw);
        if (Date.now() - p.timestamp > CACHE_TTL_MS) {
            sessionStorage.removeItem(key);
            return null;
        }
        return p.data;
    } catch {
        sessionStorage.removeItem(key);
        return null;
    }
}

function setCachedValue(key, data) {
    sessionStorage.setItem(key, JSON.stringify({ timestamp: Date.now(), data }));
}

function buildMovieCacheKey(vibes) {
    return `${CACHE_KEYS.moviePrefix}${[...vibes].map(v => v.toLowerCase()).sort().join(',')}`;
}

function setFeedback(text, kind = '') {
    els.feedback.textContent = text;
    els.feedback.className = 'feedback';
    if (kind) els.feedback.classList.add(kind);
}

function updateButton() {
    els.discoverBtn.disabled = state.selectedVibes.size === 0;
}

function escapeHtml(text) {
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function renderVibes(vibes) {
    if (!vibes.length) {
        els.vibeList.innerHTML = '<p class="feedback">No vibes available.</p>';
        return;
    }

    const frag = document.createDocumentFragment();
    vibes.forEach((vibe) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'vibe-pill';
        btn.dataset.vibeName = vibe.name;
        btn.textContent = vibe.name;
        btn.setAttribute('aria-pressed', state.selectedVibes.has(vibe.name) ? 'true' : 'false');
        if (state.selectedVibes.has(vibe.name)) {
            btn.classList.add('selected');
        }
        frag.appendChild(btn);
    });

    els.vibeList.innerHTML = '';
    els.vibeList.appendChild(frag);
}

async function loadVibes() {
    const cached = getCachedValue(CACHE_KEYS.vibes);
    if (cached && Array.isArray(cached) && cached.length) {
        state.vibes = cached;
        renderVibes(state.vibes);
    }

    try {
        const res = await fetch(ENDPOINTS.vibes);
        const payload = await res.json();
        if (!res.ok || payload.status === 'error') {
            throw new Error(payload.message || 'Failed to load vibes');
        }

        const vibes = payload.data?.vibes;
        if (!Array.isArray(vibes)) throw new Error('Invalid vibes format');

        state.vibes = vibes;
        setCachedValue(CACHE_KEYS.vibes, vibes);
        renderVibes(vibes);
        setFeedback('Ready. Select vibes and hit Find Movies.', 'success');
    } catch (err) {
        if (!state.vibes.length) {
            els.vibeList.innerHTML = `<p class="feedback error">${escapeHtml(err.message)}</p>`;
        }
        setFeedback(`Could not load vibes: ${err.message}`, 'error');
    }
}

function renderMovies(movies) {
    els.movieGrid.innerHTML = '';

    if (!Array.isArray(movies) || movies.length === 0) {
        els.emptyState.hidden = false;
        els.resultCount.textContent = '';
        return;
    }

    const frag = document.createDocumentFragment();
    movies.forEach((movie) => {
        const movieId = movie.imdbID || movie.id;
        if (!movieId) return;

        const title = movie.Title || movie.title || 'Unknown';
        const rating = movie.imdbRating || movie.vote_average;
        const year = movie.Year || (movie.release_date ? movie.release_date.slice(0, 4) : '');

        const card = document.createElement('a');
        card.className = 'movie-card';
        card.href = `/movie?id=${encodeURIComponent(movieId)}`;
        card.tabIndex = 0;

        const hasPoster = movie.Poster && movie.Poster !== 'N/A';
        const poster = hasPoster
            ? `<img class="poster" src="${escapeHtml(movie.Poster)}" alt="${escapeHtml(title)}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=poster-wrap style=background:var(--surface)><div style=display:grid;place-items:center;height:100%;color:var(--text-dim);font-size:0.75rem>No poster</div></div>'">`
            : `<div class="poster-wrap" style="display:grid;place-items:center;height:100%;color:var(--text-dim);font-size:0.75rem">No poster</div>`;

        const ratingHtml = rating && rating !== 'N/A'
            ? `<span class="movie-rating">★ ${escapeHtml(String(rating))}</span>`
            : '';

        card.innerHTML = `
            <div class="poster-wrap">
                ${poster}
                <div class="poster-overlay">${ratingHtml}</div>
            </div>
            <div class="movie-info">
                <p class="movie-title">${escapeHtml(title)}</p>
                ${year ? `<p class="movie-year">${escapeHtml(String(year))}</p>` : ''}
            </div>
        `;

        frag.appendChild(card);
    });

    els.emptyState.hidden = true;
    els.movieGrid.appendChild(frag);
    els.resultCount.textContent = `${movies.length} movie${movies.length === 1 ? '' : 's'}`;
}

function setLoading(isLoading) {
    els.loadingState.hidden = !isLoading;
    els.discoverBtn.disabled = isLoading || state.selectedVibes.size === 0;
}

async function discoverMovies() {
    if (state.selectedVibes.size === 0) {
        setFeedback('Select at least one vibe first.', 'error');
        return;
    }

    const selectedVibes = [...state.selectedVibes];
    const cacheKey = buildMovieCacheKey(selectedVibes);
    const cached = getCachedValue(cacheKey);

    if (cached) {
        els.resultsSection.hidden = false;
        renderMovies(cached);
        setFeedback('Loaded from cache.', 'success');
        return;
    }

    if (state.requestController) state.requestController.abort();
    state.requestController = new AbortController();

    els.resultsSection.hidden = false;
    setLoading(true);
    setFeedback('');

    try {
        const res = await fetch(
            `${ENDPOINTS.moviesByVibe}?vibes=${encodeURIComponent(selectedVibes.join(','))}`,
            { signal: state.requestController.signal }
        );
        const payload = await res.json();

        if (!res.ok || payload.status === 'error') {
            throw new Error(payload.message || 'Failed to fetch movies');
        }

        const movies = payload.data?.movie_list;
        if (!Array.isArray(movies)) throw new Error('Invalid movies format');

        setCachedValue(cacheKey, movies);
        renderMovies(movies);
        setFeedback('Done. Click a movie for details.', 'success');
    } catch (err) {
        if (err.name === 'AbortError') return;
        renderMovies([]);
        setFeedback(`Error: ${err.message}`, 'error');
    } finally {
        setLoading(false);
    }
}

function handleVibeClick(e) {
    const pill = e.target.closest('.vibe-pill');
    if (!pill) return;

    const name = pill.dataset.vibeName;
    if (!name) return;

    if (state.selectedVibes.has(name)) {
        state.selectedVibes.delete(name);
        pill.classList.remove('selected');
        pill.setAttribute('aria-pressed', 'false');
    } else {
        state.selectedVibes.add(name);
        pill.classList.add('selected');
        pill.setAttribute('aria-pressed', 'true');
    }

    updateButton();
}

function init() {
    els.vibeList.addEventListener('click', handleVibeClick);
    els.discoverBtn.addEventListener('click', discoverMovies);
    updateButton();
    loadVibes();
}

document.addEventListener('DOMContentLoaded', init);