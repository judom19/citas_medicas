from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LoginView
from citas_app import views

app_name = 'citas_app' 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('no_login_view/', views.no_login_view, name='no_login_view'), 
    path('medical_appointments/', include('citas_app.urls', namespace='medical_appointments')),
]

      