from contextlib import contextmanager
from random import randint

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import DEV_MODE, logger
from .schemes.packet import Packet

last_info: Packet = None


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
    if last_info is not None:
        return last_info.model_dump()
    return {
        "status": "no information"
    }


@app.post('/')
def load(body: Packet):
    global last_info
    last_info = body
    return {
        "status": "ok"
    }
