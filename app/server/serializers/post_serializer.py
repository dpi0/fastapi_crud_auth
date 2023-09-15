# NOTE: this takes in the the data from MONGODB and converts it to a dict
# NOTE: as both are essentially diff types of data
def post_serializer(post) -> dict:
    return {
        # NOTE: id must be str as normally it is of type ObjectId
        "id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"],
        "published": post["published"],
        "creation_time": post["creation_time"],
        "owner_id": post["owner_id"],
    }


# NOTE: creates a list of dicts which is NECCESSARY to output the GET ALL POSTS
def post_list_serializer(posts) -> list:
    return [post_serializer(post) for post in posts]
