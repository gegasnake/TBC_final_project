from django.urls import path
from .views import RegisterView, FollowUserView, UserProfileView, FollowersListView, FollowingsListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('users/<int:user_id>/follow/', FollowUserView.as_view(), name='follow_user'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('followers/', FollowersListView.as_view(), name='followers-list'),
    path('followings/', FollowingsListView.as_view(), name='followings-list'),
]

