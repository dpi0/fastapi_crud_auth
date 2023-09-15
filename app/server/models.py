from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    PlainSerializer,
    AfterValidator,
    WithJsonSchema,
    ConfigDict,
)
from datetime import datetime
from typing import Optional, Annotated, Union, Any
from bson.objectid import ObjectId


# NOTE: this is needed JUST to set owner_id: ObjectId
# NOTE: and this is  Pydantic's error in the ResponsePost class
def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


PyObjectId = Annotated[
    Union[str, ObjectId],
    AfterValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
# NOTE: till this


class PostBase(BaseModel):
    title: str = Field(...)
    content: str = Field(...)
    published: bool = True
    creation_time: datetime = Field(default=datetime.now())


class CreatePost(PostBase):
    pass


class ResponseCreatePost(BaseModel):
    post_id: str
    published: bool
    creation_time: datetime
    owner_id: str


class ResponsePost(PostBase):
    owner_id: PyObjectId = Field(alias="owner_id")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class UpdatePost(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class ResponseUpdatePost(PostBase):
    pass


############################################


class UserBase(BaseModel):
    username: str = Field(...)
    email: EmailStr = Field(...)
    creation_time: datetime = Field(default=datetime.now())


class CreateUser(UserBase):
    password: str = Field(...)
    verified: bool = False


class ResponseCreateUser(BaseModel):
    username: str
    creation_time: datetime


class ResponseUser(BaseModel):
    username: str
    email: EmailStr
    creation_time: datetime


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class ResponseToken(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
