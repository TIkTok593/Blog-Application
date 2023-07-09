from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


app_name = 'blog'
urlpatterns = [
     path('', views.post_list, name='post_list'),
     path('register/', views.UserRegisterView.as_view(), name='user_register'),
     path('create/', views.PostCreateView.as_view(), name='post_create'),
     path('<int:id>/update', views.PostUpdateView.as_view(), name='post_update'),
     path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
     path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.PostDetailView.as_view(), name='post_detail'),
     path('<int:post_id>/share/',
          views.PostShareView.as_view(), name='post_share'),
     path('<int:post_id>/comment/',
          views.PostCommentView.as_view(), name='post_comment'),
     path('profile/create/',
          views.ProfileCreateView.as_view(), name='profile_create'),
     path('profile/<int:pk>/',
          views.ProfileDetailView.as_view(), name='profile_detail'),
     path('users/',
          views.UserListView.as_view(), name='users_list'),
     path('users/<int:id>/',
          views.UserDetailView.as_view(), name='user_detail'),
]
