def user_serializer(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "creation_time": user["creation_time"],
    }


def user_list_serializer(users) -> list:
    return [user_serializer(user) for user in users]
