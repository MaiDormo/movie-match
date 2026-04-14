# Backend Improvement Plan (Incremental)

This document captures an honest evaluation of the current architecture and a step-by-step, game-style progression plan from easy to advanced improvements.

---

## Honest Evaluation

### What's Good
- Clear service grouping by role (`adapter_services/`, `business_logic_services/`, `process_centric_services/`).
- Consistent use of FastAPI + Pydantic enables contract-first improvements.
- Attempts at standardized responses and error handling exist in multiple services.

### What's Wrong (Examples)
- Inconsistent error handling and response shapes; some endpoints return `JSONResponse`, others raw dicts; some use invalid patterns like `raise create_response` (e.g., `adapter_services/genres_db_adapter/controllers/genre_db_controller.py`).
- Async endpoints call blocking I/O (`requests`) which breaks concurrency (e.g., `adapter_services/tmdb_adapter/controllers/tmdb_controller.py`, `adapter_services/youtube_adapter/controllers/youtube_controller.py`).
- Hardcoded service URLs; configuration is scattered and fragile (e.g., `business_logic_services/movie_search_service/controllers/movie_search_controller.py`).
- Security weaknesses: open CORS in places, no auth between services, sensitive fields can leak (e.g., hashed password in `adapter_services/user_db_adapter/controllers/user_db_controller.py`).
- Code quality inconsistencies: duplicate router initialization, typos in config filenames (e.g., `adapter_services/user_db_adapter/config/databse.py`).
- No automated tests, linting, or observable metrics.

### What Should Change (Target State)
- One consistent response/error format across all services.
- Centralized, validated configuration using environment variables.
- Proper async I/O usage with shared clients and timeouts.
- Basic security: strict CORS, service-to-service auth, no sensitive fields in responses.
- Tests + lightweight analysis tooling to make the project "mature."

---

## Incremental "Video-Game" Plan

### Level 1 - Basic Cleanup (Easy)
- Pick a "golden path" flow and make it consistent end-to-end.
- Standardize response envelope and error format for that flow.
- Replace hardcoded URLs with env-based settings.
- Fix obvious issues (duplicate routers, invalid error patterns, typos).

### Level 2 - Async Correctness + Timeouts (Easy-Medium)
- Replace blocking `requests` in async endpoints with `httpx.AsyncClient`.
- Add timeouts and retry policies for outbound calls.
- Use a shared HTTP client per service.

### Level 3 - Security Basics (Medium)
- Tighten CORS to known origins.
- Remove sensitive fields from DB responses (never return password hashes).
- Add simple service-to-service auth (API key header).
- Normalize and validate user inputs.

### Level 4 - Observability (Medium)
- Add structured logs with request IDs.
- Propagate request IDs between services.
- Add health vs readiness checks.

### Level 5 - Testing + Analysis (Medium-Hard)
- Unit tests for core controllers and helpers.
- One integration test for the golden path.
- Contract tests between two services.
- Add linting + basic type checks.

### Level 6 - Reliability + Caching (Hard)
- Add circuit breaker or fail-fast behavior to external calls.
- Add caching for expensive external API calls (Redis or in-memory).
- Add rate limiting on public endpoints.

### Level 7 - Modular/Polyglot Readiness (Harder)
- Freeze and version OpenAPI specs.
- Add contract tests to allow safe rewrites in other languages.
- Optionally introduce a gateway/BFF so frontends depend on one API.

---

## Recommended Golden Path
- `process_centric_services/movie_match_service`
  -> `business_logic_services/movie_details_service`
  -> adapters (`omdb_adapter`, `youtube_adapter`, `spotify_adapter`, `streaming_availability_adapter`)
