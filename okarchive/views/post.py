import deform
import colanderalchemy

from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )
from pyramid.security import (
    authenticated_userid,
    has_permission,
)

from ..models import (
    DBSession,
    Post,
    )


class PostView:
    """View and edit view for posts."""

    schema = colanderalchemy.SQLAlchemySchemaNode(
        Post,
        includes=['title', 'text'],
        title='Journal Post',
    )

    def __init__(self, resource, request):
        self.resource = resource
        self.request = request
        self.journal_name = request.matchdict['journal_name']
        self.journal_url = request.route_url(
            'journal', journal_name=self.journal_name)

    def _get_post(self):
        post_id = self.request.matchdict['post_id']
        post = (DBSession
                .query(Post)
                .filter(Post.journal_name == self.journal_name)
                .filter(Post.id == post_id)
                .first())
        if not post:
            raise HTTPNotFound(
                'No such journal or post: %s, %s.'
                % (self.journal_name, post_id))
        return post

    def _redirect_to_post_view(self, post):
        return HTTPFound(
            location=self.request.route_url('post',
                                            journal_name=post.journal_name,
                                            post_id=post.id))


    @view_config(route_name='post',
                 renderer='okarchive:templates/post.pt',
                 permission='view',
    )
    def view(self):
        """Show a single post."""

        post = self._get_post()
        req = self.request

        if has_permission('edit', self.resource, req):
            edit_url = req.route_url('post_edit',
                                    journal_name=self.journal_name,
                                    post_id=post.id)
        else:
            edit_url = None

        if has_permission('delete', self.resource, req):
            delete_url = req.route_url('post_delete',
                                     journal_name=self.journal_name,
                                     post_id=post.id)
        else:
            delete_url = None

        return dict(post=post,
                    edit_url=edit_url,
                    delete_url=delete_url,
                    journal_url=self.journal_url,
                    logged_in=authenticated_userid(req),
        )


    @view_config(route_name='post_edit',
                 renderer='okarchive:templates/post_edit.pt',
                 permission='edit',
    )
    def edit(self):
        """Show edit form or update post from edit form."""

        req = self.request
        form = deform.Form(self.schema,
                           formid='edit-post',
                           buttons=('edit', 'cancel'))
        post = self._get_post()

        if 'edit' in req.POST:
            controls = req.POST.items() # get the form controls
            try:
                appstruct = form.validate(controls)  # call validate
            except deform.ValidationFailure as e: # catch the exception
                return dict(form=e.render(),
                            registry=form.get_widget_resources(),
                            post=post,
                            journal_url=self.journal_url,
                            title='Edit Post',
                            logged_in=authenticated_userid(req),
                )
            post.title = appstruct['title']
            post.text = appstruct['text']
            req.session.flash(('success', 'Edited.'))
            return self._redirect_to_post_view(post)
        elif 'cancel' in req.POST:
            req.session.flash(('info', 'Cancelled.'))
            return self._redirect_to_post_view(post)
        else:
            appstruct = {'title': post.title, 'text': post.text}
            return dict(form=form.render(appstruct),
                        registry=form.get_widget_resources(),
                        post=post,
                        journal_url=self.journal_url,
                        title='Edit Post',
                        logged_in=authenticated_userid(req),
            )


    @view_config(route_name='post_delete',
                 permission='delete',
    )
    def delete(self):
        """Delete post and redirect to journal."""

        DBSession.delete(self._get_post())
        self.request.session.flash(('danger', 'Deleted.'))
        return HTTPFound(location=self.journal_url)


    @view_config(route_name='post_add',
                 renderer='okarchive:templates/post_edit.pt',
                 permission='add',
    )
    def add(self):
        """Show edit form for adding or add from form."""

        req = self.request
        form = deform.Form(self.schema, formid='add-post', buttons=('add',))
        post = Post(title='Title', journal_name=req.matchdict['journal_name'])

        if 'add' in req.POST:
            controls = req.POST.items() # get the form controls
            try:
                appstruct = form.validate(controls)  # call validate
            except deform.ValidationFailure as e: # catch the exception
                return dict(form=e.render(),
                            registry=form.get_widget_resources(),
                            post=post,
                            journal_url=self.journal_url,
                            title='Add Post',
                            logged_in=authenticated_userid(req),
                )
                # the form submission succeeded, we have the data
            post = Post(title=appstruct['title'],
                        text=appstruct['text'],
                        journal_name=req.matchdict['journal_name'])
            DBSession.add(post)
            DBSession.flush()     # make post.id available to us
            return self._redirect_to_post_view(post)

        else:
            return dict(form=form.render(),
                        registry=form.get_widget_resources(),
                        post=post,
                        journal_url=self.journal_url,
                        title='Add Post',
                        logged_in=authenticated_userid(req),
            )
