from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, conint
from typing import Annotated, List

from sqlalchemy import func, desc
from sqlalchemy.sql.functions import coalesce

import models
from models import Car, CarRating
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class CarCreate(BaseModel):
    brand: str
    model: str
    production_year: conint(ge=1769)  # Year when first car has been created


class RatingCreate(BaseModel):
    rating: conint(ge=1, le=5)


class CarResponse(BaseModel):
    id: int
    brand: str
    model: str
    production_year: int
    average_rating: float


class CarResponsePost(BaseModel):
    id: int
    brand: str
    model: str
    production_year: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.post("/cars/", response_model=CarResponsePost, status_code=status.HTTP_201_CREATED)
async def create_car(car: CarCreate, db: db_dependency):
    db_car = Car(brand=car.brand, model=car.model, production_year=car.production_year)
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


@app.post("/cars/{car_id}/rate", status_code=status.HTTP_201_CREATED)
async def rate_car(car_id: int, rating: RatingCreate, db: db_dependency):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")

    db_rating = CarRating(car_id=car_id, rating=rating.rating)
    db.add(db_rating)
    db.commit()
    return {"message": "Rating added successfully"}


@app.get("/cars/top10", response_model=List[CarResponse], status_code=status.HTTP_200_OK)
async def get_top10_cars(db: db_dependency):
    cars = db.query(
        Car.id,
        Car.brand,
        Car.model,
        Car.production_year,
        # Use COALESCE, to set average rating to 1, when there are no ratings associated to car
        coalesce(func.avg(CarRating.rating), 1).label('average_rating')
    ).join(CarRating, Car.id == CarRating.car_id, isouter=True).group_by(Car.id).order_by(desc('average_rating')).limit(10).all()

    return cars
