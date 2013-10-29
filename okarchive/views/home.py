from pyramid.view import view_config
from pyramid.security import authenticated_userid

@view_config(route_name="home",
             renderer="okarchive:templates/home.pt",
             permission="view")
class HomeView(object):
    """Home page."""

    def __init__(self, request):
        self.request = request

    def __call__(self):
        return dict(
            logged_in=authenticated_userid(self.request),
        )

