from pydantic import BaseModel, Field


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=1024)


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class PostWithToken(BaseModel):
    post: PostResponse
    token: dict
