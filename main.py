import email
from email.policy import default
from logging import raiseExceptions
from os import access
from urllib import response
from jose import jwt
from decouple import config
from passlib.context import CryptContext
from datetime import timedelta,datetime
from model import Todo,UserSchema
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi import FastAPI, HTTPException,Body,Depends
from database import (
    fetch_one_todo,
    fetch_all_todos,
    create_todo,
    update_todo,
    remove_todo,
    create_user,
    sign_in,
)

users = []
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hashed(password):
    return pwd_context.hash(password)


async def check_user(username,password):
    response = await sign_in(username)
    if response:
        password_check = pwd_context.verify(password,response[1])
        return password_check

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

def create_token(data:dict,expires_delta:timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp":expire})
    encoded_jwt = (to_encode,JWT_SECRET,JWT_ALGORITHM)
    return(encoded_jwt)


@app.get("/")
def get_route():
    return {"ping":"pong"}

@app.get("/api/todo")
async def get_todo():
    response = await fetch_all_todos()
    return response

@app.get("/api/todo{title}", dependencies=[Depends(oauth2_scheme)] ,response_model=Todo)
async def get_todo_by_id(title):
    response = await fetch_one_todo(title)
    if response:
        return response
    raise HTTPException(404, f"There is no Todo item with this title {title}")


@app.post("/api/todo", dependencies=[Depends(oauth2_scheme)] ,response_model=Todo)
async def post_todo(todo:Todo):
    response = await create_todo(todo.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong / Bad request")


@app.put("/api/todo{title}/",dependencies=[Depends(oauth2_scheme)],response_model=Todo)
async def put_todo(title:str,desc:str):
    response = await update_todo(title, desc)
    if response:
        return response
    raise HTTPException(404, f"There is no Todo item with this title {title}")


@app.delete("/api/todo{title}",dependencies=[Depends(oauth2_scheme)])
async def delete_todo(title):
    response = await remove_todo(title)
    if response:
        return "Successfully deleted todo item"
    raise HTTPException(404, f"There is no Todo item with this title {title}")

@app.post("/user/signup",tags=["user"])
async def user_signup(user: UserSchema = Body(default=None)):
    user.password = get_password_hashed(user.password)
    response = await create_user(user.dict())
    if response:
        return ("Your signup was successfull")
    raise HTTPException(400, "Something went wrong / Bad request")



@app.post("/token", tags=["user"])
async def user_login(user: OAuth2PasswordRequestForm=Depends()):
    response = await check_user(user.username,user.password)
    if response:
        access_token = create_token(data ={"sub":user.username},expires_delta =timedelta(minutes=30))
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

