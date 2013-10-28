from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import authenticated_userid

from ..models import (
    DBSession,
    Journal,
    )


class JournalView:
    """View for journals."""

    def __init__(self, request):
        self.request = request

    @view_config(route_name='journal',
                 renderer='okarchive:templates/journal.pt')
    def view(self):
        """View journal and list of posts."""

        req = self.request
        journal_name = req.matchdict['journal_name']
        journal = (DBSession
                   .query(Journal)
                   .filter(Journal.name == journal_name)
                   .first())
        if not journal:
            raise HTTPNotFound('No such journal: %s.' % journal_name)

        return dict(
            journal_name=journal_name,
            posts=journal.posts,
            add_url=req.route_url('post_add', journal_name=journal_name),
            logged_in=authenticated_userid(req),
        )
