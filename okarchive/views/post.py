from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )

from okarchive.models import (
    DBSession,
    Post,
    )


class PostView(object):
    """View and edit view for posts."""

    def __init__(self, request):
        self.request = request

    def _get_post(self):
        journal_name = self.request.matchdict['journal_name']
        post_id = self.request.matchdict['post_id']
        post = DBSession.query(Post) \
            .filter(Post.journal_name == journal_name) \
            .filter(Post.id == post_id) \
            .first()
        if not post:
            raise HTTPNotFound('No such journal and/or post: %s, %s.' % (journal_name, post_id))
        return post

    def _redirect_to_post_view(self, post):
        raise HTTPFound(location=self.request.route_url('post',
                                                        journal_name=post.journal_name,
                                                        post_id=post.id))

    @view_config(route_name='post',
                 renderer='okarchive:templates/post.pt')
    def view(self):
        """Show a single post."""
        post = self._get_post()
        return dict(post=post,
                    edit_url=self.request.route_url('post_edit',
                                                    journal_name=post.journal_name,
                                                    post_id=post.id),
                    journal_url=self.request.route_url('journal', journal_name=post.journal_name),
        )

    @view_config(route_name='post_edit',
                 renderer='okarchive:templates/post_edit.pt')
    def edit(self):
        """Show edit form or update post from edit form."""
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
                 renderer='okarchive:templates/post_edit.pt')
    def add(self):
        """Show edit form for adding or add from form."""
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