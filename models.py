import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    access_token = Column(String(255))
    name         = Column(String(255))
    picture      = Column(String(255))

    def __init__(self, access_token, name, picture):
        self.access_token = access_token
        self.name = name
        self.picture = picture

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
        """ JSON serializer method """
        return {
            'id': self.id,
            'name': self.name
        }

class Music(Base):
    __tablename__ = 'music'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    youtube_url = Column(String(255))
    thumbnail_url = Column(String(255))
    description = Column(String(2000))
    featured = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)
    sender_id = Column(Integer, ForeignKey('users.id'))
    sender = relationship(User)

    @property
    def serialize(self):
        """ JSON serializer method """
        return {
            'id': self.id,
            'title': self.title,
            'youtube_url': self.youtube_url,
            'thumbnail_url': self.thumbnail_url,
            'description': self.description,
            'featured': self.featured,
            'category_id': self.category_id,
            'category_name': self.category.name,
        }

if __name__ == '__main__':
    engine = create_engine(os.environ['DATABASE_URL'])
    Base.metadata.create_all(engine)
