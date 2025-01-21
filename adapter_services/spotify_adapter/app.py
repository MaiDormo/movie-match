import os
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from routes.spotify_routes import router as spotify_router

def create_error_response(
    status_code: int, 
    message: str, 
    details: Dict | None = None,
) -> JSONResponse:
    """Create a standardized error response"""
    content = {
        "status": "error",
        "code": status_code,
        "message": message
    }
    if details:
        content["details"] = details
    return JSONResponse(content=content, status_code=status_code)

# Initialize FastAPI app
app = FastAPI(
    title="Spotify API Adapter",
    description="An adapter service for Spotify API using FastAPI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5006",
        "http://127.0.0.1:5006"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(spotify_router)

# Error Handlers
@app.exception_handler(405)
async def method_not_allowed(request: Request, exc: HTTPException):
    """Handle method not allowed errors"""
    return create_error_response(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        message="The HTTP method is not allowed for this endpoint"
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    error_details = [
        {
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        for error in exc.errors()
    ]
    
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Request validation failed",
        details=error_details
    )

@app.exception_handler(500)
async def internal_server_error(request: Request, exc: Exception):
    """Handle internal server errors"""
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An internal server error occurred",
        details={"error": str(exc)} if app.debug else None
    )

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 5000))
    uvicorn.run(
        app, 
        host='0.0.0.0', 
        port=port,
        log_level="info"
    )