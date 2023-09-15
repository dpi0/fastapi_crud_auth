from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..oauth2 import create_access_token
from ..utils import verify_password
from ..models import ResponseToken
from ..database import users_coll


router = APIRouter()


@router.post(
    "/login", description="Login User", response_model=ResponseToken
)
# NOTE: OAuth2PasswordRequestForm allows me to enter the Body via form
async def user_login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
):
    # NOTE: the form data which i enter has TWO fields username & password
    user = users_coll.find_one({"username": user_credentials.username})

    # NOTE: we match the username or password
    if not user or not verify_password(
        user_credentials.password, user["password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials",
        )

    # NOTE: currently the token has been payloaded with
    # only "username" i can add more fields if i want
    access_token = create_access_token(data={"username": user["username"]})

    return {"access_token": access_token, "token_type": "bearer"}
