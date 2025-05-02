from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.schemas import AlertCreate, Alert
from models.models import WeatherAlertDB, UserDB
from dependencies.security import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=Alert)
async def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    new_alert = WeatherAlertDB(
        user_id=current_user.id,
        location=alert.location,
        condition=alert.condition
    )
    db.add(new_alert)
    db.commit()
    return new_alert


@router.get("", response_model=list[Alert])
async def get_alerts(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    alerts = db.query(WeatherAlertDB).filter(
        WeatherAlertDB.user_id == current_user.id
    ).all()
    return alerts
