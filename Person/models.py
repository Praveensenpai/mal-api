from typing import List, Optional
from sqlmodel import Field, SQLModel, Session, create_engine, JSON, Column
from rich import print


class PeopleLink(SQLModel, table=True):
    url: str = Field(primary_key=True)


class Person(SQLModel, table=True):
    mal_id: int = Field(primary_key=True)
    name: str
    url: str
    given_name: str = Field(nullable=True)
    family_name: str = Field(nullable=True)
    alternate_names: List[str] = Field(
        nullable=True, sa_column=Column("alternate_names", JSON)
    )
    website: str = Field(nullable=True)
    birthday: str = Field(nullable=True)
    image_url: str = Field(nullable=True)


engine = create_engine("sqlite:///people.db")
PeopleLink.metadata.create_all(engine)
Person.metadata.create_all(engine)


def insert_people_links(urls: list[str]) -> None:
    try:
        with Session(engine) as session:
            for url in urls:
                people_link = PeopleLink(url=url)
                session.add(people_link)
                print(f"Inserted URL={url}")
                session.commit()
    except Exception:
        print(f"Failed to insert URL={url}")


def get_peoplelinks() -> Optional[List[PeopleLink]]:
    with Session(engine) as session:
        return session.query(PeopleLink).all()


def insert_person(person: Person) -> None:
    try:
        with Session(engine) as session:
            session.add(person)
            session.commit()
            print(f"Inserted Person = {person.name}")
    except Exception:
        print(f"Failed to insert Person = {person.name}")


def get_person_by_url(url: int) -> Person:
    with Session(engine) as session:
        person = session.query(Person).filter(Person.url == url).first()
        return None if person is None else person
