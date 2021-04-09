from datetime import datetime
from sqlalchemy import (MetaData, Table, Column, Integer, Numeric, String,
DateTime, ForeignKey, create_engine)
import random
from time import sleep


metadata = MetaData()

courant = Table('courant', metadata,
    Column('courant_id', Integer(), primary_key=True, autoincrement=True),
    Column('courant_val', String(), nullable=False),
    Column('created_on', DateTime(), default=datetime.now),
)


def main():
    engine = create_engine('sqlite:///test3.db')
    metadata.create_all(engine)
    with engine.connect() as conn:
        for _ in range(random.randint(10, 20)):
            x = random.uniform(0, 20)
            for _ in range(random.randint(5, 10)):
                y = random.uniform(0, 1)
                for _ in range(random.randint(50, 100)):
                    ins = courant.insert().values(
                        courant_val = round(x + y + random.uniform(0, 0.5), 2)
                    )
                    conn.execute(ins)


if __name__ == '__main__':
    main()