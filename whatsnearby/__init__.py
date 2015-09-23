from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
	DBSession,
	Base,
	)


def main(global_config, **settings):
	""" This function returns a Pyramid WSGI application.
	"""
	engine = engine_from_config(settings, 'sqlalchemy.')
	DBSession.configure(bind=engine)
	Base.metadata.bind = engine
	config = Configurator(settings=settings)
	config.add_static_view(name = 'static', path='whatsnearby:static')
	config.include('pyramid_jinja2')
	config.add_route('home', '/')
	config.add_route('result', '/result')
	config.add_route('download', '/result/{file_name}')
	config.scan()
	return config.make_wsgi_app()
