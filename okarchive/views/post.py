from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )

from okarchive.models import (
    DBSession,
    Post,
    )

import deform
import colanderalchemy

from pyramid.security import authenticated_userid

class PostView:
    """View and edit view for posts."""

    schema = colanderalchemy.SQLAlchemySchemaNode(
        Post,
        includes=['title', 'text'],
        title='Journal Post',
    )

    def __init__(self, request):
        self.request = request
        self.journal_name = self.request.matchdict['journal_name']
        self.journal_url = self.request.route_url('journal', journal_name=self.journal_name)

    def _get_post(self):
        post_id = self.request.matchdict['post_id']
        post = DBSession.query(Post) \
            .filter(Post.journal_name == self.journal_name) \
            .filter(Post.id == post_id) \
            .first()
        if not post:
            raise HTTPNotFound('No such journal or post: %s, %s.' % (self.journal_name, post_id))
        return post

    def _redirect_to_post_view(self, post):
        return HTTPFound(location=self.request.route_url('post',
                                                         journal_name=post.journal_name,
                                                         post_id=post.id))

    @view_config(route_name='post',
                 renderer='okarchive:templates/post.pt',
                 permission='view',
    )
    def view(self):
        """Show a single post."""
        post = self._get_post()
        return dict(post=post,
                    edit_url=self.request.route_url('post_edit',
                                                    journal_name=self.journal_name,
                                                    post_id=post.id),
                    journal_url=self.journal_url,
                    logged_in=authenticated_userid(self.request),
        )

    @view_config(route_name='post_edit',
                 renderer='okarchive:templates/post_edit.pt',
                 permission='edit',
    )
    def edit(self):
        """Show edit form or update post from edit form."""

        form = deform.Form(self.schema, buttons=('edit', 'cancel'))
        post = self._get_post()

        if 'edit' in self.request.POST:
            controls = self.request.POST.items() # get the form controls
            try:
                appstruct = form.validate(controls)  # call validate
            except deform.ValidationFailure as e: # catch the exception
                return dict(form=e.render(),
                            registry=form.get_widget_resources(),
                            post=post,
                            journal_url=self.journal_url,
                            logged_in=authenticated_userid(self.request),
                )
            post.title = appstruct['title']
            post.text = appstruct['text']
            self.request.session.flash(('success', 'Edited.'))
            return self._redirect_to_post_view(post)
        elif 'cancel' in self.request.POST:
            self.request.session.flash(('info', 'Cancelled.'))
            return self._redirect_to_post_view(post)
        else:
            appstruct = {'title': post.title, 'text': post.text}
            return dict(form=form.render(appstruct),
                        registry=form.get_widget_resources(),
                        post=post,
                        journal_url=self.journal_url,
                        logged_in=authenticated_userid(self.request),
            )

    @view_config(route_name='post_delete',
                 permission='edit',
    )
    def delete(self):
        """Delete post and redirect to journal."""

        DBSession.delete(self._get_post())
        self.request.session.flash(('danger', 'Deleted.'))
        return HTTPFound(location=self.journal_url)

    @view_config(route_name='post_add',
                 renderer='okarchive:templates/post_edit.pt',
                 permission='edit',
    )
    def add(self):
        """Show edit form for adding or add from form."""

        form = deform.Form(self.schema, buttons=('add',))
        post = Post(title='Title',
                    journal_name=self.request.matchdict['journal_name'])

        if 'add' in self.request.POST:
            controls = self.request.POST.items() # get the form controls
            try:
                appstruct = form.validate(controls)  # call validate
            except deform.ValidationFailure as e: # catch the exception
                return dict(form=e.render(),
                            registry=form.get_widget_resources(),
                            post=post,
                            journal_url=self.journal_url,
                            logged_in=authenticated_userid(self.request),
                )
                # the form submission succeeded, we have the data
            post = Post(title=appstruct['title'],
                        text=appstruct['text'],
                        journal_name=self.request.matchdict['journal_name'])
            DBSession.add(post)
            DBSession.flush()     # make post.id available to us
            return self._redirect_to_post_view(post)

        else:
            return dict(form=form.render(),
                        registry=form.get_widget_resources(),
                        post=post,
                        journal_url=self.journal_url,
                        logged_in=authenticated_userid(self.request),
            )