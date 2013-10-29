import deform

from pyramid.view import view_config
from pyramid.security import (
    authenticated_userid,
    has_permission,
)
from pyramid.httpexceptions import HTTPFound

from ..models import (
    Post,
    Journal,
    )
from .post import PostView

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

    @view_config(name='add',
                 context=Journal,
                 renderer='okarchive:templates/post_edit.pt',
                 permission='add')
    def add(self):
        """Show edit form for adding post or add from form."""

        req = self.request
        journal = self.resource

        form = deform.Form(PostView.schema, formid='add-post', buttons=('add',))
        post = Post(title='Title', journal_name=journal.name)

        if 'add' in req.POST:
            controls = req.POST.items() # get the form controls
            try:
                appstruct = form.validate(controls)  # call validate
            except deform.ValidationFailure as e: # catch the exception
                return dict(form=e.render(),
                            registry=form.get_widget_resources(),
                            post=post,
                            journal_url=req.resource_url(journal),
                            title='Add Post',
                            logged_in=authenticated_userid(req),
                )
                # the form submission succeeded, we have the data
            post = journal.add_post(
                             title=appstruct['title'],
                             text=appstruct['text'],
                             lede=appstruct['lede'],
                             _flush=True    # make post.id available to us
                             )
            return HTTPFound(location=req.resource_url(post))

        else:
            return dict(form=form.render(),
                        registry=form.get_widget_resources(),
                        post=post,
                        journal_url=req.resource_url(journal),
                        title='Add Post',
                        logged_in=authenticated_userid(req),
            )

