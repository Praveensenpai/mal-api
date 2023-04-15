from enum import Enum
from sqlmodel import SQLModel, create_engine, Session, Field


class GenreType(Enum):
    GENRE = "Genre"
    THEME = "Theme"
    EXPLICIT = "Explicit"
    DEMOGRAPHIC = "Demographic"
    OTHER = "Other"


class Genre(SQLModel, table=True):
    mal_id: int = Field(primary_key=True)
    url: str
    name: str
    description: str = Field(nullable=True)
    count: int = Field(nullable=True)
    type: GenreType


class BasicGenre(SQLModel, table=True):
    mal_id: int = Field(primary_key=True)
    name: str
    url: str
    type: GenreType


sqlite_url = "sqlite:///genres.db"
engine = create_engine(sqlite_url)
SQLModel.metadata.create_all(engine)


def basic_genre_insert(basic_genre: BasicGenre):
    try:
        with Session(engine) as session:
            session.add(basic_genre)
            session.commit()
            session.refresh(basic_genre)
            print("Inserted genre", basic_genre.name)
    except Exception as e:
        print(e)


def genre_insert(genre: Genre):
    try:
        with Session(engine) as session:
            session.add(genre)
            session.commit()
            session.refresh(genre)
            print("Inserted genre", genre.name)
    except Exception as e:
        print(e)


def fetch_basic_genre(genre: Genre):
    with Session(engine) as session:
        return session.query(genre).one_or_none()


def fetch_genre(genre: Genre):
    with Session(engine) as session:
        return session.query(genre).one_or_none()


def fetch_basic_genre_all() -> list[BasicGenre]:
    with Session(engine) as session:
        return session.query(BasicGenre).all()
