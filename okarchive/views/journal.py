from pyramid.view import view_config
from pyramid.security import (
    authenticated_userid,
    has_permission,
)

from ..models import (
    Journal,
    )


class JournalView:
    """View for journals."""

    def __init__(self, resource, request):
        self.resource = resource
        self.request = request

    @view_config(name='',
                 context=Journal,
                 renderer='okarchive:templates/journal.pt')
    def view(self):
        """View journal and list of posts."""

        req = self.request
        journal = self.resource

        if has_permission('add', journal, req):
            add_url = req.resource_url(journal, 'add')
        else:
            add_url = None

        return dict(
            journal_name=journal.name,
            posts=journal.posts,
            logged_in=authenticated_userid(req),
            add_url=add_url,
        )
