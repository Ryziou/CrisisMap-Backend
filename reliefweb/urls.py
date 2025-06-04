from django.urls import path
from .views import reliefweb_disasters

urlpatterns = [
    path('reliefweb/disasters/', reliefweb_disasters),
]