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
from ..models import SiteRoot

class LoginLogoutView:
    """Login and logout."""

    def __init__(self, request):
        self.request = request

    @view_config(name='login',
                 context=SiteRoot,
                 renderer='okarchive:templates/login.pt')
    @forbidden_view_config(renderer='okarchive:templates/login.pt')
    def login(self):
        """Produce login form or handle response."""

        request = self.request
        login_url = request.application_url + '/login'
        referrer = request.url
        if referrer == login_url:
            referrer = '/' # never use the login form itself as came_from
        came_from = request.params.get('came_from', referrer)

        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']
            if authenticate(login, password):
                request.session.flash(('success', 'Signed in.'))
                headers = remember(request, login)
                return HTTPFound(location=came_from, headers=headers)
            request.session.flash(('danger', 'Failed sign in.'))

        else:
            login = password = ''

        return dict(
            url=login_url,
            came_from=came_from,
            login=login,
            password=password,
        )


    @view_config(name='logout',
                 context=SiteRoot)
    def logout(self):
        """Logout and return to home page."""

        headers = forget(self.request)
        self.request.session.flash(('success', 'Signed out.'))
        return HTTPFound(location='/', headers=headers)