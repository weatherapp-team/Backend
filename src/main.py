from fastapi import FastAPI
from dotenv import load_dotenv
from core.database import engine, Base
from routers import locations
from routers import alerts, auth, weather
from core.initial_data import init_admin_user

load_dotenv()

Base.metadata.create_all(bind=engine)

init_admin_user()

app = FastAPI(
    title="Weather Monitoring App",
    description="An app to monitor weather conditions"
                " with alerts and historical data",
    version="0.1.0"
)

app.include_router(auth.router)
app.include_router(weather.router)
app.include_router(locations.router)
app.include_router(alerts.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
