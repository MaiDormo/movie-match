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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Funzione che genera un numero casuale
def generate_random_number():
    return str(random.randint(1, 10))

# Funzione che genera un colore casuale
def generate_random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

# Route per la homepage
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    random_number = generate_random_number()
    return templates.TemplateResponse("index.html", {"request": request, "number": random_number})

# API per ottenere un numero casuale
@app.get("/api/random_number")
async def get_random_number():
    return {"number": generate_random_number()}

# API per ottenere un colore casuale
@app.get("/api/random_color")
async def get_random_color():
    return {"color": generate_random_color()}
