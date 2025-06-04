from django.urls import path
from .views import RegisterUserView, ProfileView, PublicProfileView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', RegisterUserView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('profile/<int:pk>', PublicProfileView.as_view())
]