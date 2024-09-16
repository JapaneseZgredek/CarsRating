from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    production_year = Column(Integer, nullable=False)

    ratings = relationship('CarRating', back_populates='car', cascade='all, delete')


class CarRating(Base):
    __tablename__ = 'car_ratings'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    car_id = Column(Integer, ForeignKey('cars.id', ondelete='CASCADE'), nullable=False)
    rating = Column(Integer, nullable=False)

    car = relationship('Car', back_populates='ratings')
