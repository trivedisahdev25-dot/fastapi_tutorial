from pydantic import BaseModel ,EmailStr


class UserCreate(BaseModel):
    username :str
    email :EmailStr
    password : str
    role :str 

class Userlogin(BaseModel):
    username :str
    password :str