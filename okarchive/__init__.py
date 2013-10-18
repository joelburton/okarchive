from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.session import UnencryptedCookieSessionFactoryConfig
my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from .security import groupfinder


from .models import (
    DBSession,
    Base,
    )


def add_routes(config):
    config.add_route('journal', '/journals/{journal_name}')
    config.add_route('post', '/journals/{journal_name}/{post_id:\d+}')
    config.add_route('post_edit', '/journals/{journal_name}/{post_id:\d+}/edit')
    config.add_route('post_delete', '/journals/{journal_name}/{post_id:\d+}/delete')
    config.add_route('post_add', '/journals/{journal_name}/add')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          session_factory=my_session_factory,
                          root_factory='okarchive.models.RootFactory'
    )
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform', 'deform:static', cache_max_age=3600)
    add_routes(config)
    config.scan()
    return config.make_wsgi_app()
