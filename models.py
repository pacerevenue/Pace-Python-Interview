from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, Date, DateTime, ForeignKey, Integer, Text, Numeric
)
from sqlalchemy.orm import relationship

Base = declarative_base()


class Hotels(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class HotelRooms(Base):
    __tablename__ = 'hotelrooms'
    id = Column(Integer, primary_key=True)

    hotel_id = Column(Integer, ForeignKey('hotels.id'), nullable=False, index=True)
    hotel = relationship("Hotels", primaryjoin=hotel_id == Hotels.id)

    name = Column(Text, nullable=False)
    capacity = Column(Integer, nullable=False)


class Bookings(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)

    hotelroom_id = Column(Integer, ForeignKey('hotelrooms.id'), nullable=False, index=True)
    hotelroom = relationship("HotelRooms", primaryjoin=hotelroom_id == HotelRooms.id)

    reserved_night_date = Column(Date, nullable=False)

    booking_datetime = Column(DateTime, nullable=False)

    # row_type choices = 'booking' or 'cancellation'
    row_type = Column(Text, nullable=False)

    price = Column(Numeric(10, 2), nullable=False)
