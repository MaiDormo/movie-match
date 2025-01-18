import random
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Inizializza l'app FastAPI
app = FastAPI()

# Configura Jinja2 per i template
templates = Jinja2Templates(directory="templates")

# Middleware CORS per consentire richieste da browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5006"],  # Dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Route per la homepage
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
