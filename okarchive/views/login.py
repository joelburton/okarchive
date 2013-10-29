"""Login/logout views."""

from pyramid.view import (
    view_config,
    forbidden_view_config,
    )
from pyramid.security import (
    remember,
    forget,
    )
from pyramid.httpexceptions import HTTPFound

from ..security import authenticate


@view_config(route_name='login',
             renderer='okarchive:templates/login.pt')
@forbidden_view_config(renderer='okarchive:templates/login.pt')
def login(request):
    """Produce login form or handle response."""

    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)

    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if authenticate(login, password):
            headers = remember(request, login)
            return HTTPFound(location=came_from, headers=headers)
        message = 'Failed login'

    else:
        message = login = password = ''

    return dict(
        message=message,
        url=request.application_url + '/login',
        came_from=came_from,
        login=login,
        password=password,
    )


@view_config(route_name='logout')
def logout(request):
    """Logout nd return to home page."""

    headers = forget(request)
    return HTTPFound(location='/', headers=headers)