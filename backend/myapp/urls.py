from django.urls import path
from .views import UsuarioView, ActivateEmail, LoginView, EndpointsView


urlpatterns = [
    path('', EndpointsView.as_view(), name='endpoints'),
    path('usuarios/', UsuarioView.as_view(), name='usuarios'),
    path('usuarios/<int:user_id>/', UsuarioView.as_view(), name='usuarios_get_by_id'),
    path('activate/<str:username>/', ActivateEmail.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
]