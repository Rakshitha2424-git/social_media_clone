import os
import logging
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from  database import get_db
import models as models
import oauth2 as oauth2
import schemas as schemas

router = APIRouter(prefix="/posts", tags=["Posts"])
media_router = APIRouter(tags=["Media"])
logger = logging.getLogger(__name__)
MEDIA_DIRECTORY = Path(
    os.getenv("MEDIA_DIRECTORY", str(Path(__file__).resolve().parents[1] / "uploads"))
)
MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024
MAX_MEDIA_PER_POST = 5
MEDIA_FORMATS = {
    ".jpg": ("image/jpeg", MAX_IMAGE_SIZE, (b"\xff\xd8\xff",)),
    ".jpeg": ("image/jpeg", MAX_IMAGE_SIZE, (b"\xff\xd8\xff",)),
    ".png": ("image/png", MAX_IMAGE_SIZE, (b"\x89PNG\r\n\x1a\n",)),
    ".gif": ("image/gif", MAX_IMAGE_SIZE, (b"GIF87a", b"GIF89a")),
    ".webp": ("image/webp", MAX_IMAGE_SIZE, (b"RIFF",)),
    ".mp4": ("video/mp4", MAX_VIDEO_SIZE, (b"ftyp",)),
    ".mov": ("video/quicktime", MAX_VIDEO_SIZE, (b"ftyp",)),
    ".webm": ("video/webm", MAX_VIDEO_SIZE, (b"\x1a\x45\xdf\xa3",)),
}


async def save_media_file(upload: UploadFile) -> models.PostMedia:
    extension = Path(upload.filename or "").suffix.lower()
    media_format = MEDIA_FORMATS.get(extension)
    if media_format is None or upload.content_type != media_format[0]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use JPG, PNG, GIF, WebP, MP4, MOV, or WebM files.",
        )

    media_type, size_limit, signatures = media_format
    stored_name = f"{uuid.uuid4().hex}{extension}"
    destination = MEDIA_DIRECTORY / stored_name
    size = 0
    prefix = b""
    valid = False

    try:
        MEDIA_DIRECTORY.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as output:
            while chunk := await upload.read(64 * 1024):
                size += len(chunk)
                if size > size_limit:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Each {media_type.split('/')[0]} file exceeds its size limit.",
                    )
                if len(prefix) < 12:
                    prefix = (prefix + chunk)[:12]
                output.write(chunk)
        if extension == ".webp":
            signature_matches = prefix.startswith(b"RIFF") and prefix[8:12] == b"WEBP"
        elif extension in {".mp4", ".mov"}:
            signature_matches = prefix[4:8] == b"ftyp"
        else:
            signature_matches = any(prefix.startswith(signature) for signature in signatures)
        if not signature_matches:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file contents do not match the selected media type.",
            )
        valid = True
        return models.PostMedia(stored_name=stored_name, media_type=media_type)
    finally:
        if not valid:
            destination.unlink(missing_ok=True)


@media_router.get("/media/{media_id}")
def get_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    media = (
        db.query(models.PostMedia)
        .join(models.Post)
        .filter(models.PostMedia.id == media_id)
        .first()
    )
    if media is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")
    if not media.post.published and media.post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    file_path = MEDIA_DIRECTORY / media.stored_name
    if not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found")
    return FileResponse(
        file_path,
        media_type=media.media_type,
        headers={"X-Content-Type-Options": "nosniff"},
    )


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: str = "",
    current_user: models.User = Depends(oauth2.get_current_user),
):
    return (
        db.query(
            models.Post,
            func.count(models.Vote.post_id).label("votes"),
        )
        .join(
            models.Vote,
            models.Vote.post_id == models.Post.id,
            isouter=True,
        )
        .filter(models.Post.title.contains(search))
        .filter(
            or_(
                models.Post.published.is_(True),
                models.Post.owner_id == current_user.id,
            )
        )
        .group_by(models.Post.id)
        .order_by(models.Post.id.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )


@router.post("/with-media", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post_with_media(
    title: str = Form(..., max_length=200),
    content: str = Form(...),
    published: bool = Form(True),
    files: List[UploadFile] = File(default_factory=list),
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    if len(files) > MAX_MEDIA_PER_POST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A post can include at most {MAX_MEDIA_PER_POST} media files.",
        )

    post = models.Post(
        title=title,
        content=content,
        published=published,
        owner_id=current_user.id,
    )
    saved_paths: list[Path] = []
    committed = False
    try:
        db.add(post)
        db.flush()
        for upload in files:
            media = await save_media_file(upload)
            saved_paths.append(MEDIA_DIRECTORY / media.stored_name)
            post.media.append(media)
        db.commit()
        committed = True
        db.refresh(post)
        return post
    finally:
        if not committed:
            db.rollback()
            for file_path in saved_paths:
                file_path.unlink(missing_ok=True)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post
)
def create_post(
    post_data: schemas.PostCreate,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    new_post = models.Post(owner_id=current_user.id, **post_data.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/latest")
def get_latest_post(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    return db.query(models.Post).order_by(models.Post.id.desc()).first()


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with id {current_user.id} is not authorized to delete this post",
        )
    media_paths = [MEDIA_DIRECTORY / media.stored_name for media in post.media]
    db.delete(post)
    db.commit()
    for file_path in media_paths:
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            logger.exception("Unable to remove media file for deleted post %s", id)


@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    post_data: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with id {current_user.id} is not authorized to update this post",
        )
    for field, value in post_data.model_dump().items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found",
        )
    votes = db.query(func.count(models.Vote.post_id)).filter(
        models.Vote.post_id == id
    ).scalar()
    return {"Post": post, "votes": votes}
