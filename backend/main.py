from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.movies import router as movie_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movie_router)

@app.get("/")
def root():
    return {"message": "CineAI Backend Running"}