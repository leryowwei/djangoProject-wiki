from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.get_page, name="get_page"),
    path("wiki/<str:title>/edit", views.edit_page, name="edit_page"),
    path("search/", views.search_results, name="search"),
    path("create/", views.create_page, name="create"),
    path("random/", views.get_random_page, name="random"),
]
