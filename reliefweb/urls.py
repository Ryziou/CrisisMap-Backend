from django.urls import path
from .views import reliefweb_disasters, reliefweb_stats

urlpatterns = [
    path('disasters/', reliefweb_disasters),
    path('stats/', reliefweb_stats)
]