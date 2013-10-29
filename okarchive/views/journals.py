from pyramid.view import view_config
from pyramid.security import authenticated_userid

from ..models import Journals


@view_config(name='',
             renderer='okarchive:templates/journals.pt',
             context=Journals,
             permission='view')
class JournalsView(object):
    """List of journals page."""

    def __init__(self, request):
        self.request = request

    def __call__(self):
        return dict(
            logged_in=authenticated_userid(self.request),
        )

