from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session, scoped_session

_SESSION = None


def get_session() -> Session:
    """
    Returns a fully configured sqlalchemy config.
    """
    global _SESSION

    if _SESSION:
        return _SESSION()

    engine = create_engine(
        'postgresql://prix:prix@localhost:5432/interview',
        connect_args={
            'application_name': 'interview-test',
            'connect_timeout': 60 * 60 * 3,
        },
        pool_recycle=60 * 60,
        pool_pre_ping=True,
        implicit_returning=True,
    )
    session_factory = sessionmaker(bind=engine)
    _SESSION = scoped_session(session_factory)
    return _SESSION()
