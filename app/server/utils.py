from passlib.context import CryptContext

# NOTE: this specifies the hashing algorithm "bcrypt"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# NOTE: this hashes the password using passlib module
def hash_password(password: str):
    return pwd_context.hash(password)


# NOTE: this takes in the pswd user enters, hashes it, then compares it with the DB's hash
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
