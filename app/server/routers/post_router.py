from fastapi import APIRouter, status, HTTPException, Response, Depends
from fastapi.encoders import jsonable_encoder
from typing import List
from ..models import (
    ResponsePost,
    ResponseCreatePost,
    CreatePost,
    UpdatePost,
    ResponseUpdatePost,
)
from ..database import posts_coll
from ..serializers.post_serializer import (
    post_list_serializer,
    post_serializer,
)
from bson.objectid import ObjectId
from ..oauth2 import get_current_user_data
from typing import Union, Any, Optional
from datetime import datetime

router = APIRouter()


def find_post(post_id: str) -> Any:
    """
    Find a post by its ID.

    Parameters:
        post_id (str): The ID of the post to find.

    Returns:
        Any: The post with the specified ID, or None if no such post exists.
    """
    return posts_coll.find_one({"_id": ObjectId(post_id)})


def validate_post(post_id: str) -> bool:
    """
    Validates a post by checking if it exists in the database.

    Parameters:
        post_id (str): The unique identifier of the post.

    Returns:
        bool: True if the post is found, False otherwise.

    Raises:
        HTTPException: If the post is not found in the database.
    """
    found_post = find_post(post_id)
    if found_post:
        return True

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post Not Found",
    )


def validate_user_for_the_post(
    post_id: str, current_user_data: dict[str, str]
) -> bool:
    """
    Validates whether the current user is authorized to access a specific post.

    Args:
        post_id (str): The ID of the post to be validated.
        current_user_data (dict): The data of the current user.

    Returns:
        bool: True if the current user is authorized to access the post, False otherwise.

    Raises:
        HTTPException: If the current user is not authorized to access the post.
    """
    found_post = find_post(post_id)
    if found_post["owner_id"] == current_user_data["_id"]:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User Not Authorized to Access Post",
    )


def validate_id(post_id: str) -> bool:
    """
    Validate a post ID.

    Args:
        post_id (str): The ID of the post to be validated.

    Returns:
        bool: True if the post ID is valid, False otherwise.

    Raises:
        HTTPException: If the post ID is invalid.

    """
    # NOTE: checks if post_id is a 24 character hex string
    if ObjectId.is_valid(post_id):
        return True
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid id: {post_id}",
    )


@router.get(
    "/",
    response_description="Get all posts",
    # NOTE: reponse is a List
    response_model=List[ResponsePost],
)
async def get_all_posts(
    limit: int = 10,
    page: int = 1,
    search: Optional[str] = "",
    current_user_data: dict[str, str] = Depends(get_current_user_data),
) -> list[dict[str, str]]:
    """
    Get all posts.

    Parameters:
        limit (int): The maximum number of posts to retrieve. Defaults to 10.
        page (int): The page number of the posts to retrieve. Defaults to 1.
        current_user_data (dict): The data of the current user. Defaults to the result of the `get_current_user_data` function.

    Returns:
        list[dict[str, str]]: A list of posts as dictionaries, where each post has a `'str'` key and a `'str'` value.
    """
    skip: int = (page - 1) * limit
    posts: list[dict[str, str]] = post_list_serializer(
        posts_coll.find(
            {
                "$and": [
                    {"owner_id": current_user_data["_id"]},
                    {"title": {"$regex": search, "$options": "i"}},
                ]
            }
        )
        .skip(skip)
        .limit(limit)
    )
    return posts


# NOTE: pretty simple, just gets the post where
# NOTE: the current_user_data's id matches the post's owner_id


@router.get(
    "/{post_id}",
    description="Get post",
    response_model=ResponsePost,
)
async def get_post(
    post_id: str,
    current_user_data: dict[str, str] = Depends(get_current_user_data),
) -> dict[str, str] | None:
    """
    A description of the entire function, its parameters, and its return types.

    GET /{post_id}

    Get post

    Parameters:
        - post_id: str
            The ID of the post to retrieve.
        - current_user_data: dict[str, str], optional
            The data of the current user.

    Returns:
        - dict[str, str] | None
            The serialized post data if the post and user are valid, otherwise None.

    Raises:
        - HTTPException
            If the post ID is invalid.
    """
    validate_id(post_id)

    # NOTE: here first post_id is checked whether exists in DB or not?
    # NOTE: is post_id is valid,i.e post is present then check current user actual owner
    # NOTE: if so then return the post
    if validate_post(post_id):
        if validate_user_for_the_post(post_id, current_user_data):
            print(current_user_data)
            return post_serializer(find_post(post_id))


@router.post(
    "/",
    description="Create a Post",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreatePost,
)
async def create_post(
    post: CreatePost,
    current_user_data: dict = Depends(get_current_user_data),
) -> dict[str, Union[str, bool, datetime]]:
    """
    Create a Post.

    Args:
        post (CreatePost): The data for creating a new post.
        current_user (dict): The data of the current user.

    Returns:
        dict[str, Union[str, bool, datetime]]: A dictionary containing the information of the new post, including the post ID, publication status, creation time, and owner ID.
    """
    post_encoded = jsonable_encoder(post)
    # NOTE: we have to add the current user's id to the new post created
    # NOTE: to link BOTH DOCUMENTS "Posts" & "Users"
    current_user_id: str = current_user_data["_id"]
    post_encoded["owner_id"] = current_user_id
    # NOTE: only then we insert the post
    new_post_id = posts_coll.insert_one(post_encoded).inserted_id
    return {
        # NOTE: id must be str as normally it is of type ObjectId
        "post_id": str(new_post_id),
        "published": True,
        "creation_time": post.creation_time,
        "owner_id": str(current_user_id),
    }


@router.put(
    "/{post_id}",
    description="Updating a Post",
    response_model=ResponseUpdatePost,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def update_post(
    post_id: str,
    post: UpdatePost,
    current_user_data: dict[str, str] = Depends(get_current_user_data),
) -> dict[str, str] | None:
    """
    Updates a post with the specified post ID.

    Args:
        post_id (str): The ID of the post to be updated.
        post (UpdatePost): The updated post data.
        current_user_data (dict): The data of the current user.

    Returns:
        Union[dict[str, str], None]: The updated post as a dictionary, or None if the post was not found.

    Raises:
        PostIDValidationError: If the post ID is invalid.
    """
    validate_id(post_id)

    if validate_post(post_id):
        if validate_user_for_the_post(post_id, current_user_data):
            # NOTE: UPDATE THE POST
            posts_coll.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": post.model_dump(exclude_none=True)},
            )
            # NOTE: after this post was updated, so NOW found_post is the updated one.
            return post_serializer(find_post(post_id))


@router.delete(
    "/{post_id}",
    description="Delete a Post",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: str,
    current_user_data: dict[str, str] = Depends(get_current_user_data),
):
    """
    Delete a Post.

    Parameters:
        - post_id (str): The ID of the post to delete.
        - current_user_data (dict, optional): The data of the current user. Defaults to the result of the `get_current_user_data` dependency.

    Returns:
        - Response: The response object with a status code of 204 (No Content).
    """
    validate_id(post_id)

    if validate_post(post_id):
        if validate_user_for_the_post(post_id, current_user_data):
            # NOTE: DELETE THE POST
            posts_coll.find_one_and_delete({"_id": ObjectId(post_id)})
            return Response(status_code=status.HTTP_204_NO_CONTENT)
