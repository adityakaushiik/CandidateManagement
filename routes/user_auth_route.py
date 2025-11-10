from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config.database import get_db
from models import UserModel
from utils.common_model_pydantics import BaseModelPy

user_auth_route = APIRouter(
    prefix="/auth",
)


class UserLogin(BaseModelPy):
    email: str
    password: str


@user_auth_route.post("/login")
async def login(login_request: UserLogin, database: Session = Depends(get_db)):
    if not login_request.email:
        return {"error": "Username is required"}

    if not login_request.password:
        return {"error": "Password is required"}

    user = (
        database.query(UserModel).filter(UserModel.email == login_request.email).first()
    )
    if not user:
        return {"error": "Invalid username or password"}

    print(user)
    return {"message": "Login endpoint"}
