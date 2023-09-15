from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import post_router, user_router, auth_router

# NOTE: this creates the app
app = FastAPI()

# NOTE: this for CORS, used for when a diff lang frontend is used
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NOTE: these connect the main.py to the routers for posts, users and authentication
app.include_router(post_router.router, tags=["Posts"], prefix="/post")
app.include_router(user_router.router, tags=["Users"], prefix="/user")
app.include_router(
    auth_router.router, tags=["Authentication"], prefix="/auth"
)


@app.get("/")
async def root():
    return {"message": "Home Page"}
