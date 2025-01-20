import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from routes.email_check_routes import router as email_check_router

app = FastAPI(
    title="EMAIL CHEKCER API Adapter",
    description="An Adapter service for checking the EMAIL using FASTAPI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(email_check_router)

def create_error_response(status_code: int, message: str, details: dict = None) -> JSONResponse:
    """Create a standardized error response."""
    content = {
        "status": "error",
        "code": status_code,
        "message": message
    }
    if details:
        content["details"] = details
    return JSONResponse(content=content, status_code=status_code)

@app.exception_handler(405)
async def method_not_allowed(request: Request, exc: HTTPException):
    return create_error_response(
        status_code=405,
        message="The HTTP method is not allowed for this endpoint"
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return create_error_response(
        status_code=422,
        message="Request validation failed",
        details=error_details
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT',5000)))