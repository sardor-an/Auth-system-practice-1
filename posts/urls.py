from django.urls import path
from .views import PostListApiView, PostRetriveUpdateDestroy, PostCommentsApiView, CommentComentApiView, CommentPostCreateApiView, \
    CommentCommenCreateApiView, CreateDeletePostLikeApiView, CreateDeleteCommentLikeApiView, \
    CommentLikesListApiView, PostLikesListApiView


urlpatterns = [
    path('list-create/', PostListApiView.as_view()),
    path('rud/<uuid:pk>/', PostRetriveUpdateDestroy.as_view()),
    path('<uuid:pk>/comments/', PostCommentsApiView.as_view()),
    path('<uuid:pk>/likes/', PostLikesListApiView.as_view()),


    path('comment/<uuid:pk>/comments/', CommentComentApiView.as_view()),
    path('comment/create/', CommentPostCreateApiView.as_view()),
    path('comment/create/comment/', CommentCommenCreateApiView.as_view()),
    path('comment/like/', CreateDeleteCommentLikeApiView.as_view()),
    path('comment/<uuid:pk>/likes/', CommentLikesListApiView.as_view()),
    path('like-unlike-post/', CreateDeletePostLikeApiView.as_view()),
]