const CACHE_KEY_PREFIX = 'movieMatch:movieDetails:';
const CACHE_TTL_MS = 30 * 60 * 1000;
const ENDPOINT = '/api/v1/movie-details';

const els = {
    page: document.getElementById('details-page'),
    loading: document.getElementById('loading-state'),
    errorState: document.getElementById('error-state'),
    errorMessage: document.getElementById('error-message'),
    poster: document.getElementById('poster'),
    title: document.getElementById('title'),
    heroMeta: document.getElementById('hero-meta'),
    tags: document.getElementById('tags'),
    plot: document.getElementById('plot'),
    trailerSection: document.getElementById('trailer-section'),
    youtubeFrame: document.getElementById('youtube-frame'),
    streamingSection: document.getElementById('streaming-section'),
    streamingContent: document.getElementById('streaming-content'),
    spotifySection: document.getElementById('spotify-section'),
    spotifyLink: document.getElementById('spotify-link'),
    spotifyCover: document.getElementById('spotify-cover'),
    spotifyTitle: document.getElementById('spotify-title'),
    spotifySubtitle: document.getElementById('spotify-subtitle')
};

function getCache(id) {
    const raw = sessionStorage.getItem(`${CACHE_KEY_PREFIX}${id}`);
    if (!raw) return null;
    try {
        const p = JSON.parse(raw);
        if (Date.now() - p.timestamp > CACHE_TTL_MS) {
            sessionStorage.removeItem(`${CACHE_KEY_PREFIX}${id}`);
            return null;
        }
        if (!p.data || typeof p.data !== 'object') return null;
        return p.data;
    } catch {
        sessionStorage.removeItem(`${CACHE_KEY_PREFIX}${id}`);
        return null;
    }
}

function setCache(id, data) {
    sessionStorage.setItem(`${CACHE_KEY_PREFIX}${id}`, JSON.stringify({ timestamp: Date.now(), data }));
}

function escapeHtml(v) {
    return String(v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function showError(msg) {
    els.page.hidden = true;
    els.loading.hidden = true;
    els.errorState.hidden = false;
    els.errorMessage.textContent = msg;
}

function renderInfo(omdb = {}) {
    const title = omdb.Title || omdb.title || 'Unknown title';
    document.title = title;
    els.title.textContent = title;

    const metaParts = [omdb.Year, omdb.Runtime, omdb.Type].filter(Boolean);
    const ratingHtml = omdb.imdbRating && omdb.imdbRating !== 'N/A'
        ? `<span class="rating">★ ${escapeHtml(omdb.imdbRating)}</span>`
        : '';
    els.heroMeta.innerHTML = metaParts.map(p => `<span>${escapeHtml(p)}</span>`).join('') + ratingHtml;

    const genres = (omdb.Genre || '').split(',').map(g => g.trim()).filter(Boolean);
    els.tags.innerHTML = genres.length
        ? genres.map(g => `<span class="tag">${escapeHtml(g)}</span>`).join('')
        : '';

    els.plot.textContent = omdb.Plot && omdb.Plot !== 'N/A' ? omdb.Plot : '';

    const poster = omdb.Poster || (omdb.poster_path ? `https://image.tmdb.org/t/p/w500${omdb.poster_path}` : null);
    if (poster) {
        els.poster.src = poster;
        els.poster.alt = `${title} poster`;
        els.poster.hidden = false;
    } else {
        els.poster.hidden = true;
    }
}

function renderTrailer(yt) {
    if (yt?.embed_url) {
        els.youtubeFrame.src = yt.embed_url;
        els.trailerSection.hidden = false;
    } else {
        els.trailerSection.hidden = true;
    }
}

function renderStreaming(s) {
    const services = Array.isArray(s?.services) ? s.services : [];
    if (!services.length) {
        els.streamingSection.hidden = true;
        return;
    }
    els.streamingSection.hidden = false;
    els.streamingContent.innerHTML = services.map(svc => `
        <a class="streaming-item" href="${escapeHtml(svc.link || '#')}" target="_blank" rel="noopener noreferrer">
            ${svc.logo ? `<img class="streaming-logo" src="${escapeHtml(svc.logo)}" alt="${escapeHtml(svc.service_name || '')}">` : ''}
            <span>${escapeHtml(svc.service_name || '')}</span>
        </a>
    `).join('');
}

function renderSpotify(sp) {
    if (!sp?.spotify_url) {
        els.spotifySection.hidden = true;
        return;
    }
    els.spotifySection.hidden = false;
    els.spotifyLink.href = sp.spotify_url;
    els.spotifyCover.src = sp.cover_url || '';
    els.spotifyCover.hidden = !sp.cover_url;
    els.spotifyTitle.textContent = sp.name || 'Open soundtrack';
    els.spotifySubtitle.textContent = 'Listen on Spotify';
}

function render(details) {
    renderInfo(details.omdb || {});
    renderTrailer(details.youtube);
    renderStreaming(details.streaming);
    renderSpotify(details.spotify);
    els.loading.hidden = true;
    els.page.hidden = false;
}

async function load(id) {
    const cached = getCache(id);
    if (cached) {
        render(cached);
        return;
    }

    try {
        const [enrichmentRes, coreRes] = await Promise.all([
            fetch(`${ENDPOINT}?id=${encodeURIComponent(id)}`),
            fetch(`/api/v1/movie-core?id=${encodeURIComponent(id)}`)
        ]);
        
        const payload = await enrichmentRes.json();
        const corePayload = await coreRes.json();

        if (!enrichmentRes.ok || payload.status === 'error') {
            throw new Error(payload.message || 'Could not load movie details');
        }
        if (!coreRes.ok || corePayload.status === 'error') {
            console.warn("Core movie data not found or failed, relying on enrichment fallback if possible");
        }

        // Merge the two payloads. `corePayload` has the base movie details, `payload` has enrichment.
        const genres = Array.isArray(corePayload.genres)
            ? corePayload.genres.map(g => g.name).filter(Boolean).join(', ')
            : '';
            
        let details = {
            omdb: {
                Title: corePayload.title || payload.title,
                imdbID: corePayload.imdb_id || payload.imdb_id,
                Year: corePayload.release_date ? corePayload.release_date.slice(0, 4) : '',
                Runtime: corePayload.runtime ? `${corePayload.runtime} min` : '',
                Genre: genres,
                Poster: corePayload.poster_path ? `https://image.tmdb.org/t/p/w500${corePayload.poster_path}` : '',
                imdbRating: corePayload.vote_average ? String(corePayload.vote_average.toFixed(1)) : '',
                Plot: corePayload.overview || payload.overview || '',
            },
            youtube: payload.youtube,
            spotify: payload.spotify,
            streaming: payload.streaming,
        };

        if (!details || typeof details !== 'object') {
            throw new Error('Invalid movie details');
        }

        setCache(id, details);
        render(details);
    } catch (err) {
        showError(err.message || 'Could not load movie details.');
    }
}

function init() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    if (!id) {
        showError('Missing movie id.');
        return;
    }
    load(id);
}

document.addEventListener('DOMContentLoaded', init);
