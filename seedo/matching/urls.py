from django.urls import path

from . import views

urlpatterns = [
    path("send_request/", views.send_request, name="send_request"),
    path("accept_request/<int:request_id>/", views.accept_request, name="accept_request"),
    path("remove_connection/<int:request_id>/", views.remove_connection, name="remove_connection"),
    path("search/", views.search_users, name="search_users"),
]
