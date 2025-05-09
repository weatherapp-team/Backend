from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from core.database import get_db
from models.models import SavedLocationDB, UserDB
from dependencies.security import get_current_user

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("")
async def save_location(
        location: str,
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    """
    Function for saving location.
    :param location: location to save
    :param db: db session
    :param current_user: current user
    :return: message
    """
    existing = db.query(SavedLocationDB).filter_by(
        user_id=current_user.id,
        location=location
    ).first()

    if not existing:
        new_location = SavedLocationDB(
            user_id=current_user.id,
            location=location
        )
        db.add(new_location)
        db.commit()
    else:
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Location already saved"
            )
    return {"message": "Location saved successfully"}


@router.get("", response_model=list[str])
async def get_saved_locations(
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    """
    Function for getting saved location.
    :param db: db session
    :param current_user: current user
    :return: list of locations in string format.
    """
    locations = db.query(SavedLocationDB).filter_by(
        user_id=current_user.id
    ).all()
    return [loc.location for loc in locations]


@router.delete("")
async def delete_location(
        location: str,
        db: Session = Depends(get_db),
        current_user: UserDB = Depends(get_current_user)
):
    """
    Function for deleting location.
    :param location: location string
    :param db: db session
    :param current_user: current user
    :return: message
    """
    existing = db.query(SavedLocationDB).filter_by(
        user_id=current_user.id,
        location=location
    ).first()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db.delete(existing)
    db.commit()

    return {"message": "Location deleted successfully"}
