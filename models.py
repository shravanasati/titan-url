from sqlalchemy import Column, Integer, String

from database import Base


class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True)
    original_url = Column(String())
    slug = Column(String(50), unique=True)

    def __init__(self, original_url: str, slug: str):
        self.original_url = original_url
        self.slug = slug

    def __repr__(self):
        return f"<URL {self.original_url!r}>"
