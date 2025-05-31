import os
from sre_parse import Tokenizer
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from constants.config import OUTPUT_DIR
from models.responses.base_response import BaseResponse
from routes import chat_routes, process_file_routes, vector_store_routes
from utils import image_pipeline, transformer_client
from utils.exception import CustomException


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        transformer_client.load_model()
        # image_pipeline.load_pipeline()
        # pass

    except Exception as e:
        print(f"Error during startup: {str(e)}")

    yield
    # transformer_client.clear_resources()
    # image_pipeline.clear_resources()


app = FastAPI(lifespan=lifespan)

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
        content=BaseResponse(
            status_code=exc.status_code, message=exc.message
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Mặc định cho các lỗi không được CustomException xử lý
    return JSONResponse(
        status_code=500,
        content=BaseResponse(status_code=500, message=str(exc)).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=BaseResponse(status_code=422, message="Validation error").model_dump(),
    )


app.include_router(chat_routes.router, prefix="/api/v1")
app.include_router(process_file_routes.router, prefix="/api/v1")
app.include_router(vector_store_routes.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to my API"}


os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount(OUTPUT_DIR, StaticFiles(directory=OUTPUT_DIR), name="outputs")
