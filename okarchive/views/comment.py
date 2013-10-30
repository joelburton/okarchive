from pyramid.view import view_config
from pyramid.response import Response

from ..models import Comment

class CommentView:
    """View for individual comment."""

    def __init__(self, resource, request):
        self.resource = resource
        self.request = request

    @view_config(name="",
                 context=Comment,
                 permission="view")
    def view(self):
        return Response(self.resource.text)


    @view_config(name="hide",
                 context=Comment,
                 permission="hide")
    def reject(self):
        self.resource.hidden = True
        return Response(self.resource.text)


    @view_config(name="publish",
                     context=Comment,
                     permission="publish")
    def publish(self):
        self.resource.hidden = False
        return Response(self.resource.text)

