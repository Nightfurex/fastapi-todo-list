from pydantic import BaseModel, Field, EmailStr



class Todo(BaseModel):
    title: str
    description: str


class UserSchema(BaseModel):
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "Your user name",
                "email": "youremail@gmail.com",
                "password": "yourpassword"
            }
        }

