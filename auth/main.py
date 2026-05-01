from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, utils
from auth_database import get_db
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError

SECRET_KEY = "3OD4WGDQom85bayPMA6LWbmJjFKszjt7i5gy40j4Ik4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


app = FastAPI()


@app.post("/signup")
def register_users(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.Username == user.username
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pass = utils.hash_password(user.password)

    new_user = models.User(
        Username=user.username,
        email=user.email,
        hashed_password=hashed_pass,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        'id': new_user.id,
        "username": new_user.Username,
        "email": new_user.email,
        "role": new_user.role
    }


@app.post("/login")
def login(from_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.Username == from_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username"
        )

    if not utils.verify_password(from_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    token_data = {'sub': user.Username, 'role': user.role}
    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "Bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # ✅ Fix 1: list mein do [ALGORITHM]
        username: str = payload.get("sub")
        role: str = payload.get("role")  # ✅ Fix 2: role define karo
        if username is None or role is None:
            raise credential_exception

    except JWTError:
        raise credential_exception

    return {"username": username, "role": role}


@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user['username']} you accessed a protected route"}


def require_roles(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")  # ✅ Fix 3: comma tha, dot hona chahiye
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permission"
            )
        return current_user
    return role_checker

@app.get("/profile")    
def profile(current_user: dict = Depends(require_roles(["admin", "user"]))):
    return {"message": f" profile of {current_user['username']} ({current_user['role']})"}



@app.get("/user/dashboard")
def user_dashboared(current_user: dict = Depends(require_roles(["user"]))): 
    return {"message": "wellcome to user"}


@app.get("/admin/dashboard")
def admin_dashboared(current_user: dict = Depends(require_roles(["admin"]))): 
    return {"message": "wellcome to admin"}

