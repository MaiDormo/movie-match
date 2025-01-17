import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from routes.user_login_route import router as user_login_router

app = FastAPI(
    title="User Login Service",
    description="A Process Centric Service for user login",
    version="1.0.0"
)

app.include_router(user_login_router)

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