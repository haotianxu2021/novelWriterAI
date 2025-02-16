"""
URL configuration for mygptapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from gptapp.views import SignUpView, CustomLoginView, api_keys_list, add_api_key, remove_api_key, generate_text, save_wrapper, redirect_to_login, save_initial_system_prompt, update_system_prompt
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('api-key/', api_keys_list, name='api_key'),
    path('api-key/add/', add_api_key, name='add_api_key'),
    path('api-key/remove/<int:api_key_id>/', remove_api_key, name='remove_api_key'),
    path('generate/', generate_text, name='generate_text'),
    path('save/', save_wrapper, name='save_outline'),
    path('system/initialize/', save_initial_system_prompt, name='save_initial'),
    path('system/update/', update_system_prompt, name='update_system'),
]
