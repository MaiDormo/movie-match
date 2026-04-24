import os
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5006", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VIBE_SERVICE_BASE_URL = os.getenv("VIBE_SERVICE_BASE_URL", "http://vibe-service:5000")
MOVIE_DETAILS_BASE_URL = os.getenv(
    "MOVIE_DETAILS_BASE_URL", "http://movie-details-service:5000"
)
HTTP_TIMEOUT = 20.0


def _build_fallback_payload(response: httpx.Response) -> dict[str, Any]:
    message = response.text.strip() or "Service returned no content"
    return {
        "status": "success" if response.status_code < 400 else "error",
        "message": message,
    }


async def _proxy_get(
    url: str, params: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(url, params=params)
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"status": "error", "message": "Upstream service timeout"},
        )
    except httpx.HTTPError as exc:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"status": "error", "message": f"Upstream service error: {str(exc)}"},
        )

    try:
        payload = response.json()
    except ValueError:
        payload = _build_fallback_payload(response)

    print(f"[PROXY] GET {url} -> {response.status_code}: {payload}")

    return JSONResponse(status_code=response.status_code, content=payload)


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("vibe.html", {"request": request})


@app.get("/health", response_model=dict)
async def health_check():
    return JSONResponse(
        content={
            "status": "success",
            "message": "Frontend is up and running!",
        }
    )


@app.get("/movie-list")
async def movie_list_page():
    return RedirectResponse(url="/vibe", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/vibe", response_class=HTMLResponse)
async def vibe_page(request: Request):
    return templates.TemplateResponse("vibe.html", {"request": request})


@app.get("/movie", response_class=HTMLResponse)
async def movie_details_page(request: Request):
    return templates.TemplateResponse("movie-details.html", {"request": request})


@app.get("/api/v1/vibes", response_class=JSONResponse)
async def get_vibes():
    return await _proxy_get(f"{VIBE_SERVICE_BASE_URL}/api/v1/vibes")


@app.get("/api/v1/vibe/movies", response_class=JSONResponse)
async def get_movies_by_vibe(vibes: str):
    return await _proxy_get(
        f"{VIBE_SERVICE_BASE_URL}/api/v1/vibe/movies", params={"vibes": vibes}
    )


@app.get("/api/v1/movie-details", response_class=JSONResponse)
async def get_movie_details(id: str):
    return await _proxy_get(
        f"{MOVIE_DETAILS_BASE_URL}/api/v1/movie_details", params={"id": id}
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 404,
            "message": "Page not found",
        },
        status_code=404,
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "message": "Internal server error",
        },
        status_code=500,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
