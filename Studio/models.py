from typing import List
from sqlmodel import JSON, Column, SQLModel, Field, Session, create_engine

database_url = "sqlite:///studio.db"
engine = create_engine(database_url)


class Studio(SQLModel, table=True):
    malid: int = Field(primary_key=True)
    url: str
    title: str
    titles: List = Field(nullable=True, sa_column=Column("titles", JSON))
    established: str = Field(nullable=True)
    favorites: int = Field(nullable=True)
    anime_count: int = Field(nullable=True)
    external_links: List = Field(
        nullable=True, sa_column=Column("external_links", JSON)
    )
    image: str = Field(nullable=True)
    about: str = Field(nullable=True)


Studio.metadata.create_all(engine)


def insert_studio(studio: Studio):
    try:
        print(f"Inserting Studio = {studio.title}")
        with Session(engine) as session:
            session.add(studio)
            session.commit()
    except Exception as e:
        print(f"Studio insertion failed: {studio.title}")


def get_studio(url: int):
    with Session(engine) as session:
        return session.query(Studio).filter(Studio.url == url).one_or_none()
