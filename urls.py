from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
#import silk
from views import profile, register, edit_profile
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from evaluations.admin import custom_admin_site  # Import your custom admin site


urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('api/', include('evaluations.urls')),  # Reemplaza 'evaluations' con el nombre de tu aplicación
    path('accounts/', include('django.contrib.auth.urls')),  # Incluye las URLs de autenticación de Django
    #path('silk/', include('silk.urls', namespace='silk')),
    #Auth views
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/profile/', profile, name='profile'),  # Perfil de usuario
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('accounts/register/', register, name='register'),  # Registro de usuario
    path('', RedirectView.as_view(url='/api/', permanent=True)),  # Redirige la raíz a `/api/evaluations/`
    #path('__debug__/', include('debug_toolbar.urls')),
] + staticfiles_urlpatterns()


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
