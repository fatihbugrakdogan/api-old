from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
from app.repositories.user_repository import UserRepository
from app.core import security
from app.models import UserInDB, UserCreate, RefreshToken, Logout
from app.core import dependencies
from app.core.dependencies import get_current_user, get_repository


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):

    user = await user_repository.authenticate_user(
        email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
        },
        "access_token": security.create_access_token(user_id=user.id),
    }


@router.get("/verify")
async def verify_token(user: UserInDB = Depends(get_current_user)):
    return user


@router.get("/me")
async def me(
    current_user: UserInDB = Depends(get_current_user),
):
    return current_user
