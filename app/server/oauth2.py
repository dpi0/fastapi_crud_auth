from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .models import TokenData
from .database import users_coll
from typing import Optional
from dotenv import dotenv_values

env_config = dotenv_values(".env")


SECRET_KEY = f"{env_config['SECRET_KEY']}"
ALGORITHM = f"{env_config['ALGORITHM']}"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    f"{env_config['ACCESS_TOKEN_EXPIRE_MINUTES']}"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# NOTE: creates an access token
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# NOTE: verifies the access token once the user tries to visit
# other endpoints using the access token it has
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("username")
        if username is None:
            raise credentials_exception
        # NOTE: this adds the "DATA" INSIDE the token
        # NOTE: this can be however many fields i want
        # NOTE: but first update the MODEL TokenData to ensure validation
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    return token_data


# NOTE: this extracts the "username" or whatever field i've set inside the token
# SIDENOTE: see the JWT videos to get why the "username" or
# any other field i've set is present INSIDE the token
def get_current_user_data(
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    # NOTE: see here the token CONTAINS the fields i've set like the username
    # print("LOOOOOOOOOK", token_data)  # output is username = 'divyansh'
    # print(
    #     "LOOOOOOOOOK", token_data.__dict__
    # )  # output is username = 'divyansh'

    # NOTE: the whole point of this function is to return the
    # details of the user who was VALIDATED to have the token

    user_data = users_coll.find_one({"username": token_data.username})
    # NOTE: so this is a dict which contains user_data document
    return user_data
