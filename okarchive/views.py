from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Journal,
    Post,
    )


@view_config(route_name='journal',
             renderer='templates/journal.pt')
def journal_view(request):
    journal_name = request.matchdict['journal_name']
    journal = DBSession.query(Journal)\
        .filter(Journal.name == journal_name)\
        .first()
    if not journal:
        raise HTTPNotFound('No such journal.')

    return dict(journal_name=journal_name,
                posts=journal.posts,
                add_url=request.route_url('post_add', journal_name=journal_name),
    )


class PostView(object):
    """View and edit view for posts."""

    def __init__(self, request):
        self.request = request

    def _get_post(self):
        journal_name = self.request.matchdict['journal_name']
        post_id = self.request.matchdict['post_id']
        post = DBSession.query(Post)\
            .filter(Post.journal_name == journal_name)\
            .filter(Post.id == post_id)\
            .first()
        if not post:
            raise HTTPNotFound('No such post.')
        return post

    @view_config(route_name='post',
                 renderer='templates/post.pt')
    def view(self):
        post = self._get_post()
        return dict(post=post,
                    edit_url=self.request.route_url('post_edit',
                            journal_name=post.journal_name,
                            post_id=post.id),
                    journal_url=self.request.route_url('journal', journal_name=post.journal_name),
                    )

    @view_config(route_name='post_edit',
                 renderer='templates/post_edit.pt')
    def edit(self):
        post = self._get_post()
        if 'form.Submitted' in self.request.params:
            post.title = self.request.POST['title']
            post.text = self.request.POST['text']
            return HTTPFound(location=self.request.route_url('post',
                                                             journal_name=post.journal_name,
                                                             post_id=post.id))
        return {'post': post, 'action': self.request.url}

    @view_config(route_name='post_add',
                 renderer='templates/post_edit.pt')
    def add(self):
        if 'form.Submitted' in self.request.params:
            post = Post(title=self.request.POST['title'],
                        text=self.request.POST['text'],
                        journal_name=self.request.matchdict['journal_name'])
            DBSession.add(post)
            DBSession.flush()
            return HTTPFound(location=self.request.route_url('post',
                                                             journal_name=post.journal_name,
                                                             post_id=post.id))

        post = Post(title='Title',
                    journal_name=self.request.matchdict['journal_name'])
        return {'post': post, 'action': self.request.url}