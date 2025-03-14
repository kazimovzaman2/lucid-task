from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, Base, engine
from app.middleware import LimitRequestSizeMiddleware
from app.schemas.post import PostCreate, PostResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserWithToken
from app.services.auth import JWTBearer, sign_jwt
from app.models.user import User as UserModel
from fastapi.security import HTTPBearer
from app.services.posts import create_post, get_all_posts, delete_post_by_id
from app.services.cache import cache


async def lifespan(app: FastAPI):
    print("Starting up...")
    Base.metadata.create_all(bind=engine)

    yield

    print("Shutting down...")


app = FastAPI(lifespan=lifespan)


app.add_middleware(LimitRequestSizeMiddleware, max_size=1 * 1024 * 1024)

security = HTTPBearer()


@app.post("/user/signup", response_model=UserWithToken)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Signup a new user, returning a JWT token for authentication
    """
    if db.query(UserModel).filter(UserModel.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = UserModel(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    token = sign_jwt(db_user.id)

    user_response = UserResponse(
        id=db_user.id, email=db_user.email, fullname=db_user.fullname
    )

    return UserWithToken(user=user_response, token=token)


@app.post("/user/login", response_model=UserWithToken)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Login an existing user, returning a JWT token for authentication
    """
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()

    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = sign_jwt(db_user.id)

    user_response = UserResponse(
        id=db_user.id, email=db_user.email, fullname=db_user.fullname
    )

    return UserWithToken(user=user_response, token=token)


@app.get("/user/me", response_model=UserResponse)
async def get_current_user(
    token: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
):
    """
    Get the current logged-in user using the JWT token
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_response = UserResponse(
        id=db_user.id, email=db_user.email, fullname=db_user.fullname
    )

    return user_response


@app.post("/post", response_model=PostResponse)
async def add_post(
    post: PostCreate, token: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
):
    """
    Add a post to the current user's account
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    db_post = create_post(db, post, user_id)

    return db_post


@app.get("/posts", response_model=list[PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    """
    Get all posts from the database
    """

    cached_posts = cache.get("posts")

    if cached_posts:
        return cached_posts

    db_posts = get_all_posts(db)

    if not db_posts:
        raise HTTPException(status_code=404, detail="No posts found")

    cache["posts"] = db_posts

    return db_posts


@app.delete("/post/{post_id}")
async def delete_post(
    post_id: int, token: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
):
    """
    Delete a post from the current user's account
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    delete_post_by_id(db, post_id, user_id)

    return {"detail": "Post deleted successfully"}
