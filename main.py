from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import models
from database import engine, get_db
from routers import vote,auth,post,user
import oauth2
models.Base.metadata.create_all(bind=engine)

origins=["https://www.google.com", "https://google.com"]

app = FastAPI()

app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def msg():
    return {"message":"Hello! RAKSHA"}