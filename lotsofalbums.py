from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Genre, Base, Albums, User
 
engine = create_engine('sqlite:///albums.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Kellen Jia", email="keyejia@gmail.com",
             picture='https://profile.actionsprout.com/default.jpeg')
session.add(User1)
session.commit()

#Menu for UrbanBurger
genre1 = Genre(name = "Rock", user_id = 1)

session.add(genre1)
session.commit()

genre2 = Genre(name = "Alternative", user_id = 1)

session.add(genre2)
session.commit()

genre3 = Genre(name = "Pop", user_id = 1)

session.add(genre3)
session.commit()

genre4 = Genre(name = "R&B Soul", user_id = 1)

session.add(genre4)
session.commit()

album1 = Albums(
	name = "The Beatles (White Album)", 
	artist = 'The Beatles', 
	year = "1968", 
	description = '''Released in 1968, much of the White Album, 
					as it is known to most fans, was written while The Beatles 
					were in India studying Transcendental Meditation with 
					Maharishi Mahesh Yogi, and recorded during a time of 
					growing tensions between the band members. The very diverse 
					and eclectic mix of songs on the album is a result of the 
					band members beginning to go their separate ways. ''', 
	image_address = "http://www.popvortex.com/images/album-covers/whte-album-the-beatles.jpg",
	genre = genre1,
	user_id = 1)

session.add(album1)
session.commit()

album2 = Albums(
	name = "Revolver", 
	artist = "The Beatles", 
	year = "1966", 
	description = '''Revolver, released in August 1966, 
					stands in the middle of the evolution from the more 
					folk-rock album Rubber Soul to the psychedelic 
					experimentation of Sgt. Pepper's Lonely Hearts Club Band 
					and reveals The Beatles growing confidence in their 
					songwriting ability, musicianship and their
					knowledge of what could be achieved in the studio.''', 
	image_address = "http://www.popvortex.com/images/album-covers/revolver-the-beatles.jpg",
	genre = genre1,
	user_id = 1)

session.add(album2)
session.commit()

album3 = Albums(
	name = "Sgt. Peppers Lonely Hearts Club Band", 
	artist = "The Beatles", 
	year = "1967", 
	description = '''Released in June of 1967, 
					at the beginning of the Summer of Love, 
					Sgt. Pepper's Lonely Hearts Club Band has 
					been labeled a landmark album ever since. 
					The Beatles, Paul McCartney in particular, 
					had been inspired by the music they heard on 
					the Beach Boys album Pet Sounds and with Sgt. Pepper 
					they intended to match or better it. ''', 
	image_address = "http://www.popvortex.com/images/album-covers/sgt-peppers-lonely-hearts-club-band.jpg",
	genre = genre1,
	user_id = 1)

session.add(album3)
session.commit()

album4 = Albums(
	name = "Abbey Road", 
	artist = "The Beatles", 
	year = "1969", 
	description = '''Though it was released eight months before Let it Be, 
					Abbey Road was the final album The Beatles recorded together. 
					The album is famous for it's side two medley, 
					mainly made up of snippets of unfinished 
					songs which were then woven together.  ''', 
	image_address = "http://www.popvortex.com/images/album-covers/abbey-road-the-bealtes.jpg",
	genre = genre1,
	user_id = 1)

session.add(album4)
session.commit()

album5 = Albums(
	name = "Nevermind", 
	artist = "Nirvana", 
	year = "1991", 
	description = '''Released in 1991, Nevermind helped to popularize the 
					alternative rock and grunge genres. It's a combination 
					of very melodic tunes mixed punk and hard rock sounds and attitude.''', 
	image_address = "http://www.popvortex.com/images/album-covers/nevermind.jpg",
	genre = genre2,
	user_id = 1)

session.add(album5)
session.commit()

album6 = Albums(
	name = "Thriller", 
	artist = "Michael Jackson", 
	year = "1982", 
	description = '''Michael Jackson's Thriller released in 1982 has spent more weeks 
					at number one on the Billboard Top 200 chart than any other album on this list, 
					spending 37 weeks at the top of the charts. This beats out Fleetwood Mac's Rumours, 
					which stayed at the top for 31 weeks, by six weeks. ''', 
	image_address = "http://www.popvortex.com/images/album-covers/thriller.jpg",
	genre = genre3, 
	user_id = 1)

session.add(album6)
session.commit()

album7 = Albums(
	name = "What's Going On", 
	artist = "Marvin Gaye", 
	year = "1971", 
	description = '''Marvin Gaye's What's Going On released in 1971 is the highest ranking album 
					on this chart to not have reached platinum certification of sale of 
					one millions copies, currently it has been certified gold with sales over 500,000.''', 
	image_address = "http://www.popvortex.com/images/album-covers/whats-going-on.jpg",
	genre = genre4,
	user_id = 1)

session.add(album7)
session.commit()

album8 = Albums(
	name = "Ok Computer", 
	artist = "Radiohead", 
	year = "1997", 
	description = '''Other Radiohead albums on the chart: Kid A and The Bends''', 
	image_address = "http://www.popvortex.com/images/album-covers/ok-computer.jpg",
	genre = genre4,
	user_id = 1)

session.add(album8)
session.commit()

print "added albums!"