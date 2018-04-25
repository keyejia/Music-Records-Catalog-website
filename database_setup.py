from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key = True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable = False)
	picture = Column(String(250))

class Genre(Base):
	__tablename__ = 'genre'

	id = Column(Integer, primary_key = True)
	name = Column(String(250), nullable = False)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)
	albums = relationship('Albums', cascade='all, delete-orphan')

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return{
			'name'		  : self.name,
			'id'          : self.id,
		}

class Albums(Base):
	__tablename__ = 'albums'

	id = Column(Integer, primary_key = True)
	name =Column(String(80), nullable = False)
	artist = Column(String(80))
	year = Column(String(80))
	description = Column(String(400))
	image_address = Column(String(120))
	genre_id = Column(Integer, ForeignKey('genre.id'))
	genre = relationship(Genre)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id'           : self.id,
			'name'         : self.name,
			'artist'       : self.artist,
			'year'         : self.year,
			'description'  : self.description,
			'image_address': self.image_address,
			'user_id'      :self.user_id
		}

engine = create_engine('sqlite:///albums.db')


Base.metadata.create_all(engine)