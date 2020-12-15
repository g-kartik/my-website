from django.urls import path
from . import views

app_name = 'sfapp'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('page/<int:page>/', views.Home.as_view(), name='page'),
    path('resume/', views.Resume.as_view(), name='resume'),
]