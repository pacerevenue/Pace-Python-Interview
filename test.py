from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app, models


@pytest.fixture
def db_connection():

    engine = create_engine(
        # TODO make this configurable (for both the fixture and the app)
        "postgresql://prix:prix@localhost:5432/interview"
    )

    models.Base.metadata.create_all(bind=engine)

    yield engine.connect()

    # TODO properly close the scoped session usedd by the app
    from utils import _SESSION
    if _SESSION:
        _SESSION.close()

    models.Base.metadata.reflect(bind=engine)
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_connection):
    Session = sessionmaker(bind=db_connection)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def hotel(db_session):
    hotel = models.Hotels(id=1, name="Intercontinental")
    db_session.add(hotel)
    db_session.commit()
    return hotel


@pytest.fixture
def hotelroom(db_session, hotel):
    hotelroom = models.HotelRooms(
        id=1,
        hotel_id=hotel.id,
        name="Queen Suite",
        capacity=10,
    )
    db_session.add(hotelroom)
    db_session.commit()
    return hotelroom


@pytest.fixture
def make_booking(db_session, hotelroom):
    def make(**overrides):
        booking_data = dict(
            id=1,
            hotelroom_id=hotelroom.id,
            reserved_night_date=date(2018, 12, 26),
            booking_datetime=date(2018, 12, 26),
            row_type="booking",
            price=Decimal("100.00"),
        )
        booking_data.update(overrides)
        return models.Bookings(**booking_data)
    return make


@pytest.fixture
def bookings(db_session, make_booking):
    bookings = [make_booking(id=i) for i in range(1, 7)]
    db_session.add_all(bookings)
    db_session.commit()
    return bookings


def test_occupancy(bookings):

    hotelroom_id = 1,
    start_date = "2018-12-26"
    end_date = "2018-12-26"

    response = app.OccupancyEndpoint().get(
        hotelroom_id, start_date, end_date
    )

    assert response["occupancy"] == "60.0"


def test_occupancy_with_blocked_rooms(db_session, bookings, make_booking):

    hotelroom_id = 1,
    start_date = "2018-12-26"
    end_date = "2018-12-26"

    blocked_rooms = [
        make_booking(
            id=i,
            reserved_night_date=date(2018, 12, 26),
            row_type="block"
        ) for i in range(7, 11)
    ]
    db_session.add_all(blocked_rooms)
    db_session.commit()

    response = app.OccupancyEndpoint().get(
        hotelroom_id, start_date, end_date
    )

    assert response["occupancy"] == "100.0"
