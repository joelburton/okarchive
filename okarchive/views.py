from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

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


class PostView(object):
    def __init__(self, request):
        self.request = request

        journal_name = request.matchdict['journal_name']
        post_id = request.matchdict['post_id']
        try:
            self.post = DBSession.query(Post).filter(Post.journal_name == journal_name).\
                filter(Post.id == post_id).first()
        except DBAPIError:
            return Response('No such post', content_type='text/plain', status_int=500)

    @view_config(route_name='post', renderer='templates/post.pt')
    def view(self):
        return {'post': self.post}

    @view_config(route_name='post_edit', renderer='templates/post_edit.pt')
    def edit(self):
        if 'form.Submitted' in self.request.params:
            self.post.title = self.request.POST['title']
            self.post.text = self.request.POST['text']
            return HTTPFound(location=self.request.route_url(
                'post', journal_name=self.post.journal_name, post_id=self.post.id))
        return {'post': self.post, 'action': self.request.url}
