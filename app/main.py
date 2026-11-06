from routers import auth, post
from fastapi import FastAPI, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from routers import user
from routers import vote


app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://www.google.com",
    "https://google.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

app.include_router(post.router)
app.include_router(post.media_router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def msg():
    return {"message":"Hello!"}

@app.get("/set-theme")
def set_theme(response: Response):
    response.set_cookie(
        key="theme",
        value="dark",
        path="/"
    )
    return {"message": "Theme cookie set!"}

@app.get("/get-theme")
def get_theme(theme: str | None = Cookie(default=None)):
    return {"theme": theme}