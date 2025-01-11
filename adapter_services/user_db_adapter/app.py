import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from dotenv import dotenv_values
from pymongo import MongoClient
from routes.user_db_routes import router as user_db_router

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file
env_path = os.path.join(current_dir, ".env")

config = dotenv_values(env_path)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    # Create indexes
    app.database["users"].create_index("email", unique=True)
    print("Connected to the MongoDB database!")
    yield
    app.mongodb_client.close()

app = FastAPI(
    title="User DB API Adapter",
    description="An adapter service for User DB using FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(user_db_router)

@app.exception_handler(405)
async def method_not_allowed(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=405,
        content={"status": "error", "code": 405, "message": "Method not allowed"},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    detailed_errors = []
    for error in errors:
        loc = error.get("loc", ["unknown"])
        msg = error.get("msg", "Unknown error")
        error_type = error.get("type", "Unknown type")
        detailed_errors.append({
            "location": loc,
            "message": msg,
            "type": error_type
        })
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "code": 422,
            "message": "Validation error",
            "details": detailed_errors
        },
    )
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))