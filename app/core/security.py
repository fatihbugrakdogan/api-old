from passlib.context import CryptContext
from datetime import timedelta, datetime
from typing import Any, Union
from .config import settings
from jose import jwt, JWTError
from fastapi import HTTPException, Depends

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_jwt_token(expires_delta: timedelta, scope: str, user_id: str) -> str:
    """Creates a JWT token with the given user_id, expiration time delta and scope."""
    try:
        expire = datetime.utcnow() + expires_delta
        to_encode = {"exp": expire, "sub": str(user_id), "scope": scope}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        return None


def create_access_token(user_id: str, expires_delta: timedelta = None) -> str:
    """Creates an access token with the given user_id and expiration time delta."""
    if not expires_delta:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_jwt_token(expires_delta, "access_token", user_id)


def create_refresh_token(user_id: str, expires_delta: timedelta = None) -> str:
    """Creates a refresh token with the given user_id and expiration time delta."""
    if not expires_delta:
        expires_delta = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return create_jwt_token(expires_delta, "refresh_token", user_id)


def create_access_refresh_tokens(user_id: str):
    """Creates and returns access and refresh tokens for the given user ID."""
    access_token_expires = timedelta(minutes=1)
    access_token = create_access_token(
        user_id=user_id, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(user_id=user_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": access_token_expires,
    }


def create_tokens_with_refresh_token(refresh_token):
    """Creates and returns tokens for the given refresh Token."""
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=ALGORITHM)
        if payload["scope"] == "refresh_token":
            user_id = payload["sub"]
            return create_access_refresh_tokens(user_id=user_id)
        raise HTTPException(status_code=401, detail="Invalid scope for token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
        return payload["sub"]
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
