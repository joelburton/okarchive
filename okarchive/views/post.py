import deform
import colanderalchemy

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    authenticated_userid,
    has_permission,
)

from ..models import (
    Post,
    )


class PostView:
    """View and edit view for posts."""

    schema = colanderalchemy.SQLAlchemySchemaNode(
        Post,
        includes=['title', 'lede', 'text', 'privacy'],
        title='Journal Post',
    )

    def __init__(self, resource, request):
        self.resource = resource
        self.request = request
        self.journal_url = request.resource_url(resource.__parent__)

    def _redirect_to_post_view(self, post):
        return HTTPFound(location=self.request.resource_url(post))


    @view_config(name='',
                 context=Post,
                 renderer='okarchive:templates/post.pt',
                 permission='view',
    )
    def view(self):
        """Show a single post."""

        post = self.resource
        req = self.request

        if has_permission('edit', post, req):
            edit_url = req.resource_url(post, 'edit')
        else:
            edit_url = None

        if has_permission('delete', post, req):
            delete_url = req.resource_url(post, 'delete')
        else:
            delete_url = None

        return dict(post=post,
                    edit_url=edit_url,
                    delete_url=delete_url,
                    journal_url=self.journal_url,
                    logged_in=authenticated_userid(req),
        )


    @view_config(name='edit',
                 context=Post,
                 renderer='okarchive:templates/post_edit.pt',
                 permission='edit',
    )
    def edit(self):
        """Show edit form or update post from edit form."""

        req = self.request
        form = deform.Form(self.schema,
                           formid='edit-post',
                           buttons=('edit', 'cancel'))
        post = self.resource

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
            post.lede = appstruct['lede']
            req.session.flash(('success', 'Edited.'))
            return self._redirect_to_post_view(post)
        elif 'cancel' in req.POST:
            req.session.flash(('info', 'Cancelled.'))
            return self._redirect_to_post_view(post)
        else:
            appstruct = {'title': post.title,
                         'text': post.text,
                         'lede': post.lede}
            return dict(form=form.render(appstruct),
                        registry=form.get_widget_resources(),
                        post=post,
                        journal_url=self.journal_url,
                        title='Edit Post',
                        logged_in=authenticated_userid(req),
            )


    @view_config(name='delete',
                 context=Post,
                 permission='delete',
    )
    def delete(self):
        """Delete post and redirect to journal."""

        self.resource.delete()
        self.request.session.flash(('danger', 'Deleted.'))
        return HTTPFound(location=self.journal_url)


