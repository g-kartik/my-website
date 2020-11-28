from django.urls import path
from . import views

app_name = 'user_account'
urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.LogoutUser.as_view(), name='logout'),
    path('signup/', views.SignUpUser.as_view(), name='signup'),
    path('edit_profile/', views.EditProfile.as_view(), name='edit_profile'),
    path('change_password/', views.ChangePassword.as_view(), name='change_password'),
]