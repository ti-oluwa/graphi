from django.views import generic


class IndexView(generic.RedirectView):
    """View for the index page."""
    url = "/dashboard/"

index_view = IndexView.as_view()
