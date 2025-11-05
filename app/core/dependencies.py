from fastapi import Depends, HTTPException, status, Request
from app.repositories.user_repository import UserRepository
from app.models import TokenPayload
from app.models.api_models.users import UserInDB
from fastapi.security import OAuth2PasswordBearer
from app.core import security
from app.core.config import settings
from jose import jwt
from app.repositories.credentials_repository import CredentialsRepository
from app.integrations.asana import Asana

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_repository(repo_class):
    async def _get_repo():
        repo = repo_class()
        async with repo:
            yield repo

    return _get_repo


def get_token_from_cookie(request: Request) -> str:
    print("request", request.cookies)

    # First try to get token from cookies (for regular auth)
    token = request.cookies.get("auth-token")

    # If no token in cookies, try to get from Vercel JWT
    if not token:
        token = request.cookies.get("_vercel_jwt")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No auth token found in cookies.",
        )
    return token


async def get_current_user(
    token: str = Depends(get_token_from_cookie),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):

    try:
        # First try to decode as regular JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)  # parse token sub, exp, etc.

        user = await user_repository.get_by_id(token_data.sub)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserInDB(**user)

    except (jwt.ExpiredSignatureError, jwt.JWTError):
        # If regular JWT fails, try to handle as Vercel JWT
        try:
            # For Vercel JWT, we need to decode without verification first to get the payload
            # Then create or find user based on the Vercel JWT payload
            import base64
            import json

            # Decode JWT payload without verification
            parts = token.split(".")
            if len(parts) != 3:
                raise HTTPException(status_code=401, detail="Invalid token format")

            # Decode payload
            payload_bytes = base64.urlsafe_b64decode(parts[1] + "==")
            payload = json.loads(payload_bytes)

            # Extract user info from Vercel JWT
            user_id = payload.get("userId") or payload.get("sub")
            username = payload.get("username")

            print(f"Vercel JWT payload: user_id={user_id}, username={username}")

            if not user_id:
                raise HTTPException(status_code=401, detail="No user ID in token")

            # Try to find user by external ID first (Vercel user ID)
            user = await user_repository.get_by_external_id(user_id)

            if not user and username:
                # Try to find by email as fallback
                user = await user_repository.get_by_email(username)

            if not user:
                # Create a minimal user record for Vercel JWT
                from app.models.api_models.users import UserCreateWithoutPassword

                # Ensure we have a valid email format
                if username and "@" in username:
                    email = username
                else:
                    email = f"{username or user_id}@vercel.app"

                print(f"Creating user with email: {email}")

                user_data = UserCreateWithoutPassword(email=email)
                user_dict = user_data.dict()
                user_dict["external_id"] = user_id  # Store the Vercel user ID

                # Create user directly with external_id
                collection = user_repository.db[user_repository.collection_name]
                result = await collection.insert_one(user_dict)
                user_dict["_id"] = result.inserted_id
                user = UserInDB(**user_dict)

            return user

        except Exception as e:
            print(f"Error handling Vercel JWT: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
            )


async def get_asana_client_in_password_flow(user=Depends(get_current_user)):
    token = await CredentialsRepository().get_token_from_platform(
        user_id=str(user.id), platform="asana"
    )

    return Asana(
        token={
            "access_token": token["access_token"],
            "refresh_token": token["refresh_token"],
            "expires_at": token["expires_at"],
        }
    )
