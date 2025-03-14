from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(...)
    fullname: str = Field(min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(min_length=6, max_length=100)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    fullname: str


class UserWithToken(BaseModel):
    user: UserResponse
    token: dict
