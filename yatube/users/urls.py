from django.urls import path
from . import views
from django.contrib.auth import views as r

app_name = 'users'

urlpatterns = [
    path('login/',
         r.LoginView.as_view(template_name='users/login.html'),
         name='login'),

    path('logout/',
         r.LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'),

    path('password_change/',
         r.PasswordChangeView.as_view(),
         name='password_change'),


    path('password_change/done/',
         r.PasswordChangeDoneView.as_view(),
         name='password_change_done'),


    path('password_reset/',
         r.PasswordResetView.as_view(),
         name='password_reset'),

    path('password_reset/done/',
         r.PasswordResetDoneView.as_view(),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         r.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    path('reset/done/',
         r.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    path('signup/', views.SignUp.as_view(), name='signup'),

]
