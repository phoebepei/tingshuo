import transaction

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import ForeignKey


from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Users(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	email = Column(Unicode(30), unique=True)
	password = Column(Unicode(30))
	activated = Column(Integer(1))
	
	meta_rel = relationship('MetaData', backref='users', cascade='all, delete, delete-orphan')
	passworeset = relationship('PasswordResets', backref='users', cascade='all, delete, delete-orphan')
	
	def __init__(self, email, password, activated=0):
		self.email = email
		self.password = password
		self.activated = activated
	
	def __repr__(self):
		return "<Email '{email}',Passord '{password}'>".format(email=self.email, password=self.password)
		
class MetaData(Base):
	__tablename__ = 'metadata'
	user_email = Column(Unicode(30), ForeignKey('users.email'),primary_key=True)
	user_photo = Column(Unicode)
	user_intro = Column(UnicodeText)
	
	def __init__(self,email, photo, intro):
		self.user_email = email
		self.user_photo = photo
		self.user_intro = intro
	
	def __repr__(self):
		return "<Email '{email}' ,Introduce '{intro}'".format(email=self.user_email, intro=self.user_intro)

class UserTitle(Base):
	__tablename__ = 'usertitle'
	user_email = Column(Unicode(30), ForeignKey('users.email'), primary_key=True)
	user_title = Column(Unicode(30), unique=True, nullable=False)
	
	def __init__(self, email, title):
		self.user_email = email
		self.user_title = title
		
	def __repr__(self):
		return "<Email '{email}', Title '{title}'".format(email=self.user_email, title=self.user_title)
		
class UserDomain(Base):
	__tablename__ = 'userdomain'
	user_email = Column(Unicode(30),ForeignKey('users.email'), primary_key=True)
	user_domain = Column(Unicode(30), unique=True, nullable=False)
	
	def __init__(self, email, domain):
		self.user_email = email
		self.user_domain = domain
		
	def __repr__(self):
		return "Email '{email}',Domain '{domain}'".format(email=self.user_email, domain=self.user_domain)
		
class Tag(Base):
	__tablename__ = 'tags'
	tag_id = Column(Integer, primary_key=True)
	tag_name = Column(Unicode(30), unique=True, nullable=False)
	tag_num = Column(Integer)
	
	def __init__(self, tag_name, tag_num=0):
		self.tag_name = tag_name
		self.tag_num = tag_num
	
	def __repr__(self):
		return "Tag Name '{name}', Tag Has '{num}'".format(name=self.tag_name, num=self.tag_num)
		
class TextPost(Base):
	__tablename__ = 'textposts'
	post_id = Column(Integer, primary_key=True)
	post_title = Column(Unicode(100), nullable=False)
	post_content = Column(UnicodeText, nullable=False)
	post_author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
	
	def __init__(self, post_id, post_title, post_content, author_id):
		self.post_id = post_id
		self.post_title = post_title
		self.post_content = post_content
		self.post_author_id = author_id
		
	def __repr__(self):
		return "Post Title '{title}'".format(title=self.post_title)
		
		
		
class PasswordResets(Base):
	__tablename__ = 'passwordreset'
	user_email = Column(Unicode, ForeignKey('users.email'), primary_key=True)
	user_reset_num = Column(Unicode(10))
	
	def __init__(self, email, reset_num):
		self.user_email = email
		self.user_reset_num = reset_num
		
	def __repr__(self):
		return "<Email '{email}' , Reset Num '{reset_num}'".format(email=self.user_email, reset_num=self.user_reset_num)

class ActivateAccount(Base):
	__tablename__ = 'activeaccount'
	user_email = Column(Unicode, ForeignKey('users.email'), primary_key=True)
	user_active_code = Column(Unicode(10))
	
	def __init__(self, email, active_code):
		self.user_email = email
		self.user_active_code = active_code
		
	def __repr__(self):
		return "<Email '{email}' , Activate Code '{active_code}'".format(email=self.user_email, active_code=self.active_code)
			
		
def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
