from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from pyramid.events import NewRequest
from pyramid.events import subscriber


from sqlalchemy import engine_from_config

from whatyousay.models import initialize_sql


	

def main(global_config, **settings):
	''' This function returns a Pyramid WSGI application.'''
	engine = engine_from_config(settings, 'sqlalchemy.')
	initialize_sql(engine)
	
	session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
	
	
	config = Configurator(settings=settings, session_factory=session_factory)
	
	
	config.add_static_view('static', 'whatyousay:static')
	
	config.add_route('home', '/')
	config.add_route('login', '/login')
	config.add_route('signup', '/signup')
	config.add_route('test', '/test')
	config.add_route('personal_page', '/{domain}')
	config.add_route('password_reset_new', '/password_reset/new')
	config.add_route('password_reset', '/password_reset/{reset_num:\w{10}}')
	config.add_route('activate_account', '/activate_account/{active_code:\w{10}}')
	config.add_route('new_text', '/dialog/new/{meta:^text|music|photo|video|link$}')
	
	config.scan()
	return config.make_wsgi_app()

