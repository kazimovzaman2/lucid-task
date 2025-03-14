from sqlalchemy.orm import Session
from app.models.post import Post
from app.schemas.post import PostCreate
from fastapi import HTTPException


def create_post(db: Session, post: PostCreate, user_id: int) -> Post:
    """Create a post and save to the database"""
    db_post = Post(title=post.title, content=post.content, user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_posts_by_user(db: Session, user_id: int):
    """Retrieve all posts for a user"""
    return db.query(Post).filter(Post.user_id == user_id).all()


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
