from django.urls import path
from django.views.generic import TemplateView

app_name = "homepage"
urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="homepage/home.html"),
        name="home",
    )
]
