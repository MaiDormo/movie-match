import random
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Initialize FastAPI app
app = FastAPI()

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5006"],  # Frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route for homepage
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route for login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route for registration page 
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 404,
            "message": "Page not found"
        },
        status_code=404
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "message": "Internal server error"
        },
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)