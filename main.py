from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, post, user
from routers import vote

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://www.google.com",
    "https://google.com",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def msg():
    return {"message":"Hello! on ubuntu"}