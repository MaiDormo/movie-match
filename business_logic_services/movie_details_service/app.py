import os
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Dict, Any, Optional
from routes.movie_details_routes import router as movie_details_router

app = FastAPI(
    title="Movie Details Service",
    description="A service to aggregate movie details from various sources",
    version="1.0.0"
)

def create_error_response(
    status_code: int, 
    message: str, 
    details: Optional[Dict[str, Any]] = None
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    return create_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        details={"headers": exc.headers} if exc.headers else None
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
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

@app.exception_handler(405)
async def method_not_allowed(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle method not allowed errors"""
    return create_error_response(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        message="The HTTP method is not allowed for this endpoint"
    )

@app.exception_handler(500)
async def internal_server_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle internal server errors"""
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An internal server error occurred",
        details={"error": str(exc)} if app.debug else None
    )

app.include_router(movie_details_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app, 
        host='0.0.0.0', 
        port=os.getenv("PORT",5000),
    )