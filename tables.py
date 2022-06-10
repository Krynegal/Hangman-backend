from sqlalchemy import MetaData, Table, Column, Integer, String, Text, ForeignKey, create_engine



user = Table('users', metadata,
    Column('id', Integer(), primary_key=True),
    Column('login', String(200), unique=True, nullable=False),
    Column('password', String(200), nullable=False)
)
