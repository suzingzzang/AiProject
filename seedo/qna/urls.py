from django.urls import path

from .views import *

app_name = "qna"

urlpatterns = [
    path("", QnAListView.as_view(), name="qna-list"),
    path("<int:pk>/", QnADetailView.as_view(), name="qna-detail"),
    path("new/", QnACreateView.as_view(), name="qna-create"),
    path("<int:pk>/edit/", QnAUpdateView.as_view(), name="qna-update"),
    path("<int:pk>/delete/", QnADeleteView.as_view(), name="qna-delete"),
    path("<int:pk>/comment/new/", CommentCreateView.as_view(), name="comment-create"),
    path("<int:pk>/comment/update/", comment_update, name="comment-update"),
    path("<int:pk>/comment/delete/", comment_delete, name="comment-delete"),
]
