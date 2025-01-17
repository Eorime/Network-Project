
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newpost", views.newpost_view, name="newpost"),
    path("profile/<str:username>", views.profile_view, name="profile"),
    path('follow/<str:username>', views.follow, name='follow'),
    path('following', views.following, name='following'),
    path('posts/<int:post_id>/edit', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/like', views.like_post, name='like_post'),
    path('posts/<int:post_id>/delete', views.delete_post, name='delete_post'),
]
