from contextlib import contextmanager
from random import randint

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import DEV_MODE, logger


@contextmanager
async def lifespan(app: FastAPI):
    # startup'
    logger.info("Server started")
    yield
    # shutdown


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/root")
def root():
    return {"message": f"DEV_MODE is {DEV_MODE}"}


@app.get('/packets')
def packets():
    return {
        'in_packets': randint(0, 1000),
        'out_packets': randint(0, 1000)
    }
