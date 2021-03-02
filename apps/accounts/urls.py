from django.urls import path

from . import views 

app_name = 'accounts'


urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('activation_email_sent/', views.ActivationEmailSentView.as_view(),
         name='activation_email_sent'),
    path('activate/<str:uidb64>/<str:token>/', views.ActivateView.as_view(), name='activate'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogOutView.as_view(), name='logout'),
    path('profile/<int:pk>/', views.ProfileUpdateView.as_view(), name='profile'),
]