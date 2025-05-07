from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from core.database import get_db
from schemas.schemas import (AlertCreate, AlertUpdate,
                             AlertDelete, AlertGet, NotificationGet)
from models.models import WeatherAlertDB, UserDB, NotificationDB
from dependencies.security import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])

comparators = [">", "<", "<=", ">="]
columns = ["temperature", "humidity", "pressure"]


@router.post("")
async def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Creating alert.
    :param alert: alert.
    :param db: db session.
    :param current_user: current user.
    :return: message
    """
    if alert.comparator not in comparators or alert.column_name not in columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comparator or column is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    new_alert = WeatherAlertDB(
        comparator=alert.comparator,
        user_id=current_user.id,
        location=alert.location,
        column_name=alert.column_name,
        number=alert.number,
    )

    db.add(new_alert)
    db.commit()

    return {"message": "Alert created successfully"}


@router.put("")
async def update_alert(
    alert: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Updating alert.
    :param alert: alert.
    :param db: db session.
    :param current_user: current user.
    :return: message
    """
    if alert.comparator not in comparators or alert.column_name not in columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comparator or column is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    alert_in_db = (db.query(WeatherAlertDB)
                   .filter_by(id=alert.id,
                              user_id=current_user.id).first())

    if alert_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alert not found",
            headers={"WWW-Authenticate": "Bearer"})

    alert_in_db.comparator = alert.comparator
    alert_in_db.location = alert.location
    alert_in_db.column_name = alert.column_name
    alert_in_db.number = alert.number

    db.commit()

    return {"message": "Alert edited successfully"}


@router.delete("")
async def delete_alert(
    alert_delete: AlertDelete,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Deleting alert.
    :param db: db session.
    :param current_user: current user.
    :param alert_delete: alert to delete
    :return: message
    """
    alert_in_db = (db.query(WeatherAlertDB)
                   .filter_by(id=alert_delete.id,
                              user_id=current_user.id).first())

    if alert_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alert not found",
            headers={"WWW-Authenticate": "Bearer"})

    db.delete(alert_in_db)
    db.commit()

    return {"message": "Alert deleted successfully"}


@router.get("", response_model=list[AlertGet])
async def get_alerts(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Getting alerts.
    :param db: db session.
    :param current_user: current user.
    :return: list of alerts.
    """
    alerts = db.query(WeatherAlertDB).filter_by(
        user_id=current_user.id
    ).all()
    return alerts


@router.get("/notifications", response_model=list[NotificationGet])
async def get_notifications(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Getting notifications.
    :param db: db session.
    :param current_user: current user.
    :return: list of notifications.
    """
    alerts = db.query(NotificationDB).filter_by(
        user_id=current_user.id
    ).all()
    return alerts
