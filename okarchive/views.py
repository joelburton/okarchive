from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)

from .models import (
    DBSession,
    Journal,
    Post,
    )


class JournalView(object):
    """View for journals."""

    def __init__(self, request):
        self.request = request

    @view_config(route_name='journal',
                 renderer='templates/journal.pt')
    def view(self):
        journal_name = self.request.matchdict['journal_name']
        journal = DBSession.query(Journal)\
            .filter(Journal.name == journal_name)\
            .first()
        if not journal:
            raise HTTPNotFound('No such journal: %s.' % journal_name)

        return dict(journal_name=journal_name,
                    posts=journal.posts,
                    add_url=self.request.route_url('post_add', journal_name=journal_name),
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
            raise HTTPNotFound('No such journal and/or post: %s, %s.' % (journal_name, post_id))
        return post

    def _redirect_to_post_view(self, post):
        raise HTTPFound(location=self.request.route_url('post',
                                                         journal_name=post.journal_name,
                                                         post_id=post.id))

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

        if 'form.Submitted' in self.request.POST:
            post.title = self.request.POST['title']
            post.text = self.request.POST['text']
            return self._redirect_to_post_view(post)
        else:
            return dict(post=post,
                        action=self.request.url,
                        )

    @view_config(route_name='post_add',
                 renderer='templates/post_edit.pt')
    def add(self):
        if 'form.Submitted' in self.request.POST:
            post = Post(title=self.request.POST['title'],
                        text=self.request.POST['text'],
                        journal_name=self.request.matchdict['journal_name'])
            DBSession.add(post)
            DBSession.flush()     # make post.id available to us
            return self._redirect_to_post_view(post)
        else:
            post = Post(title='Title',
                        journal_name=self.request.matchdict['journal_name'])
            return dict(post=post,
                        action=self.request.url,
                        )