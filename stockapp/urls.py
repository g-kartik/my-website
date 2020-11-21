from django.urls import path
from . import views

app_name = 'stockapp'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('remove/<str:ticker>/', views.remove_stock, name='remove'),
]