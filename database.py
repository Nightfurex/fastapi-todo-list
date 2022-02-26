import collections
import email
from unittest import result
import os

from click import password_option
from model import Todo
from model import UserSchema



import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
database = client.TodoList
collection = database.todo
collection2 = database.userinfo


async def fetch_one_todo(title):
    document = await collection.find_one({"title":title})
    return document

async def fetch_all_todos():
    todos = []
    cursor = collection.find({})
    async for document in cursor:
        todos.append(Todo(**document))
    return todos

async def create_todo(todo):
    documment = todo
    result = await collection.insert_one(documment)
    return documment

async def update_todo(title, desc):
    await collection.update_one({"title":title},{"$set":{"description":desc}})
    document = await collection.find_one({"title":title})
    return document

async def remove_todo(title):
    await collection.delete_one({"title":title})
    return True

async def create_user(userSchema):
    documment = userSchema
    result = await collection2.insert_one(documment)
    return documment

async def sign_in(username:str):
    user =  await collection2.find_one({"username":username},{'_id': 0})
    if user:
        username = user["username"]
        password = user["password"]
        return [username,password]
    return False




