from django.urls import path
from .views import reliefweb_disasters

urlpatterns = [
    path('disasters/', reliefweb_disasters),
]