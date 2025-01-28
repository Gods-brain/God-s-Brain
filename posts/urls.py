from django.urls import path
from .views import (PostListView,
                    PostCreateView,
                    PostDetailView,
                    PostUpdateView,
                    PostDeleteView,
                    DeleteCommentView)
from . import views



urlpatterns = [
    path('home/', PostListView.as_view(), name='home'),
    path('about/', views.about, name="about"),
    path('post/', PostCreateView.as_view(), name='post'),
    path('post/<int:pk>', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post_delete'),
    path('search/', views.SearchResult.as_view(), name='search'),
    path('post/<int:pk>/toggle-like/', views.ToggleLikeView.as_view(), name='toggle_like'),
    path('load_more/',  views.LoadMoreView.as_view(), name='load_more'),
    path('comment/<int:pk>/delete', DeleteCommentView.as_view(), name='comment_delete'),

]

