import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

load_dotenv()

DB_POOL_SIZE = int(os.environ["DB_POOL_SIZE"])
DB_POOL_RECYCLE = int(os.environ["DB_POOL_RECYCLE"])

DB_CONNECTION_URI = os.environ["POSTGRES_URL"]
if DB_CONNECTION_URI.endswith("sslmode"):
    DB_CONNECTION_URI += "=require"
engine = create_engine(
    DB_CONNECTION_URI,
    pool_size=DB_POOL_SIZE,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=True,
)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models

    Base.metadata.create_all(bind=engine)
