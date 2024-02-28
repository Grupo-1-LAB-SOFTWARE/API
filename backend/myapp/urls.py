from django.urls import path
from .views import (UsuarioView, ActivateEmail, LoginView, EndpointsView,
                    InstitutoView, CampusView, CursoView)


urlpatterns = [
    path('', EndpointsView.as_view(), name='endpoints'),
    path('usuarios/', UsuarioView.as_view(), name='usuarios'),
    path('usuarios/<int:user_id>/', UsuarioView.as_view(), name='usuarios_get_by_id'),
    path('activate/<str:username>/', ActivateEmail.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('istituto/', InstitutoView.as_view(), name='instituto'),
    path('campus/', CampusView.as_view(), name='campus'),
    path('curso/', CursoView.as_view(), name='curso')
]