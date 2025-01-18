import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from routes.streaming_availability_routes import router as stream_avail_router

app = FastAPI(
    title="STREAMING AVAILABILITY API Adapter",
    description="An adapter service for STREAMING AVAILABILITY API using FastAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5006",  # Origine 1
        "http://127.0.0.1:5006"   # Origine 2 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stream_avail_router)

@app.exception_handler(405)
async def method_not_allowed(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=405,
        content={"status": "error", "code": 405, "message": "Method not allowed"},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "code": 422,
            "message": "Validation error",
            "details": exc.errors()
        },
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))