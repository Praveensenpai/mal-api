from sqlmodel import Field, SQLModel, create_engine, Session


class Season(SQLModel, table=True):
    name: str
    year: int
    url: str = Field(primary_key=True)


engine = create_engine("sqlite:///seasons.db")

Season.metadata.create_all(engine)


def insert_seasons(seasons: list[Season]):
    for season in seasons:
        with Session(engine) as session:
            print(f"Inserting URL = {season.url}")
            session.add(season)
            session.commit()
    print("Inserted")


def get_seasons() -> list[str]:
    with Session(engine) as session:
        return session.query(Season).all()
