from django.urls import include, path

from .views import FollowSubscribeView, FollowView, UserView

urlpatterns = [
    path('users/<int:pk>/subscribe/', FollowSubscribeView.as_view(),
         name='subscribe'),
    path('users/subscriptions/', FollowView.as_view(), name='follow'),
    path('users/<int:pk>/', UserView.as_view(), name='user_detail'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
