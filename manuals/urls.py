from django.urls import path

from . import views

app_name = "manuals"

urlpatterns = [
    path("", views.manual_list, name="list"),
    path("manuals/<int:pk>/", views.manual_detail, name="detail"),
    path("generate/", views.generate_manual, name="generate"),
    path("ask/", views.ask, name="ask"),
]