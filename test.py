from datetime import date
from decimal import Decimal
import itertools
from unittest.mock import patch

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


def test_occupancy(bookings, hotelroom):

    start_date = "2018-12-26"
    end_date = "2018-12-26"

    response = app.OccupancyEndpoint().get(
        hotelroom.id, start_date, end_date
    )

    assert response["occupancy"] == "60.0"


def test_occupancy_with_blocked_rooms(
    db_session, bookings, hotelroom, make_booking
):

    start_date = "2018-12-26"
    end_date = "2018-12-26"

    blocked_rooms = models.BlockedRooms(
        id=1,
        hotelroom_id=hotelroom.id,
        reserved_night_date=date(2018, 12, 26),
        rooms=4
    )
    db_session.add(blocked_rooms)
    db_session.commit()

    response = app.OccupancyEndpoint().get(
        hotelroom.id, start_date, end_date
    )

    assert response["occupancy"] == "100.0"


def test_occupancy_with_date_range():
    pass


@pytest.fixture
def request():
    with patch("app.request") as request:
        yield request


def test_booking_curve_occupancy(
    db_session, request, hotelroom, make_booking
):
    # TODO add also bookings for different room - should be filtered out

    # for testing shorten the 90 days default
    request.args = {"days": 5}

    reserved_night_date = date(2018, 12, 26)

    ids = itertools.count()
    bookings = []

    def make_bookings(n, **overrides):
        bookings = [
            make_booking(
                id=next(ids),
                reserved_night_date=reserved_night_date,
                **overrides
            ) for i in range(n)
        ]
        db_session.add_all(bookings)
        db_session.commit()

    # bookings prior the curve date range
    make_bookings(2, booking_datetime=date(2018, 12, 21))

    # bookings within the curve date range
    make_bookings(4, booking_datetime=date(2018, 12, 23))
    make_bookings(1, booking_datetime=date(2018, 12, 24))
    make_bookings(3, booking_datetime=date(2018, 12, 26))

    response = app.BookingCurveEndpoint().get(
        hotelroom.id, reserved_night_date
    )

    expected_occupancy_curve = ["20.0", "60.0", "70.0", "70.0", "100.0"]

    assert response["booking_curve"]["occupancy"] == expected_occupancy_curve


def test_booking_curve_revenue(
    db_session, request, hotelroom, make_booking
):
    # TODO add also bookings for different room - should be filtered out

    # for testing shorten the 90 days default
    request.args = {"days": 5}

    reserved_night_date = date(2018, 12, 26)

    ids = itertools.count()
    bookings = []

    def make_bookings(prices, **overrides):
        bookings = [
            make_booking(
                id=next(ids),
                reserved_night_date=reserved_night_date,
                price=price,
                **overrides
            ) for price in prices
        ]
        db_session.add_all(bookings)
        db_session.commit()

    # bookings prior the curve date range
    make_bookings(
        ("100.0", "200.0"),
        booking_datetime=date(2018, 12, 21)
    )

    # bookings within the curve date range
    make_bookings(
        ("100.0", "100.0", "100.0", "100.0"),
        booking_datetime=date(2018, 12, 23)
    )
    make_bookings(
        ("100.0",),
        booking_datetime=date(2018, 12, 24)
    )
    make_bookings(
        ("100.0", "100.0"),
        booking_datetime=date(2018, 12, 26)
    )

    response = app.BookingCurveEndpoint().get(
        hotelroom.id, reserved_night_date
    )

    expected_revenue_curve = [
        Decimal("300.00"),
        Decimal("700.00"),
        Decimal("800.00"),
        Decimal("800.00"),
        Decimal("1000.00")
    ]

    assert response["booking_curve"]["revenue"] == expected_revenue_curve

