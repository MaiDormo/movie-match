import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from routes.user_db_routes import router as user_db_router
from config.databse import get_mongo_client

mongo_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongo_client
    try:
        # Startup: create MongoDB connection
        mongo_client = get_mongo_client()
        
        # Verify connection with timeout
        mongo_client.admin.command('ping', serverSelectionTimeoutMS=5000)

        app.state.db = mongo_client
        print("Successfully connected to MongoDB")
        yield
        
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
    except ServerSelectionTimeoutError as e:
        print(f"MongoDB server selection timeout: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail="Database server not available"
        )
    finally:
        # Shutdown: close MongoDB connection
        if mongo_client:
            mongo_client.close()
            print("MongoDB connection closed")



app = FastAPI(
    title="User DB API Adapter",
    description="An adapter service for User DB using FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(user_db_router)

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

# Create error handler for database errors
@app.exception_handler(ConnectionFailure)
async def db_connection_error_handler(request: Request, exc: ConnectionFailure):
    return JSONResponse(
        status_code=503,
        content={
            "status": "error",
            "message": "Database connection error",
            "details": str(exc)
        }
    )

@app.exception_handler(ServerSelectionTimeoutError) 
async def db_timeout_error_handler(request: Request, exc: ServerSelectionTimeoutError):
    return JSONResponse(
        status_code=503,
        content={
            "status": "error", 
            "message": "Database server not responding",
            "details": str(exc)
        }
    )


if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 5000))
    uvicorn.run(app,host='0.0.0.0',port=port,log_level="info")