from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def add_routes(config):
    config.add_route('journal', '/journals/{journal_name}')
    config.add_route('post', '/journals/{journal_name}/{post_id:\d+}')
    config.add_route('post_edit', '/journals/{journal_name}/{post_id:\d+}/edit')
    config.add_route('post_add', '/journals/{journal_name}/add')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    add_routes(config)
    config.scan()
    return config.make_wsgi_app()
