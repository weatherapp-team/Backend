from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import List, Annotated
from datetime import datetime, timedelta, timezone
from jwt import InvalidTokenError
from passlib.context import CryptContext
import jwt
import os
from fastapi.middleware.cors import CORSMiddleware
from Utils.weather import WeatherMonitor
from Models.models import User, WeatherData, AlertCreate, Token, UserLogin, UserCreate, UserInDB, TokenData
import uvicorn

app = FastAPI(
    title="Weather Monitoring App",
    description="An app to monitor weather conditions with alerts and historical data",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your-api-key-here")

monitor = WeatherMonitor(OPENWEATHER_API_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": pwd_context.hash("secret"),
        "disabled": False,
        "saved_locations": ["New York", "London"],
        "weather_alerts": [
            {"location": "New York", "condition": "temperature < 0", "active": True}
        ]
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(username: str) -> UserInDB | None:
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> UserInDB | None:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    if user_data.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user_data.password)
    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "disabled": False,
        "saved_locations": [],
        "weather_alerts": []
    }
    return {"message": "User created successfully"}

@app.get("/users/me", response_model=User)
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/weather/{location}", response_model=WeatherData)
async def get_weather(location: str, _current_user: User = Depends(get_current_active_user)):
    try:
        return monitor.fetch_weather_data(location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather/dashboard")
async def weather_dashboard(current_user: User = Depends(get_current_active_user)):
    dashboard_data = []
    for location in current_user.saved_locations:
        dashboard_data.append(monitor.fetch_weather_data(location))
    return {"locations": dashboard_data}

@app.post("/locations")
async def save_location(location: str, current_user: User = Depends(get_current_active_user)):
    if location not in current_user.saved_locations:
        fake_users_db[current_user.username]["saved_locations"].append(location)
    return {"message": "Location saved successfully"}

@app.get("/locations", response_model=List[str])
async def get_saved_locations(current_user: User = Depends(get_current_active_user)):
    return current_user.saved_locations

@app.post("/alerts")
async def create_alert(alert: AlertCreate, current_user: User = Depends(get_current_active_user)):
    new_alert = {
        "location": alert.location,
        "condition": alert.condition,
        "active": True
    }
    fake_users_db[current_user.username]["weather_alerts"].append(new_alert)
    return {"message": "Alert created successfully"}

@app.get("/alerts", response_model=List[dict])
async def get_alerts(current_user: User = Depends(get_current_active_user)):
    return current_user.weather_alerts

@app.get("/history/{location}")
async def get_historical_data(location: str, days: int = 7):
    history = []
    for i in range(days):
        history.append({
            "date": (datetime.now() - timedelta(days=i)).date(),
            "temperature": 15 + i % 10,
            "humidity": 60 + i % 20,
            "condition": "sunny" if i % 2 == 0 else "cloudy"
        })
    return {"location": location, "history": history}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)