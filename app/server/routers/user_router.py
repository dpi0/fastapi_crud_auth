from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from ..utils import hash_password
from ..models import CreateUser, ResponseCreateUser, ResponseUser
from ..database import users_coll

# from .post_router import validate_id
from typing import Any
from ..oauth2 import get_current_user_data
from ..serializers.user_serializer import (
    user_serializer,
)


router = APIRouter()


def find_user(user_name: str) -> Any:
    return users_coll.find_one({"username": user_name})


def validate_user_name(user_name: str) -> bool:
    found_user = find_user(user_name)
    if found_user:
        return True

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User Not Found",
    )


def validate_user_for_the_query(
    user_name: str, current_user_data: dict[str, str]
) -> bool:
    found_user = find_user(user_name)
    if found_user["_id"] == current_user_data["_id"]:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User Not Authorized to Access Profile Data",
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description="Create a User",
    response_model=ResponseCreateUser,
)
async def create_user(user: CreateUser):
    """
    Create a User.

    Args:
        user (CreateUser): The user object containing the user data.

    Returns:
        dict: A dictionary containing the ID and creation time of the new user.
    """
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    user_encoded = jsonable_encoder(user)
    # NOTE: jsonable_encoder converts the Model data to a dict/json type
    new_user_id = users_coll.insert_one(user_encoded).inserted_id
    return {
        "id": str(new_user_id),
        "creation_time": user.creation_time,
    }


@router.get(
    "/{user_name}",
    status_code=status.HTTP_200_OK,
    description="Get user",
    response_model=ResponseUser,
)
async def get_user(
    user_name: str,
    current_user_data: dict = Depends(get_current_user_data),
):
    """
    Get user.

    Parameters:
        user_name (str): The ID of the user.
        current_user_data (dict): The data of the current user.

    Returns:
        ResponseCreateUser: The serialized user object.

    Description:
        This function retrieves the user with the given user ID. It validates the user ID
        using the `validate_id` function. If the user is valid, it returns the serialized
        user object using the `user_serializer` function.

    Raises:
        None.
    """
    if validate_user_name(user_name):
        if validate_user_for_the_query(user_name, current_user_data):
            return user_serializer(find_user(user_name))
