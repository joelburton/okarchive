from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Journal,
    Post,
    )


@view_config(route_name='journal', renderer='templates/journal.pt')
def journal_view(request):
    journal_name = request.matchdict['journal_name']
    try:
        journal = DBSession.query(Journal).filter(Journal.name == journal_name).first()
    except DBAPIError:
        return Response("No such journal", content_type='text/plain', status_int=500)

    return {'journal_name': journal_name, 'posts': journal.posts}

