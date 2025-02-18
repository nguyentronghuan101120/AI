
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models.responses.base_response import BaseResponse
from routes import chat_routes, image_routes
from utils.exception import CustomException

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(status_code=exc.status_code, message=exc.message).model_dump(),
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Mặc định cho các lỗi không được CustomException xử lý
    return JSONResponse(
        status_code=500,
        content=BaseResponse(status_code=500, message=str(exc)).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=BaseResponse(status_code=422, message="Validation error").model_dump()
    )

app.include_router(chat_routes.router, prefix="/api/v1")
app.include_router(image_routes.router, prefix="/api/v1")
@app.get("/")
def read_root():
    return {"message": "Welcome my API"}

# Define a route for the root path ('/') that returns a JSON response with a welcome message
