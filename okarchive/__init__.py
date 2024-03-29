from sqlalchemy import engine_from_config

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .security import group_finder
from .models import (
    DBSession,
    Base,
    )

my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    authn_policy = AuthTktAuthenticationPolicy(
        secret='sosecret',
        callback=group_finder,
        hashalg='sha512',
        )
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(
        settings=settings,
        session_factory=my_session_factory,
        root_factory='okarchive.models.RootFactory',
    )
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('deform', 'deform:static', cache_max_age=3600)
    config.include('pyramid_chameleon')
    config.scan()
    return config.make_wsgi_app()
