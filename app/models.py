
from sqlalchemy import (
    Integer,
    Column,
    String,
    Boolean,
    text,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP

from database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="TRUE", nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False
    )
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    owner = relationship("User")
    media = relationship(
        "PostMedia",
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="PostMedia.id"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False
    )
    phone_number = Column(String, nullable=True)


class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True
    )


class PostMedia(Base):
    __tablename__ = "post_media"

    id = Column(Integer, primary_key=True, nullable=False)
    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False
    )
    stored_name = Column(String, nullable=False, unique=True)
    media_type = Column(String, nullable=False)

    post = relationship("Post", back_populates="media")
