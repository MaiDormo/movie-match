const CACHE_KEY_PREFIX = 'movieMatch:movieDetails:';
const CACHE_TTL_MS = 30 * 60 * 1000;
const ENDPOINT = '/api/v1/movie-details';

let correctAnswer = '';

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
    triviaSection: document.getElementById('trivia-section'),
    triviaQuestion: document.getElementById('trivia-question'),
    triviaOptions: document.getElementById('trivia-options'),
    triviaFeedback: document.getElementById('trivia-feedback'),
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
        if ('movie_details' in p.data) return null;
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
    const title = omdb.Title || 'Unknown title';
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

    if (omdb.Poster && omdb.Poster !== 'N/A') {
        els.poster.src = omdb.Poster;
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

function renderTrivia(t) {
    const opts = Array.isArray(t?.options) ? t.options : [];
    if (!t?.question || !opts.length) {
        els.triviaSection.hidden = true;
        return;
    }
    els.triviaSection.hidden = false;
    els.triviaQuestion.textContent = t.question;
    els.triviaFeedback.textContent = '';
    els.triviaFeedback.className = 'trivia-feedback';

    correctAnswer = String(t.correct_answer || '').trim().toLowerCase();

    els.triviaOptions.innerHTML = '';
    opts.forEach(opt => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'trivia-btn';
        btn.textContent = opt;
        btn.addEventListener('click', () => handleTrivia(btn, opt));
        els.triviaOptions.appendChild(btn);
    });
}

function handleTrivia(btn, val) {
    [...els.triviaOptions.querySelectorAll('.trivia-btn')].forEach(b => b.disabled = true);
    const ok = String(val).trim().toLowerCase() === correctAnswer;
    btn.classList.add(ok ? 'correct' : 'wrong');
    if (!ok) {
        const correct = [...els.triviaOptions.querySelectorAll('.trivia-btn')]
            .find(b => b.textContent.trim().toLowerCase() === correctAnswer);
        if (correct) correct.classList.add('correct');
    }
    els.triviaFeedback.textContent = ok ? 'Correct!' : 'Not quite.';
    els.triviaFeedback.className = `trivia-feedback ${ok ? 'correct' : 'wrong'}`;
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
    renderTrivia(details.trivia);
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
        const res = await fetch(`${ENDPOINT}?id=${encodeURIComponent(id)}`);
        const payload = await res.json();
        if (!res.ok || payload.status === 'error') {
            throw new Error(payload.message || 'Could not load movie details');
        }

        const details = payload.data?.movie_details;
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