from sqlalchemy.orm import Session
from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse
from fastapi import HTTPException


def create_post(db: Session, post: PostCreate, user_id: int) -> PostResponse:
    """Create a post and save to the database, returning a PostResponse"""
    db_post = Post(title=post.title, content=post.content, user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return PostResponse(
        id=db_post.id,
        title=db_post.title,
        content=db_post.content,
        user_id=db_post.user_id,
    )


def get_all_posts(db: Session) -> list[PostResponse]:
    """Retrieve all posts from the database"""
    posts = db.query(Post).all()

    return [
        PostResponse(
            id=post.id, title=post.title, content=post.content, user_id=post.user_id
        )
        for post in posts
    ]


def delete_post_by_id(db: Session, post_id: int, user_id: int):
    """Delete a post by its ID"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    if db_post.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="You can only delete your own posts"
        )

    db.delete(db_post)
    db.commit()
    return db_post
